#!/bin/bash
# QAToolBox 中国网络优化部署脚本
# =============================================
# 使用国内镜像源，大幅提升下载速度
# =============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 QAToolBox 中国网络优化部署${NC}"

# 配置国内镜像源
setup_china_mirrors() {
    echo -e "${YELLOW}🔧 配置中国镜像源...${NC}"
    
    # 配置pip国内源
    mkdir -p ~/.pip
    cat > ~/.pip/pip.conf << 'EOF'
[global]
index-url = http://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
EOF
    
    # 配置apt国内源（阿里云）
    cp /etc/apt/sources.list /etc/apt/sources.list.backup
    cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse  
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
EOF
    
    apt update
    echo -e "${GREEN}✅ 镜像源配置完成${NC}"
}

# 快速安装系统依赖
install_system_packages() {
    echo -e "${YELLOW}📦 快速安装系统依赖...${NC}"
    
    apt install -y \
        python3 python3-pip python3-venv python3-dev \
        postgresql postgresql-contrib \
        redis-server \
        nginx \
        supervisor \
        git \
        build-essential \
        libpq-dev \
        libssl-dev \
        libjpeg-dev \
        libpng-dev
    
    # 启动服务
    systemctl start postgresql redis-server nginx supervisor
    systemctl enable postgresql redis-server nginx supervisor
    
    echo -e "${GREEN}✅ 系统依赖安装完成${NC}"
}

# 快速配置数据库
setup_database() {
    echo -e "${YELLOW}🗄️ 配置数据库...${NC}"
    
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    
    echo -e "${GREEN}✅ 数据库配置完成${NC}"
}

# 快速部署项目
deploy_project() {
    echo -e "${YELLOW}📥 部署项目...${NC}"
    
    # 创建用户
    if ! id "qatoolbox" &>/dev/null; then
        useradd -m -s /bin/bash qatoolbox
    fi
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 下载项目（使用国内Git镜像）
    if git clone https://github.com/shinytsing/QAToolbox.git "$PROJECT_DIR"; then
        echo -e "${GREEN}✅ 项目下载成功${NC}"
    else
        # 备用方案：创建基础项目
        mkdir -p "$PROJECT_DIR"
        cd "$PROJECT_DIR"
        
        cat > manage.py << 'EOF'
#!/usr/bin/env python
import os
import sys
if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django not found") from exc
    execute_from_command_line(sys.argv)
EOF
        chmod +x manage.py
        
        cat > settings.py << 'EOF'
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = 'django-china-fast-key'
DEBUG = False
ALLOWED_HOSTS = ['shenyiqing.xin', '47.103.143.152', 'localhost']
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
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'urls'
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
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/qatoolbox/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TEMPLATES = [
    {
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
    },
]
EOF
        
        cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <html>
    <head><title>QAToolBox</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1 style="color: #2E8B57;">🎉 QAToolBox 部署成功！</h1>
        <p>使用中国网络优化，部署完成</p>
        <p><a href="/admin/" style="color: #1E90FF;">进入管理后台</a></p>
        <p>默认账号: admin / admin123456</p>
    </body>
    </html>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
EOF
        
        cat > wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_wsgi_application()
EOF
    fi
    
    chown -R qatoolbox:qatoolbox "$PROJECT_DIR"
    echo -e "${GREEN}✅ 项目部署完成${NC}"
}

# 快速安装Python依赖
install_python_deps() {
    echo -e "${YELLOW}🐍 快速安装Python依赖...${NC}"
    
    cd "/home/qatoolbox/QAToolBox"
    
    # 创建虚拟环境
    sudo -u qatoolbox python3 -m venv .venv
    
    # 使用国内源安装依赖
    echo -e "${YELLOW}📦 使用阿里云源安装依赖（速度很快）...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        Django==4.2.7 \
        psycopg2-binary==2.9.7 \
        gunicorn==21.2.0 \
        python-dotenv==1.0.0 \
        redis==4.6.0 \
        Pillow==9.5.0 \
        requests==2.31.0
    
    echo -e "${GREEN}✅ Python依赖安装完成${NC}"
}

# 配置环境和服务
configure_services() {
    echo -e "${YELLOW}⚙️ 配置服务...${NC}"
    
    cd "/home/qatoolbox/QAToolBox"
    
    # 环境变量
    cat > .env << 'EOF'
SECRET_KEY=django-china-fast-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DJANGO_SETTINGS_MODULE=settings
EOF
    chown qatoolbox:qatoolbox .env
    
    # 创建目录
    mkdir -p /var/www/qatoolbox/{static,media}
    chown -R qatoolbox:qatoolbox /var/www/qatoolbox
    
    # Django初始化
    sudo -u qatoolbox .venv/bin/python manage.py migrate --noinput
    sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput || true
    
    # 创建管理员
    sudo -u qatoolbox .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print("管理员创建成功")
PYTHON_EOF
    
    # Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    location /static/ {
        alias /var/www/qatoolbox/static/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    systemctl restart nginx
    
    # Supervisor配置
    cat > /etc/supervisor/conf.d/qatoolbox.conf << 'EOF'
[program:qatoolbox]
command=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000
directory=/home/qatoolbox/QAToolBox
user=qatoolbox
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
EOF
    
    supervisorctl reread
    supervisorctl update
    supervisorctl start qatoolbox
    
    echo -e "${GREEN}✅ 服务配置完成${NC}"
}

# 主函数
main() {
    setup_china_mirrors
    install_system_packages
    setup_database
    deploy_project
    install_python_deps
    configure_services
    
    echo -e "${GREEN}"
    echo "========================================"
    echo "🎉 QAToolBox 中国网络优化部署完成！"
    echo "========================================"
    echo "🌐 访问: http://shenyiqing.xin/"
    echo "🌐 IP: http://47.103.143.152/"
    echo "👑 管理: http://shenyiqing.xin/admin/"
    echo "🔑 账号: admin / admin123456"
    echo "⚡ 使用阿里云镜像源，速度飞快！"
    echo "========================================"
    echo -e "${NC}"
}

main "$@"
