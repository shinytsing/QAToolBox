from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = '初始化社交媒体订阅示例数据'

    def handle(self, *args, **options):
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': '测试',
                'last_name': '用户'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'创建测试用户: {user.username}')
            )
        
        # 创建示例订阅
        subscriptions_data = [
            {
                'platform': 'xiaohongshu',
                'target_user_id': 'user123',
                'target_user_name': '时尚博主小美',
                'subscription_types': ['newPosts', 'newFollowers'],
                'check_frequency': 15,
                'avatar_url': 'https://via.placeholder.com/40'
            },
            {
                'platform': 'douyin',
                'target_user_id': 'douyin456',
                'target_user_name': '音乐达人阿强',
                'subscription_types': ['newPosts'],
                'check_frequency': 30,
                'avatar_url': 'https://via.placeholder.com/40'
            },
            {
                'platform': 'netease',
                'target_user_id': 'netease789',
                'target_user_name': '音乐制作人小王',
                'subscription_types': ['newPosts', 'profileChanges'],
                'check_frequency': 60,
                'avatar_url': 'https://via.placeholder.com/40'
            }
        ]
        
        created_count = 0
        for sub_data in subscriptions_data:
            subscription, created = SocialMediaSubscription.objects.get_or_create(
                user=user,
                platform=sub_data['platform'],
                target_user_id=sub_data['target_user_id'],
                defaults=sub_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建订阅: {subscription.target_user_name} ({subscription.get_platform_display()})')
                )
        
        # 创建示例通知
        notifications_data = [
            {
                'subscription': SocialMediaSubscription.objects.filter(
                    user=user, 
                    platform='xiaohongshu'
                ).first(),
                'notification_type': 'newPosts',
                'title': '时尚博主小美发布了新动态',
                'content': '分享了一套春季穿搭，包含详细的搭配技巧和购买链接...',
                'is_read': False
            },
            {
                'subscription': SocialMediaSubscription.objects.filter(
                    user=user, 
                    platform='xiaohongshu'
                ).first(),
                'notification_type': 'newFollowers',
                'title': '时尚博主小美新增关注者',
                'content': '新增了 15 个关注者，总关注数达到 12,345',
                'is_read': True
            },
            {
                'subscription': SocialMediaSubscription.objects.filter(
                    user=user, 
                    platform='douyin'
                ).first(),
                'notification_type': 'newPosts',
                'title': '音乐达人阿强发布了新视频',
                'content': '发布了一首原创歌曲《春天的旋律》，获得了大量点赞...',
                'is_read': False
            }
        ]
        
        notif_created_count = 0
        for notif_data in notifications_data:
            if notif_data['subscription']:
                notification, created = SocialMediaNotification.objects.get_or_create(
                    subscription=notif_data['subscription'],
                    notification_type=notif_data['notification_type'],
                    title=notif_data['title'],
                    defaults={
                        'content': notif_data['content'],
                        'is_read': notif_data['is_read']
                    }
                )
                
                if created:
                    notif_created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'创建通知: {notification.title}')
                    )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'初始化完成！创建了 {created_count} 个订阅和 {notif_created_count} 个通知'
            )
        ) 