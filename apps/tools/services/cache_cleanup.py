"""
缓存清理服务
定期清理过期和无效的缓存数据
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheCleanupService:
    """缓存清理服务"""

    def __init__(self):
        self.cleanup_config = {
            "max_memory_mb": 512,  # 最大内存使用（MB）
            "cleanup_patterns": ["session:*", "cache:*", "temp:*", "test:*", "debug:*"],
            "preserve_patterns": ["user:*", "settings:*", "config:*"],
        }

    def cleanup_cache(self) -> Dict[str, Any]:
        """清理缓存"""
        try:
            results = {}

            # 清理过期缓存
            results["expired"] = self._cleanup_expired_cache()

            # 清理模式匹配的缓存
            results["pattern"] = self._cleanup_pattern_cache()

            # 清理内存使用
            results["memory"] = self._cleanup_memory_cache()

            # 获取缓存统计
            results["stats"] = self._get_cache_stats()

            logger.info("缓存清理完成")
            return {"status": "success", "results": results, "timestamp": datetime.now()}

        except Exception as e:
            logger.error(f"缓存清理失败: {e}")
            return {"status": "error", "message": str(e), "timestamp": datetime.now()}

    def _cleanup_expired_cache(self) -> Dict[str, Any]:
        """清理过期缓存"""
        try:
            # Django缓存会自动清理过期数据
            # 这里主要处理Redis等外部缓存的过期清理
            if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                cache_backend = settings.CACHES["default"]["BACKEND"]

                if "redis" in cache_backend.lower():
                    return self._cleanup_redis_expired()
                else:
                    return {"status": "auto_cleanup", "message": "Django自动清理"}

            return {"status": "no_cache_config"}

        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            return {"status": "error", "message": str(e)}

    def _cleanup_redis_expired(self) -> Dict[str, Any]:
        """清理Redis过期缓存"""
        try:
            import redis

            redis_url = settings.CACHES["default"]["LOCATION"]
            redis_client = redis.from_url(redis_url)

            # 获取所有键
            all_keys = redis_client.keys("*")
            expired_keys = []

            for key in all_keys:
                # 检查键是否过期
                if redis_client.ttl(key) == -1:  # 没有设置过期时间
                    # 检查键的最后访问时间
                    last_access = redis_client.object("idletime", key)
                    if last_access and last_access > 3600:  # 1小时未访问
                        expired_keys.append(key)

            # 删除过期键
            if expired_keys:
                deleted_count = redis_client.delete(*expired_keys)
                return {"status": "cleaned", "deleted_keys": deleted_count, "total_keys": len(all_keys)}
            else:
                return {"status": "no_expired_keys", "total_keys": len(all_keys)}

        except Exception as e:
            logger.error(f"清理Redis缓存失败: {e}")
            return {"status": "error", "message": str(e)}

    def _cleanup_pattern_cache(self) -> Dict[str, Any]:
        """清理模式匹配的缓存"""
        try:
            deleted_count = 0

            for pattern in self.cleanup_config["cleanup_patterns"]:
                try:
                    # 获取匹配的键
                    if hasattr(cache, "_cache") and hasattr(cache._cache, "keys"):
                        # Redis缓存
                        matching_keys = cache._cache.keys(pattern)
                        if matching_keys:
                            cache.delete_many(matching_keys)
                            deleted_count += len(matching_keys)
                    else:
                        # 其他缓存后端
                        # 这里可以实现其他缓存后端的清理逻辑
                        pass

                except Exception as e:
                    logger.warning(f"清理模式 {pattern} 失败: {e}")

            return {"status": "cleaned", "deleted_count": deleted_count, "patterns": self.cleanup_config["cleanup_patterns"]}

        except Exception as e:
            logger.error(f"清理模式缓存失败: {e}")
            return {"status": "error", "message": str(e)}

    def _cleanup_memory_cache(self) -> Dict[str, Any]:
        """清理内存缓存"""
        try:
            # 获取当前内存使用情况
            memory_usage = self._get_memory_usage()

            if memory_usage["used_mb"] > self.cleanup_config["max_memory_mb"]:
                # 内存使用超过限制，清理一些缓存
                cleared_keys = self._clear_oldest_cache()

                return {
                    "status": "memory_cleaned",
                    "before_mb": memory_usage["used_mb"],
                    "after_mb": self._get_memory_usage()["used_mb"],
                    "cleared_keys": cleared_keys,
                }
            else:
                return {
                    "status": "no_cleanup_needed",
                    "used_mb": memory_usage["used_mb"],
                    "max_mb": self.cleanup_config["max_memory_mb"],
                }

        except Exception as e:
            logger.error(f"清理内存缓存失败: {e}")
            return {"status": "error", "message": str(e)}

    def _get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        try:
            if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                cache_backend = settings.CACHES["default"]["BACKEND"]

                if "redis" in cache_backend.lower():
                    import redis

                    redis_url = settings.CACHES["default"]["LOCATION"]
                    redis_client = redis.from_url(redis_url)

                    info = redis_client.info("memory")
                    used_memory = info.get("used_memory", 0)

                    return {"used_mb": round(used_memory / (1024 * 1024), 2), "used_bytes": used_memory}

            return {"used_mb": 0, "used_bytes": 0}

        except Exception as e:
            logger.error(f"获取内存使用情况失败: {e}")
            return {"used_mb": 0, "used_bytes": 0}

    def _clear_oldest_cache(self) -> int:
        """清理最旧的缓存"""
        try:
            if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                cache_backend = settings.CACHES["default"]["BACKEND"]

                if "redis" in cache_backend.lower():
                    import redis

                    redis_url = settings.CACHES["default"]["LOCATION"]
                    redis_client = redis.from_url(redis_url)

                    # 获取所有键及其最后访问时间
                    all_keys = redis_client.keys("*")
                    key_times = []

                    for key in all_keys:
                        last_access = redis_client.object("idletime", key)
                        if last_access:
                            key_times.append((key, last_access))

                    # 按最后访问时间排序，删除最旧的20%
                    key_times.sort(key=lambda x: x[1], reverse=True)
                    keys_to_delete = key_times[: len(key_times) // 5]

                    if keys_to_delete:
                        keys = [k[0] for k in keys_to_delete]
                        deleted_count = redis_client.delete(*keys)
                        return deleted_count

            return 0

        except Exception as e:
            logger.error(f"清理最旧缓存失败: {e}")
            return 0

    def _get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            stats = {}

            if hasattr(settings, "CACHES") and "default" in settings.CACHES:
                cache_backend = settings.CACHES["default"]["BACKEND"]

                if "redis" in cache_backend.lower():
                    import redis

                    redis_url = settings.CACHES["default"]["LOCATION"]
                    redis_client = redis.from_url(redis_url)

                    info = redis_client.info()
                    keyspace = redis_client.info("keyspace")

                    stats = {
                        "backend": "redis",
                        "total_keys": sum(int(db.split("=")[1]) for db in keyspace.get("db0", "").split(",") if "keys=" in db),
                        "memory_usage_mb": round(info.get("used_memory", 0) / (1024 * 1024), 2),
                        "hit_rate": info.get("keyspace_hits", 0) / max(info.get("keyspace_misses", 1), 1),
                        "connected_clients": info.get("connected_clients", 0),
                        "uptime_seconds": info.get("uptime_in_seconds", 0),
                    }
                else:
                    stats = {"backend": cache_backend, "status": "unknown"}

            return stats

        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {e}")
            return {"error": str(e)}

    def clear_all_cache(self) -> Dict[str, Any]:
        """清理所有缓存"""
        try:
            cache.clear()

            return {"status": "success", "message": "所有缓存已清理", "timestamp": datetime.now()}

        except Exception as e:
            logger.error(f"清理所有缓存失败: {e}")
            return {"status": "error", "message": str(e), "timestamp": datetime.now()}

    def clear_pattern_cache(self, pattern: str) -> Dict[str, Any]:
        """清理指定模式的缓存"""
        try:
            if hasattr(cache, "_cache") and hasattr(cache._cache, "keys"):
                # Redis缓存
                matching_keys = cache._cache.keys(pattern)
                if matching_keys:
                    cache.delete_many(matching_keys)
                    return {"status": "success", "deleted_keys": len(matching_keys), "pattern": pattern}
                else:
                    return {"status": "no_matches", "pattern": pattern}
            else:
                return {"status": "not_supported", "message": "当前缓存后端不支持模式清理"}

        except Exception as e:
            logger.error(f"清理模式缓存失败 {pattern}: {e}")
            return {"status": "error", "message": str(e), "pattern": pattern}


# 全局实例
cache_cleanup_service = CacheCleanupService()


# 清理函数
def cleanup_cache() -> Dict[str, Any]:
    """清理缓存"""
    return cache_cleanup_service.cleanup_cache()


# 清理所有缓存
def clear_all_cache() -> Dict[str, Any]:
    """清理所有缓存"""
    return cache_cleanup_service.clear_all_cache()


# 清理模式缓存
def clear_pattern_cache(pattern: str) -> Dict[str, Any]:
    """清理指定模式的缓存"""
    return cache_cleanup_service.clear_pattern_cache(pattern)


# 获取统计信息
def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return cache_cleanup_service._get_cache_stats()
