#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification

def check_user_data():
    try:
        user = User.objects.get(username='1')
        print(f'用户 {user.username} 的订阅和通知统计:')
        
        subscriptions = SocialMediaSubscription.objects.filter(user=user)
        print(f'订阅数量: {subscriptions.count()}')
        
        notifications = SocialMediaNotification.objects.filter(subscription__user=user)
        print(f'通知总数: {notifications.count()}')
        
        unread = notifications.filter(is_read=False)
        print(f'未读通知: {unread.count()}')
        
        print('\n订阅详情:')
        for sub in subscriptions:
            print(f'- {sub.get_platform_display()}: {sub.target_user_name} (状态: {sub.get_status_display()})')
        
        print('\n最近的5条通知:')
        for n in notifications.order_by('-created_at')[:5]:
            status = '未读' if not n.is_read else '已读'
            print(f'- {n.title} ({n.created_at.strftime("%H:%M:%S")}) [{status}]')
            
    except User.DoesNotExist:
        print('用户名为1的用户不存在')
    except Exception as e:
        print(f'错误: {e}')

if __name__ == '__main__':
    check_user_data() 