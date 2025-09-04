#!/bin/bash

# QAToolBox 修复Django应用配置脚本
# 解决模块导入错误

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "QAToolBox 修复Django应用配置脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查应用目录结构
log_info "检查应用目录结构..."
ls -la apps/

# 2. 检查每个应用是否有__init__.py文件
log_info "检查应用初始化文件..."
for app in apps/*/; do
    if [ -d "$app" ]; then
        app_name=$(basename "$app")
        if [ ! -f "$app/__init__.py" ]; then
            log_info "为 $app_name 创建 __init__.py 文件"
            touch "$app/__init__.py"
        fi
    fi
done

# 3. 检查实际存在的应用
log_info "检查实际存在的应用..."
EXISTING_APPS=()
for app in apps/*/; do
    if [ -d "$app" ]; then
        app_name=$(basename "$app")
        if [ -f "$app/__init__.py" ]; then
            EXISTING_APPS+=("apps.$app_name")
            log_info "找到应用: apps.$app_name"
        fi
    fi
done

# 4. 创建正确的Django设置文件
log_info "创建正确的Django设置文件..."
cat > config/settings/production.py << 'EOF'
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'your-super-secret-key-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'captcha',
    'debug_toolbar',
    'apps.users',
    'apps.content',
    'apps.tools',
    'apps.share',
    'apps.social_sharing',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

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

# Database
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'qatoolbox_production'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'MFFtE6C4z4V1tUgqum+1sg=='),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site ID
SITE_ID = 1

# Logging configuration
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
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Debug toolbar
INTERNAL_IPS = ['127.0.0.1', '::1']
EOF

log_success "Django设置文件修复完成"

# 5. 测试Django设置
log_info "测试Django设置..."
timeout 10s /home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py check --settings=config.settings.production || {
    log_error "Django设置测试失败"
    exit 1
}

# 6. 更新supervisor配置
log_info "更新supervisor配置..."
cat > /etc/supervisor/conf.d/qatoolbox.conf << 'EOF'
[program:qatoolbox]
command=/home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py runserver 0.0.0.0:8000 --settings=config.settings.production
directory=/home/admin/QAToolbox
user=admin
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/app.log
stderr_logfile=/var/log/qatoolbox/error.log
environment=DB_NAME="qatoolbox_production",DB_USER="qatoolbox",DB_PASSWORD="MFFtE6C4z4V1tUgqum+1sg==",DB_HOST="localhost",DB_PORT="5432",DB_ENGINE="django.db.backends.postgresql",DJANGO_SETTINGS_MODULE="config.settings.production"
EOF

# 7. 重新加载supervisor配置
log_info "重新加载supervisor配置..."
supervisorctl reread
supervisorctl update

# 8. 启动应用
log_info "启动应用..."
supervisorctl start qatoolbox

# 9. 等待启动
log_info "等待应用启动..."
sleep 15

# 10. 检查状态
log_info "检查应用状态..."
supervisorctl status qatoolbox

# 11. 测试应用访问
log_info "测试应用访问..."
sleep 5
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "应用访问测试成功！"
else
    log_warning "应用访问测试失败，检查日志..."
    tail -n 20 /var/log/qatoolbox/app.log
    tail -n 20 /var/log/qatoolbox/error.log
    tail -n 20 /var/log/qatoolbox/django.log
fi

# 12. 配置Nginx
log_info "配置Nginx..."
if nginx -t; then
    systemctl reload nginx
    log_success "Nginx配置成功！"
else
    log_error "Nginx配置失败"
    exit 1
fi

log_success "=========================================="
log_success "Django应用配置修复完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo
log_info "🛠️  服务管理:"
echo "  - Supervisor状态: supervisorctl status qatoolbox"
echo "  - Supervisor重启: supervisorctl restart qatoolbox"
echo "  - Supervisor日志: supervisorctl tail qatoolbox"
echo "  - Django日志: tail -f /var/log/qatoolbox/django.log"
echo "  - 应用日志: tail -f /var/log/qatoolbox/app.log"
echo "  - 错误日志: tail -f /var/log/qatoolbox/error.log"
echo
log_success "现在你的应用应该可以正常访问了！"
log_success "=========================================="
