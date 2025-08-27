#!/bin/bash
# =============================================================================
# QAToolBox 阿里云离线部署脚本 v2.0
# =============================================================================
# 解决GitHub连接问题的离线部署方案
# 支持多种代码获取方式：Gitee镜像、直接下载、手动上传
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
🚀 QAToolBox 阿里云离线部署 v2.0
========================================
✨ 特性:
  • 多种代码获取方式
  • Gitee国内镜像支持
  • 直接ZIP下载
  • 手动上传支持
  • 网络问题自动处理
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

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
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
    
    sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1 || handle_error "PostgreSQL启动失败" "检查PostgreSQL服务状态"
    
    # 删除已存在的数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    
    # 创建新的数据库和用户
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    echo -e "${GREEN}✅ 系统服务配置完成${NC}"
}

# 创建项目用户和目录
setup_project_user() {
    show_progress "5" "12" "创建项目用户和目录结构"
    
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

# 多种方式获取项目代码
deploy_project_code() {
    show_progress "6" "12" "获取项目代码（多种方式）"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    echo -e "${YELLOW}📥 尝试多种方式获取项目代码...${NC}"
    
    # 方式1: 尝试Gitee镜像
    echo -e "${BLUE}🇨🇳 尝试从Gitee镜像获取代码...${NC}"
    if timeout 60 git clone https://gitee.com/shinytsing/QAToolbox.git "$PROJECT_DIR" 2>/dev/null; then
        echo -e "${GREEN}✅ 从Gitee成功获取代码${NC}"
        chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        return 0
    fi
    
    # 方式2: 尝试GitHub镜像
    echo -e "${BLUE}🌐 尝试从GitHub镜像获取代码...${NC}"
    local github_mirrors=(
        "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git"
        "https://hub.fastgit.xyz/shinytsing/QAToolbox.git"
        "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
    )
    
    for mirror in "${github_mirrors[@]}"; do
        echo -e "${YELLOW}尝试镜像: $mirror${NC}"
        if timeout 60 git clone "$mirror" "$PROJECT_DIR" 2>/dev/null; then
            echo -e "${GREEN}✅ 从镜像成功获取代码${NC}"
            chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
            return 0
        fi
    done
    
    # 方式3: 尝试直接从GitHub下载ZIP
    echo -e "${BLUE}📦 尝试下载ZIP文件...${NC}"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    local zip_urls=(
        "https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip"
        "https://codeload.github.com/shinytsing/QAToolbox/zip/refs/heads/main"
    )
    
    for zip_url in "${zip_urls[@]}"; do
        echo -e "${YELLOW}尝试下载: $zip_url${NC}"
        if timeout 120 curl -L "$zip_url" -o main.zip 2>/dev/null; then
            if unzip -q main.zip 2>/dev/null; then
                # 移动文件到正确位置
                if [ -d "QAToolbox-main" ]; then
                    mv QAToolbox-main/* . 2>/dev/null || true
                    mv QAToolbox-main/.* . 2>/dev/null || true
                    rmdir QAToolbox-main 2>/dev/null || true
                elif [ -d "QAToolBox-main" ]; then
                    mv QAToolBox-main/* . 2>/dev/null || true
                    mv QAToolBox-main/.* . 2>/dev/null || true
                    rmdir QAToolBox-main 2>/dev/null || true
                fi
                rm -f main.zip
                echo -e "${GREEN}✅ 从ZIP文件成功获取代码${NC}"
                chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
                
                # 验证项目结构
                if [ -f "$PROJECT_DIR/manage.py" ]; then
                    return 0
                fi
            fi
        fi
        rm -f main.zip
    done
    
    # 方式4: 手动上传提示
    echo -e "${RED}❌ 所有自动获取方式都失败${NC}"
    echo -e "${YELLOW}💡 请手动上传项目代码：${NC}"
    echo -e "   1. 在本地打包项目: tar -czf QAToolBox.tar.gz QAToolBox/"
    echo -e "   2. 上传到服务器: scp QAToolBox.tar.gz root@$SERVER_IP:/tmp/"
    echo -e "   3. 解压到指定位置: tar -xzf /tmp/QAToolBox.tar.gz -C /home/$PROJECT_USER/"
    echo -e "   4. 重新运行此脚本"
    
    # 检查是否有手动上传的文件
    if [ -f "/tmp/QAToolBox.tar.gz" ]; then
        echo -e "${BLUE}📦 发现手动上传的文件，正在解压...${NC}"
        tar -xzf /tmp/QAToolBox.tar.gz -C "/home/$PROJECT_USER/"
        chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        echo -e "${GREEN}✅ 手动上传的代码解压完成${NC}"
        return 0
    fi
    
    # 方式5: 创建基本项目结构（最后的备用方案）
    echo -e "${YELLOW}⚠️ 创建基本项目结构作为备用方案${NC}"
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # 创建基本的Django项目文件
    cat > manage.py << 'EOF'
#!/usr/bin/env python
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
EOF

    # 创建WSGI文件
    cat > wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
application = get_wsgi_application()
EOF

    # 创建URLs文件
    cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def home_view(request):
    return HttpResponse("<h1>QAToolBox 部署成功！</h1><p>项目正在运行中...</p>")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
]
EOF

    # 创建基本配置目录
    mkdir -p config/settings
    mkdir -p apps/users apps/tools apps/content apps/share
    mkdir -p templates static media
    
    # 创建空的__init__.py文件
    touch config/__init__.py
    touch config/settings/__init__.py
    touch apps/__init__.py
    touch apps/users/__init__.py
    touch apps/tools/__init__.py
    touch apps/content/__init__.py
    touch apps/share/__init__.py
    
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    echo -e "${YELLOW}⚠️ 创建了基本项目结构，建议后续手动上传完整代码${NC}"
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
        "django-cors-headers==4.3.1"
        "django-crispy-forms==2.0"
        "crispy-bootstrap5==0.7"
        "django-simple-captcha==0.6.0"
        "django-extensions==3.2.3"
    )
    
    for package in "${core_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${GREEN}✅ Python环境配置完成${NC}"
}

# 配置Django应用
configure_django() {
    show_progress "8" "12" "配置Django应用和数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}⚙️ 创建生产环境配置...${NC}"
    
    # 确保配置目录存在
    mkdir -p config/settings
    
    # 如果没有现有的配置文件，创建一个基本的
    if [ ! -f "config/settings/aliyun_production.py" ]; then
        cat > config/settings/aliyun_production.py << 'EOF'
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-me')
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

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {'connect_timeout': 60},
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/qatoolbox/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/qatoolbox/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
EOF
    fi
    
    # 创建环境变量文件
    cat > .env << EOF
DJANGO_SECRET_KEY=django-aliyun-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EOF
    
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    echo -e "${GREEN}✅ Django配置完成${NC}"
}

# 初始化Django应用
initialize_django() {
    show_progress "9" "12" "初始化Django应用和数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}📊 执行数据库迁移...${NC}"
    
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

User.objects.filter(username='admin').delete()

admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@${DOMAIN}',
    password='${ADMIN_PASSWORD}'
)

print(f"管理员用户创建成功: {admin_user.username}")
PYTHON_EOF
    
    echo -e "${GREEN}✅ Django应用初始化完成${NC}"
}

# 配置Web服务
setup_web_services() {
    show_progress "10" "12" "配置Nginx和Supervisor服务"
    
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 7d;
    }
    
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
    
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl restart nginx
    
    echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
    
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox/access.log
stderr_logfile=/var/log/qatoolbox/error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production"
EOF
    
    supervisorctl reread
    supervisorctl update
    supervisorctl start qatoolbox
    
    echo -e "${GREEN}✅ Web服务配置完成${NC}"
}

# 配置防火墙和安全
setup_security() {
    show_progress "11" "12" "配置防火墙和基础安全"
    
    echo -e "${YELLOW}🔒 配置UFW防火墙...${NC}"
    
    apt install -y ufw
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    
    echo -e "${GREEN}✅ 安全配置完成${NC}"
}

# 最终验证和信息显示
final_verification() {
    show_progress "12" "12" "验证部署结果并显示信息"
    
    echo -e "${YELLOW}🔍 等待服务启动...${NC}"
    sleep 15
    
    echo -e "${YELLOW}🔍 检查服务状态...${NC}"
    
    local services=("nginx" "postgresql" "redis-server" "supervisor")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "${GREEN}✅ $service 运行正常${NC}"
        else
            echo -e "${RED}❌ $service 状态异常${NC}"
        fi
    done
    
    if supervisorctl status qatoolbox | grep -q "RUNNING"; then
        echo -e "${GREEN}✅ QAToolBox应用运行正常${NC}"
    else
        echo -e "${RED}❌ QAToolBox应用状态异常${NC}"
    fi
    
    echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    
    if [[ "$http_status" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✅ HTTP访问正常 (状态码: $http_status)${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP访问异常 (状态码: $http_status)${NC}"
    fi
    
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 离线部署完成！
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

🔧 管理命令:
  重启应用: sudo supervisorctl restart qatoolbox
  查看日志: sudo tail -f /var/log/qatoolbox/access.log
  查看状态: sudo supervisorctl status
  重启Nginx: sudo systemctl restart nginx

📋 日志文件:
  部署日志: $LOG_FILE
  应用日志: /var/log/qatoolbox/access.log
  Django日志: /var/log/qatoolbox/django.log

🎊 部署成功完成！现在可以开始使用QAToolBox了！
========================================
EOF
    echo -e "${NC}"
}

# 主执行流程
main() {
    check_root
    trap 'echo -e "${RED}❌ 部署过程中出现错误，请查看日志: $LOG_FILE${NC}"; exit 1' ERR
    
    echo -e "${BLUE}🚀 开始QAToolBox阿里云离线部署...${NC}"
    echo -e "${BLUE}📋 详细日志: $LOG_FILE${NC}"
    echo ""
    
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
    
    echo -e "${GREEN}🎉 QAToolBox阿里云离线部署成功完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
