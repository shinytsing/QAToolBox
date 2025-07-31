from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.users.models import UserRole

class Command(BaseCommand):
    help = '设置用户为管理员角色'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='用户名')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            user_role, created = UserRole.objects.get_or_create(user=user)
            user_role.role = 'admin'
            user_role.save()
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'成功为用户 {username} 创建管理员角色')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'成功更新用户 {username} 为管理员角色')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'用户 {username} 不存在')
            ) 