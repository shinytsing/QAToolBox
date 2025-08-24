"""
健康检查视图
用于监控应用状态
"""

from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
import logging
import time

logger = logging.getLogger(__name__)


class HealthCheckView(View):
    """基础健康检查"""
    
    def get(self, request):
        """简单的健康检查"""
        return JsonResponse({
            'status': 'healthy',
            'timestamp': int(time.time()),
            'version': '2.0'
        })


class DetailedHealthCheckView(View):
    """详细健康检查"""
    
    def get(self, request):
        """详细的健康检查，包括数据库和缓存"""
        health_data = {
            'status': 'healthy',
            'timestamp': int(time.time()),
            'version': '2.0',
            'checks': {}
        }
        
        # 检查数据库
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
            health_data['checks']['database'] = 'healthy'
        except Exception as e:
            health_data['checks']['database'] = 'unhealthy'
            health_data['status'] = 'unhealthy'
            logger.error(f"Database health check failed: {e}")
        
        # 检查缓存
        try:
            cache.set('health_check', 'test', 30)
            if cache.get('health_check') == 'test':
                health_data['checks']['cache'] = 'healthy'
            else:
                health_data['checks']['cache'] = 'unhealthy'
                health_data['status'] = 'degraded'
        except Exception as e:
            health_data['checks']['cache'] = 'unhealthy'
            health_data['status'] = 'degraded'
            logger.error(f"Cache health check failed: {e}")
        
        return JsonResponse(health_data)