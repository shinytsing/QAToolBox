#!/usr/bin/env python3
"""
心动链接匹配功能测试脚本
"""

import os
import sys
import django
import time
import random
from datetime import timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from apps.tools.models import HeartLinkRequest, ChatRoom
from apps.tools.services.heart_link_matcher import matcher


def create_test_users():
    """创建测试用户"""
    users = []
    for i in range(4):
        username = f'test_user_{i+1}'
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': f'{username}@test.com',
                'is_active': True
            }
        )
        users.append(user)
        print(f"用户 {username}: {'创建' if created else '已存在'}")
    return users


def cleanup_test_data():
    """清理测试数据"""
    # 清理测试用户
    test_users = User.objects.filter(username__startswith='test_user_')
    test_users.delete()
    
    # 清理测试请求
    HeartLinkRequest.objects.filter(requester__username__startswith='test_user_').delete()
    
    # 清理测试聊天室
    ChatRoom.objects.filter(user1__username__startswith='test_user_').delete()
    ChatRoom.objects.filter(user2__username__startswith='test_user_').delete()
    
    print("测试数据已清理")


def test_basic_matching():
    """测试基础匹配功能"""
    print("\n=== 测试基础匹配功能 ===")
    
    users = create_test_users()
    
    try:
        # 创建两个用户的请求
        request1 = HeartLinkRequest.objects.create(
            requester=users[0],
            status='pending'
        )
        request2 = HeartLinkRequest.objects.create(
            requester=users[1],
            status='pending'
        )
        
        print(f"创建请求: {users[0].username} 和 {users[1].username}")
        
        # 尝试匹配
        chat_room, matched_user = matcher.match_users(users[0], request1)
        
        if chat_room and matched_user:
            print(f"✅ 匹配成功: {users[0].username} <-> {matched_user.username}")
            print(f"聊天室ID: {chat_room.room_id}")
            
            # 检查状态
            request1.refresh_from_db()
            request2.refresh_from_db()
            print(f"请求1状态: {request1.status}")
            print(f"请求2状态: {request2.status}")
            
            return True
        else:
            print("❌ 匹配失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_concurrent_matching():
    """测试并发匹配"""
    print("\n=== 测试并发匹配 ===")
    
    users = create_test_users()
    
    try:
        # 创建多个用户的请求
        requests = []
        for user in users:
            request = HeartLinkRequest.objects.create(
                requester=user,
                status='pending'
            )
            requests.append(request)
            print(f"创建请求: {user.username}")
        
        # 模拟并发匹配
        matches = []
        for i, user in enumerate(users):
            if i % 2 == 0 and i + 1 < len(users):
                # 尝试匹配相邻的用户
                chat_room, matched_user = matcher.match_users(user, requests[i])
                if chat_room and matched_user:
                    matches.append((user, matched_user))
                    print(f"✅ 匹配成功: {user.username} <-> {matched_user.username}")
        
        print(f"总共匹配成功: {len(matches)} 对")
        return len(matches) > 0
        
    except Exception as e:
        print(f"❌ 并发测试失败: {e}")
        return False


def test_retry_matching():
    """测试重试匹配"""
    print("\n=== 测试重试匹配 ===")
    
    users = create_test_users()
    
    try:
        # 创建请求
        request = HeartLinkRequest.objects.create(
            requester=users[0],
            status='pending'
        )
        
        print(f"创建请求: {users[0].username}")
        
        # 第一次匹配（应该失败，因为没有其他用户）
        chat_room, matched_user = matcher.match_users(users[0], request)
        if not chat_room:
            print("第一次匹配失败（预期）")
        
        # 创建第二个用户
        request2 = HeartLinkRequest.objects.create(
            requester=users[1],
            status='pending'
        )
        print(f"创建第二个请求: {users[1].username}")
        
        # 第二次匹配（应该成功）
        chat_room, matched_user = matcher.match_users(users[0], request)
        if chat_room and matched_user:
            print(f"✅ 重试匹配成功: {users[0].username} <-> {matched_user.username}")
            return True
        else:
            print("❌ 重试匹配失败")
            return False
            
    except Exception as e:
        print(f"❌ 重试测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理"""
    print("\n=== 测试错误处理 ===")
    
    users = create_test_users()
    
    try:
        # 测试无效用户
        request = HeartLinkRequest.objects.create(
            requester=users[0],
            status='pending'
        )
        
        # 尝试匹配已匹配的请求
        request.status = 'matched'
        request.save()
        
        chat_room, matched_user = matcher.match_users(users[0], request)
        if not chat_room:
            print("✅ 正确处理已匹配的请求")
            return True
        else:
            print("❌ 错误处理失败")
            return False
            
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 心动链接匹配功能测试开始")
    print("=" * 50)
    
    # 清理之前的测试数据
    cleanup_test_data()
    
    # 运行测试
    tests = [
        test_basic_matching,
        test_concurrent_matching,
        test_retry_matching,
        test_error_handling
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append(False)
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    for i, result in enumerate(results):
        status = "✅ 通过" if result else "❌ 失败"
        print(f"测试 {i+1}: {status}")
    
    success_count = sum(results)
    total_count = len(results)
    print(f"\n成功率: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试失败，需要进一步检查")


if __name__ == "__main__":
    main()
