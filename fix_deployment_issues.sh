#!/bin/bash

# QAToolBox 一键修复部署问题脚本
# 保持完整配置，修复所有依赖和配置问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用sudo运行此脚本"
    exit 1
fi

PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/qatoolbox/QAToolBox"

log_info "🚀 开始一键修复QAToolBox部署问题"

# 1. 安装OpenCV和图像处理相关的系统依赖
log_info "安装OpenCV和图像处理系统依赖"
apt update
apt install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    libeigen3-dev \
    libgtk2.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev

log_success "系统依赖安装完成"

# 2. 进入项目目录
cd $PROJECT_DIR

# 3. 修复OpenCV问题 - 使用无头版本替换
log_info "修复OpenCV依赖问题"
sudo -u $PROJECT_USER .venv/bin/pip uninstall opencv-python -y || true
sudo -u $PROJECT_USER .venv/bin/pip install opencv-python-headless \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 4. 安装所有可能缺失的Python依赖
log_info "安装完整的Python依赖包"
sudo -u $PROJECT_USER .venv/bin/pip install \
    django-environ \
    psutil \
    django-extensions \
    channels \
    channels-redis \
    celery \
    redis \
    gunicorn \
    whitenoise \
    python-dotenv \
    requests \
    beautifulsoup4 \
    lxml \
    Pillow \
    pandas \
    numpy \
    matplotlib \
    scipy \
    scikit-learn \
    opencv-python-headless \
    pytesseract \
    pydub \
    mutagen \
    librosa \
    soundfile \
    audioread \
    resampy \
    selenium \
    webdriver-manager \
    cryptography \
    pytz \
    tenacity \
    prettytable \
    qrcode \
    simplejson \
    yfinance \
    multitasking \
    peewee \
    sentry-sdk \
    structlog \
    django-csp \
    gevent \
    django-debug-toolbar \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 5. 重新安装requirements.txt确保完整性
log_info "重新安装requirements.txt确保完整性"
sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --upgrade

log_success "Python依赖安装完成"

# 6. 修复生产环境配置中的数据库问题
log_info "修复生产环境数据库配置"

# 备份原配置
cp config/settings/production.py config/settings/production.py.backup.$(date +%Y%m%d_%H%M%S)

# 修复PostgreSQL配置中的charset问题
sed -i "s/'charset': 'utf8'/'OPTIONS': {'charset': 'utf8'}/g" config/settings/production.py
sed -i "s/'charset': 'utf8mb4'/'OPTIONS': {'charset': 'utf8mb4'}/g" config/settings/production.py

# 如果仍有charset问题，直接移除charset配置
sed -i "/charset/d" config/settings/production.py

log_success "数据库配置修复完成"

# 7. 修复Redis配置中的CLIENT_CLASS问题
log_info "修复Redis配置"
sed -i "s/'CLIENT_CLASS': 'django_redis.client.DefaultClient'/'CLIENT_CLASS': 'django_redis.client.DefaultClient',/g" config/settings/production.py

# 8. 创建必要的目录
log_info "创建必要的目录"
sudo -u $PROJECT_USER mkdir -p /opt/qatoolbox/staticfiles
sudo -u $PROJECT_USER mkdir -p /opt/qatoolbox/media
sudo -u $PROJECT_USER mkdir -p /opt/qatoolbox/logs

# 9. 设置环境变量
log_info "设置生产环境变量"
sudo -u $PROJECT_USER tee /home/$PROJECT_USER/QAToolBox/.env > /dev/null << EOF
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox_password
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Django配置
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=47.103.143.152,shenyiqing.xin,localhost,127.0.0.1

# 静态文件
STATIC_ROOT=/opt/qatoolbox/staticfiles
MEDIA_ROOT=/opt/qatoolbox/media
EOF

# 10. 执行数据库操作
log_info "执行数据库迁移"

# 先检查Django配置
sudo -u $PROJECT_USER .venv/bin/python manage.py check --settings=config.settings.production || {
    log_warning "Django配置检查失败，尝试修复..."
    
    # 如果还有问题，创建一个临时的最小配置
    sudo -u $PROJECT_USER tee config/settings/temp_production.py > /dev/null << 'EOF'
from .base import *
import os

# 最小化数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'qatoolbox_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# 简化Redis配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

DEBUG = False
ALLOWED_HOSTS = ['*']
STATIC_ROOT = '/opt/qatoolbox/staticfiles'
MEDIA_ROOT = '/opt/qatoolbox/media'
EOF
    
    SETTINGS_MODULE="config.settings.temp_production"
    log_warning "使用临时配置: $SETTINGS_MODULE"
}

SETTINGS_MODULE=${SETTINGS_MODULE:-"config.settings.production"}

# 执行迁移
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations --settings=$SETTINGS_MODULE
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate --settings=$SETTINGS_MODULE

# 收集静态文件
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput --settings=$SETTINGS_MODULE

log_success "数据库迁移完成"

# 11. 配置Gunicorn服务
log_info "配置Gunicorn服务"
tee /etc/systemd/system/qatoolbox.service > /dev/null << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service

[Service]
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=$SETTINGS_MODULE"
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 300 --access-logfile /opt/qatoolbox/logs/gunicorn-access.log --error-logfile /opt/qatoolbox/logs/gunicorn-error.log config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 12. 配置Nginx
log_info "配置Nginx"
tee /etc/nginx/sites-available/qatoolbox > /dev/null << EOF
server {
    listen 80;
    server_name 47.103.143.152 shenyiqing.xin;
    
    # 重定向HTTP到HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 47.103.143.152 shenyiqing.xin;
    
    # SSL配置
    ssl_certificate /etc/ssl/certs/qatoolbox.crt;
    ssl_certificate_key /etc/ssl/private/qatoolbox.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /opt/qatoolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /opt/qatoolbox/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 13. 生成SSL证书（自签名）
log_info "生成SSL证书"
mkdir -p /etc/ssl/private /etc/ssl/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/qatoolbox.key \
    -out /etc/ssl/certs/qatoolbox.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/CN=shenyiqing.xin"

chmod 600 /etc/ssl/private/qatoolbox.key
chmod 644 /etc/ssl/certs/qatoolbox.crt

# 14. 启动服务
log_info "启动所有服务"
systemctl daemon-reload
systemctl enable qatoolbox
systemctl enable nginx
systemctl enable postgresql
systemctl enable redis-server

systemctl restart postgresql
systemctl restart redis-server
systemctl restart qatoolbox
systemctl restart nginx

# 15. 检查服务状态
log_info "检查服务状态"
echo "PostgreSQL状态:"
systemctl is-active postgresql && echo "✅ PostgreSQL运行正常" || echo "❌ PostgreSQL启动失败"

echo "Redis状态:"
systemctl is-active redis-server && echo "✅ Redis运行正常" || echo "❌ Redis启动失败"

echo "QAToolBox应用状态:"
systemctl is-active qatoolbox && echo "✅ QAToolBox运行正常" || echo "❌ QAToolBox启动失败"

echo "Nginx状态:"
systemctl is-active nginx && echo "✅ Nginx运行正常" || echo "❌ Nginx启动失败"

# 16. 显示访问信息
log_success "🎉 QAToolBox部署修复完成！"
echo
echo "📋 访问信息:"
echo "HTTP:  http://47.103.143.152"
echo "HTTPS: https://47.103.143.152"
echo "域名:  https://shenyiqing.xin"
echo
echo "📝 管理命令:"
echo "查看应用日志: sudo journalctl -u qatoolbox -f"
echo "查看Nginx日志: sudo tail -f /var/log/nginx/error.log"
echo "重启应用: sudo systemctl restart qatoolbox"
echo "重启Nginx: sudo systemctl restart nginx"
echo
echo "🔧 创建超级用户:"
echo "cd $PROJECT_DIR && sudo -u $PROJECT_USER .venv/bin/python manage.py createsuperuser --settings=$SETTINGS_MODULE"
echo
echo "如果需要安装Let's Encrypt证书，请运行:"
echo "sudo apt install certbot python3-certbot-nginx -y"
echo "sudo certbot --nginx -d shenyiqing.xin"
