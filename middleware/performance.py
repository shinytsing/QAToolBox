import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse

from utils.database_optimizer import db_monitor

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware:
    """性能监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_request_threshold = getattr(settings, "SLOW_REQUEST_THRESHOLD", 2.0)
        self.enable_monitoring = getattr(settings, "ENABLE_PERFORMANCE_MONITORING", True)

    def __call__(self, request):
        if not self.enable_monitoring:
            return self.get_response(request)

        # 记录请求开始
        start_time = time.time()
        start_queries = len(connection.queries)

        # 处理请求
        response = self.get_response(request)

        # 计算性能指标
        execution_time = time.time() - start_time
        query_count = len(connection.queries) - start_queries

        # 记录性能指标
        self._log_performance(request, response, execution_time, query_count)

        # 如果是慢请求，添加性能头
        if execution_time > self.slow_request_threshold:
            response["X-Response-Time"] = f"{execution_time:.3f}s"
            response["X-Query-Count"] = str(query_count)

        return response

    def _log_performance(self, request, response, execution_time, query_count):
        """记录性能指标"""
        # 基本信息
        path = request.path
        method = request.method
        status_code = response.status_code

        # 记录慢请求
        if execution_time > self.slow_request_threshold:
            logger.warning(
                f"Slow request: {method} {path} - {execution_time:.3f}s, " f"{query_count} queries, status: {status_code}"
            )

        # 记录性能指标到缓存（用于统计）
        self._store_performance_metrics(path, method, execution_time, query_count, status_code)

    def _store_performance_metrics(self, path, method, execution_time, query_count, status_code):
        """存储性能指标"""
        try:
            # 按路径聚合性能指标
            cache_key = f"perf_metrics:{path}:{method}"
            metrics = cache.get(
                cache_key,
                {
                    "count": 0,
                    "total_time": 0,
                    "total_queries": 0,
                    "avg_time": 0,
                    "avg_queries": 0,
                    "slow_count": 0,
                    "error_count": 0,
                },
            )

            metrics["count"] += 1
            metrics["total_time"] += execution_time
            metrics["total_queries"] += query_count
            metrics["avg_time"] = metrics["total_time"] / metrics["count"]
            metrics["avg_queries"] = metrics["total_queries"] / metrics["count"]

            if execution_time > self.slow_request_threshold:
                metrics["slow_count"] += 1

            if status_code >= 400:
                metrics["error_count"] += 1

            # 缓存1小时
            cache.set(cache_key, metrics, 3600)

        except Exception as e:
            logger.error(f"Failed to store performance metrics: {e}")


class DatabaseQueryMonitoringMiddleware:
    """数据库查询监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_monitoring = getattr(settings, "ENABLE_DB_MONITORING", True)

    def __call__(self, request):
        if not self.enable_monitoring:
            return self.get_response(request)

        # 清理查询日志
        connection.queries = []

        # 处理请求
        response = self.get_response(request)

        # 分析查询
        self._analyze_queries(request, response)

        return response

    def _analyze_queries(self, request, response):
        """分析数据库查询"""
        if not connection.queries:
            return

        # 获取查询统计
        stats = db_monitor.optimizer.analyze_queries()

        # 记录慢查询
        slow_queries = db_monitor.optimizer.get_slow_queries()
        if slow_queries:
            logger.warning(
                f"Slow queries detected in {request.path}: "
                f"{len(slow_queries)} slow queries, "
                f"total time: {stats['total_time']:.3f}s"
            )

            # 记录最慢的查询
            for query in slow_queries[:3]:  # 只记录前3个最慢的
                logger.warning(f"Slow query: {query['sql'][:100]}... " f"Time: {query['time']}s")

        # 存储查询统计
        self._store_query_stats(request.path, stats)

    def _store_query_stats(self, path, stats):
        """存储查询统计"""
        try:
            cache_key = f"db_stats:{path}"
            cache.set(cache_key, stats, 3600)  # 缓存1小时
        except Exception as e:
            logger.error(f"Failed to store query stats: {e}")


class CacheMonitoringMiddleware:
    """缓存监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enable_monitoring = getattr(settings, "ENABLE_CACHE_MONITORING", True)

    def __call__(self, request):
        if not self.enable_monitoring:
            return self.get_response(request)

        # 记录缓存统计
        cache_stats = self._get_cache_stats()

        # 处理请求
        response = self.get_response(request)

        # 更新缓存统计
        self._update_cache_stats(cache_stats)

        return response

    def _get_cache_stats(self):
        """获取缓存统计"""
        try:
            # 这里可以添加更详细的缓存统计
            return {"timestamp": time.time(), "cache_hits": 0, "cache_misses": 0}
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}

    def _update_cache_stats(self, stats):
        """更新缓存统计"""
        try:
            cache_key = "cache_stats"
            cache.set(cache_key, stats, 3600)
        except Exception as e:
            logger.error(f"Failed to update cache stats: {e}")


def get_performance_metrics(path=None):
    """获取性能指标"""
    if path:
        cache_key = f"perf_metrics:{path}:GET"
        return cache.get(cache_key, {})
    else:
        # 获取所有性能指标
        metrics = {}
        # 这里可以实现更复杂的聚合逻辑
        return metrics


def get_database_stats(path=None):
    """获取数据库统计"""
    if path:
        cache_key = f"db_stats:{path}"
        return cache.get(cache_key, {})
    else:
        # 获取所有数据库统计
        stats = {}
        # 这里可以实现更复杂的聚合逻辑
        return stats
