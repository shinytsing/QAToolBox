#!/bin/bash

# =============================================================================
# QAToolBox 智能路径检测修复脚本
# 自动检测项目路径并修复
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
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
echo "    🔍 QAToolBox 智能路径检测修复"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 智能检测项目路径
detect_project_path() {
    log_info "智能检测项目路径..."
    
    # 可能的项目路径
    POSSIBLE_PATHS=(
        "/home/qatoolbox/QAToolBox"
        "/home/qatoolbox/QAToolbox"
        "/home/qatoolbox/qatoolbox"
        "/opt/QAToolBox"
        "/var/www/QAToolBox"
        "/root/QAToolBox"
        "/home/ubuntu/QAToolBox"
    )
    
    PROJECT_DIR=""
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -f "$path/manage.py" ]; then
            PROJECT_DIR="$path"
            log_success "找到项目路径: $PROJECT_DIR"
            break
        fi
    done
    
    # 如果还没找到，尝试全局搜索
    if [ -z "$PROJECT_DIR" ]; then
        log_info "全局搜索 manage.py 文件..."
        FOUND_PATHS=$(find /home /opt /var/www /root 2>/dev/null -name "manage.py" -type f | head -5)
        
        if [ -n "$FOUND_PATHS" ]; then
            echo "找到以下可能的Django项目:"
            echo "$FOUND_PATHS"
            
            # 选择第一个包含QAToolBox的路径
            for path in $FOUND_PATHS; do
                dir_path=$(dirname "$path")
                if [[ "$dir_path" == *"QAToolBox"* ]] || [[ "$dir_path" == *"QAToolbox"* ]] || [[ "$dir_path" == *"qatoolbox"* ]]; then
                    PROJECT_DIR="$dir_path"
                    log_success "自动选择项目路径: $PROJECT_DIR"
                    break
                fi
            done
            
            # 如果还没选中，选择第一个
            if [ -z "$PROJECT_DIR" ]; then
                PROJECT_DIR=$(dirname $(echo "$FOUND_PATHS" | head -1))
                log_warning "使用第一个找到的Django项目: $PROJECT_DIR"
            fi
        fi
    fi
    
    if [ -z "$PROJECT_DIR" ]; then
        log_error "无法找到Django项目，请确保项目存在"
        echo "请检查以下路径是否存在manage.py文件:"
        for path in "${POSSIBLE_PATHS[@]}"; do
            echo "  - $path/manage.py"
        done
        exit 1
    fi
    
    # 验证项目结构
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        log_error "项目路径 $PROJECT_DIR 不包含 manage.py"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 项目路径确认: $PROJECT_DIR${NC}"
}

# 检测并创建项目用户
ensure_project_user() {
    if [ ! -d "/home/$PROJECT_USER" ]; then
        log_info "创建项目用户: $PROJECT_USER"
        useradd -m -s /bin/bash $PROJECT_USER
    fi
    
    # 确保用户对项目目录有权限
    chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
}

# 主要修复函数
main_fix() {
    # 检测项目路径
    detect_project_path
    
    # 确保项目用户存在
    ensure_project_user
    
    cd $PROJECT_DIR
    
    # 停止现有服务
    log_info "停止现有服务"
    systemctl stop qatoolbox 2>/dev/null || true
    pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
    sleep 3
    
    # 清理Git配置
    log_info "清理Git重定向配置"
    sudo -u $PROJECT_USER git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true
    git config --global --unset url."https://gitee.com/".insteadOf 2>/dev/null || true
    
    # 检查Python版本
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        if command -v python &> /dev/null; then
            PYTHON_CMD="python"
        else
            log_error "Python未安装"
            exit 1
        fi
    fi
    
    # 重建虚拟环境
    log_info "重建Python虚拟环境"
    if [ -d ".venv" ]; then
        rm -rf .venv
    fi
    sudo -u $PROJECT_USER $PYTHON_CMD -m venv .venv
    
    # 配置pip镜像源
    sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
    cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF
    chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf
    
    # 安装依赖
    log_info "安装Python依赖"
    sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
    
    # 核心依赖
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        setuptools wheel python-dotenv django-environ
    
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        Django==4.2.7 psycopg2-binary redis django-redis
    
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        djangorestframework django-cors-headers whitenoise gunicorn
    
    # 尝试安装requirements.txt中的其他依赖
    if [ -f "requirements.txt" ]; then
        log_info "尝试安装requirements.txt中的依赖"
        sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt --no-cache-dir || {
            log_warning "部分依赖安装失败，但核心依赖已安装"
        }
    fi
    
    # 确保数据库服务运行
    log_info "确保数据库服务运行"
    systemctl start postgresql 2>/dev/null || true
    systemctl start redis-server 2>/dev/null || true
    sleep 3
    
    # 创建数据库用户（如果不存在）
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
DJANGO_SETTINGS_MODULE=config.settings.minimal
EOF
    chown $PROJECT_USER:$PROJECT_USER .env
    
    # 创建简化Django配置
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
MINIMALEOF
    
    chown $PROJECT_USER:$PROJECT_USER config/settings/minimal.py
    
    # 检查manage.py是否存在
    if [ ! -f "manage.py" ]; then
        log_error "manage.py 文件不存在于 $PROJECT_DIR"
        ls -la
        exit 1
    fi
    
    # Django迁移
    log_info "执行Django迁移"
    export DJANGO_SETTINGS_MODULE=config.settings.minimal
    
    # 测试Django配置
    if sudo -u $PROJECT_USER .venv/bin/python manage.py check --deploy; then
        log_success "Django配置检查通过"
    else
        log_warning "Django配置检查有警告，但继续执行"
    fi
    
    # 执行迁移
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
    sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput
    
    # 创建管理员用户
    log_info "创建管理员用户"
    echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell
    
    # 创建日志目录
    mkdir -p /var/log/qatoolbox
    chown qatoolbox:qatoolbox /var/log/qatoolbox
    
    # 创建systemd服务
    log_info "配置systemd服务"
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
Environment=DJANGO_SETTINGS_MODULE=config.settings.minimal
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
    
    # 测试HTTP响应
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")
    echo -e "HTTP响应: ${GREEN}$HTTP_CODE${NC}"
    
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
}

# 运行主修复函数
main_fix
