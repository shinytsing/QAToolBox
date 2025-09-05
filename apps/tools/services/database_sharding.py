"""
数据库分片服务
支持水平分片和垂直分片，为大规模数据做准备
"""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, List

from django.core.cache import cache
from django.db import connections
from django.utils import timezone

logger = logging.getLogger(__name__)


class ShardManager:
    """分片管理器"""

    def __init__(self):
        self.shards = {}
        self.shard_configs = {}
        self.load_shard_configs()

    def load_shard_configs(self):
        """加载分片配置"""
        # 检查是否在开发环境
        from django.conf import settings

        # 如果是开发环境且没有配置分片数据库，使用默认配置
        if settings.DEBUG and not self._has_shard_databases():
            # 开发环境：使用默认数据库，不配置分片
            self.shard_configs = {}
            logger.info("开发环境：未配置分片数据库，使用默认单数据库模式")
            return

        # 生产环境或已配置分片的开发环境：加载完整分片配置
        self.shard_configs = {
            "user_data": {
                "type": "horizontal",
                "shards": ["user_shard_1", "user_shard_2", "user_shard_3"],
                "key_field": "user_id",
                "strategy": "hash",
                "replication_factor": 2,
            },
            "tool_logs": {
                "type": "horizontal",
                "shards": ["tool_shard_1", "tool_shard_2", "tool_shard_3", "tool_shard_4"],
                "key_field": "created_at",
                "strategy": "time_based",
                "time_interval": "monthly",
            },
            "social_data": {
                "type": "vertical",
                "shards": {
                    "social_posts": ["social_shard_1", "social_shard_2"],
                    "social_users": ["social_shard_3"],
                    "social_analytics": ["social_shard_4"],
                },
                "strategy": "table_based",
            },
            "analytics_data": {
                "type": "horizontal",
                "shards": ["analytics_shard_1", "analytics_shard_2"],
                "key_field": "date",
                "strategy": "time_based",
                "time_interval": "weekly",
            },
        }

    def _has_shard_databases(self):
        """检查是否配置了分片数据库"""
        from django.db import connections

        # 检查是否存在任何分片数据库连接
        test_shards = ["user_shard_1", "tool_shard_1", "analytics_shard_1"]

        for shard in test_shards:
            if shard in connections.databases:
                return True

        # 如果没有配置分片数据库，在生产环境也返回 False
        # 这样可以避免分片健康检查的错误
        return False

    def get_shard_for_key(self, table_name: str, key_value: Any) -> str:
        """根据键值获取分片"""
        config = self.shard_configs.get(table_name)
        if not config:
            return "default"

        if config["type"] == "horizontal":
            return self._get_horizontal_shard(config, key_value)
        elif config["type"] == "vertical":
            return self._get_vertical_shard(config, table_name)

        return "default"

    def _get_horizontal_shard(self, config: Dict, key_value: Any) -> str:
        """获取水平分片"""
        strategy = config.get("strategy", "hash")
        shards = config["shards"]

        if strategy == "hash":
            # 基于哈希的分片
            if isinstance(key_value, str):
                hash_value = hashlib.md5(key_value.encode(), usedforsecurity=False).hexdigest()
            else:
                hash_value = hashlib.md5(str(key_value).encode(), usedforsecurity=False).hexdigest()

            shard_index = int(hash_value, 16) % len(shards)
            return shards[shard_index]

        elif strategy == "time_based":
            # 基于时间的分片
            if isinstance(key_value, datetime):
                date = key_value
            elif isinstance(key_value, str):
                date = datetime.fromisoformat(key_value.replace("Z", "+00:00"))
            else:
                date = timezone.now()

            time_interval = config.get("time_interval", "monthly")

            if time_interval == "monthly":
                shard_index = (date.year - 2020) * 12 + date.month - 1
            elif time_interval == "weekly":
                shard_index = (date - datetime(2020, 1, 1)).days // 7
            elif time_interval == "daily":
                shard_index = (date - datetime(2020, 1, 1)).days

            return shards[shard_index % len(shards)]

        return shards[0]

    def _get_vertical_shard(self, config: Dict, table_name: str) -> str:
        """获取垂直分片"""
        shards = config["shards"]

        for table_pattern, shard_list in shards.items():
            if table_name.startswith(table_pattern):
                return shard_list[0]  # 简单返回第一个分片

        return "default"

    def get_all_shards(self, table_name: str) -> List[str]:
        """获取表的所有分片"""
        config = self.shard_configs.get(table_name)
        if not config:
            return ["default"]

        if config["type"] == "horizontal":
            return config["shards"]
        elif config["type"] == "vertical":
            all_shards = []
            for shard_list in config["shards"].values():
                all_shards.extend(shard_list)
            return all_shards

        return ["default"]


class ShardedQuerySet:
    """分片查询集"""

    def __init__(self, model_class, shard_manager: ShardManager):
        self.model_class = model_class
        self.shard_manager = shard_manager
        self.table_name = model_class._meta.db_table
        self.filters = {}
        self.ordering = []
        self.limit = None
        self.offset = None

    def filter(self, **kwargs):
        """添加过滤条件"""
        self.filters.update(kwargs)
        return self

    def order_by(self, *fields):
        """添加排序"""
        self.ordering.extend(fields)
        return self

    def limit(self, limit):
        """限制结果数量"""
        self.limit = limit
        return self

    def offset(self, offset):
        """设置偏移量"""
        self.offset = offset
        return self

    def execute(self) -> List[Any]:
        """执行分片查询"""
        config = self.shard_manager.shard_configs.get(self.table_name)
        if not config:
            # 使用默认数据库
            return self._execute_on_shard("default")

        if config["type"] == "horizontal":
            return self._execute_horizontal_query()
        elif config["type"] == "vertical":
            return self._execute_vertical_query()

        return self._execute_on_shard("default")

    def _execute_horizontal_query(self) -> List[Any]:
        """执行水平分片查询"""
        results = []
        shards = self.shard_manager.get_all_shards(self.table_name)

        for shard in shards:
            try:
                shard_results = self._execute_on_shard(shard)
                results.extend(shard_results)
            except Exception as e:
                logger.error(f"分片查询失败 {shard}: {e}")
                continue

        # 合并和排序结果
        if self.ordering:
            results = self._sort_results(results)

        # 应用分页
        if self.offset is not None:
            results = results[self.offset :]
        if self.limit is not None:
            results = results[: self.limit]

        return results

    def _execute_vertical_query(self) -> List[Any]:
        """执行垂直分片查询"""
        # 垂直分片通常需要跨分片JOIN，这里简化处理
        primary_shard = self.shard_manager.get_all_shards(self.table_name)[0]
        return self._execute_on_shard(primary_shard)

    def _execute_on_shard(self, shard: str) -> List[Any]:
        """在指定分片上执行查询"""
        # 这里应该根据实际的分片实现来执行查询
        # 目前返回空列表作为占位符
        return []

    def _sort_results(self, results: List[Any]) -> List[Any]:
        """排序结果"""
        # 实现排序逻辑
        return sorted(results, key=lambda x: getattr(x, self.ordering[0]))


class ShardRouter:
    """分片路由器"""

    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager

    def db_for_read(self, model, **hints):
        """为读操作选择数据库"""
        table_name = model._meta.db_table
        config = self.shard_manager.shard_configs.get(table_name)

        if not config:
            return "default"

        # 根据配置选择读数据库
        if config["type"] == "horizontal":
            # 水平分片：选择主分片
            return config["shards"][0]
        elif config["type"] == "vertical":
            # 垂直分片：选择对应的分片
            for table_pattern, shards in config["shards"].items():
                if table_name.startswith(table_pattern):
                    return shards[0]

        return "default"

    def db_for_write(self, model, **hints):
        """为写操作选择数据库"""
        table_name = model._meta.db_table
        config = self.shard_manager.shard_configs.get(table_name)

        if not config:
            return "default"

        # 写操作通常路由到主分片
        if config["type"] == "horizontal":
            return config["shards"][0]
        elif config["type"] == "vertical":
            for table_pattern, shards in config["shards"].items():
                if table_name.startswith(table_pattern):
                    return shards[0]

        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """允许关系查询"""
        # 检查两个对象是否在同一分片
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """允许迁移"""
        return True


class ShardReplication:
    """分片复制管理"""

    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager

    def replicate_data(self, table_name: str, data: Dict, source_shard: str):
        """复制数据到其他分片"""
        config = self.shard_manager.shard_configs.get(table_name)
        if not config:
            return

        replication_factor = config.get("replication_factor", 1)
        shards = config["shards"]

        # 选择要复制的目标分片
        target_shards = []
        for i, shard in enumerate(shards):
            if shard != source_shard and len(target_shards) < replication_factor:
                target_shards.append(shard)

        # 执行复制
        for target_shard in target_shards:
            try:
                self._copy_to_shard(table_name, data, target_shard)
                logger.info(f"数据复制成功: {source_shard} -> {target_shard}")
            except Exception as e:
                logger.error(f"数据复制失败: {source_shard} -> {target_shard}: {e}")

    def _copy_to_shard(self, table_name: str, data: Dict, target_shard: str):
        """复制数据到指定分片"""
        # 实现数据复制逻辑

    def sync_shards(self, table_name: str):
        """同步分片数据"""
        config = self.shard_manager.shard_configs.get(table_name)
        if not config:
            return

        shards = config["shards"]
        primary_shard = shards[0]

        # 从主分片同步到其他分片
        for shard in shards[1:]:
            try:
                self._sync_shard_data(table_name, primary_shard, shard)
                logger.info(f"分片同步成功: {primary_shard} -> {shard}")
            except Exception as e:
                logger.error(f"分片同步失败: {primary_shard} -> {shard}: {e}")


class ShardMonitoring:
    """分片监控"""

    def __init__(self, shard_manager: ShardManager):
        self.shard_manager = shard_manager

    def get_shard_stats(self) -> Dict[str, Any]:
        """获取分片统计信息"""
        stats = {}

        # 如果没有配置分片，返回空统计
        if not self.shard_manager.shard_configs:
            return {"message": "No shards configured, using single database mode"}

        for table_name, config in self.shard_manager.shard_configs.items():
            table_stats = {
                "type": config["type"],
                "shards": config["shards"],
                "shard_count": (
                    len(config["shards"])
                    if isinstance(config["shards"], list)
                    else sum(len(s) for s in config["shards"].values())
                ),
                "status": "healthy",
            }

            # 检查每个分片的状态
            if config["type"] == "horizontal":
                for shard in config["shards"]:
                    shard_status = self._check_shard_health(shard)
                    if shard_status != "healthy":
                        table_stats["status"] = "warning"

            stats[table_name] = table_stats

        return stats

    def _check_shard_health(self, shard: str) -> str:
        """检查分片健康状态"""
        try:
            # 检查分片是否配置
            if shard not in connections.databases:
                logger.warning(f"分片 {shard} 未配置，跳过健康检查")
                return "not_configured"

            # 检查分片连接
            with connections[shard].cursor() as cursor:
                cursor.execute("SELECT 1")
                return "healthy"
        except Exception as e:
            logger.error(f"分片健康检查失败 {shard}: {e}")
            return "unhealthy"

    def get_shard_performance(self) -> Dict[str, Any]:
        """获取分片性能指标"""
        performance = {}

        for table_name, config in self.shard_manager.shard_configs.items():
            table_performance = {}

            if config["type"] == "horizontal":
                for shard in config["shards"]:
                    shard_perf = self._get_shard_performance_metrics(shard)
                    table_performance[shard] = shard_perf

            performance[table_name] = table_performance

        return performance

    def _get_shard_performance_metrics(self, shard: str) -> Dict[str, Any]:
        """获取分片性能指标"""
        try:
            # 检查分片数据库类型
            shard_connection = connections[shard]
            is_postgres = "postgresql" in shard_connection.settings_dict["ENGINE"]

            with shard_connection.cursor() as cursor:
                if is_postgres:
                    # PostgreSQL 特定查询
                    cursor.execute("SELECT count(*) FROM pg_stat_activity")
                    connections_count = cursor.fetchone()[0]

                    # 获取查询统计（如果有 pg_stat_statements 扩展）
                    try:
                        cursor.execute("SELECT sum(calls) FROM pg_stat_statements")
                        total_queries = cursor.fetchone()[0] or 0
                    except Exception:
                        total_queries = 0
                else:
                    # 其他数据库使用默认值
                    connections_count = 1
                    total_queries = 0

                return {"connections": connections_count, "total_queries": total_queries, "status": "healthy"}
        except Exception as e:
            logger.error(f"获取分片性能指标失败 {shard}: {e}")
            return {"connections": 0, "total_queries": 0, "status": "unhealthy"}


# 全局实例
shard_manager = ShardManager()
shard_router = ShardRouter(shard_manager)
shard_replication = ShardReplication(shard_manager)
shard_monitoring = ShardMonitoring(shard_manager)


# 工具函数
def get_shard_for_user(user_id: int) -> str:
    """获取用户数据的分片"""
    return shard_manager.get_shard_for_key("user_data", user_id)


def get_shard_for_tool_log(created_at: datetime) -> str:
    """获取工具日志的分片"""
    return shard_manager.get_shard_for_key("tool_logs", created_at)


def get_shard_for_social_data(table_name: str) -> str:
    """获取社交数据的分片"""
    return shard_manager.get_shard_for_key("social_data", table_name)


# 定时任务：分片健康检查
def check_shards_health():
    """检查所有分片健康状态"""
    try:
        # 如果没有配置分片，跳过检查
        if not shard_manager.shard_configs:
            logger.debug("未配置分片，跳过分片健康检查")
            return

        stats = shard_monitoring.get_shard_stats()

        for table_name, table_stats in stats.items():
            if table_stats["status"] != "healthy":
                logger.warning(f"分片健康状态异常: {table_name} - {table_stats['status']}")

        # 缓存分片统计信息
        cache.set("shard_stats", stats, timeout=300)

    except Exception as e:
        logger.error(f"分片健康检查失败: {e}")


# 定时任务：分片数据同步
def sync_shard_data():
    """同步分片数据"""
    try:
        for table_name in shard_manager.shard_configs.keys():
            shard_replication.sync_shards(table_name)

        logger.info("分片数据同步完成")

    except Exception as e:
        logger.error(f"分片数据同步失败: {e}")
