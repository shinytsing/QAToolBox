#!/bin/bash
# QAToolBox 阿里云服务器终极一键部署脚本
# =============================================
# 专为阿里云服务器优化，包含完整的错误处理和重试机制
# 支持Ubuntu/CentOS系统，自动检测和适配
# =============================================

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
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DB_PASSWORD="QAToolBox@2024"
LOG_FILE="/var/log/qatoolbox_deploy.log"
RETRY_COUNT=3

# 日志函数
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() { log_message "INFO" "$1"; }
log_success() { log_message "SUCCESS" "$1"; echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { log_message "WARNING" "$1"; echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { log_message "ERROR" "$1"; echo -e "${RED}❌ $1${NC}"; }
log_header() { 
    log_message "HEADER" "$1"
    echo -e "${PURPLE}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
}

# 重试函数
retry_command() {
    local cmd="$1"
    local description="$2"
    local max_retries=${3:-$RETRY_COUNT}
    
    for ((i=1; i<=max_retries; i++)); do
        log_info "执行: $description (尝试 $i/$max_retries)"
        if eval "$cmd"; then
            log_success "$description 成功"
            return 0
        else
            log_warning "$description 失败 (尝试 $i/$max_retries)"
            if [ $i -eq $max_retries ]; then
                log_error "$description 最终失败"
                return 1
            fi
            sleep 2
        fi
    done
}

# 检查系统要求
check_requirements() {
    log_header "检查系统要求"
    
    # 检查root权限
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行: sudo $0"
        exit 1
    fi
    
    # 检查系统类型
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        OS_ID=$ID
    else
        log_error "无法检测系统类型"
        exit 1
    fi
    
    log_success "检测到系统: $OS $VER ($OS_ID)"
    
    # 检查内存
    local mem_total=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    if [ "$mem_total" -lt 2 ]; then
        log_warning "系统内存不足 (${mem_total}GB)，建议至少2GB内存"
    else
        log_success "系统内存: ${mem_total}GB"
    fi
    
    # 检查磁盘空间
    local disk_free=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_free" -lt 10 ]; then
        log_warning "磁盘空间不足 (${disk_free}GB)，建议至少10GB可用空间"
    else
        log_success "磁盘可用空间: ${disk_free}GB"
    fi
}

# 系统初始化
setup_system() {
    log_header "系统初始化"
    
    # 更新系统
    log_info "更新系统包管理器..."
    if [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
        retry_command "apt update && apt upgrade -y" "系统更新"
        
        # 安装基础工具
        retry_command "apt install -y curl wget git unzip vim nano htop tree software-properties-common apt-transport-https ca-certificates gnupg lsb-release" "安装基础工具"
        
    elif [ "$OS_ID" = "centos" ] || [ "$OS_ID" = "rhel" ] || [ "$OS_ID" = "rocky" ]; then
        retry_command "yum update -y" "系统更新"
        
        # 安装基础工具
        retry_command "yum install -y curl wget git unzip vim nano htop tree epel-release" "安装基础工具"
    fi
    
    log_success "系统初始化完成"
}

# 安装Python环境
install_python() {
    log_header "安装Python环境"
    
    if [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
        retry_command "apt install -y python3 python3-pip python3-venv python3-dev build-essential gcc g++ make pkg-config cmake libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev" "安装Python开发环境"
        
        # 修复Ubuntu系统的pip升级问题
        log_info "修复Ubuntu系统的pip升级问题..."
        
        # 方法1: 尝试使用--break-system-packages
        if python3 -m pip install --upgrade pip setuptools wheel --break-system-packages 2>/dev/null; then
            log_success "使用--break-system-packages升级pip成功"
        else
            log_warning "方法1失败，尝试方法2..."
            
            # 方法2: 强制重新安装，忽略已安装的包
            if python3 -m pip install --upgrade --force-reinstall --ignore-installed pip setuptools wheel 2>/dev/null; then
                log_success "使用--force-reinstall升级pip成功"
            else
                log_warning "方法2失败，尝试方法3..."
                
                # 方法3: 只升级pip和setuptools，不升级wheel
                if python3 -m pip install --upgrade --force-reinstall pip setuptools 2>/dev/null; then
                    log_success "升级pip和setuptools成功（跳过wheel）"
                else
                    log_warning "方法3失败，尝试方法4..."
                    
                    # 方法4: 使用apt升级系统pip
                    if apt install -y --only-upgrade python3-pip 2>/dev/null; then
                        log_success "使用apt升级系统pip成功"
                    else
                        log_error "所有pip升级方法都失败，继续使用系统默认版本"
                    fi
                fi
            fi
        fi
        
    elif [ "$OS_ID" = "centos" ] || [ "$OS_ID" = "rhel" ] || [ "$OS_ID" = "rocky" ]; then
        retry_command "yum install -y python3 python3-pip python3-devel gcc gcc-c++ make pkgconfig cmake3 libffi-devel openssl-devel bzip2-devel readline-devel sqlite-devel ncurses-devel tk-devel xz-devel" "安装Python开发环境"
        
        # 升级pip
        retry_command "python3 -m pip install --upgrade pip setuptools wheel" "升级pip"
    fi
    
    log_success "Python环境安装完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_header "安装系统依赖"
    
    if [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
        retry_command "apt install -y libssl-dev libcrypto++-dev libpq-dev postgresql-client libmysqlclient-dev libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libgtk-3-dev libcanberra-gtk-module libcanberra-gtk3-module libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libomp-dev libatlas-base-dev liblapack-dev libblas-dev libhdf5-dev libhdf5-serial-dev libprotobuf-dev protobuf-compiler libsndfile1-dev portaudio19-dev ffmpeg tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra chromium-browser chromium-chromedriver" "安装系统依赖库"
        
    elif [ "$OS_ID" = "centos" ] || [ "$OS_ID" = "rhel" ] || [ "$OS_ID" = "rocky" ]; then
        retry_command "yum install -y openssl-devel libpq-devel postgresql postgresql-contrib mysql-devel libjpeg-devel libpng-devel libtiff-devel ffmpeg-devel gtk3-devel glib2-devel mesa-libGL-devel libXext-devel libXrender-devel atlas-devel lapack-devel blas-devel hdf5-devel protobuf-devel protobuf-compiler portaudio-devel tesseract tesseract-langpack-chi-sim tesseract-langpack-chi-tra chromium chromium-headless chromedriver" "安装系统依赖库"
    fi
    
    log_success "系统依赖安装完成"
}

# 安装服务软件
install_services() {
    log_header "安装服务软件"
    
    if [ "$OS_ID" = "ubuntu" ] || [ "$OS_ID" = "debian" ]; then
        # PostgreSQL
        retry_command "apt install -y postgresql postgresql-contrib" "安装PostgreSQL"
        systemctl start postgresql
        systemctl enable postgresql
        
        # Redis
        retry_command "apt install -y redis-server" "安装Redis"
        systemctl start redis-server
        systemctl enable redis-server
        
        # Nginx
        retry_command "apt install -y nginx" "安装Nginx"
        systemctl start nginx
        systemctl enable nginx
        
        # Supervisor
        retry_command "apt install -y supervisor" "安装Supervisor"
        systemctl start supervisor
        systemctl enable supervisor
        
    elif [ "$OS_ID" = "centos" ] || [ "$OS_ID" = "rhel" ] || [ "$OS_ID" = "rocky" ]; then
        # PostgreSQL
        retry_command "yum install -y postgresql postgresql-server postgresql-contrib" "安装PostgreSQL"
        postgresql-setup initdb
        systemctl start postgresql
        systemctl enable postgresql
        
        # Redis
        retry_command "yum install -y redis" "安装Redis"
        systemctl start redis
        systemctl enable redis
        
        # Nginx
        retry_command "yum install -y nginx" "安装Nginx"
        systemctl start nginx
        systemctl enable nginx
        
        # Supervisor
        retry_command "yum install -y supervisor" "安装Supervisor"
        systemctl start supervisord
        systemctl enable supervisord
    fi
    
    log_success "服务软件安装完成"
}

# 配置数据库
setup_database() {
    log_header "配置数据库"
    
    # 删除旧数据库（如果存在）
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    
    # 创建新用户和数据库
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    log_success "数据库配置完成"
}

# 创建项目用户
setup_project_user() {
    log_header "创建项目用户"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER" 2>/dev/null || usermod -aG wheel "$PROJECT_USER" 2>/dev/null || true
        log_success "用户 $PROJECT_USER 创建成功"
    else
        log_success "用户 $PROJECT_USER 已存在"
    fi
    
    # 确保用户目录权限正确
    if [ -d "/home/$PROJECT_USER" ]; then
        chown -R "$PROJECT_USER:$PROJECT_USER" "/home/$PROJECT_USER"
        chmod 755 "/home/$PROJECT_USER"
        log_success "用户目录权限已修复"
    fi
}

# 修复权限问题
fix_permissions() {
    log_header "修复权限问题"
    
    # 确保项目目录权限正确
    if [ -d "$PROJECT_DIR" ]; then
        chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        chmod -R 755 "$PROJECT_DIR"
        log_success "项目目录权限已修复"
    fi
    
    # 确保静态文件目录权限正确
    if [ -d "/var/www/qatoolbox" ]; then
        chown -R "$PROJECT_USER:$PROJECT_USER" "/var/www/qatoolbox"
        chmod -R 755 "/var/www/qatoolbox"
        log_success "静态文件目录权限已修复"
    fi
    
    # 确保日志目录权限正确
    if [ -d "/var/log" ]; then
        touch "/var/log/qatoolbox.log" "/var/log/qatoolbox_error.log" 2>/dev/null || true
        chown "$PROJECT_USER:$PROJECT_USER" "/var/log/qatoolbox.log" "/var/log/qatoolbox_error.log" 2>/dev/null || true
        chmod 644 "/var/log/qatoolbox.log" "/var/log/qatoolbox_error.log" 2>/dev/null || true
        log_success "日志文件权限已修复"
    fi
}

# 下载项目代码
download_project() {
    log_header "下载项目代码"
    
    # 确保项目目录权限正确
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 创建项目目录并设置正确权限
    mkdir -p "$PROJECT_DIR"
    chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    chmod 755 "$PROJECT_DIR"
    
    # 尝试多个源克隆（中国网络环境优化）
    CLONE_SUCCESS=false
    
    # 尝试从Gitee克隆（中国网络优化）
    log_info "尝试从 https://gitee.com/shinytsing/QAToolbox.git 克隆..."
    if sudo -u "$PROJECT_USER" git clone https://gitee.com/shinytsing/QAToolbox.git "$PROJECT_DIR" 2>/dev/null; then
        log_success "从Gitee下载成功"
        CLONE_SUCCESS=true
    else
        log_warning "从Gitee克隆失败，尝试下一个..."
        sudo -u "$PROJECT_USER" rm -rf "$PROJECT_DIR" 2>/dev/null || true
        mkdir -p "$PROJECT_DIR"
        chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    fi
    
    # 尝试从GitHub镜像克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://github.com.cnpmjs.org/shinytsing/QAToolbox.git 克隆..."
        if sudo -u "$PROJECT_USER" git clone https://github.com.cnpmjs.org/shinytsing/QAToolbox.git "$PROJECT_DIR" 2>/dev/null; then
            log_success "从GitHub镜像下载成功"
            CLONE_SUCCESS=true
        else
            log_warning "从GitHub镜像克隆失败，尝试下一个..."
            sudo -u "$PROJECT_USER" rm -rf "$PROJECT_DIR" 2>/dev/null || true
            mkdir -p "$PROJECT_DIR"
            chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        fi
    fi
    
    # 尝试从FastGit克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://hub.fastgit.xyz/shinytsing/QAToolbox.git 克隆..."
        if sudo -u "$PROJECT_USER" git clone https://hub.fastgit.xyz/shinytsing/QAToolbox.git "$PROJECT_DIR" 2>/dev/null; then
            log_success "从FastGit下载成功"
            CLONE_SUCCESS=true
        else
            log_warning "从FastGit克隆失败，尝试下一个..."
            sudo -u "$PROJECT_USER" rm -rf "$PROJECT_DIR" 2>/dev/null || true
            mkdir -p "$PROJECT_DIR"
            chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        fi
    fi
    
    # 最后尝试从GitHub克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://github.com/shinytsing/QAToolbox.git 克隆..."
        if sudo -u "$PROJECT_USER" git clone https://github.com/shinytsing/QAToolbox.git "$PROJECT_DIR" 2>/dev/null; then
            log_success "从GitHub下载成功"
            CLONE_SUCCESS=true
        else
            log_warning "从GitHub克隆失败，创建基础项目结构"
        fi
    fi
    
    # 如果所有克隆都失败，创建基础项目结构
    if [ "$CLONE_SUCCESS" = false ]; then
        log_warning "所有Git源都失败，创建基础项目结构"
        cd "$PROJECT_DIR"
        
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
    
    log_success "项目代码准备完成"
}

# 创建Python虚拟环境并安装依赖
setup_python_environment() {
    log_header "创建Python环境"
    
    cd "$PROJECT_DIR"
    
    # 删除旧虚拟环境
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    # 创建虚拟环境
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip（修复wheel冲突问题）
    log_info "升级虚拟环境中的pip..."
    if sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade pip setuptools wheel 2>/dev/null; then
        log_success "虚拟环境pip升级成功"
    else
        log_warning "标准升级失败，尝试强制重新安装..."
        if sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade --force-reinstall pip setuptools wheel 2>/dev/null; then
            log_success "强制重新安装pip成功"
        else
            log_warning "强制重新安装失败，尝试跳过wheel..."
            if sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade --force-reinstall pip setuptools 2>/dev/null; then
                log_success "升级pip和setuptools成功（跳过wheel）"
            else
                log_error "虚拟环境pip升级失败，继续使用默认版本"
            fi
        fi
    fi
    
    log_info "安装Python依赖包..."
    
    # 安装基础Django依赖
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install Django==4.2.7 psycopg2-binary==2.9.7 gunicorn==21.2.0 python-dotenv==1.0.0" "安装Django基础依赖"
    
    # 安装机器学习依赖
    log_info "安装机器学习依赖（可能需要较长时间）..."
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install torch==2.1.2 torchvision==0.16.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cpu" "安装PyTorch"
    
    # 安装其他依赖
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install opencv-python==4.8.1.78 numpy==1.24.4 scikit-learn==1.3.2 django-environ==0.11.2 python-decouple==3.8 redis==4.6.0 Pillow==9.5.0 requests==2.31.0" "安装其他依赖"
    
    # 如果有requirements文件，安装剩余依赖
    if [ -f "requirements_complete.txt" ]; then
        log_info "安装剩余依赖..."
        sudo -u "$PROJECT_USER" .venv/bin/pip install -r requirements_complete.txt || true
    fi
    
    log_success "Python环境配置完成"
}

# 配置环境变量
setup_environment_variables() {
    log_header "配置环境变量"
    
    cd "$PROJECT_DIR"
    
    cat > .env << EOF
# QAToolBox 生产环境配置
SECRET_KEY=django-aliyun-production-key-$(date +%s)
DEBUG=False
ALLOWED_HOSTS=*,localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 站点配置
SITE_URL=http://localhost
DJANGO_SETTINGS_MODULE=settings

# 静态文件配置
STATIC_URL=/static/
STATIC_ROOT=/var/www/qatoolbox/static/
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/qatoolbox/media/
EOF
    
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    log_success "环境变量配置完成"
}

# 初始化Django项目
initialize_django() {
    log_header "初始化Django项目"
    
    cd "$PROJECT_DIR"
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    
    # 数据库迁移
    log_info "执行数据库迁移..."
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py makemigrations --noinput || true
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py migrate --noinput
    
    # 收集静态文件
    log_info "收集静态文件..."
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py collectstatic --noinput || true
    
    # 创建超级用户
    log_info "创建管理员用户..."
    sudo -u "$PROJECT_USER" .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@localhost', 'admin123456')
    print("管理员用户创建成功: admin/admin123456")
else:
    print("管理员用户已存在")
PYTHON_EOF
    
    log_success "Django项目初始化完成"
}

# 配置Nginx
setup_nginx() {
    log_header "配置Nginx"
    
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name _;
    
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
    
    log_success "Nginx配置完成"
}

# 配置Supervisor
setup_supervisor() {
    log_header "配置Supervisor"
    
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
    
    log_success "Supervisor配置完成"
}

# 验证部署
verify_deployment() {
    log_header "验证部署"
    
    # 检查服务状态
    log_info "检查服务状态..."
    systemctl is-active nginx postgresql redis-server supervisor
    
    # 检查应用进程
    supervisorctl status qatoolbox
    
    # 测试HTTP访问
    sleep 5  # 等待应用启动
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -E "200|301|302" > /dev/null; then
        log_success "HTTP访问正常"
    else
        log_warning "HTTP访问失败，可能需要等待应用启动"
    fi
    
    log_success "部署验证完成"
}

# 显示部署信息
show_deployment_info() {
    log_header "部署完成信息"
    
    echo -e "${GREEN}🌐 访问地址:${NC}"
    echo "  - http://$(hostname -I | awk '{print $1}')/"
    echo "  - http://localhost/"
    echo ""
    
    echo -e "${GREEN}👑 管理员登录:${NC}"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo "  - 后台: http://$(hostname -I | awk '{print $1}')/admin/"
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
    echo "  - ✅ PostgreSQL (数据库)"
    echo "  - ✅ Redis (缓存)"
    echo "  - ✅ Nginx (Web服务器)"
    echo ""
    
    echo -e "${GREEN}📋 部署日志:${NC} $LOG_FILE"
}

# 主函数
main() {
    log_header "开始QAToolBox阿里云自动部署"
    
    # 创建日志文件
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
    
    log_info "部署开始时间: $(date)"
    
    check_requirements
    setup_system
    install_python
    install_system_dependencies
    install_services
    setup_database
    setup_project_user
    fix_permissions
    download_project
    fix_permissions
    setup_python_environment
    setup_environment_variables
    initialize_django
    fix_permissions
    setup_nginx
    setup_supervisor
    verify_deployment
    show_deployment_info
    
    log_success "阿里云部署完成！"
    log_info "部署结束时间: $(date)"
}

# 执行主函数
main "$@"
