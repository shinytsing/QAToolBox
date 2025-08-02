import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from django.utils import timezone
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification


class SocialMediaCrawler:
    """社交媒体爬虫服务"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def crawl_user_updates(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取用户更新"""
        updates = []
        
        try:
            if subscription.platform == 'xiaohongshu':
                updates = self._crawl_xiaohongshu(subscription)
            elif subscription.platform == 'douyin':
                updates = self._crawl_douyin(subscription)
            elif subscription.platform == 'netease':
                updates = self._crawl_netease(subscription)
            elif subscription.platform == 'weibo':
                updates = self._crawl_weibo(subscription)
            elif subscription.platform == 'bilibili':
                updates = self._crawl_bilibili(subscription)
            elif subscription.platform == 'zhihu':
                updates = self._crawl_zhihu(subscription)
            
            # 更新最后检查时间
            subscription.last_check = timezone.now()
            subscription.save()
            
        except Exception as e:
            print(f"爬取失败 {subscription.platform} - {subscription.target_user_id}: {str(e)}")
            subscription.status = 'error'
            subscription.save()
        
        return updates
    
    def _crawl_xiaohongshu(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取小红书用户动态"""
        updates = []
        
        # 模拟数据 - 实际项目中应该调用小红书API
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.3:  # 30%概率有新动态
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新动态',
                    'content': f'分享了一套{random.choice(["春季", "夏季", "秋季", "冬季"])}穿搭，包含详细的搭配技巧和购买链接...',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.2:  # 20%概率有新关注者
                new_followers = random.randint(5, 50)
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，总关注数达到 {random.randint(1000, 50000)}',
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.1:  # 10%概率有资料变化
                changes = random.choice(['更新了头像', '修改了简介', '更改了昵称'])
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了资料',
                    'content': f'{changes}，快去看看吧！',
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_douyin(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取抖音用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.4:  # 40%概率有新视频
                video_types = ['原创歌曲', '舞蹈视频', '搞笑段子', '美食制作', '旅行vlog']
                video_type = random.choice(video_types)
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新视频',
                    'content': f'发布了一个{video_type}，获得了{random.randint(100, 10000)}个点赞...',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.25:  # 25%概率有新关注者
                new_followers = random.randint(10, 100)
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，粉丝数达到 {random.randint(5000, 100000)}',
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_netease(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取网易云音乐用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.35:  # 35%概率有新动态
                music_activities = ['发布了新歌', '分享了歌单', '发表了音乐评论', '参加了音乐活动']
                activity = random.choice(music_activities)
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}{activity}',
                    'content': f'{activity}，快来听听看吧！',
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有资料变化
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了音乐资料',
                    'content': '更新了个人简介或音乐偏好设置',
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_weibo(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取微博用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.5:  # 50%概率有新微博
                weibo_types = ['生活分享', '工作动态', '心情随笔', '热点评论', '美食分享']
                weibo_type = random.choice(weibo_types)
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新微博',
                    'content': f'发布了一条关于{weibo_type}的微博，获得了{random.randint(50, 5000)}个转发...',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.3:  # 30%概率有新关注者
                new_followers = random.randint(20, 200)
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，粉丝数达到 {random.randint(10000, 200000)}',
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_bilibili(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取B站用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.3:  # 30%概率有新视频
                video_categories = ['游戏实况', '动画解说', '科技评测', '生活分享', '音乐翻唱']
                category = random.choice(video_categories)
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新视频',
                    'content': f'发布了一个{category}视频，播放量达到{random.randint(1000, 50000)}...',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.2:  # 20%概率有新关注者
                new_followers = random.randint(15, 150)
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，粉丝数达到 {random.randint(5000, 100000)}',
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_zhihu(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取知乎用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.25:  # 25%概率有新回答
                zhihu_activities = ['回答了问题', '发布了文章', '发表了想法', '参与了讨论']
                activity = random.choice(zhihu_activities)
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}{activity}',
                    'content': f'{activity}，获得了{random.randint(10, 1000)}个赞同...',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新关注者
                new_followers = random.randint(5, 50)
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，关注数达到 {random.randint(100, 10000)}',
                    'timestamp': timezone.now()
                })
        
        return updates


class NotificationService:
    """通知服务"""
    
    @staticmethod
    def create_notifications(updates: List[Dict], subscription: SocialMediaSubscription):
        """创建通知"""
        for update in updates:
            # 检查是否已存在相同通知（避免重复）
            existing = SocialMediaNotification.objects.filter(
                subscription=subscription,
                notification_type=update['type'],
                title=update['title'],
                created_at__gte=timezone.now() - timedelta(hours=1)  # 1小时内不重复
            ).first()
            
            if not existing:
                SocialMediaNotification.objects.create(
                    subscription=subscription,
                    notification_type=update['type'],
                    title=update['title'],
                    content=update['content']
                )
    
    @staticmethod
    def get_unread_count(user) -> int:
        """获取未读通知数量"""
        return SocialMediaNotification.objects.filter(
            subscription__user=user,
            is_read=False
        ).count()


def run_crawler_task():
    """运行爬虫任务"""
    crawler = SocialMediaCrawler()
    notification_service = NotificationService()
    
    # 获取所有活跃的订阅
    active_subscriptions = SocialMediaSubscription.objects.filter(
        status='active'
    )
    
    print(f"开始检查 {active_subscriptions.count()} 个活跃订阅...")
    
    for subscription in active_subscriptions:
        try:
            # 检查是否需要更新（基于检查频率）
            last_check = subscription.last_check or subscription.created_at
            check_interval = timedelta(minutes=subscription.check_frequency)
            
            if timezone.now() - last_check >= check_interval:
                print(f"检查订阅: {subscription.target_user_name} ({subscription.get_platform_display()})")
                
                # 爬取更新
                updates = crawler.crawl_user_updates(subscription)
                
                if updates:
                    # 创建通知
                    notification_service.create_notifications(updates, subscription)
                    print(f"发现 {len(updates)} 个更新")
                
                # 添加延迟避免请求过于频繁
                time.sleep(random.uniform(1, 3))
        
        except Exception as e:
            print(f"处理订阅失败 {subscription.id}: {str(e)}")
            continue
    
    print("爬虫任务完成")


if __name__ == "__main__":
    run_crawler_task() 