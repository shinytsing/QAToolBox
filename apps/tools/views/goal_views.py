from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, Count, Avg, Sum, Max
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from ..models import LifeGoal, LifeGoalProgress, LifeStatistics
from .base import (
    BaseView,
    CachedViewMixin,
    PaginationMixin,
    SearchMixin,
    FilterMixin,
    OrderMixin,
    success_response,
    error_response,
    cache_response,
    validate_request_data,
    rate_limit,
)

logger = logging.getLogger(__name__)


@login_required
@cache_response(timeout=300)
def life_goals_dashboard(request):
    """生活目标仪表盘"""
    user = request.user

    # 获取用户目标摘要
    goals_summary = LifeGoal.get_user_goals_summary(user)

    # 获取活跃目标
    active_goals = LifeGoal.objects.filter(user=user, status="active").order_by("-priority", "-created_at")[:5]

    # 获取最近进度更新
    recent_progress = LifeGoalProgress.objects.filter(goal__user=user).select_related("goal").order_by("-created_at")[:10]

    # 获取目标完成率趋势
    completion_trend = LifeStatistics.objects.filter(user=user).order_by("-date")[:30]

    context = {
        "goals_summary": goals_summary,
        "active_goals": active_goals,
        "recent_progress": recent_progress,
        "completion_trend": completion_trend,
    }

    return render(request, "tools/life_goals_dashboard.html", context)


@login_required
@cache_response(timeout=60)
def life_goals_list(request):
    """目标列表"""
    user = request.user
    page = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 20)
    status_filter = request.GET.get("status", "")
    category_filter = request.GET.get("category", "")
    priority_filter = request.GET.get("priority", "")
    search = request.GET.get("search", "")

    queryset = LifeGoal.objects.filter(user=user)

    # 状态过滤
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # 类别过滤
    if category_filter:
        queryset = queryset.filter(category=category_filter)

    # 优先级过滤
    if priority_filter:
        queryset = queryset.filter(priority=int(priority_filter))

    # 搜索过滤
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # 分页
    total_count = queryset.count()
    start = (int(page) - 1) * int(page_size)
    end = start + int(page_size)

    goals = list(queryset.order_by("-priority", "-created_at")[start:end])

    return success_response(
        {
            "goals": goals,
            "pagination": {
                "page": int(page),
                "page_size": int(page_size),
                "total_count": total_count,
                "total_pages": (total_count + int(page_size) - 1) // int(page_size),
            },
        }
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["title", "category"])
@rate_limit(max_requests=20, window=3600)  # 每小时最多20个目标
def create_life_goal(request):
    """创建生活目标"""
    try:
        data = request.validated_data
        user = request.user

        # 创建目标
        goal = LifeGoal.objects.create(
            user=user,
            title=data["title"],
            description=data.get("description", ""),
            category=data["category"],
            goal_type=data.get("goal_type", "daily"),
            priority=data.get("priority", 5),
            difficulty=data.get("difficulty", "medium"),
            start_date=data.get("start_date"),
            target_date=data.get("target_date"),
            milestones=data.get("milestones", []),
            tags=data.get("tags", []),
            reminder_enabled=data.get("reminder_enabled", True),
            reminder_frequency=data.get("reminder_frequency", "daily"),
            reminder_time=data.get("reminder_time", "09:00"),
        )

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response(
            {
                "goal": {
                    "id": goal.id,
                    "title": goal.title,
                    "category": goal.category,
                    "status": goal.status,
                    "priority": goal.priority,
                    "progress": goal.progress,
                    "created_at": goal.created_at.isoformat(),
                }
            },
            message="目标创建成功",
        )

    except Exception as e:
        logger.error(f"Error creating life goal: {e}")
        return error_response("创建目标失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["PUT"])
@validate_request_data(required_fields=["title", "category"])
def update_life_goal(request, goal_id):
    """更新生活目标"""
    try:
        data = request.validated_data
        user = request.user

        goal = get_object_or_404(LifeGoal, id=goal_id, user=user)

        # 更新字段
        goal.title = data["title"]
        goal.description = data.get("description", goal.description)
        goal.category = data["category"]
        goal.goal_type = data.get("goal_type", goal.goal_type)
        goal.priority = data.get("priority", goal.priority)
        goal.difficulty = data.get("difficulty", goal.difficulty)
        goal.start_date = data.get("start_date", goal.start_date)
        goal.target_date = data.get("target_date", goal.target_date)
        goal.milestones = data.get("milestones", goal.milestones)
        goal.tags = data.get("tags", goal.tags)
        goal.reminder_enabled = data.get("reminder_enabled", goal.reminder_enabled)
        goal.reminder_frequency = data.get("reminder_frequency", goal.reminder_frequency)
        goal.reminder_time = data.get("reminder_time", goal.reminder_time)
        goal.save()

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response(
            {
                "goal": {
                    "id": goal.id,
                    "title": goal.title,
                    "category": goal.category,
                    "status": goal.status,
                    "priority": goal.priority,
                    "progress": goal.progress,
                    "updated_at": goal.updated_at.isoformat(),
                }
            },
            message="目标更新成功",
        )

    except Exception as e:
        logger.error(f"Error updating life goal: {e}")
        return error_response("更新目标失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_life_goal(request, goal_id):
    """删除生活目标"""
    try:
        user = request.user
        goal = get_object_or_404(LifeGoal, id=goal_id, user=user)

        goal.delete()

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response(message="目标删除成功")

    except Exception as e:
        logger.error(f"Error deleting life goal: {e}")
        return error_response("删除目标失败", status=500)


@login_required
@cache_response(timeout=300)
def life_goal_detail(request, goal_id):
    """目标详情"""
    user = request.user
    goal = get_object_or_404(LifeGoal, id=goal_id, user=user)

    # 获取进度记录
    progress_records = LifeGoalProgress.objects.filter(goal=goal).order_by("-date")[:10]

    # 计算统计信息
    total_progress_records = progress_records.count()
    avg_progress = progress_records.aggregate(avg=Avg("progress_value"))["avg"] or 0

    return success_response(
        {
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "goal_type": goal.goal_type,
                "status": goal.status,
                "priority": goal.priority,
                "difficulty": goal.difficulty,
                "start_date": goal.start_date.isoformat() if goal.start_date else None,
                "target_date": goal.target_date.isoformat() if goal.target_date else None,
                "progress": goal.progress,
                "milestones": goal.milestones,
                "tags": goal.tags,
                "reminder_enabled": goal.reminder_enabled,
                "reminder_frequency": goal.reminder_frequency,
                "reminder_time": goal.reminder_time.strftime("%H:%M") if goal.reminder_time else None,
                "created_at": goal.created_at.isoformat(),
                "updated_at": goal.updated_at.isoformat(),
                "completed_at": goal.completed_at.isoformat() if goal.completed_at else None,
                "days_remaining": goal.get_days_remaining(),
                "is_overdue": goal.is_overdue(),
                "priority_color": goal.get_priority_color(),
                "milestones_display": goal.get_milestones_display(),
                "tags_display": goal.get_tags_display(),
            },
            "progress_records": list(progress_records.values("date", "progress_value", "notes", "created_at")),
            "statistics": {
                "total_progress_records": total_progress_records,
                "avg_progress": round(avg_progress, 2),
            },
        }
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
@validate_request_data(required_fields=["progress_value"])
@rate_limit(max_requests=50, window=3600)  # 每小时最多50次进度更新
def update_goal_progress(request, goal_id):
    """更新目标进度"""
    try:
        data = request.validated_data
        user = request.user

        goal = get_object_or_404(LifeGoal, id=goal_id, user=user)

        # 检查目标状态
        if goal.status != "active":
            return error_response("只能更新活跃目标的进度", status=400)

        progress_value = int(data["progress_value"])
        if progress_value < 0 or progress_value > 100:
            return error_response("进度值必须在0-100之间", status=400)

        # 创建或更新进度记录
        progress_record, created = LifeGoalProgress.objects.get_or_create(
            goal=goal,
            date=timezone.now().date(),
            defaults={
                "progress_value": progress_value,
                "notes": data.get("notes", ""),
            },
        )

        if not created:
            progress_record.progress_value = progress_value
            progress_record.notes = data.get("notes", progress_record.notes)
            progress_record.save()

        # 更新目标总进度
        goal.progress = progress_value
        if progress_value >= 100:
            goal.status = "completed"
            goal.completed_at = timezone.now()
        goal.save()

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response(
            {
                "progress_record": {
                    "id": progress_record.id,
                    "progress_value": progress_record.progress_value,
                    "notes": progress_record.notes,
                    "date": progress_record.date.isoformat(),
                    "created_at": progress_record.created_at.isoformat(),
                },
                "goal_progress": goal.progress,
                "goal_status": goal.status,
            },
            message="进度更新成功",
        )

    except Exception as e:
        logger.error(f"Error updating goal progress: {e}")
        return error_response("更新进度失败", status=500)


@login_required
@cache_response(timeout=600)
def goals_statistics(request):
    """目标统计"""
    user = request.user
    days = int(request.GET.get("days", 30))

    # 获取目标统计
    goals_summary = LifeGoal.get_user_goals_summary(user)

    # 获取进度趋势
    from datetime import timedelta

    start_date = timezone.now().date() - timedelta(days=days)

    progress_trend = (
        LifeGoalProgress.objects.filter(goal__user=user, date__gte=start_date)
        .values("date")
        .annotate(avg_progress=Avg("progress_value"), total_updates=Count("id"))
        .order_by("date")
    )

    # 获取类别分布
    category_distribution = (
        LifeGoal.objects.filter(user=user)
        .values("category")
        .annotate(count=Count("id"), avg_progress=Avg("progress"))
        .order_by("-count")
    )

    # 获取优先级分布
    priority_distribution = (
        LifeGoal.objects.filter(user=user)
        .values("priority")
        .annotate(count=Count("id"), avg_progress=Avg("progress"))
        .order_by("priority")
    )

    return success_response(
        {
            "goals_summary": goals_summary,
            "progress_trend": list(progress_trend),
            "category_distribution": list(category_distribution),
            "priority_distribution": list(priority_distribution),
        }
    )


class GoalAPIView(BaseView, CachedViewMixin, PaginationMixin, SearchMixin, FilterMixin, OrderMixin):
    """目标API视图类"""

    @method_decorator(login_required)
    def get(self, request):
        """获取目标列表"""
        user = request.user

        # 获取查询参数
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 20)
        search = request.GET.get("search", "")
        status_filter = request.GET.get("status", "")
        category_filter = request.GET.get("category", "")
        priority_filter = request.GET.get("priority", "")
        order_by = request.GET.get("order_by", "-priority")

        # 构建查询集
        queryset = LifeGoal.objects.filter(user=user)

        # 应用过滤
        filters = {}
        if status_filter:
            filters["status"] = status_filter
        if category_filter:
            filters["category"] = category_filter
        if priority_filter:
            filters["priority"] = int(priority_filter)

        queryset = self.filter_queryset(queryset, filters)

        # 应用搜索
        if search:
            queryset = self.search_queryset(queryset, ["title", "description"], search)

        # 应用排序
        allowed_order_fields = ["priority", "-priority", "created_at", "-created_at", "target_date", "-target_date"]
        queryset = self.order_queryset(queryset, order_by, allowed_order_fields)

        # 应用分页
        result = self.get_paginated_data(queryset, page, page_size)

        return self.success_response(result)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request):
        """创建目标"""
        try:
            data = json.loads(request.body) if request.body else {}

            # 验证必需字段
            required_fields = ["title", "category"]
            for field in required_fields:
                if field not in data:
                    return self.error_response(f"缺少必需字段: {field}")

            user = request.user

            # 创建目标
            goal = LifeGoal.objects.create(
                user=user,
                title=data["title"],
                description=data.get("description", ""),
                category=data["category"],
                goal_type=data.get("goal_type", "daily"),
                priority=data.get("priority", 5),
                difficulty=data.get("difficulty", "medium"),
                start_date=data.get("start_date"),
                target_date=data.get("target_date"),
                milestones=data.get("milestones", []),
                tags=data.get("tags", []),
                reminder_enabled=data.get("reminder_enabled", True),
                reminder_frequency=data.get("reminder_frequency", "daily"),
                reminder_time=data.get("reminder_time", "09:00"),
            )

            # 清除相关缓存
            self.clear_user_cache(user.id, "goals")

            return self.success_response(
                {
                    "goal": {
                        "id": goal.id,
                        "title": goal.title,
                        "category": goal.category,
                        "status": goal.status,
                        "priority": goal.priority,
                        "progress": goal.progress,
                        "created_at": goal.created_at.isoformat(),
                    }
                }
            )

        except json.JSONDecodeError:
            return self.error_response("无效的JSON数据")
        except Exception as e:
            logger.error(f"Error creating life goal: {e}")
            return self.error_response("创建目标失败")


# 批量操作视图
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def batch_update_goals(request):
    """批量更新目标"""
    try:
        data = json.loads(request.body) if request.body else {}
        goal_ids = data.get("goal_ids", [])
        updates = data.get("updates", {})

        if not goal_ids:
            return error_response("请选择要更新的目标")

        if not updates:
            return error_response("请提供更新内容")

        user = request.user
        updated_count = LifeGoal.objects.filter(user=user, id__in=goal_ids).update(**updates)

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response({"updated_count": updated_count}, message=f"成功更新 {updated_count} 个目标")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error batch updating goals: {e}")
        return error_response("批量更新失败")


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def batch_delete_goals(request):
    """批量删除目标"""
    try:
        data = json.loads(request.body) if request.body else {}
        goal_ids = data.get("goal_ids", [])

        if not goal_ids:
            return error_response("请选择要删除的目标")

        user = request.user
        deleted_count = LifeGoal.objects.filter(user=user, id__in=goal_ids).delete()[0]

        # 清除相关缓存
        cache.delete(f"goals_summary_{user.id}")
        cache.delete(f"goals_list_{user.id}")

        return success_response({"deleted_count": deleted_count}, message=f"成功删除 {deleted_count} 个目标")

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error batch deleting goals: {e}")
        return error_response("批量删除失败")


@login_required
@cache_response(timeout=300)
def goal_reminders(request):
    """目标提醒"""
    user = request.user

    # 获取需要提醒的目标
    from datetime import datetime, timedelta

    today = timezone.now().date()

    # 即将到期的目标
    upcoming_deadlines = LifeGoal.objects.filter(
        user=user,
        status="active",
        target_date__isnull=False,
        target_date__gte=today,
        target_date__lte=today + timedelta(days=7),
    ).order_by("target_date")

    # 长期未更新的目标
    long_inactive_goals = (
        LifeGoal.objects.filter(user=user, status="active")
        .annotate(last_progress_date=Max("lifegoalprogress__date"))
        .filter(Q(last_progress_date__isnull=True) | Q(last_progress_date__lt=today - timedelta(days=30)))
        .order_by("-created_at")
    )

    return success_response(
        {
            "upcoming_deadlines": list(upcoming_deadlines.values("id", "title", "target_date", "progress")),
            "long_inactive_goals": list(long_inactive_goals.values("id", "title", "created_at", "progress")),
        }
    )
