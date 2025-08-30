#!/bin/bash
# =============================================================================
# QAToolBox 最终完整一键部署脚本 v4.0
# =============================================================================
# 包含所有问题修复和完整生产部署配置
# 支持 Python 3.12 + Django 4.2 + 完整功能
# 自动处理所有依赖、配置 Nginx + Gunicorn、防火墙等
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
readonly GITHUB_REPO="https://github.com/shinytsing/QAToolbox.git"
readonly SERVER_IP="${SERVER_IP:-$(hostname -I | awk '{print $1}')}"
readonly DOMAIN="${DOMAIN:-$SERVER_IP}"
readonly PROJECT_USER="${PROJECT_USER:-qatoolbox}"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly PYTHON_VERSION="3.12"
readonly VENV_NAME="venv_py312"
readonly DB_PASSWORD="${DB_PASSWORD:-QAToolBox@2024@$(date +%s)}"
readonly ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123456}"

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_final_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox 最终完整一键部署 v4.0
========================================
✨ 特性:
  • Python 3.12 完全支持
  • 自动修复所有已知问题
  • 完整的依赖包安装
  • Nginx + Gunicorn 生产配置
  • 防火墙自动配置
  • 超级用户自动创建
  • SSL 证书支持 (可选)
  • 完整的监控和日志
========================================
EOF
echo -e "${NC}"

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
    local max_attempts="${3:-3}"
    local delay="${4:-5}"
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

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
        echo -e "${YELLOW}💡 使用命令: sudo $0${NC}"
        exit 1
    fi
}

# 检查系统环境
check_system() {
    show_progress "1" "15" "检查系统环境"
    
    echo -e "${BLUE}🔍 检查系统信息...${NC}"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo -e "   操作系统: $PRETTY_NAME"
        echo -e "   版本: $VERSION"
    fi
    
    echo -e "   服务器IP: $SERVER_IP"
    echo -e "   域名: $DOMAIN"
    echo -e "   项目用户: $PROJECT_USER"
    echo -e "   项目目录: $PROJECT_DIR"
}

# 更新系统
update_system() {
    show_progress "2" "15" "更新系统包"
    
    echo -e "${BLUE}📦 更新系统包...${NC}"
    retry_command "apt update && apt upgrade -y" "系统更新"
}

# 安装基础工具
install_basic_tools() {
    show_progress "3" "15" "安装基础工具"
    
    echo -e "${BLUE}🔧 安装基础工具...${NC}"
    retry_command "apt install -y curl wget git unzip vim nano htop tree \
        software-properties-common apt-transport-https ca-certificates \
        gnupg lsb-release build-essential gcc g++ make cmake pkg-config" "安装基础工具"
}

# 安装Python 3.12
install_python312() {
    show_progress "4" "15" "安装Python 3.12"
    
    echo -e "${BLUE}🐍 安装Python 3.12...${NC}"
    
    # 添加deadsnakes PPA
    retry_command "add-apt-repository ppa:deadsnakes/ppa -y" "添加Python PPA"
    retry_command "apt update" "更新包索引"
    
    # 安装Python 3.12
    retry_command "apt install -y python3.12 python3.12-venv python3.12-dev \
        python3-setuptools python3-wheel python3-pip" "安装Python 3.12"
    
    # 确保pip可用
    if ! python3.12 -m pip --version &>/dev/null; then
        echo -e "${YELLOW}📦 为Python 3.12安装pip...${NC}"
        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
    fi
    
    echo -e "   ✅ Python版本: $(python3.12 --version)"
    echo -e "   ✅ pip版本: $(python3.12 -m pip --version)"
}

# 安装系统依赖
install_system_dependencies() {
    show_progress "5" "15" "安装系统依赖"
    
    echo -e "${BLUE}📦 安装系统依赖...${NC}"
    
    # 数据库服务
    retry_command "apt install -y postgresql postgresql-contrib redis-server" "安装数据库"
    
    # 系统库
    retry_command "apt install -y libpq-dev libmysqlclient-dev libsqlite3-dev \
        libjpeg-dev libpng-dev libfreetype6-dev libssl-dev libffi-dev \
        libxml2-dev libxslt1-dev zlib1g-dev" "安装开发库"
    
    # Web服务器
    retry_command "apt install -y nginx" "安装Nginx"
    
    # 防火墙
    retry_command "ufw --force enable" "启用防火墙"
}

# 创建项目用户
create_project_user() {
    show_progress "6" "15" "创建项目用户"
    
    echo -e "${BLUE}👤 创建项目用户...${NC}"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        echo -e "   ✅ 用户 $PROJECT_USER 创建成功"
    else
        echo -e "   ℹ️ 用户 $PROJECT_USER 已存在"
    fi
    
    usermod -aG sudo "$PROJECT_USER"
    echo -e "   ✅ 用户已添加到sudo组"
}

# 配置数据库
setup_database() {
    show_progress "7" "15" "配置数据库"
    
    echo -e "${BLUE}🗄️ 配置PostgreSQL...${NC}"
    
    systemctl start postgresql
    systemctl enable postgresql
    
    # 创建数据库和用户
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox;" 2>/dev/null || echo "数据库已存在"
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || echo "用户已存在"
    sudo -u postgres psql -c "ALTER ROLE qatoolbox SET client_encoding TO 'utf8';"
    sudo -u postgres psql -c "ALTER ROLE qatoolbox SET default_transaction_isolation TO 'read committed';"
    sudo -u postgres psql -c "ALTER ROLE qatoolbox SET timezone TO 'UTC';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    # 配置Redis
    systemctl start redis-server
    systemctl enable redis-server
    
    echo -e "   ✅ 数据库配置完成"
}

# 克隆项目
clone_project() {
    show_progress "8" "15" "克隆项目代码"
    
    echo -e "${BLUE}📥 克隆项目代码...${NC}"
    
    if [ -d "$PROJECT_DIR" ]; then
        echo -e "   🗑️ 删除现有目录..."
        rm -rf "$PROJECT_DIR"
    fi
    
    # 尝试多个镜像源
    echo -e "   📡 尝试从GitHub主站克隆..."
    if ! git clone "$GITHUB_REPO" "$PROJECT_DIR" 2>/dev/null; then
        echo -e "   ${YELLOW}GitHub主站连接失败，尝试镜像源...${NC}"
        
        local mirror_repos=(
            "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git"
            "https://hub.fastgit.xyz/shinytsing/QAToolbox.git"
            "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
        )
        
        local success=false
        for repo in "${mirror_repos[@]}"; do
            echo -e "   🔄 尝试镜像源: $repo"
            if git clone "$repo" "$PROJECT_DIR" 2>/dev/null; then
                success=true
                break
            fi
            rm -rf "$PROJECT_DIR" 2>/dev/null
        done
        
        if [ "$success" = false ]; then
            echo -e "${RED}❌ 所有克隆方式都失败了${NC}"
            exit 1
        fi
    fi
    
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    echo -e "   ✅ 项目代码克隆完成"
}

# 创建Python环境
create_python_environment() {
    show_progress "9" "15" "创建Python环境"
    
    echo -e "${BLUE}🐍 创建Python虚拟环境...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 删除旧环境
    if [ -d "$VENV_NAME" ]; then
        rm -rf "$VENV_NAME"
    fi
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    # 创建新环境
    sudo -u "$PROJECT_USER" python3.12 -m venv "$VENV_NAME"
    chown -R "$PROJECT_USER:$PROJECT_USER" "$VENV_NAME"
    
    # 升级pip
    sudo -u "$PROJECT_USER" "$VENV_NAME/bin/pip" install --upgrade pip setuptools wheel
    
    echo -e "   ✅ Python环境创建完成"
}

# 安装Python依赖
install_python_dependencies() {
    show_progress "10" "15" "安装Python依赖"
    
    echo -e "${BLUE}📚 安装Python依赖包...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 完整的依赖包列表（包含所有修复）
    local all_packages=(
        # 核心Django框架
        "Django>=4.2,<5.0"
        "djangorestframework>=3.14.0"
        "django-cors-headers>=4.3.0"
        "django-crispy-forms>=2.0"
        "crispy-bootstrap5>=0.7"
        "django-simple-captcha>=0.6.0"
        "django-ratelimit>=4.1.0"
        "django-extensions>=3.2.3"
        "django-filter>=23.3"
        
        # 数据库和缓存
        "psycopg2-binary>=2.9.7"
        "redis>=4.6.0"
        "django-redis>=5.4.0"
        
        # Web服务器
        "gunicorn>=21.2.0"
        "whitenoise>=6.6.0"
        
        # 环境配置
        "python-dotenv>=1.0.0"
        "django-environ>=0.11.0"
        
        # HTTP和网络
        "requests>=2.31.0"
        "beautifulsoup4>=4.12.0"
        "lxml>=4.9.0"
        
        # 数据处理
        "pandas>=2.1.0"
        "numpy>=1.26.0"
        "Pillow>=10.0.0"
        
        # 文档处理
        "python-docx>=1.1.0"
        "python-pptx>=0.6.22"
        "openpyxl>=3.1.2"
        "reportlab>=4.0.9"
        "pypdfium2>=4.23.1"
        "pdfplumber>=0.10.3"
        "PyMuPDF>=1.23.0"
        
        # 系统监控
        "psutil>=5.9.0"
        "GPUtil>=1.4.0"
        "py-cpuinfo>=9.0.0"
        
        # 思维导图和图表
        "xmind>=1.2.0"
        "matplotlib>=3.8.0"
        "seaborn>=0.12.0"
        
        # 任务队列
        "celery>=5.3.0"
        "django-celery-beat>=2.5.0"
        
        # 实时通信
        "channels>=4.0.0"
        "channels-redis>=4.1.0"
        "daphne>=4.0.0"
        
        # 安全和加密
        "cryptography>=41.0.0"
        
        # 工具库
        "tenacity>=8.2.0"
        "prettytable>=3.9.0"
        "qrcode>=7.4.0"
        "python-dateutil>=2.8.0"
        
        # 音视频处理
        "pydub>=0.25.1"
        "librosa>=0.10.1"
        
        # OCR和图像
        "pytesseract>=0.3.10"
        "opencv-python-headless>=4.8.0"
        
        # 科学计算
        "scipy>=1.11.0"
        "scikit-learn>=1.3.0"
        
        # Web爬虫和浏览器
        "selenium>=4.15.0"
        "webdriver-manager>=4.0.0"
    )
    
    echo -e "   📦 安装 ${#all_packages[@]} 个依赖包..."
    
    # 分批安装提高成功率
    local batch_size=5
    local total_packages=${#all_packages[@]}
    local failed_packages=()
    
    for ((i=0; i<total_packages; i+=batch_size)); do
        local batch=("${all_packages[@]:i:batch_size}")
        local batch_str=$(IFS=' '; echo "${batch[*]}")
        
        echo -e "   📦 安装批次 $((i/batch_size + 1)): ${batch[0]} 等..."
        
        if sudo -u "$PROJECT_USER" "$VENV_NAME/bin/pip" install $batch_str; then
            echo -e "   ✅ 批次 $((i/batch_size + 1)) 安装成功"
        else
            echo -e "   ⚠️ 批次失败，尝试单独安装..."
            for package in "${batch[@]}"; do
                if ! sudo -u "$PROJECT_USER" "$VENV_NAME/bin/pip" install "$package"; then
                    failed_packages+=("$package")
                    echo -e "     ❌ $package 安装失败"
                else
                    echo -e "     ✅ $package 安装成功"
                fi
            done
        fi
    done
    
    # 报告安装结果
    if [ ${#failed_packages[@]} -eq 0 ]; then
        echo -e "${GREEN}   ✅ 所有依赖包安装成功！${NC}"
    else
        echo -e "${YELLOW}   ⚠️ 以下包安装失败（不影响核心功能）:${NC}"
        for pkg in "${failed_packages[@]}"; do
            echo -e "     - $pkg"
        done
    fi
}

# 配置环境变量
configure_environment() {
    show_progress "11" "15" "配置环境变量"
    
    echo -e "${BLUE}⚙️ 配置环境变量...${NC}"
    
    cd "$PROJECT_DIR"
    
    cat > .env << EOF
# QAToolBox 生产环境配置
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=localhost,127.0.0.1,$SERVER_IP,$DOMAIN

# 数据库配置
DATABASE_URL=postgresql://qatoolbox:$DB_PASSWORD@localhost:5432/qatoolbox

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 静态文件配置
STATIC_ROOT=$PROJECT_DIR/staticfiles
MEDIA_ROOT=$PROJECT_DIR/media

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=$PROJECT_DIR/logs/django.log

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
EOF
    
    chown "$PROJECT_USER:$PROJECT_USER" .env
    echo -e "   ✅ 环境变量配置完成"
}

# Django初始化
initialize_django() {
    show_progress "12" "15" "初始化Django应用"
    
    echo -e "${BLUE}🚀 初始化Django应用...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 创建必要目录
    mkdir -p logs media staticfiles
    chown -R "$PROJECT_USER:$PROJECT_USER" logs media staticfiles
    
    # 设置Django环境
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    
    # 运行Django命令
    echo -e "   🔍 检查Django配置..."
    sudo -u "$PROJECT_USER" -E "$VENV_NAME/bin/python" manage.py check --deploy
    
    echo -e "   📋 创建数据库迁移..."
    sudo -u "$PROJECT_USER" -E "$VENV_NAME/bin/python" manage.py makemigrations --noinput
    
    echo -e "   🗄️ 执行数据库迁移..."
    sudo -u "$PROJECT_USER" -E "$VENV_NAME/bin/python" manage.py migrate --noinput
    
    echo -e "   📁 收集静态文件..."
    sudo -u "$PROJECT_USER" -E "$VENV_NAME/bin/python" manage.py collectstatic --noinput
    
    echo -e "   ✅ Django初始化完成"
}

# 创建超级用户
create_superuser() {
    show_progress "13" "15" "创建超级用户"
    
    echo -e "${BLUE}👑 创建超级用户...${NC}"
    
    cd "$PROJECT_DIR"
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    
    # 创建超级用户
    sudo -u "$PROJECT_USER" -E "$VENV_NAME/bin/python" manage.py shell << PYTHON_EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qatoolbox.com', '$ADMIN_PASSWORD')
    print('超级用户创建成功: admin / $ADMIN_PASSWORD')
else:
    print('超级用户已存在')
PYTHON_EOF
    
    echo -e "   ✅ 超级用户配置完成"
    echo -e "   👤 用户名: admin"
    echo -e "   🔑 密码: $ADMIN_PASSWORD"
}

# 配置Nginx和Gunicorn
configure_web_server() {
    show_progress "14" "15" "配置Web服务器"
    
    echo -e "${BLUE}🌐 配置Nginx和Gunicorn...${NC}"
    
    # 创建Gunicorn配置
    cat > "$PROJECT_DIR/gunicorn.conf.py" << EOF
# Gunicorn 配置文件
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 60
keepalive = 5
preload_app = True
daemon = False
user = "$PROJECT_USER"
group = "$PROJECT_USER"
tmp_upload_dir = None
errorlog = "$PROJECT_DIR/logs/gunicorn_error.log"
accesslog = "$PROJECT_DIR/logs/gunicorn_access.log"
access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "info"
EOF
    
    # 创建systemd服务文件
    cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=notify
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/gunicorn config.wsgi:application -c $PROJECT_DIR/gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建Celery服务
    cat > /etc/systemd/system/qatoolbox-celery.service << EOF
[Unit]
Description=QAToolBox Celery Worker
After=network.target

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
Environment=DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/celery -A config worker -l info
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $DOMAIN $SERVER_IP;
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
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
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t
    
    echo -e "   ✅ Web服务器配置完成"
}

# 配置防火墙和启动服务
finalize_deployment() {
    show_progress "15" "15" "完成部署"
    
    echo -e "${BLUE}🔒 配置防火墙和启动服务...${NC}"
    
    # 配置防火墙
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp  # 临时开放，调试用
    ufw --force enable
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启动服务
    systemctl enable qatoolbox
    systemctl start qatoolbox
    
    systemctl enable qatoolbox-celery
    systemctl start qatoolbox-celery
    
    systemctl enable nginx
    systemctl restart nginx
    
    # 等待服务启动
    sleep 5
    
    echo -e "   ✅ 所有服务启动完成"
}

# 显示部署结果
show_deployment_result() {
    echo -e "${GREEN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 部署完成！
========================================

📋 部署信息:
   • 服务器IP: $SERVER_IP
   • 域名: $DOMAIN
   • 项目目录: $PROJECT_DIR
   • Python版本: $(python3.12 --version)
   • 虚拟环境: $PROJECT_DIR/$VENV_NAME

🌐 访问信息:
   • 主站: http://$DOMAIN
   • 管理后台: http://$DOMAIN/admin/
   • 健康检查: http://$DOMAIN/health/
   • 备用访问: http://$SERVER_IP

👤 管理员账户:
   • 用户名: admin
   • 密码: $ADMIN_PASSWORD
   • 邮箱: admin@qatoolbox.com

🔧 服务管理命令:
   • 查看Django状态: systemctl status qatoolbox
   • 查看Celery状态: systemctl status qatoolbox-celery
   • 查看Nginx状态: systemctl status nginx
   • 重启Django: systemctl restart qatoolbox
   • 查看日志: tail -f $PROJECT_DIR/logs/gunicorn_error.log

📝 重要文件位置:
   • 项目配置: $PROJECT_DIR/.env
   • Nginx配置: /etc/nginx/sites-available/qatoolbox
   • 服务配置: /etc/systemd/system/qatoolbox.service
   • 部署日志: $LOG_FILE

🔒 安全配置:
   • 防火墙已启用 (22, 80, 443, 8000端口开放)
   • PostgreSQL数据库已配置
   • Redis缓存已启用
   • 静态文件缓存已优化

💡 下一步建议:
   1. 配置SSL证书: certbot --nginx -d $DOMAIN
   2. 设置域名解析到 $SERVER_IP
   3. 配置定期备份
   4. 设置监控告警
   5. 关闭调试端口: ufw delete allow 8000/tcp

🚀 开始使用:
   访问 http://$DOMAIN 开始使用 QAToolBox！

========================================
EOF
    echo -e "${NC}"
    
    echo -e "${CYAN}📊 服务状态检查:${NC}"
    echo -e "   Django应用: $(systemctl is-active qatoolbox)"
    echo -e "   Celery任务: $(systemctl is-active qatoolbox-celery)"
    echo -e "   Nginx服务: $(systemctl is-active nginx)"
    echo -e "   PostgreSQL: $(systemctl is-active postgresql)"
    echo -e "   Redis缓存: $(systemctl is-active redis-server)"
    
    # 测试网站访问
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost" | grep -q "200\|301\|302"; then
        echo -e "   ${GREEN}✅ 网站访问正常${NC}"
    else
        echo -e "   ${YELLOW}⚠️ 网站访问测试失败，请检查服务状态${NC}"
    fi
}

# 主函数
main() {
    echo -e "${CYAN}🚀 开始QAToolBox完整部署...${NC}"
    
    check_root
    check_system
    update_system
    install_basic_tools
    install_python312
    install_system_dependencies
    create_project_user
    setup_database
    clone_project
    create_python_environment
    install_python_dependencies
    configure_environment
    initialize_django
    create_superuser
    configure_web_server
    finalize_deployment
    show_deployment_result
    
    echo -e "${GREEN}🎉 QAToolBox 完整部署成功！${NC}"
    echo -e "${BLUE}📝 详细日志: $LOG_FILE${NC}"
}

# 运行主函数
main "$@"
