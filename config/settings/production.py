"""
生产环境配置
"""
from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 (初始部署时关闭SSL重定向，配置SSL后再开启)
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') if SECURE_SSL_REDIRECT else None
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 生产环境数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
            'sslmode': 'prefer',
        },
    }
}

# 生产环境缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
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

# 生产环境Celery配置
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# 生产环境API限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/minute',
    'user': '1000/minute'
}

# 生产环境CORS配置
CORS_ALLOWED_ORIGINS = [
    "https://shenyiqing.xin",
    "https://www.shenyiqing.xin",
]

# 允许的主机
ALLOWED_HOSTS = [
    'shenyiqing.xin',
    'www.shenyiqing.xin',
    '47.103.143.152',
    'localhost',
]

# 生产环境安全头
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

# 生产环境文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024  # 50MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
