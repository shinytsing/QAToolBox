#!/bin/bash

# QAToolBox 完整项目部署脚本 - 部署本地完整功能到远程服务器
# 服务器IP: 47.103.143.152
# 域名: shenyiqing.xin

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER_IP="47.103.143.152"
DOMAIN="shenyiqing.xin"

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

# 清理现有环境
cleanup_existing() {
    log_info "清理现有环境..."
    
    # 停止服务
    pkill -f "python.*manage.py" || true
    sudo systemctl stop qatoolbox || true
    sudo systemctl stop nginx || true
    
    # 删除旧项目
    rm -rf ~/qatoolbox_production ~/qatoolbox_simple ~/qatoolbox_app
    
    log_success "环境清理完成"
}

# 安装完整依赖
install_full_dependencies() {
    log_info "安装完整系统依赖..."
    
    # 更新系统
    sudo apt-get update && sudo apt-get upgrade -y
    
    # 安装Python和开发工具
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        nginx \
        redis-server \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        curl \
        wget \
        git \
        unzip \
        supervisor \
        htop \
        tree \
        vim \
        ufw \
        certbot \
        python3-certbot-nginx
    
    # 配置pip国内镜像
    mkdir -p ~/.config/pip
    cat > ~/.config/pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
EOF
    
    log_success "系统依赖安装完成"
}

# 克隆完整项目
clone_full_project() {
    log_info "获取完整项目代码..."
    
    cd ~
    
    # 尝试多种方式获取项目代码
    if git clone https://github.com/shinytsing/QAToolbox.git qatoolbox_production; then
        log_success "Git克隆成功"
    elif git clone https://hub.fastgit.xyz/shinytsing/QAToolbox.git qatoolbox_production; then
        log_success "镜像克隆成功"
    else
        log_warning "Git克隆失败，使用ZIP下载..."
        wget https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip -O qatoolbox.zip
        unzip -q qatoolbox.zip
        mv QAToolbox-main qatoolbox_production
        rm qatoolbox.zip
        log_success "ZIP下载完成"
    fi
    
    cd qatoolbox_production
    log_success "项目代码获取完成"
}

# 设置Python虚拟环境
setup_python_env() {
    log_info "设置Python虚拟环境..."
    
    cd ~/qatoolbox_production
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装项目依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    elif [ -f "requirements/production.txt" ]; then
        pip install -r requirements/production.txt
    else
        # 安装基础依赖
        pip install \
            django==4.2.7 \
            djangorestframework \
            celery \
            redis \
            psycopg2-binary \
            pillow \
            gunicorn \
            django-cors-headers \
            python-decouple \
            whitenoise
    fi
    
    log_success "Python环境设置完成"
}

# 配置生产环境设置
configure_production_settings() {
    log_info "配置生产环境设置..."
    
    cd ~/qatoolbox_production
    
    # 创建环境变量文件
    cat > .env << EOF
# 生产环境配置
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=$SERVER_IP,$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# 数据库配置
DATABASE_URL=sqlite:///$(pwd)/db.sqlite3

# Redis配置  
REDIS_URL=redis://localhost:6379/0

# 静态文件配置
STATIC_ROOT=$(pwd)/staticfiles
MEDIA_ROOT=$(pwd)/media

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
CSRF_TRUSTED_ORIGINS=http://$DOMAIN,http://$SERVER_IP,https://$DOMAIN,https://$SERVER_IP
EOF
    
    # 如果没有生产配置文件，创建一个
    if [ ! -f "config/settings/production.py" ] && [ ! -f "qatoolbox/settings/production.py" ]; then
        mkdir -p config/settings
        
        cat > config/settings/production.py << 'EOF'
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.users',
    'apps.tools',
    'apps.content',
]

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS设置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS').split(',')

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
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
    
    log_success "生产环境配置完成"
}

# 设置数据库
setup_database() {
    log_info "设置数据库..."
    
    cd ~/qatoolbox_production
    source venv/bin/activate
    
    # 创建必要目录
    mkdir -p logs media staticfiles
    
    # 设置Django设置模块
    if [ -f "config/settings/production.py" ]; then
        export DJANGO_SETTINGS_MODULE=config.settings.production
    elif [ -f "qatoolbox/settings/production.py" ]; then
        export DJANGO_SETTINGS_MODULE=qatoolbox.settings.production
    else
        export DJANGO_SETTINGS_MODULE=settings
    fi
    
    # 运行迁移
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    
    # 创建超级用户
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')" | python manage.py shell
    
    # 收集静态文件
    python manage.py collectstatic --noinput --clear
    
    # 设置权限
    chmod -R 755 staticfiles media logs
    
    log_success "数据库设置完成"
}

# 配置Gunicorn
setup_gunicorn() {
    log_info "配置Gunicorn..."
    
    cd ~/qatoolbox_production
    
    # 创建Gunicorn配置
    cat > gunicorn.conf.py << 'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
user = "admin"
group = "admin"
tmp_upload_dir = None
errorlog = "/home/admin/qatoolbox_production/logs/gunicorn_error.log"
accesslog = "/home/admin/qatoolbox_production/logs/gunicorn_access.log"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'
loglevel = "info"
preload_app = True
EOF
    
    # 创建启动脚本
    cat > start_gunicorn.sh << 'EOF'
#!/bin/bash
cd /home/admin/qatoolbox_production
source venv/bin/activate

# 设置Django设置模块
if [ -f "config/settings/production.py" ]; then
    export DJANGO_SETTINGS_MODULE=config.settings.production
elif [ -f "qatoolbox/settings/production.py" ]; then
    export DJANGO_SETTINGS_MODULE=qatoolbox.settings.production
else
    export DJANGO_SETTINGS_MODULE=settings
fi

# 启动Gunicorn
exec gunicorn --config gunicorn.conf.py \
    $(python -c "
import os
if os.path.exists('config/wsgi.py'):
    print('config.wsgi:application')
elif os.path.exists('qatoolbox/wsgi.py'):
    print('qatoolbox.wsgi:application')
else:
    print('wsgi:application')
")
EOF
    
    chmod +x start_gunicorn.sh
    
    log_success "Gunicorn配置完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 创建完整的Nginx配置
    sudo tee /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $SERVER_IP $DOMAIN www.$DOMAIN;
    
    client_max_body_size 100M;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # 静态文件
    location /static/ {
        alias /home/admin/qatoolbox_production/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/qatoolbox_production/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        alias /home/admin/qatoolbox_production/staticfiles/favicon.ico;
        access_log off;
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 创建系统服务
create_systemd_service() {
    log_info "创建系统服务..."
    
    sudo tee /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Gunicorn Application Server
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin/qatoolbox_production
Environment="PATH=/home/admin/qatoolbox_production/venv/bin"
ExecStart=/home/admin/qatoolbox_production/start_gunicorn.sh
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # 重载并启动服务
    sudo systemctl daemon-reload
    sudo systemctl start qatoolbox
    sudo systemctl enable qatoolbox
    
    log_success "系统服务创建完成"
}

# 启动Redis
setup_redis() {
    log_info "配置Redis..."
    
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    log_success "Redis配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    
    log_success "防火墙配置完成"
}

# 检查部署状态
check_deployment() {
    log_info "检查部署状态..."
    
    sleep 10
    
    # 检查服务状态
    echo "服务状态检查："
    systemctl is-active qatoolbox && echo "✅ QAToolBox服务运行正常" || echo "❌ QAToolBox服务异常"
    systemctl is-active nginx && echo "✅ Nginx服务运行正常" || echo "❌ Nginx服务异常"
    systemctl is-active redis-server && echo "✅ Redis服务运行正常" || echo "❌ Redis服务异常"
    
    # 测试网站访问
    if curl -f -s http://localhost/ > /dev/null; then
        log_success "网站访问正常"
    else
        log_error "网站访问异常"
        log_info "查看服务日志："
        sudo journalctl -u qatoolbox --no-pager -n 10
    fi
    
    # 检查静态文件
    if curl -f -s http://localhost/static/admin/css/base.css > /dev/null; then
        log_success "静态文件访问正常"
    else
        log_warning "静态文件访问可能有问题"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉🎉🎉 QAToolBox 完整项目部署完成！🎉🎉🎉"
    echo ""
    echo "📱 访问地址:"
    echo "   🌐 域名: http://$DOMAIN"
    echo "   📍 IP: http://$SERVER_IP"
    echo ""
    echo "🔐 管理后台:"
    echo "   🌐 http://$DOMAIN/admin/"
    echo "   📍 http://$SERVER_IP/admin/"
    echo ""
    echo "👤 管理员账号:"
    echo "   用户名: admin"
    echo "   密码: admin123456"
    echo ""
    echo "🛠️ 项目功能:"
    echo "   - 完整的Django应用"
    echo "   - 用户管理系统"
    echo "   - 工具模块"
    echo "   - 内容管理"
    echo "   - REST API"
    echo "   - 静态文件服务"
    echo ""
    echo "🔧 管理命令:"
    echo "   查看服务状态: sudo systemctl status qatoolbox"
    echo "   重启服务: sudo systemctl restart qatoolbox"
    echo "   查看错误日志: tail -f ~/qatoolbox_production/logs/gunicorn_error.log"
    echo "   查看访问日志: tail -f ~/qatoolbox_production/logs/gunicorn_access.log"
    echo "   进入项目目录: cd ~/qatoolbox_production"
    echo "   激活虚拟环境: source ~/qatoolbox_production/venv/bin/activate"
    echo ""
    echo "🎊 现在您拥有了完整功能的QAToolBox！"
}

# 主函数
main() {
    log_info "开始QAToolBox完整项目部署..."
    
    cleanup_existing
    install_full_dependencies
    clone_full_project
    setup_python_env
    configure_production_settings
    setup_database
    setup_gunicorn
    setup_nginx
    setup_redis
    create_systemd_service
    setup_firewall
    check_deployment
    show_deployment_info
    
    log_success "完整项目部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，在第$LINENO行"; exit 1' ERR

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
