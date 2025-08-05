from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tools.models import HeartLinkRequest, ChatRoom, UserOnlineStatus
from apps.tools.views import is_user_active, cleanup_expired_heart_link_requests, disconnect_inactive_users


class Command(BaseCommand):
    help = '清理过期的心动链接请求和断开不活跃用户的连接'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='强制清理所有过期请求，不询问确认',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='只显示将要清理的内容，不实际执行清理',
        )

    def handle(self, *args, **options):
        force = options['force']
        dry_run = options['dry_run']

        self.stdout.write(
            self.style.SUCCESS('开始清理心动链接...')
        )

        if not force and not dry_run:
            confirm = input('确定要清理过期的心动链接请求吗？(y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(
                    self.style.WARNING('清理操作已取消')
                )
                return

        # 统计清理前的状态
        pending_requests = HeartLinkRequest.objects.filter(status='pending').count()
        active_rooms = ChatRoom.objects.filter(status='active').count()
        expired_requests = HeartLinkRequest.objects.filter(status='expired').count()
        ended_rooms = ChatRoom.objects.filter(status='ended').count()

        self.stdout.write(f'清理前状态:')
        self.stdout.write(f'  - 待处理请求: {pending_requests}')
        self.stdout.write(f'  - 活跃聊天室: {active_rooms}')
        self.stdout.write(f'  - 过期请求: {expired_requests}')
        self.stdout.write(f'  - 已结束聊天室: {ended_rooms}')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN模式 - 只显示将要清理的内容')
            )
            
            # 显示将要过期的请求
            expired_requests_to_clean = HeartLinkRequest.objects.filter(
                status='pending',
                created_at__lt=timezone.now() - timedelta(minutes=30)
            )
            
            if expired_requests_to_clean.exists():
                self.stdout.write(f'将要清理的过期请求:')
                for request in expired_requests_to_clean:
                    self.stdout.write(f'  - {request.requester.username} (创建于 {request.created_at})')
            else:
                self.stdout.write('没有需要清理的过期请求')

            # 显示不活跃的用户
            inactive_users = []
            for request in HeartLinkRequest.objects.filter(status='pending'):
                if not is_user_active(request.requester):
                    inactive_users.append(request.requester.username)
            
            if inactive_users:
                self.stdout.write(f'不活跃的用户: {", ".join(set(inactive_users))}')
            else:
                self.stdout.write('没有不活跃的用户')

            return

        # 执行清理
        try:
            # 清理过期请求
            cleanup_expired_heart_link_requests()
            
            # 断开不活跃用户
            disconnect_inactive_users()

            # 统计清理后的状态
            new_pending_requests = HeartLinkRequest.objects.filter(status='pending').count()
            new_active_rooms = ChatRoom.objects.filter(status='active').count()
            new_expired_requests = HeartLinkRequest.objects.filter(status='expired').count()
            new_ended_rooms = ChatRoom.objects.filter(status='ended').count()

            self.stdout.write(f'清理后状态:')
            self.stdout.write(f'  - 待处理请求: {new_pending_requests} (减少了 {pending_requests - new_pending_requests})')
            self.stdout.write(f'  - 活跃聊天室: {new_active_rooms} (减少了 {active_rooms - new_active_rooms})')
            self.stdout.write(f'  - 过期请求: {new_expired_requests} (增加了 {new_expired_requests - expired_requests})')
            self.stdout.write(f'  - 已结束聊天室: {new_ended_rooms} (增加了 {new_ended_rooms - ended_rooms})')

            self.stdout.write(
                self.style.SUCCESS('心动链接清理完成！')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'清理过程中出现错误: {str(e)}')
            ) 