"""
性能优化服务
包括查询优化、缓存优化、连接池优化等
"""

import logging
import time
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection, connections
from django.db.models import QuerySet
from django.utils import timezone
from typing import Dict, List, Any, Optional, Tuple
import psutil
import gc

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """查询优化器"""

    def __init__(self):
        self.slow_queries = []
        self.query_stats = {}
        self.optimization_suggestions = []

    def analyze_query(self, queryset: QuerySet, execution_time: float) -> Dict[str, Any]:
        """分析查询性能"""
        analysis = {
            "query": str(queryset.query),
            "execution_time": execution_time,
            "is_slow": execution_time > 1.0,  # 超过1秒认为是慢查询
            "suggestions": [],
        }

        # 检查是否使用了select_related
        if not hasattr(queryset, "_prefetch_related_lookups") and not hasattr(queryset, "_select_related_lookups"):
            analysis["suggestions"].append("考虑使用select_related()优化外键查询")

        # 检查是否使用了prefetch_related
        if not hasattr(queryset, "_prefetch_related_lookups"):
            analysis["suggestions"].append("考虑使用prefetch_related()优化多对多查询")

        # 检查是否使用了索引
        if "WHERE" in analysis["query"] and "ORDER BY" in analysis["query"]:
            analysis["suggestions"].append("检查WHERE和ORDER BY字段是否有合适的索引")

        # 检查是否使用了LIMIT
        if "LIMIT" not in analysis["query"]:
            analysis["suggestions"].append("考虑使用LIMIT限制结果数量")

        # 记录慢查询
        if analysis["is_slow"]:
            self.slow_queries.append(analysis)
            if len(self.slow_queries) > 100:  # 只保留最近100条
                self.slow_queries = self.slow_queries[-100:]

        return analysis

    def optimize_queryset(self, queryset: QuerySet, **kwargs) -> QuerySet:
        """优化查询集"""
        optimized = queryset

        # 自动添加select_related
        if kwargs.get("auto_select_related", True):
            optimized = self._add_select_related(optimized)

        # 自动添加prefetch_related
        if kwargs.get("auto_prefetch_related", True):
            optimized = self._add_prefetch_related(optimized)

        # 添加only/values优化
        if kwargs.get("fields"):
            optimized = optimized.only(*kwargs["fields"])

        # 添加分页
        if kwargs.get("limit"):
            optimized = optimized[: kwargs["limit"]]

        return optimized

    def _add_select_related(self, queryset: QuerySet) -> QuerySet:
        """自动添加select_related"""
        model = queryset.model
        related_fields = []

        # 获取外键字段
        for field in model._meta.get_fields():
            if field.is_relation and field.many_to_one:
                related_fields.append(field.name)

        if related_fields:
            return queryset.select_related(*related_fields)

        return queryset

    def _add_prefetch_related(self, queryset: QuerySet) -> QuerySet:
        """自动添加prefetch_related"""
        model = queryset.model
        related_fields = []

        # 获取多对多字段
        for field in model._meta.get_fields():
            if field.is_relation and field.many_to_many:
                related_fields.append(field.name)

        if related_fields:
            return queryset.prefetch_related(*related_fields)

        return queryset

    def get_slow_queries_report(self) -> Dict[str, Any]:
        """获取慢查询报告"""
        if not self.slow_queries:
            return {"message": "没有发现慢查询"}

        # 按执行时间排序
        sorted_queries = sorted(self.slow_queries, key=lambda x: x["execution_time"], reverse=True)

        # 统计信息
        total_slow_queries = len(sorted_queries)
        avg_execution_time = sum(q["execution_time"] for q in sorted_queries) / total_slow_queries
        max_execution_time = max(q["execution_time"] for q in sorted_queries)

        return {
            "total_slow_queries": total_slow_queries,
            "avg_execution_time": avg_execution_time,
            "max_execution_time": max_execution_time,
            "top_slow_queries": sorted_queries[:10],  # 前10个最慢的查询
            "common_suggestions": self._get_common_suggestions(sorted_queries),
        }

    def _get_common_suggestions(self, slow_queries: List[Dict]) -> List[str]:
        """获取通用优化建议"""
        suggestions = []

        # 统计建议频率
        suggestion_counts = {}
        for query in slow_queries:
            for suggestion in query["suggestions"]:
                suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1

        # 返回最常见的建议
        sorted_suggestions = sorted(suggestion_counts.items(), key=lambda x: x[1], reverse=True)
        return [suggestion for suggestion, count in sorted_suggestions[:5]]


class CacheOptimizer:
    """缓存优化器"""

    def __init__(self):
        self.cache_stats = {}
        self.cache_patterns = {}

    def optimize_cache_key(self, key: str, data: Any, ttl: int = 300) -> str:
        """优化缓存键"""
        # 添加版本前缀
        versioned_key = f"v1:{key}"

        # 记录缓存模式
        pattern = self._extract_pattern(key)
        if pattern not in self.cache_patterns:
            self.cache_patterns[pattern] = {"count": 0, "total_size": 0, "avg_ttl": 0}

        self.cache_patterns[pattern]["count"] += 1
        self.cache_patterns[pattern]["total_size"] += len(str(data))
        self.cache_patterns[pattern]["avg_ttl"] = (self.cache_patterns[pattern]["avg_ttl"] + ttl) / 2

        return versioned_key

    def _extract_pattern(self, key: str) -> str:
        """提取缓存键模式"""
        # 将数字替换为通配符
        import re

        pattern = re.sub(r"\d+", "*", key)
        return pattern

    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 检查缓存后端类型
            cache_backend = cache.__class__.__name__

            if hasattr(cache, "client") and hasattr(cache.client, "get_client"):
                # Redis 缓存
                redis_client = cache.client.get_client()
                info = redis_client.info()

                stats = {
                    "backend": "Redis",
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "patterns": self.cache_patterns,
                }
            else:
                # 本地内存缓存或其他类型
                stats = {
                    "backend": cache_backend,
                    "used_memory": 0,
                    "used_memory_human": "0B",
                    "connected_clients": 1,
                    "total_commands_processed": 0,
                    "keyspace_hits": 0,
                    "keyspace_misses": 0,
                    "patterns": self.cache_patterns,
                }

            # 计算命中率
            total_requests = stats["keyspace_hits"] + stats["keyspace_misses"]
            if total_requests > 0:
                stats["hit_rate"] = stats["keyspace_hits"] / total_requests
            else:
                stats["hit_rate"] = 0

            return stats

        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {e}")
            return {"error": str(e)}

    def optimize_cache_strategy(self, data_type: str, access_pattern: str) -> Dict[str, Any]:
        """优化缓存策略"""
        strategies = {
            "user_profile": {"ttl": 3600, "strategy": "write_through", "invalidation": "on_update"},  # 1小时
            "tool_results": {"ttl": 1800, "strategy": "write_back", "invalidation": "time_based"},  # 30分钟
            "social_data": {"ttl": 600, "strategy": "cache_aside", "invalidation": "on_event"},  # 10分钟
            "analytics": {"ttl": 86400, "strategy": "write_through", "invalidation": "scheduled"},  # 24小时
        }

        return strategies.get(data_type, {"ttl": 300, "strategy": "cache_aside", "invalidation": "time_based"})


class ConnectionPoolOptimizer:
    """连接池优化器"""

    def __init__(self):
        self.pool_stats = {}

    def optimize_connection_pool(self) -> Dict[str, Any]:
        """优化连接池配置"""
        current_stats = self.get_connection_pool_stats()

        recommendations = []

        # 检查连接数
        if current_stats["active_connections"] > current_stats["max_connections"] * 0.8:
            recommendations.append(
                {
                    "type": "increase_max_connections",
                    "message": "活跃连接数接近最大值，建议增加最大连接数",
                    "current": current_stats["active_connections"],
                    "max": current_stats["max_connections"],
                }
            )

        # 检查连接等待时间
        if current_stats["avg_wait_time"] > 1.0:
            recommendations.append(
                {
                    "type": "increase_pool_size",
                    "message": "连接等待时间过长，建议增加连接池大小",
                    "current_wait_time": current_stats["avg_wait_time"],
                }
            )

        # 检查连接空闲时间
        if current_stats["idle_connections"] > current_stats["max_connections"] * 0.5:
            recommendations.append(
                {
                    "type": "decrease_pool_size",
                    "message": "空闲连接数过多，建议减少连接池大小",
                    "idle_connections": current_stats["idle_connections"],
                }
            )

        return {"current_stats": current_stats, "recommendations": recommendations}

    def get_connection_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        try:
            # 检查数据库类型
            is_postgres = "postgresql" in connection.settings_dict["ENGINE"]

            if is_postgres:
                # PostgreSQL 特定查询
                with connection.cursor() as cursor:
                    cursor.execute("SELECT count(*) FROM pg_stat_activity")
                    active_connections = cursor.fetchone()[0]

                    cursor.execute("SELECT setting FROM pg_settings WHERE name = 'max_connections'")
                    max_connections = int(cursor.fetchone()[0])
            else:
                # 其他数据库使用默认值
                active_connections = 1
                max_connections = 100

            # 估算空闲连接数
            idle_connections = max(0, active_connections - 10)  # 假设10个活跃连接

            return {
                "active_connections": active_connections,
                "max_connections": max_connections,
                "idle_connections": idle_connections,
                "connection_usage": active_connections / max_connections,
                "avg_wait_time": 0.1,  # 估算值
                "timestamp": timezone.now(),
            }

        except Exception as e:
            logger.error(f"获取连接池统计信息失败: {e}")
            return {"error": str(e)}


class MemoryOptimizer:
    """内存优化器"""

    def __init__(self):
        self.memory_stats = {}

    def optimize_memory_usage(self) -> Dict[str, Any]:
        """优化内存使用"""
        current_stats = self.get_memory_stats()

        recommendations = []

        # 检查内存使用率
        if current_stats["memory_percent"] > 80:
            recommendations.append(
                {
                    "type": "high_memory_usage",
                    "message": "内存使用率过高，建议增加内存或优化代码",
                    "usage_percent": current_stats["memory_percent"],
                }
            )

        # 检查Python对象数量
        if current_stats["python_objects"] > 1000000:
            recommendations.append(
                {
                    "type": "too_many_objects",
                    "message": "Python对象数量过多，建议进行垃圾回收",
                    "object_count": current_stats["python_objects"],
                }
            )

        # 检查内存泄漏
        if current_stats["memory_growth_rate"] > 0.1:  # 10%增长
            recommendations.append(
                {"type": "memory_leak", "message": "检测到可能的内存泄漏", "growth_rate": current_stats["memory_growth_rate"]}
            )

        return {"current_stats": current_stats, "recommendations": recommendations}

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        try:
            # 系统内存信息
            memory = psutil.virtual_memory()

            # Python进程内存信息
            process = psutil.Process()
            process_memory = process.memory_info()

            # Python对象统计
            python_objects = len(gc.get_objects())

            # 计算内存增长率
            current_time = timezone.now()
            if "last_check" in self.memory_stats:
                time_diff = (current_time - self.memory_stats["last_check"]).total_seconds()
                memory_diff = process_memory.rss - self.memory_stats.get("last_rss", process_memory.rss)
                growth_rate = memory_diff / time_diff if time_diff > 0 else 0
            else:
                growth_rate = 0

            stats = {
                "memory_percent": memory.percent,
                "available_memory": memory.available,
                "total_memory": memory.total,
                "process_rss": process_memory.rss,
                "process_vms": process_memory.vms,
                "python_objects": python_objects,
                "memory_growth_rate": growth_rate,
                "timestamp": current_time,
            }

            # 保存上次检查的信息
            self.memory_stats = stats.copy()
            self.memory_stats["last_check"] = current_time
            self.memory_stats["last_rss"] = process_memory.rss

            return stats

        except Exception as e:
            logger.error(f"获取内存统计信息失败: {e}")
            return {"error": str(e)}

    def perform_garbage_collection(self) -> Dict[str, Any]:
        """执行垃圾回收"""
        try:
            # 记录回收前的对象数量
            objects_before = len(gc.get_objects())

            # 执行垃圾回收
            collected = gc.collect()

            # 记录回收后的对象数量
            objects_after = len(gc.get_objects())

            return {
                "objects_before": objects_before,
                "objects_after": objects_after,
                "objects_freed": objects_before - objects_after,
                "collected": collected,
                "timestamp": timezone.now(),
            }

        except Exception as e:
            logger.error(f"垃圾回收失败: {e}")
            return {"error": str(e)}


class PerformanceOptimizer:
    """性能优化主类"""

    def __init__(self):
        self.query_optimizer = QueryOptimizer()
        self.cache_optimizer = CacheOptimizer()
        self.connection_optimizer = ConnectionPoolOptimizer()
        self.memory_optimizer = MemoryOptimizer()

    def run_full_optimization(self) -> Dict[str, Any]:
        """运行完整性能优化"""
        results = {
            "timestamp": timezone.now(),
            "query_optimization": self.query_optimizer.get_slow_queries_report(),
            "cache_optimization": self.cache_optimizer.get_cache_stats(),
            "connection_optimization": self.connection_optimizer.optimize_connection_pool(),
            "memory_optimization": self.memory_optimizer.optimize_memory_usage(),
        }

        # 缓存优化结果
        cache.set("performance_optimization_results", results, timeout=3600)

        return results

    def get_optimization_summary(self) -> Dict[str, Any]:
        """获取优化摘要"""
        cached_results = cache.get("performance_optimization_results")
        if not cached_results:
            return {"message": "没有可用的优化结果"}

        summary = {
            "timestamp": cached_results["timestamp"],
            "total_recommendations": 0,
            "critical_issues": 0,
            "optimization_areas": [],
        }

        # 统计建议数量
        for area, data in cached_results.items():
            if area == "timestamp":
                continue

            if "recommendations" in data:
                recommendations = data["recommendations"]
                summary["total_recommendations"] += len(recommendations)

                # 检查关键问题
                for rec in recommendations:
                    if rec.get("type") in ["high_memory_usage", "memory_leak", "increase_max_connections"]:
                        summary["critical_issues"] += 1

                if recommendations:
                    summary["optimization_areas"].append(area)

        return summary


# 全局实例
performance_optimizer = PerformanceOptimizer()


# 装饰器：性能监控
def monitor_performance(func):
    """性能监控装饰器"""

    def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            # 记录性能数据
            if hasattr(result, "query") and isinstance(result, QuerySet):
                performance_optimizer.query_optimizer.analyze_query(result, execution_time)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数执行失败 {func.__name__}: {e} (耗时: {execution_time:.3f}s)")
            raise

    return wrapper


# 定时任务：性能优化
def run_performance_optimization():
    """运行性能优化任务"""
    try:
        results = performance_optimizer.run_full_optimization()
        logger.info("性能优化完成")

        # 检查是否有关键问题
        summary = performance_optimizer.get_optimization_summary()
        if summary["critical_issues"] > 0:
            logger.warning(f"发现 {summary['critical_issues']} 个关键性能问题")

    except Exception as e:
        logger.error(f"性能优化失败: {e}")


# 定时任务：垃圾回收
def run_garbage_collection():
    """运行垃圾回收任务"""
    try:
        result = performance_optimizer.memory_optimizer.perform_garbage_collection()
        logger.info(f"垃圾回收完成，释放了 {result.get('objects_freed', 0)} 个对象")

    except Exception as e:
        logger.error(f"垃圾回收失败: {e}")
