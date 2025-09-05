"""
最小化Docker构建专用设置
用于在Docker构建阶段，完全跳过collectstatic，避免所有依赖问题
"""

from .base import *

# 构建阶段特定配置
DEBUG = False

# 使用SQLite文件数据库，避免PostgreSQL依赖
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_docker_minimal.sqlite3",
    }
}

# 简化的缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
    }
}

# 简化的会话配置
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# 静态文件配置 - 使用默认存储，完全跳过collectstatic
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
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}

# 简化的Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = "django-db://"
CELERY_RESULT_BACKEND = "django-db"

# 简化的API限制
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {"anon": "100/minute", "user": "1000/minute"}

# 简化的CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 允许的主机
ALLOWED_HOSTS = ["*"]

# 简化的安全头
SECURE_REFERRER_POLICY = "no-referrer-when-downgrade"

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000

# 禁用所有可能导致问题的应用
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "corsheaders",
    "crispy_forms",
    "crispy_bootstrap5",
    "django_filters",
    "channels",
    "apps.users",
    "apps.content",
    "apps.tools",
]

# 禁用所有可能导致问题的中间件
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
