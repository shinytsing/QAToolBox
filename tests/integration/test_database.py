"""
数据库集成测试
测试数据库操作和数据一致性
"""

import pytest
from django.db import transaction, IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from tests.conftest import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestDatabaseOperations:
    """数据库操作测试"""
    
    def test_user_creation_and_retrieval(self):
        """测试用户创建和检索"""
        # 创建用户
        user = UserFactory(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpass123')
        user.save()
        
        # 检索用户
        retrieved_user = User.objects.get(username='testuser')
        assert retrieved_user.email == 'test@example.com'
        assert retrieved_user.check_password('testpass123')
    
    def test_user_update_operations(self):
        """测试用户更新操作"""
        user = UserFactory()
        original_username = user.username
        
        # 更新用户信息
        user.first_name = '张三'
        user.last_name = '李四'
        user.save()
        
        # 验证更新
        updated_user = User.objects.get(username=original_username)
        assert updated_user.first_name == '张三'
        assert updated_user.last_name == '李四'
    
    def test_user_deletion(self):
        """测试用户删除"""
        user = UserFactory()
        user_id = user.id
        
        # 删除用户
        user.delete()
        
        # 验证删除
        with pytest.raises(User.DoesNotExist):
            User.objects.get(id=user_id)
    
    def test_bulk_operations(self):
        """测试批量操作"""
        # 批量创建
        users = [UserFactory() for _ in range(10)]
        
        # 批量更新
        User.objects.filter(
            id__in=[u.id for u in users]
        ).update(is_active=False)
        
        # 验证批量更新
        inactive_count = User.objects.filter(
            id__in=[u.id for u in users],
            is_active=False
        ).count()
        assert inactive_count == 10
        
        # 批量删除
        User.objects.filter(
            id__in=[u.id for u in users]
        ).delete()
        
        # 验证批量删除
        remaining_count = User.objects.filter(
            id__in=[u.id for u in users]
        ).count()
        assert remaining_count == 0


@pytest.mark.django_db
class TestDatabaseTransactions:
    """数据库事务测试"""
    
    def test_transaction_rollback(self):
        """测试事务回滚"""
        initial_count = User.objects.count()
        
        try:
            with transaction.atomic():
                # 创建一个用户
                UserFactory()
                
                # 故意引发错误
                raise Exception("测试异常")
        except Exception:
            pass
        
        # 验证事务回滚
        final_count = User.objects.count()
        assert final_count == initial_count
    
    def test_transaction_commit(self):
        """测试事务提交"""
        initial_count = User.objects.count()
        
        with transaction.atomic():
            # 创建用户
            UserFactory()
            UserFactory()
        
        # 验证事务提交
        final_count = User.objects.count()
        assert final_count == initial_count + 2
    
    def test_nested_transactions(self):
        """测试嵌套事务"""
        initial_count = User.objects.count()
        
        try:
            with transaction.atomic():
                UserFactory()  # 这个应该被保存
                
                try:
                    with transaction.atomic():
                        UserFactory()  # 这个应该被回滚
                        raise Exception("内部异常")
                except Exception:
                    pass
                
                # 外部事务继续
                UserFactory()  # 这个应该被保存
        except Exception:
            pass
        
        # 验证结果
        final_count = User.objects.count()
        assert final_count == initial_count + 2


@pytest.mark.django_db
class TestDatabaseConstraints:
    """数据库约束测试"""
    
    def test_unique_constraint(self):
        """测试唯一约束"""
        UserFactory(username='unique_user')
        
        # 尝试创建重复用户名的用户
        with pytest.raises(IntegrityError):
            UserFactory(username='unique_user')
    
    def test_null_constraint(self):
        """测试非空约束"""
        # 测试必填字段
        with pytest.raises((IntegrityError, ValidationError)):
            user = User(username=None, email='test@example.com')
            user.full_clean()
    
    def test_foreign_key_constraint(self):
        """测试外键约束"""
        # 这里需要根据实际的外键关系来测试
        # 例如：工具与用户的关系
        pass


@pytest.mark.django_db
class TestDatabaseQueries:
    """数据库查询测试"""
    
    def test_complex_queries(self):
        """测试复杂查询"""
        # 创建测试数据
        active_users = [UserFactory(is_active=True) for _ in range(5)]
        inactive_users = [UserFactory(is_active=False) for _ in range(3)]
        
        # 测试过滤查询
        active_count = User.objects.filter(is_active=True).count()
        assert active_count >= 5
        
        # 测试排序查询
        users = User.objects.order_by('-date_joined')[:3]
        assert len(users) == 3
        
        # 测试聚合查询
        from django.db.models import Count
        stats = User.objects.aggregate(
            total=Count('id'),
            active=Count('id', filter=models.Q(is_active=True))
        )
        assert stats['total'] >= 8
        assert stats['active'] >= 5
    
    def test_query_optimization(self):
        """测试查询优化"""
        # 创建测试数据
        users = [UserFactory() for _ in range(10)]
        
        # 测试select_related和prefetch_related
        # 这里需要根据实际的关联模型来测试
        pass
    
    def test_raw_sql_queries(self):
        """测试原生SQL查询"""
        UserFactory.create_batch(5)
        
        # 执行原生SQL
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            count = cursor.fetchone()[0]
            assert count >= 5


@pytest.mark.django_db
class TestDatabasePerformance:
    """数据库性能测试"""
    
    def test_query_count(self):
        """测试查询次数"""
        from django.test import override_settings
        from django.db import connection
        
        # 创建测试数据
        UserFactory.create_batch(100)
        
        # 重置查询计数
        connection.queries_log.clear()
        
        # 执行查询
        users = list(User.objects.all()[:10])
        
        # 检查查询次数
        query_count = len(connection.queries)
        assert query_count <= 5  # 期望查询次数不超过5次
    
    @pytest.mark.slow
    def test_large_dataset_operations(self):
        """测试大数据集操作"""
        # 创建大量数据
        UserFactory.create_batch(1000)
        
        # 测试批量查询性能
        import time
        start_time = time.time()
        
        users = User.objects.all()[:100]
        list(users)  # 强制执行查询
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # 查询时间应该在合理范围内
        assert query_time < 1.0  # 1秒内完成
    
    def test_database_connection_pooling(self):
        """测试数据库连接池"""
        from django.db import connections
        
        # 获取数据库连接
        connection = connections['default']
        
        # 执行多个查询，验证连接复用
        for i in range(10):
            User.objects.count()
        
        # 验证连接状态
        assert connection.is_usable()
