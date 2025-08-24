#!/bin/bash

# =============================================================================
# QAToolBox 生产环境一键智能部署脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# 自动化部署、配置域名、SSL证书、优化配置
# =============================================================================

set -e  # 遇到错误立即退出

# 服务器配置
SERVER_IP="47.103.143.152"
DOMAIN="shenyiqing.xin"
PROJECT_NAME="QAToolBox"
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/$PROJECT_NAME"

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
    echo "    🚀 QAToolBox 生产环境部署"
    echo "========================================"
    echo "  服务器: $SERVER_IP"
    echo "  域名:   $DOMAIN"
    echo "  目标:   https://$DOMAIN"
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

# 修复CentOS 8 EOL问题
fix_centos8_repos() {
    if [[ $VER == "8" ]]; then
        log_step "修复CentOS 8 EOL仓库问题"
        sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
        sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
        yum clean all
        yum makecache
        log_success "CentOS 8 仓库修复完成"
    fi
}

# 安装基础依赖
install_basic_packages() {
    log_step "安装基础依赖包"
    
    # 更新系统
    yum update -y
    
    # 安装基础工具
    yum groupinstall -y "Development Tools"
    yum install -y epel-release
    yum install -y wget curl git vim unzip htop tree
    yum install -y openssl openssl-devel
    yum install -y libffi-devel
    yum install -y zlib-devel bzip2-devel readline-devel sqlite-devel
    yum install -y firewalld
    
    log_success "基础依赖包安装完成"
}

# 安装Python 3.9
install_python() {
    log_step "安装Python 3.9"
    
    if command -v python3.9 &> /dev/null; then
        PYTHON_VERSION=$(python3.9 --version 2>&1 | awk '{print $2}')
        log_info "Python 3.9 已安装: $PYTHON_VERSION"
        return
    fi
    
    if [[ $VER == "7" ]]; then
        yum install -y centos-release-scl
        yum install -y rh-python39 rh-python39-python-devel
        ln -sf /opt/rh/rh-python39/root/usr/bin/python3.9 /usr/local/bin/python3.9
        ln -sf /opt/rh/rh-python39/root/usr/bin/pip3.9 /usr/local/bin/pip3.9
    else
        yum install -y python39 python39-devel python39-pip
        ln -sf /usr/bin/python3.9 /usr/local/bin/python3.9
        ln -sf /usr/bin/pip3.9 /usr/local/bin/pip3.9
    fi
    
    if command -v python3.9 &> /dev/null; then
        PYTHON_VERSION=$(python3.9 --version)
        log_success "Python安装成功: $PYTHON_VERSION"
    else
        log_error "Python安装失败"
        exit 1
    fi
}

# 安装PostgreSQL
install_postgresql() {
    log_step "安装PostgreSQL数据库"
    
    if command -v psql &> /dev/null; then
        log_info "PostgreSQL已安装"
        return
    fi
    
    if [[ $VER == "7" ]]; then
        yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        yum install -y postgresql15-server postgresql15-devel
        /usr/pgsql-15/bin/postgresql-15-setup initdb
    else
        dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        dnf -qy module disable postgresql
        dnf install -y postgresql15-server postgresql15-devel
        /usr/pgsql-15/bin/postgresql-15-setup initdb
    fi
    
    systemctl enable postgresql-15
    systemctl start postgresql-15
    
    echo 'export PATH="/usr/pgsql-15/bin:$PATH"' >> /etc/profile
    source /etc/profile
    
    log_success "PostgreSQL安装完成"
}

# 配置PostgreSQL
configure_postgresql() {
    log_step "配置PostgreSQL数据库"
    
    # 创建数据库用户和数据库
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS $PROJECT_USER;" || true
    sudo -u postgres psql -c "DROP USER IF EXISTS $PROJECT_USER;" || true
    sudo -u postgres psql -c "CREATE USER $PROJECT_USER WITH PASSWORD '$PROJECT_USER@2024';"
    sudo -u postgres psql -c "CREATE DATABASE $PROJECT_USER OWNER $PROJECT_USER;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $PROJECT_USER TO $PROJECT_USER;"
    
    # 配置PostgreSQL
    PG_DATA_DIR="/var/lib/pgsql/15/data"
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" $PG_DATA_DIR/postgresql.conf
    
    # 配置认证
    cp $PG_DATA_DIR/pg_hba.conf $PG_DATA_DIR/pg_hba.conf.backup
    cat > $PG_DATA_DIR/pg_hba.conf << EOF
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    all             all             0.0.0.0/0               md5
EOF
    
    systemctl restart postgresql-15
    log_success "PostgreSQL配置完成"
}

# 安装Redis和Nginx
install_services() {
    log_step "安装Redis和Nginx"
    
    # 安装Redis
    yum install -y redis
    systemctl enable redis
    systemctl start redis
    
    # 安装Nginx
    yum install -y nginx
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
        log_success "用户 $PROJECT_USER 创建完成"
    fi
}

# 克隆项目代码
clone_project() {
    log_step "克隆项目代码"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，更新代码"
        cd $PROJECT_DIR
        sudo -u $PROJECT_USER git pull
    else
        log_info "克隆项目代码"
        sudo -u $PROJECT_USER git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR
    fi
    
    cd $PROJECT_DIR
    sudo -u $PROJECT_USER chmod +x *.sh *.py 2>/dev/null || true
    
    log_success "项目代码准备完成"
}

# 创建Python虚拟环境
setup_virtualenv() {
    log_step "创建Python虚拟环境"
    
    cd $PROJECT_DIR
    
    if [ -d ".venv" ]; then
        log_info "虚拟环境已存在"
    else
        sudo -u $PROJECT_USER python3.9 -m venv .venv
        log_success "虚拟环境创建完成"
    fi
    
    # 安装依赖
    log_info "安装Python依赖包"
    sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
    sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
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
DB_PASSWORD=$PROJECT_USER@2024
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
    
    chown $PROJECT_USER:$PROJECT_USER $ENV_FILE
    chmod 600 $ENV_FILE
    
    log_success "环境变量配置完成"
}

# 数据库迁移
migrate_database() {
    log_step "执行数据库迁移"
    
    cd $PROJECT_DIR
    
    # 数据库迁移
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
    
    # 收集静态文件
    sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput
    
    # 创建超级用户
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@$DOMAIN', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell
    
    log_success "数据库迁移完成"
}

# 生成SSL证书
generate_ssl_cert() {
    log_step "生成临时SSL证书"
    
    SSL_DIR="$PROJECT_DIR/ssl"
    
    if [ ! -d "$SSL_DIR" ]; then
        mkdir -p $SSL_DIR
    fi
    
    # 生成临时自签名证书
    openssl req -x509 -newkey rsa:4096 -keyout $SSL_DIR/key.pem -out $SSL_DIR/cert.pem -days 365 -nodes -subj "/C=CN/ST=Shanghai/L=Shanghai/O=$PROJECT_NAME/OU=Production/CN=$DOMAIN"
    
    chown -R $PROJECT_USER:$PROJECT_USER $SSL_DIR
    chmod 600 $SSL_DIR/key.pem
    chmod 644 $SSL_DIR/cert.pem
    
    log_success "临时SSL证书生成完成"
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx"
    
    # 备份默认配置
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup
    
    # 创建项目配置
    cat > /etc/nginx/conf.d/$PROJECT_USER.conf << EOF
upstream ${PROJECT_USER}_backend {
    server 127.0.0.1:8000;
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
    
    client_max_body_size 100M;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    location / {
        proxy_pass http://${PROJECT_USER}_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public, no-transform";
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
    
    # 测试Nginx配置
    nginx -t
    systemctl restart nginx
    
    log_success "Nginx配置完成"
}

# 创建systemd服务
create_systemd_service() {
    log_step "创建systemd服务"
    
    cat > /etc/systemd/system/$PROJECT_USER.service << EOF
[Unit]
Description=$PROJECT_NAME Django Application
After=network.target postgresql-15.service redis.service

[Service]
Type=exec
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile /var/log/$PROJECT_USER/access.log --error-logfile /var/log/$PROJECT_USER/error.log config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建日志目录
    mkdir -p /var/log/$PROJECT_USER
    chown $PROJECT_USER:$PROJECT_USER /var/log/$PROJECT_USER
    
    # 启用并启动服务
    systemctl daemon-reload
    systemctl enable $PROJECT_USER
    systemctl start $PROJECT_USER
    
    log_success "systemd服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙"
    
    systemctl enable firewalld
    systemctl start firewalld
    
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --reload
    
    log_success "防火墙配置完成"
}

# 安装Let's Encrypt SSL证书
install_letsencrypt() {
    log_step "安装Let's Encrypt SSL证书"
    
    # 安装certbot
    yum install -y certbot python3-certbot-nginx
    
    # 获取SSL证书
    log_info "正在获取SSL证书，请确保域名 $DOMAIN 已正确解析到 $SERVER_IP"
    
    if certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN; then
        # 设置自动续期
        echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
        log_success "Let's Encrypt SSL证书安装成功"
        
        # 重启nginx使用新证书
        systemctl restart nginx
    else
        log_warning "Let's Encrypt证书获取失败，继续使用自签名证书"
        log_info "请确保域名解析正确后，手动运行: certbot --nginx -d $DOMAIN"
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
free -h
df -h /

echo
echo "🔧 服务状态:"
systemctl status qatoolbox --no-pager -l
systemctl status nginx --no-pager -l
systemctl status postgresql-15 --no-pager -l
systemctl status redis --no-pager -l

echo
echo "🌐 网络连接:"
netstat -tulpn | grep -E ":80|:443|:8000"

echo
echo "📋 最近日志:"
journalctl -u qatoolbox -n 10 --no-pager
EOF
    
    # 更新脚本
    cat > $PROJECT_DIR/update.sh << 'EOF'
#!/bin/bash
cd /home/qatoolbox/QAToolBox
source .venv/bin/activate

echo "🔄 更新QAToolBox项目"

# 拉取最新代码
git pull

# 安装新依赖
.venv/bin/pip install -r requirements.txt

# 数据库迁移
.venv/bin/python manage.py migrate

# 收集静态文件
.venv/bin/python manage.py collectstatic --noinput

# 重启服务
sudo systemctl restart qatoolbox

echo "✅ 项目更新完成"
echo "📍 访问地址: https://shenyiqing.xin"
EOF
    
    # 备份脚本
    cat > $PROJECT_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/qatoolbox/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

echo "📦 开始备份..."

# 备份数据库
sudo -u postgres pg_dump qatoolbox > $BACKUP_DIR/database_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media_$DATE.tar.gz -C /home/qatoolbox/QAToolBox media/

# 备份配置文件
cp /home/qatoolbox/QAToolBox/.env $BACKUP_DIR/env_$DATE.backup

# 清理旧备份（保留7天）
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete

echo "✅ 备份完成: $BACKUP_DIR"
EOF
    
    chmod +x $PROJECT_DIR/*.sh
    chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/*.sh
    
    # 设置定时备份
    echo "0 2 * * * /home/$PROJECT_USER/$PROJECT_NAME/backup.sh" | crontab -u $PROJECT_USER -
    
    log_success "管理脚本创建完成"
}

# 性能优化
optimize_performance() {
    log_step "性能优化配置"
    
    # PostgreSQL优化
    PG_CONF="/var/lib/pgsql/15/data/postgresql.conf"
    cp $PG_CONF $PG_CONF.backup
    
    # 根据服务器内存调整PostgreSQL配置
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    SHARED_BUFFERS=$((TOTAL_MEM / 4))
    EFFECTIVE_CACHE=$((TOTAL_MEM * 3 / 4))
    
    cat >> $PG_CONF << EOF

# Performance tuning
shared_buffers = ${SHARED_BUFFERS}MB
effective_cache_size = ${EFFECTIVE_CACHE}MB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
EOF
    
    # Nginx优化
    sed -i 's/worker_processes auto;/worker_processes auto;\nworker_rlimit_nofile 65535;/' /etc/nginx/nginx.conf
    sed -i 's/worker_connections 1024;/worker_connections 4096;\n    use epoll;\n    multi_accept on;/' /etc/nginx/nginx.conf
    
    # 系统优化
    cat >> /etc/sysctl.conf << EOF

# Network performance tuning
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
EOF
    
    sysctl -p
    
    # 重启服务应用配置
    systemctl restart postgresql-15
    systemctl restart nginx
    
    log_success "性能优化完成"
}

# 主安装函数
main() {
    show_welcome
    
    check_root
    detect_system
    
    log_info "开始部署，预计需要10-15分钟..."
    
    fix_centos8_repos
    install_basic_packages
    install_python
    install_postgresql
    configure_postgresql
    install_services
    create_user
    clone_project
    setup_virtualenv
    setup_environment
    migrate_database
    generate_ssl_cert
    configure_nginx
    create_systemd_service
    configure_firewall
    install_letsencrypt
    create_management_scripts
    optimize_performance
    
    # 最终状态检查
    log_step "最终状态检查"
    sleep 5
    
    if systemctl is-active --quiet $PROJECT_USER && systemctl is-active --quiet nginx; then
        log_success "所有服务运行正常"
    else
        log_warning "部分服务可能有问题，请检查日志"
    fi
    
    # 显示部署结果
    echo
    echo -e "${GREEN}"
    echo "========================================"
    echo "        🎉 部署完成！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${CYAN}访问地址:${NC}"
    echo -e "  主站: ${GREEN}https://$DOMAIN${NC}"
    echo -e "  备用: ${GREEN}https://$SERVER_IP${NC}"
    echo
    echo -e "${CYAN}管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码:   ${GREEN}QAToolBox@2024${NC}"
    echo
    echo -e "${CYAN}管理命令:${NC}"
    echo -e "  查看状态: ${GREEN}cd $PROJECT_DIR && bash status.sh${NC}"
    echo -e "  项目更新: ${GREEN}cd $PROJECT_DIR && bash update.sh${NC}"
    echo -e "  数据备份: ${GREEN}cd $PROJECT_DIR && bash backup.sh${NC}"
    echo
    echo -e "${CYAN}服务管理:${NC}"
    echo -e "  重启应用: ${GREEN}systemctl restart $PROJECT_USER${NC}"
    echo -e "  查看日志: ${GREEN}journalctl -u $PROJECT_USER -f${NC}"
    echo -e "  重启Nginx: ${GREEN}systemctl restart nginx${NC}"
    echo
    echo -e "${YELLOW}⚠️  重要提醒:${NC}"
    echo -e "  1. 请记住管理员密码，首次登录后建议修改"
    echo -e "  2. SSL证书会自动续期，无需手动操作"
    echo -e "  3. 系统已配置自动备份，备份文件在 /home/$PROJECT_USER/backups/"
    echo -e "  4. 如需修改配置，编辑 $PROJECT_DIR/.env 后重启服务"
    echo
    echo -e "${GREEN}🚀 现在可以访问 https://$DOMAIN 开始使用！${NC}"
    echo
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
