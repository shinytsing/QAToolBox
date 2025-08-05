#!/usr/bin/env python
import os
import sys
import django
import requests
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import SocialMediaSubscription, SocialMediaNotification

def test_social_api():
    """测试社交订阅API"""
    base_url = 'http://localhost:8000'
    
    # 创建会话对象
    session = requests.Session()
    
    # 获取用户名为1的用户
    try:
        user = User.objects.get(username='1')
        print(f'测试用户: {user.username}')
    except User.DoesNotExist:
        print('用户名为1的用户不存在')
        return
    
    # 首先登录用户
    print('\n=== 用户登录 ===')
    login_data = {
        'username': '1',
        'password': '1'  # 假设密码是1
    }
    
    try:
        # 获取CSRF token
        response = session.get(f'{base_url}/admin/login/')
        if response.status_code == 200:
            print('✓ 获取登录页面成功')
        else:
            print(f'✗ 获取登录页面失败: {response.status_code}')
            return
    except Exception as e:
        print(f'✗ 连接服务器失败: {e}')
        return
    
    # 尝试直接访问API，看看是否需要认证
    print('\n=== 测试未认证访问 ===')
    try:
        response = session.get(f'{base_url}/tools/api/social-subscription/list/')
        print(f'状态码: {response.status_code}')
        if response.status_code == 403:
            print('需要用户认证')
        elif response.status_code == 200:
            print('不需要认证')
            data = response.json()
            print(f'响应: {data}')
        else:
            print(f'其他错误: {response.text[:200]}')
    except Exception as e:
        print(f'请求失败: {e}')
    
    # 测试直接通过Django ORM访问数据
    print('\n=== 直接测试数据库访问 ===')
    try:
        subscriptions = SocialMediaSubscription.objects.filter(user=user)
        print(f'✓ 数据库访问成功，用户 {user.username} 有 {subscriptions.count()} 个订阅')
        
        notifications = SocialMediaNotification.objects.filter(subscription__user=user)
        print(f'✓ 数据库访问成功，用户 {user.username} 有 {notifications.count()} 个通知')
        
        unread_count = notifications.filter(is_read=False).count()
        print(f'✓ 未读通知: {unread_count} 个')
        
    except Exception as e:
        print(f'✗ 数据库访问失败: {e}')

if __name__ == '__main__':
    test_social_api() 