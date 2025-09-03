"""
生产环境配置
"""
from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 - Cloudflare SSL
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 生产环境数据库配置 - 使用PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox_production'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# 生产环境缓存配置 - 使用本地内存缓存简化部署  
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# 生产环境会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 生产环境静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 生产环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@qatoolbox.com')

# 生产环境日志配置
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps.tools']['level'] = 'INFO'
LOGGING['loggers']['apps.users']['level'] = 'INFO'

# 生产环境Celery配置 - 简化为同步执行
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'django-db://'
CELERY_RESULT_BACKEND = 'django-db'

# 生产环境API限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/minute',
    'user': '1000/minute'
}

# 生产环境CORS配置 - Cloudflare域名
CORS_ALLOWED_ORIGINS = [
    "http://shenyiqing.xin",
    "https://shenyiqing.xin",
    "http://www.shenyiqing.xin", 
    "https://www.shenyiqing.xin",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://192.168.0.118:8000",
]

# 允许的主机 - 配置外网访问
ALLOWED_HOSTS = [
    'shenyiqing.xin',
    'www.shenyiqing.xin',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '192.168.0.118',  # 本机内网IP
    '*',  # 允许所有主机用于外网访问
]

# 生产环境安全头 - 移除导致警告的COOP头
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'
# SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'  # 禁用避免警告

# 生产环境文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000
