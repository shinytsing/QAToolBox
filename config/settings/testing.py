"""
测试环境配置
"""
from .base import *

# 测试环境配置
DEBUG = True
TESTING = True

# 测试环境数据库配置 - 支持PostgreSQL和SQLite
import os

# 如果设置了DATABASE_URL环境变量，使用PostgreSQL
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'test_qatoolbox'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'prefer',
            },
        }
    }
else:
    # 默认使用SQLite内存数据库
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'OPTIONS': {
                'timeout': 20,
            }
        }
    }

# 测试环境缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# 测试环境会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# 禁用迁移加速测试
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# 测试环境密码验证器（简化）
AUTH_PASSWORD_VALIDATORS = []

# 测试环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# 测试环境静态文件
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 测试环境媒体文件
MEDIA_ROOT = '/tmp/qatoolbox_test_media'

# 测试环境日志配置
LOGGING['handlers']['file']['filename'] = '/tmp/django_test.log'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps.tools']['level'] = 'WARNING'
LOGGING['loggers']['apps.users']['level'] = 'WARNING'

# 测试环境Celery配置
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 禁用调试工具栏
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
MIDDLEWARE = [mw for mw in MIDDLEWARE if 'debug_toolbar' not in mw]

# 测试环境CORS配置
CORS_ALLOW_ALL_ORIGINS = True

# 测试环境允许的主机
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# 测试环境文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB