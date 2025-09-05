import hashlib
import logging
import pickle  # nosec B403
import zlib
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheService:
    """优化的缓存服务类"""

    def __init__(self, default_timeout: int = 300):
        self.default_timeout = default_timeout
        self.cache_prefix = getattr(settings, "CACHE_PREFIX", "qatoolbox")

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [self.cache_prefix, prefix]

        # 添加位置参数
        for arg in args:
            key_parts.append(str(arg))

        # 添加关键字参数
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

        # 生成哈希以避免键过长
        key_string = "_".join(key_parts)
        if len(key_string) > 200:  # Redis键长度限制
            hash_obj = hashlib.md5(key_string.encode(), usedforsecurity=False)
            return f"{self.cache_prefix}_{prefix}_{hash_obj.hexdigest()}"

        return key_string

    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        try:
            value = cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                logger.debug(f"Cache miss: {key}")
                return default
        except Exception as e:
            logger.error(f"Error getting cache for key {key}: {e}")
            return default

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            if timeout is None:
                timeout = self.default_timeout

            # 压缩大对象
            if isinstance(value, (dict, list)) and len(str(value)) > 1000:
                compressed_value = {"_compressed": True, "data": zlib.compress(pickle.dumps(value))}
                cache.set(key, compressed_value, timeout)
            else:
                cache.set(key, value, timeout)

            logger.debug(f"Cache set: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache for key {key}: {e}")
            return False

    def get_or_set(self, key: str, default_func: Callable, timeout: Optional[int] = None) -> Any:
        """获取缓存值，如果不存在则设置默认值"""
        value = self.get(key)
        if value is not None:
            # 解压缩数据
            if isinstance(value, dict) and value.get("_compressed"):
                try:
                    value = pickle.loads(zlib.decompress(value["data"]))  # nosec B301
                except Exception as e:
                    logger.error(f"Error decompressing cache data for key {key}: {e}")
                    value = None

            if value is not None:
                return value

        # 生成默认值
        try:
            value = default_func()
            self.set(key, value, timeout)
            return value
        except Exception as e:
            logger.error(f"Error generating default value for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            cache.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache for key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """清除匹配模式的缓存键"""
        try:
            # 这里需要根据具体的缓存后端实现
            # 对于Redis，可以使用scan和delete
            # 对于内存缓存，只能等待过期
            logger.info(f"Clearing cache pattern: {pattern}")
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0

    def clear_user_cache(self, user_id: int, prefix: Optional[str] = None) -> int:
        """清除用户相关缓存"""
        if prefix:
            pattern = f"{self.cache_prefix}_{prefix}_{user_id}_*"
        else:
            pattern = f"{self.cache_prefix}_*_{user_id}_*"

        return self.clear_pattern(pattern)

    def clear_model_cache(self, model_name: str, instance_id: Optional[int] = None) -> int:
        """清除模型相关缓存"""
        if instance_id:
            pattern = f"{self.cache_prefix}_{model_name}_{instance_id}_*"
        else:
            pattern = f"{self.cache_prefix}_{model_name}_*"

        return self.clear_pattern(pattern)

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取缓存值"""
        try:
            result = cache.get_many(keys)
            logger.debug(f"Cache get_many: {len(result)}/{len(keys)} hits")
            return result
        except Exception as e:
            logger.error(f"Error getting multiple cache keys: {e}")
            return {}

    def set_many(self, data: Dict[str, Any], timeout: Optional[int] = None) -> bool:
        """批量设置缓存值"""
        try:
            if timeout is None:
                timeout = self.default_timeout

            # 压缩大对象
            compressed_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)) and len(str(value)) > 1000:
                    compressed_data[key] = {"_compressed": True, "data": zlib.compress(pickle.dumps(value))}
                else:
                    compressed_data[key] = value

            cache.set_many(compressed_data, timeout)
            logger.debug(f"Cache set_many: {len(data)} keys")
            return True
        except Exception as e:
            logger.error(f"Error setting multiple cache keys: {e}")
            return False

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """增加计数器"""
        try:
            return cache.incr(key, delta)
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """减少计数器"""
        try:
            return cache.decr(key, delta)
        except Exception as e:
            logger.error(f"Error decrementing cache key {key}: {e}")
            return None

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 这里需要根据具体的缓存后端实现
            # 对于Redis，可以获取内存使用情况等
            return {
                "backend": getattr(settings, "CACHE_BACKEND", "unknown"),
                "prefix": self.cache_prefix,
                "default_timeout": self.default_timeout,
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# 全局缓存服务实例
cache_service = CacheService()


def cached(timeout: Optional[int] = None, key_func: Optional[Callable] = None):
    """缓存装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认键生成策略
                func_name = func.__name__
                module_name = func.__module__
                key_parts = [module_name, func_name]

                # 添加参数
                for arg in args:
                    key_parts.append(str(arg))
                for key, value in sorted(kwargs.items()):
                    key_parts.append(f"{key}:{value}")

                cache_key = "_".join(key_parts)

            # 获取或设置缓存
            def default_func():
                return func(*args, **kwargs)

            return cache_service.get_or_set(cache_key, default_func, timeout)

        return wrapper

    return decorator


def cache_invalidate(pattern: str):
    """缓存失效装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            cache_service.clear_pattern(pattern)
            return result

        return wrapper

    return decorator


class ModelCacheMixin:
    """模型缓存混入类"""

    def get_cache_key(self, suffix: str = "") -> str:
        """获取模型实例的缓存键"""
        model_name = self.__class__.__name__.lower()
        key_parts = [model_name, self.id]
        if suffix:
            key_parts.append(suffix)
        return "_".join(key_parts)

    def get_cached_field(self, field_name: str, default_func: Callable) -> Any:
        """获取缓存的字段值"""
        cache_key = self.get_cache_key(f"field_{field_name}")
        return cache_service.get_or_set(cache_key, default_func)

    def set_cached_field(self, field_name: str, value: Any, timeout: Optional[int] = None) -> bool:
        """设置缓存的字段值"""
        cache_key = self.get_cache_key(f"field_{field_name}")
        return cache_service.set(cache_key, value, timeout)

    def clear_instance_cache(self) -> int:
        """清除实例相关缓存"""
        pattern = f"*{self.__class__.__name__.lower()}_{self.id}_*"
        return cache_service.clear_pattern(pattern)

    def save(self, *args, **kwargs):
        """重写save方法，清除相关缓存"""
        result = super().save(*args, **kwargs)
        self.clear_instance_cache()
        return result

    def delete(self, *args, **kwargs):
        """重写delete方法，清除相关缓存"""
        self.clear_instance_cache()
        return super().delete(*args, **kwargs)


class QuerySetCacheMixin:
    """查询集缓存混入类"""

    @classmethod
    def get_cached_queryset(cls, cache_key: str, queryset_func: Callable, timeout: Optional[int] = None) -> Any:
        """获取缓存的查询集"""
        return cache_service.get_or_set(cache_key, queryset_func, timeout)

    @classmethod
    def get_cached_list(cls, cache_key: str, queryset_func: Callable, timeout: Optional[int] = None) -> List[Any]:
        """获取缓存的列表"""

        def list_func():
            return list(queryset_func())

        return cache_service.get_or_set(cache_key, list_func, timeout)

    @classmethod
    def get_cached_count(cls, cache_key: str, queryset_func: Callable, timeout: Optional[int] = None) -> int:
        """获取缓存的计数"""

        def count_func():
            return queryset_func().count()

        return cache_service.get_or_set(cache_key, count_func, timeout)

    @classmethod
    def clear_model_cache(cls) -> int:
        """清除模型相关缓存"""
        model_name = cls.__name__.lower()
        return cache_service.clear_model_cache(model_name)


# 缓存键生成器
class CacheKeyGenerator:
    """缓存键生成器"""

    @staticmethod
    def user_key(user_id: int, suffix: str = "") -> str:
        """用户相关缓存键"""
        key_parts = ["user", user_id]
        if suffix:
            key_parts.append(suffix)
        return "_".join(key_parts)

    @staticmethod
    def model_key(model_name: str, instance_id: int, suffix: str = "") -> str:
        """模型实例缓存键"""
        key_parts = [model_name, instance_id]
        if suffix:
            key_parts.append(suffix)
        return "_".join(key_parts)

    @staticmethod
    def query_key(model_name: str, filters: Dict[str, Any], suffix: str = "") -> str:
        """查询缓存键"""
        key_parts = [model_name, "query"]

        # 添加过滤条件
        for key, value in sorted(filters.items()):
            key_parts.append(f"{key}:{value}")

        if suffix:
            key_parts.append(suffix)

        return "_".join(key_parts)

    @staticmethod
    def function_key(func_name: str, *args, **kwargs) -> str:
        """函数缓存键"""
        key_parts = ["func", func_name]

        # 添加参数
        for arg in args:
            key_parts.append(str(arg))
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")

        return "_".join(key_parts)


# 缓存管理工具
class CacheManager:
    """缓存管理器"""

    @staticmethod
    def warm_up_cache():
        """预热缓存"""
        try:
            from ..models import LifeDiaryEntry, LifeGoal

            # 预热常用查询
            logger.info("开始预热缓存...")

            # 预热日记统计
            for user in LifeDiaryEntry.objects.values_list("user_id", flat=True).distinct():
                cache_key = CacheKeyGenerator.user_key(user, "diary_stats_30")
                cache_service.get_or_set(cache_key, lambda: LifeDiaryEntry.get_user_diary_stats(user, 30))

            # 预热目标统计
            for user in LifeGoal.objects.values_list("user_id", flat=True).distinct():
                cache_key = CacheKeyGenerator.user_key(user, "goals_summary")
                cache_service.get_or_set(cache_key, lambda: LifeGoal.get_user_goals_summary(user))

            logger.info("缓存预热完成")

        except Exception as e:
            logger.error(f"缓存预热失败: {e}")

    @staticmethod
    def clear_expired_cache():
        """清理过期缓存"""
        try:
            # 这里需要根据具体的缓存后端实现
            # 对于Redis，可以设置过期时间自动清理
            logger.info("清理过期缓存...")

        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")

    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """获取缓存信息"""
        try:
            stats = cache_service.get_stats()
            return {
                "stats": stats,
                "backend": getattr(settings, "CACHE_BACKEND", "unknown"),
                "location": getattr(settings, "CACHES", {}).get("default", {}).get("LOCATION", "unknown"),
            }
        except Exception as e:
            logger.error(f"获取缓存信息失败: {e}")
            return {}


# 导出主要类和函数
__all__ = [
    "CacheService",
    "cache_service",
    "cached",
    "cache_invalidate",
    "ModelCacheMixin",
    "QuerySetCacheMixin",
    "CacheKeyGenerator",
    "CacheManager",
]
