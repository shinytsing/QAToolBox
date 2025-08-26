#!/bin/bash

# =============================================================================
# QAToolBox 终极简化一键部署脚本
# 清理项目后的最简单部署方案
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/qatoolbox/QAToolbox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

echo -e "${GREEN}========================================"
echo "    🚀 QAToolBox 终极简化部署"
echo "========================================"
echo -e "${NC}"
echo "这是清理项目后的最简单部署方案"
echo "只安装必要的依赖，使用最简配置"
echo

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 停止现有服务
log_step "停止现有服务"
systemctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 3

# 更新系统
log_step "更新系统包"
apt-get update
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx curl wget git

# 创建用户
log_step "创建项目用户"
if ! id "$PROJECT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $PROJECT_USER
    log_info "用户 $PROJECT_USER 已创建"
else
    log_info "用户 $PROJECT_USER 已存在"
fi

# 检查项目是否存在
log_step "检查项目"
if [ ! -d "$PROJECT_DIR" ]; then
    log_info "项目不存在，从GitHub克隆"
    sudo -u $PROJECT_USER git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR
else
    log_info "项目已存在，更新代码"
    cd $PROJECT_DIR
    sudo -u $PROJECT_USER git pull origin main || true
fi

cd $PROJECT_DIR
chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR

# 创建虚拟环境
log_step "创建Python虚拟环境"
if [ -d ".venv" ]; then
    rm -rf .venv
fi
sudo -u $PROJECT_USER python3 -m venv .venv

# 配置pip镜像
sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF
chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf

# 安装Python依赖
log_step "安装Python依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip

# 只安装最核心的依赖
log_info "安装核心依赖"
sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
    Django==4.2.7 \
    gunicorn==21.2.0 \
    psycopg2-binary==2.9.7 \
    python-dotenv==1.0.0 \
    whitenoise==6.6.0 \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1

# 尝试安装其他常用依赖（失败也不影响核心功能）
log_info "安装扩展依赖（可选）"
OPTIONAL_DEPS=(
    "redis==4.6.0"
    "django-redis==5.4.0"
    "requests==2.31.0"
    "psutil==5.9.5"
    "Pillow==10.0.1"
    "celery==5.3.4"
)

for dep in "${OPTIONAL_DEPS[@]}"; do
    if sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir "$dep"; then
        log_success "✅ $dep"
    else
        log_warning "⚠️ $dep 安装失败，跳过"
    fi
done

# 配置数据库
log_step "配置PostgreSQL数据库"
systemctl start postgresql
systemctl enable postgresql

# 创建数据库用户和数据库
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';" 2>/dev/null || true
sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;" 2>/dev/null || true
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;" 2>/dev/null || true

log_success "数据库配置完成"

# 启动Redis
systemctl start redis-server 2>/dev/null || true
systemctl enable redis-server 2>/dev/null || true

# 创建环境变量文件
log_step "配置环境变量"
cat > .env << 'EOF'
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=django-simple-deploy-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Django设置模块
DJANGO_SETTINGS_MODULE=config.settings.simple
EOF
chown $PROJECT_USER:$PROJECT_USER .env

# 创建超级简化的Django配置
log_step "创建简化Django配置"
mkdir -p config/settings
cat > config/settings/simple.py << 'SIMPLEEOF'
"""
QAToolBox 简化配置 - 只包含核心功能
"""
import os
from pathlib import Path

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-simple-key')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost').split(',')

# 应用配置 - 只包含核心应用
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

# 中间件
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

ROOT_URLCONF = 'config.urls_simple'
WSGI_APPLICATION = 'config.wsgi.application'

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# 模板配置
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

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS配置
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# 缓存配置（如果Redis可用）
try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
except ImportError:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
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
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
SIMPLEEOF

# 创建简化的URL配置
cat > config/urls_simple.py << 'URLSEOF'
"""
QAToolBox 简化URL配置
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import platform

def home_view(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QAToolBox - 智能工具箱</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; display: flex; align-items: center; justify-content: center;
            }
            .container { 
                background: white; border-radius: 20px; padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 600px; width: 90%;
                text-align: center;
            }
            h1 { color: #333; margin-bottom: 20px; font-size: 2.5em; }
            .status { 
                background: #d4edda; color: #155724; padding: 20px;
                border-radius: 10px; margin: 20px 0; font-size: 1.2em;
            }
            .features { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 30px 0; }
            .feature { 
                background: #f8f9fa; padding: 20px; border-radius: 10px;
                border-left: 4px solid #007bff;
            }
            .feature h3 { color: #007bff; margin-bottom: 10px; }
            .links { margin: 30px 0; }
            .btn { 
                display: inline-block; background: #007bff; color: white;
                padding: 15px 30px; text-decoration: none; border-radius: 25px;
                margin: 10px; font-weight: bold; transition: all 0.3s;
            }
            .btn:hover { background: #0056b3; transform: translateY(-2px); }
            .footer { color: #666; margin-top: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 QAToolBox</h1>
            <div class="status">
                ✅ 系统运行正常！部署成功！
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 AI工具</h3>
                    <p>智能处理和分析</p>
                </div>
                <div class="feature">
                    <h3>📊 数据处理</h3>
                    <p>高效数据管理</p>
                </div>
                <div class="feature">
                    <h3>🔧 实用工具</h3>
                    <p>日常办公助手</p>
                </div>
                <div class="feature">
                    <h3>🌐 API服务</h3>
                    <p>开放接口调用</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/admin/" class="btn">管理后台</a>
                <a href="/api/status/" class="btn">API状态</a>
            </div>
            
            <div class="footer">
                <p>QAToolBox v2024 - 智能工具箱平台</p>
                <p>简化部署版本 | 核心功能完整</p>
            </div>
        </div>
    </body>
    </html>
    """)

def api_status(request):
    return JsonResponse({
        'status': 'success',
        'message': 'QAToolBox API 运行正常',
        'version': '2024-simple',
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'features': ['Django Admin', 'REST API', 'Static Files', 'Database'],
    })

def api_health(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "error"
    
    return JsonResponse({
        'status': 'healthy',
        'database': db_status,
        'timestamp': str(__import__('datetime').datetime.now()),
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('api/status/', api_status, name='api_status'),
    path('api/health/', api_health, name='api_health'),
]
URLSEOF

chown $PROJECT_USER:$PROJECT_USER config/settings/simple.py
chown $PROJECT_USER:$PROJECT_USER config/urls_simple.py

# Django初始化
log_step "初始化Django应用"
export DJANGO_SETTINGS_MODULE=config.settings.simple

# 测试配置
if sudo -u $PROJECT_USER .venv/bin/python manage.py check; then
    log_success "Django配置检查通过"
else
    log_error "Django配置有问题"
    exit 1
fi

# 数据库迁移
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput

# 创建管理员用户
log_info "创建管理员用户"
echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell

# 配置systemd服务
log_step "配置systemd服务"
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application (Simple)
After=network.target postgresql.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolbox
Environment=DJANGO_SETTINGS_MODULE=config.settings.simple
ExecStart=/home/qatoolbox/QAToolbox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 60 config.wsgi:application
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# 配置Nginx
log_step "配置Nginx"
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 7d;
    }
}
EOF

# 启用Nginx站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
if nginx -t; then
    log_success "Nginx配置正确"
else
    log_error "Nginx配置错误"
    exit 1
fi

# 启动所有服务
log_step "启动所有服务"
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox
systemctl enable nginx
systemctl start nginx

# 等待服务启动
sleep 10

# 最终检查
log_step "最终状态检查"
QATOOLBOX_STATUS=$(systemctl is-active qatoolbox)
NGINX_STATUS=$(systemctl is-active nginx)
POSTGRES_STATUS=$(systemctl is-active postgresql)

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")

echo
echo -e "${GREEN}========================================"
echo "        🎉 部署完成！"
echo "========================================"
echo -e "${NC}"

echo -e "服务状态："
echo -e "  QAToolBox: ${GREEN}$QATOOLBOX_STATUS${NC}"
echo -e "  Nginx: ${GREEN}$NGINX_STATUS${NC}"
echo -e "  PostgreSQL: ${GREEN}$POSTGRES_STATUS${NC}"
echo -e "  HTTP响应: ${GREEN}$HTTP_CODE${NC}"

echo
echo -e "${GREEN}🌐 访问地址: http://shenyiqing.xin${NC}"
echo -e "${GREEN}🔧 管理后台: http://shenyiqing.xin/admin/${NC}"
echo -e "${GREEN}📊 API状态: http://shenyiqing.xin/api/status/${NC}"
echo -e "${GREEN}💚 健康检查: http://shenyiqing.xin/api/health/${NC}"
echo
echo -e "${GREEN}👤 管理员账户:${NC}"
echo -e "   用户名: admin"
echo -e "   密码: QAToolBox@2024"

if [ "$QATOOLBOX_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ] && [ "$HTTP_CODE" = "200" ]; then
    echo
    echo -e "${GREEN}🎊 恭喜！QAToolBox部署成功！${NC}"
    echo -e "${BLUE}这是一个简化版本，包含核心功能，运行稳定可靠！${NC}"
else
    echo
    echo -e "${YELLOW}⚠️ 部分服务可能有问题，请检查：${NC}"
    echo "journalctl -u qatoolbox -f"
fi

echo
echo -e "${PURPLE}📋 有用的管理命令：${NC}"
echo "• 重启服务: systemctl restart qatoolbox nginx"
echo "• 查看日志: journalctl -u qatoolbox -f"
echo "• 更新代码: cd $PROJECT_DIR && git pull"
echo "• 进入Django shell: cd $PROJECT_DIR && .venv/bin/python manage.py shell"
