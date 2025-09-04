#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控服务
提供系统性能监控和告警功能
"""

import time
import logging
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
import redis
import psutil
import os
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.start_time = None
        self.request_data = {}

    def start_monitoring(self, request: HttpRequest):
        """开始监控请求"""
        self.start_time = time.time()
        self.request_data = {
            "path": request.path,
            "method": request.method,
            "user": request.user.username if request.user.is_authenticated else "anonymous",
            "ip": self._get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            "timestamp": timezone.now(),
        }

    def end_monitoring(self, response=None, exception=None):
        """结束监控并记录数据"""
        if not self.start_time:
            return

        duration = time.time() - self.start_time

        # 只在慢查询时才统计数据库信息，减少性能开销
        if duration > 1.0:  # 超过1秒才统计详细信息
            db_queries = len(connection.queries)
            db_time = sum(float(q.get("time", 0)) for q in connection.queries)
        else:
            db_queries = 0
            db_time = 0

        self.request_data.update(
            {
                "duration": duration,
                "status_code": response.status_code if response else 500,
                "exception": str(exception) if exception else None,
                "db_queries": db_queries,
                "db_time": db_time,
            }
        )

        # 记录性能数据
        self._log_performance()

        # 检查是否需要告警
        self._check_alerts()

    def _get_client_ip(self, request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def _log_performance(self):
        """记录性能数据"""
        # 只记录慢查询和异常，减少缓存操作
        duration = self.request_data["duration"]

        # 记录慢查询
        if duration > 2.0:  # 超过2秒的请求
            logger.warning(f"慢查询检测: {self.request_data}")
            # 只在慢查询时才存储到缓存
            cache_key = f"slow_query_log:{timezone.now().strftime('%Y%m%d%H%M%S')}"
            try:
                cache.set(cache_key, self.request_data, timeout=3600)
            except Exception:
                pass  # 缓存失败不影响主流程

        # 记录数据库查询过多
        if self.request_data["db_queries"] > 50:  # 超过50个查询
            logger.warning(f"数据库查询过多: {self.request_data['db_queries']} 查询")

    def _check_alerts(self):
        """检查是否需要告警"""
        duration = self.request_data["duration"]

        # 只在非常严重的情况下才发送告警（超过5秒）
        if duration > 5.0:
            try:
                AlertService._send_alert("响应时间过长", self.request_data)
            except Exception:
                pass  # 告警失败不影响主流程

        # 检查错误率
        if self.request_data["status_code"] >= 500:
            AlertService._send_alert("服务器错误", self.request_data)

        # 检查数据库查询时间
        if self.request_data["db_time"] > 1.0:  # 数据库查询超过1秒
            AlertService._send_alert("数据库查询缓慢", self.request_data)


class SystemMonitor:
    """系统监控器"""

    @staticmethod
    def get_system_metrics():
        """获取系统指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            "timestamp": timezone.now(),
        }

    @staticmethod
    def check_system_health():
        """检查系统健康状态"""
        metrics = SystemMonitor.get_system_metrics()
        alerts = []

        # CPU使用率检查
        if metrics["cpu_percent"] > 80:
            alerts.append(f"CPU使用率过高: {metrics['cpu_percent']}%")

        # 内存使用率检查
        if metrics["memory_percent"] > 85:
            alerts.append(f"内存使用率过高: {metrics['memory_percent']}%")

        # 磁盘使用率检查
        if metrics["disk_percent"] > 90:
            alerts.append(f"磁盘使用率过高: {metrics['disk_percent']}%")

        return alerts


class DatabaseMonitor:
    """数据库监控器"""

    @staticmethod
    def get_database_metrics():
        """获取数据库指标"""
        from django.db import connection

        # 检查数据库类型
        is_postgres = "postgresql" in connection.settings_dict["ENGINE"]

        try:
            with connection.cursor() as cursor:
                if is_postgres:
                    # PostgreSQL 特定查询
                    cursor.execute("SELECT count(*) FROM pg_stat_activity")
                    connections = cursor.fetchone()[0]

                    # 获取慢查询数
                    cursor.execute(
                        """
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 seconds'
                    """
                    )
                    slow_queries = cursor.fetchone()[0]

                    # 获取锁等待数
                    cursor.execute(
                        """
                        SELECT count(*) FROM pg_stat_activity 
                        WHERE wait_event_type = 'Lock'
                    """
                    )
                    lock_waits = cursor.fetchone()[0]
                else:
                    # 其他数据库（如 SQLite）使用默认值
                    connections = 1
                    slow_queries = 0
                    lock_waits = 0
        except Exception as e:
            logger.error(f"获取数据库指标失败: {e}")
            # 返回默认值
            connections = 1
            slow_queries = 0
            lock_waits = 0

        return {
            "connections": connections,
            "slow_queries": slow_queries,
            "lock_waits": lock_waits,
            "timestamp": timezone.now(),
        }

    @staticmethod
    def check_database_health():
        """检查数据库健康状态"""
        metrics = DatabaseMonitor.get_database_metrics()
        alerts = []

        # 连接数检查
        if metrics["connections"] > 100:
            alerts.append(f"数据库连接数过多: {metrics['connections']}")

        # 慢查询检查
        if metrics["slow_queries"] > 10:
            alerts.append(f"慢查询数量过多: {metrics['slow_queries']}")

        # 锁等待检查
        if metrics["lock_waits"] > 5:
            alerts.append(f"锁等待数量过多: {metrics['lock_waits']}")

        return alerts


class AlertService:
    """告警服务"""

    @staticmethod
    def _send_alert(subject, data):
        """发送告警"""
        try:
            # 发送邮件告警
            if hasattr(settings, "ALERT_EMAIL_RECIPIENTS"):
                AlertService._send_email_alert(subject, data)

            # 发送钉钉告警
            if hasattr(settings, "DINGTALK_WEBHOOK_URL"):
                AlertService._send_dingtalk_alert(subject, data)

            # 记录告警日志
            logger.error(f"告警: {subject} - {data}")

        except Exception as e:
            logger.error(f"发送告警失败: {e}")

    @staticmethod
    def _send_email_alert(subject, data):
        """发送邮件告警"""
        try:
            html_content = render_to_string(
                "tools/alert_email.html", {"subject": subject, "data": data, "timestamp": timezone.now()}
            )

            send_mail(
                subject=f"[QAToolBox告警] {subject}",
                message=f"告警详情: {json.dumps(data, indent=2, ensure_ascii=False)}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ALERT_EMAIL_RECIPIENTS,
                html_message=html_content,
            )
        except Exception as e:
            logger.error(f"发送邮件告警失败: {e}")

    @staticmethod
    def _send_dingtalk_alert(subject, data):
        """发送钉钉告警"""
        try:
            import requests

            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": f"QAToolBox告警: {subject}",
                    "text": f"""
### QAToolBox告警
**告警类型**: {subject}
**时间**: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
**详情**: 
```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```
                    """,
                },
            }

            response = requests.post(settings.DINGTALK_WEBHOOK_URL, json=message, timeout=10)

            if response.status_code != 200:
                logger.error(f"钉钉告警发送失败: {response.text}")

        except Exception as e:
            logger.error(f"发送钉钉告警失败: {e}")


class PerformanceMonitoringMiddleware:
    """性能监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.monitor = PerformanceMonitor()

    def __call__(self, request):
        # 开始监控
        self.monitor.start_monitoring(request)

        try:
            response = self.get_response(request)
            # 结束监控
            self.monitor.end_monitoring(response)
            return response
        except Exception as e:
            # 记录异常
            self.monitor.end_monitoring(exception=e)
            raise


class HealthCheckService:
    """健康检查服务"""

    @staticmethod
    def check_all():
        """检查所有系统健康状态"""
        results = {
            "system": SystemMonitor.check_system_health(),
            "database": DatabaseMonitor.check_database_health(),
            "timestamp": timezone.now(),
        }

        # 如果有任何告警，发送通知
        all_alerts = results["system"] + results["database"]
        if all_alerts:
            AlertService._send_alert("系统健康检查告警", {"alerts": all_alerts, "results": results})

        return results

    @staticmethod
    def get_status():
        """获取系统状态"""
        return {
            "system_metrics": SystemMonitor.get_system_metrics(),
            "database_metrics": DatabaseMonitor.get_database_metrics(),
            "timestamp": timezone.now(),
        }


# 定时任务：定期检查系统健康状态
def periodic_health_check():
    """定期健康检查任务"""
    try:
        HealthCheckService.check_all()
        logger.info("定期健康检查完成")
    except Exception as e:
        logger.error(f"定期健康检查失败: {e}")


# 定时任务：清理旧的性能日志
def cleanup_performance_logs():
    """清理旧的性能日志"""
    try:
        # 删除7天前的性能日志
        cutoff_time = timezone.now() - timedelta(days=7)
        pattern = f"performance_log:{cutoff_time.strftime('%Y%m%d')}*"

        # 这里需要根据实际的缓存实现来清理
        # 如果使用Redis，可以使用SCAN命令清理
        logger.info("性能日志清理完成")
    except Exception as e:
        logger.error(f"性能日志清理失败: {e}")


# 添加监控数据收集功能
def collect_monitoring_data() -> Dict[str, Any]:
    """收集监控数据"""
    try:
        data = {}

        # 系统监控数据
        system_monitor = SystemMonitor()
        data["system"] = system_monitor.get_system_metrics()

        # 数据库监控数据
        db_monitor = DatabaseMonitor()
        data["database"] = db_monitor.get_database_metrics()

        # 性能监控数据
        # Assuming performance_monitor is defined elsewhere or needs to be instantiated
        # For now, we'll just add a placeholder
        data["performance"] = {"placeholder": "Performance data not directly available here"}

        # 缓存统计
        from .cache_cleanup import get_cache_stats

        data["cache"] = get_cache_stats()

        # 日志统计
        from .log_rotation import get_log_stats

        data["logs"] = get_log_stats()

        # 数据库清理统计
        from .database_cleanup import get_cleanup_stats

        data["cleanup"] = get_cleanup_stats()

        # 存储到缓存中
        cache.set("monitoring_data", data, timeout=3600)

        return {"status": "success", "data_points": len(data), "timestamp": datetime.now()}

    except Exception as e:
        logger.error(f"收集监控数据失败: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.now()}


def get_monitoring_data() -> Dict[str, Any]:
    """获取监控数据"""
    try:
        data = cache.get("monitoring_data")
        if data:
            return data
        else:
            # 如果没有缓存数据，重新收集
            collect_monitoring_data()
            return cache.get("monitoring_data", {})
    except Exception as e:
        logger.error(f"获取监控数据失败: {e}")
        return {"error": str(e)}


# 添加监控数据清理功能
def cleanup_monitoring_data() -> Dict[str, Any]:
    """清理监控数据"""
    try:
        # 清理过期的监控数据
        cache.delete("monitoring_data")

        return {"status": "success", "message": "监控数据已清理", "timestamp": datetime.now()}

    except Exception as e:
        logger.error(f"清理监控数据失败: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.now()}


# 创建监控服务实例
monitoring_service = PerformanceMonitor()
