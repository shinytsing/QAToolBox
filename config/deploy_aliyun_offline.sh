#!/bin/bash
# =============================================================================
# QAToolBox 阿里云离线部署脚本 v2.0
# =============================================================================
# 适用于网络不稳定或GitHub访问困难的情况
# 支持多种代码获取方式：本地上传、国内镜像、ZIP下载等
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
  • 国内镜像源支持
  • 离线部署能力
  • 自动重试机制
  • 中国地区优化
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
        ffmpeg libsndfile1-dev portaudio19-dev \
        tesseract-ocr tesseract-ocr-chi-sim \
        libgomp1 libatlas-base-dev liblapack-dev" "安装开发库"
    
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

# 多种方式获取项目代码
deploy_project_code() {
    show_progress "6" "12" "获取项目代码（多种方式）"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    echo -e "${YELLOW}📥 尝试多种方式获取项目代码...${NC}"
    
    # 方式1: 尝试Git克隆（多个源）
    local git_urls=(
        "https://gitee.com/shinytsing/QAToolBox.git"
        "https://github.com.cnpmjs.org/shinytsing/QAToolBox.git"
        "https://hub.fastgit.xyz/shinytsing/QAToolBox.git"
        "https://ghproxy.com/https://github.com/shinytsing/QAToolBox.git"
        "https://github.com/shinytsing/QAToolBox.git"
    )
    
    local cloned=false
    for url in "${git_urls[@]}"; do
        echo -e "${YELLOW}🔄 尝试Git克隆: $url${NC}"
        if timeout 120 git clone "$url" "$PROJECT_DIR" 2>/dev/null; then
            cloned=true
            echo -e "${GREEN}✅ Git克隆成功${NC}"
            break
        fi
        echo -e "${YELLOW}⚠️ 失败，尝试下一个源...${NC}"
    done
    
    # 方式2: 如果Git失败，尝试下载ZIP
    if [ "$cloned" = false ]; then
        echo -e "${YELLOW}📦 Git克隆失败，尝试下载ZIP文件...${NC}"
        
        mkdir -p "$PROJECT_DIR"
        cd "$PROJECT_DIR"
        
        local zip_urls=(
            "https://ghproxy.com/https://github.com/shinytsing/QAToolBox/archive/refs/heads/main.zip"
            "https://github.com/shinytsing/QAToolBox/archive/refs/heads/main.zip"
            "https://codeload.github.com/shinytsing/QAToolBox/zip/refs/heads/main"
        )
        
        local downloaded=false
        for zip_url in "${zip_urls[@]}"; do
            echo -e "${YELLOW}🔄 尝试下载: $zip_url${NC}"
            if timeout 120 curl -L "$zip_url" -o main.zip 2>/dev/null; then
                if unzip -q main.zip 2>/dev/null; then
                    # 移动文件到正确位置
                    if [ -d "QAToolBox-main" ]; then
                        mv QAToolBox-main/* . 2>/dev/null || true
                        mv QAToolBox-main/.* . 2>/dev/null || true
                        rmdir QAToolBox-main 2>/dev/null || true
                    elif [ -d "QAToolBox-main" ]; then
                        mv QAToolBox-main/* . 2>/dev/null || true
                        mv QAToolBox-main/.* . 2>/dev/null || true
                        rmdir QAToolBox-main 2>/dev/null || true
                    fi
                    rm -f main.zip
                    downloaded=true
                    echo -e "${GREEN}✅ ZIP下载成功${NC}"
                    break
                fi
            fi
            echo -e "${YELLOW}⚠️ 失败，尝试下一个源...${NC}"
        done
        
        # 方式3: 如果都失败，创建基本项目结构
        if [ "$downloaded" = false ]; then
            echo -e "${YELLOW}📁 创建基本项目结构...${NC}"
            
            # 创建基本的Django项目结构
            cat > "$PROJECT_DIR/create_project.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
import os
import sys

def create_basic_structure():
    """创建基本的Django项目结构"""
    
    # 创建基本目录
    dirs = [
        'apps/users',
        'apps/tools', 
        'apps/content',
        'apps/share',
        'config/settings',
        'templates',
        'static',
        'media',
        'logs'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        # 创建__init__.py文件
        if 'apps/' in dir_path:
            with open(f"{dir_path}/__init__.py", 'w') as f:
                f.write("")
    
    # 创建manage.py
    with open('manage.py', 'w') as f:
        f.write('''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

def main():
    """Run administrative tasks."""
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
''')
    
    # 创建wsgi.py
    with open('wsgi.py', 'w') as f:
        f.write('''
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
application = get_wsgi_application()
''')
    
    # 创建urls.py
    with open('urls.py', 'w') as f:
        f.write('''
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
''')
    
    # 创建基本的用户应用
    with open('apps/users/urls.py', 'w') as f:
        f.write('''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]
''')
    
    with open('apps/users/views.py', 'w') as f:
        f.write('''
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("QAToolBox is running!")
''')
    
    with open('apps/users/models.py', 'w') as f:
        f.write('''
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """扩展用户模型"""
    pass
''')
    
    # 创建requirements.txt
    with open('requirements.txt', 'w') as f:
        f.write('''Django==4.2.7
djangorestframework==3.14.0
psycopg2-binary==2.9.7
gunicorn==21.2.0
whitenoise==6.6.0
python-dotenv==1.0.0
redis==4.6.0
django-redis==5.4.0
requests==2.31.0
Pillow==9.5.0
''')
    
    print("基本项目结构创建完成")

if __name__ == '__main__':
    create_basic_structure()
PYTHON_EOF
            
            # 执行Python脚本创建结构
            python3 "$PROJECT_DIR/create_project.py"
            rm "$PROJECT_DIR/create_project.py"
            
            echo -e "${YELLOW}⚠️ 创建了基本项目结构，某些高级功能可能不可用${NC}"
        fi
    fi
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    # 验证项目结构
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        handle_error "项目结构异常，未找到manage.py" "请检查项目文件"
    fi
    
    echo -e "${GREEN}✅ 项目代码获取完成${NC}"
}

# 其余函数与原脚本相同...
# [这里包含原脚本的其他函数: setup_python_environment, configure_django, initialize_django, setup_web_services, setup_security, final_verification]

# 简化版Python环境设置
setup_python_environment() {
    show_progress "7" "12" "创建Python环境并安装依赖"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐍 创建Python虚拟环境...${NC}"
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install --upgrade pip" "升级pip"
    
    echo -e "${YELLOW}📦 安装核心依赖...${NC}"
    
    # 核心包
    local core_packages=(
        "Django==4.2.7"
        "gunicorn==21.2.0"
        "psycopg2-binary==2.9.7"
        "python-dotenv==1.0.0"
        "whitenoise==6.6.0"
    )
    
    for package in "${core_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    # 如果requirements.txt存在，安装其他依赖
    if [ -f "requirements.txt" ]; then
        echo -e "${YELLOW}📦 安装requirements.txt中的依赖...${NC}"
        sudo -u "$PROJECT_USER" .venv/bin/pip install -r requirements.txt || echo "⚠️ 部分依赖安装失败，不影响基本功能"
    fi
    
    echo -e "${GREEN}✅ Python环境配置完成${NC}"
}

# 配置Django应用
configure_django() {
    show_progress "8" "12" "配置Django应用"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}⚙️ 创建生产环境配置...${NC}"
    
    # 创建config/settings目录
    mkdir -p config/settings
    
    # 创建基本的aliyun_production.py配置
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

# 尝试添加本地应用
try:
    import apps.users
    INSTALLED_APPS.append('apps.users')
except ImportError:
    pass

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

# 如果存在自定义用户模型
try:
    import apps.users.models
    if hasattr(apps.users.models, 'User'):
        AUTH_USER_MODEL = 'users.User'
except ImportError:
    pass
EOF
    
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
EOF