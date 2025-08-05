#!/usr/bin/env python3
"""
简单的心动链接测试
验证修复后的匹配功能
"""

import os
import sys
import django
import time
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from apps.tools.models import HeartLinkRequest, ChatRoom, UserOnlineStatus
from apps.tools.views import create_heart_link_request_api, check_heart_link_status_api
from apps.tools.services.heart_link_matcher import matcher
from django.test import RequestFactory

def create_mock_request(user):
    """创建模拟请求"""
    factory = RequestFactory()
    request = factory.post('/tools/api/heart-link/create/', data='{}', content_type='application/json')
    request.user = user
    return request

def create_test_user(username):
    """创建测试用户"""
    try:
        user = User.objects.get(username=username)
        print(f"✅ 找到现有用户: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password='testpass123')
        print(f"✅ 创建新用户: {username}")
    return user

def setup_user_online_status(user):
    """设置用户在线状态"""
    online_status, created = UserOnlineStatus.objects.get_or_create(user=user)
    online_status.status = 'online'
    online_status.last_seen = timezone.now()
    online_status.save()
    return online_status

def test_simple_matching():
    """简单匹配测试"""
    print("🎯 简单心动链接匹配测试")
    print("="*50)
    
    # 创建4个测试用户
    test_users = []
    for i in range(1, 5):
        username = f"simple_user_{i}"
        user = create_test_user(username)
        setup_user_online_status(user)
        test_users.append(user)
    
    print(f"\n👥 测试用户: {[user.username for user in test_users]}")
    
    # 清理之前的测试数据
    HeartLinkRequest.objects.filter(requester__in=test_users).delete()
    ChatRoom.objects.filter(user1__in=test_users).delete()
    ChatRoom.objects.filter(user2__in=test_users).delete()
    print("🧹 清理了之前的测试数据")
    
    print(f"\n⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 逐个创建心动链接请求
    results = []
    for i, user in enumerate(test_users):
        print(f"\n👤 [{i+1}] {user.username} 创建心动链接...")
        
        request = create_mock_request(user)
        response = create_heart_link_request_api(request)
        
        if response.status_code == 200:
            data = response.content.decode('utf-8')
            print(f"✅ [{i+1}] {user.username} 创建成功")
            
            # 检查数据库状态
            heart_request = HeartLinkRequest.objects.filter(requester=user).first()
            if heart_request:
                results.append({
                    'user': user,
                    'status': heart_request.status,
                    'chat_room': heart_request.chat_room,
                    'matched_with': heart_request.matched_with
                })
                print(f"   📊 状态: {heart_request.status}")
                if heart_request.chat_room:
                    print(f"   💬 聊天室: {heart_request.chat_room.room_id[:8]}...")
                if heart_request.matched_with:
                    print(f"   👥 匹配用户: {heart_request.matched_with.username}")
        else:
            print(f"❌ [{i+1}] {user.username} 创建失败: {response.status_code}")
        
        # 等待一下
        time.sleep(0.5)
    
    # 分析结果
    print(f"\n📊 测试结果分析")
    print("="*50)
    
    matched_count = len([r for r in results if r['status'] == 'matched'])
    pending_count = len([r for r in results if r['status'] == 'pending'])
    
    print(f"✅ 匹配成功: {matched_count}")
    print(f"⏳ 等待中: {pending_count}")
    
    # 检查聊天室
    chat_rooms = ChatRoom.objects.filter(user1__in=test_users) | ChatRoom.objects.filter(user2__in=test_users)
    print(f"🏠 聊天室数量: {chat_rooms.count()}")
    
    for room in chat_rooms:
        print(f"   💬 {room.room_id[:8]}... - {room.status}")
        print(f"      👥 {room.user1.username} 和 {room.user2.username if room.user2 else 'None'}")
    
    # 检查是否有重复匹配
    user_chat_rooms = {}
    for result in results:
        if result['chat_room']:
            user = result['user']
            if user.username not in user_chat_rooms:
                user_chat_rooms[user.username] = []
            user_chat_rooms[user.username].append(result['chat_room'].room_id)
    
    duplicate_users = [username for username, rooms in user_chat_rooms.items() if len(set(rooms)) > 1]
    
    if duplicate_users:
        print(f"\n⚠️ 发现重复匹配的用户: {duplicate_users}")
        return False
    else:
        print(f"\n✅ 没有重复匹配问题")
    
    print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断测试结果
    if matched_count >= 2 and not duplicate_users:
        print(f"\n🎉 测试成功！匹配功能正常工作！")
        return True
    else:
        print(f"\n⚠️ 测试结果不理想")
        return False

def test_concurrent_matching():
    """并发匹配测试"""
    print("\n🔥 并发匹配测试")
    print("="*50)
    
    # 创建6个用户进行并发测试
    test_users = []
    for i in range(1, 7):
        username = f"concurrent_user_{i}"
        user = create_test_user(username)
        setup_user_online_status(user)
        test_users.append(user)
    
    print(f"\n👥 并发测试用户: {[user.username for user in test_users]}")
    
    # 清理数据
    HeartLinkRequest.objects.filter(requester__in=test_users).delete()
    ChatRoom.objects.filter(user1__in=test_users).delete()
    ChatRoom.objects.filter(user2__in=test_users).delete()
    
    # 模拟并发请求
    print("\n🚀 模拟并发请求...")
    results = []
    
    # 快速连续创建请求
    for i, user in enumerate(test_users):
        request = create_mock_request(user)
        response = create_heart_link_request_api(request)
        
        if response.status_code == 200:
            heart_request = HeartLinkRequest.objects.filter(requester=user).first()
            if heart_request:
                results.append({
                    'user': user,
                    'status': heart_request.status,
                    'chat_room': heart_request.chat_room,
                    'matched_with': heart_request.matched_with
                })
    
    # 分析结果
    matched_count = len([r for r in results if r['status'] == 'matched'])
    pending_count = len([r for r in results if r['status'] == 'pending'])
    
    print(f"\n📊 并发测试结果:")
    print(f"   总用户数: {len(test_users)}")
    print(f"   匹配成功: {matched_count}")
    print(f"   等待中: {pending_count}")
    print(f"   匹配率: {(matched_count/len(test_users)*100):.1f}%")
    
    # 检查重复匹配
    user_chat_rooms = {}
    for result in results:
        if result['chat_room']:
            user = result['user']
            if user.username not in user_chat_rooms:
                user_chat_rooms[user.username] = []
            user_chat_rooms[user.username].append(result['chat_room'].room_id)
    
    duplicate_users = [username for username, rooms in user_chat_rooms.items() if len(set(rooms)) > 1]
    
    if duplicate_users:
        print(f"   重复匹配用户: {duplicate_users}")
        return False
    else:
        print(f"   ✅ 无重复匹配")
        return matched_count >= 3  # 至少要有3个用户匹配成功

if __name__ == "__main__":
    print("🎯 开始简单心动链接测试")
    
    # 简单匹配测试
    success1 = test_simple_matching()
    
    # 并发匹配测试
    success2 = test_concurrent_matching()
    
    print(f"\n🎯 测试总结:")
    print(f"   简单匹配测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"   并发匹配测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！心动链接功能正常工作！")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。") 