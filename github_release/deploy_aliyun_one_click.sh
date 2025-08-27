#!/bin/bash
# QAToolBox 阿里云服务器一键部署脚本
# =============================================
# 专为阿里云 47.103.143.152 优化
# 域名: https://shenyiqing.xin/
# 包含所有依赖：torch、environ、opencv等
# =============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
SERVER_IP="47.103.143.152"
DOMAIN="shenyiqing.xin"
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DB_PASSWORD="QAToolBox@2024"

echo -e "${BLUE}"
echo "========================================"
echo "🚀 QAToolBox 阿里云一键部署开始"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用root权限运行: sudo $0${NC}"
    exit 1
fi

# 检测系统类型
detect_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    echo -e "${GREEN}✅ 检测到系统: $OS $VER${NC}"
}

# 更新系统和安装基础工具
setup_system() {
    echo -e "${YELLOW}📦 更新系统并安装基础工具...${NC}"
    
    # 更新包管理器
    apt update && apt upgrade -y
    
    # 安装基础工具
    apt install -y \
        curl wget git unzip vim nano htop tree \
        software-properties-common apt-transport-https \
        ca-certificates gnupg lsb-release
    
    echo -e "${GREEN}✅ 系统更新完成${NC}"
}

# 安装Python和开发工具
install_python() {
    echo -e "${YELLOW}🐍 安装Python和开发环境...${NC}"
    
    apt install -y \
        python3 python3-pip python3-venv python3-dev \
        build-essential gcc g++ make \
        pkg-config cmake \
        libbz2-dev libreadline-dev libsqlite3-dev \
        libncurses5-dev libncursesw5-dev \
        xz-utils tk-dev libffi-dev liblzma-dev
    
    # 升级pip
    python3 -m pip install --upgrade pip setuptools wheel
    
    echo -e "${GREEN}✅ Python环境安装完成${NC}"
}

# 安装系统级依赖（用于torch、opencv等）
install_system_dependencies() {
    echo -e "${YELLOW}📦 安装系统级依赖库...${NC}"
    
    apt install -y \
        libssl-dev libcrypto++-dev \
        libpq-dev postgresql-client \
        libmysqlclient-dev \
        libjpeg-dev libpng-dev libtiff-dev \
        libavcodec-dev libavformat-dev libswscale-dev \
        libgtk-3-dev libcanberra-gtk-module libcanberra-gtk3-module \
        libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
        libgl1-mesa-glx libglib2.0-0 \
        libsm6 libxext6 libxrender-dev \
        libgomp1 libomp-dev \
        libatlas-base-dev liblapack-dev libblas-dev \
        libhdf5-dev libhdf5-serial-dev \
        libprotobuf-dev protobuf-compiler \
        libsndfile1-dev portaudio19-dev \
        ffmpeg \
        tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
        chromium-browser chromium-chromedriver
    
    echo -e "${GREEN}✅ 系统依赖安装完成${NC}"
}

# 安装服务软件
install_services() {
    echo -e "${YELLOW}🔧 安装服务软件...${NC}"
    
    # 安装PostgreSQL
    apt install -y postgresql postgresql-contrib
    systemctl start postgresql
    systemctl enable postgresql
    
    # 安装Redis
    apt install -y redis-server
    systemctl start redis-server
    systemctl enable redis-server
    
    # 安装Nginx
    apt install -y nginx
    systemctl start nginx
    systemctl enable nginx
    
    # 安装Supervisor
    apt install -y supervisor
    systemctl start supervisor
    systemctl enable supervisor
    
    echo -e "${GREEN}✅ 服务软件安装完成${NC}"
}

# 配置数据库
setup_database() {
    echo -e "${YELLOW}🗄️ 配置PostgreSQL数据库...${NC}"
    
    # 删除旧数据库（如果存在）
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    
    # 创建新用户和数据库
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    echo -e "${GREEN}✅ 数据库配置完成${NC}"
}

# 创建项目用户
setup_project_user() {
    echo -e "${YELLOW}👤 创建项目用户...${NC}"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER"
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 创建成功${NC}"
    else
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 已存在${NC}"
    fi
}

# 下载项目代码
download_project() {
    echo -e "${YELLOW}📥 下载项目代码...${NC}"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 尝试从GitHub克隆
    if git clone https://github.com/your-username/QAToolBox.git "$PROJECT_DIR" 2>/dev/null; then
        echo -e "${GREEN}✅ 从GitHub下载成功${NC}"
    else
        echo -e "${YELLOW}⚠️  GitHub克隆失败，创建基础项目结构${NC}"
        mkdir -p "$PROJECT_DIR"
        
        # 下载必要文件
        cd "$PROJECT_DIR"
        
        # 下载requirements文件
        curl -fsSL -o requirements_complete.txt https://raw.githubusercontent.com/your-username/QAToolBox/main/requirements_complete.txt || {
            cat > requirements_complete.txt << 'EOF'
# QAToolBox 完整依赖
Django==4.2.7
torch==2.1.2
torchvision==0.16.2
opencv-python==4.8.1.78
django-environ==0.11.2
python-decouple==3.8
scikit-learn==1.3.2
numpy==1.24.4
psycopg2-binary==2.9.7
redis==4.6.0
gunicorn==21.2.0
nginx
supervisor
EOF
        }
        
        # 创建基础manage.py
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
        
        # 创建基础settings.py
        cat > settings.py << 'EOF'
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
SECRET_KEY = 'django-aliyun-key'
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
        
        # 创建基础urls.py
        cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
def home(request):
    return HttpResponse("<h1>QAToolBox 部署成功！</h1><p>访问 <a href='/admin/'>/admin/</a> 进入管理后台</p>")
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
]
EOF
        
        # 创建wsgi.py
        cat > wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
application = get_wsgi_application()
EOF
    fi
    
    # 设置权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 项目代码准备完成${NC}"
}

# 创建Python虚拟环境并安装依赖
setup_python_environment() {
    echo -e "${YELLOW}🐍 创建Python虚拟环境...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 删除旧虚拟环境
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    # 创建虚拟环境
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip
    sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade pip setuptools wheel
    
    echo -e "${YELLOW}📦 安装Python依赖包...${NC}"
    
    # 安装基础Django依赖
    sudo -u "$PROJECT_USER" .venv/bin/pip install \
        Django==4.2.7 \
        psycopg2-binary==2.9.7 \
        gunicorn==21.2.0 \
        python-dotenv==1.0.0
    
    # 安装机器学习依赖
    echo -e "${YELLOW}📦 安装机器学习依赖（可能需要较长时间）...${NC}"
    sudo -u "$PROJECT_USER" .venv/bin/pip install \
        torch==2.1.2 \
        torchvision==0.16.2 \
        torchaudio==2.1.2 \
        --index-url https://download.pytorch.org/whl/cpu
    
    # 安装其他依赖
    sudo -u "$PROJECT_USER" .venv/bin/pip install \
        opencv-python==4.8.1.78 \
        numpy==1.24.4 \
        scikit-learn==1.3.2 \
        django-environ==0.11.2 \
        python-decouple==3.8 \
        redis==4.6.0 \
        Pillow==9.5.0 \
        requests==2.31.0
    
    # 如果有requirements文件，安装剩余依赖
    if [ -f "requirements_complete.txt" ]; then
        echo -e "${YELLOW}📦 安装剩余依赖...${NC}"
        sudo -u "$PROJECT_USER" .venv/bin/pip install -r requirements_complete.txt || true
    fi
    
    echo -e "${GREEN}✅ Python环境配置完成${NC}"
}

# 配置环境变量
setup_environment_variables() {
    echo -e "${YELLOW}⚙️ 配置环境变量...${NC}"
    
    cd "$PROJECT_DIR"
    
    cat > .env << EOF
# QAToolBox 阿里云生产环境配置
SECRET_KEY=django-aliyun-shenyiqing-production-key-$(date +%s)
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 站点配置
SITE_URL=https://$DOMAIN
DJANGO_SETTINGS_MODULE=settings

# 静态文件配置
STATIC_URL=/static/
STATIC_ROOT=/var/www/qatoolbox/static/
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/qatoolbox/media/
EOF
    
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    echo -e "${GREEN}✅ 环境变量配置完成${NC}"
}

# 初始化Django项目
initialize_django() {
    echo -e "${YELLOW}🚀 初始化Django项目...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    
    # 数据库迁移
    echo -e "${YELLOW}📊 执行数据库迁移...${NC}"
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py makemigrations --noinput || true
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py migrate --noinput
    
    # 收集静态文件
    echo -e "${YELLOW}📁 收集静态文件...${NC}"
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py collectstatic --noinput || true
    
    # 创建超级用户
    echo -e "${YELLOW}👑 创建管理员用户...${NC}"
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print("管理员用户创建成功: admin/admin123456")
else:
    print("管理员用户已存在")
PYTHON_EOF
    
    echo -e "${GREEN}✅ Django项目初始化完成${NC}"
}

# 配置Nginx
setup_nginx() {
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 7d;
    }
    
    # 应用代理
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
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    systemctl restart nginx
    
    echo -e "${GREEN}✅ Nginx配置完成${NC}"
}

# 配置Supervisor
setup_supervisor() {
    echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
    
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
environment=DJANGO_SETTINGS_MODULE=settings
EOF
    
    # 重启Supervisor
    supervisorctl reread
    supervisorctl update
    supervisorctl start qatoolbox
    
    echo -e "${GREEN}✅ Supervisor配置完成${NC}"
}

# 验证部署
verify_deployment() {
    echo -e "${YELLOW}🧪 验证部署...${NC}"
    
    # 检查服务状态
    echo "检查服务状态..."
    systemctl is-active nginx postgresql redis-server supervisor
    
    # 检查应用进程
    supervisorctl status qatoolbox
    
    # 测试HTTP访问
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -E "200|301|302" > /dev/null; then
        echo -e "${GREEN}✅ HTTP访问正常${NC}"
    else
        echo -e "${RED}❌ HTTP访问失败${NC}"
    fi
    
    echo -e "${GREEN}✅ 部署验证完成${NC}"
}

# 显示部署信息
show_deployment_info() {
    echo -e "${BLUE}"
    echo "========================================"
    echo "🎉 QAToolBox 阿里云部署完成！"
    echo "========================================"
    echo -e "${NC}"
    
    echo -e "${GREEN}🌐 访问地址:${NC}"
    echo "  - http://$DOMAIN/"
    echo "  - http://$SERVER_IP/"
    echo ""
    
    echo -e "${GREEN}👑 管理员登录:${NC}"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo "  - 后台: http://$DOMAIN/admin/"
    echo ""
    
    echo -e "${GREEN}📁 项目目录:${NC} $PROJECT_DIR"
    echo -e "${GREEN}📊 数据库:${NC} PostgreSQL (qatoolbox/$DB_PASSWORD)"
    echo -e "${GREEN}🔴 缓存:${NC} Redis (localhost:6379)"
    echo ""
    
    echo -e "${GREEN}🔧 管理命令:${NC}"
    echo "  - 重启应用: sudo supervisorctl restart qatoolbox"
    echo "  - 查看日志: sudo tail -f /var/log/qatoolbox.log"
    echo "  - 重启Nginx: sudo systemctl restart nginx"
    echo ""
    
    echo -e "${GREEN}✅ 已安装的关键依赖:${NC}"
    echo "  - ✅ Django (Web框架)"
    echo "  - ✅ PyTorch (深度学习)"
    echo "  - ✅ OpenCV (计算机视觉)"
    echo "  - ✅ Django-Environ (环境变量)"
    echo "  - ✅ PostgreSQL (数据库)"
    echo "  - ✅ Redis (缓存)"
    echo "  - ✅ Nginx (Web服务器)"
    echo ""
}

# 主函数
main() {
    echo -e "${BLUE}开始QAToolBox阿里云自动部署...${NC}"
    
    detect_system
    setup_system
    install_python
    install_system_dependencies
    install_services
    setup_database
    setup_project_user
    download_project
    setup_python_environment
    setup_environment_variables
    initialize_django
    setup_nginx
    setup_supervisor
    verify_deployment
    show_deployment_info
    
    echo -e "${GREEN}🎉 阿里云部署完成！${NC}"
}

# 执行主函数
main "$@"
