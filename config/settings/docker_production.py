"""
QAToolBox Docker生产环境配置
专为Docker容器化部署优化
"""
import os
import sys
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

# 从环境变量读取配置
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-docker-production-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
ALLOWED_HOSTS.extend(['testserver', 'web', 'localhost'])

# 站点配置
SITE_ID = 1

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# Django核心应用
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

# 第三方应用 - 安全地添加
THIRD_PARTY_APPS = []
optional_third_party = [
    'rest_framework',
    'corsheaders', 
    'captcha',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'channels',
    'django_extensions',
]

for app in optional_third_party:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
        print(f"✅ 已添加第三方应用: {app}")
    except ImportError:
        print(f"⚠️ 跳过未安装的应用: {app}")

# 本地应用 - 安全地添加
LOCAL_APPS = []
local_app_candidates = [
    'apps.users',
    'apps.content', 
    'apps.tools',
    'apps.share',
]

for app in local_app_candidates:
    app_path = BASE_DIR / app.replace('.', '/')
    if app_path.exists() and (app_path / '__init__.py').exists():
        LOCAL_APPS.append(app)
        print(f"✅ 已添加本地应用: {app}")
    else:
        print(f"⚠️ 跳过不存在的应用: {app}")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 安全地添加中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

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

WSGI_APPLICATION = 'wsgi.application'

# Channels配置 (如果安装了)
if 'channels' in THIRD_PARTY_APPS:
    ASGI_APPLICATION = 'asgi.application'
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379/0')],
            },
        },
    }

# 数据库配置 - 使用PostgreSQL [[memory:7978808]]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,
    }
}

# Redis缓存配置
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'qatoolbox',
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 14天
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'

# 收集静态文件的目录
STATICFILES_DIRS = []
static_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'src' / 'static',
]

for static_dir in static_dirs:
    if static_dir.exists():
        STATICFILES_DIRS.append(static_dir)

# 静态文件存储配置
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1000/hour',
            'user': '10000/hour',
        },
    }

# CORS配置
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOWED_ORIGINS = [
        "https://shenyiqing.xin",
        "https://www.shenyiqing.xin",
        "http://47.103.143.152",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS = True

# Crispy Forms配置
if 'crispy_forms' in THIRD_PARTY_APPS:
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

# 验证码配置
if 'captcha' in THIRD_PARTY_APPS:
    CAPTCHA_IMAGE_SIZE = (120, 40)
    CAPTCHA_LENGTH = 4
    CAPTCHA_TIMEOUT = 5

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'https://shenyiqing.xin',
    'https://www.shenyiqing.xin',
    'http://47.103.143.152',
    'http://localhost:8000',
]

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery配置
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

print(f"✅ QAToolBox Docker配置加载完成")
print(f"安装的应用数量: {len(INSTALLED_APPS)}")
print(f"Django应用: {len(DJANGO_APPS)}")
print(f"第三方应用: {len(THIRD_PARTY_APPS)}")
print(f"本地应用: {len(LOCAL_APPS)}")
