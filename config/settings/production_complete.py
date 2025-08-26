"""
QAToolBox 完整生产环境配置
保证所有功能完整性，解决依赖问题
"""
import os
from pathlib import Path

# 尝试导入环境变量库
try:
    import environ
    env = environ.Env(DEBUG=(bool, False))
    USE_ENVIRON = True
except ImportError:
    try:
        from decouple import config
        USE_ENVIRON = False
    except ImportError:
        # 使用默认环境变量
        config = lambda key, default=None, cast=str: cast(os.environ.get(key, default))
        USE_ENVIRON = False

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 安全设置
if USE_ENVIRON:
    SECRET_KEY = env('SECRET_KEY', default='django-modeshift-production-key')
    DEBUG = env('DEBUG', default=False)
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
else:
    SECRET_KEY = config('SECRET_KEY', default='django-modeshift-production-key')
    DEBUG = config('DEBUG', default=False, cast=bool)
    ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

# 确保关键主机在列表中
essential_hosts = ['47.103.143.152', 'shenyiqing.xin', 'www.shenyiqing.xin', 'localhost', '127.0.0.1']
for host in essential_hosts:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# 应用配置 - 完整功能
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
]

# 尝试添加可选的第三方应用
optional_third_party = [
    'corsheaders',
    'django_extensions',
]

for app in optional_third_party:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
    except ImportError:
        pass

LOCAL_APPS = []

# 检查并添加本地应用
local_app_paths = [
    'apps.users',
    'apps.tools', 
    'apps.content',
    'apps.share',
]

for app_path in local_app_paths:
    try:
        app_module = __import__(app_path, fromlist=[''])
        LOCAL_APPS.append(app_path)
    except ImportError:
        # 检查应用目录是否存在
        app_dir = BASE_DIR / app_path.replace('.', '/')
        if app_dir.exists():
            LOCAL_APPS.append(app_path)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]

# 添加CORS中间件（如果可用）
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(-1, 'corsheaders.middleware.CorsMiddleware')

MIDDLEWARE.extend([
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

# 添加自定义中间件（如果存在）
custom_middleware = [
    'apps.users.middleware.UserActivityMiddleware',
    'middleware.performance.PerformanceMiddleware',
]

for middleware in custom_middleware:
    try:
        __import__(middleware.rsplit('.', 1)[0], fromlist=[middleware.rsplit('.', 1)[1]])
        MIDDLEWARE.append(middleware)
    except ImportError:
        pass

ROOT_URLCONF = 'urls'

# 模板设置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'src' / 'templates',
        ],
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

WSGI_APPLICATION = 'QAToolBox.wsgi.application'

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 尝试使用PostgreSQL（如果配置了）
try:
    if USE_ENVIRON:
        db_url = env('DATABASE_URL', default=None)
    else:
        db_url = config('DATABASE_URL', default=None)
    
    if db_url and 'postgres' in db_url:
        import dj_database_url
        DATABASES['default'] = dj_database_url.parse(db_url)
except (ImportError, Exception):
    pass

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'modeshift-cache',
    }
}

# 尝试使用Redis缓存
try:
    import redis
    if USE_ENVIRON:
        redis_url = env('REDIS_URL', default=None)
    else:
        redis_url = config('REDIS_URL', default=None)
    
    if redis_url:
        CACHES['default'] = {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': redis_url,
        }
except ImportError:
    pass

# 密码验证
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件设置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 静态文件存储
try:
    import whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
except ImportError:
    pass

# 静态文件目录
STATICFILES_DIRS = []
potential_static_dirs = [
    BASE_DIR / 'src' / 'static',
    BASE_DIR / 'static',
]

for static_dir in potential_static_dirs:
    if static_dir.exists():
        STATICFILES_DIRS.append(static_dir)

# 媒体文件设置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS设置（如果可用）
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True

# 安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = [
    'http://shenyiqing.xin',
    'http://47.103.143.152',
    'https://shenyiqing.xin', 
    'https://47.103.143.152',
]

# 会话设置
SESSION_COOKIE_AGE = 86400 * 30  # 30天
SESSION_SAVE_EVERY_REQUEST = True

# 日志配置
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

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
            'filename': BASE_DIR / 'logs' / 'django.log',
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
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ],
    }

# Celery配置（如果可用）
try:
    import celery
    if USE_ENVIRON:
        CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
    else:
        CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
    
    CELERY_RESULT_BACKEND = CELERY_BROKER_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
except ImportError:
    pass

# 自定义用户模型（如果存在）
try:
    from apps.users.models import User
    AUTH_USER_MODEL = 'users.User'
except (ImportError, Exception):
    pass

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if USE_ENVIRON:
    email_host = env('EMAIL_HOST', default=None)
    if email_host:
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        EMAIL_HOST = email_host
        EMAIL_PORT = env('EMAIL_PORT', default=587, cast=int)
        EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True, cast=bool)
        EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
        EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
        DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# 文件上传限制
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 开发环境特定设置
if DEBUG:
    # 开发工具
    if 'django_extensions' in THIRD_PARTY_APPS:
        INSTALLED_APPS.append('django_extensions')
    
    # 内部IP
    INTERNAL_IPS = ['127.0.0.1', 'localhost']

print(f"✅ ModeShift 配置加载完成")
print(f"📦 已安装应用: {len(INSTALLED_APPS)} 个")
print(f"🔧 中间件: {len(MIDDLEWARE)} 个")
print(f"📁 静态文件目录: {len(STATICFILES_DIRS)} 个")
