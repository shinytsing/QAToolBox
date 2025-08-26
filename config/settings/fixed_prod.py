"""
QAToolBox 生产环境最简化配置 - 修复启动问题
"""
import os
from pathlib import Path

# 基础目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 安全密钥
SECRET_KEY = 'django-insecure-prod-key-replace-in-real-production-123456789'

# 调试模式关闭
DEBUG = False
ALLOWED_HOSTS = ['*']

# 最简化应用配置
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # 核心应用
    'apps.tools',
    'apps.users', 
    'apps.content',
]

# 最简化中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# PostgreSQL数据库配置 (trust认证模式)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Redis缓存配置 (简化版)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/home/qatoolbox/QAToolBox/staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'src' / 'static',
    BASE_DIR / 'static',
]

# 媒体文件配置  
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/qatoolbox/QAToolBox/media'

# 默认主键字段
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 移除数据库路由器 (解决应用启动问题)
DATABASE_ROUTERS = []

# SSL配置
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB

# 基础日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

