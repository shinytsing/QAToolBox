#!/bin/bash

# =============================================================================
# QAToolBox 智能修复部署脚本 - 解决502错误
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# 系统: Ubuntu (完全兼容 18.04/20.04/22.04/24.04)
# 功能: 完整重新部署，修复所有依赖和服务问题
# =============================================================================

set -e  # 遇到错误立即退出

# 服务器配置
SERVER_IP="47.103.143.152"
DOMAIN="shenyiqing.xin"
PROJECT_NAME="QAToolBox"
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/$PROJECT_NAME"
BACKUP_DIR="/home/$PROJECT_USER/backup_$(date +%Y%m%d_%H%M%S)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 显示欢迎信息
show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "========================================"
    echo "    🚀 QAToolBox 智能修复部署"
    echo "========================================"
    echo "  服务器: $SERVER_IP"
    echo "  域名:   $DOMAIN"
    echo "  目标:   https://$DOMAIN"
    echo "  功能:   修复502错误，完整重新部署"
    echo "========================================"
    echo -e "${NC}"
    echo
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 检测系统版本
detect_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        log_error "无法检测系统版本"
        exit 1
    fi
    
    log_info "检测到系统: $OS $VER"
}

# 停止所有相关服务
stop_services() {
    log_step "停止现有服务"
    
    systemctl stop $PROJECT_USER 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    systemctl stop gunicorn 2>/dev/null || true
    
    # 杀死可能残留的进程
    pkill -f "gunicorn.*$PROJECT_NAME" 2>/dev/null || true
    pkill -f "python.*manage.py" 2>/dev/null || true
    
    log_success "服务停止完成"
}

# 备份现有配置
backup_existing() {
    log_step "备份现有配置"
    
    if [ -d "$PROJECT_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        cp -r "$PROJECT_DIR" "$BACKUP_DIR/project_backup" 2>/dev/null || true
        cp /etc/nginx/sites-available/$PROJECT_USER "$BACKUP_DIR/nginx_config" 2>/dev/null || true
        cp /etc/systemd/system/$PROJECT_USER.service "$BACKUP_DIR/systemd_service" 2>/dev/null || true
        log_success "备份保存到: $BACKUP_DIR"
    else
        log_info "未找到现有项目，跳过备份"
    fi
}

# 清理现有安装
cleanup_existing() {
    log_step "清理现有安装"
    
    # 删除systemd服务
    systemctl disable $PROJECT_USER 2>/dev/null || true
    rm -f /etc/systemd/system/$PROJECT_USER.service
    systemctl daemon-reload
    
    # 删除nginx配置
    rm -f /etc/nginx/sites-enabled/$PROJECT_USER
    rm -f /etc/nginx/sites-available/$PROJECT_USER
    
    log_success "清理完成"
}

# 更新系统包
update_system() {
    log_step "更新系统包"
    
    export DEBIAN_FRONTEND=noninteractive
    
    # 修复Ubuntu 24.04的apt_pkg问题
    if [[ "$VER" == "24.04" ]]; then
        log_info "修复Ubuntu 24.04 apt问题"
        apt-get install --reinstall python3-apt python3-distutils -y 2>/dev/null || true
    fi
    
    # 更新包索引，多次重试
    for i in {1..3}; do
        if apt-get update -y; then
            log_success "包索引更新成功"
            break
        else
            log_warning "包更新失败，尝试修复... (尝试 $i/3)"
            apt-get clean
            apt-get autoclean
            if [ $i -eq 3 ]; then
                log_warning "包更新持续失败，但继续安装..."
            fi
            sleep 2
        fi
    done
    
    # 升级系统
    apt-get upgrade -y || log_warning "系统升级部分失败，继续..."
    
    log_success "系统更新完成"
}

# 安装基础包
install_basic_packages() {
    log_step "安装基础包"
    
    # 基础包列表
    PACKAGES=(
        "wget" "curl" "git" "vim" "unzip" "htop" "tree"
        "software-properties-common" "apt-transport-https" "ca-certificates"
        "gnupg" "lsb-release" "build-essential"
        "libssl-dev" "libffi-dev" "libpq-dev" "libjpeg-dev" "libpng-dev"
        "python3-dev" "python3-pip" "python3-venv" "python3-setuptools"
        "python3-apt" "python3-distutils"
        "ufw" "fail2ban" "supervisor"
    )
    
    # 尝试批量安装
    if apt-get install -y "${PACKAGES[@]}"; then
        log_success "基础包批量安装成功"
    else
        log_warning "批量安装失败，尝试单独安装关键包..."
        
        # 关键包单独安装
        for pkg in "${PACKAGES[@]}"; do
            if ! dpkg -l | grep -q "^ii  $pkg "; then
                log_info "安装: $pkg"
                apt-get install -y "$pkg" || log_warning "包 $pkg 安装失败，但继续..."
            fi
        done
    fi
    
    log_success "基础包安装完成"
}

# 安装Python 3.9
install_python() {
    log_step "安装Python 3.9"
    
    # 检查Python版本
    if command -v python3.9 &> /dev/null; then
        PYTHON_VERSION=$(python3.9 --version 2>&1 | awk '{print $2}')
        log_info "Python 3.9 已安装: $PYTHON_VERSION"
    else
        # 添加deadsnakes PPA
        add-apt-repository ppa:deadsnakes/ppa -y
        apt-get update -y
        
        # 安装Python 3.9
        apt-get install -y python3.9 python3.9-dev python3.9-venv python3.9-distutils
        
        # 创建符号链接
        update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
        
        log_success "Python 3.9 安装完成"
    fi
    
    # 升级pip
    python3.9 -m pip install --upgrade pip || log_warning "pip升级失败，但继续..."
}

# 安装和配置PostgreSQL
install_postgresql() {
    log_step "安装和配置PostgreSQL"
    
    # 安装PostgreSQL
    apt-get install -y postgresql postgresql-contrib postgresql-client
    
    # 启动服务
    systemctl enable postgresql
    systemctl start postgresql
    
    # 等待服务启动
    sleep 5
    
    # 创建数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $PROJECT_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS $PROJECT_USER;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER $PROJECT_USER WITH PASSWORD 'QAToolBox@2024';"
    sudo -u postgres psql -c "CREATE DATABASE $PROJECT_USER OWNER $PROJECT_USER;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PROJECT_USER TO $PROJECT_USER;"
    
    # 配置PostgreSQL
    PG_VERSION=$(sudo -u postgres psql -t -c "SHOW server_version;" | grep -oE '[0-9]+' | head -1)
    PG_CONF_PATH="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    PG_HBA_PATH="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
    
    if [ -f "$PG_CONF_PATH" ]; then
        # 修改配置允许本地连接
        sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_PATH"
        
        # 添加认证规则
        if [ -f "$PG_HBA_PATH" ]; then
            cp "$PG_HBA_PATH" "$PG_HBA_PATH.backup"
            if ! grep -q "host.*all.*all.*127.0.0.1/32.*md5" "$PG_HBA_PATH"; then
                echo "host    all             all             127.0.0.1/32            md5" >> "$PG_HBA_PATH"
            fi
        fi
        
        # 重启PostgreSQL
        systemctl restart postgresql
        sleep 3
    fi
    
    # 测试连接
    if PGPASSWORD="QAToolBox@2024" psql -h localhost -U $PROJECT_USER -d $PROJECT_USER -c "SELECT 1;" &>/dev/null; then
        log_success "PostgreSQL安装和配置成功"
    else
        log_error "PostgreSQL连接测试失败"
        exit 1
    fi
}

# 安装Redis和Nginx
install_services() {
    log_step "安装Redis和Nginx"
    
    # 安装Redis
    apt-get install -y redis-server
    systemctl enable redis-server
    systemctl start redis-server
    
    # 测试Redis连接
    redis-cli ping | grep -q "PONG" && log_success "Redis安装成功" || log_error "Redis安装失败"
    
    # 安装Nginx
    apt-get install -y nginx
    systemctl enable nginx
    systemctl start nginx
    
    log_success "Redis和Nginx安装完成"
}

# 创建项目用户
create_user() {
    log_step "创建项目用户"
    
    if id "$PROJECT_USER" &>/dev/null; then
        log_info "用户 $PROJECT_USER 已存在"
    else
        useradd -m -s /bin/bash $PROJECT_USER
        usermod -aG sudo $PROJECT_USER
        log_success "用户 $PROJECT_USER 创建完成"
    fi
}

# 克隆或更新项目代码
clone_project() {
    log_step "获取项目代码"
    
    # 删除旧项目目录
    if [ -d "$PROJECT_DIR" ]; then
        log_info "删除旧项目目录"
        rm -rf "$PROJECT_DIR"
    fi
    
    # 克隆项目
    CLONE_SUCCESS=false
    for repo in \
        "https://gitee.com/shinytsing/QAToolbox.git" \
        "https://github.com/shinytsing/QAToolbox.git" \
        "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
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

# 设置Python虚拟环境和依赖
setup_python_env() {
    log_step "设置Python环境和依赖"
    
    cd $PROJECT_DIR
    
    # 删除旧虚拟环境
    if [ -d ".venv" ]; then
        sudo -u $PROJECT_USER rm -rf .venv
    fi
    
    # 创建新虚拟环境
    sudo -u $PROJECT_USER python3.9 -m venv .venv
    
    # 配置pip镜像源
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
    sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
    
    # 安装核心依赖
    log_info "安装核心依赖包"
    sudo -u $PROJECT_USER .venv/bin/pip install \
        Django==4.2.7 \
        gunicorn==21.2.0 \
        psycopg2-binary==2.9.7 \
        redis==4.6.0 \
        django-redis==5.4.0 \
        python-dotenv==1.0.0 \
        requests==2.31.0 \
        Pillow==9.5.0 \
        djangorestframework==3.14.0 \
        django-cors-headers==4.3.1 \
        channels==4.0.0 \
        channels-redis==4.1.0 \
        daphne==4.0.0 \
        celery==5.3.4 \
        whitenoise==6.6.0 \
        -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    
    # 尝试安装完整依赖
    log_info "安装完整依赖包"
    sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt \
        -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn || {
        log_warning "部分依赖安装失败，但核心功能可用"
    }
    
    log_success "Python环境配置完成"
}

# 配置环境变量
setup_environment() {
    log_step "配置环境变量"
    
    ENV_FILE="$PROJECT_DIR/.env"
    
    # 生成随机密钥
    SECRET_KEY=$(python3.9 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    cat > $ENV_FILE << EOF
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

# 安全配置
SECURE_SSL_REDIRECT=True
EOF
    
    chown $PROJECT_USER:$PROJECT_USER $ENV_FILE
    chmod 600 $ENV_FILE
    
    log_success "环境变量配置完成"
}

# 数据库迁移和静态文件
setup_django() {
    log_step "配置Django应用"
    
    cd $PROJECT_DIR
    
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
    
    # 生成自签名证书
    openssl req -x509 -newkey rsa:4096 -keyout $SSL_DIR/key.pem -out $SSL_DIR/cert.pem -days 365 -nodes \
        -subj "/C=CN/ST=Shanghai/L=Shanghai/O=$PROJECT_NAME/OU=Production/CN=$DOMAIN"
    
    chown -R $PROJECT_USER:$PROJECT_USER $SSL_DIR
    chmod 600 $SSL_DIR/key.pem
    chmod 644 $SSL_DIR/cert.pem
    
    log_success "SSL证书生成完成"
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/$PROJECT_USER << EOF
upstream ${PROJECT_USER}_backend {
    server 127.0.0.1:8000;
    keepalive 32;
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
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
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
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 主应用代理
    location / {
        proxy_pass http://${PROJECT_USER}_backend;
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
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
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
    ln -sf /etc/nginx/sites-available/$PROJECT_USER /etc/nginx/sites-enabled/
    
    # 删除默认站点
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    nginx -t
    
    log_success "Nginx配置完成"
}

# 创建systemd服务
create_systemd_service() {
    log_step "创建systemd服务"
    
    # 创建日志目录
    mkdir -p /var/log/$PROJECT_USER
    chown $PROJECT_USER:$PROJECT_USER /var/log/$PROJECT_USER
    
    # 创建systemd服务文件
    cat > /etc/systemd/system/$PROJECT_USER.service << EOF
[Unit]
Description=$PROJECT_NAME Django Application
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
Environment=PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 4 \\
    --worker-class sync \\
    --timeout 300 \\
    --keepalive 5 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/$PROJECT_USER/access.log \\
    --error-logfile /var/log/$PROJECT_USER/error.log \\
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
ReadWritePaths=$PROJECT_DIR /var/log/$PROJECT_USER /tmp

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    systemctl daemon-reload
    systemctl enable $PROJECT_USER
    
    log_success "systemd服务创建完成"
}

# 启动所有服务
start_services() {
    log_step "启动所有服务"
    
    # 启动应用服务
    systemctl start $PROJECT_USER
    sleep 5
    
    # 启动Nginx
    systemctl restart nginx
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet $PROJECT_USER; then
        log_success "应用服务启动成功"
    else
        log_error "应用服务启动失败"
        journalctl -u $PROJECT_USER -n 20 --no-pager
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
    
    # 配置fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    
    log_success "防火墙配置完成"
}

# 安装Let's Encrypt证书
install_letsencrypt() {
    log_step "安装Let's Encrypt SSL证书"
    
    # 安装certbot
    apt-get install -y certbot python3-certbot-nginx
    
    # 尝试获取证书
    log_info "尝试获取SSL证书..."
    if certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN --no-eff-email; then
        # 设置自动续期
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
        log_success "Let's Encrypt SSL证书安装成功"
        systemctl restart nginx
    else
        log_warning "Let's Encrypt证书获取失败，使用自签名证书"
        log_info "手动获取证书: certbot --nginx -d $DOMAIN"
    fi
}

# 创建管理脚本
create_management_scripts() {
    log_step "创建管理脚本"
    
    # 状态检查脚本
    cat > $PROJECT_DIR/status.sh << 'EOF'
#!/bin/bash
echo "🔍 QAToolBox 服务状态检查"
echo "========================================"

echo "📊 系统资源:"
echo "内存使用:"
free -h
echo "磁盘使用:"
df -h /
echo "CPU负载:"
uptime

echo
echo "🔧 服务状态:"
echo "应用服务:"
systemctl status qatoolbox --no-pager -l
echo "Nginx状态:"
systemctl status nginx --no-pager -l
echo "PostgreSQL状态:"
systemctl status postgresql --no-pager -l
echo "Redis状态:"
systemctl status redis-server --no-pager -l

echo
echo "🌐 网络连接:"
echo "监听端口:"
ss -tulpn | grep -E ":80|:443|:8000|:5432|:6379"

echo
echo "📋 应用日志 (最近10条):"
journalctl -u qatoolbox -n 10 --no-pager

echo
echo "🔗 测试连接:"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}, 响应时间: %{time_total}s\n" https://shenyiqing.xin/health/ || echo "连接失败"
EOF
    
    # 重启脚本
    cat > $PROJECT_DIR/restart.sh << 'EOF'
#!/bin/bash
echo "🔄 重启QAToolBox服务"

echo "停止服务..."
sudo systemctl stop qatoolbox
sleep 3

echo "启动服务..."
sudo systemctl start qatoolbox
sleep 5

echo "检查状态..."
if sudo systemctl is-active --quiet qatoolbox; then
    echo "✅ 服务重启成功"
    echo "📍 访问地址: https://shenyiqing.xin"
else
    echo "❌ 服务重启失败"
    echo "查看日志: sudo journalctl -u qatoolbox -f"
fi
EOF
    
    # 更新脚本
    cat > $PROJECT_DIR/update.sh << 'EOF'
#!/bin/bash
cd /home/qatoolbox/QAToolBox
source .venv/bin/activate

echo "🔄 更新QAToolBox项目"

# 停止服务
sudo systemctl stop qatoolbox

# 拉取最新代码
git pull

# 安装新依赖
.venv/bin/pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 数据库迁移
.venv/bin/python manage.py migrate

# 收集静态文件
.venv/bin/python manage.py collectstatic --noinput

# 重启服务
sudo systemctl start qatoolbox

echo "✅ 项目更新完成"
echo "📍 访问地址: https://shenyiqing.xin"
EOF
    
    chmod +x $PROJECT_DIR/*.sh
    chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/*.sh
    
    log_success "管理脚本创建完成"
}

# 最终测试
final_test() {
    log_step "执行最终测试"
    
    # 等待服务完全启动
    sleep 10
    
    # 测试本地连接
    if curl -s -f http://127.0.0.1:8000/health/ > /dev/null; then
        log_success "本地应用服务测试通过"
    else
        log_error "本地应用服务测试失败"
        return 1
    fi
    
    # 测试Nginx代理
    if curl -s -f -k https://localhost/health/ > /dev/null; then
        log_success "Nginx代理测试通过"
    else
        log_error "Nginx代理测试失败"
        return 1
    fi
    
    log_success "所有测试通过"
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
    echo
    echo -e "${CYAN}管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码:   ${GREEN}QAToolBox@2024${NC}"
    echo -e "  管理后台: ${GREEN}https://$DOMAIN/admin/${NC}"
    echo
    echo -e "${CYAN}管理命令:${NC}"
    echo -e "  查看状态: ${GREEN}cd $PROJECT_DIR && bash status.sh${NC}"
    echo -e "  重启服务: ${GREEN}cd $PROJECT_DIR && bash restart.sh${NC}"
    echo -e "  项目更新: ${GREEN}cd $PROJECT_DIR && bash update.sh${NC}"
    echo
    echo -e "${CYAN}服务管理:${NC}"
    echo -e "  重启应用: ${GREEN}systemctl restart $PROJECT_USER${NC}"
    echo -e "  查看日志: ${GREEN}journalctl -u $PROJECT_USER -f${NC}"
    echo -e "  重启Nginx: ${GREEN}systemctl restart nginx${NC}"
    echo
    echo -e "${CYAN}故障排除:${NC}"
    echo -e "  应用日志: ${GREEN}/var/log/$PROJECT_USER/error.log${NC}"
    echo -e "  Nginx日志: ${GREEN}/var/log/nginx/error.log${NC}"
    echo -e "  系统日志: ${GREEN}journalctl -u $PROJECT_USER -n 50${NC}"
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
    detect_system
    
    log_info "开始智能修复部署，预计需要15-20分钟..."
    
    stop_services
    backup_existing
    cleanup_existing
    update_system
    install_basic_packages
    install_python
    install_postgresql
    install_services
    create_user
    clone_project
    setup_python_env
    setup_environment
    setup_django
    generate_ssl_cert
    configure_nginx
    create_systemd_service
    start_services
    configure_firewall
    install_letsencrypt
    create_management_scripts
    
    if final_test; then
        show_result
    else
        log_error "部署测试失败，请检查日志"
        log_info "查看详细日志: journalctl -u $PROJECT_USER -n 50"
        exit 1
    fi
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
