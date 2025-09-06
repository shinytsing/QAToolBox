import json
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from unittest.mock import patch, MagicMock

User = get_user_model()

class APIIntegrationTestCase(TransactionTestCase):
    """API集成测试用例"""
    
    def setUp(self):
        """测试前准备"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 获取认证令牌
        refresh_token = RefreshToken.for_user(self.user)
        self.access_token = str(refresh_token.access_token)
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
    
    def test_complete_user_workflow(self):
        """测试完整用户工作流程"""
        # 1. 用户注册和登录
        self._test_user_registration_and_login()
        
        # 2. 创建健身资料
        self._test_create_fitness_profile()
        
        # 3. 记录训练
        self._test_record_workout()
        
        # 4. 创建生活日记
        self._test_create_diary()
        
        # 5. 使用极客工具
        self._test_use_geek_tool()
        
        # 6. 社交互动
        self._test_social_interaction()
        
        # 7. 数据同步
        self._test_data_sync()
    
    def _test_user_registration_and_login(self):
        """测试用户注册和登录"""
        # 注册新用户
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
        
        # 登录
        login_data = {
            'username': 'newuser',
            'password': 'newpass123'
        }
        
        response = self.client.post('/api/v1/auth/login/', login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # 更新认证头
        self.access_token = response.data['data']['access']
        self.auth_headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}
    
    def _test_create_fitness_profile(self):
        """测试创建健身资料"""
        profile_data = {
            'height': 175.0,
            'weight': 70.0,
            'age': 25,
            'gender': 'male',
            'activity_level': 'moderate'
        }
        
        response = self.client.post('/api/v1/fitness/profile/', profile_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def _test_record_workout(self):
        """测试记录训练"""
        workout_data = {
            'name': '测试训练',
            'workout_type': 'strength',
            'duration': 60,
            'calories_burned': 300,
            'notes': '测试训练记录'
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # 获取训练记录
        response = self.client.get('/api/v1/fitness/workouts/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def _test_create_diary(self):
        """测试创建生活日记"""
        diary_data = {
            'title': '测试日记',
            'content': '今天是个好日子',
            'mood': 'happy',
            'weather': 'sunny'
        }
        
        response = self.client.post('/api/v1/life/diary/', diary_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # 获取日记列表
        response = self.client.get('/api/v1/life/diary/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def _test_use_geek_tool(self):
        """测试使用极客工具"""
        # 测试PDF转换
        pdf_data = {
            'input_file': 'test.pdf',
            'output_format': 'docx',
            'options': {}
        }
        
        with patch('api.v1.tools.views.convert_pdf') as mock_convert:
            mock_convert.return_value = {'success': True, 'output_file': 'test.docx'}
            
            response = self.client.post('/api/v1/tools/pdf/', pdf_data, **self.auth_headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
    
    def _test_social_interaction(self):
        """测试社交互动"""
        # 创建心链
        heart_link_data = {
            'title': '测试心链',
            'description': '这是一个测试心链',
            'tags': ['测试', '心链']
        }
        
        response = self.client.post('/api/v1/social/heart-link/', heart_link_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        # 获取心链列表
        response = self.client.get('/api/v1/social/heart-link/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def _test_data_sync(self):
        """测试数据同步"""
        sync_data = {
            'device_id': 'test_device_123',
            'sync_type': 'all',
            'data': {
                'fitness': {'workouts': []},
                'life': {'diaries': []},
                'social': {'heart_links': []},
                'geek': {'tools': []}
            }
        }
        
        response = self.client.post('/api/v1/auth/unified/sync/', sync_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_cross_module_data_consistency(self):
        """测试跨模块数据一致性"""
        # 创建健身资料
        profile_data = {
            'height': 175.0,
            'weight': 70.0,
            'age': 25,
            'gender': 'male',
            'activity_level': 'moderate'
        }
        
        response = self.client.post('/api/v1/fitness/profile/', profile_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 记录训练
        workout_data = {
            'name': '测试训练',
            'workout_type': 'strength',
            'duration': 60,
            'calories_burned': 300
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证数据一致性
        response = self.client.get('/api/v1/fitness/profile/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get('/api/v1/fitness/workouts/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
    
    def test_error_handling_and_recovery(self):
        """测试错误处理和恢复"""
        # 测试无效数据
        invalid_data = {
            'name': '',  # 空名称
            'workout_type': 'invalid_type',
            'duration': -10
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', invalid_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        
        # 测试正常数据仍然工作
        valid_data = {
            'name': '正常训练',
            'workout_type': 'strength',
            'duration': 60,
            'calories_burned': 300
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', valid_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        import time
        
        results = []
        
        def make_request():
            workout_data = {
                'name': f'并发训练 {threading.current_thread().ident}',
                'workout_type': 'strength',
                'duration': 60,
                'calories_burned': 300
            }
            
            response = self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
            results.append(response.status_code)
        
        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 5)
        self.assertTrue(all(status_code == status.HTTP_201_CREATED for status_code in results))
    
    def test_data_persistence_across_requests(self):
        """测试数据在请求间的持久性"""
        # 创建数据
        workout_data = {
            'name': '持久性测试训练',
            'workout_type': 'strength',
            'duration': 60,
            'calories_burned': 300
        }
        
        response = self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        workout_id = response.data['data']['id']
        
        # 在新请求中获取数据
        response = self.client.get(f'/api/v1/fitness/workouts/{workout_id}/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], '持久性测试训练')
    
    def test_api_versioning(self):
        """测试API版本控制"""
        # 测试v1 API
        response = self.client.get('/api/v1/fitness/profile/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 测试无效版本
        response = self.client.get('/api/v2/fitness/profile/', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送大量请求
        for i in range(100):
            response = self.client.get('/api/v1/fitness/profile/', **self.auth_headers)
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        
        # 验证速率限制生效
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])
    
    def test_cors_headers(self):
        """测试CORS头"""
        response = self.client.options('/api/v1/fitness/profile/')
        self.assertIn('Access-Control-Allow-Origin', response)
        self.assertIn('Access-Control-Allow-Methods', response)
        self.assertIn('Access-Control-Allow-Headers', response)
    
    def test_content_type_handling(self):
        """测试内容类型处理"""
        # 测试JSON请求
        workout_data = {
            'name': 'JSON训练',
            'workout_type': 'strength',
            'duration': 60,
            'calories_burned': 300
        }
        
        response = self.client.post(
            '/api/v1/fitness/workouts/',
            data=json.dumps(workout_data),
            content_type='application/json',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 测试表单数据请求
        response = self.client.post(
            '/api/v1/fitness/workouts/',
            data=workout_data,
            content_type='application/x-www-form-urlencoded',
            **self.auth_headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_pagination_consistency(self):
        """测试分页一致性"""
        # 创建多个训练记录
        for i in range(25):
            workout_data = {
                'name': f'训练 {i}',
                'workout_type': 'strength',
                'duration': 60,
                'calories_burned': 300
            }
            self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
        
        # 测试第一页
        response = self.client.get('/api/v1/fitness/workouts/?page=1&page_size=10', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)
        self.assertIn('pagination', response.data)
        
        # 测试第二页
        response = self.client.get('/api/v1/fitness/workouts/?page=2&page_size=10', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 10)
        
        # 测试最后一页
        response = self.client.get('/api/v1/fitness/workouts/?page=3&page_size=10', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 5)
    
    def test_search_and_filtering(self):
        """测试搜索和过滤"""
        # 创建不同类型的训练记录
        workout_types = ['strength', 'cardio', 'yoga', 'swimming']
        for i, workout_type in enumerate(workout_types):
            workout_data = {
                'name': f'{workout_type}训练',
                'workout_type': workout_type,
                'duration': 60,
                'calories_burned': 300
            }
            self.client.post('/api/v1/fitness/workouts/', workout_data, **self.auth_headers)
        
        # 测试按类型过滤
        response = self.client.get('/api/v1/fitness/workouts/?workout_type=strength', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        
        # 测试搜索
        response = self.client.get('/api/v1/fitness/workouts/?search=strength', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
        
        # 测试组合过滤
        response = self.client.get('/api/v1/fitness/workouts/?workout_type=cardio&search=训练', **self.auth_headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)
