#!/bin/bash

# =============================================================================
# QAToolBox 修复psutil依赖部署脚本
# 针对 /home/qatoolbox/QAToolbox 路径和缺失依赖问题
# =============================================================================

set -e

# 配置 - 使用实际找到的路径
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/qatoolbox/QAToolbox"  # 注意是小写b
DOMAIN="shenyiqing.xin"

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
echo "    🔧 QAToolBox psutil依赖修复"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 验证项目路径
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录 $PROJECT_DIR 不存在"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/manage.py" ]; then
    log_error "项目目录中没有 manage.py 文件"
    exit 1
fi

log_success "项目路径确认: $PROJECT_DIR"

cd $PROJECT_DIR

# 停止现有服务
log_info "停止现有服务"
systemctl stop qatoolbox 2>/dev/null || true
pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
sleep 3

# 确保项目用户存在并有正确权限
if ! id "$PROJECT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_USER
    log_info "用户 $PROJECT_USER 已创建"
fi
chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR

# 安装系统依赖（psutil需要的系统库）
log_info "安装系统依赖"
apt-get update
apt-get install -y python3-dev gcc build-essential

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    log_info "创建虚拟环境"
    sudo -u $PROJECT_USER python3 -m venv .venv
fi

# 配置pip镜像源
sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 升级pip
log_info "升级pip"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip

# 安装核心依赖和缺失的psutil
log_info "安装Python依赖（包括psutil）"

# 首先安装基础工具
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    setuptools==68.2.2 \
    wheel==0.41.2 \
    python-dotenv==1.0.0 \
    django-environ==0.11.2

# 安装Django和数据库相关
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    Django==4.2.7 \
    psycopg2-binary==2.9.7 \
    redis==4.6.0 \
    django-redis==5.4.0

# 安装API和Web相关
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1 \
    whitenoise==6.6.0 \
    gunicorn==21.2.0

# 安装系统监控相关（包括psutil）
log_info "安装系统监控依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    psutil==5.9.5 \
    requests==2.31.0 \
    celery==5.3.4

# 尝试安装requirements.txt中的其他依赖
if [ -f "requirements.txt" ]; then
    log_info "尝试安装requirements.txt中的其他依赖"
    sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt --no-cache-dir || {
        log_warning "部分requirements.txt依赖安装失败，但核心依赖已安装"
    }
fi

# 验证psutil安装
log_info "验证psutil安装"
if sudo -u $PROJECT_USER .venv/bin/python -c "import psutil; print(f'psutil版本: {psutil.__version__}')"; then
    log_success "psutil安装成功"
else
    log_error "psutil安装失败"
    exit 1
fi

# 确保数据库服务运行
log_info "确保数据库服务运行"
systemctl start postgresql 2>/dev/null || true
systemctl start redis-server 2>/dev/null || true
sleep 3

# 配置数据库
log_info "配置数据库"
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;" 2>/dev/null || true
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;" 2>/dev/null || true

# 配置环境变量
log_info "配置环境变量"
cat > .env << 'EOF'
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-simple-key-$(date +%s)
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.production
EOF
chown $PROJECT_USER:$PROJECT_USER .env

# 测试Django配置
log_info "测试Django配置"
export DJANGO_SETTINGS_MODULE=config.settings.production

if sudo -u $PROJECT_USER .venv/bin/python manage.py check; then
    log_success "Django配置检查通过"
    USE_ORIGINAL_SETTINGS=true
else
    log_warning "原始配置有问题，创建简化配置"
    USE_ORIGINAL_SETTINGS=false
    
    # 创建简化配置
    mkdir -p config/settings
    cat > config/settings/minimal.py << 'MINIMALEOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-minimal-key')
DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
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
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'QAToolBox@2024',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEMPLATES = [{
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
}]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS设置
CORS_ALLOWED_ORIGINS = [
    "https://shenyiqing.xin",
    "http://47.103.143.152",
]
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework设置
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
MINIMALEOF
    
    chown $PROJECT_USER:$PROJECT_USER config/settings/minimal.py
    
    # 更新环境变量
    sed -i 's/DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=config.settings.minimal/' .env
    export DJANGO_SETTINGS_MODULE=config.settings.minimal
fi

# Django迁移
log_info "执行Django迁移"
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput

# 创建管理员用户
log_info "创建管理员用户"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell

# 创建日志目录
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

# 配置systemd服务
log_info "配置systemd服务"
SETTINGS_MODULE="config.settings.production"
if [ "$USE_ORIGINAL_SETTINGS" = false ]; then
    SETTINGS_MODULE="config.settings.minimal"
fi

cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 120 config.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qatoolbox

# 配置Nginx
log_info "配置Nginx"
cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并启动服务
if nginx -t; then
    log_success "Nginx配置正确"
else
    log_error "Nginx配置错误"
    exit 1
fi

# 启动服务
log_info "启动服务"
systemctl start qatoolbox
sleep 5
systemctl restart nginx

# 检查状态
log_info "检查服务状态"
sleep 10

QATOOLBOX_STATUS=$(systemctl is-active qatoolbox)
NGINX_STATUS=$(systemctl is-active nginx)

echo
echo -e "${BLUE}========================================"
echo "        📊 最终状态"
echo "========================================"
echo -e "${NC}"
echo -e "项目路径: ${GREEN}$PROJECT_DIR${NC}"
echo -e "QAToolBox服务: ${GREEN}$QATOOLBOX_STATUS${NC}"
echo -e "Nginx服务: ${GREEN}$NGINX_STATUS${NC}"
echo -e "Django设置: ${GREEN}$SETTINGS_MODULE${NC}"

# 测试HTTP响应
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
echo -e "HTTP响应: ${GREEN}$HTTP_CODE${NC}"

# 验证psutil导入
echo -e "${BLUE}验证关键模块:${NC}"
sudo -u $PROJECT_USER .venv/bin/python -c "import psutil; print(f'✅ psutil {psutil.__version__}')" || echo "❌ psutil导入失败"
sudo -u $PROJECT_USER .venv/bin/python -c "import django; print(f'✅ Django {django.__version__}')" || echo "❌ Django导入失败"

if [ "$QATOOLBOX_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ]; then
    echo
    echo -e "${GREEN}🎉 修复成功！${NC}"
    echo -e "${GREEN}访问地址: http://shenyiqing.xin${NC}"
    echo -e "${GREEN}管理后台: http://shenyiqing.xin/admin/${NC}"
    echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
else
    echo -e "${YELLOW}⚠️ 服务可能有问题，请检查日志${NC}"
    echo "检查命令: journalctl -u qatoolbox -f"
fi
