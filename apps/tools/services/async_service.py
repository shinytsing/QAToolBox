#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务服务
提供异步处理能力
"""

import logging
from datetime import timedelta
from typing import Dict, List

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from celery import shared_task

from apps.tools.models import ChatMessage, ChatRoom, HeartLinkRequest, TimeCapsule
from apps.tools.services.cache_service import ChatCacheService, StatsCacheService, TimeCapsuleCacheService, UserCacheService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification_email(self, user_id: int, subject: str, message: str):
    """发送通知邮件"""
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"邮件发送成功: {user.email}")
        return True

    except Exception as exc:
        logger.error(f"邮件发送失败: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_chat_rooms():
    """清理过期的聊天室"""
    try:
        # 清理超过24小时的聊天室
        expired_time = timezone.now() - timedelta(hours=24)
        expired_rooms = ChatRoom.objects.filter(status="active", updated_at__lt=expired_time)

        count = expired_rooms.count()
        expired_rooms.update(status="expired")

        logger.info(f"清理了 {count} 个过期聊天室")
        return count

    except Exception as e:
        logger.error(f"清理过期聊天室失败: {e}")
        return 0


@shared_task
def cleanup_old_messages():
    """清理旧消息"""
    try:
        # 清理超过30天的消息
        old_time = timezone.now() - timedelta(days=30)
        old_messages = ChatMessage.objects.filter(created_at__lt=old_time)

        count = old_messages.count()
        old_messages.delete()

        logger.info(f"清理了 {count} 条旧消息")
        return count

    except Exception as e:
        logger.error(f"清理旧消息失败: {e}")
        return 0


@shared_task
def update_user_stats(user_id: int):
    """更新用户统计信息"""
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        # 计算用户统计
        stats = {
            "total_capsules": TimeCapsule.objects.filter(user=user).count(),
            "public_capsules": TimeCapsule.objects.filter(user=user, visibility="public").count(),
            "total_messages": ChatMessage.objects.filter(sender=user).count(),
            "active_rooms": ChatRoom.objects.filter(user1=user, status="active").count()
            + ChatRoom.objects.filter(user2=user, status="active").count(),
            "heart_links": HeartLinkRequest.objects.filter(requester=user).count(),
            "last_activity": timezone.now().isoformat(),
        }

        # 缓存统计信息
        UserCacheService.cache_user_stats(user_id, stats)

        logger.info(f"用户 {user_id} 统计信息已更新")
        return stats

    except Exception as e:
        logger.error(f"更新用户统计失败: {e}")
        return None


@shared_task
def update_global_stats():
    """更新全局统计信息"""
    try:
        from django.contrib.auth.models import User

        stats = {
            "total_users": User.objects.count(),
            "total_capsules": TimeCapsule.objects.count(),
            "total_messages": ChatMessage.objects.count(),
            "active_rooms": ChatRoom.objects.filter(status="active").count(),
            "total_heart_links": HeartLinkRequest.objects.count(),
            "updated_at": timezone.now().isoformat(),
        }

        # 缓存全局统计
        StatsCacheService.cache_global_stats(stats)

        logger.info("全局统计信息已更新")
        return stats

    except Exception as e:
        logger.error(f"更新全局统计失败: {e}")
        return None


@shared_task
def process_time_capsule_unlock():
    """处理时光胶囊解锁"""
    try:
        now = timezone.now()

        # 查找需要解锁的时光胶囊
        unlockable_capsules = TimeCapsule.objects.filter(unlock_time__lte=now, unlock_condition="time", visibility="private")

        count = 0
        for capsule in unlockable_capsules:
            try:
                # 发送解锁通知
                send_notification_email.delay(
                    capsule.user.id, "时光胶囊解锁通知", f"您的时光胶囊 '{capsule.title or '未命名'}' 已经解锁！"
                )
                count += 1

            except Exception as e:
                logger.error(f"处理时光胶囊解锁失败: {e}")

        logger.info(f"处理了 {count} 个时光胶囊解锁")
        return count

    except Exception as e:
        logger.error(f"处理时光胶囊解锁失败: {e}")
        return 0


@shared_task
def cache_user_data(user_id: int):
    """缓存用户数据"""
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        # 缓存用户资料
        profile_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        UserCacheService.cache_user_profile(user_id, profile_data)

        # 缓存用户时光胶囊
        capsules = list(
            TimeCapsule.objects.filter(user=user).values("id", "title", "content", "emotions", "visibility", "created_at")
        )
        TimeCapsuleCacheService.cache_user_capsules(user_id, capsules)

        # 缓存活跃聊天室
        active_rooms = list(ChatRoom.objects.filter(user1=user, status="active").values("id", "room_id", "created_at"))
        active_rooms.extend(list(ChatRoom.objects.filter(user2=user, status="active").values("id", "room_id", "created_at")))
        ChatCacheService.cache_active_rooms(user_id, active_rooms)

        logger.info(f"用户 {user_id} 数据已缓存")
        return True

    except Exception as e:
        logger.error(f"缓存用户数据失败: {e}")
        return False


@shared_task
def warm_up_cache():
    """预热缓存"""
    try:
        results = {}

        # 预热全局统计
        stats = update_global_stats()
        if stats:
            results["global_stats"] = True

        # 预热公开时光胶囊
        public_capsules = list(
            TimeCapsule.objects.filter(visibility="public").values("id", "title", "content", "emotions", "created_at")[:100]
        )
        TimeCapsuleCacheService.cache_public_capsules(public_capsules)
        results["public_capsules"] = True

        # 预热活跃用户数据
        from django.contrib.auth.models import User

        active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7))[:50]

        for user in active_users:
            cache_user_data.delay(user.id)

        results["active_users"] = len(active_users)

        logger.info("缓存预热完成")
        return results

    except Exception as e:
        logger.error(f"缓存预热失败: {e}")
        return {"error": str(e)}


@shared_task
def cleanup_cache():
    """清理过期缓存"""
    try:
        from apps.tools.services.cache_service import CacheManager

        results = CacheManager.clear_all_cache()
        logger.info(f"缓存清理完成: {results}")
        return results

    except Exception as e:
        logger.error(f"缓存清理失败: {e}")
        return {"error": str(e)}


@shared_task
def process_batch_operations(operations: List[Dict]):
    """批量处理操作"""
    try:
        results = []

        for operation in operations:
            try:
                op_type = operation.get("type")
                op_data = operation.get("data", {})

                if op_type == "create_user":
                    from django.contrib.auth.models import User

                    user = User.objects.create_user(**op_data)
                    results.append({"type": op_type, "success": True, "user_id": user.id})

                elif op_type == "create_capsule":
                    capsule = TimeCapsule.objects.create(**op_data)
                    results.append({"type": op_type, "success": True, "capsule_id": capsule.id})

                elif op_type == "create_message":
                    message = ChatMessage.objects.create(**op_data)
                    results.append({"type": op_type, "success": True, "message_id": message.id})

                else:
                    results.append({"type": op_type, "success": False, "error": "Unknown operation type"})

            except Exception as e:
                results.append({"type": operation.get("type"), "success": False, "error": str(e)})

        logger.info(f"批量操作完成: {len(results)} 个操作")
        return results

    except Exception as e:
        logger.error(f"批量操作失败: {e}")
        return {"error": str(e)}


# 定时任务配置
CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-chat-rooms": {
        "task": "apps.tools.services.async_service.cleanup_expired_chat_rooms",
        "schedule": timedelta(hours=1),  # 每小时执行一次
    },
    "cleanup-old-messages": {
        "task": "apps.tools.services.async_service.cleanup_old_messages",
        "schedule": timedelta(days=1),  # 每天执行一次
    },
    "update-global-stats": {
        "task": "apps.tools.services.async_service.update_global_stats",
        "schedule": timedelta(minutes=5),  # 每5分钟执行一次
    },
    "process-time-capsule-unlock": {
        "task": "apps.tools.services.async_service.process_time_capsule_unlock",
        "schedule": timedelta(minutes=15),  # 每15分钟执行一次
    },
    "warm-up-cache": {
        "task": "apps.tools.services.async_service.warm_up_cache",
        "schedule": timedelta(hours=6),  # 每6小时执行一次
    },
    "cleanup-cache": {
        "task": "apps.tools.services.async_service.cleanup_cache",
        "schedule": timedelta(hours=12),  # 每12小时执行一次
    },
}
