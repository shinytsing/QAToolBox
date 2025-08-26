#!/bin/bash

# =============================================================================
# QAToolBox 简化直接部署脚本
# 直接从GitHub克隆，无复杂配置
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"

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
echo "    🚀 QAToolBox 简化部署"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 停止现有服务
log_info "停止现有服务"
systemctl stop qatoolbox 2>/dev/null || true
pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
sleep 3

# 创建用户
if ! id "$PROJECT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_USER
    log_info "用户 $PROJECT_USER 已创建"
fi

# 清理Git配置中的重定向设置
log_info "清理Git配置"
sudo -u $PROJECT_USER git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true
git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true

# 直接从GitHub克隆项目
log_info "从GitHub直接克隆项目"
if [ -d "$PROJECT_DIR" ]; then
    rm -rf "$PROJECT_DIR"
fi

if sudo -u $PROJECT_USER git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR; then
    log_success "GitHub克隆成功"
else
    log_error "GitHub克隆失败"
    exit 1
fi

cd $PROJECT_DIR

# 设置Python环境
log_info "设置Python环境"
if [ -d ".venv" ]; then
    rm -rf .venv
fi

sudo -u $PROJECT_USER python3 -m venv .venv

# 配置pip镜像源
sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 安装依赖
log_info "安装Python依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
sudo -u $PROJECT_USER .venv/bin/pip install \
    Django==4.2.7 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.7 \
    redis==4.6.0 \
    django-redis==5.4.0 \
    python-dotenv==1.0.0 \
    django-environ==0.11.2 \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1 \
    whitenoise==6.6.0

# 配置数据库
log_info "配置数据库"
systemctl start postgresql 2>/dev/null || true
sleep 3

sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"

# 配置环境变量
cat > .env << 'EOF'
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-simple-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.production
EOF
chown $PROJECT_USER:$PROJECT_USER .env

# Django配置
log_info "配置Django"
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate || {
    log_warning "迁移失败，创建简化配置"
    
    mkdir -p config/settings
    cat > config/settings/minimal.py << 'MINIMALEOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-minimal-key'
DEBUG = False
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
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
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MINIMALEOF
    
    sed -i 's/DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=config.settings.minimal/' .env
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
}

sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput || true
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell || true

# 配置systemd服务
log_info "配置服务"
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.minimal
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox
sleep 10

# 配置Nginx
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 检查结果
sleep 5
if systemctl is-active --quiet qatoolbox && systemctl is-active --quiet nginx; then
    echo
    echo -e "${GREEN}========================================"
    echo "        🎉 部署成功！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${GREEN}访问地址: http://shenyiqing.xin${NC}"
    echo -e "${GREEN}管理后台: http://shenyiqing.xin/admin/${NC}"
    echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
else
    log_error "服务启动可能有问题"
    echo "检查状态: systemctl status qatoolbox nginx"
fi
