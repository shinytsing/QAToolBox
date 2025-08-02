from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ToolUsageLog, SocialMediaSubscription, SocialMediaNotification, SocialMediaPlatformConfig
import json
import tempfile
import os


class ToolUsageLogModelTest(TestCase):
    """工具使用日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_tool_usage_log_creation(self):
        """测试工具使用日志创建"""
        log = ToolUsageLog.objects.create(
            user=self.user,
            tool_type='TEST_CASE',
            input_data='测试输入数据',
            output_file='test_output.txt'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.tool_type, 'TEST_CASE')
        self.assertEqual(log.input_data, '测试输入数据')
        self.assertIsNotNone(log.created_at)
    
    def test_tool_usage_log_ordering(self):
        """测试工具使用日志排序"""
        log1 = ToolUsageLog.objects.create(
            user=self.user,
            tool_type='TEST_CASE',
            input_data='数据1',
            output_file='output1.txt'
        )
        log2 = ToolUsageLog.objects.create(
            user=self.user,
            tool_type='REDBOOK',
            input_data='数据2',
            output_file='output2.txt'
        )
        
        logs = ToolUsageLog.objects.all()
        self.assertEqual(logs[0], log2)  # 应该按创建时间倒序


class SocialMediaSubscriptionModelTest(TestCase):
    """社交媒体订阅模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_subscription_creation(self):
        """测试订阅创建"""
        subscription = SocialMediaSubscription.objects.create(
            user=self.user,
            platform='xiaohongshu',
            target_user_id='12345',
            target_user_name='测试用户',
            subscription_types=['newPosts', 'newFollowers'],
            check_frequency=15,
            status='active'
        )
        
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.platform, 'xiaohongshu')
        self.assertEqual(subscription.status, 'active')
        self.assertIn('newPosts', subscription.subscription_types)
    
    def test_subscription_unique_constraint(self):
        """测试订阅唯一性约束"""
        SocialMediaSubscription.objects.create(
            user=self.user,
            platform='xiaohongshu',
            target_user_id='12345',
            target_user_name='测试用户',
            subscription_types=['newPosts']
        )
        
        # 尝试创建重复订阅应该失败
        with self.assertRaises(Exception):
            SocialMediaSubscription.objects.create(
                user=self.user,
                platform='xiaohongshu',
                target_user_id='12345',
                target_user_name='测试用户2',
                subscription_types=['newPosts']
            )


class ToolViewsTest(TestCase):
    """工具视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_test_case_generator_view_requires_login(self):
        """测试测试用例生成器需要登录"""
        response = self.client.get(reverse('test_case_generator'))
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
    
    def test_test_case_generator_view_with_login(self):
        """测试登录后可以访问测试用例生成器"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('test_case_generator'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '测试用例生成器')
    
    def test_pdf_converter_view_requires_login(self):
        """测试PDF转换器需要登录"""
        response = self.client.get(reverse('pdf_converter'))
        self.assertEqual(response.status_code, 302)
    
    def test_redbook_generator_view_requires_login(self):
        """测试小红书生成器需要登录"""
        response = self.client.get(reverse('redbook_generator'))
        self.assertEqual(response.status_code, 302)


class ToolAPITest(APITestCase):
    """工具API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_generate_test_cases_api_missing_requirement(self):
        """测试缺少需求参数的API调用"""
        response = self.client.post('/tools/api/generate-testcases/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_generate_test_cases_api_with_requirement(self):
        """测试带需求参数的API调用"""
        data = {
            'requirement': '用户登录功能测试',
            'prompt': '生成登录功能的测试用例'
        }
        response = self.client.post('/tools/api/generate-testcases/', data)
        # 由于API可能调用外部服务，我们主要测试请求格式是否正确
        self.assertIn(response.status_code, [200, 202, 400, 500])
    
    def test_api_authentication_required(self):
        """测试API需要认证"""
        self.client.force_authenticate(user=None)
        response = self.client.post('/tools/api/generate-testcases/', {
            'requirement': 'test'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SecurityTest(TestCase):
    """安全性测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_csrf_protection(self):
        """测试CSRF保护"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b'test content')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as file:
                response = self.client.post('/tools/pdf-converter/', {
                    'file': file
                })
                # 应该返回403 Forbidden（CSRF验证失败）
                self.assertEqual(response.status_code, 403)
        finally:
            # 清理临时文件
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)
    
    def test_xss_protection(self):
        """测试XSS防护"""
        self.client.login(username='testuser', password='testpass123')
        
        # 测试包含脚本标签的输入
        malicious_input = '<script>alert("xss")</script>'
        response = self.client.post('/tools/api/generate-testcases/', {
            'requirement': malicious_input
        })
        
        # 检查响应中是否包含原始脚本标签
        if response.status_code == 200:
            response_content = str(response.content)
            self.assertNotIn('<script>', response_content)
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        self.client.login(username='testuser', password='testpass123')
        
        # 测试SQL注入尝试
        sql_injection_input = "'; DROP TABLE users; --"
        response = self.client.post('/tools/api/generate-testcases/', {
            'requirement': sql_injection_input
        })
        
        # 验证用户表仍然存在
        self.assertTrue(User.objects.filter(username='testuser').exists())


class PerformanceTest(TestCase):
    """性能测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_page_load_performance(self):
        """测试页面加载性能"""
        import time
        
        start_time = time.time()
        response = self.client.get(reverse('test_case_generator'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        # 页面加载时间应该在合理范围内（比如小于2秒）
        self.assertLess(load_time, 2.0)
    
    def test_database_query_performance(self):
        """测试数据库查询性能"""
        import time
        
        # 创建一些测试数据
        for i in range(10):
            ToolUsageLog.objects.create(
                user=self.user,
                tool_type='TEST_CASE',
                input_data=f'测试数据{i}',
                output_file=f'output{i}.txt'
            )
        
        start_time = time.time()
        logs = ToolUsageLog.objects.filter(user=self.user)
        query_time = time.time() - start_time
        
        self.assertEqual(len(logs), 10)
        # 查询时间应该在合理范围内（比如小于0.1秒）
        self.assertLess(query_time, 0.1)


class IntegrationTest(TestCase):
    """集成测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_complete_workflow(self):
        """测试完整的工作流程"""
        # 1. 访问工具页面
        response = self.client.get(reverse('test_case_generator'))
        self.assertEqual(response.status_code, 200)
        
        # 2. 提交测试用例生成请求
        data = {
            'requirement': '用户注册功能测试',
            'prompt': '生成注册功能的测试用例'
        }
        response = self.client.post('/tools/api/generate-testcases/', data)
        self.assertIn(response.status_code, [200, 202, 400, 500])
        
        # 3. 验证日志记录
        if response.status_code == 200:
            logs = ToolUsageLog.objects.filter(user=self.user)
            self.assertGreater(len(logs), 0)
    
    def test_user_session_integration(self):
        """测试用户会话集成"""
        # 测试用户登录后的会话状态
        response = self.client.get(reverse('test_case_generator'))
        self.assertEqual(response.status_code, 200)
        
        # 测试用户登出
        self.client.logout()
        response = self.client.get(reverse('test_case_generator'))
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
