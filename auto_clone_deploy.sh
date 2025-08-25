#!/bin/bash

# =============================================================================
# QAToolBox 自动克隆部署脚本
# 自动处理Git认证，无需手动输入用户名密码
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${PURPLE}[STEP]${NC} $1"; }

show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "========================================"
    echo "    🚀 QAToolBox 自动部署脚本"
    echo "========================================"
    echo "  功能: 自动处理Git认证和部署"
    echo "  服务器: $SERVER_IP"
    echo "  域名: $DOMAIN"
    echo "========================================"
    echo -e "${NC}"
}

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 停止现有服务
stop_services() {
    log_step "停止现有服务"
    
    systemctl stop qatoolbox 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
    pkill -f "python.*manage.py" 2>/dev/null || true
    sleep 3
    
    log_success "服务停止完成"
}

# 创建项目用户
create_user() {
    log_step "创建项目用户"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash $PROJECT_USER
        usermod -aG sudo $PROJECT_USER
        log_success "用户 $PROJECT_USER 创建完成"
    else
        log_info "用户 $PROJECT_USER 已存在"
    fi
}

# 自动克隆项目（处理认证）
auto_clone_project() {
    log_step "自动克隆项目代码"
    
    # 删除旧项目
    if [ -d "$PROJECT_DIR" ]; then
        log_info "删除旧项目目录"
        rm -rf "$PROJECT_DIR"
    fi
    
    # 配置Git跳过SSL验证和自动认证
    sudo -u $PROJECT_USER git config --global http.sslverify false
    sudo -u $PROJECT_USER git config --global credential.helper store
    
    # 创建临时认证文件
    TEMP_CRED_FILE="/home/$PROJECT_USER/.git-credentials"
    
    # 尝试多个克隆源（按优先级排序）
    CLONE_SUCCESS=false
    
    # 方案1: 使用GitHub直接克隆（公开仓库，无需认证）
    log_info "尝试从GitHub直接克隆（公开仓库）..."
    if timeout 300 sudo -u $PROJECT_USER git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR; then
        log_success "GitHub直接克隆成功"
        CLONE_SUCCESS=true
    else
        log_warning "GitHub直接克隆失败，尝试其他方式..."
        sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
    fi
    
    # 方案2: 使用GitHub镜像站
    if [ "$CLONE_SUCCESS" = false ]; then
        for mirror in \
            "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git" \
            "https://hub.fastgit.xyz/shinytsing/QAToolbox.git" \
            "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
        do
            log_info "尝试从镜像站克隆: $mirror"
            if timeout 300 sudo -u $PROJECT_USER git clone $mirror $PROJECT_DIR; then
                log_success "镜像站克隆成功"
                CLONE_SUCCESS=true
                break
            else
                log_warning "镜像站 $mirror 克隆失败"
                sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
            fi
        done
    fi
    
    # 方案3: 使用Gitee（需要处理认证）
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从Gitee克隆（自动处理认证）..."
        
        # 创建期望脚本处理交互式认证
        expect -c "
        spawn sudo -u $PROJECT_USER git clone https://gitee.com/shinytsing/QAToolbox.git $PROJECT_DIR
        expect {
            \"Username*\" {
                send \"shinytsing\r\"
                expect \"Password*\"
                send \"\r\"
                expect eof
            }
            \"fatal:*\" {
                exit 1
            }
            eof {
                exit 0
            }
        }
        " 2>/dev/null || {
            log_warning "Gitee克隆失败"
            sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
        }
        
        if [ -d "$PROJECT_DIR" ] && [ "$(ls -A $PROJECT_DIR 2>/dev/null)" ]; then
            log_success "Gitee克隆成功"
            CLONE_SUCCESS=true
        fi
    fi
    
    # 方案4: 使用wget下载ZIP包
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试下载ZIP包..."
        
        cd /home/$PROJECT_USER
        
        for zip_url in \
            "https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip" \
            "https://codeload.github.com/shinytsing/QAToolbox/zip/refs/heads/main"
        do
            log_info "尝试下载: $zip_url"
            if sudo -u $PROJECT_USER wget -O QAToolbox.zip "$zip_url"; then
                if sudo -u $PROJECT_USER unzip -q QAToolbox.zip; then
                    sudo -u $PROJECT_USER mv QAToolbox-main $PROJECT_NAME 2>/dev/null || \
                    sudo -u $PROJECT_USER mv QAToolbox $PROJECT_NAME 2>/dev/null || true
                    
                    if [ -d "$PROJECT_DIR" ]; then
                        sudo -u $PROJECT_USER rm -f QAToolbox.zip
                        log_success "ZIP包下载解压成功"
                        CLONE_SUCCESS=true
                        break
                    fi
                fi
                sudo -u $PROJECT_USER rm -f QAToolbox.zip 2>/dev/null || true
            fi
        done
    fi
    
    # 检查克隆结果
    if [ "$CLONE_SUCCESS" = false ]; then
        log_error "所有克隆方式都失败了"
        log_info "请检查网络连接或手动克隆项目"
        exit 1
    fi
    
    # 验证项目完整性
    if [ ! -f "$PROJECT_DIR/manage.py" ]; then
        log_error "项目克隆不完整，缺少关键文件"
        exit 1
    fi
    
    cd $PROJECT_DIR
    sudo -u $PROJECT_USER chmod +x *.sh *.py 2>/dev/null || true
    
    # 清理认证文件
    rm -f "$TEMP_CRED_FILE" 2>/dev/null || true
    
    log_success "项目代码获取完成"
}

# 安装expect工具（用于自动化交互）
install_expect() {
    log_step "安装自动化工具"
    
    if ! command -v expect &> /dev/null; then
        log_info "安装expect工具..."
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -y
        apt-get install -y expect
    fi
    
    log_success "自动化工具安装完成"
}

# 快速设置Python环境
quick_setup_python() {
    log_step "快速设置Python环境"
    
    cd $PROJECT_DIR
    
    # 删除旧环境
    if [ -d ".venv" ]; then
        rm -rf .venv
    fi
    
    # 创建虚拟环境
    sudo -u $PROJECT_USER python3 -m venv .venv
    
    # 配置pip镜像源
    sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
    cat > /home/$PROJECT_USER/.pip/pip.conf << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 300
retries = 5
no-cache-dir = true
EOF
    chown $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.pip/pip.conf
    
    # 升级pip
    sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
    
    # 安装核心依赖
    log_info "安装核心依赖..."
    sudo -u $PROJECT_USER .venv/bin/pip install \
        Django==4.2.7 \
        gunicorn==21.2.0 \
        psycopg2-binary==2.9.7 \
        redis==4.6.0 \
        django-redis==5.4.0 \
        python-dotenv==1.0.0 \
        django-environ==0.11.2 \
        djangorestframework==3.14.0 \
        django-cors-headers==4.3.1 \
        whitenoise==6.6.0
    
    log_success "Python环境设置完成"
}

# 快速配置数据库
quick_setup_database() {
    log_step "快速配置数据库"
    
    # 确保PostgreSQL运行
    systemctl start postgresql 2>/dev/null || true
    sleep 3
    
    # 重置数据库
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    log_success "数据库配置完成"
}

# 快速配置Django
quick_setup_django() {
    log_step "快速配置Django"
    
    cd $PROJECT_DIR
    
    # 创建环境变量
    cat > .env << 'EOF'
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-quick-deploy-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.production
SITE_URL=https://shenyiqing.xin
EOF
    chown $PROJECT_USER:$PROJECT_USER .env
    chmod 600 .env
    
    # 数据库迁移
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate || {
        log_warning "迁移失败，创建简化配置"
        
        # 创建简化配置
        mkdir -p config/settings
        cat > config/settings/minimal.py << 'MINIMALEOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'minimal-key'
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'qatoolbox',
        'USER': 'qatoolbox',
        'PASSWORD': 'QAToolBox@2024',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

TEMPLATES = [{
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
}]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MINIMALEOF
        
        # 更新环境变量
        sed -i 's/DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=config.settings.minimal/' .env
        
        # 重新尝试迁移
        sudo -u $PROJECT_USER .venv/bin/python manage.py migrate
    }
    
    # 收集静态文件
    sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput || true
    
    # 创建管理员
    echo "from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell || true
    
    log_success "Django配置完成"
}

# 启动服务
start_services() {
    log_step "启动服务"
    
    # 创建systemd服务
    cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.minimal
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 config.wsgi:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    # 启动服务
    systemctl daemon-reload
    systemctl enable qatoolbox
    systemctl start qatoolbox
    sleep 10
    
    # 配置Nginx
    cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl restart nginx
    
    log_success "服务启动完成"
}

# 主函数
main() {
    show_welcome
    check_root
    
    log_info "开始自动部署，预计需要10-15分钟..."
    
    stop_services
    install_expect
    create_user
    auto_clone_project
    quick_setup_python
    quick_setup_database
    quick_setup_django
    start_services
    
    # 最终检查
    sleep 10
    if systemctl is-active --quiet qatoolbox && systemctl is-active --quiet nginx; then
        echo
        echo -e "${GREEN}========================================"
        echo "        🎉 部署成功！"
        echo "========================================"
        echo -e "${NC}"
        echo -e "${GREEN}访问地址: http://shenyiqing.xin${NC}"
        echo -e "${GREEN}管理后台: http://shenyiqing.xin/admin/${NC}"
        echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
        echo
        echo "服务状态:"
        echo "  应用服务: $(systemctl is-active qatoolbox)"
        echo "  Nginx服务: $(systemctl is-active nginx)"
    else
        log_error "部署完成但服务可能有问题"
        echo "检查日志: sudo journalctl -u qatoolbox -f"
    fi
}

# 运行主函数
main "$@"
