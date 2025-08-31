"""
QAToolBox 阿里云生产环境配置
专为阿里云服务器和中国地区优化
"""
import os
import sys
from pathlib import Path
import environ

# 首先定义BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 添加apps目录到Python路径
sys.path.append(str(BASE_DIR / 'apps'))

# 初始化environ
env = environ.Env(
    DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, 'django-insecure-change-me-in-production'),
    ALLOWED_HOSTS=(str, 'shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1'),
    DB_NAME=(str, 'qatoolbox'),
    DB_USER=(str, 'qatoolbox'),
    DB_PASSWORD=(str, ''),
    DB_HOST=(str, 'localhost'),
    DB_PORT=(int, 5432),
    REDIS_URL=(str, 'redis://localhost:6379/0'),
)

# 尝试加载.env文件
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# 允许的主机
ALLOWED_HOSTS_STR = env('ALLOWED_HOSTS')
if isinstance(ALLOWED_HOSTS_STR, str):
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ['shenyiqing.xin', 'www.shenyiqing.xin', '47.103.143.152', 'localhost', '127.0.0.1']

# 添加testserver用于测试
ALLOWED_HOSTS.append('testserver')

# 站点配置
SITE_ID = 1

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # 用于CAPTCHA
]

# 第三方应用 - 按重要性和依赖关系排序
THIRD_PARTY_APPS = []

# 根据安装情况添加第三方应用
optional_apps = [
    'rest_framework',
    'corsheaders', 
    'captcha',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'channels',
    'django_extensions',
]

for app in optional_apps:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
    except ImportError:
        print(f"Warning: {app} not installed, skipping...")

# 本地应用
LOCAL_APPS = []
local_app_candidates = [
    'apps.users',
    'apps.content', 
    'apps.tools',
    'apps.share',
]

for app in local_app_candidates:
    app_path = BASE_DIR / app.replace('.', '/')
    if app_path.exists():
        LOCAL_APPS.append(app)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 静态文件服务
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 根据安装情况添加中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

# 安全地添加自定义中间件
custom_middlewares = [
    'apps.users.middleware.SessionExtensionMiddleware',
]

for middleware in custom_middlewares:
    try:
        module_path = '.'.join(middleware.split('.')[:-1])
        __import__(module_path)
        MIDDLEWARE.append(middleware)
    except ImportError:
        print(f"Warning: {middleware} not found, skipping...")

ROOT_URLCONF = 'urls'

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
    
    # Channel Layers配置
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [env('REDIS_URL')],
            },
        } if 'channels_redis' in [app for app in THIRD_PARTY_APPS] else {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'connect_timeout': 60,
            'sslmode': 'prefer',
        },
        'CONN_MAX_AGE': 60,
    }
}

# Redis缓存配置
REDIS_URL = env('REDIS_URL')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'qatoolbox',
        'VERSION': 1,
    }
}

# 会话配置 - 使用数据库存储（更可靠）
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 14天
SESSION_COOKIE_SECURE = False  # 初期设为False，配置SSL后改为True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = False

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/qatoolbox/static/'

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
MEDIA_ROOT = '/var/www/qatoolbox/media/'

# 确保媒体目录存在
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 日志配置
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
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/qatoolbox/django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
Path('/var/log/qatoolbox').mkdir(parents=True, exist_ok=True)

# Django REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',
        ],
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1000/hour',
            'user': '10000/hour',
        },
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    }

# CORS配置
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOWED_ORIGINS = [
        "https://shenyiqing.xin",
        "https://www.shenyiqing.xin",
        "http://47.103.143.152",
    ]
    
    CORS_ALLOW_CREDENTIALS = True
    
    CORS_ALLOWED_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]

# Crispy Forms配置
if 'crispy_forms' in THIRD_PARTY_APPS:
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

# 验证码配置
if 'captcha' in THIRD_PARTY_APPS:
    CAPTCHA_IMAGE_SIZE = (120, 40)
    CAPTCHA_LENGTH = 4
    CAPTCHA_TIMEOUT = 5
    CAPTCHA_BACKGROUND_COLOR = '#ffffff'
    CAPTCHA_FOREGROUND_COLOR = '#333333'

# 安全配置 (初期保守设置，后续可以加强)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # 允许在同域名下使用iframe

# SSL配置 (初期关闭，配置SSL证书后开启)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'https://shenyiqing.xin',
    'https://www.shenyiqing.xin',
    'http://47.103.143.152',
    'http://47.103.143.152:8000',
]

# 邮件配置 (可选)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # 开发时使用控制台

# Celery配置 (如果需要)
if 'celery' in [app.split('.')[-1] for app in INSTALLED_APPS]:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# 性能优化
if not DEBUG:
    # 数据库连接池配置移除，MAX_CONNS不是psycopg2的有效选项
    # 如果需要连接池，应该使用django-db-connection-pool或类似的第三方包
    pass
    
    # 缓存模板加载器 - 关闭APP_DIRS，使用自定义loaders
    TEMPLATES[0]['APP_DIRS'] = False
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# 中国地区特殊配置
CHINA_TIMEZONE = 'Asia/Shanghai'
CHINA_LANGUAGE = 'zh-hans'

# 自定义设置
CUSTOM_SETTINGS = {
    'DEPLOYMENT_TYPE': 'aliyun_production',
    'REGION': 'china',
    'SERVER_LOCATION': 'aliyun',
    'VERSION': '1.0.0',
}

print(f"QAToolBox 阿里云生产环境配置加载完成")
print(f"安装的应用数量: {len(INSTALLED_APPS)}")
print(f"Django应用: {len(DJANGO_APPS)}")
print(f"第三方应用: {len(THIRD_PARTY_APPS)}")
print(f"本地应用: {len(LOCAL_APPS)}")
