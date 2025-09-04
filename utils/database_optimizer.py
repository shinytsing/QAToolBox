import logging
import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.db import connection

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库查询优化器"""

    def __init__(self):
        self.slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 1.0)

    def log_slow_queries(self, func):
        """装饰器：记录慢查询"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            if execution_time > self.slow_query_threshold:
                logger.warning(f"Slow query detected: {func.__name__} took {execution_time:.3f}s")

            return result

        return wrapper

    def get_query_count(self):
        """获取当前查询数量"""
        return len(connection.queries)

    def get_slow_queries(self, threshold=None):
        """获取慢查询列表"""
        if threshold is None:
            threshold = self.slow_query_threshold

        slow_queries = []
        for query in connection.queries:
            if float(query["time"]) > threshold:
                slow_queries.append(query)

        return slow_queries

    def clear_query_log(self):
        """清理查询日志"""
        connection.queries = []

    def analyze_queries(self):
        """分析查询性能"""
        if not connection.queries:
            return {}

        total_time = sum(float(q["time"]) for q in connection.queries)
        avg_time = total_time / len(connection.queries)
        slow_count = len(self.get_slow_queries())

        return {
            "total_queries": len(connection.queries),
            "total_time": total_time,
            "avg_time": avg_time,
            "slow_queries": slow_count,
            "slow_query_threshold": self.slow_query_threshold,
        }


class QueryCache:
    """查询缓存管理器"""

    def __init__(self, timeout=300):
        self.timeout = timeout

    def cache_query(self, key, func, *args, **kwargs):
        """缓存查询结果"""
        cache_key = f"query_cache:{key}"
        result = cache.get(cache_key)

        if result is None:
            result = func(*args, **kwargs)
            cache.set(cache_key, result, self.timeout)

        return result

    def invalidate_cache(self, pattern):
        """使缓存失效"""
        # 这里可以实现更复杂的缓存失效逻辑
        cache.delete_pattern(f"query_cache:{pattern}")


class DatabaseMonitor:
    """数据库监控器"""

    def __init__(self):
        self.optimizer = DatabaseOptimizer()
        self.query_cache = QueryCache()

    def monitor_query(self, func):
        """监控查询性能"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # 记录查询开始
            start_queries = self.optimizer.get_query_count()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # 记录查询结束
                end_queries = self.optimizer.get_query_count()
                execution_time = time.time() - start_time
                query_count = end_queries - start_queries

                # 记录性能指标
                self._log_performance(func.__name__, execution_time, query_count)

                return result

            except Exception as e:
                logger.error(f"Query failed: {func.__name__} - {e}")
                raise

        return wrapper

    def _log_performance(self, func_name, execution_time, query_count):
        """记录性能指标"""
        if execution_time > self.optimizer.slow_query_threshold:
            logger.warning(f"Slow query: {func_name} - {execution_time:.3f}s, {query_count} queries")

        # 可以在这里添加性能指标收集
        # 例如发送到监控系统


# 全局实例
db_monitor = DatabaseMonitor()
query_cache = QueryCache()


def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """优化QuerySet"""
    if select_related:
        queryset = queryset.select_related(*select_related)

    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)

    return queryset


def bulk_operation(queryset, operation, batch_size=1000):
    """批量操作"""
    total_count = queryset.count()
    processed_count = 0

    for i in range(0, total_count, batch_size):
        batch = queryset[i : i + batch_size]
        operation(batch)
        processed_count += len(batch)

        logger.info(f"Processed {processed_count}/{total_count} records")

    return processed_count


def cache_queryset(key, queryset, timeout=300):
    """缓存QuerySet结果"""
    return query_cache.cache_query(key, lambda: list(queryset), timeout=timeout)


# 常用优化装饰器
def monitor_database_query(func):
    """监控数据库查询装饰器"""
    return db_monitor.monitor_query(func)


def cache_database_result(key_prefix, timeout=300):
    """缓存数据库结果装饰器"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{key_prefix}:{hash(str(args) + str(kwargs))}"
            return query_cache.cache_query(cache_key, func, *args, **kwargs)

        return wrapper

    return decorator
