"""
QAToolBox 简化生产环境设置
解决线上部署依赖问题
"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 安全设置
SECRET_KEY = os.environ.get("SECRET_KEY", "django-modeshift-production-key-default")
DEBUG = False
ALLOWED_HOSTS = ["47.103.143.152", "shenyiqing.xin", "www.shenyiqing.xin", "localhost", "127.0.0.1", "*"]

# 应用配置 - 只包含核心应用，避免复杂依赖
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
]

# 尝试添加自定义应用（如果存在且可导入）
try:
    import apps.users

    INSTALLED_APPS.append("apps.users")
except (ImportError, ModuleNotFoundError):
    pass

try:
    import apps.content

    INSTALLED_APPS.append("apps.content")
except (ImportError, ModuleNotFoundError):
    pass

# 中间件
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls_simple"

# 模板设置
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "src" / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "QAToolBox.wsgi.application"

# 数据库配置
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# 国际化
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True

# 静态文件设置
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 静态文件目录
STATICFILES_DIRS = []
for static_dir in [
    BASE_DIR / "src" / "static",
    BASE_DIR / "static",
]:
    if static_dir.exists():
        STATICFILES_DIRS.append(static_dir)

# 媒体文件设置
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# 默认主键字段类型
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS设置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 安全设置
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [
    "http://shenyiqing.xin",
    "http://47.103.143.152",
    "https://shenyiqing.xin",
    "https://47.103.143.152",
]

# 日志配置
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# REST Framework配置
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# 缓存配置
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
