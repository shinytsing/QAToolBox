"""
模型测试模块 - 提高测试覆盖率
"""
import pytest
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import date, timedelta

# 导入需要测试的模型
from apps.tools.models import ToolUsageLog, LifeGoal, VanityWealth, SinPoints
from apps.content.models import Article, Comment
from apps.users.models import UserRole, UserStatus, Profile, UserTheme
from apps.share.models import ShareRecord, ShareLink


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class TestToolUsageLog(TestCase):
    """工具使用日志测试"""
    
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
            tool_name='test_tool',
            action='test_action',
            details={'test': 'data'}
        )
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.tool_name, 'test_tool')
        self.assertEqual(log.action, 'test_action')
        self.assertEqual(log.details, {'test': 'data'})
    
    def test_tool_usage_log_str(self):
        """测试工具使用日志字符串表示"""
        log = ToolUsageLog.objects.create(
            user=self.user,
            tool_name='test_tool',
            action='test_action'
        )
        self.assertIn('test_tool', str(log))
        self.assertIn('test_action', str(log))