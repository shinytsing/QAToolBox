"""
社交媒体通知服务
"""

from typing import Dict, List

from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaSubscription


class NotificationService:
    """社交媒体通知服务"""

    @staticmethod
    def create_notifications(updates: List[Dict], subscription: SocialMediaSubscription):
        """创建通知"""
        for update in updates:
            # 检查是否已存在相同通知
            existing_notification = SocialMediaNotification.objects.filter(
                subscription=subscription,
                notification_type=update["type"],
                external_url=update.get("external_url", ""),
                created_at__gte=timezone.now() - timezone.timedelta(hours=1),
            ).first()

            if existing_notification:
                continue

            # 创建新通知
            notification = SocialMediaNotification.objects.create(
                subscription=subscription,
                notification_type=update["type"],
                title=update["title"],
                content=update["content"],
                external_url=update.get("external_url", ""),
                data=update,  # Use 'data' field instead of 'metadata'
                is_read=False,
                created_at=timezone.now(),
            )

            print(f"创建通知: {notification.title}")

    @staticmethod
    def get_unread_count(user) -> int:
        """获取未读通知数量"""
        return SocialMediaNotification.objects.filter(
            subscription__user=user, is_read=False  # Access user through subscription
        ).count()

    @staticmethod
    def mark_as_read(notification_id: int, user) -> bool:
        """标记通知为已读"""
        try:
            notification = SocialMediaNotification.objects.get(
                id=notification_id, subscription__user=user  # Access user through subscription
            )
            notification.is_read = True
            # Note: 'read_at' field doesn't exist in the model, so we'll just save is_read
            notification.save()
            return True
        except SocialMediaNotification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_as_read(user) -> int:
        """标记所有通知为已读"""
        count = SocialMediaNotification.objects.filter(
            subscription__user=user, is_read=False  # Access user through subscription
        ).update(
            is_read=True
            # Note: 'read_at' field doesn't exist in the model
        )
        return count

    @staticmethod
    def delete_old_notifications(days: int = 30) -> int:
        """删除旧通知"""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        count = SocialMediaNotification.objects.filter(created_at__lt=cutoff_date).delete()[0]
        return count
