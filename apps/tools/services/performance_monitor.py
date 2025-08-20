import time
import psutil
import logging
from django.core.cache import cache
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from typing import Dict, Any, List, Optional
import json
import threading
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
        self.cache_prefix = 'perf_monitor'
    
    def start_timer(self, operation: str) -> float:
        """开始计时"""
        return time.time()
    
    def end_timer(self, operation: str, start_time: float, **kwargs):
        """结束计时并记录指标"""
        duration = time.time() - start_time
        
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'times': [],
                    'last_updated': datetime.now(),
                    'metadata': {}
                }
            
            metric = self.metrics[operation]
            metric['count'] += 1
            metric['total_time'] += duration
            metric['min_time'] = min(metric['min_time'], duration)
            metric['max_time'] = max(metric['max_time'], duration)
            metric['times'].append(duration)
            metric['last_updated'] = datetime.now()
            
            # 限制历史记录数量
            if len(metric['times']) > 1000:
                metric['times'] = metric['times'][-1000:]
            
            # 添加元数据
            for key, value in kwargs.items():
                if key not in metric['metadata']:
                    metric['metadata'][key] = []
                metric['metadata'][key].append(value)
                
                # 限制元数据记录数量
                if len(metric['metadata'][key]) > 100:
                    metric['metadata'][key] = metric['metadata'][key][-100:]
    
    def get_metrics(self, operation: str = None) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            if operation:
                return self.metrics.get(operation, {})
            else:
                return self.metrics.copy()
    
    def get_statistics(self, operation: str) -> Dict[str, Any]:
        """获取统计信息"""
        metric = self.get_metrics(operation)
        if not metric or not metric['times']:
            return {}
        
        times = metric['times']
        return {
            'count': metric['count'],
            'total_time': metric['total_time'],
            'min_time': metric['min_time'],
            'max_time': metric['max_time'],
            'avg_time': metric['total_time'] / metric['count'],
            'median_time': statistics.median(times),
            'p95_time': statistics.quantiles(times, n=20)[18] if len(times) >= 20 else max(times),
            'p99_time': statistics.quantiles(times, n=100)[98] if len(times) >= 100 else max(times),
            'last_updated': metric['last_updated'].isoformat(),
        }
    
    def clear_metrics(self, operation: str = None):
        """清除指标"""
        with self.lock:
            if operation:
                self.metrics.pop(operation, None)
            else:
                self.metrics.clear()
    
    def save_to_cache(self):
        """保存指标到缓存"""
        try:
            cache.set(f"{self.cache_prefix}_metrics", self.metrics, 3600)  # 缓存1小时
        except Exception as e:
            logger.error(f"保存性能指标到缓存失败: {e}")
    
    def load_from_cache(self):
        """从缓存加载指标"""
        try:
            cached_metrics = cache.get(f"{self.cache_prefix}_metrics")
            if cached_metrics:
                with self.lock:
                    self.metrics.update(cached_metrics)
        except Exception as e:
            logger.error(f"从缓存加载性能指标失败: {e}")


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """性能监控装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = performance_monitor.start_timer(operation)
            try:
                result = func(*args, **kwargs)
                performance_monitor.end_timer(operation, start_time, status='success')
                return result
            except Exception as e:
                performance_monitor.end_timer(operation, start_time, status='error', error=str(e))
                raise
        return wrapper
    return decorator


class SystemMonitor:
    """系统监控器"""
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """获取系统信息"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free,
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100,
                },
                'network': SystemMonitor.get_network_info(),
                'timestamp': datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {}
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """获取网络信息"""
        try:
            network_io = psutil.net_io_counters()
            return {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv,
            }
        except Exception as e:
            logger.error(f"获取网络信息失败: {e}")
            return {}
    
    @staticmethod
    def get_process_info() -> Dict[str, Any]:
        """获取进程信息"""
        try:
            current_process = psutil.Process()
            return {
                'pid': current_process.pid,
                'name': current_process.name(),
                'cpu_percent': current_process.cpu_percent(),
                'memory_percent': current_process.memory_percent(),
                'memory_info': current_process.memory_info()._asdict(),
                'num_threads': current_process.num_threads(),
                'create_time': datetime.fromtimestamp(current_process.create_time()).isoformat(),
            }
        except Exception as e:
            logger.error(f"获取进程信息失败: {e}")
            return {}


class DatabaseMonitor:
    """数据库监控器"""
    
    @staticmethod
    def get_database_stats():
        """获取数据库统计信息"""
        try:
            from django.db import connection
            from django.db import connections
            
            stats = {}
            
            # 获取连接信息
            for alias in connections.databases:
                connection = connections[alias]
                stats[alias] = {
                    'connected': connection.connection is not None,
                    'autocommit': connection.autocommit,
                    'in_atomic_block': connection.in_atomic_block,
                }
            
            # 获取查询统计
            if hasattr(connection, 'queries'):
                queries = connection.queries
                stats['queries'] = {
                    'total_count': len(queries),
                    'total_time': sum(float(q['time']) for q in queries),
                    'slow_queries': [q for q in queries if float(q['time']) > 1.0],
                }
            
            return stats
        except Exception as e:
            logger.error(f"获取数据库统计信息失败: {e}")
            return {}


class CacheMonitor:
    """缓存监控器"""
    
    @staticmethod
    def get_cache_stats():
        """获取缓存统计信息"""
        try:
            # 这里需要根据具体的缓存后端实现
            # 对于Redis，可以获取更多信息
            stats = {
                'backend': cache.__class__.__name__,
                'test_key': 'cache_monitor_test',
            }
            
            # 测试缓存功能
            test_value = f"test_{datetime.now().timestamp()}"
            cache.set(stats['test_key'], test_value, 60)
            retrieved_value = cache.get(stats['test_key'])
            cache.delete(stats['test_key'])
            
            stats['working'] = retrieved_value == test_value
            
            return stats
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: {e}")
            return {'working': False, 'error': str(e)}


class PerformanceMonitorView(View):
    """性能监控视图"""
    
    @method_decorator(csrf_exempt)
    def get(self, request):
        """获取性能监控信息"""
        try:
            # 获取查询参数
            operation = request.GET.get('operation')
            include_system = request.GET.get('system', 'true').lower() == 'true'
            include_db = request.GET.get('database', 'true').lower() == 'true'
            include_cache = request.GET.get('cache', 'true').lower() == 'true'
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'performance_metrics': {},
            }
            
            # 获取性能指标
            if operation:
                result['performance_metrics'] = performance_monitor.get_statistics(operation)
            else:
                metrics = performance_monitor.get_metrics()
                result['performance_metrics'] = {
                    op: performance_monitor.get_statistics(op)
                    for op in metrics.keys()
                }
            
            # 获取系统信息
            if include_system:
                result['system_info'] = SystemMonitor.get_system_info()
                result['process_info'] = SystemMonitor.get_process_info()
            
            # 获取数据库信息
            if include_db:
                result['database_stats'] = DatabaseMonitor.get_database_stats()
            
            # 获取缓存信息
            if include_cache:
                result['cache_stats'] = CacheMonitor.get_cache_stats()
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"获取性能监控信息失败: {e}")
            return JsonResponse({
                'error': '获取性能监控信息失败',
                'message': str(e)
            }, status=500)
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """清除性能指标"""
        try:
            data = json.loads(request.body) if request.body else {}
            operation = data.get('operation')
            
            performance_monitor.clear_metrics(operation)
            
            return JsonResponse({
                'success': True,
                'message': f"已清除{'指定操作' if operation else '所有'}的性能指标"
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': '无效的JSON数据'
            }, status=400)
        except Exception as e:
            logger.error(f"清除性能指标失败: {e}")
            return JsonResponse({
                'error': '清除性能指标失败',
                'message': str(e)
            }, status=500)


class HealthCheckView(View):
    """健康检查视图"""
    
    def get(self, request):
        """健康检查"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'checks': {}
            }
            
            # 系统健康检查
            system_info = SystemMonitor.get_system_info()
            if system_info:
                memory_ok = system_info.get('memory', {}).get('percent', 0) < 90
                disk_ok = system_info.get('disk', {}).get('percent', 0) < 90
                cpu_ok = system_info.get('cpu', {}).get('percent', 0) < 90
                
                health_status['checks']['system'] = {
                    'status': 'healthy' if all([memory_ok, disk_ok, cpu_ok]) else 'warning',
                    'memory_ok': memory_ok,
                    'disk_ok': disk_ok,
                    'cpu_ok': cpu_ok,
                }
            else:
                health_status['checks']['system'] = {
                    'status': 'error',
                    'message': '无法获取系统信息'
                }
            
            # 数据库健康检查
            db_stats = DatabaseMonitor.get_database_stats()
            if db_stats:
                db_ok = any(stats.get('connected', False) for stats in db_stats.values() if isinstance(stats, dict))
                health_status['checks']['database'] = {
                    'status': 'healthy' if db_ok else 'error',
                    'connected': db_ok,
                }
            else:
                health_status['checks']['database'] = {
                    'status': 'error',
                    'message': '无法获取数据库信息'
                }
            
            # 缓存健康检查
            cache_stats = CacheMonitor.get_cache_stats()
            if cache_stats:
                cache_ok = cache_stats.get('working', False)
                health_status['checks']['cache'] = {
                    'status': 'healthy' if cache_ok else 'error',
                    'working': cache_ok,
                }
            else:
                health_status['checks']['cache'] = {
                    'status': 'error',
                    'message': '无法获取缓存信息'
                }
            
            # 整体状态
            all_healthy = all(
                check.get('status') == 'healthy' 
                for check in health_status['checks'].values()
            )
            
            if not all_healthy:
                health_status['status'] = 'unhealthy'
            
            status_code = 200 if health_status['status'] == 'healthy' else 503
            
            return JsonResponse(health_status, status=status_code)
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return JsonResponse({
                'status': 'error',
                'message': '健康检查失败',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            }, status=500)


class PerformanceAlert:
    """性能告警"""
    
    def __init__(self):
        self.alerts = []
        self.thresholds = {
            'response_time': 5.0,  # 5秒
            'cpu_percent': 80.0,   # 80%
            'memory_percent': 85.0, # 85%
            'disk_percent': 90.0,   # 90%
        }
    
    def check_alerts(self, metrics: Dict[str, Any], system_info: Dict[str, Any]):
        """检查告警"""
        alerts = []
        
        # 检查响应时间
        for operation, metric in metrics.items():
            if isinstance(metric, dict) and 'avg_time' in metric:
                if metric['avg_time'] > self.thresholds['response_time']:
                    alerts.append({
                        'type': 'response_time',
                        'operation': operation,
                        'value': metric['avg_time'],
                        'threshold': self.thresholds['response_time'],
                        'message': f"操作 {operation} 平均响应时间 {metric['avg_time']:.2f}s 超过阈值 {self.thresholds['response_time']}s",
                        'timestamp': datetime.now().isoformat(),
                    })
        
        # 检查系统资源
        if system_info:
            cpu_percent = system_info.get('cpu', {}).get('percent', 0)
            if cpu_percent > self.thresholds['cpu_percent']:
                alerts.append({
                    'type': 'cpu_usage',
                    'value': cpu_percent,
                    'threshold': self.thresholds['cpu_percent'],
                    'message': f"CPU使用率 {cpu_percent}% 超过阈值 {self.thresholds['cpu_percent']}%",
                    'timestamp': datetime.now().isoformat(),
                })
            
            memory_percent = system_info.get('memory', {}).get('percent', 0)
            if memory_percent > self.thresholds['memory_percent']:
                alerts.append({
                    'type': 'memory_usage',
                    'value': memory_percent,
                    'threshold': self.thresholds['memory_percent'],
                    'message': f"内存使用率 {memory_percent}% 超过阈值 {self.thresholds['memory_percent']}%",
                    'timestamp': datetime.now().isoformat(),
                })
            
            disk_percent = system_info.get('disk', {}).get('percent', 0)
            if disk_percent > self.thresholds['disk_percent']:
                alerts.append({
                    'type': 'disk_usage',
                    'value': disk_percent,
                    'threshold': self.thresholds['disk_percent'],
                    'message': f"磁盘使用率 {disk_percent}% 超过阈值 {self.thresholds['disk_percent']}%",
                    'timestamp': datetime.now().isoformat(),
                })
        
        return alerts


# 导出主要类和函数
__all__ = [
    'PerformanceMonitor',
    'performance_monitor',
    'monitor_performance',
    'SystemMonitor',
    'DatabaseMonitor',
    'CacheMonitor',
    'PerformanceMonitorView',
    'HealthCheckView',
    'PerformanceAlert',
]
