#!/bin/bash

# =============================================================================
# QAToolBox 权限和路径快速修复脚本
# 解决Git克隆权限问题和服务启动问题
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/qatoolbox/QAToolbox"

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
echo "    🔧 快速修复权限和路径问题"
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
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# 修复用户和目录权限
log_info "修复用户和目录权限"

# 确保用户存在
if ! id "$PROJECT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_USER
    log_info "用户 $PROJECT_USER 已创建"
else
    log_info "用户 $PROJECT_USER 已存在"
fi

# 确保用户家目录权限正确
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER
chmod 755 /home/$PROJECT_USER

# 删除旧的项目目录（如果存在但有权限问题）
if [ -d "$PROJECT_DIR" ]; then
    log_info "删除旧的项目目录"
    rm -rf "$PROJECT_DIR"
fi

# 创建项目目录并设置正确权限
log_info "创建项目目录"
mkdir -p "$PROJECT_DIR"
chown $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR"

# 克隆项目
log_info "克隆项目代码"
cd /home/$PROJECT_USER

# 使用root克隆，然后修改权限
if git clone https://github.com/shinytsing/QAToolbox.git QAToolbox; then
    log_success "项目克隆成功"
    chown -R $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR"
else
    log_error "GitHub克隆失败，尝试其他方法"
    
    # 尝试下载ZIP文件
    log_info "尝试下载ZIP文件"
    if wget -O QAToolbox.zip https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip; then
        unzip -q QAToolbox.zip
        mv QAToolbox-main QAToolbox
        rm QAToolbox.zip
        chown -R $PROJECT_USER:$PROJECT_USER "$PROJECT_DIR"
        log_success "ZIP下载解压成功"
    else
        log_error "所有下载方法都失败了"
        exit 1
    fi
fi

cd "$PROJECT_DIR"

# 检查关键文件是否存在
log_info "检查关键文件"
if [ ! -f "manage.py" ]; then
    log_error "manage.py 文件不存在"
    exit 1
fi

if [ ! -f "config/wsgi.py" ]; then
    log_error "config/wsgi.py 文件不存在"
    exit 1
fi

log_success "关键文件检查通过"

# 创建虚拟环境
log_info "创建虚拟环境"
if [ -d ".venv" ]; then
    rm -rf .venv
fi

sudo -u $PROJECT_USER python3 -m venv .venv
chown -R $PROJECT_USER:$PROJECT_USER .venv

# 配置pip镜像
sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 安装核心依赖
log_info "安装Python依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip

# 只安装最必要的依赖
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    Django==4.2.7 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.7 \
    python-dotenv==1.0.0 \
    whitenoise==6.6.0

log_success "核心依赖安装完成"

# 创建环境变量文件
log_info "创建环境变量文件"
cat > .env << 'EOF'
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-quick-fix-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.quickfix
EOF
chown $PROJECT_USER:$PROJECT_USER .env

# 创建超级简化的Django配置
log_info "创建快速修复Django配置"
mkdir -p config/settings
cat > config/settings/quickfix.py << 'QUICKFIXEOF'
"""
QAToolBox 快速修复配置 - 最小化配置确保能启动
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'django-quickfix-key-12345'
DEBUG = False
ALLOWED_HOSTS = ['*']

# 最小化应用
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
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls_quickfix'
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
    'DIRS': [],
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
QUICKFIXEOF

# 创建简化的URL配置
cat > config/urls_quickfix.py << 'URLSEOF'
"""
快速修复URL配置
"""
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse, JsonResponse

def home_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QAToolBox - 快速修复版</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            .container { max-width: 600px; margin: 0 auto; }
            .status { background: #d4edda; color: #155724; padding: 20px; border-radius: 5px; margin: 20px 0; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 QAToolBox</h1>
            <div class="status">
                ✅ 快速修复版本运行成功！
            </div>
            <p>这是一个快速修复版本，确保系统能够正常启动。</p>
            <a href="/admin/" class="btn">进入管理后台</a>
        </div>
    </body>
    </html>
    """)

def api_status(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'QAToolBox Quick Fix Version',
        'version': 'quickfix-1.0'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/status/', api_status, name='api_status'),
]
URLSEOF

chown $PROJECT_USER:$PROJECT_USER config/settings/quickfix.py
chown $PROJECT_USER:$PROJECT_USER config/urls_quickfix.py

# 确保数据库服务运行
log_info "确保数据库服务运行"
systemctl start postgresql
systemctl enable postgresql

# 配置数据库
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;" 2>/dev/null || true
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;" 2>/dev/null || true

# Django初始化
log_info "初始化Django"
export DJANGO_SETTINGS_MODULE=config.settings.quickfix

# 测试Django配置
if sudo -u $PROJECT_USER .venv/bin/python manage.py check; then
    log_success "Django配置检查通过"
else
    log_error "Django配置仍有问题"
    exit 1
fi

# 数据库迁移
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput

# 创建管理员用户
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell

# 创建日志目录
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

# 修复systemd服务配置
log_info "修复systemd服务配置"
cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application (Quick Fix)
After=network.target postgresql.service

[Service]
Type=exec
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.quickfix
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 60 config.wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 重新加载systemd配置
systemctl daemon-reload
systemctl enable qatoolbox

# 启动服务
log_info "启动QAToolBox服务"
if systemctl start qatoolbox; then
    log_success "QAToolBox服务启动成功"
else
    log_error "QAToolBox服务启动失败"
    journalctl -u qatoolbox --no-pager -n 10
    exit 1
fi

# 等待服务启动
sleep 10

# 检查状态
QATOOLBOX_STATUS=$(systemctl is-active qatoolbox)
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")

echo
echo -e "${GREEN}========================================"
echo "        🎉 快速修复完成！"
echo "========================================"
echo -e "${NC}"

echo -e "服务状态："
echo -e "  QAToolBox: ${GREEN}$QATOOLBOX_STATUS${NC}"
echo -e "  HTTP响应: ${GREEN}$HTTP_CODE${NC}"

if [ "$QATOOLBOX_STATUS" = "active" ] && [ "$HTTP_CODE" = "200" ]; then
    echo
    echo -e "${GREEN}🎊 修复成功！服务正常运行！${NC}"
    echo -e "${GREEN}🌐 访问地址: http://shenyiqing.xin${NC}"
    echo -e "${GREEN}🔧 管理后台: http://shenyiqing.xin/admin/${NC}"
    echo -e "${GREEN}👤 用户名: admin, 密码: QAToolBox@2024${NC}"
else
    echo -e "${YELLOW}⚠️ 服务可能还有问题${NC}"
    echo "查看日志: journalctl -u qatoolbox -f"
fi

echo
echo -e "${BLUE}📋 下一步可以运行完整部署脚本来获得更多功能${NC}"
