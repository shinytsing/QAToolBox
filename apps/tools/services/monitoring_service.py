#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控服务
提供系统性能监控和告警功能
"""

import time
import psutil
import logging
from typing import Dict, List, Any, Optional
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # 内存指标
            memory = psutil.virtual_memory()
            
            # 磁盘指标
            disk = psutil.disk_usage('/')
            
            # 网络指标
            network = psutil.net_io_counters()
            
            # 进程指标
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': cpu_freq.current if cpu_freq else None,
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': disk.percent,
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                },
                'process': {
                    'memory_rss': process_memory.rss,
                    'memory_vms': process_memory.vms,
                    'cpu_percent': process_cpu,
                }
            }
            
            self.metrics = metrics
            return metrics
            
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """检查告警"""
        alerts = []
        
        if not self.metrics:
            return alerts
        
        # CPU告警
        cpu_percent = self.metrics.get('cpu', {}).get('percent', 0)
        if cpu_percent > 80:
            alerts.append({
                'type': 'cpu_high',
                'level': 'warning',
                'message': f'CPU使用率过高: {cpu_percent}%',
                'timestamp': timezone.now().isoformat(),
            })
        elif cpu_percent > 95:
            alerts.append({
                'type': 'cpu_critical',
                'level': 'critical',
                'message': f'CPU使用率严重过高: {cpu_percent}%',
                'timestamp': timezone.now().isoformat(),
            })
        
        # 内存告警
        memory_percent = self.metrics.get('memory', {}).get('percent', 0)
        if memory_percent > 85:
            alerts.append({
                'type': 'memory_high',
                'level': 'warning',
                'message': f'内存使用率过高: {memory_percent}%',
                'timestamp': timezone.now().isoformat(),
            })
        elif memory_percent > 95:
            alerts.append({
                'type': 'memory_critical',
                'level': 'critical',
                'message': f'内存使用率严重过高: {memory_percent}%',
                'timestamp': timezone.now().isoformat(),
            })
        
        # 磁盘告警
        disk_percent = self.metrics.get('disk', {}).get('percent', 0)
        if disk_percent > 90:
            alerts.append({
                'type': 'disk_high',
                'level': 'warning',
                'message': f'磁盘使用率过高: {disk_percent}%',
                'timestamp': timezone.now().isoformat(),
            })
        
        self.alerts = alerts
        return alerts


class DatabaseMonitor:
    """数据库监控器"""
    
    def __init__(self):
        self.connection_stats = {}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取数据库连接统计"""
        try:
            from django.db import connection
            
            with connection.cursor() as cursor:
                # 获取连接信息
                cursor.execute("SELECT count(*) FROM pg_stat_activity")
                active_connections = cursor.fetchone()[0]
                
                # 获取慢查询统计
                cursor.execute("""
                    SELECT query, mean_time, calls 
                    FROM pg_stat_statements 
                    ORDER BY mean_time DESC 
                    LIMIT 10
                """)
                slow_queries = cursor.fetchall()
                
                stats = {
                    'active_connections': active_connections,
                    'slow_queries': [
                        {
                            'query': query[:100] + '...' if len(query) > 100 else query,
                            'mean_time': mean_time,
                            'calls': calls
                        }
                        for query, mean_time, calls in slow_queries
                    ],
                    'timestamp': timezone.now().isoformat(),
                }
                
                self.connection_stats = stats
                return stats
                
        except Exception as e:
            logger.error(f"获取数据库连接统计失败: {e}")
            return {}
    
    def check_database_alerts(self) -> List[Dict[str, Any]]:
        """检查数据库告警"""
        alerts = []
        
        if not self.connection_stats:
            return alerts
        
        # 连接数告警
        active_connections = self.connection_stats.get('active_connections', 0)
        if active_connections > 50:
            alerts.append({
                'type': 'db_connections_high',
                'level': 'warning',
                'message': f'数据库连接数过高: {active_connections}',
                'timestamp': timezone.now().isoformat(),
            })
        
        # 慢查询告警
        slow_queries = self.connection_stats.get('slow_queries', [])
        for query in slow_queries:
            if query.get('mean_time', 0) > 1000:  # 超过1秒
                alerts.append({
                    'type': 'db_slow_query',
                    'level': 'warning',
                    'message': f'发现慢查询: {query.get("mean_time", 0)}ms',
                    'timestamp': timezone.now().isoformat(),
                })
        
        return alerts


class CacheMonitor:
    """缓存监控器"""
    
    def __init__(self):
        self.cache_stats = {}
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        try:
            # 尝试获取Redis统计信息
            if hasattr(cache, 'client') and hasattr(cache.client, 'info'):
                redis_info = cache.client.info()
                
                stats = {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory': redis_info.get('used_memory', 0),
                    'used_memory_peak': redis_info.get('used_memory_peak', 0),
                    'total_commands_processed': redis_info.get('total_commands_processed', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0),
                    'timestamp': timezone.now().isoformat(),
                }
                
                # 计算命中率
                total_requests = stats['keyspace_hits'] + stats['keyspace_misses']
                if total_requests > 0:
                    stats['hit_rate'] = stats['keyspace_hits'] / total_requests
                else:
                    stats['hit_rate'] = 0
                
                self.cache_stats = stats
                return stats
            else:
                return {'status': 'cache_stats_not_available'}
                
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {}
    
    def check_cache_alerts(self) -> List[Dict[str, Any]]:
        """检查缓存告警"""
        alerts = []
        
        if not self.cache_stats:
            return alerts
        
        # 命中率告警
        hit_rate = self.cache_stats.get('hit_rate', 0)
        if hit_rate < 0.8:
            alerts.append({
                'type': 'cache_hit_rate_low',
                'level': 'warning',
                'message': f'缓存命中率过低: {hit_rate:.2%}',
                'timestamp': timezone.now().isoformat(),
            })
        
        # 内存使用告警
        used_memory = self.cache_stats.get('used_memory', 0)
        if used_memory > 100 * 1024 * 1024:  # 超过100MB
            alerts.append({
                'type': 'cache_memory_high',
                'level': 'warning',
                'message': f'缓存内存使用过高: {used_memory / 1024 / 1024:.2f}MB',
                'timestamp': timezone.now().isoformat(),
            })
        
        return alerts


class ApplicationMonitor:
    """应用监控器"""
    
    def __init__(self):
        self.app_stats = {}
    
    def get_application_stats(self) -> Dict[str, Any]:
        """获取应用统计"""
        try:
            from django.contrib.auth.models import User
            from apps.tools.models import ChatRoom, ChatMessage, TimeCapsule, HeartLinkRequest
            
            # 获取应用指标
            stats = {
                'total_users': User.objects.count(),
                'active_users_today': User.objects.filter(
                    last_login__gte=timezone.now() - timedelta(days=1)
                ).count(),
                'total_chat_rooms': ChatRoom.objects.count(),
                'active_chat_rooms': ChatRoom.objects.filter(status='active').count(),
                'total_messages': ChatMessage.objects.count(),
                'messages_today': ChatMessage.objects.filter(
                    created_at__gte=timezone.now() - timedelta(days=1)
                ).count(),
                'total_capsules': TimeCapsule.objects.count(),
                'public_capsules': TimeCapsule.objects.filter(visibility='public').count(),
                'total_heart_links': HeartLinkRequest.objects.count(),
                'pending_heart_links': HeartLinkRequest.objects.filter(status='pending').count(),
                'timestamp': timezone.now().isoformat(),
            }
            
            self.app_stats = stats
            return stats
            
        except Exception as e:
            logger.error(f"获取应用统计失败: {e}")
            return {}
    
    def check_application_alerts(self) -> List[Dict[str, Any]]:
        """检查应用告警"""
        alerts = []
        
        if not self.app_stats:
            return alerts
        
        # 活跃用户告警
        active_users = self.app_stats.get('active_users_today', 0)
        if active_users < 10:
            alerts.append({
                'type': 'low_active_users',
                'level': 'info',
                'message': f'今日活跃用户较少: {active_users}',
                'timestamp': timezone.now().isoformat(),
            })
        
        # 消息量告警
        messages_today = self.app_stats.get('messages_today', 0)
        if messages_today > 10000:
            alerts.append({
                'type': 'high_message_volume',
                'level': 'warning',
                'message': f'今日消息量过高: {messages_today}',
                'timestamp': timezone.now().isoformat(),
            })
        
        return alerts


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.performance_metrics = {}
        self.response_times = []
    
    def record_response_time(self, endpoint: str, response_time: float):
        """记录响应时间"""
        self.response_times.append({
            'endpoint': endpoint,
            'response_time': response_time,
            'timestamp': timezone.now().isoformat(),
        })
        
        # 只保留最近1000条记录
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        if not self.response_times:
            return {}
        
        # 按端点分组计算统计信息
        endpoint_stats = {}
        for record in self.response_times:
            endpoint = record['endpoint']
            response_time = record['response_time']
            
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0,
                    'times': []
                }
            
            stats = endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_time'] += response_time
            stats['min_time'] = min(stats['min_time'], response_time)
            stats['max_time'] = max(stats['max_time'], response_time)
            stats['times'].append(response_time)
        
        # 计算平均值和百分位数
        for endpoint, stats in endpoint_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['times'].sort()
            stats['p95_time'] = stats['times'][int(len(stats['times']) * 0.95)]
            stats['p99_time'] = stats['times'][int(len(stats['times']) * 0.99)]
            del stats['times']  # 删除原始数据以节省内存
        
        self.performance_metrics = endpoint_stats
        return endpoint_stats
    
    def check_performance_alerts(self) -> List[Dict[str, Any]]:
        """检查性能告警"""
        alerts = []
        
        if not self.performance_metrics:
            return alerts
        
        for endpoint, stats in self.performance_metrics.items():
            avg_time = stats.get('avg_time', 0)
            p95_time = stats.get('p95_time', 0)
            
            if avg_time > 1.0:  # 平均响应时间超过1秒
                alerts.append({
                    'type': 'slow_response_avg',
                    'level': 'warning',
                    'message': f'端点 {endpoint} 平均响应时间过慢: {avg_time:.3f}s',
                    'timestamp': timezone.now().isoformat(),
                })
            
            if p95_time > 3.0:  # 95%响应时间超过3秒
                alerts.append({
                    'type': 'slow_response_p95',
                    'level': 'warning',
                    'message': f'端点 {endpoint} 95%响应时间过慢: {p95_time:.3f}s',
                    'timestamp': timezone.now().isoformat(),
                })
        
        return alerts


class MonitoringService:
    """监控服务主类"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.db_monitor = DatabaseMonitor()
        self.cache_monitor = CacheMonitor()
        self.app_monitor = ApplicationMonitor()
        self.performance_monitor = PerformanceMonitor()
    
    def collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有监控指标"""
        metrics = {
            'system': self.system_monitor.get_system_metrics(),
            'database': self.db_monitor.get_connection_stats(),
            'cache': self.cache_monitor.get_cache_stats(),
            'application': self.app_monitor.get_application_stats(),
            'performance': self.performance_monitor.get_performance_metrics(),
            'timestamp': timezone.now().isoformat(),
        }
        
        # 缓存监控数据
        cache.set('monitoring_metrics', json.dumps(metrics), 300)  # 5分钟缓存
        
        return metrics
    
    def check_all_alerts(self) -> List[Dict[str, Any]]:
        """检查所有告警"""
        alerts = []
        
        # 收集各模块告警
        alerts.extend(self.system_monitor.check_alerts())
        alerts.extend(self.db_monitor.check_database_alerts())
        alerts.extend(self.cache_monitor.check_cache_alerts())
        alerts.extend(self.app_monitor.check_application_alerts())
        alerts.extend(self.performance_monitor.check_performance_alerts())
        
        # 缓存告警信息
        cache.set('monitoring_alerts', json.dumps(alerts), 60)  # 1分钟缓存
        
        return alerts
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取仪表板数据"""
        metrics = self.collect_all_metrics()
        alerts = self.check_all_alerts()
        
        # 计算健康状态
        health_score = 100
        critical_alerts = len([a for a in alerts if a.get('level') == 'critical'])
        warning_alerts = len([a for a in alerts if a.get('level') == 'warning'])
        
        health_score -= critical_alerts * 20
        health_score -= warning_alerts * 5
        health_score = max(0, health_score)
        
        return {
            'metrics': metrics,
            'alerts': alerts,
            'health_score': health_score,
            'alert_summary': {
                'critical': critical_alerts,
                'warning': warning_alerts,
                'info': len([a for a in alerts if a.get('level') == 'info']),
            },
            'timestamp': timezone.now().isoformat(),
        }
    
    def record_request(self, endpoint: str, response_time: float):
        """记录请求性能"""
        self.performance_monitor.record_response_time(endpoint, response_time)


# 全局监控服务实例
monitoring_service = MonitoringService()


# 中间件用于自动记录请求性能
class PerformanceMonitoringMiddleware:
    """性能监控中间件"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 记录请求性能
        endpoint = request.path
        monitoring_service.record_request(endpoint, response_time)
        
        return response
