"""
简化的生产环境配置
用于Docker构建，避免复杂的依赖问题
"""

from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 - 简化设置
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "SAMEORIGIN"

# 简化的数据库配置 - 使用SQLite避免PostgreSQL依赖
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 简化的缓存配置 - 使用本地内存缓存
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    }
}

# 简化的会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 简化的静态文件配置
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 简化的邮件配置
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 简化的日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# 简化的Celery配置 - 同步执行
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "django-db://"
CELERY_RESULT_BACKEND = "django-db"

# 简化的API限制
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "100/minute", "user": "1000/minute"}

# 简化的CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 允许的主机
ALLOWED_HOSTS = [
    "shenyiqing.xin",
    "www.shenyiqing.xin",
    "47.103.143.152",
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "*",
]

# 简化的安全头
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000
