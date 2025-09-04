import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string

import requests

logger = logging.getLogger(__name__)


class AlertLevel:
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel:
    """告警渠道"""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"


class AlertSystem:
    """告警系统"""

    def __init__(self):
        self.alert_config = getattr(settings, "ALERT_CONFIG", {})
        self.enable_alerts = getattr(settings, "ENABLE_ALERTS", True)
        self.alert_cooldown = getattr(settings, "ALERT_COOLDOWN", 300)  # 5分钟冷却时间

    def send_alert(self, level, message, context=None, channels=None):
        """发送告警"""
        if not self.enable_alerts:
            return

        # 检查冷却时间
        if not self._should_send_alert(level, message):
            return

        # 记录告警
        self._log_alert(level, message, context)

        # 发送到指定渠道
        if channels is None:
            channels = self._get_default_channels(level)

        for channel in channels:
            try:
                self._send_to_channel(channel, level, message, context)
            except Exception as e:
                logger.error(f"Failed to send alert to {channel}: {e}")

    def _should_send_alert(self, level, message):
        """检查是否应该发送告警（冷却时间）"""
        cache_key = f"alert_cooldown:{level}:{hash(message)}"
        if cache.get(cache_key):
            return False

        # 设置冷却时间
        cache.set(cache_key, True, self.alert_cooldown)
        return True

    def _log_alert(self, level, message, context):
        """记录告警"""
        log_message = f"ALERT [{level.upper()}] {message}"
        if context:
            log_message += f" Context: {context}"

        if level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif level == AlertLevel.ERROR:
            logger.error(log_message)
        elif level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    def _get_default_channels(self, level):
        """获取默认告警渠道"""
        if level == AlertLevel.CRITICAL:
            return [AlertChannel.EMAIL, AlertChannel.SLACK]
        elif level == AlertLevel.ERROR:
            return [AlertChannel.EMAIL]
        elif level == AlertLevel.WARNING:
            return [AlertChannel.SLACK]
        else:
            return []

    def _send_to_channel(self, channel, level, message, context):
        """发送告警到指定渠道"""
        if channel == AlertChannel.EMAIL:
            self._send_email_alert(level, message, context)
        elif channel == AlertChannel.SLACK:
            self._send_slack_alert(level, message, context)
        elif channel == AlertChannel.WEBHOOK:
            self._send_webhook_alert(level, message, context)
        elif channel == AlertChannel.SMS:
            self._send_sms_alert(level, message, context)

    def _send_email_alert(self, level, message, context):
        """发送邮件告警"""
        try:
            subject = f"[{level.upper()}] QAToolBox Alert"

            # 构建邮件内容
            email_context = {
                "level": level,
                "message": message,
                "context": context,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "environment": getattr(settings, "ENVIRONMENT", "development"),
            }

            html_content = render_to_string("alerts/email_alert.html", email_context)
            text_content = render_to_string("alerts/email_alert.txt", email_context)

            # 获取收件人列表
            recipients = self.alert_config.get("email_recipients", [])
            if not recipients:
                logger.warning("No email recipients configured for alerts")
                return

            # 发送邮件
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=html_content,
            )

            logger.info(f"Email alert sent: {message}")

        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")

    def _send_slack_alert(self, level, message, context):
        """发送Slack告警"""
        try:
            webhook_url = self.alert_config.get("slack_webhook_url")
            if not webhook_url:
                logger.warning("No Slack webhook URL configured")
                return

            # 构建Slack消息
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ff9500",
                AlertLevel.ERROR: "#ff0000",
                AlertLevel.CRITICAL: "#8b0000",
            }

            slack_message = {
                "attachments": [
                    {
                        "color": color_map.get(level, "#36a64f"),
                        "title": f"QAToolBox Alert - {level.upper()}",
                        "text": message,
                        "fields": [
                            {"title": "Environment", "value": getattr(settings, "ENVIRONMENT", "development"), "short": True},
                            {"title": "Timestamp", "value": time.strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                        ],
                    }
                ]
            }

            if context:
                slack_message["attachments"][0]["fields"].append({"title": "Context", "value": str(context), "short": False})

            # 发送到Slack
            response = requests.post(webhook_url, json=slack_message, timeout=10)
            response.raise_for_status()

            logger.info(f"Slack alert sent: {message}")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def _send_webhook_alert(self, level, message, context):
        """发送Webhook告警"""
        try:
            webhook_url = self.alert_config.get("webhook_url")
            if not webhook_url:
                logger.warning("No webhook URL configured")
                return

            # 构建webhook数据
            webhook_data = {
                "level": level,
                "message": message,
                "context": context,
                "timestamp": time.time(),
                "environment": getattr(settings, "ENVIRONMENT", "development"),
            }

            # 发送webhook
            response = requests.post(webhook_url, json=webhook_data, timeout=10)
            response.raise_for_status()

            logger.info(f"Webhook alert sent: {message}")

        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")

    def _send_sms_alert(self, level, message, context):
        """发送短信告警"""
        # 这里可以实现短信告警逻辑
        logger.info(f"SMS alert (not implemented): {message}")


# 全局告警系统实例
alert_system = AlertSystem()


# 便捷函数
def send_info_alert(message, context=None, channels=None):
    """发送信息告警"""
    alert_system.send_alert(AlertLevel.INFO, message, context, channels)


def send_warning_alert(message, context=None, channels=None):
    """发送警告告警"""
    alert_system.send_alert(AlertLevel.WARNING, message, context, channels)


def send_error_alert(message, context=None, channels=None):
    """发送错误告警"""
    alert_system.send_alert(AlertLevel.ERROR, message, context, channels)


def send_critical_alert(message, context=None, channels=None):
    """发送严重告警"""
    alert_system.send_alert(AlertLevel.CRITICAL, message, context, channels)


# 特定告警函数
def alert_slow_request(path, execution_time, query_count):
    """慢请求告警"""
    message = f"Slow request detected: {path} took {execution_time:.3f}s with {query_count} queries"
    context = {"path": path, "execution_time": execution_time, "query_count": query_count}
    send_warning_alert(message, context)


def alert_database_error(error, query=None):
    """数据库错误告警"""
    message = f"Database error: {error}"
    context = {"error": str(error), "query": query}
    send_error_alert(message, context)


def alert_high_memory_usage(usage_percent):
    """高内存使用告警"""
    message = f"High memory usage: {usage_percent:.1f}%"
    context = {"usage_percent": usage_percent}
    send_warning_alert(message, context)


def alert_high_cpu_usage(usage_percent):
    """高CPU使用告警"""
    message = f"High CPU usage: {usage_percent:.1f}%"
    context = {"usage_percent": usage_percent}
    send_warning_alert(message, context)


def alert_service_down(service_name, error):
    """服务宕机告警"""
    message = f"Service {service_name} is down: {error}"
    context = {"service": service_name, "error": str(error)}
    send_critical_alert(message, context)
