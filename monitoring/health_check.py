import time
import psutil
import redis
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'cache': self.check_cache,
            'redis': self.check_redis,
            'disk': self.check_disk,
            'memory': self.check_memory,
            'cpu': self.check_cpu,
        }
    
    def check_database(self):
        """检查数据库连接"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {'status': 'healthy', 'message': 'Database connection OK'}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'Database error: {e}'}
    
    def check_cache(self):
        """检查缓存"""
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                return {'status': 'healthy', 'message': 'Cache OK'}
            else:
                return {'status': 'unhealthy', 'message': 'Cache not working'}
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'Cache error: {e}'}
    
    def check_redis(self):
        """检查Redis连接"""
        try:
            if hasattr(settings, 'REDIS_URL'):
                r = redis.from_url(settings.REDIS_URL)
                r.ping()
                return {'status': 'healthy', 'message': 'Redis connection OK'}
            else:
                return {'status': 'healthy', 'message': 'Redis not configured'}
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'Redis error: {e}'}
    
    def check_disk(self):
        """检查磁盘空间"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = disk_usage.percent
            if usage_percent < 90:
                return {
                    'status': 'healthy',
                    'message': f'Disk usage: {usage_percent:.1f}%',
                    'data': {'usage_percent': usage_percent}
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'High disk usage: {usage_percent:.1f}%',
                    'data': {'usage_percent': usage_percent}
                }
        except Exception as e:
            logger.error(f"Disk health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'Disk check error: {e}'}
    
    def check_memory(self):
        """检查内存使用"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            if usage_percent < 90:
                return {
                    'status': 'healthy',
                    'message': f'Memory usage: {usage_percent:.1f}%',
                    'data': {'usage_percent': usage_percent}
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'High memory usage: {usage_percent:.1f}%',
                    'data': {'usage_percent': usage_percent}
                }
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'Memory check error: {e}'}
    
    def check_cpu(self):
        """检查CPU使用"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                return {
                    'status': 'healthy',
                    'message': f'CPU usage: {cpu_percent:.1f}%',
                    'data': {'usage_percent': cpu_percent}
                }
            else:
                return {
                    'status': 'warning',
                    'message': f'High CPU usage: {cpu_percent:.1f}%',
                    'data': {'usage_percent': cpu_percent}
                }
        except Exception as e:
            logger.error(f"CPU health check failed: {e}")
            return {'status': 'unhealthy', 'message': f'CPU check error: {e}'}
    
    def run_all_checks(self):
        """运行所有健康检查"""
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in self.checks.items():
            start_time = time.time()
            try:
                result = check_func()
                result['response_time'] = round((time.time() - start_time) * 1000, 2)
                results[check_name] = result
                
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results[check_name] = {
                    'status': 'unhealthy',
                    'message': f'Check failed: {e}',
                    'response_time': round((time.time() - start_time) * 1000, 2)
                }
                overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': time.time(),
            'checks': results
        }


# 全局健康检查器实例
health_checker = HealthChecker()


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """健康检查端点"""
    try:
        results = health_checker.run_all_checks()
        
        # 根据整体状态设置HTTP状态码
        if results['status'] == 'healthy':
            status_code = 200
        elif results['status'] == 'warning':
            status_code = 200  # 警告仍然返回200
        else:
            status_code = 503  # 服务不可用
        
        return JsonResponse(results, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check endpoint failed: {e}")
        return JsonResponse({
            'status': 'unhealthy',
            'message': f'Health check failed: {e}',
            'timestamp': time.time()
        }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def health_check_simple(request):
    """简单健康检查端点"""
    try:
        # 只检查关键服务
        db_result = health_checker.check_database()
        cache_result = health_checker.check_cache()
        
        if db_result['status'] == 'healthy' and cache_result['status'] == 'healthy':
            return JsonResponse({'status': 'ok'}, status=200)
        else:
            return JsonResponse({'status': 'error'}, status=503)
            
    except Exception as e:
        logger.error(f"Simple health check failed: {e}")
        return JsonResponse({'status': 'error'}, status=503)
