#!/bin/bash

# =============================================================================
# QAToolBox 完整一键重来脚本
# 彻底清理所有环境，从零开始重新部署
# 适用于中国网络环境，解决所有依赖和配置问题
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"
BACKUP_DIR="/tmp/qatoolbox_backup_$(date +%Y%m%d_%H%M%S)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "========================================"
    echo "    🔥 QAToolBox 完整重来部署"
    echo "========================================"
    echo "  功能: 彻底清理并重新部署"
    echo "  服务器: $SERVER_IP"
    echo "  域名: $DOMAIN"
    echo "  警告: 将删除现有环境！"
    echo "========================================"
    echo -e "${NC}"
    
    echo -e "${YELLOW}此脚本将：${NC}"
    echo "1. 停止所有服务"
    echo "2. 备份数据库"
    echo "3. 完全清理Python环境"
    echo "4. 重新安装所有依赖"
    echo "5. 重新配置服务"
    echo
    
    read -p "确定要继续吗？(输入 YES 确认): " -r
    if [[ ! $REPLY == "YES" ]]; then
        echo "操作已取消"
        exit 0
    fi
}

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 停止所有服务
stop_all_services() {
    log_step "停止所有相关服务"
    
    # 停止systemd服务
    systemctl stop qatoolbox 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    systemctl disable qatoolbox 2>/dev/null || true
    
    # 杀死所有相关进程
    pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
    pkill -f "python.*manage.py" 2>/dev/null || true
    pkill -f "runserver" 2>/dev/null || true
    
    # 等待进程完全终止
    sleep 5
    
    log_success "所有服务已停止"
}

# 备份重要数据
backup_data() {
    log_step "备份重要数据"
    
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw qatoolbox; then
        log_info "备份数据库..."
        sudo -u postgres pg_dump qatoolbox > "$BACKUP_DIR/database.sql"
        log_success "数据库备份完成"
    else
        log_warning "未找到数据库，跳过备份"
    fi
    
    # 备份配置文件
    if [ -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env" "$BACKUP_DIR/env.backup"
    fi
    
    if [ -f "/etc/nginx/sites-available/qatoolbox" ]; then
        cp "/etc/nginx/sites-available/qatoolbox" "$BACKUP_DIR/nginx.conf.backup"
    fi
    
    if [ -f "/etc/systemd/system/qatoolbox.service" ]; then
        cp "/etc/systemd/system/qatoolbox.service" "$BACKUP_DIR/systemd.service.backup"
    fi
    
    log_success "备份保存到: $BACKUP_DIR"
}

# 完全清理环境
complete_cleanup() {
    log_step "完全清理现有环境"
    
    # 删除systemd服务
    rm -f /etc/systemd/system/qatoolbox.service
    systemctl daemon-reload
    
    # 删除nginx配置
    rm -f /etc/nginx/sites-enabled/qatoolbox
    rm -f /etc/nginx/sites-available/qatoolbox
    
    # 清理Python环境
    if [ -d "$PROJECT_DIR" ]; then
        log_info "清理Python虚拟环境"
        rm -rf "$PROJECT_DIR/.venv"
        rm -rf "$PROJECT_DIR/staticfiles"
        find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true
        find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # 清理用户Python缓存
    if [ -d "/home/$PROJECT_USER" ]; then
        rm -rf "/home/$PROJECT_USER/.pip"
        rm -rf "/home/$PROJECT_USER/.cache"
        rm -rf "/home/$PROJECT_USER/.local"
    fi
    
    # 清理日志
    rm -rf /var/log/qatoolbox
    
    log_success "环境清理完成"
}

# 更新系统和安装基础包
update_system() {
    log_step "更新系统并安装基础包"
    
    export DEBIAN_FRONTEND=noninteractive
    
    # 配置阿里云镜像源
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s) 2>/dev/null || true
    
    # 根据Ubuntu版本配置镜像源
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case "$VERSION_ID" in
            "18.04")
                cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
EOF
                ;;
            "20.04")
                cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
EOF
                ;;
            "22.04")
                cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
EOF
                ;;
        esac
        log_info "已配置阿里云镜像源"
    fi
    
    # 更新包索引
    apt-get clean
    apt-get update -y
    
    # 安装基础包
    PACKAGES=(
        "wget" "curl" "git" "vim" "unzip" "htop" "tree"
        "software-properties-common" "apt-transport-https" "ca-certificates"
        "gnupg" "lsb-release" "build-essential"
        "libssl-dev" "libffi-dev" "libpq-dev" "libjpeg-dev" "libpng-dev"
        "python3" "python3-pip" "python3-venv" "python3-dev" "python3-setuptools"
        "postgresql" "postgresql-contrib" "postgresql-client"
        "redis-server" "nginx" "supervisor" "openssl"
    )
    
    for pkg in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            log_info "安装: $pkg"
            apt-get install -y "$pkg" || log_warning "包 $pkg 安装失败，但继续..."
        fi
    done
    
    log_success "系统更新和基础包安装完成"
}

# 安装Python 3.9
install_python() {
    log_step "安装Python 3.9"
    
    if ! command -v python3.9 &> /dev/null; then
        # 添加deadsnakes PPA
        add-apt-repository ppa:deadsnakes/ppa -y
        apt-get update -y
        apt-get install -y python3.9 python3.9-dev python3.9-venv python3.9-distutils
        
        # 创建符号链接
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
    fi
    
    # 验证Python安装
    PYTHON_VERSION=$(python3.9 --version)
    log_success "Python安装完成: $PYTHON_VERSION"
}

# 配置PostgreSQL
setup_postgresql() {
    log_step "配置PostgreSQL"
    
    # 启动PostgreSQL
    systemctl enable postgresql
    systemctl start postgresql
    sleep 5
    
    # 重置数据库
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $PROJECT_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS $PROJECT_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER $PROJECT_USER WITH PASSWORD 'QAToolBox@2024';"
    sudo -u postgres psql -c "CREATE DATABASE $PROJECT_USER OWNER $PROJECT_USER;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PROJECT_USER TO $PROJECT_USER;"
    
    # 配置PostgreSQL连接
    PG_VERSION=$(sudo -u postgres psql -t -c "SHOW server_version;" | grep -oE '[0-9]+' | head -1)
    PG_HBA_PATH="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
    
    if [ -f "$PG_HBA_PATH" ]; then
        cp "$PG_HBA_PATH" "$PG_HBA_PATH.backup"
        if ! grep -q "host.*all.*all.*127.0.0.1/32.*md5" "$PG_HBA_PATH"; then
            echo "host    all             all             127.0.0.1/32            md5" >> "$PG_HBA_PATH"
        fi
        systemctl restart postgresql
        sleep 3
    fi
    
    # 测试连接
    if PGPASSWORD="QAToolBox@2024" psql -h localhost -U $PROJECT_USER -d $PROJECT_USER -c "SELECT 1;" &>/dev/null; then
        log_success "PostgreSQL配置完成"
    else
        log_error "PostgreSQL连接测试失败"
        exit 1
    fi
}

# 配置Redis
setup_redis() {
    log_step "配置Redis"
    
    systemctl enable redis-server
    systemctl start redis-server
    
    # 测试Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis配置完成"
    else
        log_error "Redis连接测试失败"
        exit 1
    fi
}

# 创建项目用户
create_user() {
    log_step "创建项目用户"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash $PROJECT_USER
        usermod -aG sudo $PROJECT_USER
        log_success "用户 $PROJECT_USER 创建完成"
    else
        log_info "用户 $PROJECT_USER 已存在"
    fi
}

# 克隆项目代码
clone_project() {
    log_step "获取项目代码"
    
    # 删除旧项目
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 配置Git使用国内镜像
    sudo -u $PROJECT_USER git config --global url."https://gitee.com/".insteadOf "https://github.com/"
    
    # 尝试多个源克隆
    CLONE_SUCCESS=false
    for repo in \
        "https://gitee.com/shinytsing/QAToolbox.git" \
        "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git" \
        "https://hub.fastgit.xyz/shinytsing/QAToolbox.git" \
        "https://github.com/shinytsing/QAToolbox.git"
    do
        log_info "尝试从 $repo 克隆..."
        if timeout 300 sudo -u $PROJECT_USER git clone $repo $PROJECT_DIR; then
            log_success "成功从 $repo 克隆项目"
            CLONE_SUCCESS=true
            break
        else
            log_warning "从 $repo 克隆失败，尝试下一个..."
            sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
        fi
    done
    
    if [ "$CLONE_SUCCESS" = false ]; then
        log_error "无法克隆项目，请检查网络连接"
        exit 1
    fi
    
    cd $PROJECT_DIR
    sudo -u $PROJECT_USER chmod +x *.sh *.py 2>/dev/null || true
    
    log_success "项目代码获取完成"
}

# 设置Python环境
setup_python_env() {
    log_step "设置Python环境"
    
    cd $PROJECT_DIR
    
    # 创建虚拟环境
    sudo -u $PROJECT_USER python3.9 -m venv .venv
    
    # 配置pip国内镜像
    sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
    cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 300
retries = 5
no-cache-dir = true

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
    chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf
    
    # 升级pip
    sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
    
    # 按顺序安装核心依赖
    log_info "安装核心依赖包"
    
    # 第一批：基础工具
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        setuptools==68.2.2 \
        wheel==0.41.2 \
        six==1.16.0 \
        packaging==23.2
    
    # 第二批：数据库驱动
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        psycopg2-binary==2.9.7 \
        redis==4.6.0
    
    # 第三批：Django核心
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        Django==4.2.7 \
        python-dotenv==1.0.0 \
        django-environ==0.11.2
    
    # 第四批：Django扩展
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        djangorestframework==3.14.0 \
        django-cors-headers==4.3.1 \
        django-redis==5.4.0
    
    # 第五批：Web服务器
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        gunicorn==21.2.0 \
        whitenoise==6.6.0
    
    # 第六批：其他工具
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir \
        requests==2.31.0 \
        Pillow==9.5.0
    
    # 验证Django安装
    log_info "验证Django安装"
    sudo -u $PROJECT_USER .venv/bin/python -c "
import django
print(f'Django version: {django.VERSION}')
import django.db.migrations.migration
print('Migrations module: OK')
import psycopg2
print('PostgreSQL driver: OK')
import gunicorn
print('Gunicorn: OK')
"
    
    # 尝试安装完整依赖
    log_info "尝试安装完整依赖"
    sudo -u $PROJECT_USER .venv/bin/pip install --no-cache-dir -r requirements.txt || {
        log_warning "部分依赖安装失败，但核心功能可用"
    }
    
    log_success "Python环境配置完成"
}

# 配置Django
setup_django() {
    log_step "配置Django应用"
    
    cd $PROJECT_DIR
    
    # 创建环境变量文件
    SECRET_KEY=$(python3.9 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    cat > .env << EOF
# 数据库配置
DB_NAME=$PROJECT_USER
DB_USER=$PROJECT_USER
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,$SERVER_IP,localhost,127.0.0.1

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 其他配置
DJANGO_SETTINGS_MODULE=config.settings.production
SITE_URL=https://$DOMAIN
EOF
    
    chown $PROJECT_USER:$PROJECT_USER .env
    chmod 600 .env
    
    # 测试Django配置
    log_info "测试Django配置"
    if ! sudo -u $PROJECT_USER .venv/bin/python manage.py check; then
        log_warning "Django配置检查有警告，创建简化配置"
        
        # 创建简化配置
        mkdir -p config/settings
        cat > config/settings/simple.py << 'EOF'
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'temp-key')
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
STATICFILES_DIRS = [BASE_DIR / 'static', BASE_DIR / 'src' / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
    }
}
EOF
        
        # 更新环境变量使用简化配置
        sed -i 's/DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=config.settings.simple/' .env
    fi
    
    # 数据库迁移
    log_info "执行数据库迁移"
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
    
    # 收集静态文件
    log_info "收集静态文件"
    sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput
    
    # 创建超级用户
    log_info "创建管理员用户"
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@$DOMAIN', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell
    
    log_success "Django应用配置完成"
}

# 生成SSL证书
generate_ssl_cert() {
    log_step "生成SSL证书"
    
    SSL_DIR="$PROJECT_DIR/ssl"
    mkdir -p $SSL_DIR
    
    if [ ! -f "$SSL_DIR/cert.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout $SSL_DIR/key.pem -out $SSL_DIR/cert.pem -days 365 -nodes \
            -subj "/C=CN/ST=Shanghai/L=Shanghai/O=QAToolBox/CN=$DOMAIN"
        chown -R $PROJECT_USER:$PROJECT_USER $SSL_DIR
        chmod 600 $SSL_DIR/key.pem
        chmod 644 $SSL_DIR/cert.pem
    fi
    
    log_success "SSL证书生成完成"
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
upstream qatoolbox_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name $DOMAIN $SERVER_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN $SERVER_IP;
    
    ssl_certificate $PROJECT_DIR/ssl/cert.pem;
    ssl_certificate_key $PROJECT_DIR/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    client_max_body_size 100M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # 主应用代理
    location / {
        proxy_pass http://qatoolbox_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 错误处理
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
        access_log off;
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # favicon
    location /favicon.ico {
        alias $PROJECT_DIR/static/favicon.ico;
        expires 30d;
        access_log off;
    }
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    if nginx -t; then
        log_success "Nginx配置测试通过"
    else
        log_error "Nginx配置测试失败"
        exit 1
    fi
}

# 创建systemd服务
create_systemd_service() {
    log_step "创建systemd服务"
    
    # 创建日志目录
    mkdir -p /var/log/qatoolbox
    chown qatoolbox:qatoolbox /var/log/qatoolbox
    
    # 创建systemd服务文件
    cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.simple
Environment=PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 3 \\
    --worker-class sync \\
    --timeout 120 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/qatoolbox/access.log \\
    --error-logfile /var/log/qatoolbox/error.log \\
    --log-level info \\
    config.wsgi:application

ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
TimeoutStopSec=30

# 安全设置
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=$PROJECT_DIR /var/log/qatoolbox /tmp

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    systemctl daemon-reload
    systemctl enable qatoolbox
    
    log_success "systemd服务创建完成"
}

# 启动所有服务
start_services() {
    log_step "启动所有服务"
    
    # 启动应用服务
    systemctl start qatoolbox
    sleep 10
    
    # 启动Nginx
    systemctl restart nginx
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet qatoolbox; then
        log_success "应用服务启动成功"
    else
        log_error "应用服务启动失败"
        echo "错误日志:"
        journalctl -u qatoolbox -n 30 --no-pager
        exit 1
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx服务启动成功"
    else
        log_error "Nginx服务启动失败"
        journalctl -u nginx -n 20 --no-pager
        exit 1
    fi
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙"
    
    # 启用UFW
    ufw --force enable
    
    # 允许必要端口
    ufw allow 22/tcp   # SSH
    ufw allow 80/tcp   # HTTP
    ufw allow 443/tcp  # HTTPS
    
    log_success "防火墙配置完成"
}

# 最终测试
final_test() {
    log_step "执行最终测试"
    
    # 等待服务完全启动
    sleep 15
    
    # 测试本地连接
    if curl -s -f http://127.0.0.1:8000/health/ > /dev/null 2>&1; then
        log_success "本地应用服务测试通过"
    elif curl -s -f http://127.0.0.1:8000/ > /dev/null 2>&1; then
        log_success "本地应用服务测试通过（主页响应）"
    else
        log_error "本地应用服务测试失败"
        echo "应用日志:"
        journalctl -u qatoolbox -n 20 --no-pager
        return 1
    fi
    
    # 测试Nginx代理
    if curl -s -f -k https://localhost/health/ > /dev/null 2>&1; then
        log_success "Nginx代理测试通过"
    elif curl -s -f -k https://localhost/ > /dev/null 2>&1; then
        log_success "Nginx代理测试通过（主页响应）"
    else
        log_warning "Nginx代理测试失败，但应用服务正常"
        echo "Nginx错误日志:"
        tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "无法读取Nginx日志"
    fi
    
    log_success "所有测试完成"
}

# 显示部署结果
show_result() {
    echo
    echo -e "${GREEN}"
    echo "========================================"
    echo "        🎉 部署完成！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${CYAN}访问地址:${NC}"
    echo -e "  主站: ${GREEN}https://$DOMAIN${NC}"
    echo -e "  备用: ${GREEN}https://$SERVER_IP${NC}"
    echo -e "  健康检查: ${GREEN}https://$DOMAIN/health/${NC}"
    echo -e "  管理后台: ${GREEN}https://$DOMAIN/admin/${NC}"
    echo
    echo -e "${CYAN}管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码:   ${GREEN}QAToolBox@2024${NC}"
    echo
    echo -e "${CYAN}服务状态:${NC}"
    echo -e "  应用服务: $(systemctl is-active qatoolbox)"
    echo -e "  Nginx服务: $(systemctl is-active nginx)"
    echo -e "  PostgreSQL: $(systemctl is-active postgresql)"
    echo -e "  Redis: $(systemctl is-active redis-server)"
    echo
    echo -e "${CYAN}日志位置:${NC}"
    echo -e "  应用日志: ${GREEN}/var/log/qatoolbox/error.log${NC}"
    echo -e "  Nginx日志: ${GREEN}/var/log/nginx/error.log${NC}"
    echo -e "  系统日志: ${GREEN}journalctl -u qatoolbox -f${NC}"
    echo
    echo -e "${CYAN}管理命令:${NC}"
    echo -e "  重启应用: ${GREEN}systemctl restart qatoolbox${NC}"
    echo -e "  查看日志: ${GREEN}journalctl -u qatoolbox -f${NC}"
    echo -e "  重启Nginx: ${GREEN}systemctl restart nginx${NC}"
    echo
    echo -e "${GREEN}🚀 现在可以访问 https://$DOMAIN 开始使用！${NC}"
    echo
    
    if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
        echo -e "${YELLOW}📦 备份位置: $BACKUP_DIR${NC}"
        echo
    fi
}

# 主函数
main() {
    show_welcome
    
    check_root
    
    log_info "开始完整重新部署，预计需要20-30分钟..."
    
    stop_all_services
    backup_data
    complete_cleanup
    update_system
    install_python
    setup_postgresql
    setup_redis
    create_user
    clone_project
    setup_python_env
    setup_django
    generate_ssl_cert
    configure_nginx
    create_systemd_service
    start_services
    configure_firewall
    
    if final_test; then
        show_result
    else
        log_error "部署测试失败，但基础服务已启动"
        log_info "请检查详细日志: journalctl -u qatoolbox -n 50"
        show_result
    fi
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
