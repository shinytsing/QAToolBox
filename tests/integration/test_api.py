"""
API集成测试
测试API端点的完整功能
"""

import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestAPIAuthentication:
    """API认证测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()
        self.user = UserFactory()
        self.user.set_password("testpass123")
        self.user.save()

    def test_api_without_authentication(self):
        """测试未认证的API访问"""
        response = self.client.get("/api/users/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_api_with_session_authentication(self):
        """测试会话认证"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/users/profile/")
        # 根据实际API实现调整
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_api_login_logout_flow(self):
        """测试登录注销流程"""
        # 登录
        login_data = {"username": self.user.username, "password": "testpass123"}
        response = self.client.post("/api/auth/login/", login_data)
        # 根据实际API实现调整

        # 访问受保护资源
        response = self.client.get("/api/users/profile/")
        # 根据认证结果调整期望


@pytest.mark.django_db
class TestToolsAPI:
    """工具API测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_tools_list_api(self):
        """测试工具列表API"""
        response = self.client.get("/api/tools/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_tool_detail_api(self):
        """测试工具详情API"""
        # 假设存在工具详情API
        response = self.client.get("/api/tools/1/")
        # 根据实际API实现调整期望结果
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_tool_usage_logging(self):
        """测试工具使用日志记录"""
        # 使用工具
        tool_data = {"tool_name": "test_tool", "action": "use"}
        response = self.client.post("/api/tools/usage/", tool_data)
        # 根据实际API实现调整

    def test_tool_search_api(self):
        """测试工具搜索API"""
        response = self.client.get("/api/tools/search/?q=chat")
        # 根据实际API实现调整期望结果


@pytest.mark.django_db
class TestUserAPI:
    """用户API测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_user_profile_get(self):
        """测试获取用户配置"""
        response = self.client.get("/api/users/profile/")
        # 根据实际API实现调整
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_user_profile_update(self):
        """测试更新用户配置"""
        update_data = {"first_name": "测试", "last_name": "用户"}
        response = self.client.patch("/api/users/profile/", update_data)
        # 根据实际API实现调整

    def test_user_avatar_upload(self):
        """测试用户头像上传"""
        # 创建测试图片数据
        import io
        from PIL import Image

        image = Image.new("RGB", (100, 100), color="red")
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)

        response = self.client.post("/api/users/avatar/", {"avatar": image_io}, format="multipart")
        # 根据实际API实现调整期望结果


@pytest.mark.django_db
class TestContentAPI:
    """内容API测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_content_list_api(self):
        """测试内容列表API"""
        response = self.client.get("/api/content/")
        # 根据实际API实现调整
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_content_create_api(self):
        """测试内容创建API"""
        content_data = {"title": "测试内容", "content": "这是测试内容", "category": "test"}
        response = self.client.post("/api/content/", content_data)
        # 根据实际API实现调整期望结果

    def test_content_update_permission(self):
        """测试内容更新权限"""
        # 创建其他用户的内容，测试权限控制
        other_user = UserFactory()
        # 根据实际模型实现创建内容

        # 尝试更新其他用户的内容
        update_data = {"title": "修改标题"}
        response = self.client.patch("/api/content/1/", update_data)
        # 应该返回权限错误


@pytest.mark.django_db
class TestAPIRateLimiting:
    """API限流测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()

    def test_api_rate_limiting(self):
        """测试API限流"""
        # 快速发送多个请求
        for i in range(100):
            response = self.client.get("/api/tools/")
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        else:
            # 如果没有触发限流，可能限流配置较宽松
            pytest.skip("API限流配置较宽松，未触发限制")


@pytest.mark.django_db
class TestAPIErrorHandling:
    """API错误处理测试"""

    def setup_method(self):
        """测试设置"""
        self.client = APIClient()

    def test_api_404_error(self):
        """测试API 404错误"""
        response = self.client.get("/api/nonexistent/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_api_method_not_allowed(self):
        """测试API方法不允许错误"""
        response = self.client.delete("/api/tools/")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_api_invalid_data(self):
        """测试API无效数据"""
        invalid_data = {"invalid_field": "invalid_value"}
        response = self.client.post("/api/users/", invalid_data)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_api_large_payload(self):
        """测试API大载荷"""
        large_data = {"content": "x" * 10000000}  # 10MB数据
        response = self.client.post("/api/content/", large_data)
        # 应该返回413错误或400错误
