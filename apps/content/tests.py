from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Suggestion, Feedback, Announcement
import json


class SuggestionModelTest(TestCase):
    """建议模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_suggestion_creation(self):
        """测试建议创建"""
        suggestion = Suggestion.objects.create(
            user=self.user,
            title='测试建议',
            content='这是一个测试建议的内容',
            category='feature',
            priority='medium'
        )
        
        self.assertEqual(suggestion.user, self.user)
        self.assertEqual(suggestion.title, '测试建议')
        self.assertEqual(suggestion.category, 'feature')
        self.assertEqual(suggestion.priority, 'medium')
        self.assertEqual(suggestion.status, 'pending')
        self.assertIsNotNone(suggestion.created_at)
    
    def test_suggestion_str_representation(self):
        """测试建议字符串表示"""
        suggestion = Suggestion.objects.create(
            user=self.user,
            title='测试建议',
            content='内容',
            category='feature'
        )
        
        self.assertIn('测试建议', str(suggestion))
        self.assertIn('testuser', str(suggestion))


class FeedbackModelTest(TestCase):
    """反馈模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_feedback_creation(self):
        """测试反馈创建"""
        feedback = Feedback.objects.create(
            user=self.user,
            title='测试反馈',
            content='这是一个测试反馈的内容',
            feedback_type='bug',
            rating=4
        )
        
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.title, '测试反馈')
        self.assertEqual(feedback.feedback_type, 'bug')
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.status, 'pending')
    
    def test_feedback_rating_validation(self):
        """测试反馈评分验证"""
        # 测试有效评分
        feedback = Feedback.objects.create(
            user=self.user,
            title='测试反馈',
            content='内容',
            feedback_type='bug',
            rating=5
        )
        self.assertEqual(feedback.rating, 5)
        
        # 测试边界值
        feedback2 = Feedback.objects.create(
            user=self.user,
            title='测试反馈2',
            content='内容',
            feedback_type='bug',
            rating=1
        )
        self.assertEqual(feedback2.rating, 1)


class AnnouncementModelTest(TestCase):
    """公告模型测试"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_announcement_creation(self):
        """测试公告创建"""
        announcement = Announcement.objects.create(
            title='测试公告',
            content='这是一个测试公告的内容',
            author=self.admin_user,
            priority='high',
            is_active=True
        )
        
        self.assertEqual(announcement.title, '测试公告')
        self.assertEqual(announcement.author, self.admin_user)
        self.assertEqual(announcement.priority, 'high')
        self.assertTrue(announcement.is_active)
        self.assertIsNotNone(announcement.created_at)
    
    def test_announcement_str_representation(self):
        """测试公告字符串表示"""
        announcement = Announcement.objects.create(
            title='测试公告',
            content='内容',
            author=self.admin_user
        )
        
        self.assertIn('测试公告', str(announcement))
        self.assertIn('admin', str(announcement))


class ContentViewsTest(TestCase):
    """内容视图测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_suggestion_submission_view(self):
        """测试建议提交视图"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('submit_suggestion'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '提交建议')
    
    def test_suggestion_submission_post(self):
        """测试建议提交POST请求"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('submit_suggestion'), {
            'title': '新功能建议',
            'content': '希望添加新功能',
            'category': 'feature',
            'priority': 'high'
        })
        
        self.assertEqual(response.status_code, 302)  # 重定向到成功页面
        
        # 验证建议是否创建
        suggestion = Suggestion.objects.filter(user=self.user).first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.title, '新功能建议')
    
    def test_feedback_submission_view(self):
        """测试反馈提交视图"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('submit_feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '提交反馈')
    
    def test_feedback_submission_post(self):
        """测试反馈提交POST请求"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('submit_feedback'), {
            'title': 'Bug反馈',
            'content': '发现了一个bug',
            'feedback_type': 'bug',
            'rating': 3
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 验证反馈是否创建
        feedback = Feedback.objects.filter(user=self.user).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.title, 'Bug反馈')
    
    def test_admin_suggestions_view_requires_admin(self):
        """测试管理员建议页面需要管理员权限"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('admin_suggestions'))
        self.assertEqual(response.status_code, 403)  # 禁止访问
    
    def test_admin_suggestions_view_with_admin(self):
        """测试管理员可以访问建议管理页面"""
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(reverse('admin_suggestions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '建议管理')


class ContentAPITest(APITestCase):
    """内容API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_suggestions_api_get(self):
        """测试建议API GET请求"""
        # 创建测试建议
        Suggestion.objects.create(
            user=self.user,
            title='测试建议',
            content='内容',
            category='feature'
        )
        
        response = self.client.get('/content/api/suggestions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_suggestions_api_post(self):
        """测试建议API POST请求"""
        data = {
            'title': 'API测试建议',
            'content': '通过API提交的建议',
            'category': 'feature',
            'priority': 'medium'
        }
        
        response = self.client.post('/content/api/suggestions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证建议是否创建
        suggestion = Suggestion.objects.filter(user=self.user).first()
        self.assertIsNotNone(suggestion)
        self.assertEqual(suggestion.title, 'API测试建议')
    
    def test_suggestions_api_unauthorized(self):
        """测试建议API未授权访问"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/content/api/suggestions/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_feedback_api_get(self):
        """测试反馈API GET请求"""
        # 创建测试反馈
        Feedback.objects.create(
            user=self.user,
            title='测试反馈',
            content='内容',
            feedback_type='bug',
            rating=4
        )
        
        response = self.client.get('/content/api/feedback/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_feedback_api_post(self):
        """测试反馈API POST请求"""
        data = {
            'title': 'API测试反馈',
            'content': '通过API提交的反馈',
            'feedback_type': 'bug',
            'rating': 5
        }
        
        response = self.client.post('/content/api/feedback/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 验证反馈是否创建
        feedback = Feedback.objects.filter(user=self.user).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.title, 'API测试反馈')


class SecurityTest(TestCase):
    """安全性测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_suggestion_xss_protection(self):
        """测试建议XSS防护"""
        self.client.login(username='testuser', password='testpass123')
        
        malicious_content = '<script>alert("xss")</script>'
        response = self.client.post(reverse('submit_suggestion'), {
            'title': 'XSS测试',
            'content': malicious_content,
            'category': 'feature'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 验证内容是否被正确存储（不应该包含脚本标签）
        suggestion = Suggestion.objects.filter(user=self.user).first()
        if suggestion:
            self.assertNotIn('<script>', suggestion.content)
    
    def test_feedback_injection_protection(self):
        """测试反馈注入防护"""
        self.client.login(username='testuser', password='testpass123')
        
        sql_injection_content = "'; DROP TABLE content_suggestion; --"
        response = self.client.post(reverse('submit_feedback'), {
            'title': '注入测试',
            'content': sql_injection_content,
            'feedback_type': 'bug',
            'rating': 1
        })
        
        self.assertEqual(response.status_code, 302)
        
        # 验证数据库表仍然存在
        self.assertTrue(Suggestion.objects.all().exists())
    
    def test_admin_access_control(self):
        """测试管理员访问控制"""
        # 普通用户尝试访问管理员页面
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('admin_suggestions'))
        self.assertEqual(response.status_code, 403)
        
        # 管理员可以访问
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(reverse('admin_suggestions'))
        self.assertEqual(response.status_code, 200)


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
    
    def test_suggestion_creation_performance(self):
        """测试建议创建性能"""
        import time
        
        start_time = time.time()
        response = self.client.post(reverse('submit_suggestion'), {
            'title': '性能测试建议',
            'content': '这是一个性能测试',
            'category': 'feature',
            'priority': 'low'
        })
        creation_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 302)
        self.assertLess(creation_time, 1.0)  # 创建时间应该小于1秒
    
    def test_suggestions_list_performance(self):
        """测试建议列表性能"""
        # 创建多个建议
        for i in range(10):
            Suggestion.objects.create(
                user=self.user,
                title=f'建议{i}',
                content=f'内容{i}',
                category='feature'
            )
        
        import time
        start_time = time.time()
        response = self.client.get(reverse('suggestions_list'))
        load_time = time.time() - start_time
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(load_time, 2.0)  # 加载时间应该小于2秒


class IntegrationTest(TestCase):
    """集成测试"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_complete_suggestion_workflow(self):
        """测试完整的建议工作流程"""
        # 1. 用户提交建议
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('submit_suggestion'), {
            'title': '工作流程测试建议',
            'content': '测试完整的工作流程',
            'category': 'feature',
            'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)
        
        # 2. 管理员查看建议
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.get(reverse('admin_suggestions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '工作流程测试建议')
        
        # 3. 管理员处理建议
        suggestion = Suggestion.objects.filter(title='工作流程测试建议').first()
        self.assertIsNotNone(suggestion)
        
        response = self.client.post(f'/content/admin/suggestions/{suggestion.id}/update/', {
            'status': 'approved',
            'admin_notes': '建议已批准'
        })
        self.assertEqual(response.status_code, 302)
        
        # 4. 验证建议状态更新
        suggestion.refresh_from_db()
        self.assertEqual(suggestion.status, 'approved')
    
    def test_feedback_rating_integration(self):
        """测试反馈评分集成"""
        self.client.login(username='testuser', password='testpass123')
        
        # 提交多个不同评分的反馈
        ratings = [1, 3, 5]
        for rating in ratings:
            response = self.client.post(reverse('submit_feedback'), {
                'title': f'评分{rating}反馈',
                'content': f'评分{rating}的反馈内容',
                'feedback_type': 'bug',
                'rating': rating
            })
            self.assertEqual(response.status_code, 302)
        
        # 验证所有反馈都已创建
        feedbacks = Feedback.objects.filter(user=self.user)
        self.assertEqual(len(feedbacks), 3)
        
        # 验证评分统计
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        self.assertEqual(avg_rating, 3.0)
    
    def test_announcement_integration(self):
        """测试公告集成"""
        # 管理员创建公告
        self.client.login(username='admin', password='adminpass123')
        
        response = self.client.post(reverse('create_announcement'), {
            'title': '重要公告',
            'content': '这是一个重要公告',
            'priority': 'high',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        
        # 用户查看公告
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('announcements'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '重要公告')
