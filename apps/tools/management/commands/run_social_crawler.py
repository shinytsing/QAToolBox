import random
import time
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.tools.models import SocialMediaNotification, SocialMediaSubscription
from apps.tools.services.social_media_crawler import run_continuous_crawler


class Command(BaseCommand):
    help = "运行社交媒体爬虫任务"

    def add_arguments(self, parser):
        parser.add_argument("--continuous", action="store_true", help="持续运行爬虫任务")
        parser.add_argument("--interval", type=int, default=300, help="检查间隔时间（秒），默认300秒（5分钟）")
        parser.add_argument("--subscription-id", type=int, help="指定订阅ID进行单次检查")

    def handle(self, *args, **options):
        continuous = options.get("continuous")
        interval = options.get("interval")
        subscription_id = options.get("subscription_id")

        if subscription_id:
            # 检查指定订阅
            try:
                subscription = SocialMediaSubscription.objects.get(id=subscription_id)
                self.check_subscription(subscription)
                self.stdout.write(self.style.SUCCESS(f"完成订阅 {subscription.target_user_name} 的检查"))
            except SocialMediaSubscription.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"订阅ID {subscription_id} 不存在"))
            return

        if continuous:
            self.stdout.write(self.style.SUCCESS("开始持续运行爬虫任务，根据订阅频率自动调度"))
            try:
                run_continuous_crawler()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("爬虫任务已停止"))
        else:
            # 单次运行
            self.stdout.write("开始单次爬虫任务...")
            self.run_crawler_cycle()
            self.stdout.write(self.style.SUCCESS("爬虫任务完成"))

    def run_crawler_cycle(self):
        """运行一轮爬虫检查"""
        # 获取需要检查的活跃订阅
        active_subscriptions = SocialMediaSubscription.objects.filter(status="active").select_related("user")

        if not active_subscriptions.exists():
            self.stdout.write("没有找到活跃的订阅")
            return

        self.stdout.write(f"开始检查 {active_subscriptions.count()} 个活跃订阅...")

        for subscription in active_subscriptions:
            try:
                self.check_subscription(subscription)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"检查订阅 {subscription.target_user_name} 时出错: {str(e)}"))
                # 标记订阅为错误状态
                subscription.status = "error"
                subscription.save()

        # 更新最后检查时间
        active_subscriptions.update(last_check=timezone.now())

    def check_subscription(self, subscription):
        """检查单个订阅"""
        self.stdout.write(f"检查订阅: {subscription.target_user_name} ({subscription.get_platform_display()})")

        # 模拟检查过程
        time.sleep(0.5)  # 模拟网络请求延迟

        # 根据订阅类型生成模拟通知
        for notification_type in subscription.subscription_types:
            if self.should_generate_notification(subscription, notification_type):
                self.generate_notification(subscription, notification_type)

    def should_generate_notification(self, subscription, notification_type):
        """判断是否应该生成通知（模拟逻辑）"""
        # 模拟30%的概率生成通知
        return random.random() < 0.3

    def generate_notification(self, subscription, notification_type):
        """生成通知"""
        notification_data = self.get_notification_template(subscription, notification_type)

        notification = SocialMediaNotification.objects.create(
            subscription=subscription,
            notification_type=notification_type,
            title=notification_data["title"],
            content=notification_data["content"],
            is_read=False,
        )

        self.stdout.write(self.style.SUCCESS(f"✓ 生成通知: {notification.title}"))

    def get_notification_template(self, subscription, notification_type):
        """获取通知模板"""
        templates = {
            "newPosts": [
                {
                    "title": f"{subscription.target_user_name} 发布了新内容",
                    "content": f"刚刚在{subscription.get_platform_display()}发布了一篇精彩的内容，快去看看吧！",
                },
                {"title": f"{subscription.target_user_name} 更新了动态", "content": f"有新的动态更新，内容很有趣哦～"},
                {"title": f"{subscription.target_user_name} 分享了新作品", "content": f"新作品上线了，质量很高，值得关注！"},
            ],
            "newFollowers": [
                {"title": f"{subscription.target_user_name} 新增关注者", "content": f"获得了新的关注者，粉丝数量又增加了！"},
                {"title": f"{subscription.target_user_name} 粉丝增长", "content": f"粉丝数量突破新纪录，影响力在扩大！"},
            ],
            "profileChanges": [
                {
                    "title": f"{subscription.target_user_name} 更新了个人资料",
                    "content": f"个人资料有新的变化，可能更新了头像或简介。",
                },
                {"title": f"{subscription.target_user_name} 修改了签名", "content": f"个人签名有更新，看看有什么新想法！"},
            ],
        }

        return random.choice(
            templates.get(
                notification_type,
                [
                    {
                        "title": f"{subscription.target_user_name} 有新的活动",
                        "content": f"在{subscription.get_platform_display()}上有新的活动发生。",
                    }
                ],
            )
        )
