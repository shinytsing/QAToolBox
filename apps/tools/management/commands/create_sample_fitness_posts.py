"""
创建示例健身社区帖子的管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tools.models.legacy_models import FitnessCommunityPost


class Command(BaseCommand):
    help = "创建示例健身社区帖子"

    def handle(self, *args, **options):
        # 获取或创建测试用户
        user, created = User.objects.get_or_create(
            username="健身达人", defaults={"email": "fitness@example.com", "first_name": "健身", "last_name": "达人"}
        )

        if created:
            self.stdout.write(f"创建用户: {user.username}")
        else:
            self.stdout.write(f"使用现有用户: {user.username}")

        # 示例帖子数据
        sample_posts = [
            {
                "post_type": "checkin",
                "title": "今日训练打卡",
                "content": "今天完成了30分钟的有氧训练，感觉超棒！坚持了一个月，体重已经减了5公斤，继续加油！💪",
                "tags": ["有氧训练", "减脂", "坚持"],
                "training_parts": ["全身"],
                "difficulty_level": "beginner",
                "likes_count": 24,
                "comments_count": 8,
                "shares_count": 3,
            },
            {
                "post_type": "plan",
                "title": "增肌训练计划分享",
                "content": "分享一个适合初学者的增肌训练计划，包含胸、背、腿、肩、臂五个部位的训练。每个部位每周训练一次，循序渐进。",
                "tags": ["增肌", "训练计划", "初学者"],
                "training_parts": ["胸部", "背部", "腿部", "肩部", "手臂"],
                "difficulty_level": "beginner",
                "likes_count": 56,
                "comments_count": 15,
                "shares_count": 12,
            },
            {
                "post_type": "achievement",
                "title": "减重成功！",
                "content": "坚持健身3个月，成功减重10公斤！从85kg减到75kg，体脂率从25%降到18%。感谢自己的坚持！",
                "tags": ["减重", "成就", "坚持"],
                "training_parts": ["全身"],
                "difficulty_level": "intermediate",
                "likes_count": 89,
                "comments_count": 23,
                "shares_count": 18,
            },
            {
                "post_type": "motivation",
                "title": "健身改变生活",
                "content": "健身不仅改变了我的身材，更改变了我的生活态度。每天早起训练让我更有活力，更有自信面对每一天的挑战！",
                "tags": ["励志", "生活改变", "正能量"],
                "training_parts": ["全身"],
                "difficulty_level": "beginner",
                "likes_count": 67,
                "comments_count": 19,
                "shares_count": 25,
            },
            {
                "post_type": "question",
                "title": "新手如何开始健身？",
                "content": "我是健身新手，想开始健身但不知道从哪里开始。请问有什么建议吗？需要准备什么装备？",
                "tags": ["新手", "求助", "健身入门"],
                "training_parts": ["全身"],
                "difficulty_level": "beginner",
                "likes_count": 12,
                "comments_count": 34,
                "shares_count": 2,
            },
        ]

        created_count = 0
        for post_data in sample_posts:
            # 检查是否已存在相同的帖子
            existing_post = FitnessCommunityPost.objects.filter(user=user, title=post_data["title"]).first()

            if not existing_post:
                post = FitnessCommunityPost.objects.create(user=user, **post_data)
                created_count += 1
                self.stdout.write(f"创建帖子: {post.title}")
            else:
                self.stdout.write(f'帖子已存在: {post_data["title"]}')

        self.stdout.write(self.style.SUCCESS(f"成功创建 {created_count} 个示例帖子"))
