import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from django.conf import settings
import os


def init_sentry():
    """初始化Sentry监控"""
    if hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                DjangoIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
            ],
            # 性能监控
            traces_sample_rate=0.1,
            # 错误采样率
            profiles_sample_rate=0.1,
            # 环境
            environment=os.getenv("ENVIRONMENT", "development"),
            # 发布版本
            release=os.getenv("VERSION", "1.0.0"),
            # 调试模式
            debug=settings.DEBUG,
            # 发送PII数据
            send_default_pii=True,
        )


def capture_exception(exception, context=None):
    """捕获异常"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_exception(exception)


def capture_message(message, level="info", context=None):
    """捕获消息"""
    if context:
        sentry_sdk.set_context("custom", context)
    sentry_sdk.capture_message(message, level=level)


def set_user(user):
    """设置用户信息"""
    if user and user.is_authenticated:
        sentry_sdk.set_user(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        )


def set_tag(key, value):
    """设置标签"""
    sentry_sdk.set_tag(key, value)


def set_extra(key, value):
    """设置额外信息"""
    sentry_sdk.set_extra(key, value)
