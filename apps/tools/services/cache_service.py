#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存服务
提供统一的缓存操作接口
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder


class CacheService:
    """缓存服务类"""

    # 缓存前缀
    PREFIXES = {
        "user": "user",
        "chat_room": "chat_room",
        "chat_message": "chat_message",
        "time_capsule": "time_capsule",
        "heart_link": "heart_link",
        "stats": "stats",
        "api": "api",
    }

    # 默认过期时间（秒）
    DEFAULT_TIMEOUTS = {
        "user": 3600,  # 1小时
        "chat_room": 1800,  # 30分钟
        "chat_message": 900,  # 15分钟
        "time_capsule": 7200,  # 2小时
        "heart_link": 1800,  # 30分钟
        "stats": 300,  # 5分钟
        "api": 600,  # 10分钟
    }

    @classmethod
    def _generate_key(cls, prefix: str, identifier: str, suffix: str = "") -> str:
        """生成缓存键"""
        key_parts = [cls.PREFIXES.get(prefix, prefix), str(identifier)]
        if suffix:
            key_parts.append(suffix)
        return ":".join(key_parts)

    @classmethod
    def _serialize_data(cls, data: Any) -> str:
        """序列化数据"""
        if isinstance(data, (dict, list)):
            return json.dumps(data, cls=DjangoJSONEncoder)
        return str(data)

    @classmethod
    def _deserialize_data(cls, data: str) -> Any:
        """反序列化数据"""
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            return data

    @classmethod
    def set(cls, prefix: str, identifier: str, data: Any, timeout: Optional[int] = None, suffix: str = "") -> bool:
        """设置缓存"""
        key = cls._generate_key(prefix, identifier, suffix)
        timeout = timeout or cls.DEFAULT_TIMEOUTS.get(prefix, 300)

        try:
            serialized_data = cls._serialize_data(data)
            return cache.set(key, serialized_data, timeout)
        except Exception as e:
            print(f"缓存设置失败: {e}")
            return False

    @classmethod
    def get(cls, prefix: str, identifier: str, suffix: str = "") -> Any:
        """获取缓存"""
        key = cls._generate_key(prefix, identifier, suffix)

        try:
            data = cache.get(key)
            if data is not None:
                return cls._deserialize_data(data)
            return None
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return None

    @classmethod
    def delete(cls, prefix: str, identifier: str, suffix: str = "") -> bool:
        """删除缓存"""
        key = cls._generate_key(prefix, identifier, suffix)

        try:
            return cache.delete(key)
        except Exception as e:
            print(f"缓存删除失败: {e}")
            return False

    @classmethod
    def exists(cls, prefix: str, identifier: str, suffix: str = "") -> bool:
        """检查缓存是否存在"""
        key = cls._generate_key(prefix, identifier, suffix)

        try:
            return cache.get(key) is not None
        except Exception as e:
            print(f"缓存检查失败: {e}")
            return False

    @classmethod
    def expire(cls, prefix: str, identifier: str, timeout: int, suffix: str = "") -> bool:
        """设置缓存过期时间"""
        key = cls._generate_key(prefix, identifier, suffix)

        try:
            return cache.touch(key, timeout)
        except Exception as e:
            print(f"缓存过期设置失败: {e}")
            return False

    @classmethod
    def clear_pattern(cls, pattern: str) -> int:
        """清除匹配模式的缓存"""
        try:
            # 这里需要根据具体的缓存后端实现
            # Redis支持模式删除，其他后端可能需要遍历
            if hasattr(cache, "delete_pattern"):
                return cache.delete_pattern(pattern)
            else:
                # 对于不支持模式删除的缓存后端，返回0
                return 0
        except Exception as e:
            print(f"模式缓存清除失败: {e}")
            return 0

    @classmethod
    def clear_prefix(cls, prefix: str) -> int:
        """清除指定前缀的所有缓存"""
        pattern = f"{cls.PREFIXES.get(prefix, prefix)}:*"
        return cls.clear_pattern(pattern)


class UserCacheService(CacheService):
    """用户缓存服务"""

    @classmethod
    def cache_user_profile(cls, user_id: int, profile_data: Dict) -> bool:
        """缓存用户资料"""
        return cls.set("user", user_id, profile_data, timeout=3600)

    @classmethod
    def get_user_profile(cls, user_id: int) -> Optional[Dict]:
        """获取用户资料缓存"""
        return cls.get("user", user_id)

    @classmethod
    def cache_user_stats(cls, user_id: int, stats_data: Dict) -> bool:
        """缓存用户统计信息"""
        return cls.set("user", user_id, stats_data, timeout=1800, suffix="stats")

    @classmethod
    def get_user_stats(cls, user_id: int) -> Optional[Dict]:
        """获取用户统计信息缓存"""
        return cls.get("user", user_id, suffix="stats")

    @classmethod
    def clear_user_cache(cls, user_id: int) -> bool:
        """清除用户相关缓存"""
        cls.delete("user", user_id)
        cls.delete("user", user_id, suffix="stats")
        return True


class ChatCacheService(CacheService):
    """聊天缓存服务"""

    @classmethod
    def cache_chat_room(cls, room_id: str, room_data: Dict) -> bool:
        """缓存聊天室信息"""
        return cls.set("chat_room", room_id, room_data, timeout=1800)

    @classmethod
    def get_chat_room(cls, room_id: str) -> Optional[Dict]:
        """获取聊天室缓存"""
        return cls.get("chat_room", room_id)

    @classmethod
    def cache_chat_messages(cls, room_id: str, messages: List[Dict]) -> bool:
        """缓存聊天消息"""
        return cls.set("chat_message", room_id, messages, timeout=900)

    @classmethod
    def get_chat_messages(cls, room_id: str) -> Optional[List[Dict]]:
        """获取聊天消息缓存"""
        return cls.get("chat_message", room_id)

    @classmethod
    def cache_active_rooms(cls, user_id: int, rooms: List[Dict]) -> bool:
        """缓存用户活跃聊天室"""
        return cls.set("chat_room", user_id, rooms, timeout=600, suffix="active")

    @classmethod
    def get_active_rooms(cls, user_id: int) -> Optional[List[Dict]]:
        """获取用户活跃聊天室缓存"""
        return cls.get("chat_room", user_id, suffix="active")

    @classmethod
    def clear_chat_cache(cls, room_id: str) -> bool:
        """清除聊天相关缓存"""
        cls.delete("chat_room", room_id)
        cls.delete("chat_message", room_id)
        return True


class TimeCapsuleCacheService(CacheService):
    """时光胶囊缓存服务"""

    @classmethod
    def cache_capsule(cls, capsule_id: int, capsule_data: Dict) -> bool:
        """缓存时光胶囊"""
        return cls.set("time_capsule", capsule_id, capsule_data, timeout=7200)

    @classmethod
    def get_capsule(cls, capsule_id: int) -> Optional[Dict]:
        """获取时光胶囊缓存"""
        return cls.get("time_capsule", capsule_id)

    @classmethod
    def cache_user_capsules(cls, user_id: int, capsules: List[Dict]) -> bool:
        """缓存用户时光胶囊列表"""
        return cls.set("time_capsule", user_id, capsules, timeout=3600, suffix="list")

    @classmethod
    def get_user_capsules(cls, user_id: int) -> Optional[List[Dict]]:
        """获取用户时光胶囊列表缓存"""
        return cls.get("time_capsule", user_id, suffix="list")

    @classmethod
    def cache_public_capsules(cls, capsules: List[Dict]) -> bool:
        """缓存公开时光胶囊列表"""
        return cls.set("time_capsule", "public", capsules, timeout=1800, suffix="list")

    @classmethod
    def get_public_capsules(cls) -> Optional[List[Dict]]:
        """获取公开时光胶囊列表缓存"""
        return cls.get("time_capsule", "public", suffix="list")


class StatsCacheService(CacheService):
    """统计缓存服务"""

    @classmethod
    def cache_user_stats(cls, user_id: int, stats: Dict) -> bool:
        """缓存用户统计"""
        return cls.set("stats", user_id, stats, timeout=300)

    @classmethod
    def get_user_stats(cls, user_id: int) -> Optional[Dict]:
        """获取用户统计缓存"""
        return cls.get("stats", user_id)

    @classmethod
    def cache_global_stats(cls, stats: Dict) -> bool:
        """缓存全局统计"""
        return cls.set("stats", "global", stats, timeout=300)

    @classmethod
    def get_global_stats(cls) -> Optional[Dict]:
        """获取全局统计缓存"""
        return cls.get("stats", "global")

    @classmethod
    def cache_daily_stats(cls, date: str, stats: Dict) -> bool:
        """缓存每日统计"""
        return cls.set("stats", date, stats, timeout=3600, suffix="daily")

    @classmethod
    def get_daily_stats(cls, date: str) -> Optional[Dict]:
        """获取每日统计缓存"""
        return cls.get("stats", date, suffix="daily")


class APICacheService(CacheService):
    """API缓存服务"""

    @classmethod
    def cache_api_response(cls, endpoint: str, params: Dict, response: Any) -> bool:
        """缓存API响应"""
        # 生成参数哈希作为缓存键的一部分
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode(), usedforsecurity=False).hexdigest()
        return cls.set("api", endpoint, response, timeout=600, suffix=params_hash)

    @classmethod
    def get_api_response(cls, endpoint: str, params: Dict) -> Any:
        """获取API响应缓存"""
        params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode(), usedforsecurity=False).hexdigest()
        return cls.get("api", endpoint, suffix=params_hash)

    @classmethod
    def clear_api_cache(cls, endpoint: str = None) -> bool:
        """清除API缓存"""
        if endpoint:
            return cls.clear_pattern(f"api:{endpoint}:*")
        else:
            return cls.clear_prefix("api")


# 缓存装饰器
def cache_result(prefix: str, timeout: Optional[int] = None, key_func=None):
    """缓存结果装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成键
                key_parts = [func.__name__] + [str(arg) for arg in args]
                cache_key = ":".join(key_parts)

            # 尝试从缓存获取
            cached_result = CacheService.get("api", cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            CacheService.set("api", cache_key, result, timeout)
            return result

        return wrapper

    return decorator


# 缓存管理工具
class CacheManager:
    """缓存管理器"""

    @classmethod
    def clear_all_cache(cls) -> Dict[str, int]:
        """清除所有缓存"""
        results = {}
        for prefix in CacheService.PREFIXES.values():
            results[prefix] = CacheService.clear_prefix(prefix)
        return results

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            # 这里需要根据具体的缓存后端实现
            # Redis支持info命令，其他后端可能不支持
            if hasattr(cache, "client") and hasattr(cache.client, "info"):
                return cache.client.info()
            else:
                return {"status": "cache_stats_not_available"}
        except Exception as e:
            return {"error": str(e)}

    @classmethod
    def warm_up_cache(cls) -> Dict[str, bool]:
        """预热缓存"""
        results = {}

        # 预热全局统计
        try:
            from apps.tools.views import get_global_stats

            stats = get_global_stats()
            if stats:
                StatsCacheService.cache_global_stats(stats)
                results["global_stats"] = True
        except Exception as e:
            results["global_stats"] = False
            print(f"预热全局统计失败: {e}")

        return results
