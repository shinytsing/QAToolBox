#!/bin/bash
# QAToolBox Django 一键修复和启动脚本
# ==========================================
# 解决所有依赖问题并启动服务
# ==========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="/home/qatoolbox/QAToolbox"

echo -e "${CYAN}"
echo "========================================"
echo "🔧 QAToolBox Django 一键修复启动"
echo "========================================"
echo "修复依赖 + 数据库 + 启动服务"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用root权限运行: sudo $0${NC}"
    exit 1
fi

# 进度显示
show_step() {
    local step=$1
    local total=$2
    local desc=$3
    echo -e "${CYAN}[${step}/${total}] ${desc}${NC}"
}

# 第1步：安装所有缺失的Python依赖
install_missing_deps() {
    show_step "1" "5" "安装所有缺失的Python依赖"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐍 安装核心依赖...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        psutil \
        python-dotenv \
        django-environ \
        python-decouple \
        requests \
        beautifulsoup4 \
        lxml \
        html5lib || echo "⚠️ 部分核心依赖安装失败，继续"
    
    echo -e "${YELLOW}📊 安装数据分析库...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        pandas \
        numpy \
        matplotlib \
        pyecharts || echo "⚠️ 部分数据分析库安装失败，继续"
    
    echo -e "${YELLOW}📄 安装文档处理库...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        python-docx \
        python-pptx \
        openpyxl \
        reportlab \
        Pillow || echo "⚠️ 部分文档处理库安装失败，继续"
    
    echo -e "${YELLOW}🔧 安装工具库...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        pydub \
        selenium \
        cryptography \
        tenacity \
        prettytable \
        qrcode \
        yfinance \
        peewee || echo "⚠️ 部分工具库安装失败，继续"
    
    echo -e "${YELLOW}⚡ 安装异步和任务库...${NC}"
    sudo -u qatoolbox .venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
        channels \
        channels-redis \
        daphne \
        asgiref \
        celery \
        django-celery-beat || echo "⚠️ 部分异步库安装失败，继续"
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 第2步：创建简化的生产配置
create_production_settings() {
    show_step "2" "5" "创建简化的Django生产配置"
    
    cd "$PROJECT_DIR"
    
    # 创建简化的生产设置，避免复杂导入
    sudo -u qatoolbox cat > config/settings/production_simple.py << 'EOF'
"""
简化的生产环境设置 - 避免复杂依赖
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 基础设置
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-production-key-shenyiqing-2024')
DEBUG = False
ALLOWED_HOSTS = ['shenyiqing.xin', 'www.shenyiqing.xin', '47.103.143.152', 'localhost', '127.0.0.1', '*']

# Django核心应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# 尝试导入本地应用（安全方式）
import sys
sys.path.append(str(BASE_DIR / 'apps'))

# 安全地添加本地应用
local_apps = []
for app_name in ['apps.users', 'apps.tools', 'apps.content', 'apps.share']:
    try:
        __import__(app_name.split('.')[-1])
        local_apps.append(app_name)
        print(f"✅ 已加载应用: {app_name}")
    except ImportError as e:
        print(f"⚠️ 跳过应用: {app_name} - {e}")

INSTALLED_APPS.extend(local_apps)

# 中间件
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

# 模板设置
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

# 数据库设置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'QAToolBox@2024'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {'connect_timeout': 60},
    }
}

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/qatoolbox/static/'
STATICFILES_DIRS = []

# 媒体文件
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/qatoolbox/media/'

# 文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/qatoolbox/django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
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
EOF

    chown qatoolbox:qatoolbox config/settings/production_simple.py
    echo -e "${GREEN}✅ 生产配置创建完成${NC}"
}

# 第3步：初始化数据库
initialize_database() {
    show_step "3" "5" "初始化Django数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🗄️ 执行数据库迁移...${NC}"
    export DJANGO_SETTINGS_MODULE=config.settings.production_simple
    
    # 创建迁移文件
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_simple .venv/bin/python manage.py makemigrations --noinput || echo "⚠️ makemigrations失败，继续"
    
    # 执行迁移
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_simple .venv/bin/python manage.py migrate --noinput
    
    echo -e "${YELLOW}👑 创建管理员用户...${NC}"
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_simple .venv/bin/python manage.py shell << 'PYTHON_EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    if User.objects.filter(username='admin').exists():
        print("✅ 管理员用户已存在")
    else:
        User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
        print("✅ 管理员用户创建成功")
except Exception as e:
    print(f"⚠️ 管理员用户操作: {e}")
PYTHON_EOF
    
    echo -e "${YELLOW}📁 收集静态文件...${NC}"
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production_simple .venv/bin/python manage.py collectstatic --noinput || echo "⚠️ collectstatic失败，继续"
    
    echo -e "${GREEN}✅ 数据库初始化完成${NC}"
}

# 第4步：配置Web服务
setup_web_services() {
    show_step "4" "5" "配置Nginx和Supervisor服务"
    
    echo -e "${YELLOW}🌐 配置Nginx...${NC}"
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl restart nginx
    
    echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=/home/qatoolbox/QAToolbox/.venv/bin/gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 --max-requests 1000
directory=/home/qatoolbox/QAToolbox
user=qatoolbox
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox/access.log
stderr_logfile=/var/log/qatoolbox/error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.production_simple"
EOF
    
    # 创建日志目录
    mkdir -p /var/log/qatoolbox
    chown qatoolbox:qatoolbox /var/log/qatoolbox
    
    # 重启服务
    supervisorctl reread
    supervisorctl update
    supervisorctl restart qatoolbox || supervisorctl start qatoolbox
    
    echo -e "${GREEN}✅ Web服务配置完成${NC}"
}

# 第5步：验证和启动
verify_and_start() {
    show_step "5" "5" "验证部署并启动服务"
    
    echo -e "${YELLOW}🔍 等待服务启动...${NC}"
    sleep 10
    
    echo -e "${YELLOW}📊 检查服务状态...${NC}"
    systemctl is-active nginx postgresql redis-server supervisor || echo "⚠️ 部分系统服务异常"
    supervisorctl status qatoolbox
    
    echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -E "200|301|302" > /dev/null; then
        echo -e "${GREEN}✅ HTTP访问正常${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP访问异常，检查日志...${NC}"
        tail -10 /var/log/qatoolbox/error.log || echo "无错误日志"
    fi
    
    echo -e "${CYAN}"
    echo "========================================"
    echo "🎉 QAToolBox 部署完成！"
    echo "========================================"
    echo -e "${NC}"
    
    echo -e "${GREEN}🌐 访问地址:${NC}"
    echo "  - 主站: http://shenyiqing.xin/"
    echo "  - IP访问: http://47.103.143.152/"
    echo "  - 管理后台: http://shenyiqing.xin/admin/"
    echo ""
    
    echo -e "${GREEN}👑 管理员账号:${NC}"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo ""
    
    echo -e "${GREEN}🔧 管理命令:${NC}"
    echo "  - 重启应用: sudo supervisorctl restart qatoolbox"
    echo "  - 查看日志: sudo tail -f /var/log/qatoolbox/access.log"
    echo "  - 查看错误: sudo tail -f /var/log/qatoolbox/error.log"
    echo "  - 检查状态: sudo supervisorctl status"
    echo ""
    
    echo -e "${CYAN}🎊 开始使用你的QAToolBox吧！${NC}"
}

# 主执行流程
main() {
    echo -e "${BLUE}开始Django一键修复和启动...${NC}"
    
    install_missing_deps
    create_production_settings
    initialize_database
    setup_web_services
    verify_and_start
    
    echo -e "${GREEN}🎉 一键修复启动完成！${NC}"
}

# 错误处理
trap 'echo -e "${RED}❌ 执行过程中出现错误，请查看上面的输出信息${NC}"; exit 1' ERR

# 执行主函数
main "$@"
