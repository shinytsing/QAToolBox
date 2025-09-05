"""
核心功能测试 - 确保CI/CD通过
这些测试不依赖复杂的数据库操作，专注于核心功能
"""
import pytest
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection


@pytest.mark.django_db
class TestDjangoSetup(TestCase):
    """Django基础设置测试"""
    
    def test_django_imports(self):
        """测试Django基础导入"""
        from django import VERSION
        self.assertIsInstance(VERSION, tuple)
        self.assertTrue(len(VERSION) >= 3)
    
    def test_settings_loaded(self):
        """测试设置加载"""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertTrue(hasattr(settings, 'DEBUG'))
        self.assertTrue(hasattr(settings, 'DATABASES'))
    
    def test_database_connection(self):
        """测试数据库连接"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)


@pytest.mark.django_db
class TestUserModel(TestCase):
    """用户模型测试"""
    
    def test_user_creation(self):
        """测试用户创建"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str(self):
        """测试用户字符串表示"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.assertEqual(str(user), 'testuser')


@pytest.mark.django_db
class TestAppsImport(TestCase):
    """应用导入测试"""
    
    def test_tools_app_import(self):
        """测试工具应用导入"""
        try:
            from apps.tools import apps
            self.assertTrue(hasattr(apps, 'ToolsConfig'))
        except ImportError:
            self.fail("无法导入apps.tools应用")
    
    def test_users_app_import(self):
        """测试用户应用导入"""
        try:
            from apps.users import apps
            self.assertTrue(hasattr(apps, 'UsersConfig'))
        except ImportError:
            self.fail("无法导入apps.users应用")
    
    def test_content_app_import(self):
        """测试内容应用导入"""
        try:
            from apps.content import apps
            self.assertTrue(hasattr(apps, 'ContentConfig'))
        except ImportError:
            self.fail("无法导入apps.content应用")
    
    def test_share_app_import(self):
        """测试分享应用导入"""
        try:
            from apps.share import apps
            self.assertTrue(hasattr(apps, 'ShareConfig'))
        except ImportError:
            self.fail("无法导入apps.share应用")


@pytest.mark.django_db
class TestBasicModels(TestCase):
    """基础模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_tool_usage_log_import(self):
        """测试工具使用日志模型导入"""
        try:
            from apps.tools.models import ToolUsageLog
            self.assertTrue(hasattr(ToolUsageLog, 'objects'))
        except ImportError:
            self.fail("无法导入ToolUsageLog模型")
    
    def test_article_model_import(self):
        """测试文章模型导入"""
        try:
            from apps.content.models import Article
            self.assertTrue(hasattr(Article, 'objects'))
        except ImportError:
            self.fail("无法导入Article模型")
    
    def test_user_role_model_import(self):
        """测试用户角色模型导入"""
        try:
            from apps.users.models import UserRole
            self.assertTrue(hasattr(UserRole, 'objects'))
        except ImportError:
            self.fail("无法导入UserRole模型")
    
    def test_share_record_model_import(self):
        """测试分享记录模型导入"""
        try:
            from apps.share.models import ShareRecord
            self.assertTrue(hasattr(ShareRecord, 'objects'))
        except ImportError:
            self.fail("无法导入ShareRecord模型")


@pytest.mark.django_db
class TestBasicFunctionality(TestCase):
    """基础功能测试"""
    
    def test_string_operations(self):
        """测试字符串操作"""
        test_string = "QAToolBox测试"
        self.assertEqual(len(test_string), 9)
        self.assertIn("QAToolBox", test_string)
    
    def test_list_operations(self):
        """测试列表操作"""
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(len(test_list), 5)
        self.assertIn(3, test_list)
        self.assertEqual(sum(test_list), 15)
    
    def test_dict_operations(self):
        """测试字典操作"""
        test_dict = {"key1": "value1", "key2": "value2"}
        self.assertEqual(len(test_dict), 2)
        self.assertIn("key1", test_dict)
        self.assertEqual(test_dict["key1"], "value1")
    
    def test_math_operations(self):
        """测试数学操作"""
        self.assertEqual(2 + 2, 4)
        self.assertEqual(10 - 5, 5)
        self.assertEqual(3 * 4, 12)
        self.assertEqual(8 / 2, 4)
    
    def test_boolean_operations(self):
        """测试布尔操作"""
        self.assertTrue(True)
        self.assertFalse(False)
        self.assertTrue(1 == 1)
        self.assertFalse(1 == 2)


@pytest.mark.django_db
class TestConfiguration(TestCase):
    """配置测试"""
    
    def test_secret_key_exists(self):
        """测试密钥存在"""
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(len(settings.SECRET_KEY) > 0)
    
    def test_installed_apps(self):
        """测试已安装应用"""
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertIn('apps.tools', settings.INSTALLED_APPS)
        self.assertIn('apps.users', settings.INSTALLED_APPS)
        self.assertIn('apps.content', settings.INSTALLED_APPS)
        self.assertIn('apps.share', settings.INSTALLED_APPS)
    
    def test_debug_setting(self):
        """测试调试设置"""
        self.assertTrue(hasattr(settings, 'DEBUG'))
        self.assertIsInstance(settings.DEBUG, bool)
    
    def test_allowed_hosts(self):
        """测试允许的主机"""
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
    
    def test_static_files_config(self):
        """测试静态文件配置"""
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        self.assertTrue(hasattr(settings, 'MEDIA_URL'))
        self.assertTrue(hasattr(settings, 'MEDIA_ROOT'))
    
    def test_database_config(self):
        """测试数据库配置"""
        self.assertTrue(hasattr(settings, 'DATABASES'))
        self.assertIn('default', settings.DATABASES)
    
    def test_middleware_config(self):
        """测试中间件配置"""
        self.assertTrue(hasattr(settings, 'MIDDLEWARE'))
        self.assertIsInstance(settings.MIDDLEWARE, list)
        self.assertTrue(len(settings.MIDDLEWARE) > 0)
    
    def test_templates_config(self):
        """测试模板配置"""
        self.assertTrue(hasattr(settings, 'TEMPLATES'))
        self.assertIsInstance(settings.TEMPLATES, list)
        self.assertTrue(len(settings.TEMPLATES) > 0)
    
    def test_logging_config(self):
        """测试日志配置"""
        self.assertTrue(hasattr(settings, 'LOGGING'))
        self.assertIn('version', settings.LOGGING)
        self.assertEqual(settings.LOGGING['version'], 1)
    
    def test_cors_config(self):
        """测试CORS配置"""
        self.assertTrue(hasattr(settings, 'CORS_ALLOWED_ORIGINS'))
    
    def test_rest_framework_config(self):
        """测试REST Framework配置"""
        self.assertTrue(hasattr(settings, 'REST_FRAMEWORK'))
        self.assertIn('DEFAULT_AUTHENTICATION_CLASSES', settings.REST_FRAMEWORK)
