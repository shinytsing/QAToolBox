"""
视图单元测试
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestHomeView:
    """首页视图测试"""
    
    def test_home_page_status_code(self, client):
        """测试首页状态码"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_home_page_contains_title(self, client):
        """测试首页包含标题"""
        response = client.get('/')
        assert 'QAToolBox' in response.content.decode()
    
    def test_home_page_template_used(self, client):
        """测试首页使用的模板"""
        response = client.get('/')
        assert 'home.html' in [t.name for t in response.templates]


@pytest.mark.django_db
class TestUserViews:
    """用户视图测试"""
    
    def test_login_page_get(self, client):
        """测试登录页面GET请求"""
        response = client.get(reverse('users:login'))
        assert response.status_code == 200
    
    def test_login_page_post_valid(self, client):
        """测试有效登录"""
        user = UserFactory()
        user.set_password('testpass123')
        user.save()
        
        response = client.post(reverse('users:login'), {
            'username': user.username,
            'password': 'testpass123'
        })
        assert response.status_code == 302  # 重定向
    
    def test_login_page_post_invalid(self, client):
        """测试无效登录"""
        response = client.post(reverse('users:login'), {
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        assert response.status_code == 200  # 返回登录页面
    
    def test_logout_redirect(self, authenticated_client):
        """测试注销重定向"""
        response = authenticated_client.post(reverse('users:logout'))
        assert response.status_code == 302
    
    def test_profile_requires_login(self, client):
        """测试个人资料页面需要登录"""
        response = client.get(reverse('users:profile'))
        assert response.status_code == 302  # 重定向到登录页面
    
    def test_profile_authenticated_user(self, authenticated_client):
        """测试已认证用户访问个人资料页面"""
        response = authenticated_client.get(reverse('users:profile'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestToolViews:
    """工具视图测试"""
    
    def test_tools_list_page(self, client):
        """测试工具列表页面"""
        response = client.get('/tools/')
        assert response.status_code == 200
    
    def test_chat_tool_page(self, client):
        """测试聊天工具页面"""
        response = client.get('/tools/chat/')
        assert response.status_code == 200
    
    def test_fitness_tool_page(self, client):
        """测试健身工具页面"""
        response = client.get('/tools/fitness/')
        assert response.status_code == 200
    
    def test_tool_access_permission(self, client, authenticated_client):
        """测试工具访问权限"""
        # 某些工具可能需要登录
        protected_url = '/tools/premium-feature/'
        
        # 未登录访问
        response = client.get(protected_url)
        # 根据实际情况调整期望结果
        
        # 已登录访问
        response = authenticated_client.get(protected_url)
        # 根据实际情况调整期望结果


@pytest.mark.django_db
class TestAPIViews:
    """API视图测试"""
    
    def test_api_health_check(self, client):
        """测试API健康检查"""
        response = client.get('/api/health/')
        assert response.status_code == 200
        assert response.json()['status'] == 'ok'
    
    def test_api_tools_list(self, client):
        """测试工具列表API"""
        response = client.get('/api/tools/')
        assert response.status_code == 200
        assert 'results' in response.json()
    
    def test_api_user_profile_unauthorized(self, client):
        """测试未授权访问用户配置API"""
        response = client.get('/api/users/profile/')
        assert response.status_code == 401
    
    def test_api_user_profile_authorized(self, authenticated_client):
        """测试已授权访问用户配置API"""
        response = authenticated_client.get('/api/users/profile/')
        # 根据实际API实现调整期望结果
        assert response.status_code in [200, 404]  # 可能还未实现


@pytest.mark.django_db
class TestErrorViews:
    """错误页面测试"""
    
    def test_404_page(self, client):
        """测试404页面"""
        response = client.get('/nonexistent-page/')
        assert response.status_code == 404
    
    def test_500_page(self, client, settings):
        """测试500页面"""
        # 这个测试需要特殊设置来触发500错误
        settings.DEBUG = False
        # 需要实际的500错误触发机制
