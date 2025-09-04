import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaPlatformConfig, SocialMediaSubscription


class Command(BaseCommand):
    help = "初始化社交媒体订阅示例数据"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, help="指定用户名，如果不指定则使用第一个用户")

    def handle(self, *args, **options):
        # 获取用户
        username = options.get("user")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"用户 {username} 不存在"))
                return
        else:
            # 使用第一个用户
            if not User.objects.exists():
                self.stdout.write(self.style.ERROR("没有找到任何用户，请先创建用户"))
                return
            user = User.objects.first()

        self.stdout.write(f"正在为用户 {user.username} 初始化社交媒体订阅数据...")

        # 创建平台配置
        self.create_platform_configs()

        # 创建示例订阅
        subscriptions = self.create_sample_subscriptions(user)

        # 创建示例通知
        self.create_sample_notifications(subscriptions)

        self.stdout.write(self.style.SUCCESS(f"成功初始化社交媒体订阅数据！"))
        self.stdout.write(f"- 创建了 {len(subscriptions)} 个订阅")
        self.stdout.write(f"- 创建了示例通知")

    def create_platform_configs(self):
        """创建平台配置"""
        platforms = [
            {"platform": "xiaohongshu", "api_endpoint": "https://api.xiaohongshu.com/v1", "rate_limit": 100},
            {"platform": "douyin", "api_endpoint": "https://api.douyin.com/v1", "rate_limit": 150},
            {"platform": "netease", "api_endpoint": "https://api.music.163.com/v1", "rate_limit": 200},
            {"platform": "weibo", "api_endpoint": "https://api.weibo.com/v2", "rate_limit": 120},
            {"platform": "bilibili", "api_endpoint": "https://api.bilibili.com/x", "rate_limit": 180},
            {"platform": "zhihu", "api_endpoint": "https://api.zhihu.com/v4", "rate_limit": 80},
        ]

        for platform_data in platforms:
            SocialMediaPlatformConfig.objects.get_or_create(
                platform=platform_data["platform"],
                defaults={
                    "api_endpoint": platform_data["api_endpoint"],
                    "rate_limit": platform_data["rate_limit"],
                    "is_active": True,
                },
            )

        self.stdout.write("✓ 平台配置已创建")

    def create_sample_subscriptions(self, user):
        """创建示例订阅"""
        sample_subscriptions = [
            {
                "platform": "xiaohongshu",
                "target_user_id": "fashion_lover_123",
                "target_user_name": "时尚达人小美",
                "subscription_types": ["newPosts", "profileChanges"],
                "check_frequency": 15,
                "status": "active",
            },
            {
                "platform": "douyin",
                "target_user_id": "dance_queen_456",
                "target_user_name": "舞蹈女王",
                "subscription_types": ["newPosts"],
                "check_frequency": 30,
                "status": "active",
            },
            {
                "platform": "netease",
                "target_user_id": "music_producer_789",
                "target_user_name": "音乐制作人",
                "subscription_types": ["newPosts", "newFollowers"],
                "check_frequency": 60,
                "status": "active",
            },
            {
                "platform": "weibo",
                "target_user_id": "tech_blogger_101",
                "target_user_name": "科技博主",
                "subscription_types": ["newPosts", "profileChanges"],
                "check_frequency": 15,
                "status": "paused",
            },
            {
                "platform": "bilibili",
                "target_user_id": "game_streamer_202",
                "target_user_name": "游戏主播",
                "subscription_types": ["newPosts"],
                "check_frequency": 30,
                "status": "active",
            },
            {
                "platform": "zhihu",
                "target_user_id": "knowledge_sharer_303",
                "target_user_name": "知识分享者",
                "subscription_types": ["newPosts", "newFollowers"],
                "check_frequency": 60,
                "status": "active",
            },
        ]

        subscriptions = []
        for sub_data in sample_subscriptions:
            subscription, created = SocialMediaSubscription.objects.get_or_create(
                user=user,
                platform=sub_data["platform"],
                target_user_id=sub_data["target_user_id"],
                defaults={
                    "target_user_name": sub_data["target_user_name"],
                    "subscription_types": sub_data["subscription_types"],
                    "check_frequency": sub_data["check_frequency"],
                    "status": sub_data["status"],
                    "last_check": timezone.now(),
                },
            )
            subscriptions.append(subscription)
            if created:
                self.stdout.write(f'✓ 创建订阅: {sub_data["target_user_name"]} ({sub_data["platform"]})')

        return subscriptions

    def create_sample_notifications(self, subscriptions):
        """创建示例通知"""
        notification_templates = {
            "newPosts": [
                {"title": "发布了新内容", "content": "刚刚发布了一篇精彩的内容，快去看看吧！"},
                {"title": "更新了动态", "content": "有新的动态更新，内容很有趣哦～"},
                {"title": "分享了新作品", "content": "新作品上线了，质量很高，值得关注！"},
            ],
            "newFollowers": [
                {"title": "新增关注者", "content": "获得了新的关注者，粉丝数量又增加了！"},
                {"title": "粉丝增长", "content": "粉丝数量突破新纪录，影响力在扩大！"},
            ],
            "profileChanges": [
                {"title": "更新了个人资料", "content": "个人资料有新的变化，可能更新了头像或简介。"},
                {"title": "修改了签名", "content": "个人签名有更新，看看有什么新想法！"},
            ],
        }

        # 为每个订阅创建一些通知
        for subscription in subscriptions:
            for notification_type in subscription.subscription_types:
                templates = notification_templates.get(notification_type, [])
                if templates:
                    # 随机选择1-3个通知创建
                    num_notifications = random.randint(1, 3)
                    for i in range(num_notifications):
                        template = random.choice(templates)
                        notification = SocialMediaNotification.objects.create(
                            subscription=subscription,
                            notification_type=notification_type,
                            title=f"{subscription.target_user_name} {template['title']}",
                            content=template["content"],
                            is_read=random.choice([True, False]),
                            created_at=timezone.now() - timezone.timedelta(hours=random.randint(1, 72)),
                        )
                        self.stdout.write(f"✓ 创建通知: {notification.title}")

        self.stdout.write("✓ 示例通知已创建")
