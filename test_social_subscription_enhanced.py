#!/usr/bin/env python3
"""
测试增强的社交媒体订阅功能
包括新粉丝、新关注的区分和详细通知内容
"""

import os
import sys
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification
from apps.tools.services.social_media_crawler import SocialMediaCrawler, NotificationService

def create_test_user():
    """创建测试用户"""
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': '测试',
            'last_name': '用户'
        }
    )
    if created:
        user.set_password('test123456')
        user.save()
        print(f"创建测试用户: {user.username}")
    else:
        print(f"使用现有测试用户: {user.username}")
    return user

def create_test_subscriptions(user):
    """创建测试订阅"""
    subscriptions = []
    
    # 小红书订阅 - 包含所有类型
    xiaohongshu_sub, created = SocialMediaSubscription.objects.get_or_create(
        user=user,
        platform='xiaohongshu',
        target_user_id='xiaohongshu_user_001',
        defaults={
            'target_user_name': '小红书博主',
            'subscription_types': ['newPosts', 'newFollowers', 'newFollowing', 'profileChanges'],
            'check_frequency': 15,
            'status': 'active'
        }
    )
    subscriptions.append(xiaohongshu_sub)
    print(f"{'创建' if created else '使用'}小红书订阅: {xiaohongshu_sub.target_user_name}")
    
    # 抖音订阅 - 包含所有类型
    douyin_sub, created = SocialMediaSubscription.objects.get_or_create(
        user=user,
        platform='douyin',
        target_user_id='douyin_user_001',
        defaults={
            'target_user_name': '抖音UP主',
            'subscription_types': ['newPosts', 'newFollowers', 'newFollowing'],
            'check_frequency': 15,
            'status': 'active'
        }
    )
    subscriptions.append(douyin_sub)
    print(f"{'创建' if created else '使用'}抖音订阅: {douyin_sub.target_user_name}")
    
    return subscriptions

def test_crawler():
    """测试爬虫功能"""
    print("\n=== 测试爬虫功能 ===")
    
    user = create_test_user()
    subscriptions = create_test_subscriptions(user)
    
    crawler = SocialMediaCrawler()
    
    for subscription in subscriptions:
        print(f"\n测试订阅: {subscription.target_user_name} ({subscription.get_platform_display()})")
        print(f"订阅类型: {subscription.subscription_types}")
        
        # 爬取更新
        updates = crawler.crawl_user_updates(subscription)
        
        if updates:
            print(f"发现 {len(updates)} 个更新:")
            for update in updates:
                print(f"  - 类型: {update['type']}")
                print(f"    标题: {update['title']}")
                print(f"    内容: {update['content']}")
                
                # 显示详细信息
                if update['type'] == 'newPosts':
                    if 'post_content' in update:
                        print(f"    帖子内容: {update['post_content'][:50]}...")
                    if 'post_likes' in update:
                        print(f"    点赞数: {update['post_likes']}")
                
                elif update['type'] == 'newFollowers':
                    if 'follower_name' in update:
                        print(f"    粉丝名称: {update['follower_name']}")
                    if 'follower_count' in update:
                        print(f"    总粉丝数: {update['follower_count']}")
                
                elif update['type'] == 'newFollowing':
                    if 'following_name' in update:
                        print(f"    关注对象: {update['following_name']}")
                    if 'following_count' in update:
                        print(f"    关注总数: {update['following_count']}")
                
                print()
        else:
            print("  没有发现更新")

def test_notification_creation():
    """测试通知创建功能"""
    print("\n=== 测试通知创建功能 ===")
    
    user = create_test_user()
    subscriptions = create_test_subscriptions(user)
    
    # 清除现有通知
    SocialMediaNotification.objects.filter(subscription__user=user).delete()
    
    crawler = SocialMediaCrawler()
    notification_service = NotificationService()
    
    for subscription in subscriptions:
        print(f"\n为订阅创建通知: {subscription.target_user_name}")
        
        # 爬取更新
        updates = crawler.crawl_user_updates(subscription)
        
        if updates:
            # 创建通知
            notification_service.create_notifications(updates, subscription)
            print(f"创建了 {len(updates)} 个通知")
        else:
            print("没有更新，跳过通知创建")

def test_notification_display():
    """测试通知显示功能"""
    print("\n=== 测试通知显示功能 ===")
    
    user = create_test_user()
    notifications = SocialMediaNotification.objects.filter(subscription__user=user).order_by('-created_at')
    
    if notifications.exists():
        print(f"找到 {notifications.count()} 个通知:")
        
        for notification in notifications[:5]:  # 只显示前5个
            print(f"\n通知 #{notification.id}")
            print(f"  类型: {notification.get_notification_type_display()}")
            print(f"  标题: {notification.title}")
            print(f"  内容: {notification.content}")
            print(f"  平台: {notification.subscription.get_platform_display()}")
            print(f"  时间: {notification.created_at}")
            
            # 显示详细信息
            if notification.notification_type == 'newPosts':
                if notification.post_content:
                    print(f"  帖子内容: {notification.post_content[:100]}...")
                if notification.post_likes:
                    print(f"  点赞数: {notification.post_likes}")
                if notification.post_tags:
                    print(f"  标签: {', '.join(notification.post_tags)}")
            
            elif notification.notification_type == 'newFollowers':
                if notification.follower_name:
                    print(f"  粉丝名称: {notification.follower_name}")
                if notification.follower_count:
                    print(f"  总粉丝数: {notification.follower_count}")
            
            elif notification.notification_type == 'newFollowing':
                if notification.following_name:
                    print(f"  关注对象: {notification.following_name}")
                if notification.following_count:
                    print(f"  关注总数: {notification.following_count}")
            
            elif notification.notification_type == 'profileChanges':
                if notification.profile_changes:
                    print(f"  变化类型: {notification.profile_changes.get('change_type', '未知')}")
    else:
        print("没有找到通知")

def test_subscription_types():
    """测试订阅类型说明"""
    print("\n=== 测试订阅类型说明 ===")
    
    print("订阅类型详细说明:")
    for choice, label in SocialMediaSubscription.SUBSCRIPTION_TYPE_CHOICES:
        description = SocialMediaSubscription.SUBSCRIPTION_TYPE_DESCRIPTIONS.get(choice, '无描述')
        print(f"  {label} ({choice}): {description}")
    
    print("\n通知类型详细说明:")
    for choice, label in SocialMediaNotification.NOTIFICATION_TYPE_CHOICES:
        description = SocialMediaNotification.NOTIFICATION_TYPE_DESCRIPTIONS.get(choice, '无描述')
        print(f"  {label} ({choice}): {description}")

def main():
    """主函数"""
    print("社交媒体订阅功能增强测试")
    print("=" * 50)
    
    try:
        # 测试订阅类型说明
        test_subscription_types()
        
        # 测试爬虫功能
        test_crawler()
        
        # 测试通知创建
        test_notification_creation()
        
        # 测试通知显示
        test_notification_display()
        
        print("\n" + "=" * 50)
        print("测试完成！")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 