import pytest
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import User
from django.core.cache import cache
import factory
from factory.django import DjangoModelFactory


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """设置测试数据库"""
    with django_db_blocker.unblock():
        # 创建测试数据库
        from django.core.management import call_command
        call_command('migrate', verbosity=0)


@pytest.fixture
def db_access_without_rollback_and_truncate(django_db_setup, django_db_blocker):
    """数据库访问，不回滚和截断"""
    django_db_blocker.unblock()
    yield
    django_db_blocker.restore()


@pytest.fixture
def user_factory():
    """用户工厂"""
    class UserFactory(DjangoModelFactory):
        class Meta:
            model = User
        
        username = factory.Sequence(lambda n: f'user{n}')
        email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
        password = factory.PostGenerationMethodCall('set_password', 'password123')
        is_active = True
    
    return UserFactory


@pytest.fixture
def user(user_factory):
    """创建测试用户"""
    return user_factory()


@pytest.fixture
def admin_user(user_factory):
    """创建管理员用户"""
    user = user_factory(username='admin', is_staff=True, is_superuser=True)
    return user


@pytest.fixture
def request_factory():
    """请求工厂"""
    return RequestFactory()


@pytest.fixture
def authenticated_request(request_factory, user):
    """认证请求"""
    request = request_factory.get('/')
    request.user = user
    return request


@pytest.fixture
def api_client():
    """API客户端"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """认证的API客户端"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture(autouse=True)
def clear_cache():
    """自动清理缓存"""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_redis(mocker):
    """模拟Redis"""
    mock_redis = mocker.patch('django.core.cache.cache')
    return mock_redis


@pytest.fixture
def mock_celery(mocker):
    """模拟Celery"""
    mock_celery = mocker.patch('celery.app.task.Task.delay')
    return mock_celery


@pytest.fixture
def mock_requests(mocker):
    """模拟HTTP请求"""
    mock_requests = mocker.patch('requests.get')
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {}
    return mock_requests


# 标记定义
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "database: marks tests as database tests"
    )
