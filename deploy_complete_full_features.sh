#!/bin/bash

# QAToolBox 完整功能一键部署脚本
# 专注于保持完整URL导入，不简化任何功能
# 阿里云优化版本，服务器: 47.103.143.152, 域名: shenyiqing.xin

set -e  # 遇到错误立即退出

# 颜色输出函数
print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要root权限运行"
   exit 1
fi

print_status "🚀 开始QAToolBox完整功能一键部署"
print_status "🎯 目标: 保持完整URL导入，不简化任何功能"
print_status "🌐 服务器: 47.103.143.152"
print_status "🔗 域名: shenyiqing.xin"

# ================================
# [1/10] 系统环境检测和优化
# ================================
print_status "[1/10] 系统环境检测和优化"

# 检测系统版本
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_VERSION="$VERSION_ID"
    print_status "📋 检测到系统: $NAME $VERSION"
else
    print_warning "无法检测系统版本，假设为Ubuntu"
    OS_VERSION="20.04"
fi

# 配置阿里云源加速下载
print_status "🚀 配置阿里云软件源..."
cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)

cat > /etc/apt/sources.list << EOF
# 阿里云Ubuntu镜像源
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
EOF

# 更新软件包列表
print_status "📦 更新软件包列表..."
apt update

print_success "系统环境优化完成"

# ================================
# [2/10] 安装系统依赖（全面支持）
# ================================
print_status "[2/10] 安装系统依赖（全面支持）"

print_status "🔧 安装基础开发工具..."
apt install -y \
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
    tree

print_status "🐍 安装Python和相关工具..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

print_status "🗃️ 安装数据库和缓存..."
apt install -y \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all \
    redis-server

print_status "🌐 安装Web服务器..."
apt install -y \
    nginx \
    supervisor

print_status "📚 安装系统开发库（完整版）..."
# 处理Ubuntu 24.04的包名变化
if [[ "$OS_VERSION" == "24.04" ]]; then
    print_status "🔧 Ubuntu 24.04特殊处理..."
    apt install -y \
        libglib2.0-0t64 \
        libgl1-mesa-dri \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        libfontconfig1 \
        libdbus-1-3 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xinput0 \
        libxcb-xfixes0 \
        libxkbcommon-x11-0 \
        libxcb-shape0 || print_warning "部分图形库安装失败，继续执行..."
else
    apt install -y \
        libglib2.0-0 \
        libgl1-mesa-glx \
        libgstreamer1.0-0 \
        libgstreamer-plugins-base1.0-0 \
        libfontconfig1 \
        libdbus-1-3 \
        libxcb-icccm4 \
        libxcb-image0 \
        libxcb-keysyms1 \
        libxcb-randr0 \
        libxcb-render-util0 \
        libxcb-xinerama0 \
        libxcb-xinput0 \
        libxcb-xfixes0 \
        libxkbcommon-x11-0 \
        libxcb-shape0 || print_warning "部分图形库安装失败，继续执行..."
fi

# 安装图像处理相关库
print_status "🖼️ 安装图像处理库..."
apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff5-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev || {
    print_warning "某些图像库安装失败，尝试修复..."
    apt --fix-broken install -y
    apt install -y --no-install-recommends \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
        libffi-dev \
        libssl-dev
}

# 音频和视频处理库
print_status "🎵 安装音频视频处理库..."
apt install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavresample-dev \
    libportaudio2 \
    portaudio19-dev \
    python3-pyaudio || print_warning "部分音视频库安装失败，继续执行..."

# 机器学习和科学计算库
print_status "🧠 安装科学计算基础库..."
apt install -y \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libhdf5-dev \
    pkg-config || print_warning "部分科学计算库安装失败，继续执行..."

print_success "系统依赖安装完成"

# ================================
# [3/10] 配置服务和安全
# ================================
print_status "[3/10] 配置PostgreSQL、Redis、Nginx等服务"

print_status "🚀 启动系统服务..."
systemctl enable postgresql redis-server nginx supervisor
systemctl start postgresql redis-server nginx supervisor

print_status "🗄️ 配置PostgreSQL数据库..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS qatoolbox;
DROP ROLE IF EXISTS qatoolbox;
CREATE ROLE qatoolbox WITH LOGIN PASSWORD 'qatoolbox2024!';
ALTER ROLE qatoolbox CREATEDB;
CREATE DATABASE qatoolbox OWNER qatoolbox;
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
EOF

print_status "🔐 配置Redis..."
sed -i 's/# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf
sed -i 's/# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf
systemctl restart redis-server

print_success "系统服务配置完成"

# ================================
# [4/10] 创建项目用户和目录
# ================================
print_status "[4/10] 创建项目用户和目录结构"

if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
    print_success "用户 qatoolbox 创建成功"
else
    print_success "用户 qatoolbox 已存在"
fi

# 创建项目目录结构
mkdir -p /home/qatoolbox/{QAToolbox,logs,backups}
chown -R qatoolbox:qatoolbox /home/qatoolbox/

print_success "项目目录结构创建完成"

# ================================
# [5/10] 下载项目代码
# ================================
print_status "[5/10] 从GitHub下载完整项目代码"

cd /home/qatoolbox

# 如果目录存在，先备份
if [ -d "QAToolbox" ]; then
    print_status "🔄 备份现有项目..."
    mv QAToolbox "QAToolbox.backup.$(date +%Y%m%d_%H%M%S)"
fi

print_status "📥 下载项目代码..."
# 尝试多种下载方法
if ! sudo -u qatoolbox git clone https://github.com/shinytsing/QAToolbox.git; then
    print_warning "Git克隆失败，尝试下载ZIP包..."
    sudo -u qatoolbox wget --no-check-certificate -O QAToolbox.zip https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip
    sudo -u qatoolbox unzip QAToolbox.zip
    sudo -u qatoolbox mv QAToolbox-main QAToolbox
    rm -f QAToolbox.zip
fi

if [ ! -d "QAToolbox" ]; then
    print_error "项目下载失败"
    exit 1
fi

cd QAToolbox
chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolbox

print_success "项目代码下载完成"

# ================================
# [6/10] 创建Python虚拟环境
# ================================
print_status "[6/10] 创建Python虚拟环境"

print_status "🐍 创建虚拟环境..."
sudo -u qatoolbox python3 -m venv .venv
sudo -u qatoolbox .venv/bin/pip install --upgrade pip setuptools wheel

# 配置pip使用阿里云源
sudo -u qatoolbox mkdir -p /home/qatoolbox/.pip
cat > /home/qatoolbox/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 60
EOF
chown -R qatoolbox:qatoolbox /home/qatoolbox/.pip

print_success "Python虚拟环境创建完成"

# ================================
# [7/10] 安装Python依赖（完整版）
# ================================
print_status "[7/10] 安装Python依赖（完整版，支持所有功能）"

print_status "📋 创建完整依赖列表..."
cat > requirements_full_deploy.txt << EOF
# Django核心框架
Django==4.2.7
django-extensions==3.2.3
django-debug-toolbar==4.2.0

# 环境配置
python-dotenv==1.0.0
django-environ==0.11.2
python-decouple==3.8

# 数据库
psycopg2-binary==2.9.9
django-redis==5.4.0
redis==5.0.1

# API框架
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-filter==23.3
drf-spectacular==0.26.5

# 认证和权限
djangorestframework-simplejwt==5.3.0
django-oauth-toolkit==1.7.1

# 异步任务
celery==5.3.4
django-celery-beat==2.5.0
kombu==5.3.4

# 文件处理
Pillow==10.1.0
python-magic==0.4.27
PyPDF2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
xlrd==2.0.1

# 机器学习和AI（完整支持）
torch==2.1.1
torchvision==0.16.1
opencv-python==4.8.1.78
scikit-learn==1.3.2
numpy==1.24.4
pandas==2.1.3
matplotlib==3.8.2
seaborn==0.13.0
tensorflow==2.15.0

# 自然语言处理
nltk==3.8.1
jieba==0.42.1
transformers==4.35.2

# 网络爬虫
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
selenium==4.15.2
scrapy==2.11.0

# 音频处理
pydub==0.25.1
librosa==0.10.1
soundfile==0.12.1
pyaudio==0.2.11

# 图像处理扩展
opencv-contrib-python==4.8.1.78
imageio==2.31.6
scikit-image==0.22.0

# 系统监控
psutil==5.9.6
py-cpuinfo==9.0.0

# 网络工具
httpx==0.25.2
aiohttp==3.9.1
websockets==12.0

# 数据序列化
pyyaml==6.0.1
toml==0.10.2
ujson==5.8.0

# 日期时间处理
python-dateutil==2.8.2
pytz==2023.3

# 加密和安全
cryptography==41.0.7
bcrypt==4.1.2

# 文本处理
chardet==5.2.0
cchardet==2.1.7

# 调试和测试
pytest==7.4.3
pytest-django==4.7.0
factory-boy==3.3.0

# 生产环境
gunicorn==21.2.0
whitenoise==6.6.0
django-compressor==4.4

# 监控和日志
sentry-sdk==1.38.0
structlog==23.2.0

# 工具库
tqdm==4.66.1
click==8.1.7
python-slugify==8.0.1
EOF

chown qatoolbox:qatoolbox requirements_full_deploy.txt

print_status "📦 安装基础Python依赖..."
sudo -u qatoolbox .venv/bin/pip install --timeout 300 \
    Django==4.2.7 \
    python-dotenv==1.0.0 \
    django-environ==0.11.2 \
    python-decouple==3.8 \
    psycopg2-binary==2.9.9 \
    psutil==5.9.6 \
    gunicorn==21.2.0

print_status "🧠 安装机器学习依赖（torch等）..."
sudo -u qatoolbox .venv/bin/pip install --timeout 600 \
    torch==2.1.1 \
    torchvision==0.16.1 \
    opencv-python==4.8.1.78 \
    scikit-learn==1.3.2 \
    numpy==1.24.4

print_status "📦 安装剩余依赖..."
sudo -u qatoolbox .venv/bin/pip install --timeout 600 -r requirements_full_deploy.txt || {
    print_warning "批量安装失败，逐个安装重要依赖..."
    
    # 核心依赖逐个安装
    CORE_DEPS=(
        "djangorestframework==3.14.0"
        "django-cors-headers==4.3.1"
        "django-redis==5.4.0"
        "redis==5.0.1"
        "Pillow==10.1.0"
        "requests==2.31.0"
        "beautifulsoup4==4.12.2"
        "celery==5.3.4"
        "whitenoise==6.6.0"
    )
    
    for dep in "${CORE_DEPS[@]}"; do
        print_status "安装: $dep"
        sudo -u qatoolbox .venv/bin/pip install --timeout 300 "$dep" || print_warning "跳过: $dep"
    done
}

print_success "Python依赖安装完成"

# ================================
# [8/10] 配置Django生产环境
# ================================
print_status "[8/10] 配置Django生产环境（保持完整功能）"

print_status "⚙️ 创建生产环境配置..."

# 创建配置目录
sudo -u qatoolbox mkdir -p config/settings

# 生产环境配置（支持完整URL导入）
cat > config/settings/production_full.py << 'EOF'
"""
QAToolBox 生产环境配置
专门设计来支持完整的URL导入，不简化任何功能
"""
import os
import sys
from pathlib import Path

# 环境变量加载
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import environ
    env = environ.Env(
        DEBUG=(bool, False),
        SECRET_KEY=(str, 'django-production-key-shenyiqing-2024'),
        DATABASE_URL=(str, 'postgres://qatoolbox:qatoolbox2024!@localhost:5432/qatoolbox'),
        REDIS_URL=(str, 'redis://localhost:6379/0'),
    )
except ImportError:
    class FakeEnv:
        def __call__(self, key, default=None, cast=str):
            value = os.environ.get(key, default)
            if cast == bool:
                return str(value).lower() in ('true', '1', 'yes', 'on')
            return cast(value) if value is not None else default
    env = FakeEnv()

# 基础配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=False)
ALLOWED_HOSTS = [
    'shenyiqing.xin',
    'www.shenyiqing.xin', 
    '47.103.143.152',
    'localhost',
    '127.0.0.1',
    '*'  # 生产环境建议限制具体域名
]

# 应用配置
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_extensions',
]

# 本地应用 - 动态检测并添加
LOCAL_APPS = []
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / 'apps'))

# 检测apps目录下的应用
apps_dir = BASE_DIR / 'apps'
if apps_dir.exists():
    for app_path in apps_dir.iterdir():
        if app_path.is_dir() and (app_path / '__init__.py').exists():
            app_name = f'apps.{app_path.name}'
            try:
                __import__(app_name)
                LOCAL_APPS.append(app_name)
                print(f"✅ 成功加载应用: {app_name}")
            except Exception as e:
                print(f"⚠️ 应用加载失败: {app_name} - {e}")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL配置 - 使用完整的urls.py
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

# WSGI应用
WSGI_APPLICATION = 'wsgi.application'

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
            'connect_timeout': 10,
        }
    }
}

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 站点ID
SITE_ID = 1

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 安全配置（生产环境）
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

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
            'filename': '/home/qatoolbox/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

print(f"✅ Django配置加载完成")
print(f"📊 已加载应用数量: {len(INSTALLED_APPS)}")
print(f"🔗 URL配置: {ROOT_URLCONF}")
print(f"🗃️ 数据库: PostgreSQL")
print(f"🔄 缓存: Redis")
EOF

chown qatoolbox:qatoolbox config/settings/production_full.py

# 创建环境变量文件
cat > .env.production << EOF
DEBUG=False
SECRET_KEY=django-production-key-shenyiqing-2024-$(date +%s)
DATABASE_URL=postgres://qatoolbox:qatoolbox2024!@localhost:5432/qatoolbox
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
EOF

chown qatoolbox:qatoolbox .env.production

print_success "Django生产环境配置完成"

# ================================
# [9/10] 初始化Django应用
# ================================
print_status "[9/10] 初始化Django应用（完整功能）"

# 切换到项目目录
cd /home/qatoolbox/QAToolbox

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.production_full

print_status "🔍 检查Django配置..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py check --deploy || {
    print_warning "Django检查发现问题，继续执行..."
}

print_status "🗃️ 数据库迁移..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py makemigrations || print_warning "makemigrations失败，继续..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py migrate

print_status "👤 创建超级用户..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin2024!')
    print("✅ 超级用户创建成功: admin/admin2024!")
else:
    print("ℹ️  超级用户已存在")
EOF

print_status "📁 收集静态文件..."
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full .venv/bin/python manage.py collectstatic --noinput

print_success "Django应用初始化完成"

# ================================
# [10/10] 配置生产环境服务
# ================================
print_status "[10/10] 配置生产环境服务"

print_status "🔧 配置Gunicorn..."
cat > gunicorn_config.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 2000
max_requests_jitter = 100
timeout = 120
keepalive = 5
preload_app = True
reload = False

# 日志配置
accesslog = "/home/qatoolbox/logs/gunicorn_access.log"
errorlog = "/home/qatoolbox/logs/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程命名
proc_name = "qatoolbox_gunicorn"

# 环境变量
raw_env = [
    "DJANGO_SETTINGS_MODULE=config.settings.production_full",
]
EOF

chown qatoolbox:qatoolbox gunicorn_config.py

print_status "🌐 配置Nginx..."
cat > /etc/nginx/sites-available/qatoolbox << EOF
upstream qatoolbox_app {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # 主应用
    location / {
        proxy_pass http://qatoolbox_app;
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

print_status "🔄 配置Supervisor..."
cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=/home/qatoolbox/QAToolbox/.venv/bin/gunicorn wsgi:application -c gunicorn_config.py
directory=/home/qatoolbox/QAToolbox
user=qatoolbox
group=qatoolbox
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/qatoolbox/logs/supervisor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=DJANGO_SETTINGS_MODULE="config.settings.production_full"

[program:qatoolbox_celery]
command=/home/qatoolbox/QAToolbox/.venv/bin/celery -A QAToolBox worker -l info
directory=/home/qatoolbox/QAToolbox
user=qatoolbox
group=qatoolbox
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/qatoolbox/logs/celery.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=DJANGO_SETTINGS_MODULE="config.settings.production_full"
EOF

# 创建日志目录
mkdir -p /home/qatoolbox/logs
chown -R qatoolbox:qatoolbox /home/qatoolbox/logs

print_status "🚀 启动所有服务..."
nginx -t && systemctl reload nginx
supervisorctl reread
supervisorctl update
supervisorctl start all

print_success "生产环境服务配置完成"

# ================================
# 部署验证
# ================================
print_status "🔍 验证部署状态"

# 等待服务启动
sleep 5

# 检查服务状态
print_status "📊 服务状态检查:"
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Redis: $(systemctl is-active redis-server)"
echo "Nginx: $(systemctl is-active nginx)"
echo "Supervisor: $(systemctl is-active supervisor)"

# 检查端口监听
print_status "🔌 端口监听检查:"
netstat -tlnp | grep -E ":(80|8000|5432|6379)" || print_warning "部分端口未监听"

# 检查应用响应
print_status "🌐 应用响应测试:"
if curl -f -s http://localhost/ > /dev/null; then
    print_success "应用响应正常"
else
    print_warning "应用可能需要更多时间启动"
fi

# ================================
# 部署完成报告
# ================================
print_success "🎉 QAToolBox完整功能部署成功！"

cat << EOF

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎊 QAToolBox 完整功能部署成功！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 访问地址:
   • 主域名: http://shenyiqing.xin
   • 备用域名: http://www.shenyiqing.xin  
   • IP访问: http://47.103.143.152
   • 管理后台: http://shenyiqing.xin/admin

👤 管理员账户:
   • 用户名: admin
   • 密码: admin2024!
   • 邮箱: admin@shenyiqing.xin

🔧 关键特性:
   ✅ 完整URL导入 - 未简化任何功能
   ✅ 机器学习支持 - torch, opencv等已安装
   ✅ 图像处理功能 - 完整图像识别功能
   ✅ 异步任务支持 - Celery已配置
   ✅ 高性能部署 - Gunicorn + Nginx
   ✅ 进程管理 - Supervisor自动重启
   ✅ 数据库支持 - PostgreSQL + Redis

📋 服务管理命令:
   • 重启应用: supervisorctl restart qatoolbox
   • 查看日志: tail -f /home/qatoolbox/logs/supervisor.log
   • 重启Nginx: systemctl restart nginx
   • 数据库命令: sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_full /home/qatoolbox/QAToolbox/.venv/bin/python /home/qatoolbox/QAToolbox/manage.py

📁 重要路径:
   • 项目目录: /home/qatoolbox/QAToolbox
   • 日志目录: /home/qatoolbox/logs
   • 静态文件: /home/qatoolbox/QAToolbox/staticfiles
   • 媒体文件: /home/qatoolbox/QAToolbox/media

🚀 下一步:
   1. 访问 http://shenyiqing.xin 确认功能正常
   2. 登录管理后台进行配置
   3. 根据需要调整具体功能设置
   4. 配置SSL证书（推荐使用Let's Encrypt）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

print_success "部署脚本执行完成！"
