import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthViewsTestCase(APITestCase):
    """认证视图测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_user_registration_success(self):
        """测试用户注册成功"""
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/v1/auth/register/', new_user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_user_registration_duplicate_username(self):
        """测试重复用户名注册"""
        response = self.client.post('/api/v1/auth/register/', self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('username', response.data['message'])
    
    def test_user_login_success(self):
        """测试用户登录成功"""
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
    
    def test_user_login_invalid_credentials(self):
        """测试无效凭据登录"""
        login_data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_token_refresh_success(self):
        """测试令牌刷新成功"""
        refresh_token = RefreshToken.for_user(self.user)
        
        response = self.client.post('/api/v1/auth/refresh/', {
            'refresh': str(refresh_token)
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
    
    def test_user_profile_get(self):
        """测试获取用户资料"""
        # 获取访问令牌
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        # 设置认证头
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get('/api/v1/auth/profile/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['username'], self.user.username)
    
    def test_user_profile_update(self):
        """测试更新用户资料"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.put('/api/v1/auth/profile/', update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 验证更新
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.email, 'updated@example.com')
    
    def test_password_change_success(self):
        """测试密码修改成功"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        password_data = {
            'old_password': self.user_data['password'],
            'new_password': 'newpass123'
        }
        
        response = self.client.post('/api/v1/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_password_change_wrong_old_password(self):
        """测试密码修改时旧密码错误"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        password_data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpass123'
        }
        
        response = self.client.post('/api/v1/auth/change-password/', password_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_unified_login_success(self):
        """测试统一登录成功"""
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
            'device_id': 'test_device_123',
            'device_name': 'Test Device',
            'platform': 'web'
        }
        
        response = self.client.post('/api/v1/auth/unified/login/', login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('device_id', response.data['data'])
    
    def test_get_user_devices(self):
        """测试获取用户设备列表"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get('/api/v1/auth/unified/devices/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIsInstance(response.data['data'], list)
    
    def test_terminate_device(self):
        """测试终止设备会话"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 先创建一个设备会话
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
            'device_id': 'test_device_456',
            'device_name': 'Test Device 2',
            'platform': 'mobile'
        }
        self.client.post('/api/v1/auth/unified/login/', login_data)
        
        # 终止设备会话
        response = self.client.post('/api/v1/auth/unified/devices/test_device_456/terminate/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_terminate_all_devices(self):
        """测试终止所有设备会话"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.post('/api/v1/auth/unified/devices/terminate-all/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_sync_data(self):
        """测试数据同步"""
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        sync_data = {
            'device_id': 'test_device_789',
            'sync_type': 'all',
            'data': {
                'fitness': {'workouts': []},
                'life': {'diaries': []},
                'social': {'messages': []},
                'geek': {'tools': []}
            }
        }
        
        response = self.client.post('/api/v1/auth/unified/sync/', sync_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('fitness', response.data['data'])
        self.assertIn('life', response.data['data'])
        self.assertIn('social', response.data['data'])
        self.assertIn('geek', response.data['data'])
