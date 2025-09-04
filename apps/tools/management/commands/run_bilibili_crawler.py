from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription
from apps.tools.services.social_media_crawler import SocialMediaCrawler, NotificationService
from django.utils import timezone


class Command(BaseCommand):
    help = "运行B站爬虫，爬取指定用户的更新"

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=str, help="要爬取的B站用户ID", default="29162776")
        parser.add_argument("--username", type=str, help="Django用户名（用于创建订阅）", default="shinytsing")
        parser.add_argument(
            "--subscription-types",
            nargs="+",
            type=str,
            default=["newPosts", "newFollowers", "newFollowing", "profileChanges"],
            help="订阅类型列表",
        )
        parser.add_argument("--check-frequency", type=int, default=5, help="检查频率（分钟）")

    def handle(self, *args, **options):
        user_id = options["user_id"]
        username = options["username"]
        subscription_types = options["subscription_types"]
        check_frequency = options["check_frequency"]

        self.stdout.write(self.style.SUCCESS(f"开始运行B站爬虫..."))
        self.stdout.write(f"目标用户ID: {user_id}")
        self.stdout.write(f"Django用户: {username}")
        self.stdout.write(f"订阅类型: {subscription_types}")
        self.stdout.write(f"检查频率: {check_frequency}分钟")
        self.stdout.write("=" * 50)

        try:
            # 获取或创建Django用户
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.com", "first_name": username, "last_name": "用户"}
            )

            if created:
                self.stdout.write(f"创建Django用户: {username}")
            else:
                self.stdout.write(f"使用现有Django用户: {username}")

            # 获取或创建B站订阅
            subscription, created = SocialMediaSubscription.objects.get_or_create(
                user=user,
                platform="bilibili",
                target_user_id=user_id,
                defaults={
                    "target_user_name": f"B站用户{user_id}",
                    "subscription_types": subscription_types,
                    "check_frequency": check_frequency,
                    "status": "active",
                },
            )

            if created:
                self.stdout.write(f"创建B站订阅: {subscription.target_user_name}")
            else:
                # 更新现有订阅
                subscription.subscription_types = subscription_types
                subscription.check_frequency = check_frequency
                subscription.save()
                self.stdout.write(f"更新B站订阅: {subscription.target_user_name}")

            # 创建爬虫实例
            crawler = SocialMediaCrawler()

            # 爬取更新
            self.stdout.write("开始爬取B站数据...")
            updates = crawler.crawl_user_updates(subscription)

            self.stdout.write(f"发现更新数量: {len(updates)}")

            if updates:
                self.stdout.write("\n更新详情:")
                for i, update in enumerate(updates, 1):
                    self.stdout.write(f'\n{i}. 类型: {update["type"]}')
                    self.stdout.write(f'   标题: {update["title"]}')
                    self.stdout.write(f'   内容: {update["content"]}')
                    self.stdout.write(f'   时间: {update["timestamp"]}')

                    # 根据类型显示详细信息
                    if update["type"] == "newPosts":
                        self.stdout.write(f'   视频链接: {update.get("post_video_url", "N/A")}')
                        self.stdout.write(f'   点赞数: {update.get("post_likes", 0)}')
                        self.stdout.write(f'   评论数: {update.get("post_comments", 0)}')
                        self.stdout.write(f'   分享数: {update.get("post_shares", 0)}')
                    elif update["type"] == "newFollowers":
                        self.stdout.write(f'   新增粉丝数: {update.get("new_followers_count", 0)}')
                        self.stdout.write(f'   当前总粉丝数: {update.get("follower_count", 0)}')
                    elif update["type"] == "newFollowing":
                        self.stdout.write(f'   关注对象: {update.get("following_name", "N/A")}')
                        self.stdout.write(f'   当前关注数: {update.get("following_count", 0)}')
                    elif update["type"] == "profileChanges":
                        changes = update.get("profile_changes", [])
                        self.stdout.write(f"   变化项数: {len(changes)}")
                        for change in changes:
                            self.stdout.write(f'     - {change["field"]}: {change["old_value"]} -> {change["new_value"]}')

                # 创建通知
                self.stdout.write("\n创建通知...")
                NotificationService.create_notifications(updates, subscription)
                self.stdout.write(self.style.SUCCESS("通知创建完成！"))

            else:
                self.stdout.write("本次检查未发现新更新")

            # 显示订阅的最新状态
            subscription.refresh_from_db()
            self.stdout.write(f"\n订阅状态更新:")
            self.stdout.write(f"最后检查时间: {subscription.last_check}")
            self.stdout.write(f"上次粉丝数: {subscription.last_follower_count}")
            self.stdout.write(f"上次视频ID: {subscription.last_video_id}")
            self.stdout.write(f"上次关注数: {subscription.last_following_count}")

            self.stdout.write(self.style.SUCCESS("\nB站爬虫运行完成！"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"运行过程中出现错误: {str(e)}"))
            import traceback

            traceback.print_exc()
