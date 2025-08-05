#!/usr/bin/env python3
"""
测试心动链接重连功能
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.tools.models import HeartLinkRequest, ChatRoom, UserOnlineStatus

User = get_user_model()

class HeartLinkReconnectTest(TestCase):
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
        
    def test_reconnect_with_active_chatroom(self):
        """测试用户有活跃聊天室时的重连功能"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 创建一个活跃的聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-123',
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
        
        # 测试创建心动链接请求API（应该返回重连信息）
        response = self.client.post('/tools/api/heart-link/create/', {
            'action': 'create'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证返回重连信息
        self.assertTrue(data['success'])
        self.assertTrue(data['reconnect'])
        self.assertEqual(data['room_id'], 'test-room-123')
        self.assertEqual(data['matched_user'], 'testuser2')
        self.assertIn('重连', data['message'])
        
    def test_normal_match_without_active_chatroom(self):
        """测试没有活跃聊天室时的正常匹配流程"""
        # 登录用户1
        self.client.force_login(self.user1)
        
        # 测试创建心动链接请求API（应该正常创建新请求）
        response = self.client.post('/tools/api/heart-link/create/', {
            'action': 'create'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证返回正常匹配信息
        self.assertTrue(data['success'])
        self.assertFalse(data.get('reconnect', False))
        self.assertIn('request_id', data)
        
    def test_status_check_with_active_chatroom(self):
        """测试状态检查API在有活跃聊天室时的返回"""
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
        
        # 测试状态检查API
        response = self.client.get('/tools/api/heart-link/status/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # 验证返回匹配状态
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'matched')
        self.assertEqual(data['room_id'], 'test-room-456')
        self.assertEqual(data['matched_user'], 'testuser2')
        
    def test_reconnect_button_text(self):
        """测试重连按钮的文本显示"""
        # 这个测试验证前端逻辑，实际测试需要在前端进行
        # 这里只是验证后端API返回的数据结构
        self.client.force_login(self.user1)
        
        # 创建活跃聊天室
        chat_room = ChatRoom.objects.create(
            room_id='test-room-789',
            user1=self.user1,
            user2=self.user2,
            status='active',
            created_at=timezone.now()
        )
        
        # 测试API返回
        response = self.client.post('/tools/api/heart-link/create/', {
            'action': 'create'
        })
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['reconnect'])
        # 前端应该根据reconnect字段显示"重进房间"按钮

if __name__ == '__main__':
    # 运行测试
    import unittest
    unittest.main() 