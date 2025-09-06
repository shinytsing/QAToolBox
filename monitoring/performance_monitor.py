import time
import psutil
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
import json
import threading
from collections import defaultdict, deque

User = get_user_model()

class SystemPerformanceMonitor:
    """系统性能监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance_monitor')
        self.metrics = defaultdict(list)
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time': 2.0,
            'error_rate': 5.0,
        }
        self.alert_recipients = getattr(settings, 'PERFORMANCE_ALERT_EMAILS', [])
        self.monitoring_interval = 60  # 监控间隔（秒）
        self.is_monitoring = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                self._check_alerts()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self):
        """收集指标"""
        try:
            timestamp = timezone.now()
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            self._store_metric('cpu_percent', cpu_percent, timestamp)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            self._store_metric('memory_percent', memory.percent, timestamp)
            
            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self._store_metric('disk_percent', disk_percent, timestamp)
            
            # 网络IO
            net_io = psutil.net_io_counters()
            self._store_metric('network_bytes_sent', net_io.bytes_sent, timestamp)
            self._store_metric('network_bytes_recv', net_io.bytes_recv, timestamp)
            
            # 数据库连接数
            db_connections = self._get_db_connection_count()
            self._store_metric('db_connections', db_connections, timestamp)
            
            # 缓存命中率
            cache_hit_rate = self._get_cache_hit_rate()
            self._store_metric('cache_hit_rate', cache_hit_rate, timestamp)
            
            # 活跃用户数
            active_users = self._get_active_users_count()
            self._store_metric('active_users', active_users, timestamp)
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
    
    def _store_metric(self, metric_name, value, timestamp):
        """存储指标"""
        try:
            # 存储到内存
            self.metrics[metric_name].append({
                'value': value,
                'timestamp': timestamp,
                'timestamp_epoch': timestamp.timestamp()
            })
            
            # 保持最近1000个数据点
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name] = self.metrics[metric_name][-1000:]
            
            # 存储到缓存
            cache_key = f"metric_{metric_name}_{timestamp.strftime('%Y%m%d%H%M')}"
            cache.set(cache_key, value, 3600)  # 1小时过期
            
        except Exception as e:
            self.logger.error(f"Failed to store metric {metric_name}: {e}")
    
    def _get_db_connection_count(self):
        """获取数据库连接数"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception:
            return 0
    
    def _get_cache_hit_rate(self):
        """获取缓存命中率"""
        try:
            # 这里需要根据使用的缓存后端实现
            # 例如Redis的INFO命令
            return 0.95  # 示例值
        except Exception:
            return 0.0
    
    def _get_active_users_count(self):
        """获取活跃用户数"""
        try:
            # 获取最近5分钟内的活跃用户
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            return User.objects.filter(last_login__gte=five_minutes_ago).count()
        except Exception:
            return 0
    
    def _check_alerts(self):
        """检查告警"""
        try:
            current_time = timezone.now()
            
            # 检查CPU使用率
            cpu_percent = self._get_current_metric('cpu_percent')
            if cpu_percent and cpu_percent > self.alert_thresholds['cpu_percent']:
                self._send_alert('CPU使用率过高', f'当前CPU使用率: {cpu_percent:.1f}%')
            
            # 检查内存使用率
            memory_percent = self._get_current_metric('memory_percent')
            if memory_percent and memory_percent > self.alert_thresholds['memory_percent']:
                self._send_alert('内存使用率过高', f'当前内存使用率: {memory_percent:.1f}%')
            
            # 检查磁盘使用率
            disk_percent = self._get_current_metric('disk_percent')
            if disk_percent and disk_percent > self.alert_thresholds['disk_percent']:
                self._send_alert('磁盘使用率过高', f'当前磁盘使用率: {disk_percent:.1f}%')
            
            # 检查响应时间
            response_time = self._get_avg_response_time()
            if response_time and response_time > self.alert_thresholds['response_time']:
                self._send_alert('响应时间过长', f'平均响应时间: {response_time:.3f}秒')
            
            # 检查错误率
            error_rate = self._get_error_rate()
            if error_rate and error_rate > self.alert_thresholds['error_rate']:
                self._send_alert('错误率过高', f'当前错误率: {error_rate:.1f}%')
            
        except Exception as e:
            self.logger.error(f"Failed to check alerts: {e}")
    
    def _get_current_metric(self, metric_name):
        """获取当前指标值"""
        try:
            if metric_name in self.metrics and self.metrics[metric_name]:
                return self.metrics[metric_name][-1]['value']
            return None
        except Exception:
            return None
    
    def _get_avg_response_time(self):
        """获取平均响应时间"""
        try:
            # 这里需要从请求日志中获取响应时间数据
            # 示例实现
            return 0.5  # 示例值
        except Exception:
            return None
    
    def _get_error_rate(self):
        """获取错误率"""
        try:
            # 这里需要从错误日志中获取错误率数据
            # 示例实现
            return 1.0  # 示例值
        except Exception:
            return None
    
    def _send_alert(self, title, message):
        """发送告警"""
        try:
            if not self.alert_recipients:
                return
            
            subject = f"🚨 性能告警 - {title}"
            full_message = f"""
            {message}
            
            时间: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
            系统: {settings.SITE_NAME or 'QAToolBox'}
            
            请立即检查系统状态！
            """
            
            send_mail(
                subject=subject,
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=self.alert_recipients,
                fail_silently=False,
            )
            
            self.logger.warning(f"Performance alert sent: {title} - {message}")
            
        except Exception as e:
            self.logger.error(f"Failed to send performance alert: {e}")
    
    def get_performance_dashboard(self):
        """获取性能仪表板数据"""
        try:
            current_time = timezone.now()
            
            # 获取最近1小时的数据
            one_hour_ago = current_time - timedelta(hours=1)
            
            dashboard_data = {
                'timestamp': current_time.isoformat(),
                'current_metrics': {},
                'trends': {},
                'alerts': [],
                'health_status': 'healthy'
            }
            
            # 当前指标
            for metric_name in ['cpu_percent', 'memory_percent', 'disk_percent', 'active_users']:
                current_value = self._get_current_metric(metric_name)
                dashboard_data['current_metrics'][metric_name] = current_value or 0
            
            # 趋势数据
            for metric_name in ['cpu_percent', 'memory_percent', 'disk_percent']:
                trend_data = self._get_metric_trend(metric_name, one_hour_ago, current_time)
                dashboard_data['trends'][metric_name] = trend_data
            
            # 健康状态
            health_issues = []
            if dashboard_data['current_metrics']['cpu_percent'] > self.alert_thresholds['cpu_percent']:
                health_issues.append('CPU使用率过高')
            if dashboard_data['current_metrics']['memory_percent'] > self.alert_thresholds['memory_percent']:
                health_issues.append('内存使用率过高')
            if dashboard_data['current_metrics']['disk_percent'] > self.alert_thresholds['disk_percent']:
                health_issues.append('磁盘使用率过高')
            
            if health_issues:
                dashboard_data['health_status'] = 'warning'
                dashboard_data['alerts'] = health_issues
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Failed to get performance dashboard: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e),
                'health_status': 'error'
            }
    
    def _get_metric_trend(self, metric_name, start_time, end_time):
        """获取指标趋势"""
        try:
            trend_data = []
            if metric_name in self.metrics:
                for data_point in self.metrics[metric_name]:
                    if start_time <= data_point['timestamp'] <= end_time:
                        trend_data.append({
                            'timestamp': data_point['timestamp'].isoformat(),
                            'value': data_point['value']
                        })
            return trend_data
        except Exception as e:
            self.logger.error(f"Failed to get metric trend for {metric_name}: {e}")
            return []
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': psutil.disk_usage('/').total,
                'disk_free': psutil.disk_usage('/').free,
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'python_version': psutil.sys.version,
                'django_version': settings.VERSION,
            }
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {}

class APIPerformanceMonitor:
    """API性能监控器"""
    
    def __init__(self):
        self.logger = logging.getLogger('api_performance_monitor')
        self.request_times = deque(maxlen=1000)
        self.endpoint_stats = defaultdict(list)
    
    def record_request(self, endpoint, method, duration, status_code, user_id=None):
        """记录请求性能"""
        try:
            request_data = {
                'endpoint': endpoint,
                'method': method,
                'duration': duration,
                'status_code': status_code,
                'user_id': user_id,
                'timestamp': timezone.now()
            }
            
            self.request_times.append(request_data)
            self.endpoint_stats[endpoint].append(request_data)
            
            # 记录慢请求
            if duration > 2.0:  # 2秒阈值
                self.logger.warning(
                    f"Slow API request: {method} {endpoint} - {duration:.3f}s",
                    extra=request_data
                )
            
        except Exception as e:
            self.logger.error(f"Failed to record request: {e}")
    
    def get_api_stats(self, hours=24):
        """获取API统计"""
        try:
            end_time = timezone.now()
            start_time = end_time - timedelta(hours=hours)
            
            # 过滤时间范围内的请求
            recent_requests = [
                req for req in self.request_times
                if start_time <= req['timestamp'] <= end_time
            ]
            
            if not recent_requests:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'max_response_time': 0,
                    'min_response_time': 0,
                    'error_rate': 0,
                    'top_endpoints': [],
                    'response_time_distribution': {}
                }
            
            # 计算统计信息
            total_requests = len(recent_requests)
            response_times = [req['duration'] for req in recent_requests]
            status_codes = [req['status_code'] for req in recent_requests]
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # 错误率
            error_requests = [code for code in status_codes if code >= 400]
            error_rate = (len(error_requests) / total_requests) * 100
            
            # 最常用端点
            endpoint_counts = defaultdict(int)
            for req in recent_requests:
                endpoint_counts[req['endpoint']] += 1
            
            top_endpoints = sorted(
                endpoint_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # 响应时间分布
            response_time_distribution = {
                '0-0.5s': len([t for t in response_times if t < 0.5]),
                '0.5-1s': len([t for t in response_times if 0.5 <= t < 1.0]),
                '1-2s': len([t for t in response_times if 1.0 <= t < 2.0]),
                '2-5s': len([t for t in response_times if 2.0 <= t < 5.0]),
                '5s+': len([t for t in response_times if t >= 5.0]),
            }
            
            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 3),
                'max_response_time': round(max_response_time, 3),
                'min_response_time': round(min_response_time, 3),
                'error_rate': round(error_rate, 2),
                'top_endpoints': top_endpoints,
                'response_time_distribution': response_time_distribution,
                'status_code_distribution': dict(Counter(status_codes))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get API stats: {e}")
            return {}

# 全局监控器实例
system_performance_monitor = SystemPerformanceMonitor()
api_performance_monitor = APIPerformanceMonitor()

# 中间件
class PerformanceMonitoringMiddleware:
    """性能监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # 记录API性能
        if request.path.startswith('/api/'):
            api_performance_monitor.record_request(
                endpoint=request.path,
                method=request.method,
                duration=duration,
                status_code=response.status_code,
                user_id=getattr(request, 'user', {}).get('id') if hasattr(request, 'user') else None
            )
        
        return response
