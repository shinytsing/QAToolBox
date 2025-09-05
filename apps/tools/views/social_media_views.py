import json
import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from ..models import SocialMediaNotification, SocialMediaSubscription
from .base import (
    BaseView,
    CachedViewMixin,
    FilterMixin,
    OrderMixin,
    PaginationMixin,
    SearchMixin,
    cache_response,
    error_response,
    rate_limit,
    success_response,
    validate_request_data,
)

logger = logging.getLogger(__name__)


@login_required
@cache_response(timeout=300)
def social_subscription_demo(request):
    """社交媒体订阅演示页面"""
    return render(request, "tools/social_subscription_demo.html")


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["platform", "target_user_id", "target_user_name"])
@rate_limit(max_requests=10, window=3600)  # 每小时最多10个订阅
def add_social_subscription_api(request):
    """添加社交媒体订阅"""
    try:
        data = request.validated_data
        user = request.user

        # 检查是否已存在相同订阅
        existing_subscription = SocialMediaSubscription.objects.filter(
            user=user, platform=data["platform"], target_user_id=data["target_user_id"]
        ).first()

        if existing_subscription:
            return error_response("该订阅已存在", status=400)

        # 创建订阅
        subscription = SocialMediaSubscription.objects.create(
            user=user,
            platform=data["platform"],
            target_user_id=data["target_user_id"],
            target_user_name=data["target_user_name"],
            subscription_types=data.get("subscription_types", ["newPosts"]),
            check_frequency=data.get("check_frequency", 30),
            status="active",
            # 使用模型中存在的字段
            # last_check 字段会自动设置为当前时间（auto_now=True）
        )

        # 清除相关缓存
        cache.delete(f"subscriptions_{user.id}")
        cache.delete(f"subscription_stats_{user.id}")

        return success_response(
            {
                "subscription": {
                    "id": subscription.id,
                    "platform": subscription.platform,
                    "target_user_name": subscription.target_user_name,
                    "status": subscription.status,
                    "created_at": subscription.created_at.isoformat(),
                }
            },
            message="订阅添加成功",
        )

    except Exception as e:
        logger.error(f"Error adding social subscription: {e}")
        return error_response("添加订阅失败", status=500)


@login_required
@cache_response(timeout=60)
def get_subscriptions_api(request):
    """获取用户订阅列表"""
    try:
        user = request.user
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        platform_filter = request.GET.get("platform", "")
        status_filter = request.GET.get("status", "")

        queryset = SocialMediaSubscription.objects.filter(user=user)

        # 平台过滤
        if platform_filter:
            queryset = queryset.filter(platform=platform_filter)

        # 状态过滤
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # 分页
        total_count = queryset.count()
        start = (int(page) - 1) * int(page_size)
        end = start + int(page_size)

        subscriptions = list(queryset.order_by("-created_at")[start:end])

        return success_response(
            {
                "subscriptions": subscriptions,
                "pagination": {
                    "page": int(page),
                    "page_size": int(page_size),
                    "total_count": total_count,
                    "total_pages": (total_count + int(page_size) - 1) // int(page_size),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting subscriptions: {e}")
        return error_response("获取订阅列表失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
@validate_request_data(required_fields=["subscription_id"])
def update_subscription_api(request):
    """更新订阅设置"""
    try:
        data = request.validated_data
        user = request.user

        subscription = get_object_or_404(SocialMediaSubscription, id=data["subscription_id"], user=user)

        # 更新字段 - 只更新模型中存在的字段
        update_fields = ["subscription_types", "check_frequency", "status"]

        for field in update_fields:
            if field in data:
                setattr(subscription, field, data[field])

        subscription.save()

        # 清除相关缓存
        cache.delete(f"subscriptions_{user.id}")
        cache.delete(f"subscription_stats_{user.id}")

        return success_response(
            {
                "subscription": {
                    "id": subscription.id,
                    "platform": subscription.platform,
                    "target_user_name": subscription.target_user_name,
                    "status": subscription.status,
                    "updated_at": subscription.updated_at.isoformat(),
                }
            },
            message="订阅更新成功",
        )

    except Exception as e:
        logger.error(f"Error updating subscription: {e}")
        return error_response("更新订阅失败", status=500)


@login_required
@cache_response(timeout=300)
def get_notifications_api(request):
    """获取通知列表"""
    try:
        user = request.user
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        platform_filter = request.GET.get("platform", "")
        is_read_filter = request.GET.get("is_read", "")

        queryset = SocialMediaNotification.objects.filter(subscription__user=user)

        # 平台过滤
        if platform_filter:
            queryset = queryset.filter(subscription__platform=platform_filter)

        # 已读状态过滤
        if is_read_filter:
            is_read = is_read_filter.lower() == "true"
            queryset = queryset.filter(is_read=is_read)

        # 分页
        total_count = queryset.count()
        start = (int(page) - 1) * int(page_size)
        end = start + int(page_size)

        notifications = list(queryset.select_related("subscription").order_by("-created_at")[start:end])

        return success_response(
            {
                "notifications": notifications,
                "pagination": {
                    "page": int(page),
                    "page_size": int(page_size),
                    "total_count": total_count,
                    "total_pages": (total_count + int(page_size) - 1) // int(page_size),
                },
            }
        )

    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return error_response("获取通知列表失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["notification_id"])
def mark_notification_read_api(request):
    """标记通知为已读"""
    try:
        data = request.validated_data
        user = request.user

        notification = get_object_or_404(SocialMediaNotification, id=data["notification_id"], subscription__user=user)

        notification.is_read = True
        notification.save()

        # 清除相关缓存
        cache.delete(f"unread_notifications_{user.id}")

        return success_response(message="通知已标记为已读")

    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        return error_response("标记通知失败", status=500)


@login_required
@cache_response(timeout=600)
def get_subscription_stats_api(request):
    """获取订阅统计信息"""
    try:
        user = request.user

        # 获取订阅统计
        stats = SocialMediaSubscription.get_user_subscription_stats(user)

        # 获取通知统计
        notification_stats = SocialMediaNotification.get_user_notification_stats(user)

        # 获取平台分布
        platform_distribution = (
            SocialMediaSubscription.objects.filter(user=user)
            .values("platform")
            .annotate(
                count=Count("id"),
                active_count=Count("id", filter=Q(status="active")),
                error_count=Count("id", filter=Q(status="error")),
            )
            .order_by("-count")
        )

        return success_response(
            {
                "subscription_stats": stats,
                "notification_stats": notification_stats,
                "platform_distribution": list(platform_distribution),
            }
        )

    except Exception as e:
        logger.error(f"Error getting subscription stats: {e}")
        return error_response("获取统计信息失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["subscription_id"])
def delete_subscription_api(request):
    """删除订阅"""
    try:
        data = request.validated_data
        user = request.user

        subscription = get_object_or_404(SocialMediaSubscription, id=data["subscription_id"], user=user)

        subscription.delete()

        # 清除相关缓存
        cache.delete(f"subscriptions_{user.id}")
        cache.delete(f"subscription_stats_{user.id}")

        return success_response(message="订阅删除成功")

    except Exception as e:
        logger.error(f"Error deleting subscription: {e}")
        return error_response("删除订阅失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def batch_update_subscriptions_api(request):
    """批量更新订阅"""
    try:
        data = json.loads(request.body) if request.body else {}
        subscription_ids = data.get("subscription_ids", [])
        updates = data.get("updates", {})

        if not subscription_ids:
            return error_response("请选择要更新的订阅")

        if not updates:
            return error_response("请提供更新内容")

        user = request.user
        updated_count = SocialMediaSubscription.objects.filter(user=user, id__in=subscription_ids).update(**updates)

        # 清除相关缓存
        cache.delete(f"subscriptions_{user.id}")
        cache.delete(f"subscription_stats_{user.id}")

        return success_response({"updated_count": updated_count}, message=f"成功更新 {updated_count} 个订阅")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error batch updating subscriptions: {e}")
        return error_response("批量更新失败")


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def batch_delete_subscriptions_api(request):
    """批量删除订阅"""
    try:
        data = json.loads(request.body) if request.body else {}
        subscription_ids = data.get("subscription_ids", [])

        if not subscription_ids:
            return error_response("请选择要删除的订阅")

        user = request.user
        deleted_count = SocialMediaSubscription.objects.filter(user=user, id__in=subscription_ids).delete()[0]

        # 清除相关缓存
        cache.delete(f"subscriptions_{user.id}")
        cache.delete(f"subscription_stats_{user.id}")

        return success_response({"deleted_count": deleted_count}, message=f"成功删除 {deleted_count} 个订阅")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error batch deleting subscriptions: {e}")
        return error_response("批量删除失败")


class SocialMediaAPIView(BaseView, CachedViewMixin, PaginationMixin, SearchMixin, FilterMixin, OrderMixin):
    """社交媒体API视图类"""

    @method_decorator(login_required)
    def get(self, request):
        """获取社交媒体数据"""
        user = request.user

        # 获取查询参数
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        search = request.GET.get("search", "")
        platform_filter = request.GET.get("platform", "")
        status_filter = request.GET.get("status", "")
        order_by = request.GET.get("order_by", "-created_at")

        # 构建查询集
        queryset = SocialMediaSubscription.objects.filter(user=user)

        # 应用过滤
        filters = {}
        if platform_filter:
            filters["platform"] = platform_filter
        if status_filter:
            filters["status"] = status_filter

        queryset = self.filter_queryset(queryset, filters)

        # 应用搜索
        if search:
            queryset = self.search_queryset(queryset, ["target_user_name", "target_user_id"], search)

        # 应用排序
        allowed_order_fields = [
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "last_check_time",
            "-last_check_time",
        ]
        queryset = self.order_queryset(queryset, order_by, allowed_order_fields)

        # 应用分页
        result = self.get_paginated_data(queryset, page, page_size)

        return self.success_response(result)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """创建社交媒体订阅"""
        try:
            data = json.loads(request.body) if request.body else {}

            # 验证必需字段
            required_fields = ["platform", "target_user_id", "target_user_name"]
            for field in required_fields:
                if field not in data:
                    return self.error_response(f"缺少必需字段: {field}")

            user = request.user

            # 检查是否已存在相同订阅
            existing_subscription = SocialMediaSubscription.objects.filter(
                user=user, platform=data["platform"], target_user_id=data["target_user_id"]
            ).first()

            if existing_subscription:
                return self.error_response("该订阅已存在")

            # 创建订阅
            subscription = SocialMediaSubscription.objects.create(
                user=user,
                platform=data["platform"],
                target_user_id=data["target_user_id"],
                target_user_name=data["target_user_name"],
                subscription_types=data.get("subscription_types", ["newPosts"]),
                check_frequency=data.get("check_frequency", 30),
                status="active",
                last_check_time=timezone.now(),
                next_check_time=timezone.now() + timedelta(minutes=data.get("check_frequency", 30)),
                notification_enabled=data.get("notification_enabled", True),
                email_notification=data.get("email_notification", False),
                custom_keywords=data.get("custom_keywords", []),
                exclude_keywords=data.get("exclude_keywords", []),
                max_posts_per_check=data.get("max_posts_per_check", 10),
                auto_archive_old_posts=data.get("auto_archive_old_posts", True),
                archive_after_days=data.get("archive_after_days", 30),
            )

            # 清除相关缓存
            self.clear_user_cache(user.id, "subscriptions")

            return self.success_response(
                {
                    "subscription": {
                        "id": subscription.id,
                        "platform": subscription.platform,
                        "target_user_name": subscription.target_user_name,
                        "status": subscription.status,
                        "created_at": subscription.created_at.isoformat(),
                    }
                }
            )

        except json.JSONDecodeError:
            return self.error_response("无效的JSON数据")
        except Exception as e:
            logger.error(f"Error creating social media subscription: {e}")
            return self.error_response("创建订阅失败")


# 导出主要函数
__all__ = [
    "social_subscription_demo",
    "add_social_subscription_api",
    "get_subscriptions_api",
    "update_subscription_api",
    "get_notifications_api",
    "mark_notification_read_api",
    "get_subscription_stats_api",
    "delete_subscription_api",
    "batch_update_subscriptions_api",
    "batch_delete_subscriptions_api",
    "SocialMediaAPIView",
]
