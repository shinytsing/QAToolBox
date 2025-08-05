#!/usr/bin/env python3
"""
简单的心动链接匹配测试
使用Django shell直接测试匹配逻辑
"""

import os
import sys
import django
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import HeartLinkRequest, ChatRoom
from apps.tools.views import create_heart_link_request_api, check_heart_link_status_api
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

def create_mock_request(user):
    """创建模拟请求"""
    factory = RequestFactory()
    request = factory.post('/tools/api/heart-link/create/', data='{}', content_type='application/json')
    request.user = user
    return request

def create_mock_get_request(user):
    """创建模拟GET请求"""
    factory = RequestFactory()
    request = factory.get('/tools/api/heart-link/status/')
    request.user = user
    return request

def test_heart_link_matching():
    """测试心动链接匹配功能"""
    print("🎯 心动链接匹配测试")
    print("="*50)
    
    # 获取两个测试用户
    try:
        user1 = User.objects.get(username='testuser')
        user2 = User.objects.get(username='testuser_complete')
        print(f"✅ 找到测试用户: {user1.username} 和 {user2.username}")
    except User.DoesNotExist:
        print("❌ 找不到测试用户，创建新用户...")
        user1 = User.objects.create_user(username='testuser1', password='testpass123')
        user2 = User.objects.create_user(username='testuser2', password='testpass123')
        print(f"✅ 创建测试用户: {user1.username} 和 {user2.username}")
    
    # 清理之前的测试数据
    HeartLinkRequest.objects.filter(requester__in=[user1, user2]).delete()
    ChatRoom.objects.filter(user1__in=[user1, user2]).delete()
    ChatRoom.objects.filter(user2__in=[user1, user2]).delete()
    print("🧹 清理了之前的测试数据")
    
    print(f"\n⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 用户1创建心动链接请求
    print(f"\n👤 {user1.username} 创建心动链接请求...")
    request1 = create_mock_request(user1)
    response1 = create_heart_link_request_api(request1)
    
    if response1.status_code == 200:
        data1 = response1.content.decode('utf-8')
        print(f"✅ {user1.username} 创建成功: {data1}")
    else:
        print(f"❌ {user1.username} 创建失败: {response1.status_code}")
        return
    
    # 用户2创建心动链接请求
    print(f"\n👤 {user2.username} 创建心动链接请求...")
    request2 = create_mock_request(user2)
    response2 = create_heart_link_request_api(request2)
    
    if response2.status_code == 200:
        data2 = response2.content.decode('utf-8')
        print(f"✅ {user2.username} 创建成功: {data2}")
    else:
        print(f"❌ {user2.username} 创建失败: {response2.status_code}")
        return
    
    # 检查匹配状态
    print(f"\n🔄 检查匹配状态...")
    
    # 检查用户1的状态
    status_request1 = create_mock_get_request(user1)
    status_response1 = check_heart_link_status_api(status_request1)
    
    if status_response1.status_code == 200:
        status_data1 = status_response1.content.decode('utf-8')
        print(f"📋 {user1.username} 状态: {status_data1}")
    else:
        print(f"❌ {user1.username} 状态检查失败: {status_response1.status_code}")
    
    # 检查用户2的状态
    status_request2 = create_mock_get_request(user2)
    status_response2 = check_heart_link_status_api(status_request2)
    
    if status_response2.status_code == 200:
        status_data2 = status_response2.content.decode('utf-8')
        print(f"📋 {user2.username} 状态: {status_data2}")
    else:
        print(f"❌ {user2.username} 状态检查失败: {status_response2.status_code}")
    
    # 检查数据库中的实际状态
    print(f"\n🔍 检查数据库状态...")
    
    request1_db = HeartLinkRequest.objects.filter(requester=user1).first()
    request2_db = HeartLinkRequest.objects.filter(requester=user2).first()
    
    if request1_db:
        print(f"📊 {user1.username} 数据库状态: {request1_db.status}")
        if request1_db.chat_room:
            print(f"   💬 聊天室ID: {request1_db.chat_room.room_id}")
            print(f"   👥 聊天室用户: {request1_db.chat_room.user1.username} 和 {request1_db.chat_room.user2.username if request1_db.chat_room.user2 else 'None'}")
    
    if request2_db:
        print(f"📊 {user2.username} 数据库状态: {request2_db.status}")
        if request2_db.chat_room:
            print(f"   💬 聊天室ID: {request2_db.chat_room.room_id}")
            print(f"   👥 聊天室用户: {request2_db.chat_room.user1.username} 和 {request2_db.chat_room.user2.username if request2_db.chat_room.user2 else 'None'}")
    
    # 检查聊天室
    chat_rooms = ChatRoom.objects.filter(user1__in=[user1, user2]) | ChatRoom.objects.filter(user2__in=[user1, user2])
    print(f"\n🏠 聊天室数量: {chat_rooms.count()}")
    for room in chat_rooms:
        print(f"   💬 聊天室 {room.room_id}: {room.status}")
        print(f"      👥 用户: {room.user1.username} 和 {room.user2.username if room.user2 else 'None'}")
    
    print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断测试结果
    if request1_db and request2_db and request1_db.status == 'matched' and request2_db.status == 'matched':
        if request1_db.chat_room and request2_db.chat_room and request1_db.chat_room == request2_db.chat_room:
            print(f"\n🎉 测试成功！两个用户成功匹配到同一个聊天室！")
            return True
        else:
            print(f"\n⚠️ 部分成功：用户状态为matched，但聊天室可能有问题")
            return False
    else:
        print(f"\n❌ 测试失败：用户状态不正确")
        return False

if __name__ == "__main__":
    success = test_heart_link_matching()
    if success:
        print("✅ 心动链接匹配功能正常工作！")
    else:
        print("❌ 心动链接匹配功能存在问题，需要进一步调试。") 