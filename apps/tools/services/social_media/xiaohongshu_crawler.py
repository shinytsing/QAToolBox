"""
小红书爬虫服务
"""

import random
from typing import Dict, List

from django.utils import timezone

from apps.tools.models import SocialMediaSubscription

from .base_crawler import BaseSocialMediaCrawler


class XiaohongshuCrawler(BaseSocialMediaCrawler):
    """小红书爬虫服务"""

    def _crawl_xiaohongshu(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取小红书用户动态"""
        updates = []

        # 模拟数据 - 实际项目中应该调用小红书API
        if "newPosts" in subscription.subscription_types:
            if random.random() < 0.25:  # 25%概率有新动态
                post_types = ["穿搭分享", "美食探店", "旅行攻略", "护肤心得", "生活日常", "购物分享", "美妆教程"]
                post_type = random.choice(post_types)

                # 根据帖子类型生成更真实的内容
                if post_type == "穿搭分享":
                    post_content = f'今日穿搭分享！这套{random.choice(["春季", "夏季", "秋季", "冬季"])}搭配真的很适合{random.choice(["约会", "上班", "聚会", "旅行"])}，单品链接都在下面啦～'
                    tags = [post_type, "穿搭", "时尚", "分享"]
                elif post_type == "美食探店":
                    post_content = f'发现了一家超好吃的{random.choice(["火锅", "日料", "韩料", "西餐", "甜品"])}店！环境很好，味道也很棒，强烈推荐给大家～'
                    tags = [post_type, "美食", "探店", "推荐"]
                elif post_type == "旅行攻略":
                    post_content = f'刚从{random.choice(["云南", "西藏", "新疆", "海南", "四川"])}回来，整理了一份详细的旅行攻略，包含住宿、美食、景点推荐～'
                    tags = [post_type, "旅行", "攻略", "推荐"]
                else:
                    post_content = f"分享一个{post_type}的小技巧，希望对大家有帮助！记得点赞收藏哦～"
                    tags = [post_type, "分享", "推荐"]

                updates.append(
                    {
                        "type": "newPosts",
                        "title": f"{subscription.target_user_name}发布了新动态",
                        "content": f"分享了一个{post_type}，获得了{random.randint(50, 500)}个点赞...",
                        "post_content": post_content,
                        "post_images": [f"https://via.placeholder.com/300x400/ff6b6b/ffffff?text={post_type}"],
                        "post_tags": tags,
                        "post_likes": random.randint(50, 500),
                        "post_comments": random.randint(10, 100),
                        "post_shares": random.randint(5, 50),
                        "external_url": f"https://xiaohongshu.com/post/{random.randint(1000000, 9999999)}",
                        "timestamp": timezone.now(),
                    }
                )

        if "newFollowers" in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新粉丝
                follower_names = ["小红薯123", "时尚达人", "美食爱好者", "旅行家", "美妆博主", "生活分享者", "购物达人"]
                follower_name = random.choice(follower_names)
                new_followers = random.randint(1, 8)
                current_followers = random.randint(1000, 50000)

                updates.append(
                    {
                        "type": "newFollowers",
                        "title": f"{subscription.target_user_name}获得了新粉丝",
                        "content": f"新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}",
                        "follower_name": follower_name,
                        "follower_avatar": f"https://via.placeholder.com/50x50/ff6b6b/ffffff?text={follower_name[:2]}",
                        "follower_id": f"user_{random.randint(10000, 99999)}",
                        "follower_count": current_followers,
                        "new_followers": new_followers,
                        "external_url": f"https://xiaohongshu.com/user/{subscription.target_user_id}",
                        "timestamp": timezone.now(),
                    }
                )

        if "newLikes" in subscription.subscription_types:
            if random.random() < 0.3:  # 30%概率有新点赞
                post_titles = ["今日穿搭分享", "美食探店记录", "旅行攻略分享", "护肤心得", "生活日常", "购物分享", "美妆教程"]
                post_title = random.choice(post_titles)
                new_likes = random.randint(10, 100)
                total_likes = random.randint(100, 1000)

                updates.append(
                    {
                        "type": "newLikes",
                        "title": f"{subscription.target_user_name}的帖子获得了新点赞",
                        "content": f"帖子《{post_title}》新增了 {new_likes} 个点赞，总点赞数达到 {total_likes}",
                        "post_title": post_title,
                        "post_id": f"post_{random.randint(100000, 999999)}",
                        "new_likes": new_likes,
                        "total_likes": total_likes,
                        "external_url": f"https://xiaohongshu.com/post/{random.randint(1000000, 9999999)}",
                        "timestamp": timezone.now(),
                    }
                )

        return updates
