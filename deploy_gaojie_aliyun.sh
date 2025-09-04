#!/bin/bash
# =============================================================================
# QAToolBox 高杰阿里云服务器部署脚本
# 服务器信息: 华东2(上海) 47.103.143.152
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# 服务器配置
readonly SERVER_IP="47.103.143.152"
readonly DOMAIN="shenyiqing.xin"
readonly PROJECT_USER="qatoolbox"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly DB_PASSWORD="QAToolBox@2024@$(date +%s)"
readonly ADMIN_PASSWORD="admin123456"

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox 阿里云部署脚本
========================================
服务器: 华东2(上海) 47.103.143.152
域名: shenyiqing.xin
========================================
EOF
echo -e "${NC}"

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
        echo -e "${YELLOW}💡 使用命令: sudo $0${NC}"
        exit 1
    fi
}

# 显示进度
show_progress() {
    local step=$1
    local total=$2
    local desc=$3
    local percent=$((step * 100 / total))
    echo -e "${CYAN}${BOLD}[${step}/${total}] (${percent}%) ${desc}${NC}"
}

# 配置中国镜像源
setup_china_mirrors() {
    show_progress "1" "10" "配置中国镜像源"
    
    # 备份原始sources.list
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s)
    
    # 检测Ubuntu版本
    local ubuntu_codename=$(lsb_release -cs)
    
    cat > /etc/apt/sources.list << EOF
# 阿里云Ubuntu镜像源
deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse
EOF

    # 配置pip中国镜像源
    mkdir -p /etc/pip
    cat > /etc/pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
EOF

    echo -e "${GREEN}✅ 中国镜像源配置完成${NC}"
}

# 更新系统
update_system() {
    show_progress "2" "10" "更新系统"
    
    apt update
    apt upgrade -y
    apt install -y curl wget git unzip vim nano htop tree jq
    apt install -y software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    
    echo -e "${GREEN}✅ 系统更新完成${NC}"
}

# 安装Python和基础依赖
install_python_dependencies() {
    show_progress "3" "10" "安装Python和基础依赖"
    
    # 安装Python 3.12
    apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
    apt install -y build-essential gcc g++ make cmake pkg-config
    
    # 安装数据库
    apt install -y postgresql postgresql-contrib postgresql-client
    apt install -y redis-server redis-tools
    
    # 安装Web服务器
    apt install -y nginx supervisor
    
    # 安装图像处理依赖
    apt install -y libjpeg-dev libpng-dev libfreetype6-dev liblcms2-dev
    apt install -y libtiff5-dev libwebp-dev zlib1g-dev
    
    # 安装OCR依赖
    apt install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
    
    echo -e "${GREEN}✅ Python和基础依赖安装完成${NC}"
}

# 配置数据库
setup_database() {
    show_progress "4" "10" "配置PostgreSQL数据库"
    
    # 启动PostgreSQL
    systemctl start postgresql
    systemctl enable postgresql
    
    # 创建数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;"
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;"
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    # 配置Redis
    systemctl start redis-server
    systemctl enable redis-server
    
    echo -e "${GREEN}✅ 数据库配置完成${NC}"
}

# 创建项目用户和目录
setup_project_user() {
    show_progress "5" "10" "创建项目用户和目录"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER"
    fi
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    mkdir -p /var/log/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/log/qatoolbox
    
    echo -e "${GREEN}✅ 项目用户和目录创建完成${NC}"
}

# 部署项目代码
deploy_project() {
    show_progress "6" "10" "部署项目代码"
    
    # 如果项目目录不存在，创建它
    if [ ! -d "$PROJECT_DIR" ]; then
        mkdir -p "$PROJECT_DIR"
        chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    fi
    
    # 这里需要您手动上传项目代码到服务器
    echo -e "${YELLOW}📁 请将项目代码上传到: $PROJECT_DIR${NC}"
    echo -e "${YELLOW}💡 您可以使用以下命令上传代码:${NC}"
    echo -e "   scp -r /Users/gaojie/Desktop/PycharmProjects/QAToolBox/* root@$SERVER_IP:$PROJECT_DIR/"
    
    # 等待用户确认代码已上传
    read -p "代码上传完成后，按Enter继续..."
    
    # 设置权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    chmod -R 755 "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 项目代码部署完成${NC}"
}

# 创建Python虚拟环境
setup_python_environment() {
    show_progress "7" "10" "创建Python虚拟环境"
    
    cd "$PROJECT_DIR"
    
    # 创建虚拟环境
    sudo -u "$PROJECT_USER" python3.12 -m venv .venv
    
    # 升级pip
    sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade pip setuptools wheel
    
    # 安装核心依赖
    sudo -u "$PROJECT_USER" .venv/bin/pip install Django==4.2.7
    sudo -u "$PROJECT_USER" .venv/bin/pip install djangorestframework django-cors-headers
    sudo -u "$PROJECT_USER" .venv/bin/pip install django-crispy-forms crispy-bootstrap5
    sudo -u "$PROJECT_USER" .venv/bin/pip install django-simple-captcha django-extensions
    sudo -u "$PROJECT_USER" .venv/bin/pip install psycopg2-binary redis django-redis
    sudo -u "$PROJECT_USER" .venv/bin/pip install channels channels-redis daphne
    sudo -u "$PROJECT_USER" .venv/bin/pip install celery django-celery-beat
    sudo -u "$PROJECT_USER" .venv/bin/pip install gunicorn whitenoise
    sudo -u "$PROJECT_USER" .venv/bin/pip install django-environ python-dotenv
    sudo -u "$PROJECT_USER" .venv/bin/pip install Pillow requests beautifulsoup4
    
    echo -e "${GREEN}✅ Python虚拟环境创建完成${NC}"
}

# 配置Django应用
configure_django() {
    show_progress "8" "10" "配置Django应用"
    
    cd "$PROJECT_DIR"
    
    # 创建环境变量文件
    cat > .env << EOF
# Django配置
DJANGO_SECRET_KEY=django-aliyun-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=settings

# 主机配置
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 生产环境配置
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
EOF

    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    # 执行数据库迁移
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py makemigrations --noinput
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py migrate --noinput
    
    # 收集静态文件
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py collectstatic --noinput
    
    # 创建管理员用户
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py shell << PYTHON_EOF
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(username='admin').delete()
User.objects.create_superuser('admin', 'admin@$DOMAIN', '$ADMIN_PASSWORD')
print('管理员用户创建成功')
PYTHON_EOF
    
    echo -e "${GREEN}✅ Django应用配置完成${NC}"
}

# 配置Nginx
setup_nginx() {
    show_progress "9" "10" "配置Nginx"
    
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 1w;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
    show_progress "10" "10" "配置Supervisor"
    
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/gunicorn.log
stderr_logfile=/var/log/qatoolbox/gunicorn_error.log
environment=DJANGO_SETTINGS_MODULE="settings"
EOF

    # 重新加载配置
    supervisorctl reread
    supervisorctl update
    supervisorctl start qatoolbox
    
    echo -e "${GREEN}✅ Supervisor配置完成${NC}"
}

# 最终验证
final_verification() {
    echo -e "${YELLOW}🔍 等待服务启动...${NC}"
    sleep 10
    
    echo -e "${YELLOW}🔍 检查服务状态...${NC}"
    
    # 检查服务
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✅ Nginx 运行正常${NC}"
    else
        echo -e "${RED}❌ Nginx 状态异常${NC}"
    fi
    
    if systemctl is-active --quiet postgresql; then
        echo -e "${GREEN}✅ PostgreSQL 运行正常${NC}"
    else
        echo -e "${RED}❌ PostgreSQL 状态异常${NC}"
    fi
    
    if systemctl is-active --quiet redis-server; then
        echo -e "${GREEN}✅ Redis 运行正常${NC}"
    else
        echo -e "${RED}❌ Redis 状态异常${NC}"
    fi
    
    if supervisorctl status qatoolbox | grep -q RUNNING; then
        echo -e "${GREEN}✅ QAToolBox应用 运行正常${NC}"
    else
        echo -e "${RED}❌ QAToolBox应用 状态异常${NC}"
    fi
    
    # 显示部署信息
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 部署成功！
========================================

🌐 访问信息:
  主站地址: http://$DOMAIN/
  IP访问:   http://$SERVER_IP/
  管理后台: http://$DOMAIN/admin/

👑 管理员账户:
  用户名: admin
  密码:   $ADMIN_PASSWORD
  邮箱:   admin@$DOMAIN

📊 系统信息:
  项目目录: $PROJECT_DIR
  数据库:   PostgreSQL (qatoolbox)
  缓存:     Redis
  Web服务器: Nginx + Gunicorn

🔧 管理命令:
  重启应用: sudo supervisorctl restart qatoolbox
  查看日志: sudo tail -f /var/log/qatoolbox/gunicorn.log
  重启服务: sudo systemctl restart nginx

========================================
EOF
    echo -e "${NC}"
}

# 主执行流程
main() {
    check_root
    
    echo -e "${BLUE}🚀 开始QAToolBox阿里云部署...${NC}"
    echo -e "${BLUE}📋 详细日志: $LOG_FILE${NC}"
    echo ""
    
    setup_china_mirrors
    update_system
    install_python_dependencies
    setup_database
    setup_project_user
    deploy_project
    setup_python_environment
    configure_django
    setup_nginx
    setup_supervisor
    final_verification
    
    echo -e "${GREEN}🎉 QAToolBox阿里云部署成功完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
