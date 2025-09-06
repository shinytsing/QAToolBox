import logging
import traceback
import json
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

User = get_user_model()

class ErrorMonitor:
    """错误监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger('error_monitor')
        self.error_threshold = 10  # 错误阈值
        self.time_window = 300  # 时间窗口（秒）
        self.alert_recipients = getattr(settings, 'ERROR_ALERT_EMAILS', [])
        
        # 初始化Sentry
        self._init_sentry()
    
    def _init_sentry(self):
        """初始化Sentry错误监控"""
        if hasattr(settings, 'SENTRY_DSN'):
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    DjangoIntegration(),
                    CeleryIntegration(),
                    RedisIntegration(),
                ],
                traces_sample_rate=0.1,
                send_default_pii=True,
                environment=getattr(settings, 'ENVIRONMENT', 'development'),
            )
    
    def capture_exception(self, exception, request=None, user=None, extra_data=None):
        """捕获异常"""
        try:
            # 记录到Sentry
            with sentry_sdk.push_scope() as scope:
                if request:
                    scope.set_context("request", {
                        "url": request.build_absolute_uri(),
                        "method": request.method,
                        "headers": dict(request.META),
                        "data": getattr(request, 'data', {}),
                    })
                
                if user:
                    scope.set_user({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    })
                
                if extra_data:
                    scope.set_extra("extra_data", extra_data)
                
                sentry_sdk.capture_exception(exception)
            
            # 记录到本地日志
            self.logger.error(
                f"Exception captured: {str(exception)}",
                exc_info=True,
                extra={
                    'user_id': user.id if user else None,
                    'request_url': request.build_absolute_uri() if request else None,
                    'extra_data': extra_data,
                }
            )
            
            # 检查是否需要发送告警
            self._check_error_threshold()
            
        except Exception as e:
            self.logger.error(f"Failed to capture exception: {e}")
    
    def capture_message(self, message, level='info', request=None, user=None, extra_data=None):
        """捕获消息"""
        try:
            with sentry_sdk.push_scope() as scope:
                if request:
                    scope.set_context("request", {
                        "url": request.build_absolute_uri(),
                        "method": request.method,
                    })
                
                if user:
                    scope.set_user({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    })
                
                if extra_data:
                    scope.set_extra("extra_data", extra_data)
                
                sentry_sdk.capture_message(message, level=level)
            
            # 记录到本地日志
            getattr(self.logger, level.lower())(
                message,
                extra={
                    'user_id': user.id if user else None,
                    'request_url': request.build_absolute_uri() if request else None,
                    'extra_data': extra_data,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to capture message: {e}")
    
    def _check_error_threshold(self):
        """检查错误阈值"""
        try:
            current_time = timezone.now()
            time_key = f"error_count_{current_time.strftime('%Y%m%d%H%M')}"
            
            # 获取当前时间窗口的错误计数
            error_count = cache.get(time_key, 0) + 1
            cache.set(time_key, error_count, self.time_window)
            
            # 如果超过阈值，发送告警
            if error_count >= self.error_threshold:
                self._send_error_alert(error_count, current_time)
                
        except Exception as e:
            self.logger.error(f"Failed to check error threshold: {e}")
    
    def _send_error_alert(self, error_count, timestamp):
        """发送错误告警"""
        try:
            if not self.alert_recipients:
                return
            
            subject = f"🚨 错误告警 - {settings.SITE_NAME or 'QAToolBox'}"
            message = f"""
            系统检测到大量错误：
            
            错误数量: {error_count}
            时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}
            阈值: {self.error_threshold}
            时间窗口: {self.time_window}秒
            
            请立即检查系统状态！
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=self.alert_recipients,
                fail_silently=False,
            )
            
            self.logger.warning(f"Error alert sent: {error_count} errors in {self.time_window}s")
            
        except Exception as e:
            self.logger.error(f"Failed to send error alert: {e}")
    
    def get_error_stats(self, hours=24):
        """获取错误统计"""
        try:
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 从Sentry获取错误统计
            # 这里需要根据实际的Sentry API实现
            stats = {
                'total_errors': 0,
                'error_rate': 0.0,
                'top_errors': [],
                'error_trend': [],
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get error stats: {e}")
            return {}
    
    def get_system_health(self):
        """获取系统健康状态"""
        try:
            health = {
                'status': 'healthy',
                'timestamp': timezone.now().isoformat(),
                'checks': {}
            }
            
            # 检查数据库连接
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                health['checks']['database'] = 'healthy'
            except Exception as e:
                health['checks']['database'] = f'unhealthy: {str(e)}'
                health['status'] = 'unhealthy'
            
            # 检查缓存
            try:
                cache.set('health_check', 'ok', 10)
                if cache.get('health_check') == 'ok':
                    health['checks']['cache'] = 'healthy'
                else:
                    health['checks']['cache'] = 'unhealthy'
            except Exception as e:
                health['checks']['cache'] = f'unhealthy: {str(e)}'
                health['status'] = 'unhealthy'
            
            # 检查Redis
            try:
                from django.core.cache import cache
                cache.set('redis_check', 'ok', 10)
                if cache.get('redis_check') == 'ok':
                    health['checks']['redis'] = 'healthy'
                else:
                    health['checks']['redis'] = 'unhealthy'
            except Exception as e:
                health['checks']['redis'] = f'unhealthy: {str(e)}'
                health['status'] = 'unhealthy'
            
            return health
            
        except Exception as e:
            self.logger.error(f"Failed to get system health: {e}")
            return {
                'status': 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'error': str(e)
            }

class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance_monitor')
        self.performance_threshold = 2.0  # 性能阈值（秒）
        self.slow_query_threshold = 1.0  # 慢查询阈值（秒）
    
    def monitor_request(self, request, response, duration):
        """监控请求性能"""
        try:
            # 记录请求性能
            self.logger.info(
                f"Request performance: {request.method} {request.path} - {duration:.3f}s",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'status_code': response.status_code,
                    'user_id': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None,
                }
            )
            
            # 检查是否超过性能阈值
            if duration > self.performance_threshold:
                self._log_slow_request(request, response, duration)
            
            # 记录到Sentry
            sentry_sdk.add_breadcrumb(
                message=f"Request: {request.method} {request.path}",
                category="http",
                level="info",
                data={
                    "duration": duration,
                    "status_code": response.status_code,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to monitor request performance: {e}")
    
    def monitor_database_query(self, query, duration):
        """监控数据库查询性能"""
        try:
            if duration > self.slow_query_threshold:
                self.logger.warning(
                    f"Slow query detected: {duration:.3f}s - {query[:100]}...",
                    extra={
                        'query': query,
                        'duration': duration,
                    }
                )
                
                # 记录到Sentry
                sentry_sdk.add_breadcrumb(
                    message="Slow database query",
                    category="db",
                    level="warning",
                    data={
                        "query": query[:200],
                        "duration": duration,
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Failed to monitor database query: {e}")
    
    def _log_slow_request(self, request, response, duration):
        """记录慢请求"""
        try:
            self.logger.warning(
                f"Slow request: {request.method} {request.path} - {duration:.3f}s",
                extra={
                    'method': request.method,
                    'path': request.path,
                    'duration': duration,
                    'status_code': response.status_code,
                    'user_id': getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None,
                    'query_params': dict(request.GET),
                    'post_data': getattr(request, 'data', {}),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to log slow request: {e}")
    
    def get_performance_stats(self, hours=24):
        """获取性能统计"""
        try:
            # 这里需要从日志或监控系统中获取性能数据
            stats = {
                'avg_response_time': 0.0,
                'max_response_time': 0.0,
                'slow_requests': 0,
                'total_requests': 0,
                'performance_trend': [],
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get performance stats: {e}")
            return {}

class UserBehaviorMonitor:
    """用户行为监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger('user_behavior_monitor')
    
    def track_user_action(self, user, action, details=None):
        """跟踪用户行为"""
        try:
            self.logger.info(
                f"User action: {action}",
                extra={
                    'user_id': user.id,
                    'username': user.username,
                    'action': action,
                    'details': details,
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
            # 记录到Sentry
            sentry_sdk.add_breadcrumb(
                message=f"User action: {action}",
                category="user",
                level="info",
                data={
                    "user_id": user.id,
                    "username": user.username,
                    "action": action,
                    "details": details,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to track user action: {e}")
    
    def track_api_usage(self, user, endpoint, method, status_code, duration):
        """跟踪API使用情况"""
        try:
            self.logger.info(
                f"API usage: {method} {endpoint}",
                extra={
                    'user_id': user.id,
                    'username': user.username,
                    'endpoint': endpoint,
                    'method': method,
                    'status_code': status_code,
                    'duration': duration,
                    'timestamp': timezone.now().isoformat(),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to track API usage: {e}")
    
    def get_user_behavior_stats(self, user_id, days=7):
        """获取用户行为统计"""
        try:
            # 这里需要从日志或数据库中获取用户行为数据
            stats = {
                'total_actions': 0,
                'most_used_features': [],
                'activity_trend': [],
                'session_duration': 0,
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get user behavior stats: {e}")
            return {}

# 全局监控器实例
error_monitor = ErrorMonitor()
performance_monitor = PerformanceMonitor()
user_behavior_monitor = UserBehaviorMonitor()

# 中间件
class MonitoringMiddleware:
    """监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # 监控请求性能
        performance_monitor.monitor_request(request, response, duration)
        
        return response
    
    def process_exception(self, request, exception):
        """处理异常"""
        error_monitor.capture_exception(
            exception,
            request=request,
            user=getattr(request, 'user', None)
        )
        
        return None
