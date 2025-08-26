#!/bin/bash

# QAToolBox 智能企业级部署脚本
# 包含重试机制、失败记录、手工安装指导
# 服务器: 47.103.143.152, 域名: shenyiqing.xin

set -e

# 全局变量
FAILED_PACKAGES=()
FAILED_COMMANDS=()
LOG_FILE="/var/log/qatoolbox_deploy.log"
RETRY_COUNT=3
DEPLOY_START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 颜色输出函数
print_status() {
    local msg="[$(date '+%H:%M:%S')] $1"
    echo -e "\033[1;34m$msg\033[0m"
    echo "$msg" >> "$LOG_FILE"
}

print_success() {
    local msg="✅ $1"
    echo -e "\033[1;32m$msg\033[0m"
    echo "$msg" >> "$LOG_FILE"
}

print_error() {
    local msg="❌ $1"
    echo -e "\033[1;31m$msg\033[0m"
    echo "$msg" >> "$LOG_FILE"
}

print_warning() {
    local msg="⚠️  $1"
    echo -e "\033[1;33m$msg\033[0m"
    echo "$msg" >> "$LOG_FILE"
}

print_header() {
    local msg="$1"
    echo -e "\033[1;35m"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$msg"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "\033[0m"
    echo "$msg" >> "$LOG_FILE"
}

# 智能重试函数
retry_command() {
    local cmd="$1"
    local description="$2"
    local max_retries=${3:-$RETRY_COUNT}
    
    for ((i=1; i<=max_retries; i++)); do
        print_status "执行: $description (尝试 $i/$max_retries)"
        if eval "$cmd"; then
            print_success "$description 成功"
            return 0
        else
            print_warning "$description 失败 (尝试 $i/$max_retries)"
            if [ $i -eq $max_retries ]; then
                print_error "$description 最终失败，已记录"
                FAILED_COMMANDS+=("$description: $cmd")
                return 1
            fi
            sleep 2
        fi
    done
}

# 智能包安装函数
install_packages() {
    local packages=("$@")
    local success_packages=()
    local failed_packages=()
    
    print_status "安装包: ${packages[*]}"
    
    # 先尝试批量安装
    if apt install -y "${packages[@]}" 2>/dev/null; then
        print_success "批量安装成功: ${packages[*]}"
        return 0
    fi
    
    print_warning "批量安装失败，逐个尝试..."
    
    # 逐个安装包
    for package in "${packages[@]}"; do
        local installed=false
        for ((i=1; i<=RETRY_COUNT; i++)); do
            print_status "安装 $package (尝试 $i/$RETRY_COUNT)"
            if apt install -y "$package" 2>/dev/null; then
                print_success "$package 安装成功"
                success_packages+=("$package")
                installed=true
                break
            else
                print_warning "$package 安装失败 (尝试 $i/$RETRY_COUNT)"
                sleep 1
            fi
        done
        
        if [ "$installed" = false ]; then
            print_error "$package 最终安装失败"
            failed_packages+=("$package")
            FAILED_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#failed_packages[@]} -gt 0 ]; then
        print_warning "部分包安装失败: ${failed_packages[*]}"
        return 1
    fi
    
    return 0
}

# 智能pip安装函数
pip_install_smart() {
    local packages=("$@")
    local user="qatoolbox"
    local pip_cmd=".venv/bin/pip"
    local success_packages=()
    local failed_packages=()
    
    print_status "安装Python包: ${packages[*]}"
    
    # 逐个安装Python包
    for package in "${packages[@]}"; do
        local installed=false
        for ((i=1; i<=RETRY_COUNT; i++)); do
            print_status "安装Python包 $package (尝试 $i/$RETRY_COUNT)"
            if sudo -u "$user" $pip_cmd install --timeout 300 "$package"; then
                print_success "Python包 $package 安装成功"
                success_packages+=("$package")
                installed=true
                break
            else
                print_warning "Python包 $package 安装失败 (尝试 $i/$RETRY_COUNT)"
                sleep 2
            fi
        done
        
        if [ "$installed" = false ]; then
            print_error "Python包 $package 最终安装失败"
            failed_packages+=("$package")
            FAILED_PACKAGES+=("$package")
        fi
    done
    
    if [ ${#failed_packages[@]} -gt 0 ]; then
        print_warning "部分Python包安装失败: ${failed_packages[*]}"
        return 1
    fi
    
    return 0
}

# 生成失败报告
generate_failure_report() {
    local report_file="/home/qatoolbox/deployment_failures.txt"
    
    cat > "$report_file" << EOF
QAToolBox 部署失败报告
生成时间: $(date '+%Y-%m-%d %H:%M:%S')
部署开始时间: $DEPLOY_START_TIME
═══════════════════════════════════════════════════════════════

失败的系统包 (${#FAILED_PACKAGES[@]} 个):
$(printf '%s\n' "${FAILED_PACKAGES[@]}")

失败的命令 (${#FAILED_COMMANDS[@]} 个):
$(printf '%s\n' "${FAILED_COMMANDS[@]}")

═══════════════════════════════════════════════════════════════
手工修复指导:

1. 系统包手工安装:
$(for pkg in "${FAILED_PACKAGES[@]}"; do
    echo "   sudo apt install -y $pkg"
done)

2. Python包手工安装:
   cd /home/qatoolbox/QAToolbox
$(for pkg in "${FAILED_PACKAGES[@]}"; do
    if [[ $pkg == *"=="* ]]; then
        echo "   sudo -u qatoolbox .venv/bin/pip install $pkg"
    fi
done)

3. 检查服务状态:
   sudo systemctl status nginx postgresql redis-server supervisor

4. 查看详细日志:
   tail -f $LOG_FILE
   tail -f /var/log/qatoolbox/supervisor.log

5. 重启部署:
   curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/enterprise_smart_deploy.sh | sudo bash

═══════════════════════════════════════════════════════════════
EOF

    chown qatoolbox:qatoolbox "$report_file"
    print_warning "失败报告已生成: $report_file"
}

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要root权限运行"
   exit 1
fi

# 创建日志文件
mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

print_header "🚀 QAToolBox 智能企业级部署开始"
print_status "🎯 目标: 智能重试 + 失败记录 + 手工指导"
print_status "📝 日志文件: $LOG_FILE"

# ================================
# [1/12] 系统环境检测和优化
# ================================
print_header "[1/12] 系统环境检测和优化"

# 检测系统版本
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_VERSION="$VERSION_ID"
    print_status "📋 检测到系统: $NAME $VERSION"
else
    print_warning "无法检测系统版本，假设为Ubuntu"
    OS_VERSION="20.04"
fi

# 配置阿里云源
print_status "🚀 配置阿里云软件源..."
cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)

cat > /etc/apt/sources.list << EOF
# 阿里云Ubuntu镜像源
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
EOF

retry_command "apt update && apt upgrade -y" "更新软件包列表"

print_success "系统环境优化完成"

# ================================
# [2/12] 安装系统依赖（智能重试版）
# ================================
print_header "[2/12] 安装系统依赖（智能重试版）"

# 基础开发工具
print_status "🔧 安装基础开发工具..."
install_packages \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    gnupg \
    lsb-release \
    build-essential \
    git \
    unzip \
    vim \
    htop \
    tree \
    tmux \
    screen \
    rsync \
    fail2ban \
    ufw

# Python生态系统（智能处理）
print_status "🐍 安装Python生态系统..."
python_packages=(
    "python3"
    "python3-pip" 
    "python3-venv"
    "python3-dev"
    "python3-setuptools"
    "python3-wheel"
)

# Ubuntu 24.04特殊处理
if [[ "$OS_VERSION" == "24.04" ]]; then
    python_packages+=("python3-setuptools-whl")
else
    python_packages+=("python3-distutils")
fi

install_packages "${python_packages[@]}"

# 数据库和缓存
print_status "🗃️ 安装数据库和缓存..."
install_packages \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    postgresql-client \
    redis-server \
    redis-tools

# Web服务器
print_status "🌐 安装Web服务器..."
install_packages \
    nginx \
    nginx-extras \
    supervisor \
    certbot \
    python3-certbot-nginx

# 开发库（分批安装）
print_status "📚 安装开发库（分批处理）..."

# 基础开发库
basic_dev_libs=(
    "libjpeg-dev"
    "libpng-dev"
    "libwebp-dev"
    "zlib1g-dev"
    "libffi-dev"
    "libssl-dev"
    "libxml2-dev"
    "libxslt1-dev"
)
install_packages "${basic_dev_libs[@]}"

# 图像处理库
image_libs=(
    "libfreetype6-dev"
    "libcairo2-dev"
    "libpango1.0-dev"
    "libgdk-pixbuf2.0-dev"
)
install_packages "${image_libs[@]}"

# 科学计算库
science_libs=(
    "libatlas-base-dev"
    "liblapack-dev"
    "libblas-dev"
    "libhdf5-dev"
    "pkg-config"
)
install_packages "${science_libs[@]}"

# 音视频库（容错处理）
print_status "🎵 安装音视频处理库（容错模式）..."
media_libs=(
    "ffmpeg"
    "libavcodec-dev"
    "libavformat-dev"
    "libswscale-dev"
    "libportaudio2"
    "portaudio19-dev"
)
install_packages "${media_libs[@]}"

print_success "系统依赖安装完成"

# ================================
# [3/12] 配置安全
# ================================
print_header "[3/12] 配置系统安全"

retry_command "ufw --force enable && ufw allow ssh && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 8000/tcp && ufw reload" "配置防火墙"
retry_command "systemctl enable fail2ban && systemctl start fail2ban" "配置fail2ban"

print_success "系统安全配置完成"

# ================================
# [4/12] 配置数据库
# ================================
print_header "[4/12] 配置PostgreSQL和Redis"

retry_command "systemctl enable postgresql redis-server && systemctl start postgresql redis-server" "启动数据库服务"

# 配置PostgreSQL
print_status "🗄️ 配置PostgreSQL数据库..."
sudo -u postgres psql << 'EOF' || {
    print_error "PostgreSQL配置失败"
    FAILED_COMMANDS+=("PostgreSQL数据库配置")
}
DROP DATABASE IF EXISTS qatoolbox;
DROP ROLE IF EXISTS qatoolbox;
CREATE ROLE qatoolbox WITH LOGIN PASSWORD 'qatoolbox2024!';
ALTER ROLE qatoolbox CREATEDB;
CREATE DATABASE qatoolbox OWNER qatoolbox;
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
\c qatoolbox;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF

# 配置Redis
print_status "🔐 配置Redis..."
cp /etc/redis/redis.conf /etc/redis/redis.conf.backup
sed -i 's/# maxmemory <bytes>/maxmemory 512mb/' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
retry_command "systemctl restart redis-server" "重启Redis"

print_success "数据库配置完成"

# ================================
# [5/12] 创建用户和目录
# ================================
print_header "[5/12] 创建项目用户和目录"

if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
    usermod -aG www-data qatoolbox
    print_success "用户 qatoolbox 创建成功"
else
    print_success "用户 qatoolbox 已存在"
fi

mkdir -p /home/qatoolbox/{QAToolbox,logs,backups,uploads,static,media}
mkdir -p /var/log/qatoolbox
mkdir -p /etc/qatoolbox
chown -R qatoolbox:qatoolbox /home/qatoolbox/
chown -R qatoolbox:qatoolbox /var/log/qatoolbox/

print_success "项目目录结构创建完成"

# ================================
# [6/12] 下载项目代码
# ================================
print_header "[6/12] 下载项目代码"

cd /home/qatoolbox

if [ -d "QAToolbox" ]; then
    print_status "🔄 备份现有项目..."
    mv QAToolbox "QAToolbox.backup.$(date +%Y%m%d_%H%M%S)"
fi

print_status "📥 下载项目代码..."
if ! retry_command "sudo -u qatoolbox git clone https://github.com/shinytsing/QAToolbox.git" "Git克隆项目"; then
    print_warning "Git克隆失败，尝试下载ZIP包..."
    retry_command "sudo -u qatoolbox wget --timeout=30 --tries=3 -O QAToolbox.zip https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip" "下载ZIP包"
    sudo -u qatoolbox unzip -q QAToolbox.zip
    sudo -u qatoolbox mv QAToolbox-main QAToolbox
    rm -f QAToolbox.zip
fi

if [ ! -d "QAToolbox" ]; then
    print_error "项目下载失败"
    generate_failure_report
    exit 1
fi

cd QAToolbox
chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolbox

print_success "项目代码下载完成"

# ================================
# [7/12] Python环境
# ================================
print_header "[7/12] 创建Python虚拟环境"

retry_command "sudo -u qatoolbox python3 -m venv .venv" "创建虚拟环境"
retry_command "sudo -u qatoolbox .venv/bin/pip install --upgrade pip setuptools wheel" "升级pip工具"

# 配置pip源
sudo -u qatoolbox mkdir -p /home/qatoolbox/.pip
cat > /home/qatoolbox/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 3
EOF
chown -R qatoolbox:qatoolbox /home/qatoolbox/.pip

print_success "Python虚拟环境创建完成"

# ================================
# [8/12] 安装Python依赖（智能重试）
# ================================
print_header "[8/12] 安装Python依赖（智能重试）"

# 核心依赖包列表
core_packages=(
    "Django==4.2.7"
    "python-dotenv==1.0.0"
    "django-environ==0.11.2"
    "psycopg2-binary==2.9.9"
    "psutil==5.9.6"
    "gunicorn==21.2.0"
    "whitenoise==6.6.0"
)

api_packages=(
    "djangorestframework==3.14.0"
    "django-cors-headers==4.3.1"
    "django-redis==5.4.0"
    "redis==5.0.1"
    "django-extensions==3.2.3"
)

websocket_packages=(
    "channels==4.0.0"
    "channels-redis==4.1.0"
    "daphne==4.0.0"
    "asgiref==3.7.2"
)

ml_packages=(
    "torch==2.1.1"
    "torchvision==0.16.1"
    "opencv-python==4.8.1.78"
    "scikit-learn==1.3.2"
    "numpy==1.24.4"
)

utility_packages=(
    "Pillow==10.1.0"
    "PyPDF2==3.0.1"
    "PyMuPDF==1.23.14"
    "requests==2.31.0"
    "beautifulsoup4==4.12.2"
    "ratelimit==2.2.1"
    "celery==5.3.4"
)

# 分阶段安装
print_status "🔧 第一阶段：核心依赖..."
pip_install_smart "${core_packages[@]}"

print_status "🌐 第二阶段：API框架..."
pip_install_smart "${api_packages[@]}"

print_status "🔄 第三阶段：WebSocket支持..."
pip_install_smart "${websocket_packages[@]}"

print_status "🧠 第四阶段：机器学习..."
pip_install_smart "${ml_packages[@]}"

print_status "🛠️ 第五阶段：工具库..."
pip_install_smart "${utility_packages[@]}"

print_success "Python依赖安装阶段完成"

# ================================
# [9/12] Django配置
# ================================
print_header "[9/12] 配置Django生产环境"

sudo -u qatoolbox mkdir -p config/settings

# 创建企业级配置（容错版本）
cat > config/settings/production_smart.py << 'EOF'
"""
QAToolBox 智能生产环境配置
包含容错处理和智能应用加载
"""
import os
import sys
from pathlib import Path

# 环境变量加载（容错）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv未安装，跳过.env文件加载")

try:
    import environ
    env = environ.Env(DEBUG=(bool, False))
except ImportError:
    print("⚠️ django-environ未安装，使用基础环境变量")
    class FakeEnv:
        def __call__(self, key, default=None, cast=str):
            value = os.environ.get(key, default)
            if cast == bool:
                return str(value).lower() in ('true', '1', 'yes', 'on')
            return cast(value) if value is not None else default
    env = FakeEnv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY', default='django-smart-key-shenyiqing-2024')
DEBUG = env('DEBUG', default=False)
ALLOWED_HOSTS = ['*']

# Django核心应用
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

# 第三方应用（智能加载）
THIRD_PARTY_APPS = []

# 检查并添加第三方应用
third_party_candidates = [
    'rest_framework',
    'corsheaders', 
    'channels',
    'django_extensions',
]

for app in third_party_candidates:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
        print(f"✅ 第三方应用加载: {app}")
    except ImportError:
        print(f"⚠️ 第三方应用跳过: {app}")

# 本地应用（智能加载）
LOCAL_APPS = []
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'apps'))

apps_dir = BASE_DIR / 'apps'
if apps_dir.exists():
    for app_path in apps_dir.iterdir():
        if app_path.is_dir() and (app_path / '__init__.py').exists():
            app_name = f'apps.{app_path.name}'
            try:
                __import__(app_name)
                LOCAL_APPS.append(app_name)
                print(f"✅ 本地应用加载: {app_name}")
            except Exception as e:
                print(f"⚠️ 本地应用加载警告: {app_name} - {str(e)[:100]}")
                # 仍然添加到列表中，在运行时处理
                LOCAL_APPS.append(app_name)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

# 智能添加CORS中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

MIDDLEWARE.extend([
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])

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

# 智能ASGI配置
if 'channels' in THIRD_PARTY_APPS:
    ASGI_APPLICATION = 'asgi.application'

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'qatoolbox2024!',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 20,
        },
        'CONN_MAX_AGE': 60,
    }
}

# 缓存配置（智能）
try:
    import redis
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://localhost:6379/0',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
except ImportError:
    print("⚠️ Redis缓存不可用，使用本地缓存")
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Channels配置（智能）
if 'channels' in THIRD_PARTY_APPS:
    try:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [('localhost', 6379)],
                },
            },
        }
    except:
        print("⚠️ Channels Redis不可用，使用内存层")
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer'
            }
        }

# 基础配置
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1

# REST Framework配置（智能）
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
        'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
    }

# CORS配置（智能）
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOW_ALL_ORIGINS = True

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

print(f"✅ 智能Django配置加载完成")
print(f"📊 应用数量: {len(INSTALLED_APPS)}")
print(f"🔗 URL配置: {ROOT_URLCONF}")
print(f"🗃️ 数据库: PostgreSQL")
print(f"🔄 缓存: {'Redis' if 'redis' in str(CACHES) else 'Local'}")
print(f"🌐 WebSocket: {'Channels' if 'channels' in THIRD_PARTY_APPS else '未启用'}")
EOF

chown qatoolbox:qatoolbox config/settings/production_smart.py

# 创建环境变量文件
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=django-smart-key-shenyiqing-2024-$(date +%s)
DATABASE_URL=postgres://qatoolbox:qatoolbox2024!@localhost:5432/qatoolbox
REDIS_URL=redis://localhost:6379/0
EOF
chown qatoolbox:qatoolbox .env.production

print_success "Django智能配置完成"

# ================================
# [10/12] Django初始化（容错版）
# ================================
print_header "[10/12] Django应用初始化（容错版）"

cd /home/qatoolbox/QAToolbox
export DJANGO_SETTINGS_MODULE=config.settings.production_smart

# Django检查（容错）
print_status "🔍 检查Django配置..."
if ! sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_smart .venv/bin/python manage.py check; then
    print_warning "Django检查发现问题，但继续执行..."
    FAILED_COMMANDS+=("Django配置检查")
fi

# 数据库迁移（容错）
print_status "🗃️ 数据库迁移..."
if ! sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_smart .venv/bin/python manage.py makemigrations; then
    print_warning "makemigrations失败，继续migrate..."
    FAILED_COMMANDS+=("Django makemigrations")
fi

if ! sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_smart .venv/bin/python manage.py migrate; then
    print_error "数据库迁移失败"
    FAILED_COMMANDS+=("Django migrate")
fi

# 创建超级用户（容错）
print_status "👤 创建超级用户..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_smart .venv/bin/python manage.py shell << 'EOF' || {
    print_warning "超级用户创建可能失败"
    FAILED_COMMANDS+=("创建超级用户")
}
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin2024!')
        print("✅ 超级用户创建成功: admin/admin2024!")
    else:
        print("✅ 超级用户已存在")
except Exception as e:
    print(f"⚠️ 超级用户创建失败: {e}")
EOF

# 收集静态文件（容错）
print_status "📁 收集静态文件..."
if ! sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_smart .venv/bin/python manage.py collectstatic --noinput; then
    print_warning "静态文件收集失败"
    FAILED_COMMANDS+=("收集静态文件")
fi

print_success "Django初始化完成（可能有部分失败）"

# ================================
# [11/12] 配置服务
# ================================
print_header "[11/12] 配置生产环境服务"

# Gunicorn配置
cat > gunicorn_smart.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
timeout = 120
keepalive = 5
preload_app = True

accesslog = "/var/log/qatoolbox/gunicorn_access.log"
errorlog = "/var/log/qatoolbox/gunicorn_error.log"
loglevel = "info"

proc_name = "qatoolbox_smart"

raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings.production_smart",
]
EOF
chown qatoolbox:qatoolbox gunicorn_smart.py

# Nginx配置
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
upstream qatoolbox_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 1y;
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 1y;
    }
    
    location / {
        proxy_pass http://qatoolbox_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Supervisor配置
cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=/home/qatoolbox/QAToolbox/.venv/bin/gunicorn wsgi:application -c gunicorn_smart.py
directory=/home/qatoolbox/QAToolbox
user=qatoolbox
group=qatoolbox
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=DJANGO_SETTINGS_MODULE="config.settings.production_smart"
EOF

print_success "服务配置完成"

# ================================
# [12/12] 启动和验证
# ================================
print_header "[12/12] 启动和验证服务"

# 启动服务（容错）
retry_command "nginx -t" "Nginx配置测试"
retry_command "systemctl reload nginx" "重载Nginx"
retry_command "supervisorctl reread && supervisorctl update" "更新Supervisor"
retry_command "supervisorctl restart all" "重启Supervisor服务"

sleep 10

# 验证服务
print_status "🔍 验证部署状态..."
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Redis: $(systemctl is-active redis-server)" 
echo "Nginx: $(systemctl is-active nginx)"
echo "Supervisor: $(systemctl is-active supervisor)"

supervisorctl status

# 测试应用响应
if curl -f -s http://localhost/ > /dev/null; then
    print_success "🎉 应用响应正常！"
else
    print_warning "应用可能需要更多时间启动"
    FAILED_COMMANDS+=("应用响应测试")
fi

# ================================
# 生成部署报告
# ================================
print_header "📋 生成部署报告"

if [ ${#FAILED_PACKAGES[@]} -gt 0 ] || [ ${#FAILED_COMMANDS[@]} -gt 0 ]; then
    generate_failure_report
    print_warning "部署完成，但有部分失败项目，请查看失败报告"
else
    print_success "🎊 完美部署！所有组件成功安装！"
fi

# 最终报告
cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 QAToolBox 智能企业级部署完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 访问地址:
   • 主站: http://shenyiqing.xin
   • IP访问: http://47.103.143.152  
   • 管理后台: http://shenyiqing.xin/admin

👤 管理员账户:
   • 用户名: admin
   • 密码: admin2024!

📊 部署统计:
   • 失败包数量: ${#FAILED_PACKAGES[@]}
   • 失败命令数量: ${#FAILED_COMMANDS[@]}
   • 部署开始时间: $DEPLOY_START_TIME
   • 部署结束时间: $(date '+%Y-%m-%d %H:%M:%S')

📝 重要文件:
   • 部署日志: $LOG_FILE
   • 失败报告: /home/qatoolbox/deployment_failures.txt
   • 应用日志: /var/log/qatoolbox/supervisor.log

🔧 智能特性:
   ✅ 3次重试机制
   ✅ 失败自动记录
   ✅ 手工修复指导
   ✅ 容错配置加载
   ✅ 智能应用检测

📋 下一步:
   1. 检查失败报告并手工修复
   2. 访问网站验证功能
   3. 配置SSL证书
   4. 设置监控告警

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

print_success "智能部署脚本执行完成！"
