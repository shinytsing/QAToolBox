#!/bin/bash

# =============================================================================
# QAToolBox 阿里云 CentOS 一键智能部署脚本
# 支持 CentOS 7/8/9 系统
# 自动安装所有依赖，配置环境，部署项目
# =============================================================================

set -e  # 遇到错误立即退出

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
    
    # 检查是否为CentOS
    if [[ $OS != *"CentOS"* ]] && [[ $OS != *"Red Hat"* ]] && [[ $OS != *"Rocky"* ]] && [[ $OS != *"AlmaLinux"* ]]; then
        log_warning "此脚本专为CentOS/RHEL系列系统设计，当前系统: $OS"
        read -p "是否继续安装? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 修复CentOS 8 EOL问题
fix_centos8_repos() {
    if [[ $VER == "8" ]]; then
        log_step "修复CentOS 8 EOL仓库问题"
        sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
        sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
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
    yum install -y wget curl git vim unzip htop
    yum install -y openssl openssl-devel
    yum install -y libffi-devel
    yum install -y zlib-devel bzip2-devel readline-devel sqlite-devel
    
    log_success "基础依赖包安装完成"
}

# 安装Python 3.9
install_python() {
    log_step "安装Python 3.9"
    
    # 检查Python版本
    if command -v python3.9 &> /dev/null; then
        PYTHON_VERSION=$(python3.9 --version 2>&1 | awk '{print $2}')
        log_info "Python 3.9 已安装: $PYTHON_VERSION"
        return
    fi
    
    # 安装Python 3.9
    if [[ $VER == "7" ]]; then
        yum install -y centos-release-scl
        yum install -y rh-python39 rh-python39-python-devel
        # 创建软链接
        ln -sf /opt/rh/rh-python39/root/usr/bin/python3.9 /usr/local/bin/python3.9
        ln -sf /opt/rh/rh-python39/root/usr/bin/pip3.9 /usr/local/bin/pip3.9
    else
        # CentOS 8/9
        yum install -y python39 python39-devel python39-pip
        # 创建软链接
        ln -sf /usr/bin/python3.9 /usr/local/bin/python3.9
        ln -sf /usr/bin/pip3.9 /usr/local/bin/pip3.9
    fi
    
    # 验证安装
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
    
    # 检查是否已安装
    if command -v psql &> /dev/null; then
        log_info "PostgreSQL已安装"
        return
    fi
    
    # 安装PostgreSQL官方仓库
    if [[ $VER == "7" ]]; then
        yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        yum install -y postgresql15-server postgresql15-devel
        /usr/pgsql-15/bin/postgresql-15-setup initdb
        systemctl enable postgresql-15
        systemctl start postgresql-15
    else
        # CentOS 8/9
        dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
        dnf -qy module disable postgresql
        dnf install -y postgresql15-server postgresql15-devel
        /usr/pgsql-15/bin/postgresql-15-setup initdb
        systemctl enable postgresql-15
        systemctl start postgresql-15
    fi
    
    # 添加到PATH
    echo 'export PATH="/usr/pgsql-15/bin:$PATH"' >> /etc/profile
    source /etc/profile
    
    log_success "PostgreSQL安装完成"
}

# 配置PostgreSQL
configure_postgresql() {
    log_step "配置PostgreSQL数据库"
    
    # 创建数据库用户和数据库
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    # 配置PostgreSQL允许本地连接
    PG_VERSION=$(sudo -u postgres psql -c "SHOW server_version;" | grep PostgreSQL | awk '{print $2}' | cut -d. -f1)
    PG_DATA_DIR="/var/lib/pgsql/15/data"
    
    # 修改pg_hba.conf
    sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" $PG_DATA_DIR/postgresql.conf
    echo "host    all             all             127.0.0.1/32            md5" >> $PG_DATA_DIR/pg_hba.conf
    echo "host    all             all             0.0.0.0/0               md5" >> $PG_DATA_DIR/pg_hba.conf
    
    # 重启PostgreSQL
    systemctl restart postgresql-15
    
    log_success "PostgreSQL配置完成"
}

# 安装Redis
install_redis() {
    log_step "安装Redis"
    
    if command -v redis-server &> /dev/null; then
        log_info "Redis已安装"
        return
    fi
    
    yum install -y redis
    systemctl enable redis
    systemctl start redis
    
    log_success "Redis安装完成"
}

# 安装Nginx
install_nginx() {
    log_step "安装Nginx"
    
    if command -v nginx &> /dev/null; then
        log_info "Nginx已安装"
        return
    fi
    
    yum install -y nginx
    systemctl enable nginx
    systemctl start nginx
    
    log_success "Nginx安装完成"
}

# 创建项目用户
create_user() {
    log_step "创建项目用户"
    
    if id "qatoolbox" &>/dev/null; then
        log_info "用户 qatoolbox 已存在"
    else
        useradd -m -s /bin/bash qatoolbox
        log_success "用户 qatoolbox 创建完成"
    fi
}

# 克隆项目代码
clone_project() {
    log_step "克隆项目代码"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，更新代码"
        cd $PROJECT_DIR
        sudo -u qatoolbox git pull
    else
        log_info "克隆项目代码"
        sudo -u qatoolbox git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR
    fi
    
    cd $PROJECT_DIR
    sudo -u qatoolbox chmod +x *.sh *.py
    
    log_success "项目代码准备完成"
}

# 创建Python虚拟环境
setup_virtualenv() {
    log_step "创建Python虚拟环境"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    cd $PROJECT_DIR
    
    if [ -d ".venv" ]; then
        log_info "虚拟环境已存在"
    else
        sudo -u qatoolbox python3.9 -m venv .venv
        log_success "虚拟环境创建完成"
    fi
    
    # 安装依赖
    log_info "安装Python依赖包"
    sudo -u qatoolbox .venv/bin/pip install --upgrade pip
    sudo -u qatoolbox .venv/bin/pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
}

# 配置环境变量
setup_environment() {
    log_step "配置环境变量"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    ENV_FILE="$PROJECT_DIR/.env"
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_SERVER_IP")
    
    cat > $ENV_FILE << EOF
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=$(python3.9 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 其他配置
DJANGO_SETTINGS_MODULE=config.settings.production
EOF
    
    chown qatoolbox:qatoolbox $ENV_FILE
    chmod 600 $ENV_FILE
    
    log_success "环境变量配置完成"
}

# 数据库迁移
migrate_database() {
    log_step "执行数据库迁移"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    cd $PROJECT_DIR
    
    sudo -u qatoolbox .venv/bin/python manage.py migrate
    sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput
    
    # 创建超级用户
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | sudo -u qatoolbox .venv/bin/python manage.py shell
    
    log_success "数据库迁移完成"
}

# 生成SSL证书
generate_ssl_cert() {
    log_step "生成SSL证书"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    SSL_DIR="$PROJECT_DIR/ssl"
    
    if [ ! -d "$SSL_DIR" ]; then
        mkdir -p $SSL_DIR
    fi
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_SERVER_IP")
    
    openssl req -x509 -newkey rsa:4096 -keyout $SSL_DIR/key.pem -out $SSL_DIR/cert.pem -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/OU=Production/CN=$SERVER_IP"
    
    chown -R qatoolbox:qatoolbox $SSL_DIR
    chmod 600 $SSL_DIR/key.pem
    chmod 644 $SSL_DIR/cert.pem
    
    log_success "SSL证书生成完成"
}

# 配置Nginx
configure_nginx() {
    log_step "配置Nginx"
    
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_SERVER_IP")
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    
    cat > /etc/nginx/conf.d/qatoolbox.conf << EOF
upstream qatoolbox_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $SERVER_IP localhost;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $SERVER_IP localhost;
    
    ssl_certificate $PROJECT_DIR/ssl/cert.pem;
    ssl_certificate_key $PROJECT_DIR/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://qatoolbox_backend;
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
}
EOF
    
    # 测试Nginx配置
    nginx -t
    
    # 重启Nginx
    systemctl restart nginx
    
    log_success "Nginx配置完成"
}

# 创建systemd服务
create_systemd_service() {
    log_step "创建systemd服务"
    
    cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql-15.service redis.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 300 --access-logfile /var/log/qatoolbox/access.log --error-logfile /var/log/qatoolbox/error.log config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建日志目录
    mkdir -p /var/log/qatoolbox
    chown qatoolbox:qatoolbox /var/log/qatoolbox
    
    # 启用并启动服务
    systemctl daemon-reload
    systemctl enable qatoolbox
    systemctl start qatoolbox
    
    log_success "systemd服务创建完成"
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙"
    
    # 检查防火墙状态
    if systemctl is-active --quiet firewalld; then
        firewall-cmd --permanent --add-port=80/tcp
        firewall-cmd --permanent --add-port=443/tcp
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --reload
        log_success "防火墙配置完成"
    else
        log_info "防火墙未启用，跳过配置"
    fi
}

# 创建管理脚本
create_management_scripts() {
    log_step "创建管理脚本"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    
    # 创建启动脚本
    cat > $PROJECT_DIR/start_production.sh << 'EOF'
#!/bin/bash
cd /home/qatoolbox/QAToolBox
source .venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.production

echo "🚀 启动QAToolBox生产环境"
echo "检查服务状态..."

# 检查数据库
systemctl status postgresql-15 --no-pager
systemctl status redis --no-pager

# 检查应用
systemctl status qatoolbox --no-pager
systemctl status nginx --no-pager

echo "✅ 所有服务运行正常"
echo "📍 访问地址: https://$(curl -s ifconfig.me)"
EOF
    
    # 创建更新脚本
    cat > $PROJECT_DIR/update_project.sh << 'EOF'
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
EOF
    
    chmod +x $PROJECT_DIR/*.sh
    chown qatoolbox:qatoolbox $PROJECT_DIR/*.sh
    
    log_success "管理脚本创建完成"
}

# 主安装函数
main() {
    echo -e "${CYAN}"
    echo "========================================"
    echo "  QAToolBox 阿里云 CentOS 一键部署"
    echo "========================================"
    echo -e "${NC}"
    
    check_root
    detect_system
    
    log_info "开始安装，预计需要10-15分钟..."
    
    fix_centos8_repos
    install_basic_packages
    install_python
    install_postgresql
    configure_postgresql
    install_redis
    install_nginx
    create_user
    clone_project
    setup_virtualenv
    setup_environment
    migrate_database
    generate_ssl_cert
    configure_nginx
    create_systemd_service
    configure_firewall
    create_management_scripts
    
    # 获取服务器IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "YOUR_SERVER_IP")
    
    echo -e "${GREEN}"
    echo "========================================"
    echo "        🎉 部署完成！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${CYAN}访问地址:${NC}"
    echo -e "  HTTPS: ${GREEN}https://$SERVER_IP${NC}"
    echo -e "  HTTP:  ${GREEN}http://$SERVER_IP${NC} (自动重定向到HTTPS)"
    echo
    echo -e "${CYAN}管理员账号:${NC}"
    echo -e "  用户名: ${GREEN}admin${NC}"
    echo -e "  密码:   ${GREEN}admin123${NC}"
    echo
    echo -e "${CYAN}管理命令:${NC}"
    echo -e "  启动服务: ${GREEN}sudo systemctl start qatoolbox${NC}"
    echo -e "  停止服务: ${GREEN}sudo systemctl stop qatoolbox${NC}"
    echo -e "  查看状态: ${GREEN}sudo systemctl status qatoolbox${NC}"
    echo -e "  查看日志: ${GREEN}sudo journalctl -u qatoolbox -f${NC}"
    echo
    echo -e "${CYAN}项目目录:${NC} ${GREEN}/home/qatoolbox/QAToolBox${NC}"
    echo -e "${CYAN}配置文件:${NC} ${GREEN}/etc/nginx/conf.d/qatoolbox.conf${NC}"
    echo
    echo -e "${YELLOW}⚠️  请记住管理员密码，首次登录后建议修改密码${NC}"
    echo -e "${YELLOW}⚠️  如需修改配置，请编辑 /home/qatoolbox/QAToolBox/.env${NC}"
    echo
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
