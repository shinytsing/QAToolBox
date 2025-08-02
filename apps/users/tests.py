from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import (
    UserRole, UserStatus, UserMembership, UserActionLog, 
    UserActivityLog, UserSessionStats, APIUsageStats, Profile, UserTheme
)
import json
from datetime import timedelta


class UserRoleModelTest(TestCase):
    """用户角色模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_role_creation(self):
        """测试用户角色创建"""
        role = UserRole.objects.create(
            user=self.user,
            role='user'
        )
        
        self.assertEqual(role.user, self.user)
        self.assertEqual(role.role, 'user')
        self.assertFalse(role.is_admin)
    
    def test_admin_role(self):
        """测试管理员角色"""
        role = UserRole.objects.create(
            user=self.user,
            role='admin'
        )
        
        self.assertTrue(role.is_admin)
    
    def test_role_str_representation(self):
        """测试角色字符串表示"""
        role = UserRole.objects.create(
            user=self.user,
            role='admin'
        )
        
        self.assertIn('testuser', str(role))
        self.assertIn('管理员', str(role))


class UserStatusModelTest(TestCase):
    """用户状态模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_status_creation(self):
        """测试用户状态创建"""
        status_obj = UserStatus.objects.create(
            user=self.user,
            status='active'
        )
        
        self.assertEqual(status_obj.user, self.user)
        self.assertEqual(status_obj.status, 'active')
        self.assertTrue(status_obj.is_active)
    
    def test_suspended_status(self):
        """测试暂停状态"""
        future_time = timezone.now() + timedelta(hours=1)
        status_obj = UserStatus.objects.create(
            user=self.user,
            status='suspended',
            suspended_until=future_time
        )
        
        self.assertFalse(status_obj.is_active)
    
    def test_expired_suspension(self):
        """测试过期的暂停状态"""
        past_time = timezone.now() - timedelta(hours=1)
        status_obj = UserStatus.objects.create(
            user=self.user,
            status='suspended',
            suspended_until=past_time
        )
        
        self.assertTrue(status_obj.is_active)


class UserMembershipModelTest(TestCase):
    """用户会员模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_free_membership(self):
        """测试免费会员"""
        membership = UserMembership.objects.create(
            user=self.user,
            membership_type='free'
        )
        
        self.assertTrue(membership.is_valid)
    
    def test_premium_membership_with_end_date(self):
        """测试有结束时间的高级会员"""
        future_time = timezone.now() + timedelta(days=30)
        membership = UserMembership.objects.create(
            user=self.user,
            membership_type='premium',
            end_date=future_time
        )
        
        self.assertTrue(membership.is_valid)
    
    def test_expired_membership(self):
        """测试过期会员"""
        past_time = timezone.now() - timedelta(days=1)
        membership = UserMembership.objects.create(
            user=self.user,
            membership_type='premium',
            end_date=past_time
        )
        
        self.assertFalse(membership.is_valid)
    
    def test_inactive_membership(self):
        """测试非活跃会员"""
        membership = UserMembership.objects.create(
            user=self.user,
            membership_type='premium',
            is_active=False
        )
        
        self.assertFalse(membership.is_valid)


class UserActionLogModelTest(TestCase):
    """用户操作日志模型测试"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.target_user = User.objects.create_user(
            username='target',
            email='target@example.com',
            password='targetpass123'
        )
    
    def test_action_log_creation(self):
        """测试操作日志创建"""
        log = UserActionLog.objects.create(
            admin_user=self.admin_user,
            target_user=self.target_user,
            action='status_change',
            details='将用户状态改为暂停'
        )
        
        self.assertEqual(log.admin_user, self.admin_user)
        self.assertEqual(log.target_user, self.target_user)
        self.assertEqual(log.action, 'status_change')
        self.assertIsNotNone(log.created_at)


class UserActivityLogModelTest(TestCase):
    """用户活动日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_activity_log_creation(self):
        """测试活动日志创建"""
        log = UserActivityLog.objects.create(
            user=self.user,
            activity_type='login',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0',
            endpoint='/users/login/',
            method='POST',
            status_code=200,
            response_time=0.5
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.activity_type, 'login')
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.status_code, 200)
    
    def test_activity_log_ordering(self):
        """测试活动日志排序"""
        log1 = UserActivityLog.objects.create(
            user=self.user,
            activity_type='login'
        )
        log2 = UserActivityLog.objects.create(
            user=self.user,
            activity_type='logout'
        )
        
        logs = UserActivityLog.objects.all()
        self.assertEqual(logs[0], log2)  # 应该按创建时间倒序


class UserViewsTest(TestCase):
    """用户视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """测试登录页面GET请求"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '登录')
    
    def test_login_view_post_success(self):
        """测试登录成功"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到首页
    
    def test_login_view_post_failure(self):
        """测试登录失败"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # 返回登录页面
        self.assertContains(response, '用户名或密码错误')
    
    def test_register_view_get(self):
        """测试注册页面GET请求"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '注册')
    
    def test_register_view_post_success(self):
        """测试注册成功"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
        
        # 验证用户是否创建
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_view_post_password_mismatch(self):
        """测试注册密码不匹配"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '密码不匹配')
    
    def test_profile_view_requires_login(self):
        """测试个人资料页面需要登录"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # 重定向到登录页面
    
    def test_profile_view_with_login(self):
        """测试登录后可以访问个人资料"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '个人资料')


class UserAPITest(APITestCase):
    """用户API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_theme_api_get(self):
        """测试主题API GET请求"""
        response = self.client.get('/users/theme/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_theme_api_post(self):
        """测试主题API POST请求"""
        data = {
            'mode': 'work',
            'theme_style': 'dark'
        }
        response = self.client.post('/users/theme/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 验证主题是否保存
        theme = UserTheme.objects.get(user=self.user)
        self.assertEqual(theme.mode, 'work')
        self.assertEqual(theme.theme_style, 'dark')
    
    def test_theme_api_invalid_data(self):
        """测试主题API无效数据"""
        data = {
            'mode': 'invalid_mode',
            'theme_style': 'invalid_style'
        }
        response = self.client.post('/users/theme/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SecurityTest(TestCase):
    """安全性测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_password_strength_validation(self):
        """测试密码强度验证"""
        # 测试弱密码
        response = self.client.post(reverse('register'), {
            'username': 'weakuser',
            'email': 'weak@example.com',
            'password1': '123',
            'password2': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '密码太短')
    
    def test_username_validation(self):
        """测试用户名验证"""
        # 测试特殊字符用户名
        response = self.client.post(reverse('register'), {
            'username': 'user<script>',
            'email': 'test@example.com',
            'password1': 'validpass123',
            'password2': 'validpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '用户名只能包含字母、数字和下划线')
    
    def test_email_validation(self):
        """测试邮箱验证"""
        # 测试无效邮箱格式
        response = self.client.post(reverse('register'), {
            'username': 'validuser',
            'email': 'invalid-email',
            'password1': 'validpass123',
            'password2': 'validpass123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '请输入有效的邮箱地址')
    
    def test_session_security(self):
        """测试会话安全"""
        self.client.login(username='testuser', password='testpass123')
        
        # 测试会话是否正常工作
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # 测试登出后会话是否清除
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)


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
    
    def test_login_performance(self):
        """测试登录性能"""
        import time
        
        start_time = time.time()
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        login_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 302)
        self.assertLess(login_time, 1.0)  # 登录时间应该小于1秒
    
    def test_user_creation_performance(self):
        """测试用户创建性能"""
        import time
        
        start_time = time.time()
        user = User.objects.create_user(
            username=f'perfuser{time.time()}',
            email=f'perf{time.time()}@example.com',
            password='perfpass123'
        )
        creation_time = time.time() - start_time
        
        self.assertIsNotNone(user)
        self.assertLess(creation_time, 0.1)  # 用户创建时间应该小于0.1秒


class IntegrationTest(TestCase):
    """集成测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_complete_user_workflow(self):
        """测试完整的用户工作流程"""
        # 1. 用户注册
        response = self.client.post(reverse('register'), {
            'username': 'workflowuser',
            'email': 'workflow@example.com',
            'password1': 'workflowpass123',
            'password2': 'workflowpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 2. 用户登录
        response = self.client.post(reverse('login'), {
            'username': 'workflowuser',
            'password': 'workflowpass123'
        })
        self.assertEqual(response.status_code, 302)
        
        # 3. 访问个人资料
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # 4. 用户登出
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
    
    def test_user_role_integration(self):
        """测试用户角色集成"""
        # 创建用户角色
        role = UserRole.objects.create(
            user=self.user,
            role='admin'
        )
        
        # 登录用户
        self.client.login(username='testuser', password='testpass123')
        
        # 测试管理员功能（如果有的话）
        # 这里可以根据实际的管理员功能进行测试
        
        self.assertTrue(role.is_admin)
    
    def test_user_activity_tracking(self):
        """测试用户活动跟踪"""
        # 登录用户
        self.client.login(username='testuser', password='testpass123')
        
        # 访问页面
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
        # 检查活动日志是否创建
        activity_logs = UserActivityLog.objects.filter(user=self.user)
        self.assertGreater(len(activity_logs), 0)
