"""
pytest配置文件
定义测试夹具和配置
"""

import os
from unittest.mock import Mock, patch

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client

# import factory  # 暂时注释掉，因为SQLAlchemy与Python 3.13不兼容
import pytest
from faker import Faker

# 设置Django配置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test_minimal")
django.setup()

User = get_user_model()
fake = Faker("zh_CN")


@pytest.fixture(scope="session")
def django_db_setup():
    """数据库设置"""
    # 使用SQLite数据库进行本地测试
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture
def client():
    """Django测试客户端"""
    return Client()


@pytest.fixture
def user():
    """创建测试用户"""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def admin_user():
    """创建管理员用户"""
    return User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")


@pytest.fixture
def authenticated_client(client, user):
    """已登录的客户端"""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """管理员客户端"""
    client.force_login(admin_user)
    return client


@pytest.fixture
def sample_data():
    """示例数据"""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
        "title": fake.sentence(),
        "content": fake.text(),
        "url": fake.url(),
    }


@pytest.fixture
def mock_external_api():
    """模拟外部API"""
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": {}}
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_redis():
    """模拟Redis"""
    with patch("django_redis.get_redis_connection") as mock_redis:
        mock_connection = Mock()
        mock_redis.return_value = mock_connection
        yield mock_connection


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """为所有测试启用数据库访问"""
    pass


# Pytest配置
def pytest_configure(config):
    """pytest配置"""
    # 禁用迁移以加速测试
    settings.MIGRATION_MODULES = {
        "auth": None,
        "contenttypes": None,
        "sessions": None,
        "users": None,
        "tools": None,
        "content": None,
    }

    # 测试数据库配置
    settings.DATABASES["default"]["NAME"] = ":memory:"

    # 禁用缓存
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }

    # 禁用Celery
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

    # 静态文件设置
    settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

    # 邮件设置
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# 工厂类
# class UserFactory(factory.django.DjangoModelFactory):  # 暂时注释掉，因为SQLAlchemy与Python 3.13不兼容
#     """用户工厂"""
#
#     class Meta:
#         model = User
#
#     username = factory.Sequence(lambda n: f"user{n}")
#     email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
#     first_name = factory.Faker("first_name")
#     last_name = factory.Faker("last_name")
#     is_active = True


# 临时的简单用户工厂替代
class UserFactory:
    """临时的简单用户工厂"""

    @staticmethod
    def create(**kwargs):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_user(**kwargs)


class AdminUserFactory(UserFactory):
    """管理员用户工厂"""

    @staticmethod
    def create(**kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        return UserFactory.create(**kwargs)


# 自定义标记
pytest_plugins = []


def pytest_collection_modifyitems(config, items):
    """自定义测试收集"""
    for item in items:
        # 为慢速测试添加标记
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)

        # 为集成测试添加标记
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.integration)

        # 为API测试添加标记
        if "api" in item.keywords:
            item.add_marker(pytest.mark.api)
