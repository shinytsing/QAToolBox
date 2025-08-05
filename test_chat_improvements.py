#!/usr/bin/env python3
"""
测试聊天功能改进
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import HeartLinkRequest, ChatRoom, ChatMessage, UserOnlineStatus

User = get_user_model()

class ChatImprovementsTest(TestCase):
    def setUp(self):
        """设置测试环境"""
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        
        # 创建客户端
        self.client = Client()
        
    def test_mark_messages_read_accuracy(self):
        """测试已读未读状态的准确性"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-123',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 用户2发送消息给用户1
        message1 = ChatMessage.objects.create(
            room=chat_room,
            sender=self.user2,
            content='你好！',
            message_type='text',
            is_read=False
        )
        
        # 用户1发送消息给用户2
        message2 = ChatMessage.objects.create(
            room=chat_room,
            sender=self.user1,
            content='你好！',
            message_type='text',
            is_read=False
        )
        
        # 用户1标记消息为已读
        response = self.client.post(f'/tools/api/chat/{chat_room.room_id}/mark-read/', {
            'action': 'mark_read'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证只有用户2发送的消息被标记为已读
        self.assertTrue(data['success'])
        self.assertEqual(data['marked_count'], 1)
        
        # 重新获取消息状态
        message1.refresh_from_db()
        message2.refresh_from_db()
        
        # 用户2发送的消息应该被标记为已读
        self.assertTrue(message1.is_read)
        # 用户1发送的消息应该保持未读状态
        self.assertFalse(message2.is_read)
        
    def test_reject_reconnect_functionality(self):
        """测试拒绝重连功能"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个活跃的聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-456',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 创建一个已匹配的心动链接请求
        heart_request = HeartLinkRequest.objects.create(
            requester=self.user1,
            matched_with=self.user2,
            chat_room=chat_room,
            status='matched',
            matched_at=timezone.now()
        )
        
        # 测试拒绝重连（结束聊天室）
        response = self.client.post('/tools/api/heart-link/cleanup/', {
            'room_id': chat_room.room_id
        }, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证聊天室被结束
        self.assertTrue(data['success'])
        self.assertEqual(data['room_id'], chat_room.room_id)
        
        # 重新获取聊天室状态
        chat_room.refresh_from_db()
        self.assertEqual(chat_room.status, 'ended')
        
        # 验证相关的心动链接请求也被标记为过期
        heart_request.refresh_from_db()
        self.assertEqual(heart_request.status, 'expired')
        
    def test_reconnect_with_reject_option(self):
        """测试重连时提供拒绝选项"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个活跃的聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-789',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 测试创建心动链接请求（应该返回重连信息）
        response = self.client.post('/tools/api/heart-link/create/', {
            'action': 'create'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证返回重连信息
        self.assertTrue(data['success'])
        self.assertTrue(data['reconnect'])
        self.assertEqual(data['room_id'], chat_room.room_id)
        self.assertEqual(data['matched_user'], 'testuser2')
        
    def test_message_read_status_display(self):
        """测试消息已读状态显示"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-999',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 获取消息列表
        response = self.client.get(f'/tools/api/chat/{chat_room.room_id}/messages/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证消息格式正确
        self.assertTrue(data['success'])
        self.assertIn('messages', data)
        
        # 如果有消息，验证已读状态字段存在
        if data['messages']:
            for message in data['messages']:
                self.assertIn('is_read', message)
                self.assertIn('is_own', message)
                
    def test_cleanup_api_with_room_id(self):
        """测试带room_id参数的清理API"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-cleanup',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 测试带room_id的清理请求
        response = self.client.post('/tools/api/heart-link/cleanup/', 
            json.dumps({'room_id': chat_room.room_id}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证成功结束指定聊天室
        self.assertTrue(data['success'])
        self.assertEqual(data['room_id'], chat_room.room_id)
        
    def test_cleanup_api_without_room_id(self):
        """测试不带room_id参数的清理API（全局清理）"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 测试不带room_id的清理请求
        response = self.client.post('/tools/api/heart-link/cleanup/', {
            'action': 'cleanup'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证执行全局清理
        self.assertTrue(data['success'])
        self.assertIn('expired_requests', data)
        self.assertIn('ended_rooms', data)

if __name__ == '__main__':
    # 运行测试
    import unittest
    unittest.main() 