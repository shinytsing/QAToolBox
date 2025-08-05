#!/usr/bin/env python3
"""
测试爬虫功能
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
from apps.tools.services.social_media_crawler import SocialMediaCrawler, NotificationService

def test_crawler():
    """测试爬虫功能"""
    print("=" * 50)
    print("🧪 测试爬虫功能")
    print("=" * 50)
    
    # 检查是否有活跃订阅
    active_subscriptions = SocialMediaSubscription.objects.filter(status='active')
    print(f"发现 {active_subscriptions.count()} 个活跃订阅")
    
    if not active_subscriptions.exists():
        print("❌ 没有活跃订阅，请先创建一些订阅")
        return
    
    # 测试每个订阅
    crawler = SocialMediaCrawler()
    notification_service = NotificationService()
    
    for subscription in active_subscriptions:
        print(f"\n📱 测试订阅: {subscription.target_user_name} ({subscription.get_platform_display()})")
        print(f"   平台: {subscription.platform}")
        print(f"   检查频率: {subscription.check_frequency} 分钟")
        print(f"   订阅类型: {', '.join(subscription.subscription_types)}")
        
        try:
            # 检查是否需要更新
            last_check = subscription.last_check or subscription.created_at
            check_interval = timedelta(minutes=subscription.check_frequency)
            
            if datetime.now().replace(tzinfo=None) - last_check.replace(tzinfo=None) >= check_interval:
                print("   ✅ 需要检查更新")
                
                # 爬取更新
                updates = crawler.crawl_user_updates(subscription)
                
                if updates:
                    print(f"   📝 发现 {len(updates)} 个更新")
                    
                    # 创建通知
                    notification_service.create_notifications(updates, subscription)
                    
                    for update in updates:
                        print(f"      - {update['title']}")
                        if 'new_followers_count' in update:
                            print(f"        新增粉丝: {update['new_followers_count']}")
                        if 'new_following_count' in update:
                            print(f"        新增关注: {update['new_following_count']}")
                else:
                    print("   ⏭️  无更新")
                
                # 更新最后检查时间
                subscription.last_check = datetime.now()
                subscription.save()
            else:
                remaining = check_interval - (datetime.now().replace(tzinfo=None) - last_check.replace(tzinfo=None))
                remaining_minutes = int(remaining.total_seconds() / 60)
                print(f"   ⏰ 还需等待 {remaining_minutes} 分钟")
        
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
    
    # 检查通知
    recent_notifications = SocialMediaNotification.objects.filter(
        created_at__gte=datetime.now() - timedelta(hours=1)
    )
    print(f"\n📢 最近1小时生成的通知: {recent_notifications.count()} 个")
    
    print("\n" + "=" * 50)
    print("✅ 测试完成")
    print("=" * 50)

def test_data_generation():
    """测试数据生成"""
    print("\n" + "=" * 50)
    print("🎲 测试数据生成")
    print("=" * 50)
    
    # 创建测试订阅
    from apps.users.models import User
    
    try:
        test_user = User.objects.first()
        if not test_user:
            print("❌ 没有找到用户，请先创建用户")
            return
        
        # 测试不同平台的数据生成
        platforms = ['xiaohongshu', 'douyin', 'weibo', 'bilibili', 'zhihu', 'netease']
        
        for platform in platforms:
            print(f"\n📱 测试 {platform} 平台数据生成:")
            
            # 创建临时订阅
            subscription = SocialMediaSubscription(
                user=test_user,
                platform=platform,
                target_user_name=f"测试用户_{platform}",
                target_user_id=f"test_{platform}_123",
                subscription_types=['newPosts', 'newFollowers', 'newFollowing', 'profileChanges'],
                check_frequency=5,
                status='active'
            )
            
            # 测试爬虫
            crawler = SocialMediaCrawler()
            updates = crawler.crawl_user_updates(subscription)
            
            if updates:
                print(f"   ✅ 生成了 {len(updates)} 个更新")
                for update in updates:
                    print(f"      - {update['title']}")
                    if 'new_followers_count' in update:
                        print(f"        新增粉丝: {update['new_followers_count']}")
                    if 'new_following_count' in update:
                        print(f"        新增关注: {update['new_following_count']}")
            else:
                print("   ⏭️  无更新")
    
    except Exception as e:
        print(f"❌ 测试数据生成时出错: {str(e)}")

if __name__ == '__main__':
    test_crawler()
    test_data_generation() 