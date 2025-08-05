#!/usr/bin/env python3
"""
改进的心动链接智能匹配测试
测试新的智能匹配算法和竞态条件处理
"""

import os
import sys
import django
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def setup_user_online_status(user):
    """设置用户在线状态"""
    online_status, created = UserOnlineStatus.objects.get_or_create(user=user)
    online_status.status = 'online'
    online_status.last_seen = timezone.now()
    online_status.save()
    return online_status

def user_heart_link_test(user, user_index):
    """单个用户的心动链接测试"""
    print(f"\n👤 [{user_index}] {user.username} 开始测试...")
    
    try:
        # 设置用户在线状态
        setup_user_online_status(user)
        
        # 创建心动链接请求
        request = create_mock_request(user)
        response = create_heart_link_request_api(request)
        
        if response.status_code == 200:
            data = response.content.decode('utf-8')
            print(f"✅ [{user_index}] {user.username} 创建成功")
            
            # 等待一下让匹配逻辑执行
            time.sleep(0.5)
            
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

def test_improved_matching():
    """测试改进的匹配算法"""
    print("🎯 改进的心动链接智能匹配测试")
    print("="*60)
    
    # 创建测试用户
    test_users = []
    for i in range(1, 9):  # 创建8个测试用户
        username = f"improved_user_{i}"
        user = create_test_user(username)
        test_users.append(user)
    
    print(f"\n👥 测试用户数量: {len(test_users)}")
    for i, user in enumerate(test_users, 1):
        print(f"   {i}. {user.username}")
    
    # 清理之前的测试数据
    HeartLinkRequest.objects.filter(requester__in=test_users).delete()
    ChatRoom.objects.filter(user1__in=test_users).delete()
    ChatRoom.objects.filter(user2__in=test_users).delete()
    UserOnlineStatus.objects.filter(user__in=test_users).delete()
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
    
    # 检查是否有重复匹配
    user_chat_rooms = {}
    for result in matched_users:
        user = result['user']
        chat_room = result['chat_room']
        if user.username not in user_chat_rooms:
            user_chat_rooms[user.username] = []
        user_chat_rooms[user.username].append(chat_room.room_id if chat_room else None)
    
    duplicate_users = [username for username, rooms in user_chat_rooms.items() if len(set(rooms)) > 1]
    if duplicate_users:
        print(f"\n⚠️ 发现重复匹配的用户:")
        for username in duplicate_users:
            print(f"   👤 {username}: {user_chat_rooms[username]}")
    else:
        print(f"\n✅ 没有发现重复匹配问题")
    
    # 获取匹配统计
    stats = matcher.get_matching_stats()
    print(f"\n📈 匹配统计:")
    print(f"   总请求数: {stats['total']}")
    print(f"   匹配成功: {stats['matched']}")
    print(f"   等待中: {stats['pending']}")
    print(f"   已过期: {stats['expired']}")
    print(f"   匹配率: {stats['match_rate']:.1f}%")
    
    print(f"\n⏰ 测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 判断测试结果
    if len(matched_users) >= 4 and not duplicate_users:  # 至少要有4个用户匹配成功且无重复
        print(f"\n🎉 测试成功！智能匹配功能正常工作！")
        return True
    else:
        print(f"\n⚠️ 测试结果不理想")
        return False

def test_concurrent_stress():
    """压力测试：大量并发用户"""
    print("\n🔥 压力测试：大量并发用户")
    print("="*60)
    
    # 创建更多用户进行压力测试
    stress_users = []
    for i in range(1, 21):  # 创建20个用户
        username = f"stress_user_{i}"
        user = create_test_user(username)
        stress_users.append(user)
    
    # 清理数据
    HeartLinkRequest.objects.filter(requester__in=stress_users).delete()
    ChatRoom.objects.filter(user1__in=stress_users).delete()
    ChatRoom.objects.filter(user2__in=stress_users).delete()
    UserOnlineStatus.objects.filter(user__in=stress_users).delete()
    
    print(f"👥 压力测试用户数量: {len(stress_users)}")
    
    # 分批启动，模拟真实场景
    print("🚀 分批启动用户...")
    
    # 第一批：10个用户
    print("   第一批用户启动...")
    batch1_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(user_heart_link_test, user, i+1)
            for i, user in enumerate(stress_users[:10])
        ]
        for future in as_completed(futures):
            batch1_results.append(future.result())
    
    time.sleep(1)  # 等待匹配
    
    # 第二批：10个用户
    print("   第二批用户启动...")
    batch2_results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(user_heart_link_test, user, i+11)
            for i, user in enumerate(stress_users[10:])
        ]
        for future in as_completed(futures):
            batch2_results.append(future.result())
    
    # 分析压力测试结果
    all_results = batch1_results + batch2_results
    matched_count = len([r for r in all_results if r['success'] and r['status'] == 'matched'])
    
    # 检查重复匹配
    user_chat_rooms = {}
    for result in all_results:
        if result['success'] and result['status'] == 'matched' and result['chat_room']:
            user = result['user']
            chat_room = result['chat_room']
            if user.username not in user_chat_rooms:
                user_chat_rooms[user.username] = []
            user_chat_rooms[user.username].append(chat_room.room_id)
    
    duplicate_users = [username for username, rooms in user_chat_rooms.items() if len(set(rooms)) > 1]
    
    print(f"\n📊 压力测试结果:")
    print(f"   总用户数: {len(stress_users)}")
    print(f"   匹配成功: {matched_count}")
    print(f"   匹配率: {(matched_count/len(stress_users)*100):.1f}%")
    print(f"   重复匹配用户数: {len(duplicate_users)}")
    
    if duplicate_users:
        print(f"   重复匹配用户: {duplicate_users[:5]}...")  # 只显示前5个
    
    return matched_count >= 12 and len(duplicate_users) == 0  # 至少60%匹配率且无重复

def test_matching_algorithm():
    """测试匹配算法的智能性"""
    print("\n🧠 智能匹配算法测试")
    print("="*60)
    
    # 创建不同特征的测试用户
    test_cases = [
        {'username': 'active_user_1', 'online': True, 'activity': 10},
        {'username': 'active_user_2', 'online': True, 'activity': 8},
        {'username': 'inactive_user_1', 'online': False, 'activity': 2},
        {'username': 'inactive_user_2', 'online': False, 'activity': 1},
        {'username': 'new_user_1', 'online': True, 'activity': 0},
        {'username': 'new_user_2', 'online': True, 'activity': 0},
    ]
    
    test_users = []
    for case in test_cases:
        user = create_test_user(case['username'])
        
        # 设置在线状态
        if case['online']:
            setup_user_online_status(user)
        
        # 模拟用户活动（这里只是设置标记，实际活动记录需要更复杂的模拟）
        test_users.append({
            'user': user,
            'case': case
        })
    
    print(f"👥 智能匹配测试用户: {len(test_users)}")
    for i, test_case in enumerate(test_users, 1):
        case = test_case['case']
        print(f"   {i}. {case['username']} (在线: {case['online']}, 活跃度: {case['activity']})")
    
    # 清理数据
    user_list = [tc['user'] for tc in test_users]
    HeartLinkRequest.objects.filter(requester__in=user_list).delete()
    ChatRoom.objects.filter(user1__in=user_list).delete()
    ChatRoom.objects.filter(user2__in=user_list).delete()
    
    # 测试匹配
    print("\n🚀 测试智能匹配...")
    results = []
    with ThreadPoolExecutor(max_workers=len(test_users)) as executor:
        futures = [
            executor.submit(user_heart_link_test, tc['user'], i+1)
            for i, tc in enumerate(test_users)
        ]
        for future in as_completed(futures):
            results.append(future.result())
    
    # 分析智能匹配结果
    matched_results = [r for r in results if r['success'] and r['status'] == 'matched']
    
    print(f"\n📊 智能匹配结果:")
    print(f"   总用户数: {len(test_users)}")
    print(f"   匹配成功: {len(matched_results)}")
    
    # 分析匹配质量
    online_matched = 0
    active_matched = 0
    
    for result in matched_results:
        user = result['user']
        case = next(tc['case'] for tc in test_users if tc['user'] == user)
        if case['online']:
            online_matched += 1
        if case['activity'] >= 5:
            active_matched += 1
    
    print(f"   在线用户匹配: {online_matched}")
    print(f"   活跃用户匹配: {active_matched}")
    
    return len(matched_results) >= 3  # 至少要有3个用户匹配成功

if __name__ == "__main__":
    print("🎯 开始改进的心动链接测试")
    
    # 基础改进测试
    success1 = test_improved_matching()
    
    # 压力测试
    success2 = test_concurrent_stress()
    
    # 智能匹配测试
    success3 = test_matching_algorithm()
    
    print(f"\n🎯 测试总结:")
    print(f"   基础改进测试: {'✅ 通过' if success1 else '❌ 失败'}")
    print(f"   压力测试: {'✅ 通过' if success2 else '❌ 失败'}")
    print(f"   智能匹配测试: {'✅ 通过' if success3 else '❌ 失败'}")
    
    if success1 and success2 and success3:
        print("🎉 所有测试通过！改进的心动链接功能正常工作！")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。") 