from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models import HeartLinkRequest, UserOnlineStatus
from apps.tools.views import cleanup_expired_heart_link_requests, disconnect_inactive_users


class Command(BaseCommand):
    help = "清理过期的心动链接请求和断开不活跃用户"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="强制执行清理，忽略概率限制",
        )

    def handle(self, *args, **options):
        self.stdout.write("开始清理过期的心动链接请求...")

        # 强制执行清理
        if options["force"]:
            self.stdout.write("强制执行清理...")
            cleanup_expired_heart_link_requests()
            disconnect_inactive_users()
        else:
            # 智能清理：根据系统负载动态调整清理频率
            from apps.tools.models import HeartLinkRequest

            pending_count = HeartLinkRequest.objects.filter(status="pending").count()

            # 根据待处理请求数量调整清理概率
            if pending_count > 50:
                # 请求较多时，增加清理频率
                cleanup_probability = 0.5
            elif pending_count > 20:
                # 请求中等时，正常清理频率
                cleanup_probability = 0.3
            else:
                # 请求较少时，减少清理频率
                cleanup_probability = 0.1

            import random

            if random.random() < cleanup_probability:
                self.stdout.write(f"执行智能清理 (概率: {cleanup_probability:.1%})...")
                cleanup_expired_heart_link_requests()
                disconnect_inactive_users()
            else:
                self.stdout.write(f"跳过本次清理 (概率: {cleanup_probability:.1%})...")

        # 统计信息
        total_requests = HeartLinkRequest.objects.count()
        pending_requests = HeartLinkRequest.objects.filter(status="pending").count()
        expired_requests = HeartLinkRequest.objects.filter(status="expired").count()
        matched_requests = HeartLinkRequest.objects.filter(status="matched").count()

        # 计算匹配成功率
        if total_requests > 0:
            match_rate = (matched_requests / total_requests) * 100
        else:
            match_rate = 0

        self.stdout.write(
            self.style.SUCCESS(
                f"清理完成！统计信息：\n"
                f"总请求数: {total_requests}\n"
                f"等待中: {pending_requests}\n"
                f"已过期: {expired_requests}\n"
                f"已匹配: {matched_requests}\n"
                f"匹配成功率: {match_rate:.1f}%"
            )
        )
