"""
阿里云环境专用配置
适用于SQLite数据库的简化生产环境配置
"""
from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 (初始部署时关闭SSL重定向)
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 使用SQLite数据库（适合小型部署）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,
        },
    }
}

# 简化缓存配置（使用本地内存缓存）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 静态文件配置
STATIC_ROOT = '/opt/QAToolbox/staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 重写静态文件目录配置，避免重复文件警告
STATICFILES_DIRS = [
    BASE_DIR / 'src/static',  # 只使用src/static目录
]

# 邮件配置（使用控制台后端用于测试）
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/qatoolbox_django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.tools': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.users': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Celery配置（禁用用于简化部署）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# API限制
if 'rest_framework' in INSTALLED_APPS:
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '100/minute',
        'user': '1000/minute'
    }

# CORS配置
CORS_ALLOWED_ORIGINS = [
    "http://47.103.143.152:8000",
    "https://47.103.143.152:8000",
    "http://localhost:8000",
]

# 允许的主机
ALLOWED_HOSTS = [
    '47.103.143.152',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
]

# 安全头配置
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000

# 媒体文件配置
MEDIA_ROOT = '/opt/QAToolbox/media'
MEDIA_URL = '/media/'

# 时区配置
USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'
