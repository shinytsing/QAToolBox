from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.db.models import Q, Count, Avg, Sum
from django.views import View
from django.utils.decorators import method_decorator
from functools import wraps
import json
import logging

logger = logging.getLogger(__name__)


def is_admin(user):
    """检查用户是否为管理员"""
    try:
        return user.role.role == 'admin'
    except:
        return False


def admin_required(view_func):
    """管理员权限装饰器"""
    decorated_view = user_passes_test(is_admin, login_url='/users/login/')(view_func)
    return decorated_view


class BaseView(View):
    """基础视图类，提供通用功能"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cache_timeout = 300  # 默认缓存5分钟
    
    def get_cache_key(self, prefix, *args, **kwargs):
        """生成缓存键"""
        key_parts = [prefix]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        return "_".join(key_parts)
    
    def get_cached_data(self, cache_key, data_func, timeout=None):
        """获取缓存数据，如果不存在则调用函数生成"""
        if timeout is None:
            timeout = self.cache_timeout
        
        data = cache.get(cache_key)
        if data is None:
            try:
                data = data_func()
                cache.set(cache_key, data, timeout)
            except Exception as e:
                logger.error(f"Error generating cached data for {cache_key}: {e}")
                return None
        
        return data
    
    def clear_user_cache(self, user_id, prefix=None):
        """清除用户相关缓存"""
        if prefix:
            pattern = f"{prefix}_{user_id}_*"
        else:
            pattern = f"*_{user_id}_*"
        
        # 这里需要根据具体的缓存后端实现清除逻辑
        # 对于Redis，可以使用scan和delete
        # 对于内存缓存，只能等待过期
        logger.info(f"Clearing cache pattern: {pattern}")
    
    def json_response(self, data, status=200, **kwargs):
        """返回JSON响应"""
        response_data = {
            'success': status < 400,
            'data': data,
            'timestamp': timezone.now().isoformat(),
            **kwargs
        }
        return JsonResponse(response_data, status=status)
    
    def error_response(self, message, status=400, **kwargs):
        """返回错误响应"""
        return self.json_response({
            'error': message,
            **kwargs
        }, status=status)
    
    def success_response(self, data, **kwargs):
        """返回成功响应"""
        return self.json_response(data, **kwargs)


class CachedViewMixin:
    """缓存视图混入类"""
    
    def get_cache_key(self, *args, **kwargs):
        """生成缓存键"""
        view_name = self.__class__.__name__
        user_id = getattr(self.request.user, 'id', 'anonymous')
        return f"{view_name}_{user_id}_{hash(str(args) + str(sorted(kwargs.items())))}"
    
    def get_cached_response(self, cache_key, response_func, timeout=300):
        """获取缓存的响应"""
        response_data = cache.get(cache_key)
        if response_data is None:
            response_data = response_func()
            cache.set(cache_key, response_data, timeout)
        return response_data


def cache_response(timeout=300, key_func=None):
    """缓存响应装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if key_func:
                cache_key = key_func(request, *args, **kwargs)
            else:
                cache_key = f"{view_func.__name__}_{request.user.id}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            response_data = cache.get(cache_key)
            if response_data is None:
                response_data = view_func(request, *args, **kwargs)
                cache.set(cache_key, response_data, timeout)
            
            return response_data
        return wrapper
    return decorator


def rate_limit(max_requests=100, window=3600):
    """速率限制装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_id = getattr(request.user, 'id', 'anonymous')
            cache_key = f"rate_limit_{view_func.__name__}_{user_id}"
            
            current_requests = cache.get(cache_key, 0)
            if current_requests >= max_requests:
                return JsonResponse({
                    'error': '请求过于频繁，请稍后再试',
                    'retry_after': window
                }, status=429)
            
            cache.set(cache_key, current_requests + 1, window)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def validate_request_data(required_fields=None, optional_fields=None):
    """请求数据验证装饰器"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST':
                try:
                    data = json.loads(request.body) if request.body else {}
                except json.JSONDecodeError:
                    return JsonResponse({'error': '无效的JSON数据'}, status=400)
                
                # 检查必需字段
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return JsonResponse({
                            'error': f'缺少必需字段: {", ".join(missing_fields)}'
                        }, status=400)
                
                # 验证字段类型和格式
                if optional_fields:
                    for field, field_type in optional_fields.items():
                        if field in data:
                            try:
                                if field_type == 'int':
                                    data[field] = int(data[field])
                                elif field_type == 'float':
                                    data[field] = float(data[field])
                                elif field_type == 'bool':
                                    data[field] = bool(data[field])
                            except (ValueError, TypeError):
                                return JsonResponse({
                                    'error': f'字段 {field} 格式错误'
                                }, status=400)
                
                request.validated_data = data
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class PaginationMixin:
    """分页混入类"""
    
    def get_paginated_data(self, queryset, page=1, page_size=20):
        """获取分页数据"""
        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            page = 1
            page_size = 20
        
        # 限制页面大小
        page_size = min(page_size, 100)
        page_size = max(page_size, 1)
        
        total_count = queryset.count()
        total_pages = (total_count + page_size - 1) // page_size
        
        start = (page - 1) * page_size
        end = start + page_size
        
        data = list(queryset[start:end])
        
        return {
            'data': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            }
        }


class SearchMixin:
    """搜索混入类"""
    
    def search_queryset(self, queryset, search_fields, search_term):
        """在指定字段中搜索"""
        if not search_term:
            return queryset
        
        q_objects = Q()
        for field in search_fields:
            q_objects |= Q(**{f"{field}__icontains": search_term})
        
        return queryset.filter(q_objects)


class FilterMixin:
    """过滤混入类"""
    
    def filter_queryset(self, queryset, filters):
        """根据过滤条件过滤查询集"""
        if not filters:
            return queryset
        
        for field, value in filters.items():
            if value is not None and value != '':
                if isinstance(value, (list, tuple)):
                    queryset = queryset.filter(**{f"{field}__in": value})
                else:
                    queryset = queryset.filter(**{field: value})
        
        return queryset


class OrderMixin:
    """排序混入类"""
    
    def order_queryset(self, queryset, order_by=None, allowed_fields=None):
        """排序查询集"""
        if not order_by:
            return queryset
        
        if allowed_fields and order_by not in allowed_fields:
            return queryset
        
        # 处理降序
        if order_by.startswith('-'):
            field = order_by[1:]
            if allowed_fields and field not in allowed_fields:
                return queryset
            return queryset.order_by(order_by)
        
        return queryset.order_by(order_by)


# 通用响应函数
def api_response(data=None, message="", status=200, **kwargs):
    """通用API响应函数"""
    response_data = {
        'success': status < 400,
        'message': message,
        'data': data,
        'timestamp': timezone.now().isoformat(),
        **kwargs
    }
    return JsonResponse(response_data, status=status)


def success_response(data=None, message="操作成功", **kwargs):
    """成功响应"""
    return api_response(data=data, message=message, status=200, **kwargs)


def error_response(message="操作失败", status=400, **kwargs):
    """错误响应"""
    return api_response(message=message, status=status, **kwargs)


def not_found_response(message="资源不存在"):
    """404响应"""
    return error_response(message=message, status=404)


def permission_denied_response(message="权限不足"):
    """403响应"""
    return error_response(message=message, status=403)


def validation_error_response(errors, message="数据验证失败"):
    """验证错误响应"""
    return error_response(message=message, status=400, errors=errors)
