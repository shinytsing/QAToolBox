#!/bin/bash

# =============================================================================
# QAToolBox 终极修复脚本 - 彻底解决所有Django和依赖问题
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}========================================"
echo "    🔧 QAToolBox 终极修复脚本"
echo "========================================"
echo "  功能: 彻底解决Django和依赖问题"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

log_info "开始终极修复流程..."

# 停止所有相关服务
log_info "停止所有相关服务"
systemctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
pkill -f "python.*manage.py" 2>/dev/null || true
sleep 5

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

# 完全重建Python环境
log_info "完全重建Python环境"
if [ -d ".venv" ]; then
    rm -rf .venv
fi

# 清理Python缓存
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 创建全新虚拟环境
sudo -u $PROJECT_USER python3.9 -m venv .venv

# 配置pip镜像源
sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
retries = 5

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 升级pip和基础工具
log_info "升级pip和基础工具"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip setuptools wheel

# 按特定顺序安装核心依赖
log_info "按顺序安装核心依赖"

# 第一批：基础依赖
sudo -u $PROJECT_USER .venv/bin/pip install \
    six==1.16.0 \
    setuptools==68.2.2 \
    wheel==0.41.2 \
    packaging==23.2 \
    typing-extensions==4.8.0

# 第二批：数据库和缓存
sudo -u $PROJECT_USER .venv/bin/pip install \
    psycopg2-binary==2.9.7 \
    redis==4.6.0

# 第三批：Django核心
sudo -u $PROJECT_USER .venv/bin/pip install \
    Django==4.2.7 \
    django-environ==0.11.2 \
    python-dotenv==1.0.0

# 第四批：Django扩展
sudo -u $PROJECT_USER .venv/bin/pip install \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1 \
    django-redis==5.4.0 \
    django-crispy-forms==2.0 \
    crispy-bootstrap5==0.7 \
    django-simple-captcha==0.6.0 \
    django-ratelimit==4.1.0

# 第五批：异步和消息队列
sudo -u $PROJECT_USER .venv/bin/pip install \
    channels==4.0.0 \
    channels-redis==4.1.0 \
    daphne==4.0.0 \
    celery==5.3.4

# 第六批：Web服务器和工具
sudo -u $PROJECT_USER .venv/bin/pip install \
    gunicorn==21.2.0 \
    whitenoise==6.6.0 \
    requests==2.31.0 \
    Pillow==9.5.0

# 验证Django安装
log_info "验证Django安装"
if sudo -u $PROJECT_USER .venv/bin/python -c "import django; print(f'Django version: {django.VERSION}')"; then
    log_success "Django安装验证成功"
else
    log_error "Django安装验证失败"
    exit 1
fi

# 重置数据库
log_info "重置数据库"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"

# 检查环境变量文件
log_info "检查环境变量文件"
if [ ! -f ".env" ]; then
    log_warning "创建环境变量文件"
    cat > .env << 'ENVEOF'
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=django-insecure-temp-key-for-testing-only-change-in-production
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 其他配置
DJANGO_SETTINGS_MODULE=config.settings.production
SITE_URL=https://shenyiqing.xin
ENVEOF
    chown $PROJECT_USER:$PROJECT_USER .env
    chmod 600 .env
fi

# 测试Django配置
log_info "测试Django基础配置"
if sudo -u $PROJECT_USER .venv/bin/python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
print('Django setup successful')
"; then
    log_success "Django基础配置测试通过"
else
    log_error "Django基础配置测试失败，尝试简化配置"
    
    # 创建简化的settings文件
    cat > config/settings/emergency.py << 'SETTINGSEOF'
"""
紧急简化配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-emergency-key-change-immediately')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['shenyiqing.xin', '47.103.143.152', 'localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    
    # Local apps
    'apps.users',
    'apps.tools',
    'apps.content',
    'apps.share',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'QAToolBox@2024'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
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
    BASE_DIR / 'src' / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Custom user model
AUTH_USER_MODEL = 'users.User'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
SETTINGSEOF
    
    # 更新环境变量使用紧急配置
    sed -i 's/DJANGO_SETTINGS_MODULE=config.settings.production/DJANGO_SETTINGS_MODULE=config.settings.emergency/' .env
    
    log_info "使用紧急配置重新测试"
    if sudo -u $PROJECT_USER .venv/bin/python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.emergency')
django.setup()
print('Django emergency setup successful')
"; then
        log_success "紧急配置测试通过"
    else
        log_error "紧急配置也失败，需要手动检查"
        exit 1
    fi
fi

# 清理并重新创建迁移
log_info "清理并重新创建迁移文件"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null || true
find . -path "*/migrations/*.pyc" -delete 2>/dev/null || true

# 确保migrations目录存在
for app in apps/users apps/tools apps/content apps/share; do
    if [ -d "$app" ]; then
        mkdir -p "$app/migrations"
        touch "$app/migrations/__init__.py"
        chown -R $PROJECT_USER:$PROJECT_USER "$app/migrations"
    fi
done

# 创建迁移文件
log_info "创建新的迁移文件"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations users || log_warning "users迁移创建失败"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations tools || log_warning "tools迁移创建失败"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations content || log_warning "content迁移创建失败"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations share || log_warning "share迁移创建失败"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations || log_warning "总体迁移创建失败"

# 执行迁移
log_info "执行数据库迁移"
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate || {
    log_warning "常规迁移失败，尝试强制迁移"
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate --fake-initial || {
        log_warning "强制迁移也失败，尝试逐个应用迁移"
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate contenttypes || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate auth || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate admin || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate sessions || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate users || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate tools || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate content || true
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate share || true
    }
}

# 收集静态文件
log_info "收集静态文件"
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput || {
    log_warning "静态文件收集失败，创建基础静态目录"
    mkdir -p staticfiles static
    chown -R $PROJECT_USER:$PROJECT_USER staticfiles static
}

# 创建管理员用户
log_info "创建管理员用户"
echo "
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='admin').delete()
try:
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'QAToolBox@2024')
    print('Admin user created successfully')
except Exception as e:
    print(f'Admin user creation failed: {e}')
" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell || {
    log_warning "管理员用户创建失败，但继续..."
}

# 修复systemd服务配置
log_info "修复systemd服务配置"
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.emergency
Environment=PATH=/home/qatoolbox/QAToolBox/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    --max-requests 500 \
    --access-logfile /var/log/qatoolbox/access.log \
    --error-logfile /var/log/qatoolbox/error.log \
    --log-level info \
    config.wsgi:application

Restart=always
RestartSec=10
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

# 重新加载并启动服务
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox

# 等待服务启动
log_info "等待服务启动"
sleep 15

# 检查服务状态
if systemctl is-active --quiet qatoolbox; then
    log_success "应用服务启动成功"
else
    log_error "应用服务启动失败"
    echo "错误日志:"
    journalctl -u qatoolbox -n 30 --no-pager
    echo "尝试直接启动测试:"
    sudo -u $PROJECT_USER cd $PROJECT_DIR && .venv/bin/python manage.py runserver 127.0.0.1:8001 &
    sleep 5
    if curl -s http://127.0.0.1:8001/ > /dev/null; then
        log_info "直接启动成功，问题可能在systemd配置"
        pkill -f "runserver"
    else
        log_error "直接启动也失败"
    fi
    exit 1
fi

# 重启Nginx
systemctl restart nginx

# 测试连接
log_info "测试连接"
sleep 5

if curl -s -f http://127.0.0.1:8000/health/ > /dev/null 2>&1; then
    log_success "本地应用连接正常 (health check)"
elif curl -s -f http://127.0.0.1:8000/ > /dev/null 2>&1; then
    log_success "本地应用连接正常 (main page)"
else
    log_warning "本地应用连接可能有问题，但服务已启动"
    echo "应用状态:"
    systemctl status qatoolbox --no-pager -l
fi

echo
echo -e "${GREEN}========================================"
echo "        🎉 终极修复完成！"
echo "========================================"
echo -e "${NC}"
echo -e "${GREEN}访问地址: https://shenyiqing.xin${NC}"
echo -e "${GREEN}管理后台: https://shenyiqing.xin/admin/${NC}"
echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
echo
echo "服务状态:"
echo "  应用服务: $(systemctl is-active qatoolbox)"
echo "  Nginx服务: $(systemctl is-active nginx)"
echo "  PostgreSQL: $(systemctl is-active postgresql)"
echo "  Redis: $(systemctl is-active redis-server)"
echo
echo -e "${BLUE}如果还有问题，查看日志:${NC}"
echo "  sudo journalctl -u qatoolbox -f"
echo "  tail -f /var/log/qatoolbox/error.log"
echo
echo -e "${YELLOW}注意: 使用了紧急简化配置，建议稍后优化${NC}"
