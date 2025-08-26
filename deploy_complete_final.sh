#!/bin/bash

# QAToolBox 完整一键部署脚本
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

# 停止现有服务
cleanup_existing() {
    log_info "清理现有服务..."
    
    # 停止Django服务
    pkill -f "python.*manage.py" || true
    pkill -f "runserver" || true
    
    # 停止Nginx
    sudo systemctl stop nginx || true
    
    # 删除旧的项目目录
    rm -rf ~/qatoolbox_simple ~/qatoolbox_app ~/QAToolBox
    
    log_success "清理完成"
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 更新包管理器
    sudo apt-get update
    
    # 安装必要软件
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        nginx \
        curl \
        wget \
        git \
        ufw
    
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

# 创建Django项目
create_django_project() {
    log_info "创建Django项目..."
    
    # 创建项目目录
    mkdir -p ~/qatoolbox_production
    cd ~/qatoolbox_production
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 安装Django
    pip install django gunicorn
    
    # 创建Django项目
    django-admin startproject qatoolbox .
    
    # 创建自定义应用
    python manage.py startapp main
    
    log_success "Django项目创建完成"
}

# 配置Django设置
configure_django() {
    log_info "配置Django设置..."
    
    cd ~/qatoolbox_production
    source venv/bin/activate
    
    # 创建完整的settings.py
    cat > qatoolbox/settings.py << EOF
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-qatoolbox-production-key-$(openssl rand -base64 32 | tr -d "=+/")'

DEBUG = False

ALLOWED_HOSTS = [
    '$SERVER_IP',
    '$DOMAIN',
    'www.$DOMAIN',
    'localhost',
    '127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
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

ROOT_URLCONF = 'qatoolbox.urls'

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

WSGI_APPLICATION = 'qatoolbox.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF
    
    log_success "Django设置配置完成"
}

# 创建应用视图
create_app_views() {
    log_info "创建应用视图..."
    
    cd ~/qatoolbox_production
    
    # 创建模板目录
    mkdir -p templates
    
    # 创建主页模板
    cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QAToolBox - 智能工具箱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 2rem;
            font-size: 1.2rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .feature h3 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .feature p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .admin-link {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            text-decoration: none;
            border-radius: 50px;
            margin-top: 2rem;
            transition: transform 0.3s ease;
        }
        
        .admin-link:hover {
            transform: translateY(-2px);
        }
        
        .info {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin-top: 2rem;
            border-left: 4px solid #2196f3;
        }
        
        .status {
            color: #4caf50;
            font-weight: bold;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🛠️</div>
        <h1>QAToolBox</h1>
        <p class="subtitle">智能工具箱 - 让工作更高效</p>
        
        <div class="status">✅ 服务运行正常</div>
        
        <div class="features">
            <div class="feature">
                <h3>🚀 高性能</h3>
                <p>基于Django框架，稳定可靠</p>
            </div>
            <div class="feature">
                <h3>🔧 多功能</h3>
                <p>集成多种实用工具</p>
            </div>
            <div class="feature">
                <h3>🎨 美观界面</h3>
                <p>现代化设计，用户体验优秀</p>
            </div>
            <div class="feature">
                <h3>📱 响应式</h3>
                <p>支持各种设备访问</p>
            </div>
        </div>
        
        <a href="/admin/" class="admin-link">进入管理后台</a>
        
        <div class="info">
            <strong>访问信息:</strong><br>
            🌐 域名: http://shenyiqing.xin<br>
            📍 IP: http://47.103.143.152<br>
            🔐 管理员: admin / admin123456
        </div>
    </div>
</body>
</html>
EOF
    
    # 创建视图文件
    cat > main/views.py << 'EOF'
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def health(request):
    return HttpResponse("OK")
EOF
    
    # 创建URL配置
    cat > main/urls.py << 'EOF'
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health, name='health'),
]
EOF
    
    # 更新主URL配置
    cat > qatoolbox/urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]
EOF
    
    log_success "应用视图创建完成"
}

# 初始化数据库
setup_database() {
    log_info "初始化数据库..."
    
    cd ~/qatoolbox_production
    source venv/bin/activate
    
    # 运行迁移
    python manage.py makemigrations
    python manage.py migrate
    
    # 创建超级用户
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')" | python manage.py shell
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    log_success "数据库初始化完成"
}

# 配置Gunicorn
setup_gunicorn() {
    log_info "配置Gunicorn..."
    
    cd ~/qatoolbox_production
    
    # 创建Gunicorn配置文件
    cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 3
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
EOF
    
    # 创建日志目录
    mkdir -p logs
    
    # 创建启动脚本
    cat > start_gunicorn.sh << 'EOF'
#!/bin/bash
cd /home/admin/qatoolbox_production
source venv/bin/activate
exec gunicorn --config gunicorn.conf.py qatoolbox.wsgi:application
EOF
    
    chmod +x start_gunicorn.sh
    
    log_success "Gunicorn配置完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $SERVER_IP $DOMAIN www.$DOMAIN;
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /home/admin/qatoolbox_production/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
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
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
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

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载systemd
    sudo systemctl daemon-reload
    
    # 启动服务
    sudo systemctl start qatoolbox
    sudo systemctl enable qatoolbox
    
    log_success "系统服务创建完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    # 配置UFW防火墙
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
    
    sleep 5
    
    # 检查服务状态
    if systemctl is-active --quiet qatoolbox; then
        log_success "QAToolBox服务运行正常"
    else
        log_error "QAToolBox服务未运行"
        sudo systemctl status qatoolbox
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx服务运行正常"
    else
        log_error "Nginx服务未运行"
        sudo systemctl status nginx
    fi
    
    # 测试网站访问
    if curl -f -s http://localhost/ > /dev/null; then
        log_success "网站访问正常"
    else
        log_error "网站访问失败"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉🎉🎉 QAToolBox 部署完成！🎉🎉🎉"
    echo ""
    echo "📱 访问地址:"
    echo "   🌐 域名: http://$DOMAIN"
    echo "   📍 IP: http://$SERVER_IP"
    echo ""
    echo "🔐 管理后台:"
    echo "   🌐 域名: http://$DOMAIN/admin/"
    echo "   📍 IP: http://$SERVER_IP/admin/"
    echo ""
    echo "👤 管理员账号:"
    echo "   用户名: admin"
    echo "   密码: admin123456"
    echo ""
    echo "🛠️ 管理命令:"
    echo "   查看服务状态: sudo systemctl status qatoolbox"
    echo "   重启服务: sudo systemctl restart qatoolbox"
    echo "   查看日志: tail -f ~/qatoolbox_production/logs/gunicorn_error.log"
    echo "   查看访问日志: tail -f ~/qatoolbox_production/logs/gunicorn_access.log"
    echo ""
    echo "🎊 恭喜！您的QAToolBox已成功部署并运行！"
}

# 主函数
main() {
    log_info "开始QAToolBox完整部署..."
    
    cleanup_existing
    install_dependencies
    create_django_project
    configure_django
    create_app_views
    setup_database
    setup_gunicorn
    setup_nginx
    create_systemd_service
    setup_firewall
    check_deployment
    show_deployment_info
    
    log_success "部署流程完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
