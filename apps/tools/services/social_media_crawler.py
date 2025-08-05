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
            if random.random() < 0.25:  # 25%概率有新动态
                post_types = ['穿搭分享', '美食探店', '旅行攻略', '护肤心得', '生活日常', '购物分享', '美妆教程']
                post_type = random.choice(post_types)
                
                # 根据帖子类型生成更真实的内容
                if post_type == '穿搭分享':
                    post_content = f'今日穿搭分享！这套{random.choice(["春季", "夏季", "秋季", "冬季"])}搭配真的很适合{random.choice(["约会", "上班", "聚会", "旅行"])}，单品链接都在下面啦～'
                    tags = [post_type, '穿搭', '时尚', '分享']
                elif post_type == '美食探店':
                    post_content = f'发现了一家超好吃的{random.choice(["火锅", "日料", "韩料", "西餐", "甜品"])}店！环境很好，味道也很棒，强烈推荐给大家～'
                    tags = [post_type, '美食', '探店', '推荐']
                elif post_type == '旅行攻略':
                    post_content = f'刚从{random.choice(["云南", "西藏", "新疆", "海南", "四川"])}回来，整理了一份详细的旅行攻略，包含住宿、美食、景点推荐～'
                    tags = [post_type, '旅行', '攻略', '推荐']
                else:
                    post_content = f'分享一个{post_type}的小技巧，希望对大家有帮助！记得点赞收藏哦～'
                    tags = [post_type, '分享', '推荐']
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新动态',
                    'content': f'分享了一个{post_type}，获得了{random.randint(50, 500)}个点赞...',
                    'post_content': post_content,
                    'post_images': [f'https://via.placeholder.com/300x400/ff6b6b/ffffff?text={post_type}'],
                    'post_tags': tags,
                    'post_likes': random.randint(50, 500),
                    'post_comments': random.randint(10, 100),
                    'post_shares': random.randint(5, 50),
                    'external_url': f'https://xiaohongshu.com/post/{random.randint(1000000, 9999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新粉丝
                follower_names = ['小红薯123', '时尚达人', '美食爱好者', '旅行家', '美妆博主', '生活分享者', '购物达人']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(1, 8)
                current_followers = random.randint(1000, 50000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}获得了新粉丝',
                    'content': f'新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://via.placeholder.com/50x50/ff6b6b/ffffff?text={follower_name[:2]}',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.1:  # 10%概率有新关注
                following_names = ['知名博主', '时尚达人', '美食专家', '旅行博主', '美妆达人', '生活博主', '购物达人']
                following_name = random.choice(following_names)
                current_following = random.randint(100, 1000)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://via.placeholder.com/50x50/4ecdc4/ffffff?text={following_name[:2]}',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.08:  # 8%概率有资料变化
                changes = ['更新了头像', '修改了简介', '更改了昵称', '更新了个人资料']
                change = random.choice(changes)
                
                if change == '更新了头像':
                    old_data = {'avatar': '旧头像.jpg'}
                    new_data = {'avatar': '新头像.jpg'}
                elif change == '修改了简介':
                    old_data = {'bio': '旧简介：分享生活点滴'}
                    new_data = {'bio': '新简介：热爱生活，分享美好'}
                elif change == '更改了昵称':
                    old_data = {'nickname': '旧昵称'}
                    new_data = {'nickname': '新昵称'}
                else:
                    old_data = {'profile': '旧资料'}
                    new_data = {'profile': '新资料'}
                
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了资料',
                    'content': f'{change}，快去看看吧！',
                    'profile_changes': {'change_type': change},
                    'old_profile_data': old_data,
                    'new_profile_data': new_data,
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_douyin(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取抖音用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.4:  # 40%概率有新视频
                video_types = ['原创歌曲', '舞蹈视频', '搞笑段子', '美食制作', '旅行vlog', '生活分享', '技能教学']
                video_type = random.choice(video_types)
                video_content = f'今天给大家分享一个{video_type}，希望大家喜欢！记得点赞关注哦～'
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新视频',
                    'content': f'发布了一个{video_type}，获得了{random.randint(100, 10000)}个点赞...',
                    'post_content': video_content,
                    'post_video_url': f'https://douyin.com/video/{random.randint(1000000, 9999999)}',
                    'post_images': [f'https://example.com/thumbnail_{random.randint(1, 5)}.jpg'],
                    'post_tags': [video_type, '抖音', '分享'],
                    'post_likes': random.randint(100, 10000),
                    'post_comments': random.randint(20, 500),
                    'post_shares': random.randint(10, 200),
                    'external_url': f'https://douyin.com/video/{random.randint(1000000, 9999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.25:  # 25%概率有新粉丝
                follower_names = ['抖音用户123', '音乐爱好者', '舞蹈达人', '美食家', '旅行者']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(1, 20)
                current_followers = random.randint(5000, 100000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}获得了新粉丝',
                    'content': f'新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://example.com/avatar_{random.randint(1, 10)}.jpg',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.2:  # 20%概率有新关注
                following_names = ['知名UP主', '音乐人', '舞蹈老师', '美食博主', '旅行达人']
                following_name = random.choice(following_names)
                current_following = random.randint(200, 2000)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://example.com/avatar_{random.randint(1, 10)}.jpg',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
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
                
                # 根据活动类型生成更真实的内容
                if activity == '发布了新歌':
                    song_types = ['流行', '摇滚', '民谣', '电子', '古典', '爵士', '说唱']
                    song_type = random.choice(song_types)
                    song_content = f'发布了一首新的{song_type}歌曲，希望大家喜欢！'
                    tags = ['新歌', song_type, '音乐']
                elif activity == '分享了歌单':
                    playlist_types = ['心情歌单', '工作歌单', '运动歌单', '睡前歌单', '旅行歌单']
                    playlist_type = random.choice(playlist_types)
                    song_content = f'分享了一个{playlist_type}，包含了很多好听的歌曲～'
                    tags = ['歌单', playlist_type, '分享']
                elif activity == '发表了音乐评论':
                    song_content = f'对一首歌发表了评论，分享了自己的感受和想法...'
                    tags = ['评论', '音乐', '分享']
                else:
                    song_content = f'参加了一个音乐活动，现场很精彩，和大家分享一下...'
                    tags = ['活动', '音乐', '分享']
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}{activity}',
                    'content': f'{activity}，快来听听看吧！',
                    'post_content': song_content,
                    'post_images': [f'https://via.placeholder.com/300x300/c20c0c/ffffff?text=音乐'],
                    'post_tags': tags,
                    'post_likes': random.randint(20, 200),
                    'post_comments': random.randint(5, 50),
                    'post_shares': random.randint(1, 20),
                    'external_url': f'https://music.163.com/song?id={random.randint(1000000, 9999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.2:  # 20%概率有新粉丝
                follower_names = ['音乐爱好者', '歌迷', '音乐人', '乐评人', '音乐制作人', '歌手', '音乐老师']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(1, 15)
                current_followers = random.randint(500, 10000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}获得了新粉丝',
                    'content': f'新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://via.placeholder.com/50x50/c20c0c/ffffff?text={follower_name[:2]}',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新关注
                following_names = ['知名歌手', '音乐制作人', '乐评人', '音乐博主', '音乐老师', '音乐人', '歌迷']
                following_name = random.choice(following_names)
                current_following = random.randint(50, 500)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://via.placeholder.com/50x50/c20c0c/ffffff?text={following_name[:2]}',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有资料变化
                changes = ['更新了头像', '修改了简介', '更改了昵称', '更新了音乐偏好']
                change = random.choice(changes)
                
                if change == '更新了头像':
                    old_data = {'avatar': '旧头像.jpg'}
                    new_data = {'avatar': '新头像.jpg'}
                elif change == '修改了简介':
                    old_data = {'bio': '旧简介：热爱音乐'}
                    new_data = {'bio': '新简介：音乐是我的生命'}
                elif change == '更改了昵称':
                    old_data = {'nickname': '旧昵称'}
                    new_data = {'nickname': '新昵称'}
                else:
                    old_data = {'music_preference': '旧偏好'}
                    new_data = {'music_preference': '新偏好'}
                
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了音乐资料',
                    'content': f'{change}，快去看看吧！',
                    'profile_changes': {'change_type': change},
                    'old_profile_data': old_data,
                    'new_profile_data': new_data,
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
                
                # 根据微博类型生成更真实的内容
                if weibo_type == '生活分享':
                    weibo_content = f'今天天气真好，{random.choice(["去公园散步", "在家看书", "和朋友聚会", "做家务"])}，心情很愉快～'
                elif weibo_type == '工作动态':
                    weibo_content = f'今天工作很忙，{random.choice(["完成了重要项目", "参加了会议", "处理了很多邮件", "学习了新技能"])}，虽然累但很有成就感！'
                elif weibo_type == '心情随笔':
                    weibo_content = f'最近{random.choice(["心情不错", "有点小烦恼", "很充实", "需要放松"])}，{random.choice(["希望明天会更好", "相信一切都会好起来", "继续加油", "保持积极心态"])}'
                elif weibo_type == '热点评论':
                    weibo_content = f'关于{random.choice(["最近的新闻", "热门话题", "社会现象", "科技发展"])}，我觉得{random.choice(["很有意思", "值得思考", "需要关注", "很有意义"])}'
                else:
                    weibo_content = f'分享一个{weibo_type}，{random.choice(["味道很棒", "做法简单", "营养丰富", "很受欢迎"])}，推荐给大家！'
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新微博',
                    'content': f'发布了一条关于{weibo_type}的微博，获得了{random.randint(50, 5000)}个转发...',
                    'post_content': weibo_content,
                    'post_images': [f'https://via.placeholder.com/400x300/e74c3c/ffffff?text={weibo_type}'],
                    'post_tags': [weibo_type, '微博', '分享'],
                    'post_likes': random.randint(50, 5000),
                    'post_comments': random.randint(10, 500),
                    'post_shares': random.randint(5, 200),
                    'external_url': f'https://weibo.com/status/{random.randint(1000000000, 9999999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.3:  # 30%概率有新关注者
                follower_names = ['微博用户123', '生活分享者', '工作达人', '美食爱好者', '旅行家', '科技迷', '音乐爱好者']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(20, 200)
                current_followers = random.randint(10000, 200000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，粉丝数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://via.placeholder.com/50x50/e74c3c/ffffff?text={follower_name[:2]}',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新关注
                following_names = ['知名博主', '生活达人', '工作专家', '美食博主', '旅行达人', '科技博主', '音乐人']
                following_name = random.choice(following_names)
                current_following = random.randint(500, 5000)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://via.placeholder.com/50x50/e74c3c/ffffff?text={following_name[:2]}',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.1:  # 10%概率有资料变化
                changes = ['更新了头像', '修改了简介', '更改了昵称', '更新了个人资料']
                change = random.choice(changes)
                
                if change == '更新了头像':
                    old_data = {'avatar': '旧头像.jpg'}
                    new_data = {'avatar': '新头像.jpg'}
                elif change == '修改了简介':
                    old_data = {'bio': '旧简介：分享生活点滴'}
                    new_data = {'bio': '新简介：热爱生活，分享美好'}
                elif change == '更改了昵称':
                    old_data = {'nickname': '旧昵称'}
                    new_data = {'nickname': '新昵称'}
                else:
                    old_data = {'profile': '旧资料'}
                    new_data = {'profile': '新资料'}
                
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了资料',
                    'content': f'{change}，快去看看吧！',
                    'profile_changes': {'change_type': change},
                    'old_profile_data': old_data,
                    'new_profile_data': new_data,
                    'timestamp': timezone.now()
                })
        
        return updates
    
    def _crawl_bilibili(self, subscription: SocialMediaSubscription) -> List[Dict]:
        """爬取B站用户动态"""
        updates = []
        
        if 'newPosts' in subscription.subscription_types:
            if random.random() < 0.25:  # 25%概率有新视频
                video_categories = ['游戏实况', '动画解说', '科技评测', '生活分享', '音乐翻唱', '编程教程', '美食制作', '知识科普', '搞笑视频']
                category = random.choice(video_categories)
                
                # 根据视频类型生成更真实的内容
                if category == '游戏实况':
                    games = ['原神', '王者荣耀', '英雄联盟', '和平精英', '我的世界']
                    game = random.choice(games)
                    video_content = f'今天给大家带来{game}的实况视频！这局游戏真的很精彩，希望大家喜欢，记得一键三连哦～'
                    tags = [category, game, '实况', '游戏']
                elif category == '动画解说':
                    anime = ['火影忍者', '海贼王', '进击的巨人', '鬼灭之刃', '咒术回战']
                    anime_name = random.choice(anime)
                    video_content = f'为大家解说{anime_name}的最新剧情！这集真的很精彩，一起来分析一下吧～'
                    tags = [category, anime_name, '解说', '动画']
                elif category == '科技评测':
                    tech = ['手机', '电脑', '耳机', '相机', '平板']
                    tech_item = random.choice(tech)
                    video_content = f'深度评测这款{tech_item}！从性能到体验，全方位为大家分析，希望对大家有帮助～'
                    tags = [category, tech_item, '评测', '科技']
                else:
                    video_content = f'分享一个{category}视频，希望大家喜欢！记得点赞关注哦～'
                    tags = [category, '分享', 'B站']
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}发布了新视频',
                    'content': f'发布了一个{category}视频，播放量达到{random.randint(1000, 50000)}...',
                    'post_content': video_content,
                    'post_video_url': f'https://www.bilibili.com/video/BV{random.randint(10000000, 99999999)}',
                    'post_images': [f'https://via.placeholder.com/300x200/00a1d6/ffffff?text={category}'],
                    'post_tags': tags,
                    'post_likes': random.randint(100, 5000),
                    'post_comments': random.randint(20, 300),
                    'post_shares': random.randint(10, 100),
                    'external_url': f'https://www.bilibili.com/video/BV{random.randint(10000000, 99999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新粉丝
                follower_names = ['B站用户123', '游戏爱好者', '动画迷', '科技达人', '美食家', '音乐爱好者', '知识分享者']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(1, 12)
                current_followers = random.randint(5000, 100000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}获得了新粉丝',
                    'content': f'新增了 {new_followers} 个粉丝，当前粉丝数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://via.placeholder.com/50x50/00a1d6/ffffff?text={follower_name[:2]}',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.1:  # 10%概率有新关注
                following_names = ['知名UP主', '游戏主播', '动画制作人', '科技博主', '美食UP主', '音乐UP主', '知识UP主']
                following_name = random.choice(following_names)
                current_following = random.randint(100, 1000)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://via.placeholder.com/50x50/00a1d6/ffffff?text={following_name[:2]}',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.08:  # 8%概率有资料变化
                changes = ['更新了头像', '修改了简介', '更改了昵称', '更新了个人资料']
                change = random.choice(changes)
                
                if change == '更新了头像':
                    old_data = {'avatar': '旧头像.jpg'}
                    new_data = {'avatar': '新头像.jpg'}
                elif change == '修改了简介':
                    old_data = {'bio': '旧简介：分享有趣的内容'}
                    new_data = {'bio': '新简介：热爱创作，分享快乐'}
                elif change == '更改了昵称':
                    old_data = {'nickname': '旧昵称'}
                    new_data = {'nickname': '新昵称'}
                else:
                    old_data = {'profile': '旧资料'}
                    new_data = {'profile': '新资料'}
                
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了资料',
                    'content': f'{change}，快去看看吧！',
                    'profile_changes': {'change_type': change},
                    'old_profile_data': old_data,
                    'new_profile_data': new_data,
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
                
                # 根据活动类型生成更真实的内容
                if activity == '回答了问题':
                    questions = ['如何提高工作效率？', '有什么好的学习方法？', '如何保持健康的生活方式？', '推荐一些好书？', '如何学习编程？']
                    question = random.choice(questions)
                    answer_content = f'关于"{question}"这个问题，我想分享一下我的经验和看法...'
                    tags = ['回答', '经验分享', '建议']
                elif activity == '发布了文章':
                    article_types = ['技术分享', '生活感悟', '读书笔记', '职场经验', '学习心得']
                    article_type = random.choice(article_types)
                    answer_content = f'写了一篇关于{article_type}的文章，希望对大家有帮助...'
                    tags = ['文章', article_type, '分享']
                elif activity == '发表了想法':
                    thoughts = ['今天学到了新知识', '对某个话题有了新的思考', '分享一个小发现', '记录一下今天的感悟']
                    thought = random.choice(thoughts)
                    answer_content = f'{thought}，想和大家分享一下...'
                    tags = ['想法', '分享', '感悟']
                else:
                    answer_content = f'参与了一个有趣的讨论，学到了很多...'
                    tags = ['讨论', '交流', '学习']
                
                updates.append({
                    'type': 'newPosts',
                    'title': f'{subscription.target_user_name}{activity}',
                    'content': f'{activity}，获得了{random.randint(10, 1000)}个赞同...',
                    'post_content': answer_content,
                    'post_images': [f'https://via.placeholder.com/400x300/0084ff/ffffff?text={activity}'],
                    'post_tags': tags,
                    'post_likes': random.randint(10, 1000),
                    'post_comments': random.randint(5, 100),
                    'post_shares': random.randint(1, 50),
                    'external_url': f'https://www.zhihu.com/question/{random.randint(100000000, 999999999)}',
                    'timestamp': timezone.now()
                })
        
        if 'newFollowers' in subscription.subscription_types:
            if random.random() < 0.15:  # 15%概率有新关注者
                follower_names = ['知乎用户123', '知识分享者', '技术达人', '生活博主', '学习爱好者', '职场达人', '读书人']
                follower_name = random.choice(follower_names)
                new_followers = random.randint(5, 50)
                current_followers = random.randint(100, 10000)
                
                updates.append({
                    'type': 'newFollowers',
                    'title': f'{subscription.target_user_name}新增关注者',
                    'content': f'新增了 {new_followers} 个关注者，关注数达到 {current_followers}',
                    'follower_name': follower_name,
                    'follower_avatar': f'https://via.placeholder.com/50x50/0084ff/ffffff?text={follower_name[:2]}',
                    'follower_id': f'user_{random.randint(10000, 99999)}',
                    'follower_count': current_followers,
                    'new_followers_count': new_followers,
                    'timestamp': timezone.now()
                })
        
        if 'newFollowing' in subscription.subscription_types:
            if random.random() < 0.1:  # 10%概率有新关注
                following_names = ['知名答主', '技术专家', '生活达人', '学习博主', '职场导师', '读书达人', '知识分享者']
                following_name = random.choice(following_names)
                current_following = random.randint(50, 500)
                
                updates.append({
                    'type': 'newFollowing',
                    'title': f'{subscription.target_user_name}关注了新用户',
                    'content': f'新关注了 {following_name}，当前关注数达到 {current_following}',
                    'following_name': following_name,
                    'following_avatar': f'https://via.placeholder.com/50x50/0084ff/ffffff?text={following_name[:2]}',
                    'following_id': f'user_{random.randint(10000, 99999)}',
                    'following_count': current_following,
                    'new_following_count': 1,
                    'timestamp': timezone.now()
                })
        
        if 'profileChanges' in subscription.subscription_types:
            if random.random() < 0.08:  # 8%概率有资料变化
                changes = ['更新了头像', '修改了简介', '更改了昵称', '更新了个人资料']
                change = random.choice(changes)
                
                if change == '更新了头像':
                    old_data = {'avatar': '旧头像.jpg'}
                    new_data = {'avatar': '新头像.jpg'}
                elif change == '修改了简介':
                    old_data = {'bio': '旧简介：分享知识和经验'}
                    new_data = {'bio': '新简介：热爱学习，分享智慧'}
                elif change == '更改了昵称':
                    old_data = {'nickname': '旧昵称'}
                    new_data = {'nickname': '新昵称'}
                else:
                    old_data = {'profile': '旧资料'}
                    new_data = {'profile': '新资料'}
                
                updates.append({
                    'type': 'profileChanges',
                    'title': f'{subscription.target_user_name}更新了资料',
                    'content': f'{change}，快去看看吧！',
                    'profile_changes': {'change_type': change},
                    'old_profile_data': old_data,
                    'new_profile_data': new_data,
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
                # 创建通知对象，包含所有可能的字段
                notification_data = {
                    'subscription': subscription,
                    'notification_type': update['type'],
                    'title': update['title'],
                    'content': update['content'],
                }
                
                # 根据通知类型添加特定字段
                if update['type'] == 'newPosts':
                    notification_data.update({
                        'post_content': update.get('post_content', ''),
                        'post_images': update.get('post_images', []),
                        'post_video_url': update.get('post_video_url', ''),
                        'post_tags': update.get('post_tags', []),
                        'post_likes': update.get('post_likes', 0),
                        'post_comments': update.get('post_comments', 0),
                        'post_shares': update.get('post_shares', 0),
                        'external_url': update.get('external_url', ''),
                    })
                
                elif update['type'] == 'newFollowers':
                    notification_data.update({
                        'follower_name': update.get('follower_name', ''),
                        'follower_avatar': update.get('follower_avatar', ''),
                        'follower_id': update.get('follower_id', ''),
                        'follower_count': update.get('follower_count', 0),
                    })
                
                elif update['type'] == 'newFollowing':
                    notification_data.update({
                        'following_name': update.get('following_name', ''),
                        'following_avatar': update.get('following_avatar', ''),
                        'following_id': update.get('following_id', ''),
                        'following_count': update.get('following_count', 0),
                    })
                
                elif update['type'] == 'profileChanges':
                    notification_data.update({
                        'profile_changes': update.get('profile_changes', {}),
                        'old_profile_data': update.get('old_profile_data', {}),
                        'new_profile_data': update.get('new_profile_data', {}),
                    })
                
                # 添加平台特定数据
                notification_data['platform_specific_data'] = update.get('platform_specific_data', {})
                
                SocialMediaNotification.objects.create(**notification_data)
    
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
                    print(f"✓ 生成通知: {subscription.target_user_name} {updates[0]['title'].split('发布了')[0] if '发布了' in updates[0]['title'] else updates[0]['title'].split('获得了')[0] if '获得了' in updates[0]['title'] else updates[0]['title'].split('关注了')[0] if '关注了' in updates[0]['title'] else updates[0]['title'].split('更新了')[0] if '更新了' in updates[0]['title'] else '有新的活动'}")
                else:
                    print(f"检查订阅: {subscription.target_user_name} ({subscription.get_platform_display()}) - 无更新")
                
                # 添加延迟避免请求过于频繁
                time.sleep(random.uniform(1, 3))
            else:
                # 计算下次检查时间
                next_check = last_check + check_interval
                print(f"跳过订阅: {subscription.target_user_name} ({subscription.get_platform_display()}) - 下次检查: {next_check.strftime('%H:%M:%S')}")
        
        except Exception as e:
            print(f"处理订阅失败 {subscription.id}: {str(e)}")
            continue
    
    print("爬虫任务完成")


def run_continuous_crawler():
    """持续运行爬虫任务，根据订阅频率自动调度"""
    print("启动持续爬虫任务...")
    print("按 Ctrl+C 停止")
    
    try:
        while True:
            print(f"\n[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始新一轮检查...")
            
            # 获取所有活跃的订阅
            active_subscriptions = SocialMediaSubscription.objects.filter(
                status='active'
            )
            
            if not active_subscriptions.exists():
                print("没有活跃订阅，等待5分钟后重试...")
                time.sleep(300)
                continue
            
            # 检查每个订阅是否需要更新
            checked_count = 0
            for subscription in active_subscriptions:
                try:
                    # 检查是否需要更新（基于检查频率）
                    last_check = subscription.last_check or subscription.created_at
                    check_interval = timedelta(minutes=subscription.check_frequency)
                    
                    if timezone.now() - last_check >= check_interval:
                        print(f"检查订阅: {subscription.target_user_name} ({subscription.get_platform_display()}) - 频率: {subscription.check_frequency}分钟")
                        
                        # 爬取更新
                        crawler = SocialMediaCrawler()
                        updates = crawler.crawl_user_updates(subscription)
                        
                        if updates:
                            # 创建通知
                            notification_service = NotificationService()
                            notification_service.create_notifications(updates, subscription)
                            
                            # 生成简化的通知描述
                            update_type = updates[0]['type']
                            if update_type == 'newPosts':
                                desc = '发布了新内容'
                            elif update_type == 'newFollowers':
                                desc = '获得了新粉丝'
                            elif update_type == 'newFollowing':
                                desc = '关注了新用户'
                            elif update_type == 'profileChanges':
                                desc = '更新了资料'
                            else:
                                desc = '有新的活动'
                            
                            print(f"  ✓ 生成通知: {subscription.target_user_name} {desc}")
                        else:
                            print(f"  - 无更新")
                        
                        # 更新最后检查时间
                        subscription.last_check = timezone.now()
                        subscription.save()
                        
                        checked_count += 1
                        
                        # 添加延迟避免请求过于频繁
                        time.sleep(random.uniform(1, 2))
                    else:
                        # 计算剩余时间
                        remaining = check_interval - (timezone.now() - last_check)
                        remaining_minutes = int(remaining.total_seconds() / 60)
                        if remaining_minutes < 5:  # 只显示5分钟内的等待
                            print(f"跳过: {subscription.target_user_name} - 还需等待 {remaining_minutes} 分钟")
                
                except Exception as e:
                    print(f"错误: {subscription.target_user_name} - {str(e)}")
                    # 标记订阅为错误状态
                    subscription.status = 'error'
                    subscription.save()
                    continue
            
            # 计算下次检查时间（基于最短频率）
            if checked_count > 0:
                # 如果有订阅被检查，等待最短频率的一半时间
                min_freq = min([sub.check_frequency for sub in active_subscriptions])
                wait_time = min(min_freq * 30, 300)  # 最多等待5分钟
                print(f"\n[{timezone.now().strftime('%H:%M:%S')}] 本轮检查完成，等待 {wait_time} 秒后进行下一轮检查...")
                time.sleep(wait_time)
            else:
                # 如果没有订阅需要检查，等待最短频率
                min_freq = min([sub.check_frequency for sub in active_subscriptions])
                print(f"\n[{timezone.now().strftime('%H:%M:%S')}] 所有订阅都在等待中，等待 {min_freq} 分钟后进行下一轮检查...")
                time.sleep(min_freq * 60)
                
    except KeyboardInterrupt:
        print("\n爬虫任务已停止")


if __name__ == "__main__":
    run_crawler_task() 