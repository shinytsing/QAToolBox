"""
阿里云生产环境配置
"""

from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 - 阿里云SSL
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# 阿里云数据库配置 - 使用PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "qatoolbox_production"),
        "USER": os.environ.get("DB_USER", "qatoolbox"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "prefer",
        },
    }
}

# 阿里云缓存配置 - 使用Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
    }
}

# 阿里云会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 86400  # 24小时
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# 阿里云静态文件配置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
STATIC_ROOT = "/var/www/qatoolbox/staticfiles/"
MEDIA_ROOT = "/var/www/qatoolbox/media/"

# 阿里云允许的主机
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "shenyiqing.xin",
    "www.shenyiqing.xin",
    "app.shenyiqing.xin",
    "qatoolbox.aliyun.com",
    "*.aliyun.com",
]

# 阿里云日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/qatoolbox/django.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
            "level": "INFO",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/qatoolbox/error.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "verbose",
            "level": "ERROR",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "WARNING",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file", "console"],
            "level": "INFO",
            "propagate": True,
        },
        "apps.tools": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
        "apps.users": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# 阿里云邮件配置
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.aliyun.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@shenyiqing.xin")

# 阿里云Celery配置
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Asia/Shanghai"

# 阿里云安全配置
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"

# 阿里云特定设置
ALIYUN_PRODUCTION = True

# 创建必要的目录
import os

os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)
os.makedirs("/var/log/qatoolbox", exist_ok=True)
