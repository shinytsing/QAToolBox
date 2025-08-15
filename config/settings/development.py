"""
开发环境配置
"""
from .base import *

# 开发环境特定配置
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

# 数据库配置 - 开发环境使用SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 30,  # 增加超时时间
            'check_same_thread': False,  # 允许多线程访问
        },
        'ATOMIC_REQUESTS': False,  # 禁用自动事务以提高并发性能
    }
}

# 开发环境禁用HTTPS
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# 开发环境允许所有CORS
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 开发环境日志级别 - 减少debug信息输出
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps.tools']['level'] = 'INFO'
LOGGING['loggers']['apps.users']['level'] = 'INFO'
LOGGING['handlers']['console']['level'] = 'WARNING'

# 开发环境使用本地内存缓存（支持验证码功能）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    },
    'session': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'session-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    }
}

# 开发环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 开发环境静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 开发环境调试工具栏
if DEBUG:
    try:
        import debug_toolbar
        if 'debug_toolbar' not in INSTALLED_APPS:
            INSTALLED_APPS += ['debug_toolbar']
        if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE:
            MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass

# 开发环境Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 开发环境API限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/minute',
    'user': '10000/minute'
}
