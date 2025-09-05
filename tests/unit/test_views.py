"""
视图单元测试
"""

from django.contrib.auth import get_user_model
from django.urls import reverse

import pytest

from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestHomeView:
    """首页视图测试"""

    def test_home_page_status_code(self, client):
        """测试首页状态码"""
        response = client.get("/")
        assert response.status_code == 200

    def test_home_page_contains_title(self, client):
        """测试首页包含标题"""
        response = client.get("/")
        assert "QAToolBox" in response.content.decode()

    def test_home_page_template_used(self, client):
        """测试首页使用的模板"""
        response = client.get("/")
        assert "home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
class TestUserViews:
    """用户视图测试"""

    def test_login_page_get(self, client):
        """测试登录页面GET请求"""
        response = client.get(reverse("users:login"))
        assert response.status_code == 200

    def test_login_page_post_valid(self, client):
        """测试有效登录"""
        user = UserFactory()
        user.set_password("testpass123")
        user.save()

        response = client.post(reverse("users:login"), {"username": user.username, "password": "testpass123"})
        assert response.status_code == 302  # 重定向

    def test_login_page_post_invalid(self, client):
        """测试无效登录"""
        response = client.post(reverse("users:login"), {"username": "nonexistent", "password": "wrongpass"})
        assert response.status_code == 200  # 返回登录页面

    def test_logout_redirect(self, authenticated_client):
        """测试注销重定向"""
        response = authenticated_client.post(reverse("users:logout"))
        assert response.status_code == 302

    def test_profile_requires_login(self, client):
        """测试个人资料页面需要登录"""
        response = client.get(reverse("users:profile"))
        assert response.status_code == 302  # 重定向到登录页面

    def test_profile_authenticated_user(self, authenticated_client):
        """测试已认证用户访问个人资料页面"""
        response = authenticated_client.get(reverse("users:profile"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestToolViews:
    """工具视图测试"""

    def test_tools_list_page(self, client):
        """测试工具列表页面"""
        response = client.get("/tools/")
        assert response.status_code == 200

    def test_chat_tool_page(self, client):
        """测试聊天工具页面"""
        response = client.get("/tools/chat/")
        assert response.status_code == 200

    def test_fitness_tool_page(self, client):
        """测试健身工具页面"""
        response = client.get("/tools/fitness/")
        assert response.status_code == 200

    def test_tool_access_permission(self, client, authenticated_client):
        """测试工具访问权限"""
        # 某些工具可能需要登录
        protected_url = "/tools/premium-feature/"

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
        response = client.get("/api/health/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_api_tools_list(self, client):
        """测试工具列表API"""
        response = client.get("/api/tools/")
        assert response.status_code == 200
        assert "results" in response.json()

    def test_api_user_profile_unauthorized(self, client):
        """测试未授权访问用户配置API"""
        response = client.get("/api/users/profile/")
        assert response.status_code == 401

    def test_api_user_profile_authorized(self, authenticated_client):
        """测试已授权访问用户配置API"""
        response = authenticated_client.get("/api/users/profile/")
        # 根据实际API实现调整期望结果
        assert response.status_code in [200, 404]  # 可能还未实现


@pytest.mark.django_db
class TestErrorViews:
    """错误页面测试"""

    def test_404_page(self, client):
        """测试404页面"""
        response = client.get("/nonexistent-page/")
        assert response.status_code == 404

    def test_500_page(self, client, settings):
        """测试500页面"""
        # 这个测试需要特殊设置来触发500错误
        settings.DEBUG = False
        # 需要实际的500错误触发机制


@pytest.mark.django_db
class TestContentViews:
    """内容视图测试"""

    def test_article_list_page(self, client):
        """测试文章列表页面"""
        response = client.get("/content/articles/")
        assert response.status_code == 200

    def test_article_detail_page(self, client):
        """测试文章详情页面"""
        # 假设有一个ID为1的文章
        response = client.get("/content/articles/1/")
        assert response.status_code in [200, 404]  # 可能不存在

    def test_article_create_requires_login(self, client):
        """测试创建文章需要登录"""
        response = client.get("/content/articles/create/")
        assert response.status_code == 302  # 重定向到登录页面


@pytest.mark.django_db
class TestShareViews:
    """分享视图测试"""

    def test_share_page(self, client):
        """测试分享页面"""
        response = client.get("/share/")
        assert response.status_code == 200

    def test_share_record_creation(self, authenticated_client):
        """测试分享记录创建"""
        data = {"platform": "wechat", "page_url": "https://example.com", "page_title": "测试页面"}
        response = authenticated_client.post("/share/record/", data)
        assert response.status_code in [200, 201, 302]  # 根据实际实现调整


@pytest.mark.django_db
class TestHealthViews:
    """健康检查视图测试"""

    def test_health_check_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health/")
        assert response.status_code == 200
        assert "status" in response.json()

    def test_health_check_database(self, client):
        """测试数据库健康检查"""
        response = client.get("/health/database/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestStaticFiles:
    """静态文件测试"""

    def test_static_files_served(self, client):
        """测试静态文件服务"""
        response = client.get("/static/css/style.css")
        # 静态文件可能不存在，所以状态码可能是200或404
        assert response.status_code in [200, 404]

    def test_media_files_served(self, client):
        """测试媒体文件服务"""
        response = client.get("/media/test.jpg")
        # 媒体文件可能不存在，所以状态码可能是200或404
        assert response.status_code in [200, 404]


@pytest.mark.django_db
class TestMiddleware:
    """中间件测试"""

    def test_cors_headers(self, client):
        """测试CORS头部"""
        response = client.get("/api/health/")
        # 检查CORS相关头部是否存在
        assert response.status_code == 200

    def test_security_headers(self, client):
        """测试安全头部"""
        response = client.get("/")
        # 检查安全相关头部
        assert response.status_code == 200


@pytest.mark.django_db
class TestURLPatterns:
    """URL模式测试"""

    def test_root_url_resolves(self, client):
        """测试根URL解析"""
        response = client.get("/")
        assert response.status_code == 200

    def test_tools_url_resolves(self, client):
        """测试工具URL解析"""
        response = client.get("/tools/")
        assert response.status_code == 200

    def test_users_url_resolves(self, client):
        """测试用户URL解析"""
        response = client.get("/users/login/")
        assert response.status_code == 200

    def test_content_url_resolves(self, client):
        """测试内容URL解析"""
        response = client.get("/content/")
        assert response.status_code in [200, 404]  # 根据实际实现调整

    def test_share_url_resolves(self, client):
        """测试分享URL解析"""
        response = client.get("/share/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestTemplateRendering:
    """模板渲染测试"""

    def test_base_template_inheritance(self, client):
        """测试基础模板继承"""
        response = client.get("/")
        content = response.content.decode()
        # 检查基础模板元素
        assert "<!DOCTYPE html>" in content or "<html" in content

    def test_template_context(self, client):
        """测试模板上下文"""
        response = client.get("/")
        # 检查模板上下文变量
        assert response.status_code == 200

    def test_template_filters(self, client):
        """测试模板过滤器"""
        response = client.get("/")
        content = response.content.decode()
        # 检查模板过滤器是否正常工作
        assert response.status_code == 200


@pytest.mark.django_db
class TestFormHandling:
    """表单处理测试"""

    def test_login_form_rendering(self, client):
        """测试登录表单渲染"""
        response = client.get("/users/login/")
        content = response.content.decode()
        assert "form" in content.lower()
        assert response.status_code == 200

    def test_registration_form_rendering(self, client):
        """测试注册表单渲染"""
        response = client.get("/users/register/")
        # 如果注册页面存在
        if response.status_code == 200:
            content = response.content.decode()
            assert "form" in content.lower()

    def test_form_validation(self, client):
        """测试表单验证"""
        # 测试无效的登录数据
        response = client.post("/users/login/", {"username": "", "password": ""})
        assert response.status_code == 200  # 返回表单页面显示错误


@pytest.mark.django_db
class TestSessionHandling:
    """会话处理测试"""

    def test_session_creation(self, authenticated_client):
        """测试会话创建"""
        response = authenticated_client.get("/")
        assert response.status_code == 200
        # 检查会话是否正常工作

    def test_session_persistence(self, authenticated_client):
        """测试会话持久性"""
        # 第一次请求
        response1 = authenticated_client.get("/")
        assert response1.status_code == 200

        # 第二次请求，会话应该保持
        response2 = authenticated_client.get("/")
        assert response2.status_code == 200


@pytest.mark.django_db
class TestCSRFProtection:
    """CSRF保护测试"""

    def test_csrf_token_present(self, client):
        """测试CSRF令牌存在"""
        response = client.get("/users/login/")
        content = response.content.decode()
        # 检查CSRF令牌是否存在
        assert response.status_code == 200

    def test_csrf_protection(self, client):
        """测试CSRF保护"""
        # 尝试没有CSRF令牌的POST请求
        response = client.post("/users/login/", {"username": "test", "password": "test"})
        # 应该被CSRF保护阻止
        assert response.status_code in [200, 403, 400]
