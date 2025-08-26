#!/bin/bash

# ModeShift 完整项目部署脚本
# 部署本地所有炫酷界面和功能到远程服务器
# 服务器IP: 47.103.143.152 域名: shenyiqing.xin

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_modeshift() {
    echo -e "${PURPLE}[MODESHIFT]${NC} $1"
}

# 显示ModeShift Logo
show_modeshift_logo() {
    echo -e "${CYAN}"
    cat << 'EOF'
    ██████████████████████████████████████████████████████████
    █                                                        █
    █    ███    ███  ██████  ██████  ███████ ███████ ██   ██ █
    █    ████  ████ ██    ██ ██   ██ ██      ██      ██   ██ █
    █    ██ ████ ██ ██    ██ ██   ██ █████   ███████ ███████ █
    █    ██  ██  ██ ██    ██ ██   ██ ██           ██ ██   ██ █
    █    ██      ██  ██████  ██████  ███████ ███████ ██   ██ █
    █                                                        █
    █           Four Modes, One Beast - 完整部署             █
    █                                                        █
    ██████████████████████████████████████████████████████████
EOF
    echo -e "${NC}"
}

# 清理环境
cleanup_environment() {
    log_modeshift "清理现有环境..."
    
    # 停止所有相关服务
    pkill -f "python.*manage.py" || true
    pkill -f "gunicorn" || true
    sudo systemctl stop qatoolbox || true
    sudo systemctl stop nginx || true
    
    # 删除旧项目
    rm -rf ~/qatoolbox_production ~/qatoolbox_simple ~/qatoolbox_app ~/ModeShift
    
    log_success "环境清理完成"
}

# 安装完整依赖
install_complete_dependencies() {
    log_modeshift "安装完整系统依赖..."
    
    # 更新系统
    sudo apt-get update && sudo apt-get upgrade -y
    
    # 安装完整依赖列表
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
        libssl-dev \
        libffi-dev \
        libjpeg-dev \
        libpng-dev \
        zlib1g-dev \
        curl \
        wget \
        git \
        unzip \
        supervisor \
        htop \
        tree \
        vim \
        nano \
        ufw \
        certbot \
        python3-certbot-nginx \
        nodejs \
        npm
    
    # 配置pip国内镜像
    mkdir -p ~/.config/pip
    cat > ~/.config/pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
[install]
trusted-host = mirrors.aliyun.com
EOF
    
    log_success "完整系统依赖安装完成"
}

# 克隆完整项目代码
clone_complete_project() {
    log_modeshift "获取完整ModeShift项目代码..."
    
    cd ~
    
    # 多源克隆策略
    CLONE_SUCCESS=false
    
    # 尝试GitHub官方
    if git clone https://github.com/shinytsing/QAToolbox.git ModeShift; then
        log_success "GitHub官方克隆成功"
        CLONE_SUCCESS=true
    # 尝试FastGit镜像
    elif git clone https://hub.fastgit.xyz/shinytsing/QAToolbox.git ModeShift; then
        log_success "FastGit镜像克隆成功"
        CLONE_SUCCESS=true
    # 尝试GitClone镜像
    elif git clone https://gitclone.com/github.com/shinytsing/QAToolbox.git ModeShift; then
        log_success "GitClone镜像克隆成功"
        CLONE_SUCCESS=true
    # 使用ZIP下载
    else
        log_warning "Git克隆失败，使用ZIP下载..."
        if wget https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip -O modeshift.zip; then
            unzip -q modeshift.zip
            mv QAToolbox-main ModeShift
            rm modeshift.zip
            CLONE_SUCCESS=true
            log_success "ZIP下载完成"
        fi
    fi
    
    if [ "$CLONE_SUCCESS" = false ]; then
        log_error "无法获取项目代码，请检查网络连接"
        exit 1
    fi
    
    cd ModeShift
    log_success "完整项目代码获取完成"
}

# 设置Python环境和依赖
setup_complete_python_env() {
    log_modeshift "设置完整Python环境..."
    
    cd ~/ModeShift
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip setuptools wheel
    
    # 安装项目依赖 - 支持多种requirements文件
    if [ -f "requirements/production.txt" ]; then
        log_info "安装生产环境依赖..."
        pip install -r requirements/production.txt
    elif [ -f "requirements/base.txt" ]; then
        log_info "安装基础依赖..."
        pip install -r requirements/base.txt
        if [ -f "requirements/optional.txt" ]; then
            pip install -r requirements/optional.txt || true
        fi
    elif [ -f "requirements.txt" ]; then
        log_info "安装项目依赖..."
        pip install -r requirements.txt
    else
        log_warning "未找到requirements文件，安装基础依赖..."
        pip install \
            django==4.2.7 \
            djangorestframework \
            django-cors-headers \
            celery \
            redis \
            psycopg2-binary \
            pillow \
            gunicorn \
            python-decouple \
            whitenoise \
            django-extensions \
            django-debug-toolbar
    fi
    
    log_success "Python环境设置完成"
}

# 配置生产环境设置
configure_production_settings() {
    log_modeshift "配置ModeShift生产环境..."
    
    cd ~/ModeShift
    
    # 生成安全密钥
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    
    # 创建生产环境配置
    cat > .env << EOF
# ModeShift 生产环境配置
DEBUG=False
SECRET_KEY=$SECRET_KEY
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

# ModeShift 特定配置
MODESHIFT_THEME=cyberpunk
ENABLE_ALL_MODES=True
EOF
    
    # 确保使用正确的settings模块
    if [ -f "config/settings/production.py" ]; then
        export DJANGO_SETTINGS_MODULE=config.settings.production
    elif [ -f "config/settings/base.py" ]; then
        export DJANGO_SETTINGS_MODULE=config.settings.production
        # 如果没有production.py，创建一个
        if [ ! -f "config/settings/production.py" ]; then
            cp config/settings/base.py config/settings/production.py
            # 修改生产设置
            cat >> config/settings/production.py << 'PRODEOF'

# 生产环境覆盖设置
import os
from decouple import config

DEBUG = False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# 静态文件设置
STATIC_URL = '/static/'
STATIC_ROOT = config('STATIC_ROOT')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件设置
MEDIA_URL = '/media/'
MEDIA_ROOT = config('MEDIA_ROOT')

# 安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='').split(',')

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
PRODEOF
        fi
    else
        # 创建基础settings文件
        mkdir -p config/settings
        cat > config/settings/production.py << 'SETTINGSEOF'
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
    'apps.share',
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

# 安全设置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS').split(',')
CORS_ALLOW_ALL_ORIGINS = True
SETTINGSEOF
    fi
    
    log_success "ModeShift生产环境配置完成"
}

# 初始化数据库和数据
initialize_complete_database() {
    log_modeshift "初始化完整数据库..."
    
    cd ~/ModeShift
    source venv/bin/activate
    
    # 设置Django设置模块
    if [ -f "config/settings/production.py" ]; then
        export DJANGO_SETTINGS_MODULE=config.settings.production
    else
        export DJANGO_SETTINGS_MODULE=settings
    fi
    
    # 创建必要目录
    mkdir -p logs media staticfiles
    
    # 运行数据库迁移
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput
    
    # 创建超级用户
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')" | python manage.py shell
    
    # 运行初始化命令（如果存在）
    python manage.py loaddata initial_data.json 2>/dev/null || true
    
    # 收集静态文件
    python manage.py collectstatic --noinput --clear
    
    # 设置权限
    chmod -R 755 staticfiles media logs
    chown -R admin:admin .
    
    log_success "完整数据库初始化完成"
}

# 配置Gunicorn服务
setup_gunicorn_service() {
    log_modeshift "配置Gunicorn服务..."
    
    cd ~/ModeShift
    
    # 创建Gunicorn配置
    cat > gunicorn.conf.py << 'EOF'
import multiprocessing
import os

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
errorlog = "/home/admin/ModeShift/logs/gunicorn_error.log"
accesslog = "/home/admin/ModeShift/logs/gunicorn_access.log"
access_log_format = '%h %l %u %t "%r" %s %b "%{Referer}i" "%{User-Agent}i"'
loglevel = "info"
preload_app = True
daemon = False

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
EOF
    
    # 创建启动脚本
    cat > start_modeshift.sh << 'EOF'
#!/bin/bash
cd /home/admin/ModeShift
source venv/bin/activate

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.production

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# 启动Gunicorn
exec gunicorn --config gunicorn.conf.py \
    $(python -c "
import os
import sys
sys.path.append('.')
if os.path.exists('config/wsgi.py'):
    print('config.wsgi:application')
elif os.path.exists('qatoolbox/wsgi.py'):
    print('qatoolbox.wsgi:application')
elif os.path.exists('wsgi.py'):
    print('wsgi:application')
else:
    print('QAToolBox.wsgi:application')
")
EOF
    
    chmod +x start_modeshift.sh
    
    log_success "Gunicorn服务配置完成"
}

# 配置Nginx
setup_nginx_config() {
    log_modeshift "配置Nginx..."
    
    # 创建完整的Nginx配置
    sudo tee /etc/nginx/sites-available/modeshift << EOF
# ModeShift Nginx配置
server {
    listen 80;
    server_name $SERVER_IP $DOMAIN www.$DOMAIN;
    
    client_max_body_size 100M;
    client_body_timeout 60s;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # 静态文件 - 优化缓存
    location /static/ {
        alias /home/admin/ModeShift/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
        
        # 预压缩支持
        location ~* \\.(?:css|js)\$ {
            gzip_static on;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/ModeShift/media/;
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # Favicon
    location = /favicon.ico {
        alias /home/admin/ModeShift/staticfiles/favicon.ico;
        expires 1y;
        access_log off;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
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
        proxy_redirect off;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/modeshift /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/qatoolbox
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 创建系统服务
create_modeshift_service() {
    log_modeshift "创建ModeShift系统服务..."
    
    sudo tee /etc/systemd/system/modeshift.service << EOF
[Unit]
Description=ModeShift Django Application Server
After=network.target

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/home/admin/ModeShift
Environment="PATH=/home/admin/ModeShift/venv/bin"
ExecStart=/home/admin/ModeShift/start_modeshift.sh
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # 停止旧服务
    sudo systemctl stop qatoolbox || true
    sudo systemctl disable qatoolbox || true
    
    # 启动新服务
    sudo systemctl daemon-reload
    sudo systemctl start modeshift
    sudo systemctl enable modeshift
    
    log_success "ModeShift系统服务创建完成"
}

# 配置Redis和其他服务
setup_additional_services() {
    log_modeshift "配置Redis和其他服务..."
    
    # 启动Redis
    sudo systemctl start redis-server
    sudo systemctl enable redis-server
    
    # 配置防火墙
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    
    log_success "其他服务配置完成"
}

# 最终检查和验证
final_verification() {
    log_modeshift "最终验证部署..."
    
    sleep 10
    
    echo ""
    echo "=== 服务状态检查 ==="
    systemctl is-active modeshift && echo "✅ ModeShift服务正常" || echo "❌ ModeShift服务异常"
    systemctl is-active nginx && echo "✅ Nginx服务正常" || echo "❌ Nginx服务异常"
    systemctl is-active redis-server && echo "✅ Redis服务正常" || echo "❌ Redis服务异常"
    
    echo ""
    echo "=== 网站访问测试 ==="
    if curl -f -s http://localhost/ > /dev/null; then
        echo "✅ 网站访问正常"
    else
        echo "❌ 网站访问异常"
        log_warning "查看服务日志："
        sudo journalctl -u modeshift --no-pager -n 5
    fi
    
    if curl -f -s http://localhost/static/admin/css/base.css > /dev/null; then
        echo "✅ 静态文件正常"
    else
        echo "❌ 静态文件异常"
    fi
}

# 显示完成信息
show_completion_info() {
    echo ""
    echo -e "${PURPLE}🎉🎉🎉 ModeShift 完整部署成功！🎉🎉🎉${NC}"
    echo ""
    echo -e "${CYAN}📱 访问地址:${NC}"
    echo -e "   🌐 域名: ${GREEN}http://$DOMAIN${NC}"
    echo -e "   📍 IP: ${GREEN}http://$SERVER_IP${NC}"
    echo ""
    echo -e "${CYAN}🔐 管理后台:${NC}"
    echo -e "   🌐 ${GREEN}http://$DOMAIN/admin/${NC}"
    echo -e "   📍 ${GREEN}http://$SERVER_IP/admin/${NC}"
    echo ""
    echo -e "${CYAN}👤 管理员账号:${NC}"
    echo -e "   用户名: ${GREEN}admin${NC}"
    echo -e "   密码: ${GREEN}admin123456${NC}"
    echo ""
    echo -e "${CYAN}🎨 ModeShift 特性:${NC}"
    echo -e "   - ${YELLOW}四种模式界面${NC} (极客/生活/狂暴/Emo)"
    echo -e "   - ${YELLOW}炫酷UI设计${NC} (霓虹光效/科技感)"
    echo -e "   - ${YELLOW}完整功能${NC} (用户/工具/内容管理)"
    echo -e "   - ${YELLOW}响应式布局${NC} (支持各种设备)"
    echo -e "   - ${YELLOW}现代化架构${NC} (Django + Nginx + Redis)"
    echo ""
    echo -e "${CYAN}🛠️ 管理命令:${NC}"
    echo -e "   查看状态: ${GREEN}sudo systemctl status modeshift${NC}"
    echo -e "   重启服务: ${GREEN}sudo systemctl restart modeshift${NC}"
    echo -e "   查看日志: ${GREEN}tail -f ~/ModeShift/logs/gunicorn_error.log${NC}"
    echo -e "   项目目录: ${GREEN}cd ~/ModeShift${NC}"
    echo ""
    echo -e "${PURPLE}🚀 Four Modes, One Beast - 现在完全部署！${NC}"
}

# 主函数
main() {
    show_modeshift_logo
    log_modeshift "开始ModeShift完整部署..."
    
    cleanup_environment
    install_complete_dependencies
    clone_complete_project
    setup_complete_python_env
    configure_production_settings
    initialize_complete_database
    setup_gunicorn_service
    setup_nginx_config
    create_modeshift_service
    setup_additional_services
    final_verification
    show_completion_info
    
    log_success "ModeShift完整部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，在第$LINENO行"; exit 1' ERR

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
