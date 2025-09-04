import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models import ChatRoom, HeartLinkRequest, UserOnlineStatus

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "清理不活跃的聊天室，用户断开连接10分钟后聊天室消失"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="强制执行清理，忽略时间限制",
        )
        parser.add_argument(
            "--minutes",
            type=int,
            default=10,
            help="设置断开连接后的清理时间（分钟），默认10分钟",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="仅显示将要清理的聊天室，不实际执行清理",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        force = options["force"]
        dry_run = options["dry_run"]

        self.stdout.write(f"开始清理不活跃的聊天室（断开连接{minutes}分钟后清理）...")

        # 获取当前时间
        now = timezone.now()
        cutoff_time = now - timedelta(minutes=minutes)

        # 查找活跃的聊天室
        active_rooms = ChatRoom.objects.filter(status="active")

        rooms_to_cleanup = []

        for room in active_rooms:
            # 检查聊天室是否刚创建（5分钟内不清理）
            if not force and now - room.created_at < timedelta(minutes=5):
                continue

            # 检查房间中的用户是否都不活跃
            user1_inactive = self._is_user_inactive(room.user1, cutoff_time)
            user2_inactive = True  # 如果user2不存在，认为是不活跃的

            if room.user2:
                user2_inactive = self._is_user_inactive(room.user2, cutoff_time)

            # 如果两个用户都不活跃，标记为需要清理
            if user1_inactive and user2_inactive:
                rooms_to_cleanup.append(room)

        if dry_run:
            self.stdout.write(f"将要清理 {len(rooms_to_cleanup)} 个聊天室:")
            for room in rooms_to_cleanup:
                self.stdout.write(f"  - 聊天室 {room.room_id} (创建时间: {room.created_at})")
            return

        # 执行清理
        cleaned_count = 0
        for room in rooms_to_cleanup:
            try:
                # 更新聊天室状态
                room.status = "ended"
                room.ended_at = now
                room.save()

                # 更新相关的心动链接请求状态
                HeartLinkRequest.objects.filter(chat_room=room, status="matched").update(status="expired")

                # 更新用户的在线状态
                self._update_user_status(room.user1, "offline")
                if room.user2:
                    self._update_user_status(room.user2, "offline")

                cleaned_count += 1
                self.stdout.write(f"已清理聊天室: {room.room_id}")

            except Exception as e:
                logger.error(f"清理聊天室 {room.room_id} 时出错: {e}")
                self.stdout.write(self.style.ERROR(f"清理聊天室 {room.room_id} 时出错: {e}"))

        # 统计信息
        total_active = ChatRoom.objects.filter(status="active").count()
        total_ended = ChatRoom.objects.filter(status="ended").count()
        total_waiting = ChatRoom.objects.filter(status="waiting").count()

        self.stdout.write(
            self.style.SUCCESS(
                f"清理完成！\n"
                f"本次清理: {cleaned_count} 个聊天室\n"
                f"当前状态:\n"
                f"  - 活跃聊天室: {total_active}\n"
                f"  - 已结束聊天室: {total_ended}\n"
                f"  - 等待匹配: {total_waiting}"
            )
        )

    def _is_user_inactive(self, user, cutoff_time):
        """检查用户是否不活跃"""
        try:
            # 首先检查在线状态
            online_status = UserOnlineStatus.objects.filter(user=user).first()
            if online_status and online_status.last_seen:
                return online_status.last_seen < cutoff_time

            # 如果没有在线状态记录，检查最后登录时间
            if user.last_login:
                return user.last_login < cutoff_time

            # 如果都没有，认为是不活跃的
            return True

        except Exception as e:
            logger.error(f"检查用户 {user.username} 活跃状态时出错: {e}")
            return True

    def _update_user_status(self, user, status):
        """更新用户在线状态"""
        try:
            online_status, created = UserOnlineStatus.objects.get_or_create(user=user, defaults={"status": status})
            online_status.status = status
            online_status.is_online = status == "online"
            online_status.save()
        except Exception as e:
            logger.error(f"更新用户 {user.username} 状态时出错: {e}")
