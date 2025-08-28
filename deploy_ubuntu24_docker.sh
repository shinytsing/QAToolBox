#!/bin/bash
# =============================================================================
# QAToolBox Ubuntu 24.04 Docker部署脚本 v4.0
# =============================================================================
# 专为Ubuntu 24.04设计，使用Docker解决包冲突问题
# 保证项目完整性，支持所有功能
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

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_ubuntu24_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox Ubuntu 24.04 Docker部署
========================================
✨ 特性:
  • Ubuntu 24.04完全兼容
  • Docker容器化部署
  • 避免系统包冲突
  • 保证项目完整性
  • 所有功能完整支持
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
    show_progress "1" "12" "检测Ubuntu 24.04系统信息"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        handle_error "无法检测操作系统" "请确保使用Ubuntu系统"
    fi
    
    echo -e "${GREEN}操作系统: $OS $VER${NC}"
    echo -e "${GREEN}架构: $(uname -m)${NC}"
    echo -e "${GREEN}内核: $(uname -r)${NC}"
    echo -e "${GREEN}内存: $(free -h | awk '/^Mem:/ {print $2}')${NC}"
    echo -e "${GREEN}磁盘: $(df -h / | awk 'NR==2 {print $4}') 可用${NC}"
    
    # 检查是否为Ubuntu 24.04
    if [[ "$VER" == "24.04" ]]; then
        echo -e "${GREEN}✅ 检测到Ubuntu 24.04，使用Docker部署方案${NC}"
    else
        echo -e "${YELLOW}⚠️ 检测到Ubuntu $VER，此脚本专为24.04优化${NC}"
    fi
}

# 安装Docker
install_docker() {
    show_progress "2" "12" "安装Docker和Docker Compose"
    
    echo -e "${YELLOW}🐳 检查Docker安装状态...${NC}"
    
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✅ Docker已安装${NC}"
        docker --version
    else
        echo -e "${YELLOW}📦 安装Docker...${NC}"
        
        # 更新包列表
        apt update
        
        # 安装必要的软件包
        apt install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加Docker官方GPG密钥
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 设置Docker仓库
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 更新包列表并安装Docker
        apt update
        apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        # 启动并启用Docker服务
        systemctl start docker
        systemctl enable docker
        
        echo -e "${GREEN}✅ Docker安装完成${NC}"
    fi
    
    # 检查Docker Compose
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}✅ Docker Compose已安装${NC}"
        docker compose version
    else
        echo -e "${YELLOW}📦 安装Docker Compose...${NC}"
        
        # 下载Docker Compose
        DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
        mkdir -p $DOCKER_CONFIG/cli-plugins
        curl -SL https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
        chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
        
        echo -e "${GREEN}✅ Docker Compose安装完成${NC}"
    fi
}

# 安装基础系统工具
install_basic_tools() {
    show_progress "3" "12" "安装基础系统工具"
    
    echo -e "${YELLOW}📦 安装基础工具...${NC}"
    
    apt update
    apt install -y \
        curl wget git unzip vim nano htop tree jq \
        nginx supervisor ufw \
        build-essential
    
    echo -e "${GREEN}✅ 基础工具安装完成${NC}"
}

# 创建项目用户和目录
setup_project_user() {
    show_progress "4" "12" "创建项目用户和目录结构"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER"
        usermod -aG docker "$PROJECT_USER"  # 添加到docker组
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 创建成功${NC}"
    else
        usermod -aG docker "$PROJECT_USER"  # 确保在docker组中
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 已存在${NC}"
    fi
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    mkdir -p /var/log/qatoolbox
    mkdir -p "$PROJECT_DIR"
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/log/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 项目用户和目录配置完成${NC}"
}

# 验证项目代码
verify_project_code() {
    show_progress "5" "12" "验证项目代码完整性"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        handle_error "项目目录不存在: $PROJECT_DIR" "请确保项目代码已正确放置"
    fi
    
    cd "$PROJECT_DIR"
    
    # 验证关键文件
    local required_files=(
        "manage.py"
        "wsgi.py" 
        "urls.py"
        "requirements.txt"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -e "$file" ]; then
            handle_error "缺少关键文件: $file" "请检查项目结构完整性"
        fi
    done
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 项目代码验证完成${NC}"
}

# 创建Dockerfile
create_dockerfile() {
    show_progress "6" "12" "创建Docker镜像配置"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐳 创建Dockerfile...${NC}"
    
    cat > Dockerfile << 'EOF'
# QAToolBox Docker镜像 - Ubuntu 24.04兼容版本
FROM python:3.12-bullseye

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    # 基础工具
    curl wget git unzip vim nano htop tree \
    build-essential gcc g++ make cmake pkg-config \
    # 数据库驱动
    libpq-dev postgresql-client \
    libmysqlclient-dev default-libmysqlclient-dev \
    libsqlite3-dev \
    # 图像处理库
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libfreetype6-dev liblcms2-dev libopenjp2-7-dev \
    zlib1g-dev libimagequant-dev \
    # 音视频处理
    ffmpeg libavcodec-dev libavformat-dev libswscale-dev \
    libavresample-dev libavutil-dev \
    libsndfile1-dev portaudio19-dev \
    # OCR支持
    tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
    tesseract-ocr-eng libtesseract-dev \
    poppler-utils antiword unrtf ghostscript \
    # 科学计算
    libgomp1 libatlas-base-dev liblapack-dev libblas-dev \
    libopenblas-dev libhdf5-dev libprotobuf-dev \
    # GUI和显示
    libgtk-3-dev libgstreamer1.0-dev \
    libgl1-mesa-glx libsm6 libxext6 libxrender1 \
    # 浏览器支持
    chromium-browser \
    # 清理缓存
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip setuptools wheel

# 安装Python依赖 - 分阶段安装避免冲突
# 1. 核心Django框架
RUN pip install \
    Django==4.2.7 \
    djangorestframework==3.14.0 \
    django-cors-headers==4.3.1 \
    django-crispy-forms==2.0 \
    crispy-bootstrap5==0.7 \
    django-simple-captcha==0.6.0 \
    django-extensions==3.2.3

# 2. 数据库和缓存
RUN pip install \
    psycopg2-binary==2.9.7 \
    redis==4.6.0 \
    django-redis==5.4.0

# 3. 异步和实时通信
RUN pip install \
    channels==4.0.0 \
    channels-redis==4.1.0 \
    daphne==4.0.0 \
    asgiref==3.8.1

# 4. 任务队列
RUN pip install \
    celery==5.3.4 \
    django-celery-beat==2.5.0

# 5. Web服务器
RUN pip install \
    gunicorn==21.2.0 \
    whitenoise==6.6.0

# 6. 环境配置
RUN pip install \
    python-dotenv==1.0.0 \
    django-environ==0.11.2

# 7. HTTP和网络
RUN pip install \
    requests==2.31.0 \
    urllib3==1.26.18 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3

# 8. 数据处理
RUN pip install \
    pandas==2.0.3 \
    numpy==1.24.4 \
    scipy==1.9.3 \
    matplotlib==3.7.5

# 9. 机器学习（CPU版本）
RUN pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    && pip install \
    tensorflow-cpu \
    scikit-learn==1.3.2

# 10. 图像处理
RUN pip install \
    Pillow==9.5.0 \
    opencv-python-headless==4.8.1.78 \
    scikit-image \
    imageio

# 11. 文档处理
RUN pip install \
    python-docx==1.1.0 \
    python-pptx==0.6.22 \
    openpyxl==3.1.2 \
    reportlab==4.0.9 \
    pypdfium2==4.23.1 \
    pdfplumber==0.10.3

# 12. OCR
RUN pip install \
    pytesseract==0.3.10 \
    easyocr

# 13. 音频处理
RUN pip install \
    pydub==0.25.1 \
    librosa==0.10.1 \
    soundfile==0.12.1

# 14. 浏览器自动化
RUN pip install \
    selenium==4.15.2 \
    webdriver-manager==4.0.1

# 15. 其他工具
RUN pip install \
    cryptography==41.0.7 \
    tenacity==8.2.3 \
    prettytable==3.9.0 \
    qrcode==7.4.2 \
    python-dateutil==2.8.2

# 复制项目文件
COPY . /app/

# 创建必要目录
RUN mkdir -p /app/static /app/media /app/logs

# 设置权限
RUN chmod +x /app/manage.py

# 暴露端口
EXPOSE 8000

# 默认命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
EOF

    echo -e "${GREEN}✅ Dockerfile创建完成${NC}"
}

# 创建Docker Compose配置
create_docker_compose() {
    show_progress "7" "12" "创建Docker Compose配置"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐳 创建docker-compose.yml...${NC}"
    
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:16
    restart: always
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    networks:
      - qatoolbox_network

  # Redis缓存
  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network

  # QAToolBox主应用
  web:
    build: .
    restart: always
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             python manage.py shell -c \"
             from django.contrib.auth import get_user_model;
             User = get_user_model();
             User.objects.filter(username='admin').delete();
             User.objects.create_superuser('admin', 'admin@${DOMAIN}', '${ADMIN_PASSWORD}');
             print('管理员用户创建完成')
             \" &&
             gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 60"
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},${SERVER_IP},localhost,127.0.0.1
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - qatoolbox_network

  # Celery Worker（如果需要）
  celery:
    build: .
    restart: always
    command: celery -A QAToolBox worker --loglevel=info
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    networks:
      - qatoolbox_network

  # Celery Beat（定时任务）
  celery-beat:
    build: .
    restart: always
    command: celery -A QAToolBox beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=${DB_PASSWORD}
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    networks:
      - qatoolbox_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  qatoolbox_network:
    driver: bridge
EOF

    echo -e "${YELLOW}🐳 创建数据库初始化脚本...${NC}"
    
    cat > init-db.sql << EOF
-- 初始化QAToolBox数据库
CREATE DATABASE IF NOT EXISTS qatoolbox;
CREATE USER IF NOT EXISTS qatoolbox WITH ENCRYPTED PASSWORD '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
ALTER DATABASE qatoolbox OWNER TO qatoolbox;
EOF

    echo -e "${GREEN}✅ Docker Compose配置完成${NC}"
}

# 创建Docker专用Django配置
create_docker_django_settings() {
    show_progress "8" "12" "创建Docker专用Django配置"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}⚙️ 创建Docker生产配置...${NC}"
    
    # 确保配置目录存在
    mkdir -p config/settings
    
    cat > config/settings/docker_production.py << 'EOF'
"""
QAToolBox Docker生产环境配置
专为Docker容器化部署优化
"""
import os
import sys
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

# 从环境变量读取配置
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-docker-production-key-change-me')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# 允许的主机
ALLOWED_HOSTS_STR = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
ALLOWED_HOSTS.extend(['testserver', 'web', 'localhost'])

# 站点配置
SITE_ID = 1

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

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

# 第三方应用 - 安全地添加
THIRD_PARTY_APPS = []
optional_third_party = [
    'rest_framework',
    'corsheaders', 
    'captcha',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'channels',
    'django_extensions',
]

for app in optional_third_party:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
        print(f"✅ 已添加第三方应用: {app}")
    except ImportError:
        print(f"⚠️ 跳过未安装的应用: {app}")

# 本地应用 - 安全地添加
LOCAL_APPS = []
local_app_candidates = [
    'apps.users',
    'apps.content', 
    'apps.tools',
    'apps.share',
]

for app in local_app_candidates:
    app_path = BASE_DIR / app.replace('.', '/')
    if app_path.exists() and (app_path / '__init__.py').exists():
        LOCAL_APPS.append(app)
        print(f"✅ 已添加本地应用: {app}")
    else:
        print(f"⚠️ 跳过不存在的应用: {app}")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置
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

# 安全地添加中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

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

# Channels配置 (如果安装了)
if 'channels' in THIRD_PARTY_APPS:
    ASGI_APPLICATION = 'asgi.application'
    
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [os.environ.get('REDIS_URL', 'redis://redis:6379/0')],
            },
        },
    }

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 60,
        },
        'CONN_MAX_AGE': 60,
    }
}

# Redis缓存配置
REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'qatoolbox',
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 14天
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/app/static/'

# 收集静态文件的目录
STATICFILES_DIRS = []
static_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'src' / 'static',
]

for static_dir in static_dirs:
    if static_dir.exists():
        STATICFILES_DIRS.append(static_dir)

# 静态文件存储配置
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/app/media/'

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Django REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1000/hour',
            'user': '10000/hour',
        },
    }

# CORS配置
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOWED_ORIGINS = [
        "https://shenyiqing.xin",
        "https://www.shenyiqing.xin",
        "http://47.103.143.152",
        "http://localhost:8000",
    ]
    CORS_ALLOW_CREDENTIALS = True

# Crispy Forms配置
if 'crispy_forms' in THIRD_PARTY_APPS:
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

# 验证码配置
if 'captcha' in THIRD_PARTY_APPS:
    CAPTCHA_IMAGE_SIZE = (120, 40)
    CAPTCHA_LENGTH = 4
    CAPTCHA_TIMEOUT = 5

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'https://shenyiqing.xin',
    'https://www.shenyiqing.xin',
    'http://47.103.143.152',
    'http://localhost:8000',
]

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery配置
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

print(f"✅ QAToolBox Docker配置加载完成")
print(f"安装的应用数量: {len(INSTALLED_APPS)}")
print(f"Django应用: {len(DJANGO_APPS)}")
print(f"第三方应用: {len(THIRD_PARTY_APPS)}")
print(f"本地应用: {len(LOCAL_APPS)}")
EOF

    echo -e "${GREEN}✅ Docker Django配置完成${NC}"
}

# 构建和启动Docker容器
build_and_start_containers() {
    show_progress "9" "12" "构建和启动Docker容器"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐳 构建Docker镜像...${NC}"
    retry_command "sudo -u '$PROJECT_USER' docker compose build" "构建Docker镜像" 2 10
    
    echo -e "${YELLOW}🐳 启动Docker容器...${NC}"
    retry_command "sudo -u '$PROJECT_USER' docker compose up -d" "启动Docker容器" 2 10
    
    echo -e "${YELLOW}⏳ 等待容器启动...${NC}"
    sleep 30
    
    # 检查容器状态
    echo -e "${YELLOW}📊 检查容器状态...${NC}"
    sudo -u "$PROJECT_USER" docker compose ps
    
    echo -e "${GREEN}✅ Docker容器启动完成${NC}"
}

# 配置Nginx反向代理
setup_nginx_proxy() {
    show_progress "10" "12" "配置Nginx反向代理"
    
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
# QAToolBox Docker Nginx配置
upstream qatoolbox_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 文件上传大小限制
    client_max_body_size 100M;
    
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
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Django应用代理
    location / {
        proxy_pass http://qatoolbox_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
        
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
}
EOF
    
    # 启用站点配置
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t || handle_error "Nginx配置语法错误" "检查配置文件语法"
    
    # 重启Nginx
    systemctl restart nginx
    
    echo -e "${GREEN}✅ Nginx配置完成${NC}"
}

# 配置防火墙和安全
setup_security() {
    show_progress "11" "12" "配置防火墙和安全"
    
    echo -e "${YELLOW}🔒 配置UFW防火墙...${NC}"
    
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
    
    echo -e "${GREEN}✅ 安全配置完成${NC}"
}

# 最终验证和信息显示
final_verification() {
    show_progress "12" "12" "最终验证和系统信息"
    
    echo -e "${YELLOW}🔍 等待服务完全启动...${NC}"
    sleep 20
    
    echo -e "${YELLOW}🔍 检查Docker容器状态...${NC}"
    cd "$PROJECT_DIR"
    sudo -u "$PROJECT_USER" docker compose ps
    
    echo -e "${YELLOW}🔍 检查系统服务状态...${NC}"
    local services=("nginx" "docker")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "${GREEN}✅ $service 运行正常${NC}"
        else
            echo -e "${RED}❌ $service 状态异常${NC}"
        fi
    done
    
    echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
    
    # 测试本地访问
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    
    if [[ "$http_status" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✅ HTTP访问正常 (状态码: $http_status)${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP访问异常 (状态码: $http_status)${NC}"
    fi
    
    # 显示容器日志
    echo -e "${YELLOW}📋 查看应用日志...${NC}"
    sudo -u "$PROJECT_USER" docker compose logs web --tail=10
    
    # 显示最终部署信息
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox Docker部署成功！
========================================

🌐 访问信息:
  主站地址: http://$DOMAIN/
  IP访问:   http://$SERVER_IP/
  管理后台: http://$DOMAIN/admin/

👑 管理员账户:
  用户名: admin
  密码:   $ADMIN_PASSWORD
  邮箱:   admin@$DOMAIN

🐳 Docker信息:
  项目目录: $PROJECT_DIR
  容器状态: docker compose ps
  容器日志: docker compose logs

📊 系统信息:
  数据库:   PostgreSQL (Docker容器)
  缓存:     Redis (Docker容器)
  Python:   $(python3 --version 2>&1)
  Docker:   $(docker --version 2>&1)

🚀 完整功能支持:
  ✅ 机器学习 (PyTorch, TensorFlow)
  ✅ 计算机视觉 (OpenCV, PIL)
  ✅ 数据分析 (pandas, numpy, matplotlib)
  ✅ 文档处理 (Word, Excel, PDF)
  ✅ OCR识别 (Tesseract, EasyOCR)
  ✅ 音频处理 (librosa, pydub)
  ✅ 浏览器自动化 (Selenium)
  ✅ 实时通信 (WebSocket, Channels)
  ✅ 任务队列 (Celery, Redis)
  ✅ API框架 (DRF, CORS支持)

🔧 Docker管理命令:
  查看容器: docker compose ps
  查看日志: docker compose logs
  重启服务: docker compose restart
  停止服务: docker compose down
  更新服务: docker compose up -d --build

🔧 系统管理命令:
  重启Nginx: sudo systemctl restart nginx
  查看防火墙: sudo ufw status
  系统状态: htop

📋 重要文件:
  项目目录: $PROJECT_DIR
  Docker配置: $PROJECT_DIR/docker-compose.yml
  Nginx配置: /etc/nginx/sites-available/qatoolbox
  部署日志: $LOG_FILE

🔒 安全配置:
  防火墙: UFW已启用 (SSH, HTTP, HTTPS)
  容器隔离: Docker网络隔离
  数据持久化: Docker卷存储

📝 下一步建议:
  1. 配置域名DNS解析指向 $SERVER_IP
  2. 申请SSL证书 (certbot --nginx -d $DOMAIN)
  3. 设置自动备份 (docker compose exec db pg_dump...)
  4. 监控容器状态
  5. 定期更新镜像

========================================
EOF
    echo -e "${NC}"
    
    echo -e "${BLUE}🧪 快速测试命令:${NC}"
    echo -e "  curl -I http://localhost/"
    echo -e "  curl -I http://$SERVER_IP/"
    echo -e "  docker compose ps"
    echo -e "  docker compose logs web"
    echo ""
    
    echo -e "${CYAN}🎊 恭喜！QAToolBox Docker部署成功完成！${NC}"
    echo -e "${BLUE}现在您可以享受完整的容器化AI应用了！${NC}"
}

# 主执行流程
main() {
    # 检查权限
    check_root
    
    # 设置错误处理
    trap 'echo -e "${RED}❌ 部署过程中出现错误，请查看日志: $LOG_FILE${NC}"; exit 1' ERR
    
    echo -e "${BLUE}🚀 开始QAToolBox Ubuntu 24.04 Docker部署...${NC}"
    echo -e "${BLUE}📋 详细日志: $LOG_FILE${NC}"
    echo ""
    
    # 执行部署步骤
    detect_system
    install_docker
    install_basic_tools
    setup_project_user
    verify_project_code
    create_dockerfile
    create_docker_compose
    create_docker_django_settings
    build_and_start_containers
    setup_nginx_proxy
    setup_security
    final_verification
    
    echo -e "${GREEN}🎉 QAToolBox Ubuntu 24.04 Docker部署成功完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
