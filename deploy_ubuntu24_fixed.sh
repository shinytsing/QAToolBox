#!/bin/bash
# QAToolBox Ubuntu 24.04 兼容部署脚本
# =============================================
# 修复Ubuntu 24.04包名变化问题
# =============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}🔧 修复Ubuntu 24.04包依赖问题...${NC}"

# 检测Ubuntu版本
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}检测到系统: $NAME $VERSION${NC}"
fi

# Ubuntu 24.04兼容的包安装
echo -e "${YELLOW}📦 安装兼容的系统级依赖...${NC}"

# 基础依赖
apt install -y \
    libssl-dev libcrypto++-dev \
    libpq-dev postgresql-client \
    libmysqlclient-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libgtk-3-dev libcanberra-gtk-module libcanberra-gtk3-module \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Ubuntu 24.04特定包名（替换已废弃的包）
if [[ "$VERSION_ID" == "24.04" ]] || [[ "$VERSION_ID" > "24" ]]; then
    echo -e "${YELLOW}🔄 使用Ubuntu 24.04兼容包名...${NC}"
    
    # 替换libgl1-mesa-glx为新的包名
    apt install -y \
        libgl1-mesa-dri \
        libglib2.0-0t64 \
        libsm6 libxext6 libxrender1 \
        libgomp1 \
        libatlas-base-dev liblapack-dev libblas-dev \
        libhdf5-dev \
        libprotobuf-dev protobuf-compiler \
        libsndfile1-dev portaudio19-dev \
        ffmpeg \
        tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra
    
    # 尝试安装chromium（Ubuntu 24.04可能包名不同）
    apt install -y chromium-browser || apt install -y chromium || echo "Chromium安装跳过"
    
else
    echo -e "${YELLOW}🔄 使用传统包名...${NC}"
    
    # 传统包名
    apt install -y \
        libgl1-mesa-glx \
        libglib2.0-0 \
        libsm6 libxext6 libxrender-dev \
        libgomp1 libomp-dev \
        libatlas-base-dev liblapack-dev libblas-dev \
        libhdf5-dev libhdf5-serial-dev \
        libprotobuf-dev protobuf-compiler \
        libsndfile1-dev portaudio19-dev \
        ffmpeg \
        tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
        chromium-browser chromium-chromedriver
fi

echo -e "${GREEN}✅ 系统依赖安装完成${NC}"

# 继续安装服务
echo -e "${YELLOW}🔧 安装服务软件...${NC}"
apt install -y postgresql postgresql-contrib redis-server nginx supervisor
systemctl start postgresql redis-server nginx supervisor
systemctl enable postgresql redis-server nginx supervisor

# 配置数据库
echo -e "${YELLOW}🗄️ 配置数据库...${NC}"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"

# 创建项目用户
echo -e "${YELLOW}👤 创建项目用户...${NC}"
if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
    usermod -aG sudo qatoolbox
fi

# 下载项目
echo -e "${YELLOW}📥 下载项目...${NC}"
PROJECT_DIR="/home/qatoolbox/QAToolBox"
if [ -d "$PROJECT_DIR" ]; then
    rm -rf "$PROJECT_DIR"
fi

if git clone https://github.com/shinytsing/QAToolbox.git "$PROJECT_DIR"; then
    echo -e "${GREEN}✅ 项目下载成功${NC}"
else
    echo -e "${YELLOW}⚠️  创建基础项目结构${NC}"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # 创建基础文件
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
SECRET_KEY = 'django-ubuntu24-key'
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
EOF
    
    cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
def home(request):
    return HttpResponse("<h1>QAToolBox Ubuntu 24.04 部署成功！</h1><p>访问 <a href='/admin/'>/admin/</a> 进入管理后台</p>")
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

# 创建虚拟环境
echo -e "${YELLOW}🐍 创建虚拟环境...${NC}"
cd "$PROJECT_DIR"
if [ -d ".venv" ]; then
    rm -rf ".venv"
fi

sudo -u qatoolbox python3 -m venv .venv
sudo -u qatoolbox .venv/bin/pip install --upgrade pip

# 安装Python依赖
echo -e "${YELLOW}📦 安装Python依赖...${NC}"
sudo -u qatoolbox .venv/bin/pip install \
    Django==4.2.7 \
    psycopg2-binary==2.9.7 \
    gunicorn==21.2.0 \
    python-dotenv==1.0.0 \
    django-environ==0.11.2 \
    redis==4.6.0 \
    Pillow==9.5.0 \
    requests==2.31.0

# 尝试安装机器学习依赖（可选）
echo -e "${YELLOW}📦 尝试安装机器学习依赖...${NC}"
sudo -u qatoolbox .venv/bin/pip install \
    torch==2.1.2 \
    torchvision==0.16.2 \
    --index-url https://download.pytorch.org/whl/cpu || echo "⚠️ torch安装失败，跳过"

sudo -u qatoolbox .venv/bin/pip install \
    opencv-python==4.8.1.78 \
    numpy==1.24.4 \
    scikit-learn==1.3.2 || echo "⚠️ 部分ML库安装失败，跳过"

# 配置环境变量
echo -e "${YELLOW}⚙️ 配置环境变量...${NC}"
cat > .env << 'EOF'
SECRET_KEY=django-ubuntu24-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=settings
EOF
chown qatoolbox:qatoolbox .env

# 初始化Django
echo -e "${YELLOW}🚀 初始化Django...${NC}"
mkdir -p /var/www/qatoolbox/{static,media}
chown -R qatoolbox:qatoolbox /var/www/qatoolbox

sudo -u qatoolbox .venv/bin/python manage.py migrate --noinput
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput || true

# 创建超级用户
sudo -u qatoolbox .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print("管理员用户创建成功: admin/admin123456")
PYTHON_EOF

# 配置Nginx
echo -e "${YELLOW}🌐 配置Nginx...${NC}"
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    location /static/ {
        alias /var/www/qatoolbox/static/;
    }
    
    location /media/ {
        alias /var/www/qatoolbox/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 配置Supervisor
echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 2
directory=$PROJECT_DIR
user=qatoolbox
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
environment=DJANGO_SETTINGS_MODULE=settings
EOF

supervisorctl reread
supervisorctl update
supervisorctl start qatoolbox

echo -e "${GREEN}"
echo "========================================"
echo "🎉 QAToolBox Ubuntu 24.04 部署完成！"
echo "========================================"
echo "🌐 访问地址: http://shenyiqing.xin/"
echo "🌐 IP访问: http://47.103.143.152/"
echo "👑 管理后台: http://shenyiqing.xin/admin/"
echo "🔑 默认账号: admin / admin123456"
echo "📁 项目目录: $PROJECT_DIR"
echo "📊 数据库: PostgreSQL"
echo "🔴 缓存: Redis"
echo "========================================"
echo -e "${NC}"
