#!/bin/bash

# =============================================================================
# QAToolBox 就地修复部署脚本
# 基于现有项目代码，不重新克隆
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
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
echo "    🔧 QAToolBox 就地修复"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录 $PROJECT_DIR 不存在"
    exit 1
fi

cd $PROJECT_DIR

# 停止现有服务
log_info "停止现有服务"
systemctl stop qatoolbox 2>/dev/null || true
pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
sleep 3

# 清理Git配置中的重定向设置
log_info "清理Git重定向配置"
sudo -u $PROJECT_USER git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true
git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true
log_success "Git配置已清理"

# 重建Python环境
log_info "重建Python虚拟环境"
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
timeout = 120
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 升级pip并安装核心依赖
log_info "安装Python依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip

# 按顺序安装依赖，避免冲突
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    setuptools==68.2.2 \
    wheel==0.41.2

sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    python-dotenv==1.0.0 \
    django-environ==0.11.2

sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    Django==4.2.7 \
    psycopg2-binary==2.9.7 \
    redis==4.6.0 \
    django-redis==5.4.0

sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1 \
    whitenoise==6.6.0 \
    gunicorn==21.2.0

log_success "Python依赖安装完成"

# 确保数据库服务运行
log_info "确保数据库服务运行"
systemctl start postgresql 2>/dev/null || true
systemctl start redis-server 2>/dev/null || true
sleep 3

# 重置数据库
log_info "重置数据库"
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
DJANGO_SETTINGS_MODULE=config.settings.minimal
EOF
chown $PROJECT_USER:$PROJECT_USER .env

# 创建简化的Django配置
log_info "创建简化Django配置"
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

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'config.wsgi.application'

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

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
MINIMALEOF

chown $PROJECT_USER:$PROJECT_USER config/settings/minimal.py

# Django数据库迁移
log_info "执行Django迁移"
export DJANGO_SETTINGS_MODULE=config.settings.minimal
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput

# 创建管理员用户
log_info "创建管理员用户"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell

# 创建日志目录
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

# 修复systemd服务配置
log_info "修复systemd服务配置"
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.minimal
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 120 config.wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qatoolbox

# 确保Nginx配置正确
log_info "确保Nginx配置正确"
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
        expires 7d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
if nginx -t; then
    log_success "Nginx配置正确"
else
    log_error "Nginx配置有误"
    exit 1
fi

# 启动所有服务
log_info "启动所有服务"
systemctl start qatoolbox
sleep 5
systemctl restart nginx

# 检查服务状态
log_info "检查服务状态"
sleep 10

QATOOLBOX_STATUS=$(systemctl is-active qatoolbox)
NGINX_STATUS=$(systemctl is-active nginx)
POSTGRESQL_STATUS=$(systemctl is-active postgresql)
REDIS_STATUS=$(systemctl is-active redis-server)

echo
echo -e "${BLUE}========================================"
echo "        📊 服务状态检查"
echo "========================================"
echo -e "${NC}"

if [ "$QATOOLBOX_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ QAToolBox服务: 运行中${NC}"
else
    echo -e "${RED}❌ QAToolBox服务: $QATOOLBOX_STATUS${NC}"
fi

if [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ Nginx服务: 运行中${NC}"
else
    echo -e "${RED}❌ Nginx服务: $NGINX_STATUS${NC}"
fi

if [ "$POSTGRESQL_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ PostgreSQL服务: 运行中${NC}"
else
    echo -e "${RED}❌ PostgreSQL服务: $POSTGRESQL_STATUS${NC}"
fi

if [ "$REDIS_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ Redis服务: 运行中${NC}"
else
    echo -e "${RED}❌ Redis服务: $REDIS_STATUS${NC}"
fi

# 测试HTTP响应
log_info "测试HTTP响应"
sleep 5
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ || echo "000")

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${GREEN}✅ HTTP响应: $HTTP_CODE (正常)${NC}"
    SUCCESS=true
else
    echo -e "${RED}❌ HTTP响应: $HTTP_CODE (异常)${NC}"
    SUCCESS=false
fi

# 创建状态检查脚本
cat > status.sh << 'EOF'
#!/bin/bash
echo "=== QAToolBox 服务状态 ==="
echo "QAToolBox: $(systemctl is-active qatoolbox)"
echo "Nginx: $(systemctl is-active nginx)"
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Redis: $(systemctl is-active redis-server)"
echo
echo "=== 最近日志 ==="
journalctl -u qatoolbox --no-pager -n 10
echo
echo "=== HTTP测试 ==="
curl -s -I http://localhost:8000/ | head -1
EOF
chmod +x status.sh
chown $PROJECT_USER:$PROJECT_USER status.sh

# 显示最终结果
echo
if [ "$SUCCESS" = true ] && [ "$QATOOLBOX_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}========================================"
    echo "        🎉 修复成功！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${GREEN}访问地址: http://shenyiqing.xin${NC}"
    echo -e "${GREEN}管理后台: http://shenyiqing.xin/admin/${NC}"
    echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
    echo
    echo -e "${BLUE}状态检查: ./status.sh${NC}"
else
    echo -e "${YELLOW}========================================"
    echo "        ⚠️  修复完成，但可能有问题"
    echo "========================================"
    echo -e "${NC}"
    echo "请检查服务状态: systemctl status qatoolbox nginx"
    echo "查看日志: journalctl -u qatoolbox -f"
    echo "运行状态检查: ./status.sh"
fi
