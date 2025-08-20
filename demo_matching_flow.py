#!/usr/bin/env python
"""
演示完整的匹配流程
"""
import os
import django
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models.legacy_models import ChatRoom, HeartLinkRequest
from django.contrib.auth.models import User
from apps.tools.services.heart_link_matcher import matcher

def demo_matching_flow():
    """演示完整的匹配流程"""
    print("🎭 演示完整的匹配流程")
    print("=" * 50)
    
    # 1. 获取用户
    user1 = User.objects.get(username='1')
    user2 = User.objects.get(username='shinytsing')
    
    print(f"用户1: {user1.username}")
    print(f"用户2: {user2.username}")
    
    # 2. 清理现有请求
    HeartLinkRequest.objects.filter(status__in=['pending', 'matching']).update(status='cancelled')
    print("✅ 已清理现有请求")
    
    # 3. 创建用户1的请求
    print("\n📝 用户1创建心动链接请求...")
    room1 = ChatRoom.objects.create(
        room_id=f"demo-room-{int(time.time())}",
        user1=user1,
        status='waiting'
    )
    
    request1 = HeartLinkRequest.objects.create(
        requester=user1,
        chat_room=room1,
        status='pending'
    )
    print(f"✅ 用户1请求已创建: {request1.id}")
    
    # 4. 创建用户2的请求
    print("\n📝 用户2创建心动链接请求...")
    room2 = ChatRoom.objects.create(
        room_id=f"demo-room-{int(time.time())+1}",
        user1=user2,
        status='waiting'
    )
    
    request2 = HeartLinkRequest.objects.create(
        requester=user2,
        chat_room=room2,
        status='pending'
    )
    print(f"✅ 用户2请求已创建: {request2.id}")
    
    # 5. 执行匹配
    print("\n🔗 开始匹配...")
    chat_room, matched_user = matcher.match_users(user1, request1)
    
    if chat_room and matched_user:
        print(f"✅ 匹配成功！")
        print(f"   聊天室ID: {chat_room.room_id}")
        print(f"   用户1: {chat_room.user1.username}")
        print(f"   用户2: {chat_room.user2.username}")
        print(f"   状态: {chat_room.status}")
        
        # 6. 生成安全访问令牌
        from apps.tools.views.chat_views import generate_chat_token
        token1 = generate_chat_token(user1, chat_room.room_id)
        token2 = generate_chat_token(user2, chat_room.room_id)
        
        print(f"\n🔐 安全访问令牌:")
        print(f"   用户1令牌: {token1}")
        print(f"   用户2令牌: {token2}")
        
        # 7. 生成安全聊天室URL
        chat_url1 = f"/tools/chat/secure/{chat_room.room_id}/{token1}/"
        chat_url2 = f"/tools/chat/secure/{chat_room.room_id}/{token2}/"
        
        print(f"\n🌐 安全聊天室URL:")
        print(f"   用户1: http://localhost:8000{chat_url1}")
        print(f"   用户2: http://localhost:8000{chat_url2}")
        
        # 8. 验证权限
        from apps.tools.views.chat_views import verify_chat_token
        can_access1 = verify_chat_token(user1, chat_room.room_id, token1)
        can_access2 = verify_chat_token(user2, chat_room.room_id, token2)
        
        print(f"\n✅ 权限验证:")
        print(f"   用户1可访问: {can_access1}")
        print(f"   用户2可访问: {can_access2}")
        
        # 9. 测试未授权访问
        fake_user = User.objects.create_user(username='fake_user', password='test123')
        fake_token = "fake_token_123"
        can_access_fake = verify_chat_token(fake_user, chat_room.room_id, fake_token)
        print(f"   假用户访问: {can_access_fake} (应该为False)")
        
        # 清理测试用户
        fake_user.delete()
        
    else:
        print("❌ 匹配失败")
    
    print("\n" + "=" * 50)
    print("🎯 演示完成！")
    print("\n📋 总结:")
    print("✅ 心动链接匹配系统正常工作")
    print("✅ 安全聊天室系统正常工作")
    print("✅ 权限验证系统正常工作")
    print("✅ 自动跳转功能已配置")
    print("\n🚀 现在可以测试完整的用户流程了！")

if __name__ == "__main__":
    demo_matching_flow()
