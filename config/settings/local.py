"""
本地开发环境配置
与生产环境保持一致，但使用本地数据库和开发工具
"""
from .base import *

# 开发环境特定配置  
DEBUG = True

# 允许的主机 - 包含本地IP地址
ALLOWED_HOSTS = [
    'localhost', 
    '127.0.0.1', 
    'testserver',
    '192.168.0.118',  # 本地网络IP
    '172.16.0.1',     # 虚拟网络IP
    '0.0.0.0',        # 允许所有IP（仅开发环境）
]

# 本地数据库配置 - 使用PostgreSQL与生产保持一致
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox_local',
        'USER': 'gaojie',  # macOS当前用户
        'PASSWORD': '',    # 本地无密码
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# 开发环境缓存配置 - 使用内存缓存（简化开发）
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

# 开发环境会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# 开发环境静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 开发环境邮件配置 - 输出到控制台
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 开发环境安全配置 - 关闭HTTPS相关
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 开发环境CORS配置 - 允许所有来源
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 开发环境日志配置 - 显示更多调试信息
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['apps.tools']['level'] = 'DEBUG'
LOGGING['loggers']['apps.users']['level'] = 'DEBUG'
LOGGING['handlers']['console']['level'] = 'DEBUG'

# 开发环境Celery配置 - 同步执行（简化开发）
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 开发环境API限制 - 更宽松的限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '10000/minute',
    'user': '10000/minute'
}

# 开发环境调试工具栏
if DEBUG:
    try:
        import debug_toolbar
        if 'debug_toolbar' not in INSTALLED_APPS:
            INSTALLED_APPS += ['debug_toolbar']
        if 'debug_toolbar.middleware.DebugToolbarMiddleware' not in MIDDLEWARE:
            MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
        INTERNAL_IPS = ['127.0.0.1', 'localhost', '192.168.0.118', '172.16.0.1']
        
        # 调试工具栏配置
        DEBUG_TOOLBAR_CONFIG = {
            'DISABLE_PANELS': [
                'debug_toolbar.panels.redirects.RedirectsPanel',
            ],
            'SHOW_TEMPLATE_CONTEXT': True,
        }
    except ImportError:
        pass

# 开发环境文件上传限制 - 与生产保持一致
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# 开发环境错误报告 - 显示详细错误
ADMINS = [('Developer', 'dev@qatoolbox.local')]
MANAGERS = ADMINS

# 开发环境时区和语言设置 - 与生产保持一致
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 开发环境模板调试
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

print(f"🔧 本地开发环境已加载")
print(f"📊 数据库: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}")
print(f"🌐 允许的主机: {ALLOWED_HOSTS}")
print(f"🐛 调试模式: {DEBUG}")
