#!/bin/bash

# QAToolBox 完整一键部署脚本 - Ubuntu版本
# 包含所有功能：系统环境、数据库、缓存、Web服务器、SSL、监控等

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置变量
DOMAIN="${1:-shenyiqing.xin}"
SERVER_IP="${2:-47.103.143.152}"
PROJECT_USER="qatoolbox"
PROJECT_DIR="/opt/qatoolbox"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="/var/log/qatoolbox"

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

# 检查系统要求
check_requirements() {
    log_step "检查系统要求"
    
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此脚本: sudo bash $0"
        exit 1
    fi
    
    # 检查Ubuntu版本
    if ! command -v lsb_release &> /dev/null; then
        apt update && apt install -y lsb-release
    fi
    
    UBUNTU_VERSION=$(lsb_release -rs)
    log_info "检测到Ubuntu版本: $UBUNTU_VERSION"
    
    # 检查内存
    MEMORY_GB=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    if [ "$MEMORY_GB" -lt 2 ]; then
        log_warning "建议至少2GB内存，当前: ${MEMORY_GB}GB"
    fi
    
    log_success "系统要求检查完成"
}

# 更新系统并安装基础包
install_base_packages() {
    log_step "更新系统并安装基础包"
    
    # 配置APT使用阿里云镜像
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)
    UBUNTU_CODENAME=$(lsb_release -cs)
    
    tee /etc/apt/sources.list > /dev/null << EOF
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-backports main restricted universe multiverse
EOF
    
    # 禁用command-not-found更新以避免apt_pkg错误
    chmod 000 /usr/lib/cnf-update-db 2>/dev/null || true
    
    # 更新系统
    export DEBIAN_FRONTEND=noninteractive
    apt update && apt upgrade -y
    
    # 安装基础开发工具
    apt install -y \
        wget curl git vim unzip \
        build-essential cmake pkg-config \
        software-properties-common \
        apt-transport-https ca-certificates gnupg lsb-release \
        htop tree zip unzip \
        ufw fail2ban \
        supervisor \
        nginx \
        redis-server \
        postgresql postgresql-contrib \
        python3 python3-pip python3-venv python3-dev \
        libssl-dev libffi-dev libpq-dev \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
        libgomp1 libgtk-3-dev libavcodec-dev libavformat-dev \
        libswscale-dev libv4l-dev libxvidcore-dev libx264-dev \
        libjpeg-dev libpng-dev libtiff-dev libatlas-base-dev \
        libeigen3-dev libgtk2.0-dev libcairo2-dev \
        libgirepository1.0-dev
    
    # 安装Python 3.9（如果不存在）
    if ! command -v python3.9 &> /dev/null; then
        add-apt-repository ppa:deadsnakes/ppa -y
        apt update
        apt install -y python3.9 python3.9-venv python3.9-dev
    fi
    
    log_success "基础包安装完成"
}

# 配置PostgreSQL
setup_postgresql() {
    log_step "配置PostgreSQL数据库"
    
    # 启动PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # 配置数据库
    sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS qatoolbox;
DROP USER IF EXISTS qatoolbox;
CREATE USER qatoolbox WITH PASSWORD 'qatoolbox_secure_2024!';
CREATE DATABASE qatoolbox OWNER qatoolbox;
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
ALTER USER qatoolbox CREATEDB;
\q
EOF
    
    # 配置PostgreSQL监听所有IP
    PG_VERSION=$(sudo -u postgres psql -t -c "SHOW server_version;" | grep -oE '[0-9]+' | head -1)
    PG_CONF_PATH="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    PG_HBA_PATH="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
    
    if [ -f "$PG_CONF_PATH" ]; then
        sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_PATH"
        sed -i "s/#max_connections = 100/max_connections = 200/" "$PG_CONF_PATH"
        sed -i "s/#shared_buffers = 128MB/shared_buffers = 256MB/" "$PG_CONF_PATH"
        
        # 配置认证
        echo "host    qatoolbox    qatoolbox    127.0.0.1/32    md5" >> "$PG_HBA_PATH"
    fi
    
    systemctl restart postgresql
    
    # 测试连接
    if sudo -u postgres psql -d qatoolbox -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "PostgreSQL配置完成"
    else
        log_error "PostgreSQL配置失败"
        exit 1
    fi
}

# 配置Redis
setup_redis() {
    log_step "配置Redis缓存服务"
    
    # 配置Redis
    sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
    sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
    
    systemctl start redis-server
    systemctl enable redis-server
    
    # 测试Redis连接
    if redis-cli ping | grep -q PONG; then
        log_success "Redis配置完成"
    else
        log_error "Redis配置失败"
        exit 1
    fi
}

# 创建项目用户和目录
setup_project_user() {
    log_step "创建项目用户和目录"
    
    # 创建用户
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -r -s /bin/bash -d /home/$PROJECT_USER -m $PROJECT_USER
        log_info "用户 $PROJECT_USER 创建完成"
    else
        log_info "用户 $PROJECT_USER 已存在"
    fi
    
    # 创建项目目录
    mkdir -p $PROJECT_DIR $LOG_DIR
    chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR $LOG_DIR
    
    log_success "项目用户和目录创建完成"
}

# 克隆项目代码
clone_project() {
    log_step "克隆项目代码"
    
    if [ -d "$PROJECT_DIR/.git" ]; then
        log_info "项目已存在，更新代码"
        cd $PROJECT_DIR
        sudo -u $PROJECT_USER git pull || {
            log_warning "Git pull失败，尝试重新克隆"
            rm -rf $PROJECT_DIR/*
            clone_from_sources
        }
    else
        clone_from_sources
    fi
    
    cd $PROJECT_DIR
    chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
    log_success "项目代码准备完成"
}

clone_from_sources() {
    # 尝试多个Git源
    CLONE_SUCCESS=false
    for repo in \
        "https://gitee.com/shinytsing/QAToolbox.git" \
        "https://github.com/shinytsing/QAToolbox.git" \
        "https://hub.fastgit.xyz/shinytsing/QAToolbox.git"
    do
        log_info "尝试从 $repo 克隆..."
        if timeout 300 sudo -u $PROJECT_USER git clone $repo $PROJECT_DIR; then
            log_success "成功从 $repo 克隆项目"
            CLONE_SUCCESS=true
            break
        else
            log_warning "从 $repo 克隆失败"
            rm -rf $PROJECT_DIR 2>/dev/null || true
        fi
    done
    
    if [ "$CLONE_SUCCESS" = false ]; then
        log_error "无法克隆项目，请检查网络连接"
        exit 1
    fi
}

# 设置Python环境
setup_python_environment() {
    log_step "设置Python虚拟环境"
    
    cd $PROJECT_DIR
    
    # 创建虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        sudo -u $PROJECT_USER python3.9 -m venv $VENV_DIR
        log_info "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi
    
    # 配置pip使用清华镜像源
    sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
    sudo -u $PROJECT_USER tee /home/$PROJECT_USER/.pip/pip.conf > /dev/null << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
retries = 5

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
    
    # 升级pip
    sudo -u $PROJECT_USER $VENV_DIR/bin/pip install --upgrade pip
    
    # 安装wheel和基础依赖
    sudo -u $PROJECT_USER $VENV_DIR/bin/pip install wheel setuptools
    
    # 安装核心依赖
    sudo -u $PROJECT_USER $VENV_DIR/bin/pip install \
        Django gunicorn psycopg2-binary redis \
        django-environ opencv-python-headless psutil
    
    # 安装完整依赖
    sudo -u $PROJECT_USER $VENV_DIR/bin/pip install -r requirements.txt || {
        log_warning "部分依赖安装失败，继续执行"
    }
    
    log_success "Python环境设置完成"
}

# 配置Django环境
setup_django_environment() {
    log_step "配置Django环境"
    
    cd $PROJECT_DIR
    
    # 创建环境变量文件
    sudo -u $PROJECT_USER tee .env > /dev/null << EOF
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox_secure_2024!
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# Django配置
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,$DOMAIN,localhost,127.0.0.1

# 静态文件和媒体文件
STATIC_ROOT=$PROJECT_DIR/staticfiles
MEDIA_ROOT=$PROJECT_DIR/media

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
EOF
    
    # 创建必要目录
    sudo -u $PROJECT_USER mkdir -p staticfiles media logs
    
    log_success "Django环境配置完成"
}

# 执行数据库迁移
run_database_migrations() {
    log_step "执行数据库迁移"
    
    cd $PROJECT_DIR
    
    # 检查Django配置
    sudo -u $PROJECT_USER $VENV_DIR/bin/python manage.py check --settings=config.settings.production || {
        log_error "Django配置检查失败"
        return 1
    }
    
    # 执行迁移
    sudo -u $PROJECT_USER $VENV_DIR/bin/python manage.py makemigrations --settings=config.settings.production
    sudo -u $PROJECT_USER $VENV_DIR/bin/python manage.py migrate --settings=config.settings.production
    
    # 收集静态文件
    sudo -u $PROJECT_USER $VENV_DIR/bin/python manage.py collectstatic --noinput --settings=config.settings.production
    
    log_success "数据库迁移完成"
}

# 配置Gunicorn服务
setup_gunicorn_service() {
    log_step "配置Gunicorn服务"
    
    # 创建Gunicorn配置文件
    tee $PROJECT_DIR/gunicorn.conf.py > /dev/null << EOF
bind = "127.0.0.1:8000"
workers = 3
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 300
keepalive = 2
preload_app = True
user = "$PROJECT_USER"
group = "$PROJECT_USER"
pid = "$PROJECT_DIR/gunicorn.pid"
accesslog = "$LOG_DIR/gunicorn-access.log"
errorlog = "$LOG_DIR/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
EOF
    
    # 创建systemd服务文件
    tee /etc/systemd/system/qatoolbox.service > /dev/null << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=forking
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=$VENV_DIR/bin/gunicorn config.wsgi:application -c $PROJECT_DIR/gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
PIDFile=$PROJECT_DIR/gunicorn.pid
Restart=always
RestartSec=3
KillMode=mixed
TimeoutStopSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/gunicorn.conf.py
    
    log_success "Gunicorn服务配置完成"
}

# 配置Celery服务
setup_celery_service() {
    log_step "配置Celery异步任务服务"
    
    # 创建Celery worker服务
    tee /etc/systemd/system/qatoolbox-celery.service > /dev/null << EOF
[Unit]
Description=QAToolBox Celery Worker
After=network.target redis.service
Requires=redis.service

[Service]
Type=forking
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=$VENV_DIR/bin/celery -A config worker --detach --loglevel=info --logfile=$LOG_DIR/celery-worker.log --pidfile=$PROJECT_DIR/celery-worker.pid
ExecStop=/bin/kill -TERM \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建Celery beat服务
    tee /etc/systemd/system/qatoolbox-celery-beat.service > /dev/null << EOF
[Unit]
Description=QAToolBox Celery Beat
After=network.target redis.service
Requires=redis.service

[Service]
Type=forking
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=$VENV_DIR/bin/celery -A config beat --detach --loglevel=info --logfile=$LOG_DIR/celery-beat.log --pidfile=$PROJECT_DIR/celery-beat.pid
ExecStop=/bin/kill -TERM \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    log_success "Celery服务配置完成"
}

# 配置Nginx
setup_nginx() {
    log_step "配置Nginx Web服务器"
    
    # 创建SSL目录
    mkdir -p /etc/ssl/private /etc/ssl/certs
    
    # 生成SSL证书（自签名）
    if [ ! -f "/etc/ssl/certs/qatoolbox.crt" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/qatoolbox.key \
            -out /etc/ssl/certs/qatoolbox.crt \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/CN=$DOMAIN"
        
        chmod 600 /etc/ssl/private/qatoolbox.key
        chmod 644 /etc/ssl/certs/qatoolbox.crt
    fi
    
    # 创建Nginx配置
    tee /etc/nginx/sites-available/qatoolbox > /dev/null << EOF
# HTTP -> HTTPS重定向
server {
    listen 80;
    server_name $SERVER_IP $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS主配置
server {
    listen 443 ssl http2;
    server_name $SERVER_IP $DOMAIN;
    
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
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # 文件上传大小限制
    client_max_body_size 100M;
    
    # 日志配置
    access_log $LOG_DIR/nginx-access.log;
    error_log $LOG_DIR/nginx-error.log;
    
    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header Vary Accept-Encoding;
        gzip_static on;
    }
    
    # 媒体文件
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Favicon
    location /favicon.ico {
        alias $PROJECT_DIR/staticfiles/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        access_log off;
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
        proxy_buffering off;
        proxy_buffer_size 128k;
        proxy_buffers 100 128k;
    }
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t || {
        log_error "Nginx配置测试失败"
        exit 1
    }
    
    log_success "Nginx配置完成"
}

# 配置防火墙
setup_firewall() {
    log_step "配置防火墙"
    
    # 配置UFW
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    # 配置fail2ban
    tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
port = http,https
logpath = $LOG_DIR/nginx-error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = $LOG_DIR/nginx-error.log
maxretry = 10
EOF
    
    systemctl enable fail2ban
    systemctl restart fail2ban
    
    log_success "防火墙配置完成"
}

# 配置日志轮转
setup_log_rotation() {
    log_step "配置日志轮转"
    
    tee /etc/logrotate.d/qatoolbox > /dev/null << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $PROJECT_USER $PROJECT_USER
    postrotate
        systemctl reload nginx
        systemctl reload qatoolbox
    endscript
}
EOF
    
    log_success "日志轮转配置完成"
}

# 设置监控
setup_monitoring() {
    log_step "设置系统监控"
    
    # 创建监控脚本
    tee /usr/local/bin/qatoolbox-monitor.sh > /dev/null << 'EOF'
#!/bin/bash

LOG_FILE="/var/log/qatoolbox-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查服务状态
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo "[$DATE] $service: OK" >> $LOG_FILE
    else
        echo "[$DATE] $service: FAILED" >> $LOG_FILE
        systemctl restart $service
        echo "[$DATE] $service: RESTARTED" >> $LOG_FILE
    fi
}

check_service postgresql
check_service redis-server
check_service qatoolbox
check_service nginx

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] DISK: WARNING - Usage at ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查内存使用
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
if [ $MEMORY_USAGE -gt 85 ]; then
    echo "[$DATE] MEMORY: WARNING - Usage at ${MEMORY_USAGE}%" >> $LOG_FILE
fi
EOF
    
    chmod +x /usr/local/bin/qatoolbox-monitor.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/qatoolbox-monitor.sh") | crontab -
    
    log_success "监控设置完成"
}

# 启动所有服务
start_services() {
    log_step "启动所有服务"
    
    systemctl daemon-reload
    
    # 启用和启动服务
    systemctl enable postgresql redis-server nginx
    systemctl enable qatoolbox qatoolbox-celery qatoolbox-celery-beat
    
    systemctl restart postgresql
    systemctl restart redis-server
    systemctl restart qatoolbox
    systemctl restart qatoolbox-celery
    systemctl restart qatoolbox-celery-beat
    systemctl restart nginx
    
    # 等待服务启动
    sleep 10
    
    log_success "所有服务启动完成"
}

# 验证部署
verify_deployment() {
    log_step "验证部署状态"
    
    # 检查服务状态
    echo "📊 服务状态检查:"
    for service in postgresql redis-server qatoolbox qatoolbox-celery qatoolbox-celery-beat nginx; do
        if systemctl is-active --quiet $service; then
            echo "  ✅ $service: 运行正常"
        else
            echo "  ❌ $service: 启动失败"
        fi
    done
    
    # 检查端口监听
    echo
    echo "🔌 端口监听检查:"
    ss -tlnp | grep -E ':80|:443|:8000|:5432|:6379' | while read line; do
        echo "  📡 $line"
    done
    
    # 检查Web服务
    echo
    echo "🌐 Web服务检查:"
    if curl -k -s -o /dev/null -w "%{http_code}" https://localhost/ | grep -q "200\|301\|302"; then
        echo "  ✅ HTTPS服务: 正常访问"
    else
        echo "  ❌ HTTPS服务: 访问失败"
    fi
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "301\|302"; then
        echo "  ✅ HTTP重定向: 正常工作"
    else
        echo "  ❌ HTTP重定向: 配置错误"
    fi
    
    log_success "部署验证完成"
}

# 创建管理脚本
create_management_scripts() {
    log_step "创建管理脚本"
    
    # 状态检查脚本
    tee /usr/local/bin/qatoolbox-status > /dev/null << 'EOF'
#!/bin/bash
echo "🔍 QAToolBox 系统状态"
echo "====================="
echo
echo "📊 服务状态:"
for service in postgresql redis-server qatoolbox qatoolbox-celery qatoolbox-celery-beat nginx; do
    status=$(systemctl is-active $service)
    if [ "$status" = "active" ]; then
        echo "  ✅ $service: $status"
    else
        echo "  ❌ $service: $status"
    fi
done

echo
echo "💾 系统资源:"
echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)% 使用"
echo "  内存: $(free -h | awk 'NR==2{printf "使用 %s/%s (%.0f%%)", $3,$2,$3*100/$2}')"
echo "  磁盘: $(df -h / | awk 'NR==2{printf "%s/%s (%s)", $3,$2,$5}')"

echo
echo "📡 网络端口:"
ss -tlnp | grep -E ':80|:443|:8000|:5432|:6379'

echo
echo "📋 最近日志 (最后10行):"
tail -10 /var/log/qatoolbox/gunicorn-error.log 2>/dev/null || echo "  暂无错误日志"
EOF
    
    # 重启脚本
    tee /usr/local/bin/qatoolbox-restart > /dev/null << 'EOF'
#!/bin/bash
echo "🔄 重启 QAToolBox 服务..."
systemctl restart qatoolbox qatoolbox-celery qatoolbox-celery-beat nginx
echo "✅ 服务重启完成"
/usr/local/bin/qatoolbox-status
EOF
    
    # 更新脚本
    tee /usr/local/bin/qatoolbox-update > /dev/null << 'EOF'
#!/bin/bash
echo "📥 更新 QAToolBox..."
cd /opt/qatoolbox
sudo -u qatoolbox git pull
sudo -u qatoolbox .venv/bin/pip install -r requirements.txt
sudo -u qatoolbox .venv/bin/python manage.py migrate --settings=config.settings.production
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production
systemctl restart qatoolbox qatoolbox-celery qatoolbox-celery-beat
echo "✅ 更新完成"
EOF
    
    # 备份脚本
    tee /usr/local/bin/qatoolbox-backup > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/qatoolbox"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "💾 创建备份: $DATE"
echo "  备份数据库..."
sudo -u postgres pg_dump qatoolbox > $BACKUP_DIR/database_$DATE.sql
echo "  备份项目文件..."
tar -czf $BACKUP_DIR/project_$DATE.tar.gz -C /opt qatoolbox --exclude='.venv' --exclude='*.pyc'
echo "  备份配置文件..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/nginx/sites-available/qatoolbox /etc/systemd/system/qatoolbox*

echo "✅ 备份完成: $BACKUP_DIR/"
ls -lh $BACKUP_DIR/*$DATE*
EOF
    
    chmod +x /usr/local/bin/qatoolbox-*
    
    log_success "管理脚本创建完成"
}

# 显示完成信息
show_completion_info() {
    clear
    echo -e "${GREEN}"
    echo "🎉🎉🎉 QAToolBox 部署完成！🎉🎉🎉"
    echo -e "${NC}"
    echo "=============================================="
    echo
    echo -e "${CYAN}📱 访问地址:${NC}"
    echo "  🌐 HTTP:  http://$SERVER_IP"
    echo "  🔒 HTTPS: https://$SERVER_IP"
    echo "  🌍 域名:  https://$DOMAIN"
    echo
    echo -e "${CYAN}🔧 管理命令:${NC}"
    echo "  📊 查看状态: qatoolbox-status"
    echo "  🔄 重启服务: qatoolbox-restart"
    echo "  📥 更新系统: qatoolbox-update"
    echo "  💾 备份数据: qatoolbox-backup"
    echo
    echo -e "${CYAN}📋 系统服务:${NC}"
    echo "  查看应用日志: journalctl -u qatoolbox -f"
    echo "  查看Nginx日志: tail -f $LOG_DIR/nginx-error.log"
    echo "  查看Celery日志: tail -f $LOG_DIR/celery-worker.log"
    echo
    echo -e "${CYAN}👤 创建管理员账户:${NC}"
    echo "  cd $PROJECT_DIR"
    echo "  sudo -u $PROJECT_USER .venv/bin/python manage.py createsuperuser --settings=config.settings.production"
    echo
    echo -e "${CYAN}🔐 SSL证书:${NC}"
    echo "  当前使用自签名证书，如需正式证书请运行:"
    echo "  apt install certbot python3-certbot-nginx -y"
    echo "  certbot --nginx -d $DOMAIN"
    echo
    echo -e "${CYAN}📁 重要目录:${NC}"
    echo "  项目目录: $PROJECT_DIR"
    echo "  日志目录: $LOG_DIR"
    echo "  配置文件: /etc/nginx/sites-available/qatoolbox"
    echo
    echo -e "${GREEN}✨ 部署成功！您的QAToolBox已准备就绪！${NC}"
    echo "=============================================="
}

# 主执行流程
main() {
    echo -e "${CYAN}"
    echo "🚀 QAToolBox 完整一键部署脚本"
    echo "================================"
    echo "域名: $DOMAIN"
    echo "IP: $SERVER_IP"
    echo "用户: $PROJECT_USER"
    echo "目录: $PROJECT_DIR"
    echo -e "${NC}"
    echo
    
    check_requirements
    install_base_packages
    setup_postgresql
    setup_redis
    setup_project_user
    clone_project
    setup_python_environment
    setup_django_environment
    run_database_migrations
    setup_gunicorn_service
    setup_celery_service
    setup_nginx
    setup_firewall
    setup_log_rotation
    setup_monitoring
    start_services
    verify_deployment
    create_management_scripts
    show_completion_info
}

# 执行主函数
main "$@"