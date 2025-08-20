"""
测试环境配置
"""
import sys
from .base import *

# 测试环境标识
DEBUG = True
TESTING = True

# 使用内存数据库进行测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# 使用内存缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# 禁用密码哈希以加快测试速度
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 禁用日志输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 禁用静态文件收集
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 禁用媒体文件处理
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# 禁用Celery任务
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# 禁用邮件发送
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# 禁用外部API调用
MOCK_EXTERNAL_APIS = True

# 测试专用设置
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 禁用中间件以减少测试开销
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 禁用不必要的应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.tools',
    'apps.users',
    'apps.content',
]

# 禁用安全设置
SECURE_SSL_REDIRECT = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# 测试数据库配置
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
