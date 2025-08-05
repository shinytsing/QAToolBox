#!/usr/bin/env python3
"""
多人心动链接匹配测试
模拟多个用户同时启动心动链接，测试匹配效果
"""

import os
import sys
import django
import time
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tools.models import HeartLinkRequest, ChatRoom
from apps.tools.views import create_heart_link_request_api, check_heart_link_status_api
from django.test import RequestFactory
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

def create_test_user(username):
    """创建测试用户"""
    try:
        user = User.objects.get(username=username)
        print(f"✅ 找到现有用户: {username}")
    except User.DoesNotExist:
        user = User.objects.create_user(username=username, password='testpass123')
        print(f"✅ 创建新用户: {username}")
    return user

def user_heart_link_test(user, user_index):
    """单个用户的心动链接测试"""
    print(f"\n👤 [{user_index}] {user.username} 开始测试...")
    
    try:
        # 创建心动链接请求
        request = create_mock_request(user)
        response = create_heart_link_request_api(request)
        
        if response.status_code == 200:
            data = response.content.decode('utf-8')
            print(f"✅ [{user_index}] {user.username} 创建成功")
            
            # 等待一下让匹配逻辑执行
            time.sleep(1)
            
            # 检查状态
            status_request = create_mock_get_request(user)
            status_response = check_heart_link_status_api(status_request)
            
            if status_response.status_code == 200:
                status_data = status_response.content.decode('utf-8')
                print(f"📋 [{user_index}] {user.username} 状态检查完成")
                
                # 检查数据库状态
                heart_request = HeartLinkRequest.objects.filter(requester=user).first()
                if heart_request:
                    return {
                        'user': user,
                        'user_index': user_index,
                        'status': heart_request.status,
                        'chat_room': heart_request.chat_room,
                        'matched_with': heart_request.matched_with,
                        'success': True
                    }
            
        else:
            print(f"❌ [{user_index}] {user.username} 创建失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ [{user_index}] {user.username} 测试出错: {str(e)}")
    
    return {
        'user': user,
        'user_index': user_index,
        'status': 'error',
        'chat_room': None,
        'matched_with': None,
        'success': False
    }

def test_multi_user_heart_link():
    """测试多用户心动链接匹配"""
    print("🎯 多人心动链接匹配测试")
    print("="*60)
    
    # 创建测试用户
    test_users = []
    for i in range(1, 7):  # 创建6个测试用户
        username = f"testuser_multi_{i}"
        user = create_test_user(username)
        test_users.append(user)
    
    print(f"\n👥 测试用户数量: {len(test_users)}")
    for i, user in enumerate(test_users, 1):
        print(f"   {i}. {user.username}")
    
    # 清理之前的测试数据
    HeartLinkRequest.objects.filter(requester__in=test_users).delete()
    ChatRoom.objects.filter(user1__in=test_users).delete()
    ChatRoom.objects.filter(user2__in=test_users).delete()
    print("\n🧹 清理了之前的测试数据")
    
    print(f"\n⏰ 测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 使用线程池同时启动多个用户的心动链接
    print(f"\n🚀 同时启动 {len(test_users)} 个用户的心动链接...")
    
    results = []
    with ThreadPoolExecutor(max_workers=len(test_users)) as executor:
        # 提交所有任务
        future_to_user = {
            executor.submit(user_heart_link_test, user, i+1): user 
            for i, user in enumerate(test_users)
        }
        
        # 收集结果
        for future in as_completed(future_to_user):
            result = future.result()
            results.append(result)
    
    # 分析结果
    print(f"\n📊 测试结果分析")
    print("="*60)
    
    matched_users = []
    pending_users = []
    error_users = []
    
    for result in results:
        if result['success']:
            if result['status'] == 'matched':
                matched_users.append(result)
            elif result['status'] == 'pending':
                pending_users.append(result)
        else:
            error_users.append(result)
    
    print(f"✅ 成功匹配的用户: {len(matched_users)}")
    print(f"⏳ 等待中的用户: {len(pending_users)}")
    print(f"❌ 出错的用户: {len(error_users)}")
    
    # 显示匹配详情
    if matched_users:
        print(f"\n💕 匹配详情:")
        chat_rooms = {}
        
        for result in matched_users:
            user = result['user']
            chat_room = result['chat_room']
            matched_with = result['matched_with']
            
            if chat_room:
                if chat_room.room_id not in chat_rooms:
                    chat_rooms[chat_room.room_id] = []
                chat_rooms[chat_room.room_id].append({
                    'user': user,
                    'matched_with': matched_with
                })
        
        for room_id, users in chat_rooms.items():
            print(f"   💬 聊天室 {room_id[:8]}...:")
            for user_info in users:
                print(f"      👤 {user_info['user'].username} ↔️ {user_info['matched_with'].username if user_info['matched_with'] else 'None'}")
    
    # 显示等待中的用户
    if pending_users:
        print(f"\n⏳ 等待中的用户:")
        for result in pending_users:
            print(f"   👤 {result['user'].username}")
    
    # 显示出错的用户
    if error_users:
        print(f"\n❌ 出错的用户:")
        for result in error_users:
            print(f"   👤 {result['user'].username}")
    
    # 检查数据库中的聊天室
    print(f"\n🏠 数据库中的聊天室:")
    all_chat_rooms = ChatRoom.objects.filter(
        user1__in=test_users
    ) | ChatRoom.objects.filter(
        user2__in=test_users
    )
    
    for room in all_chat_rooms:
        print(f"   💬 {room.room_id[:8]}... - 状态: {room.status}")
        print(f"      👥 {room.user1.username} 和 {room.user2.username if room.user2 else 'None'}")
    
    # 统计信息
    total_requests = HeartLinkRequest.objects.filter(requester__in=test_users).count()
    matched_requests = HeartLinkRequest.objects.filter(
        requester__in=test_users, 
        status='matched'
    ).count()
    pending_requests = HeartLinkRequest.objects.filter(
        requester__in=test_users, 
        status='pending'
    ).count()
    
    print(f"\n📈 统计信息:")
    print(f"   总请求数: {total_requests}")
    print(f"   匹配成功: {matched_requests}")
    print(f"   等待中: {pending_requests}")
    print(f"   匹配率: {(matched_requests/total_requests*100):.1f}%" if total_requests > 0 else "   匹配率: 0%")
    
    print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断测试结果
    if matched_requests >= 2:  # 至少要有2个用户匹配成功
        print(f"\n🎉 测试成功！多人匹配功能正常工作！")
        return True
    else:
        print(f"\n⚠️ 测试结果不理想，匹配数量较少")
        return False

def test_concurrent_matching():
    """测试并发匹配场景"""
    print("\n🔄 并发匹配场景测试")
    print("="*60)
    
    # 创建更多用户进行并发测试
    concurrent_users = []
    for i in range(1, 11):  # 创建10个用户
        username = f"concurrent_user_{i}"
        user = create_test_user(username)
        concurrent_users.append(user)
    
    # 清理数据
    HeartLinkRequest.objects.filter(requester__in=concurrent_users).delete()
    ChatRoom.objects.filter(user1__in=concurrent_users).delete()
    ChatRoom.objects.filter(user2__in=concurrent_users).delete()
    
    print(f"👥 并发测试用户数量: {len(concurrent_users)}")
    
    # 分批启动，模拟真实场景
    print("🚀 分批启动用户...")
    
    # 第一批：5个用户
    print("   第一批用户启动...")
    batch1_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(user_heart_link_test, user, i+1)
            for i, user in enumerate(concurrent_users[:5])
        ]
        for future in as_completed(futures):
            batch1_results.append(future.result())
    
    time.sleep(2)  # 等待匹配
    
    # 第二批：5个用户
    print("   第二批用户启动...")
    batch2_results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(user_heart_link_test, user, i+6)
            for i, user in enumerate(concurrent_users[5:])
        ]
        for future in as_completed(futures):
            batch2_results.append(future.result())
    
    # 分析并发结果
    all_results = batch1_results + batch2_results
    matched_count = len([r for r in all_results if r['success'] and r['status'] == 'matched'])
    
    print(f"\n📊 并发测试结果:")
    print(f"   总用户数: {len(concurrent_users)}")
    print(f"   匹配成功: {matched_count}")
    print(f"   匹配率: {(matched_count/len(concurrent_users)*100):.1f}%")
    
    return matched_count >= 4  # 至少要有4个用户匹配成功

if __name__ == "__main__":
    print("🎯 开始多人心动链接测试")
    
    # 基础多人测试
    success1 = test_multi_user_heart_link()
    
    # 并发测试
    success2 = test_concurrent_matching()
    
    print(f"\n🎯 测试总结:")
    print(f"   基础多人测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"   并发匹配测试: {'✅ 通过' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("🎉 所有测试通过！多人心动链接功能正常工作！")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。") 