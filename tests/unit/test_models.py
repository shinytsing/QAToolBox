"""
模型单元测试
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from tests.conftest import UserFactory

User = get_user_model()


class TestUserModel:
    """用户模型测试"""
    
    def test_create_user(self):
        """测试创建用户"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
    
    def test_create_superuser(self):
        """测试创建超级用户"""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        assert admin.is_staff
        assert admin.is_superuser
        assert admin.is_active
    
    def test_user_str_representation(self):
        """测试用户字符串表示"""
        user = UserFactory(username='testuser')
        assert str(user) == 'testuser'
    
    def test_duplicate_username(self):
        """测试重复用户名"""
        UserFactory(username='duplicate')
        
        with pytest.raises(IntegrityError):
            UserFactory(username='duplicate')
    
    def test_email_validation(self):
        """测试邮箱验证"""
        with pytest.raises(ValidationError):
            user = User(username='test', email='invalid-email')
            user.full_clean()


@pytest.mark.django_db
class TestToolModel:
    """工具模型测试（假设存在工具模型）"""
    
    def test_tool_creation(self):
        """测试工具创建"""
        # 这里需要根据实际的工具模型来编写测试
        # 目前作为示例
        pass
    
    def test_tool_validation(self):
        """测试工具验证"""
        # 工具字段验证测试
        pass
