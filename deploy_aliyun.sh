#!/bin/bash
# =============================================================================
# QAToolBox 阿里云服务器一键部署脚本 v2.0
# =============================================================================
# 全新Ubuntu服务器一键部署，包含自动重试机制和中国地区优化
# 服务器: 阿里云 Ubuntu 20.04/22.04/24.04
# 域名: https://shenyiqing.xin/
# 管理员: admin / admin123456
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

# 配置变量
readonly SERVER_IP="${SERVER_IP:-47.103.143.152}"
readonly DOMAIN="${DOMAIN:-shenyiqing.xin}"
readonly PROJECT_USER="${PROJECT_USER:-qatoolbox}"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly DB_PASSWORD="${DB_PASSWORD:-QAToolBox@2024@$(date +%s)}"
readonly ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123456}"

# 重试配置
readonly MAX_RETRIES=3
readonly RETRY_DELAY=5

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox 阿里云一键部署 v2.0
========================================
✨ 特性:
  • 全新Ubuntu服务器支持
  • 自动重试机制
  • 中国地区镜像加速
  • 完整Django应用部署
  • 管理员账户自动初始化
  • 生产级配置优化
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

# 重试机制
retry_command() {
    local command="$1"
    local description="$2"
    local max_attempts="${3:-$MAX_RETRIES}"
    local delay="${4:-$RETRY_DELAY}"
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}🔄 尝试 ${attempt}/${max_attempts}: ${description}${NC}"
        
        if eval "$command"; then
            echo -e "${GREEN}✅ 成功: ${description}${NC}"
            return 0
        else
            if [ $attempt -eq $max_attempts ]; then
                echo -e "${RED}❌ 失败: ${description} (已达最大重试次数)${NC}"
                return 1
            fi
            echo -e "${YELLOW}⚠️ 失败，${delay}秒后重试...${NC}"
            sleep $delay
            ((attempt++))
        fi
    done
}

# 错误处理
handle_error() {
    local error_msg="$1"
    local suggestion="$2"
    echo -e "${RED}❌ 错误: ${error_msg}${NC}"
    echo -e "${YELLOW}💡 建议: ${suggestion}${NC}"
    echo -e "${BLUE}📋 详细日志: ${LOG_FILE}${NC}"
    exit 1
}

# 检测系统信息
detect_system() {
    echo -e "${BLUE}🔍 检测系统信息...${NC}"
    
    # 检测操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        handle_error "无法检测操作系统" "请确保使用受支持的Linux发行版"
    fi
    
    echo -e "${GREEN}操作系统: $OS $VER${NC}"
    echo -e "${GREEN}架构: $(uname -m)${NC}"
    echo -e "${GREEN}内核: $(uname -r)${NC}"
    
    # 检查是否为Ubuntu
    if [[ "$OS" != *"Ubuntu"* ]]; then
        echo -e "${YELLOW}⚠️ 警告: 此脚本专为Ubuntu优化，其他系统可能需要手动调整${NC}"
    fi
}

# 配置中国镜像源
setup_china_mirrors() {
    show_progress "1" "12" "配置中国镜像源加速"
    
    echo -e "${YELLOW}🔧 配置apt镜像源...${NC}"
    
    # 备份原始sources.list
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s)
    
    # 检测Ubuntu版本并配置相应的阿里云镜像
    local ubuntu_codename=$(lsb_release -cs)
    
    cat > /etc/apt/sources.list << EOF
# 阿里云Ubuntu镜像源
deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-proposed main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
EOF

    echo -e "${YELLOW}🐍 配置pip中国镜像源...${NC}"
    
    # 全局pip配置
    mkdir -p /etc/pip
    cat > /etc/pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
EOF

    # 根用户pip配置
    mkdir -p ~/.pip
    cp /etc/pip/pip.conf ~/.pip/

    echo -e "${GREEN}✅ 中国镜像源配置完成${NC}"
}

# 更新系统并修复依赖
update_system() {
    show_progress "2" "12" "更新系统并修复依赖冲突"
    
    echo -e "${YELLOW}📦 更新包列表...${NC}"
    retry_command "apt update" "更新包列表"
    
    echo -e "${YELLOW}🔧 修复破损的包...${NC}"
    apt --fix-broken install -y || true
    apt autoremove -y || true
    apt autoclean || true
    
    echo -e "${YELLOW}⬆️ 升级系统包...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt upgrade -y" "升级系统包"
    
    echo -e "${GREEN}✅ 系统更新完成${NC}"
}

# 安装系统依赖
install_system_dependencies() {
    show_progress "3" "12" "安装完整系统依赖"
    
    echo -e "${YELLOW}📦 安装基础工具...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        curl wget git unzip vim nano htop tree \
        software-properties-common apt-transport-https \
        ca-certificates gnupg lsb-release build-essential \
        gcc g++ make cmake pkg-config" "安装基础工具"
    
    echo -e "${YELLOW}🐍 安装Python环境...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        python3 python3-pip python3-venv python3-dev \
        python3-setuptools python3-wheel" "安装Python环境"
    
    echo -e "${YELLOW}🗄️ 安装数据库服务...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        postgresql postgresql-contrib \
        redis-server" "安装数据库服务"
    
    echo -e "${YELLOW}🌐 安装Web服务器...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        nginx supervisor" "安装Web服务器"
    
    echo -e "${YELLOW}📚 安装开发库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libssl-dev libffi-dev libpq-dev \
        libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
        libfreetype6-dev liblcms2-dev libopenjp2-7-dev \
        libavcodec-dev libavformat-dev libswscale-dev \
        ffmpeg libsndfile1-dev portaudio19-dev \
        tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
        libgtk-3-dev libgstreamer1.0-dev \
        libgomp1 libatlas-base-dev liblapack-dev \
        libhdf5-dev libprotobuf-dev protobuf-compiler" "安装开发库"
    
    echo -e "${GREEN}✅ 系统依赖安装完成${NC}"
}

# 配置系统服务
setup_system_services() {
    show_progress "4" "12" "配置PostgreSQL、Redis、Nginx等服务"
    
    echo -e "${YELLOW}🚀 启动系统服务...${NC}"
    systemctl enable postgresql redis-server nginx supervisor
    systemctl start postgresql redis-server nginx supervisor
    
    echo -e "${YELLOW}🗄️ 配置PostgreSQL数据库...${NC}"
    
    # 安全地设置PostgreSQL
    sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1 || handle_error "PostgreSQL启动失败" "检查PostgreSQL服务状态"
    
    # 删除已存在的数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    
    # 创建新的数据库和用户
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    echo -e "${YELLOW}🔒 配置Redis安全设置...${NC}"
    
    # 配置Redis
    sed -i 's/^# requirepass foobared/requirepass qatoolbox123/' /etc/redis/redis.conf || true
    sed -i 's/^bind 127.0.0.1/bind 127.0.0.1/' /etc/redis/redis.conf || true
    systemctl restart redis-server
    
    echo -e "${GREEN}✅ 系统服务配置完成${NC}"
}

# 创建项目用户和目录
setup_project_user() {
    show_progress "5" "12" "创建项目用户和目录结构"
    
    # 创建项目用户
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER"
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 创建成功${NC}"
    else
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 已存在${NC}"
    fi
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    mkdir -p /var/log/qatoolbox
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/log/qatoolbox
    chmod -R 755 /var/www/qatoolbox
    chmod -R 755 /var/log/qatoolbox
    
    # 为项目用户配置pip源
    sudo -u "$PROJECT_USER" mkdir -p "/home/$PROJECT_USER/.pip"
    sudo -u "$PROJECT_USER" cat > "/home/$PROJECT_USER/.pip/pip.conf" << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
EOF

    echo -e "${GREEN}✅ 项目用户和目录配置完成${NC}"
}

# 部署项目代码
deploy_project_code() {
    show_progress "6" "12" "从GitHub克隆项目代码"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    echo -e "${YELLOW}📥 克隆项目代码...${NC}"
    
    # 使用重试机制克隆代码
    retry_command "git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR" "克隆项目代码" 3 10
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    # 验证项目结构
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        handle_error "项目结构异常，未找到manage.py" "检查GitHub仓库是否正确"
    fi
    
    echo -e "${GREEN}✅ 项目代码部署完成${NC}"
}

# 创建Python虚拟环境并安装依赖
setup_python_environment() {
    show_progress "7" "12" "创建Python环境并安装项目依赖"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐍 创建Python虚拟环境...${NC}"
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install --upgrade pip setuptools wheel" "升级pip工具"
    
    echo -e "${YELLOW}📦 安装核心Django依赖...${NC}"
    
    # 分阶段安装依赖，避免冲突
    local core_packages=(
        "Django==4.2.7"
        "djangorestframework==3.14.0"
        "psycopg2-binary==2.9.7"
        "gunicorn==21.2.0"
        "whitenoise==6.6.0"
        "python-dotenv==1.0.0"
        "django-environ==0.11.2"
        "redis==4.6.0"
        "django-redis==5.4.0"
    )
    
    for package in "${core_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装Django扩展包...${NC}"
    
    # Django扩展包
    local django_packages=(
        "django-cors-headers==4.3.1"
        "django-crispy-forms==2.0"
        "crispy-bootstrap5==0.7"
        "django-simple-captcha==0.6.0"
        "django-ratelimit==4.1.0"
        "django-extensions==3.2.3"
        "django-filter==23.3"
    )
    
    for package in "${django_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装数据处理包...${NC}"
    
    # 数据处理包
    local data_packages=(
        "pandas==2.0.3"
        "numpy==1.24.4"
        "Pillow==9.5.0"
        "requests==2.31.0"
        "beautifulsoup4==4.12.2"
        "lxml==4.9.3"
    )
    
    for package in "${data_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装文档处理包...${NC}"
    
    # 文档处理包
    local doc_packages=(
        "python-docx==1.1.0"
        "openpyxl==3.1.2"
        "reportlab==4.0.9"
        "pypdfium2==4.23.1"
    )
    
    for package in "${doc_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 批量安装其他依赖...${NC}"
    
    # 其他工具包
    local other_packages=(
        "celery==5.3.4"
        "channels==4.0.0"
        "daphne==4.0.0"
        "cryptography==41.0.7"
        "tenacity==8.2.3"
        "prettytable==3.9.0"
        "qrcode==7.4.2"
        "python-dateutil==2.8.2"
    )
    
    # 批量安装其他包（允许部分失败）
    local packages_str=$(IFS=' '; echo "${other_packages[*]}")
    sudo -u "$PROJECT_USER" .venv/bin/pip install $packages_str || echo "⚠️ 部分非核心包安装失败，不影响基本功能"
    
    echo -e "${GREEN}✅ Python环境配置完成${NC}"
}

# 配置Django应用
configure_django() {
    show_progress "8" "12" "配置Django应用和数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}⚙️ 创建生产环境配置...${NC}"
    
    # 创建环境变量文件
    cat > .env << EOF
# Django基础配置
DJANGO_SECRET_KEY=django-aliyun-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

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

# 邮件配置 (可选)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 日志配置
LOG_LEVEL=INFO
EOF
    
    # 设置文件权限
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    echo -e "${GREEN}✅ Django配置完成${NC}"
}

# 初始化Django应用
initialize_django() {
    show_progress "9" "12" "初始化Django应用和数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}📊 执行数据库迁移...${NC}"
    
    # 设置Django环境变量
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    
    # 创建迁移文件
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py makemigrations --noinput" "创建数据库迁移" 2 5
    
    # 执行迁移
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py migrate --noinput" "执行数据库迁移" 2 5
    
    echo -e "${YELLOW}📁 收集静态文件...${NC}"
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py collectstatic --noinput" "收集静态文件" 2 5
    
    echo -e "${YELLOW}👑 创建管理员用户...${NC}"
    
    # 创建管理员用户
    sudo -u "$PROJECT_USER" DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py shell << PYTHON_EOF
import os
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# 删除已存在的admin用户
User.objects.filter(username='admin').delete()

# 创建新的管理员用户
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@${DOMAIN}',
    password='${ADMIN_PASSWORD}'
)

print(f"管理员用户创建成功: {admin_user.username}")
print(f"邮箱: {admin_user.email}")
PYTHON_EOF
    
    echo -e "${GREEN}✅ Django应用初始化完成${NC}"
}

# 配置Web服务
setup_web_services() {
    show_progress "10" "12" "配置Nginx和Supervisor服务"
    
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
# QAToolBox Nginx配置
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 文件上传大小限制
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 静态文件
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 1w;
        add_header Cache-Control "public";
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
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
    
    # 错误页面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
EOF
    
    # 启用站点配置
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t || handle_error "Nginx配置语法错误" "检查配置文件语法"
    
    echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
    
    # 创建Supervisor配置
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/gunicorn.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=3
stderr_logfile=/var/log/qatoolbox/gunicorn_error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=3

# Gunicorn配置
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production",PATH="$PROJECT_DIR/.venv/bin"
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application --bind 127.0.0.1:8000 --workers 3 --worker-class sync --timeout 60 --max-requests 1000 --max-requests-jitter 100 --preload

# 进程管理
killasgroup=true
stopasgroup=true
stopsignal=TERM
stopwaitsecs=10
EOF
    
    # 重新加载Supervisor配置
    supervisorctl reread
    supervisorctl update
    
    # 重启服务
    systemctl restart nginx
    supervisorctl restart qatoolbox
    
    echo -e "${GREEN}✅ Web服务配置完成${NC}"
}

# 配置防火墙和安全
setup_security() {
    show_progress "11" "12" "配置防火墙和基础安全"
    
    echo -e "${YELLOW}🔒 配置UFW防火墙...${NC}"
    
    # 安装并配置UFW
    apt install -y ufw
    
    # 重置防火墙规则
    ufw --force reset
    
    # 设置默认策略
    ufw default deny incoming
    ufw default allow outgoing
    
    # 允许必要端口
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 启用防火墙
    ufw --force enable
    
    echo -e "${YELLOW}🛡️ 配置基础安全设置...${NC}"
    
    # 禁用不必要的服务
    systemctl disable apache2 2>/dev/null || true
    
    # 设置文件权限
    chmod 640 "$PROJECT_DIR/.env"
    chmod -R 755 "$PROJECT_DIR"
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 安全配置完成${NC}"
}

# 最终验证和信息显示
final_verification() {
    show_progress "12" "12" "验证部署结果并显示信息"
    
    echo -e "${YELLOW}🔍 等待服务启动...${NC}"
    sleep 15
    
    echo -e "${YELLOW}🔍 检查服务状态...${NC}"
    
    # 检查系统服务
    local services=("nginx" "postgresql" "redis-server" "supervisor")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "${GREEN}✅ $service 运行正常${NC}"
        else
            echo -e "${RED}❌ $service 状态异常${NC}"
        fi
    done
    
    # 检查Supervisor管理的应用
    if supervisorctl status qatoolbox | grep -q "RUNNING"; then
        echo -e "${GREEN}✅ QAToolBox应用运行正常${NC}"
    else
        echo -e "${RED}❌ QAToolBox应用状态异常${NC}"
        echo -e "${YELLOW}📋 查看日志: sudo tail -f /var/log/qatoolbox/gunicorn.log${NC}"
    fi
    
    echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
    
    # 测试本地访问
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    
    if [[ "$http_status" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✅ HTTP访问正常 (状态码: $http_status)${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP访问异常 (状态码: $http_status)${NC}"
    fi
    
    # 显示部署信息
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 部署完成！
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
  Python:   $(python3 --version 2>&1)
  Django:   $(sudo -u $PROJECT_USER $PROJECT_DIR/.venv/bin/python -c "import django; print(django.get_version())" 2>/dev/null || echo "未知")

🔧 管理命令:
  重启应用: sudo supervisorctl restart qatoolbox
  查看日志: sudo tail -f /var/log/qatoolbox/gunicorn.log
  查看状态: sudo supervisorctl status
  重启Nginx: sudo systemctl restart nginx

📋 日志文件:
  部署日志: $LOG_FILE
  应用日志: /var/log/qatoolbox/gunicorn.log
  Django日志: /var/log/qatoolbox/django.log
  Nginx日志: /var/log/nginx/access.log

🔒 安全配置:
  防火墙: UFW已启用
  开放端口: 22(SSH), 80(HTTP), 443(HTTPS)
  数据库密码: $DB_PASSWORD

📝 下一步建议:
  1. 配置SSL证书 (Let's Encrypt)
  2. 设置域名DNS解析
  3. 配置邮件服务
  4. 设置定期备份

========================================
EOF
    echo -e "${NC}"
    
    # 显示重要文件路径
    echo -e "${BLUE}📁 重要文件路径:${NC}"
    echo -e "  配置文件: $PROJECT_DIR/.env"
    echo -e "  Nginx配置: /etc/nginx/sites-available/qatoolbox"
    echo -e "  Supervisor配置: /etc/supervisor/conf.d/qatoolbox.conf"
    echo ""
    
    # 提供快速测试命令
    echo -e "${GREEN}🧪 快速测试命令:${NC}"
    echo -e "  curl -I http://localhost/"
    echo -e "  curl -I http://$SERVER_IP/"
    echo ""
    
    echo -e "${CYAN}🎊 部署成功完成！现在可以开始使用QAToolBox了！${NC}"
}

# 主执行流程
main() {
    # 检查权限
    check_root
    
    # 设置错误处理
    trap 'echo -e "${RED}❌ 部署过程中出现错误，请查看日志: $LOG_FILE${NC}"; exit 1' ERR
    
    echo -e "${BLUE}🚀 开始QAToolBox阿里云一键部署...${NC}"
    echo -e "${BLUE}📋 详细日志: $LOG_FILE${NC}"
    echo ""
    
    # 执行部署步骤
    detect_system
    setup_china_mirrors
    update_system
    install_system_dependencies
    setup_system_services
    setup_project_user
    deploy_project_code
    setup_python_environment
    configure_django
    initialize_django
    setup_web_services
    setup_security
    final_verification
    
    echo -e "${GREEN}🎉 QAToolBox阿里云一键部署成功完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
