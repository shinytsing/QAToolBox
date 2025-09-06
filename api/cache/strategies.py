from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from functools import wraps
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

class CacheStrategy:
    """缓存策略基类"""
    
    def __init__(self, timeout=300, key_prefix=''):
        self.timeout = timeout
        self.key_prefix = key_prefix
    
    def get_cache_key(self, *args, **kwargs):
        """生成缓存键"""
        key_data = {
            'args': args,
            'kwargs': kwargs,
            'prefix': self.key_prefix
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key):
        """获取缓存"""
        return cache.get(key)
    
    def set(self, key, value, timeout=None):
        """设置缓存"""
        timeout = timeout or self.timeout
        cache.set(key, value, timeout)
    
    def delete(self, key):
        """删除缓存"""
        cache.delete(key)
    
    def clear_pattern(self, pattern):
        """清除匹配模式的缓存"""
        # 这里需要根据使用的缓存后端实现
        pass

class UserDataCache(CacheStrategy):
    """用户数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=600, key_prefix='user_data')
    
    def get_user_profile(self, user_id):
        """获取用户资料缓存"""
        key = f"{self.key_prefix}:profile:{user_id}"
        return self.get(key)
    
    def set_user_profile(self, user_id, profile_data):
        """设置用户资料缓存"""
        key = f"{self.key_prefix}:profile:{user_id}"
        self.set(key, profile_data)
    
    def invalidate_user_profile(self, user_id):
        """失效用户资料缓存"""
        key = f"{self.key_prefix}:profile:{user_id}"
        self.delete(key)

class FitnessDataCache(CacheStrategy):
    """健身数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=300, key_prefix='fitness')
    
    def get_workout_stats(self, user_id, date_range):
        """获取训练统计缓存"""
        key = f"{self.key_prefix}:stats:{user_id}:{date_range}"
        return self.get(key)
    
    def set_workout_stats(self, user_id, date_range, stats_data):
        """设置训练统计缓存"""
        key = f"{self.key_prefix}:stats:{user_id}:{date_range}"
        self.set(key, stats_data)
    
    def get_recent_workouts(self, user_id, limit=10):
        """获取最近训练缓存"""
        key = f"{self.key_prefix}:recent:{user_id}:{limit}"
        return self.get(key)
    
    def set_recent_workouts(self, user_id, workouts_data, limit=10):
        """设置最近训练缓存"""
        key = f"{self.key_prefix}:recent:{user_id}:{limit}"
        self.set(key, workouts_data)
    
    def invalidate_user_fitness(self, user_id):
        """失效用户健身数据缓存"""
        patterns = [
            f"{self.key_prefix}:stats:{user_id}:*",
            f"{self.key_prefix}:recent:{user_id}:*",
            f"{self.key_prefix}:achievements:{user_id}",
        ]
        for pattern in patterns:
            self.clear_pattern(pattern)

class LifeDataCache(CacheStrategy):
    """生活数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=1800, key_prefix='life')
    
    def get_diary_list(self, user_id, page=1, page_size=20):
        """获取日记列表缓存"""
        key = f"{self.key_prefix}:diary:{user_id}:{page}:{page_size}"
        return self.get(key)
    
    def set_diary_list(self, user_id, page, page_size, diary_data):
        """设置日记列表缓存"""
        key = f"{self.key_prefix}:diary:{user_id}:{page}:{page_size}"
        self.set(key, diary_data)
    
    def get_checkin_stats(self, user_id, month):
        """获取签到统计缓存"""
        key = f"{self.key_prefix}:checkin:{user_id}:{month}"
        return self.get(key)
    
    def set_checkin_stats(self, user_id, month, stats_data):
        """设置签到统计缓存"""
        key = f"{self.key_prefix}:checkin:{user_id}:{month}"
        self.set(key, stats_data)
    
    def invalidate_user_life(self, user_id):
        """失效用户生活数据缓存"""
        patterns = [
            f"{self.key_prefix}:diary:{user_id}:*",
            f"{self.key_prefix}:checkin:{user_id}:*",
            f"{self.key_prefix}:meditation:{user_id}",
        ]
        for pattern in patterns:
            self.clear_pattern(pattern)

class SocialDataCache(CacheStrategy):
    """社交数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=600, key_prefix='social')
    
    def get_chat_messages(self, room_id, page=1, page_size=50):
        """获取聊天消息缓存"""
        key = f"{self.key_prefix}:chat:{room_id}:{page}:{page_size}"
        return self.get(key)
    
    def set_chat_messages(self, room_id, page, page_size, messages_data):
        """设置聊天消息缓存"""
        key = f"{self.key_prefix}:chat:{room_id}:{page}:{page_size}"
        self.set(key, messages_data)
    
    def get_heart_links(self, user_id, status='active'):
        """获取心链缓存"""
        key = f"{self.key_prefix}:heart_links:{user_id}:{status}"
        return self.get(key)
    
    def set_heart_links(self, user_id, status, links_data):
        """设置心链缓存"""
        key = f"{self.key_prefix}:heart_links:{user_id}:{status}"
        self.set(key, links_data)
    
    def invalidate_user_social(self, user_id):
        """失效用户社交数据缓存"""
        patterns = [
            f"{self.key_prefix}:chat:*",
            f"{self.key_prefix}:heart_links:{user_id}:*",
            f"{self.key_prefix}:tarot:{user_id}",
        ]
        for pattern in patterns:
            self.clear_pattern(pattern)

class GeekDataCache(CacheStrategy):
    """极客工具数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=3600, key_prefix='geek')
    
    def get_tool_result(self, tool_type, input_hash):
        """获取工具结果缓存"""
        key = f"{self.key_prefix}:tool:{tool_type}:{input_hash}"
        return self.get(key)
    
    def set_tool_result(self, tool_type, input_hash, result_data):
        """设置工具结果缓存"""
        key = f"{self.key_prefix}:tool:{tool_type}:{input_hash}"
        self.set(key, result_data)
    
    def get_user_tools(self, user_id, tool_type=None):
        """获取用户工具使用记录缓存"""
        key = f"{self.key_prefix}:user_tools:{user_id}:{tool_type or 'all'}"
        return self.get(key)
    
    def set_user_tools(self, user_id, tool_type, tools_data):
        """设置用户工具使用记录缓存"""
        key = f"{self.key_prefix}:user_tools:{user_id}:{tool_type or 'all'}"
        self.set(key, tools_data)
    
    def invalidate_user_geek(self, user_id):
        """失效用户极客工具数据缓存"""
        patterns = [
            f"{self.key_prefix}:user_tools:{user_id}:*",
        ]
        for pattern in patterns:
            self.clear_pattern(pattern)

class SystemCache(CacheStrategy):
    """系统数据缓存策略"""
    
    def __init__(self):
        super().__init__(timeout=7200, key_prefix='system')
    
    def get_system_stats(self):
        """获取系统统计缓存"""
        key = f"{self.key_prefix}:stats"
        return self.get(key)
    
    def set_system_stats(self, stats_data):
        """设置系统统计缓存"""
        key = f"{self.key_prefix}:stats"
        self.set(key, stats_data)
    
    def get_feature_flags(self):
        """获取功能开关缓存"""
        key = f"{self.key_prefix}:features"
        return self.get(key)
    
    def set_feature_flags(self, features_data):
        """设置功能开关缓存"""
        key = f"{self.key_prefix}:features"
        self.set(key, features_data)
    
    def invalidate_system_cache(self):
        """失效系统缓存"""
        patterns = [
            f"{self.key_prefix}:stats",
            f"{self.key_prefix}:features",
            f"{self.key_prefix}:config",
        ]
        for pattern in patterns:
            self.clear_pattern(pattern)

# 缓存装饰器
def cache_result(cache_strategy: CacheStrategy, timeout=None):
    """缓存结果装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = cache_strategy.get_cache_key(func.__name__, *args, **kwargs)
            
            # 尝试从缓存获取
            cached_result = cache_strategy.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}: {cache_key}")
                return cached_result
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache_strategy.set(cache_key, result, timeout)
            logger.debug(f"Cache set for {func.__name__}: {cache_key}")
            
            return result
        return wrapper
    return decorator

def cache_invalidate(cache_strategy: CacheStrategy, pattern=None):
    """缓存失效装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # 失效相关缓存
            if pattern:
                cache_strategy.clear_pattern(pattern)
            else:
                # 默认失效所有相关缓存
                cache_strategy.invalidate_user_data(args[0].user.id)
            
            return result
        return wrapper
    return decorator

# 缓存管理器
class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.user_cache = UserDataCache()
        self.fitness_cache = FitnessDataCache()
        self.life_cache = LifeDataCache()
        self.social_cache = SocialDataCache()
        self.geek_cache = GeekDataCache()
        self.system_cache = SystemCache()
    
    def invalidate_user_cache(self, user_id):
        """失效用户所有缓存"""
        self.user_cache.invalidate_user_profile(user_id)
        self.fitness_cache.invalidate_user_fitness(user_id)
        self.life_cache.invalidate_user_life(user_id)
        self.social_cache.invalidate_user_social(user_id)
        self.geek_cache.invalidate_user_geek(user_id)
    
    def clear_all_cache(self):
        """清除所有缓存"""
        cache.clear()
    
    def get_cache_stats(self):
        """获取缓存统计"""
        # 这里需要根据使用的缓存后端实现
        return {
            'total_keys': 0,
            'memory_usage': 0,
            'hit_rate': 0
        }

# 全局缓存管理器实例
cache_manager = CacheManager()
