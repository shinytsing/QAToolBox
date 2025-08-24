"""
开发环境配置
"""
from .base import *

# 开发环境特定配置
DEBUG = True

# 允许的主机 - 添加局域网访问支持
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver', '192.168.0.118', '172.16.0.1', '0.0.0.0', '*']

# 数据库配置 - 开发环境使用PostgreSQL（与生产保持一致）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox_local'),
        'USER': os.environ.get('DB_USER', 'gaojie'),  # macOS当前用户
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),    # 本地无密码
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# HTTPS配置
SECURE_SSL_REDIRECT = False  # 开发环境不强制重定向
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# 开发环境允许所有CORS - 支持局域网访问
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.0.118:8000",
    "http://172.16.0.1:8000",
    "https://localhost:8443",
    "https://127.0.0.1:8443", 
    "https://192.168.0.118:8443",
    "https://172.16.0.1:8443",
]

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

# 添加django-extensions支持
if 'django_extensions' not in INSTALLED_APPS:
    INSTALLED_APPS += ['django_extensions']

# 开发环境Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 开发环境API限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/minute',
    'user': '10000/minute'
}
