#!/usr/bin/env python3
"""
测试B站爬虫功能
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.services.social_media_crawler import SocialMediaCrawler, NotificationService
from apps.tools.models import SocialMediaSubscription
from django.contrib.auth.models import User

def test_bilibili_crawler():
    """测试B站爬虫"""
    print("=== 测试B站爬虫功能 ===")
    
    try:
        # 获取shinytsing用户的B站订阅
        user = User.objects.get(username='shinytsing')
        subscription = SocialMediaSubscription.objects.get(
            user=user, 
            platform='bilibili'
        )
        
        print(f"用户: {user.username}")
        print(f"订阅目标: {subscription.target_user_name}")
        print(f"订阅类型: {subscription.subscription_types}")
        print(f"检查频率: {subscription.check_frequency}分钟")
        print(f"最后检查时间: {subscription.last_check}")
        print()
        
        # 创建爬虫实例
        crawler = SocialMediaCrawler()
        
        # 爬取更新
        print("开始爬取更新...")
        updates = crawler.crawl_user_updates(subscription)
        
        print(f"发现更新数量: {len(updates)}")
        
        if updates:
            print("\n更新详情:")
            for i, update in enumerate(updates, 1):
                print(f"{i}. 类型: {update['type']}")
                print(f"   标题: {update['title']}")
                print(f"   内容: {update['content']}")
                
                # 显示详细信息
                if update['type'] == 'newPosts':
                    if 'post_content' in update:
                        print(f"   帖子内容: {update['post_content'][:50]}...")
                    if 'post_likes' in update:
                        print(f"   点赞数: {update['post_likes']}")
                
                elif update['type'] == 'newFollowers':
                    if 'follower_name' in update:
                        print(f"   粉丝名称: {update['follower_name']}")
                    if 'follower_count' in update:
                        print(f"   总粉丝数: {update['follower_count']}")
                
                elif update['type'] == 'newFollowing':
                    if 'following_name' in update:
                        print(f"   关注对象: {update['following_name']}")
                    if 'following_count' in update:
                        print(f"   关注总数: {update['following_count']}")
                
                elif update['type'] == 'profileChanges':
                    if 'profile_changes' in update:
                        print(f"   变化类型: {update['profile_changes'].get('change_type', '未知')}")
                
                print()
            
            # 创建通知
            print("创建通知...")
            NotificationService.create_notifications(updates, subscription)
            print("通知创建完成！")
            
            # 检查通知是否创建成功
            from apps.tools.models import SocialMediaNotification
            notifications = SocialMediaNotification.objects.filter(
                subscription=subscription
            ).order_by('-created_at')[:len(updates)]
            
            print(f"\n创建的通知:")
            for notif in notifications:
                print(f"- {notif.notification_type}: {notif.title}")
        
        else:
            print("没有发现更新")
        
        # 更新订阅的最后检查时间
        subscription.refresh_from_db()
        print(f"\n更新后的最后检查时间: {subscription.last_check}")
        
    except User.DoesNotExist:
        print("错误: 用户shinytsing不存在")
    except SocialMediaSubscription.DoesNotExist:
        print("错误: 未找到B站订阅")
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_bilibili_crawler() 