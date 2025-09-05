"""
模型测试模块 - 提高测试覆盖率
"""
import pytest
from django.test import TestCase
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


@pytest.mark.django_db
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
    
    def test_tool_usage_log_defaults(self):
        """测试工具使用日志默认值"""
        log = ToolUsageLog.objects.create(
            user=self.user,
            tool_name='default_tool',
            action='default_action'
        )
        self.assertIsNotNone(log.created_at)
        self.assertIsNone(log.details)
    
    def test_tool_usage_log_ordering(self):
        """测试工具使用日志排序"""
        log1 = ToolUsageLog.objects.create(
            user=self.user,
            tool_name='tool1',
            action='action1'
        )
        log2 = ToolUsageLog.objects.create(
            user=self.user,
            tool_name='tool2',
            action='action2'
        )
        logs = list(ToolUsageLog.objects.all())
        self.assertEqual(len(logs), 2)
        self.assertIn(log1, logs)
        self.assertIn(log2, logs)


@pytest.mark.django_db
class TestLifeGoal(TestCase):
    """生活目标模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_life_goal_creation(self):
        """测试生活目标创建"""
        goal = LifeGoal.objects.create(
            user=self.user,
            title='测试目标',
            description='这是一个测试目标',
            goal_type='career',
            priority='high',
            status='in_progress',
            target_date=date.today() + timedelta(days=30),
            progress=50,
            tags=['测试', '目标'],
            is_public=True
        )
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.title, '测试目标')
        self.assertEqual(goal.goal_type, 'career')
        self.assertEqual(goal.priority, 'high')
        self.assertEqual(goal.status, 'in_progress')
        self.assertEqual(goal.progress, 50)
        self.assertTrue(goal.is_public)
    
    def test_life_goal_defaults(self):
        """测试生活目标默认值"""
        goal = LifeGoal.objects.create(
            user=self.user,
            title='默认目标',
            description='默认描述',
            goal_type='personal'
        )
        self.assertEqual(goal.priority, 'medium')
        self.assertEqual(goal.status, 'not_started')
        self.assertEqual(goal.progress, 0)
        self.assertFalse(goal.is_public)
        self.assertEqual(goal.tags, [])
    
    def test_life_goal_str(self):
        """测试生活目标字符串表示"""
        goal = LifeGoal.objects.create(
            user=self.user,
            title='测试目标',
            description='测试描述',
            goal_type='health'
        )
        self.assertEqual(str(goal), '测试目标')
    
    def test_life_goal_choices(self):
        """测试生活目标选择字段"""
        # 测试目标类型选择
        goal = LifeGoal.objects.create(
            user=self.user,
            title='职业目标',
            description='职业发展',
            goal_type='career'
        )
        self.assertEqual(goal.get_goal_type_display(), '职业发展')
        
        # 测试优先级选择
        goal.priority = 'urgent'
        self.assertEqual(goal.get_priority_display(), '紧急')
        
        # 测试状态选择
        goal.status = 'completed'
        self.assertEqual(goal.get_status_display(), '已完成')


@pytest.mark.django_db
class TestVanityWealth(TestCase):
    """虚荣财富模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_vanity_wealth_creation(self):
        """测试虚荣财富创建"""
        wealth = VanityWealth.objects.create(
            user=self.user,
            virtual_wealth=1000,
            wealth_type='gold'
        )
        self.assertEqual(wealth.user, self.user)
        self.assertEqual(wealth.virtual_wealth, 1000)
        self.assertEqual(wealth.wealth_type, 'gold')
    
    def test_vanity_wealth_str(self):
        """测试虚荣财富字符串表示"""
        wealth = VanityWealth.objects.create(
            user=self.user,
            virtual_wealth=500,
            wealth_type='silver'
        )
        self.assertEqual(str(wealth), '500')
    
    def test_vanity_wealth_defaults(self):
        """测试虚荣财富默认值"""
        wealth = VanityWealth.objects.create(
            user=self.user,
            virtual_wealth=100
        )
        self.assertEqual(wealth.wealth_type, 'gold')
        self.assertIsNotNone(wealth.created_at)


@pytest.mark.django_db
class TestSinPoints(TestCase):
    """罪恶点数模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_sin_points_creation(self):
        """测试罪恶点数创建"""
        sin = SinPoints.objects.create(
            user=self.user,
            points=100,
            sin_type='laziness',
            description='测试罪恶'
        )
        self.assertEqual(sin.user, self.user)
        self.assertEqual(sin.points, 100)
        self.assertEqual(sin.sin_type, 'laziness')
        self.assertEqual(sin.description, '测试罪恶')
    
    def test_sin_points_defaults(self):
        """测试罪恶点数默认值"""
        sin = SinPoints.objects.create(
            user=self.user,
            points=50
        )
        self.assertEqual(sin.sin_type, 'general')
        self.assertEqual(sin.description, '')
    
    def test_sin_points_str(self):
        """测试罪恶点数字符串表示"""
        sin = SinPoints.objects.create(
            user=self.user,
            points=75,
            sin_type='greed'
        )
        self.assertIn('75', str(sin))
        self.assertIn('greed', str(sin))


@pytest.mark.django_db
class TestArticle(TestCase):
    """文章模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_article_creation(self):
        """测试文章创建"""
        article = Article.objects.create(
            title='测试文章',
            content='这是测试内容',
            author=self.user,
            is_published=True
        )
        self.assertEqual(article.title, '测试文章')
        self.assertEqual(article.content, '这是测试内容')
        self.assertEqual(article.author, self.user)
        self.assertTrue(article.is_published)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)
    
    def test_article_defaults(self):
        """测试文章默认值"""
        article = Article.objects.create(
            title='默认文章',
            content='默认内容',
            author=self.user
        )
        self.assertFalse(article.is_published)
    
    def test_article_str(self):
        """测试文章字符串表示"""
        article = Article.objects.create(
            title='测试标题',
            content='测试内容',
            author=self.user
        )
        self.assertEqual(str(article), '测试标题')
    
    def test_article_meta(self):
        """测试文章元数据"""
        article = Article.objects.create(
            title='测试文章',
            content='测试内容',
            author=self.user
        )
        self.assertEqual(article._meta.verbose_name, '文章')
        self.assertEqual(article._meta.verbose_name_plural, '文章')


@pytest.mark.django_db
class TestComment(TestCase):
    """评论模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.article = Article.objects.create(
            title='测试文章',
            content='测试内容',
            author=self.user
        )
    
    def test_comment_creation(self):
        """测试评论创建"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='这是测试评论'
        )
        self.assertEqual(comment.article, self.article)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, '这是测试评论')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_str(self):
        """测试评论字符串表示"""
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='测试评论'
        )
        self.assertIn('测试评论', str(comment))


@pytest.mark.django_db
class TestUserRole(TestCase):
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
            role='admin'
        )
        self.assertEqual(role.user, self.user)
        self.assertEqual(role.role, 'admin')
        self.assertTrue(role.is_admin())
    
    def test_user_role_str(self):
        """测试用户角色字符串表示"""
        role = UserRole.objects.create(
            user=self.user,
            role='user'
        )
        self.assertIn('testuser', str(role))
        self.assertIn('user', str(role))
    
    def test_user_role_is_admin(self):
        """测试用户角色管理员检查"""
        admin_role = UserRole.objects.create(
            user=self.user,
            role='admin'
        )
        self.assertTrue(admin_role.is_admin())
        
        user_role = UserRole.objects.create(
            user=self.user,
            role='user'
        )
        self.assertFalse(user_role.is_admin())


@pytest.mark.django_db
class TestUserStatus(TestCase):
    """用户状态模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_status_creation(self):
        """测试用户状态创建"""
        status = UserStatus.objects.create(
            user=self.user,
            status='active',
            last_login=timezone.now()
        )
        self.assertEqual(status.user, self.user)
        self.assertEqual(status.status, 'active')
        self.assertIsNotNone(status.last_login)
    
    def test_user_status_str(self):
        """测试用户状态字符串表示"""
        status = UserStatus.objects.create(
            user=self.user,
            status='inactive'
        )
        self.assertIn('testuser', str(status))
        self.assertIn('inactive', str(status))


@pytest.mark.django_db
class TestProfile(TestCase):
    """用户档案模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """测试用户档案创建"""
        profile = Profile.objects.create(
            user=self.user,
            bio='测试个人简介',
            location='测试地点'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, '测试个人简介')
        self.assertEqual(profile.location, '测试地点')
    
    def test_profile_str(self):
        """测试用户档案字符串表示"""
        profile = Profile.objects.create(
            user=self.user,
            bio='测试简介'
        )
        self.assertIn('testuser', str(profile))


@pytest.mark.django_db
class TestUserTheme(TestCase):
    """用户主题模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_theme_creation(self):
        """测试用户主题创建"""
        theme = UserTheme.objects.create(
            user=self.user,
            theme_name='dark',
            is_active=True
        )
        self.assertEqual(theme.user, self.user)
        self.assertEqual(theme.theme_name, 'dark')
        self.assertTrue(theme.is_active)
    
    def test_user_theme_str(self):
        """测试用户主题字符串表示"""
        theme = UserTheme.objects.create(
            user=self.user,
            theme_name='light'
        )
        self.assertIn('testuser', str(theme))
        self.assertIn('light', str(theme))


@pytest.mark.django_db
class TestShareRecord(TestCase):
    """分享记录模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_share_record_creation(self):
        """测试分享记录创建"""
        record = ShareRecord.objects.create(
            user=self.user,
            platform='wechat',
            page_url='https://example.com',
            page_title='测试页面'
        )
        self.assertEqual(record.user, self.user)
        self.assertEqual(record.platform, 'wechat')
        self.assertEqual(record.page_url, 'https://example.com')
        self.assertEqual(record.page_title, '测试页面')
    
    def test_share_record_str(self):
        """测试分享记录字符串表示"""
        record = ShareRecord.objects.create(
            user=self.user,
            platform='weibo',
            page_url='https://test.com',
            page_title='测试标题'
        )
        self.assertIn('testuser', str(record))
        self.assertIn('weibo', str(record))
        self.assertIn('测试标题', str(record))


@pytest.mark.django_db
class TestShareLink(TestCase):
    """分享链接模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_share_link_creation(self):
        """测试分享链接创建"""
        link = ShareLink.objects.create(
            user=self.user,
            original_url='https://example.com',
            short_code='abc123',
            title='测试链接'
        )
        self.assertEqual(link.user, self.user)
        self.assertEqual(link.original_url, 'https://example.com')
        self.assertEqual(link.short_code, 'abc123')
        self.assertEqual(link.title, '测试链接')
    
    def test_share_link_str(self):
        """测试分享链接字符串表示"""
        link = ShareLink.objects.create(
            user=self.user,
            original_url='https://test.com',
            short_code='xyz789',
            title='测试标题'
        )
        self.assertIn('testuser', str(link))
        self.assertIn('xyz789', str(link))
        self.assertIn('测试标题', str(link))