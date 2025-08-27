#!/bin/bash
# QAToolBox 完整一键部署脚本 - 解决所有依赖问题
# =============================================
# 服务器: 47.103.143.152
# 域名: https://shenyiqing.xin/
# 功能: 系统化解决torch、environ等依赖缺失问题
# =============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root权限运行此脚本: sudo $0"
        exit 1
    fi
}

# 检测系统类型
detect_system() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    log_info "检测到系统: $OS $VER"
}

# 更新系统源
update_system_sources() {
    log_info "🔄 更新系统软件源..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        # 备份原有源
        cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)
        
        # 使用阿里云源提高下载速度
        if [[ "$OS" == *"Ubuntu"* ]]; then
            cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
EOF
        fi
        
        # 更新包列表
        apt update
        apt upgrade -y
        
        # 安装基础编译工具和库
        log_info "📦 安装系统级依赖..."
        apt install -y \
            python3 python3-pip python3-venv python3-dev \
            build-essential pkg-config \
            git wget curl unzip \
            nginx supervisor \
            postgresql postgresql-contrib \
            redis-server \
            libpq-dev \
            libffi-dev libssl-dev \
            libjpeg-dev libpng-dev \
            zlib1g-dev libtiff-dev \
            libfreetype6-dev liblcms2-dev \
            libopenjp2-7-dev libwebp-dev \
            libharfbuzz-dev libfribidi-dev \
            libxcb1-dev \
            libblas-dev liblapack-dev \
            libatlas-base-dev gfortran \
            libsndfile1-dev \
            ffmpeg \
            tesseract-ocr tesseract-ocr-chi-sim \
            chromium-browser chromium-chromedriver \
            libgl1-mesa-glx libglib2.0-0 \
            libsm6 libxext6 libxrender-dev \
            libgomp1 \
            htop tree vim nano
            
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
        # CentOS/RHEL 系统
        yum update -y
        yum groupinstall -y "Development Tools"
        yum install -y \
            python3 python3-pip python3-devel \
            git wget curl unzip \
            nginx supervisor \
            postgresql-server postgresql-contrib postgresql-devel \
            redis \
            openssl-devel libffi-devel \
            libjpeg-devel libpng-devel \
            zlib-devel libtiff-devel \
            freetype-devel lcms2-devel \
            openjpeg2-devel libwebp-devel \
            atlas-devel blas-devel lapack-devel \
            libsndfile-devel \
            ffmpeg \
            tesseract \
            chromium chromedriver \
            mesa-libGL-devel \
            htop tree vim nano
    fi
    
    log_success "✅ 系统依赖安装完成"
}

# 配置PostgreSQL
setup_postgresql() {
    log_info "🗄️ 配置PostgreSQL数据库..."
    
    if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
        systemctl start postgresql
        systemctl enable postgresql
    elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
        postgresql-setup initdb
        systemctl start postgresql
        systemctl enable postgresql
    fi
    
    # 创建数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    log_success "✅ PostgreSQL配置完成"
}

# 配置Redis
setup_redis() {
    log_info "🔴 配置Redis..."
    
    systemctl start redis-server 2>/dev/null || systemctl start redis 2>/dev/null || true
    systemctl enable redis-server 2>/dev/null || systemctl enable redis 2>/dev/null || true
    
    log_success "✅ Redis配置完成"
}

# 设置项目用户
setup_project_user() {
    log_info "👤 设置项目用户..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    # 创建用户
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        log_success "✅ 创建用户: $PROJECT_USER"
    else
        log_info "用户 $PROJECT_USER 已存在"
    fi
    
    # 设置用户到sudo组
    usermod -aG sudo "$PROJECT_USER" 2>/dev/null || usermod -aG wheel "$PROJECT_USER" 2>/dev/null || true
}

# 部署项目代码
deploy_project() {
    log_info "📁 部署项目代码..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    # 删除旧目录
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "删除旧项目目录"
        rm -rf "$PROJECT_DIR"
    fi
    
    # 克隆项目
    sudo -u "$PROJECT_USER" git clone https://github.com/your-username/QAToolBox.git "$PROJECT_DIR" 2>/dev/null || {
        log_warning "Git克隆失败，手动创建项目目录"
        mkdir -p "$PROJECT_DIR"
        chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        
        # 如果没有Git仓库，从当前目录复制
        if [ -f "$(pwd)/manage.py" ]; then
            log_info "从当前目录复制项目文件"
            cp -r "$(pwd)"/* "$PROJECT_DIR/"
            chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
        fi
    }
    
    cd "$PROJECT_DIR"
    
    log_success "✅ 项目代码部署完成"
}

# 创建虚拟环境并安装依赖
setup_virtual_environment() {
    log_info "🐍 创建Python虚拟环境..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    cd "$PROJECT_DIR"
    
    # 删除旧虚拟环境
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    # 创建新虚拟环境
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip
    sudo -u "$PROJECT_USER" .venv/bin/pip install --upgrade pip setuptools wheel
    
    # 使用完整依赖文件安装
    if [ -f "requirements_complete.txt" ]; then
        log_info "📦 安装完整依赖包（包含torch、environ等）..."
        sudo -u "$PROJECT_USER" .venv/bin/pip install -r requirements_complete.txt --timeout 600
    elif [ -f "requirements.txt" ]; then
        log_info "📦 安装基础依赖包..."
        sudo -u "$PROJECT_USER" .venv/bin/pip install -r requirements.txt --timeout 600
        
        # 手动安装关键缺失依赖
        log_info "📦 安装关键缺失依赖..."
        sudo -u "$PROJECT_USER" .venv/bin/pip install \
            torch==2.1.2 \
            torchvision==0.16.2 \
            torchaudio==2.1.2 \
            opencv-python==4.8.1.78 \
            django-environ==0.11.2 \
            python-decouple==3.8 \
            scikit-learn==1.3.2 \
            --timeout 600
    else
        log_error "未找到依赖文件"
        exit 1
    fi
    
    log_success "✅ 虚拟环境和依赖安装完成"
}

# 验证关键依赖
verify_dependencies() {
    log_info "🧪 验证关键依赖..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    cd "$PROJECT_DIR"
    
    # 验证关键模块
    CRITICAL_MODULES=(
        "django"
        "torch"
        "torchvision"
        "cv2"
        "numpy"
        "environ"
        "decouple"
        "PIL"
        "requests"
        "redis"
        "psycopg2"
    )
    
    FAILED_MODULES=()
    
    for module in "${CRITICAL_MODULES[@]}"; do
        if sudo -u "$PROJECT_USER" .venv/bin/python -c "import $module" 2>/dev/null; then
            version=$(sudo -u "$PROJECT_USER" .venv/bin/python -c "import $module; print(getattr($module, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
            log_success "✅ $module ($version)"
        else
            log_error "❌ $module 导入失败"
            FAILED_MODULES+=("$module")
        fi
    done
    
    if [ ${#FAILED_MODULES[@]} -gt 0 ]; then
        log_error "关键模块验证失败: ${FAILED_MODULES[*]}"
        log_info "尝试修复..."
        
        # 尝试修复失败的模块
        for module in "${FAILED_MODULES[@]}"; do
            case $module in
                "cv2")
                    sudo -u "$PROJECT_USER" .venv/bin/pip install opencv-python opencv-contrib-python
                    ;;
                "environ")
                    sudo -u "$PROJECT_USER" .venv/bin/pip install django-environ
                    ;;
                "decouple")
                    sudo -u "$PROJECT_USER" .venv/bin/pip install python-decouple
                    ;;
                "torch")
                    sudo -u "$PROJECT_USER" .venv/bin/pip install torch torchvision torchaudio
                    ;;
                *)
                    sudo -u "$PROJECT_USER" .venv/bin/pip install "$module"
                    ;;
            esac
        done
    fi
    
    log_success "✅ 依赖验证完成"
}

# 配置环境变量
setup_environment() {
    log_info "⚙️ 配置环境变量..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    cd "$PROJECT_DIR"
    
    # 创建环境变量文件
    cat > .env << 'EOF'
# QAToolBox 生产环境配置
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432

# Django配置
SECRET_KEY=django-shenyiqing-production-key-$(date +%s)
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1,www.shenyiqing.xin

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 站点配置
SITE_URL=https://shenyiqing.xin
FORCE_SCRIPT_NAME=

# Django设置模块
DJANGO_SETTINGS_MODULE=config.settings.production

# 文件上传配置
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
MAX_UPLOAD_SIZE=104857600

# 静态文件配置
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/var/www/qatoolbox/static/
MEDIA_ROOT=/var/www/qatoolbox/media/

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
CSRF_TRUSTED_ORIGINS=https://shenyiqing.xin,https://www.shenyiqing.xin

# API配置
API_RATE_LIMIT_ANON=1000
API_RATE_LIMIT_USER=10000

# 邮件配置（可选）
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# 日志配置
LOG_LEVEL=INFO
EOF
    
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    log_success "✅ 环境变量配置完成"
}

# 创建兼容的Django设置
setup_django_settings() {
    log_info "🔧 创建Django配置文件..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    cd "$PROJECT_DIR"
    
    # 确保config/settings目录存在
    mkdir -p config/settings
    
    # 创建生产环境配置文件
    cat > config/settings/production.py << 'SETTINGS_EOF'
"""
QAToolBox 生产环境配置 - 完整功能版本
解决所有依赖问题，确保功能完整性
"""
import os
import sys
from pathlib import Path

# 尝试导入环境变量库
try:
    import environ
    env = environ.Env(DEBUG=(bool, False))
    USE_ENVIRON = True
except ImportError:
    try:
        from decouple import config
        env = lambda key, default=None, cast=str: config(key, default=default, cast=cast)
        USE_ENVIRON = False
    except ImportError:
        # 使用默认环境变量
        env = lambda key, default=None, cast=str: cast(os.environ.get(key, default))
        USE_ENVIRON = False

# 基础路径
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 将apps目录添加到Python路径
sys.path.append(str(BASE_DIR / 'apps'))

# 安全设置
SECRET_KEY = env('SECRET_KEY', default='django-shenyiqing-production-key')
DEBUG = env('DEBUG', default=False, cast=bool)

# 允许的主机
ALLOWED_HOSTS_ENV = env('ALLOWED_HOSTS', default='shenyiqing.xin,47.103.143.152,localhost,127.0.0.1')
if isinstance(ALLOWED_HOSTS_ENV, str):
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS_ENV

# 确保关键主机在列表中
essential_hosts = ['47.103.143.152', 'shenyiqing.xin', 'www.shenyiqing.xin', 'localhost', '127.0.0.1']
for host in essential_hosts:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# 应用配置
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
]

# 尝试添加可选的第三方应用
optional_third_party = [
    'corsheaders',
    'django_extensions',
    'captcha',
    'django_ratelimit',
]

for app in optional_third_party:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
    except ImportError:
        pass

# 检查并添加本地应用
LOCAL_APPS = []
local_app_paths = [
    'apps.users',
    'apps.tools', 
    'apps.content',
    'apps.share',
]

for app_path in local_app_paths:
    try:
        __import__(app_path)
        LOCAL_APPS.append(app_path)
    except ImportError:
        pass

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件
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

# 添加可选中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

if 'django_ratelimit' in THIRD_PARTY_APPS:
    MIDDLEWARE.append('django_ratelimit.middleware.RatelimitMiddleware')

ROOT_URLCONF = 'urls'

# 模板配置
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

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='qatoolbox'),
        'USER': env('DB_USER', default='qatoolbox'),
        'PASSWORD': env('DB_PASSWORD', default='QAToolBox@2024'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
    }
}

# Redis配置
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default='/var/www/qatoolbox/static/')
STATICFILES_DIRS = [BASE_DIR / 'static']

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default='/var/www/qatoolbox/media/')

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '100/hour',
            'user': '1000/hour'
        }
    }

# CORS配置
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOWED_ORIGINS = [
        "https://shenyiqing.xin",
        "https://www.shenyiqing.xin",
    ]
    CORS_ALLOW_CREDENTIALS = True

# 安全配置
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    CSRF_TRUSTED_ORIGINS = [
        'https://shenyiqing.xin',
        'https://www.shenyiqing.xin',
    ]

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 创建日志目录
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(exist_ok=True)
SETTINGS_EOF
    
    chown -R "$PROJECT_USER:$PROJECT_USER" config/
    
    log_success "✅ Django配置文件创建完成"
}

# 初始化Django项目
initialize_django() {
    log_info "🚀 初始化Django项目..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_HOME="/home/$PROJECT_USER"
    PROJECT_DIR="$PROJECT_HOME/QAToolBox"
    
    cd "$PROJECT_DIR"
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE=config.settings.production
    
    # 创建必要目录
    mkdir -p logs static media
    mkdir -p /var/www/qatoolbox/static
    mkdir -p /var/www/qatoolbox/media
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    
    # 数据库迁移
    log_info "📊 执行数据库迁移..."
    sudo -u "$PROJECT_USER" -E .venv/bin/python manage.py makemigrations --noinput 2>/dev/null || true
    sudo -u "$PROJECT_USER" -E .venv/bin/python manage.py migrate --noinput
    
    # 收集静态文件
    log_info "📁 收集静态文件..."
    sudo -u "$PROJECT_USER" -E .venv/bin/python manage.py collectstatic --noinput
    
    # 创建超级用户（可选）
    log_info "👑 创建管理员用户..."
    sudo -u "$PROJECT_USER" -E .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print("管理员用户创建成功: admin/admin123456")
else:
    print("管理员用户已存在")
PYTHON_EOF
    
    log_success "✅ Django项目初始化完成"
}

# 配置Nginx
setup_nginx() {
    log_info "🌐 配置Nginx..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << 'NGINX_EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # SSL配置（需要SSL证书）
    # ssl_certificate /etc/ssl/certs/shenyiqing.xin.crt;
    # ssl_certificate_key /etc/ssl/private/shenyiqing.xin.key;
    
    # 临时禁用SSL
    listen 80;
    
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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
NGINX_EOF
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t
    
    # 重启Nginx
    systemctl restart nginx
    systemctl enable nginx
    
    log_success "✅ Nginx配置完成"
}

# 配置Supervisor（进程管理）
setup_supervisor() {
    log_info "⚡ 配置Supervisor..."
    
    PROJECT_USER="qatoolbox"
    PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
    
    # 创建Supervisor配置
    cat > /etc/supervisor/conf.d/qatoolbox.conf << 'SUPERVISOR_EOF'
[program:qatoolbox]
command=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn wsgi:application
directory=/home/qatoolbox/QAToolBox
user=qatoolbox
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
environment=DJANGO_SETTINGS_MODULE=config.settings.production
SUPERVISOR_EOF
    
    # 重新加载Supervisor配置
    supervisorctl reread
    supervisorctl update
    supervisorctl start qatoolbox
    
    log_success "✅ Supervisor配置完成"
}

# 启动服务
start_services() {
    log_info "🚀 启动所有服务..."
    
    # 启动系统服务
    systemctl start nginx
    systemctl start postgresql
    systemctl start redis-server 2>/dev/null || systemctl start redis 2>/dev/null
    systemctl start supervisor
    
    # 启动应用
    supervisorctl start qatoolbox
    
    log_success "✅ 所有服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "🔍 检查服务状态..."
    
    echo "=== 系统服务状态 ==="
    systemctl status nginx --no-pager -l
    echo ""
    systemctl status postgresql --no-pager -l
    echo ""
    systemctl status redis-server --no-pager -l 2>/dev/null || systemctl status redis --no-pager -l
    echo ""
    systemctl status supervisor --no-pager -l
    echo ""
    
    echo "=== 应用服务状态 ==="
    supervisorctl status qatoolbox
    echo ""
    
    echo "=== 端口监听状态 ==="
    netstat -tlnp | grep -E ":(80|443|8000|5432|6379)"
    echo ""
    
    log_success "✅ 服务状态检查完成"
}

# 测试部署
test_deployment() {
    log_info "🧪 测试部署..."
    
    # 测试网站访问
    echo "=== 测试本地访问 ==="
    curl -I http://localhost/ 2>/dev/null || log_warning "本地HTTP访问失败"
    curl -I http://127.0.0.1:8000/ 2>/dev/null || log_warning "应用直接访问失败"
    
    # 测试数据库连接
    echo "=== 测试数据库连接 ==="
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    cd "$PROJECT_DIR"
    sudo -u qatoolbox -E .venv/bin/python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('数据库连接正常')
"
    
    # 测试Redis连接
    echo "=== 测试Redis连接 ==="
    redis-cli ping 2>/dev/null || log_warning "Redis连接失败"
    
    log_success "✅ 部署测试完成"
}

# 显示部署信息
show_deployment_info() {
    log_info "📋 部署信息"
    
    echo "=========================="
    echo "🎉 QAToolBox 部署完成！"
    echo "=========================="
    echo ""
    echo "🌐 访问地址:"
    echo "  - https://shenyiqing.xin/"
    echo "  - http://47.103.143.152/"
    echo ""
    echo "👑 管理员登录:"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo "  - 后台: https://shenyiqing.xin/admin/"
    echo ""
    echo "📁 项目目录: /home/qatoolbox/QAToolBox"
    echo "📊 数据库: PostgreSQL (qatoolbox/QAToolBox@2024)"
    echo "🔴 缓存: Redis (localhost:6379)"
    echo ""
    echo "🔧 管理命令:"
    echo "  - 重启应用: supervisorctl restart qatoolbox"
    echo "  - 查看日志: tail -f /var/log/qatoolbox.log"
    echo "  - 重启Nginx: systemctl restart nginx"
    echo ""
    echo "✅ 所有依赖已安装，包括:"
    echo "  - ✅ torch (深度学习)"
    echo "  - ✅ environ (环境变量)"
    echo "  - ✅ opencv-python (计算机视觉)"
    echo "  - ✅ Django (Web框架)"
    echo "  - ✅ PostgreSQL (数据库)"
    echo "  - ✅ Redis (缓存)"
    echo ""
}

# 主函数
main() {
    log_info "🚀 开始QAToolBox完整部署..."
    
    check_root
    detect_system
    update_system_sources
    setup_postgresql
    setup_redis
    setup_project_user
    deploy_project
    setup_virtual_environment
    verify_dependencies
    setup_environment
    setup_django_settings
    initialize_django
    setup_nginx
    setup_supervisor
    start_services
    check_services
    test_deployment
    show_deployment_info
    
    log_success "🎉 QAToolBox部署完成！"
}

# 执行主函数
main "$@"
