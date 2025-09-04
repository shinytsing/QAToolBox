"""
社交媒体爬虫任务调度服务
"""

import time
import random
from datetime import datetime, timedelta
from typing import List
from django.utils import timezone
from django.core.management.base import BaseCommand
from apps.tools.models import SocialMediaSubscription
from .xiaohongshu_crawler import XiaohongshuCrawler
from .notification_service import NotificationService


class SocialMediaScheduler:
    """社交媒体爬虫任务调度器"""

    def __init__(self):
        self.crawler = XiaohongshuCrawler()
        self.notification_service = NotificationService()

    def run_crawler_task(self):
        """运行爬虫任务"""
        print(f"开始运行社交媒体爬虫任务 - {timezone.now()}")

        # 获取所有活跃的订阅
        active_subscriptions = SocialMediaSubscription.objects.filter(status="active", is_active=True)

        total_updates = 0

        for subscription in active_subscriptions:
            try:
                print(f"爬取 {subscription.platform} - {subscription.target_user_name}")

                # 爬取更新
                updates = self.crawler.crawl_user_updates(subscription)

                if updates:
                    # 创建通知
                    self.notification_service.create_notifications(updates, subscription)
                    total_updates += len(updates)
                    print(f"发现 {len(updates)} 个更新")

                # 随机延迟，避免被反爬
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"爬取失败 {subscription.platform} - {subscription.target_user_name}: {str(e)}")
                subscription.status = "error"
                subscription.save()

        print(f"爬虫任务完成，共发现 {total_updates} 个更新")
        return total_updates

    def run_continuous_crawler(self, interval_minutes: int = 30):
        """运行持续爬虫"""
        print(f"启动持续爬虫，检查间隔: {interval_minutes} 分钟")

        while True:
            try:
                self.run_crawler_task()

                # 等待下次检查
                print(f"等待 {interval_minutes} 分钟后进行下次检查...")
                time.sleep(interval_minutes * 60)

            except KeyboardInterrupt:
                print("收到中断信号，停止爬虫")
                break
            except Exception as e:
                print(f"爬虫运行出错: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再重试

    def cleanup_old_data(self, days: int = 30):
        """清理旧数据"""
        print(f"清理 {days} 天前的旧数据")

        # 清理旧通知
        deleted_notifications = self.notification_service.delete_old_notifications(days)
        print(f"删除了 {deleted_notifications} 个旧通知")

        # 清理错误状态的订阅
        error_subscriptions = SocialMediaSubscription.objects.filter(
            status="error", updated_at__lt=timezone.now() - timedelta(days=7)
        )
        error_count = error_subscriptions.count()
        error_subscriptions.delete()
        print(f"删除了 {error_count} 个错误状态的订阅")


class CrawlerCommand(BaseCommand):
    """Django管理命令"""

    help = "运行社交媒体爬虫任务"

    def add_arguments(self, parser):
        parser.add_argument(
            "--continuous",
            action="store_true",
            help="运行持续爬虫",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="检查间隔（分钟）",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="清理旧数据",
        )

    def handle(self, *args, **options):
        scheduler = SocialMediaScheduler()

        if options["cleanup"]:
            scheduler.cleanup_old_data()

        if options["continuous"]:
            scheduler.run_continuous_crawler(options["interval"])
        else:
            scheduler.run_crawler_task()
