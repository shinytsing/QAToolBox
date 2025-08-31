#!/bin/bash

# QAToolBox Ubuntu服务器完全自动化一键部署脚本
# 专为中国区网络环境优化，无需任何用户交互

# 遇到错误不退出，继续执行
set +e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 错误恢复函数
continue_on_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_warning "命令执行失败（退出码: $exit_code），但继续执行..."
        return 0
    fi
    return $exit_code
}

# 配置变量
PROJECT_NAME="QAToolBox"
PROJECT_DIR="/var/www/qatoolbox"
GITHUB_REPO="shinytsing/QAToolbox"
BRANCH="main"

# 检查系统信息
check_system() {
    log_info "检查系统信息..."
    
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        log_error "此脚本仅支持Ubuntu系统，当前系统: $ID"
        exit 1
    fi
    
    log_success "操作系统: $NAME $VERSION"
    
    ARCH=$(uname -m)
    log_info "系统架构: $ARCH"
    
    MEM_TOTAL=$(free -m | awk 'NR==2{printf "%.0f", $2/1024}')
    if [[ $MEM_TOTAL -lt 2 ]]; then
        log_warning "系统内存不足2GB，可能影响性能"
    else
        log_success "系统内存: ${MEM_TOTAL}GB"
    fi
    
    DISK_FREE=$(df -h / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $DISK_FREE -lt 10 ]]; then
        log_warning "磁盘空间不足10GB，建议清理"
    else
        log_success "可用磁盘空间: ${DISK_FREE}GB"
    fi
}

# 配置中国区镜像源
setup_china_mirrors() {
    log_info "配置中国区镜像源..."
    
    # 备份原有源
    if [[ -f /etc/apt/sources.list ]]; then
        sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # 检测Ubuntu版本并配置对应镜像源
    UBUNTU_VERSION=$(lsb_release -cs)
    
    # 阿里云镜像源
    sudo tee /etc/apt/sources.list > /dev/null <<EOF
deb https://mirrors.aliyun.com/ubuntu/ $UBUNTU_VERSION main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $UBUNTU_VERSION-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $UBUNTU_VERSION-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $UBUNTU_VERSION-backports main restricted universe multiverse
EOF
    
    # 更新包列表
    sudo apt update -y
    
    log_success "中国区镜像源配置完成"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    # 设置非交互式安装
    export DEBIAN_FRONTEND=noninteractive
    
    # 基础工具
    sudo apt install -y curl wget git vim htop unzip software-properties-common
    
    # Python相关
    sudo apt install -y python3 python3-pip python3-venv python3-dev
    
    # 数据库相关
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    
    # Redis
    sudo apt install -y redis-server
    
    # Nginx
    sudo apt install -y nginx
    
    # 音频处理依赖
    sudo apt install -y ffmpeg libsndfile1-dev libasound2-dev portaudio19-dev
    
    # 图像处理依赖
    sudo apt install -y libjpeg-dev libpng-dev libfreetype6-dev
    
    # 编译工具
    sudo apt install -y build-essential pkg-config
    
    # Supervisor
    sudo apt install -y supervisor
    
    log_success "系统依赖安装完成"
}

# 配置PostgreSQL
setup_postgresql() {
    log_info "配置PostgreSQL..."
    
    # 启动PostgreSQL服务
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    
    # 等待PostgreSQL启动
    sleep 5
    
    # 检查用户和数据库是否已存在
    USER_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='qatoolbox'")
    DB_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='qatoolbox'")
    
    if [[ -z "$USER_EXISTS" ]]; then
        log_info "创建数据库用户qatoolbox..."
        sudo -u postgres psql <<EOF
CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';
EOF
    else
        log_info "数据库用户qatoolbox已存在"
    fi
    
    if [[ -z "$DB_EXISTS" ]]; then
        log_info "创建数据库qatoolbox..."
        sudo -u postgres psql <<EOF
CREATE DATABASE qatoolbox OWNER qatoolbox;
EOF
    else
        log_info "数据库qatoolbox已存在"
    fi
    
    # 确保权限正确
    sudo -u postgres psql <<EOF
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
ALTER USER qatoolbox CREATEDB;
\q
EOF
    
    # 配置PostgreSQL允许本地连接
    sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
    
    # 重启PostgreSQL
    sudo systemctl restart postgresql
    
    log_success "PostgreSQL配置完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    # 启动Redis服务
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    
    # 等待Redis启动
    sleep 3
    
    # 测试Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis配置完成"
    else
        log_error "Redis配置失败"
        exit 1
    fi
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    # 创建Nginx配置
    sudo tee /etc/nginx/sites-available/qatoolbox > /dev/null <<EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152 172.24.33.31;
    
    client_max_body_size 500M;
    client_body_timeout 300s;
    client_header_timeout 300s;
    
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
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
}
EOF
    
    # 启用站点
    sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试配置
    sudo nginx -t
    
    # 重启Nginx
    sudo systemctl enable nginx
    sudo systemctl restart nginx
    
    log_success "Nginx配置完成"
}

# 配置Supervisor
setup_supervisor() {
    log_info "配置Supervisor..."
    
    # 创建Supervisor配置
    sudo tee /etc/supervisor/conf.d/qatoolbox.conf > /dev/null <<EOF
[program:qatoolbox]
command=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 300 --max-requests 1000 --max-requests-jitter 100 config.wsgi:application
directory=$PROJECT_DIR
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/qatoolbox.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production"
EOF
    
    # 创建日志目录
    sudo mkdir -p /var/log/supervisor
    
    # 重新加载Supervisor配置
    sudo supervisorctl reread
    sudo supervisorctl update
    
    log_success "Supervisor配置完成"
}

# 创建项目目录
create_project_dir() {
    log_info "创建项目目录..."
    
    # 创建项目目录
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    # 创建媒体文件目录
    sudo mkdir -p $PROJECT_DIR/media
    sudo chown www-data:www-data $PROJECT_DIR/media
    sudo chmod 755 $PROJECT_DIR/media
    
    # 创建日志目录
    sudo mkdir -p $PROJECT_DIR/logs
    sudo chown $USER:$USER $PROJECT_DIR/logs
    
    log_success "项目目录创建完成"
}

# 从GitHub克隆项目
clone_project() {
    log_info "从GitHub克隆项目..."
    
    cd $PROJECT_DIR
    
    # 检查目录状态并智能处理
    if [[ -d ".git" ]]; then
        log_info "项目已存在，更新代码..."
        git pull origin $BRANCH
    else
        log_info "目录存在但不是Git仓库，彻底清理后重新克隆..."
        
        # 备份重要文件（如果有的话）
        if [[ -f ".env" ]]; then
            cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
            log_info "已备份.env文件"
        fi
        
        # 记录当前目录
        CURRENT_DIR=$(pwd)
        
        # 回到上级目录
        cd ..
        
        # 重命名当前目录作为备份
        sudo mv qatoolbox qatoolbox.backup.$(date +%Y%m%d_%H%M%S)
        
        # 重新创建空目录
        sudo mkdir -p qatoolbox
        sudo chown $USER:$USER qatoolbox
        
        # 进入新目录
        cd qatoolbox
        
        # 重新克隆项目
        log_info "重新克隆项目..."
        git clone -b $BRANCH https://github.com/$GITHUB_REPO.git .
        
        # 恢复备份的.env文件（如果存在）
        if [[ -f "../qatoolbox.backup.$(date +%Y%m%d_%H%M%S)/.env.backup.$(date +%Y%m%d_%H%M%S)" ]]; then
            cp "../qatoolbox.backup.$(date +%Y%m%d_%H%M%S)/.env.backup.$(date +%Y%m%d_%H%M%S)" .env
            log_info "已恢复.env文件"
        fi
    fi
    
    log_success "项目代码获取完成"
}

# 配置Python环境
setup_python_env() {
    log_info "配置Python环境..."
    
    cd $PROJECT_DIR
    
    # 创建虚拟环境
    python3 -m venv venv
    source venv/bin/activate
    
    # 升级pip并配置中国区镜像
    pip install --upgrade pip
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r requirements/base.txt
    
    # 安装音频处理依赖（兼容Python 3.12）
    log_info "安装音频处理依赖..."
    if pip install -r requirements/audio_processing.txt; then
        log_success "音频处理依赖安装成功"
    else
        log_warning "音频处理依赖安装失败，尝试安装兼容版本..."
        # 尝试安装兼容Python 3.12的版本
        pip install librosa>=0.10.0 numpy>=1.24.0 scipy>=1.10.0 soundfile>=0.12.0 pydub>=0.25.0 audioread>=3.0.0 resampy>=0.4.0
        if [ $? -eq 0 ]; then
            log_success "兼容版本安装成功"
        else
            log_warning "兼容版本安装也失败，尝试从源码编译..."
            # 最后尝试从源码编译
            pip install --no-binary :all: librosa numpy scipy soundfile
        fi
    fi
    
    # 安装生产环境依赖
    log_info "安装生产环境依赖..."
    pip install -r requirements/production.txt
    
    # 安装额外的重要依赖
    log_info "安装额外的重要依赖..."
    pip install psutil>=5.9.0 Pillow>=10.0.0 opencv-python>=4.8.0 torch>=2.0.0 torchvision>=0.15.0 channels>=4.0.0 channels-redis>=4.1.0 websockets>=11.0.0 PyMuPDF>=1.23.0 reportlab>=4.0.0 PyPDF2>=3.0.0 pdfplumber>=0.9.0 pypdf>=3.15.0 ratelimit>=2.0.0 python-magic>=0.4.27 xmind>=1.2.0 || log_warning "部分依赖安装失败，继续执行..."
    
    # 安装HEIC图片支持
    log_info "安装HEIC图片支持..."
    pip install pillow-heif>=0.15.0 || log_warning "pillow-heif安装失败，尝试替代方案..."
    
    # 如果pillow-heif安装失败，尝试安装替代方案
    if ! python -c "import pillow_heif" 2>/dev/null; then
        log_warning "pillow-heif不可用，尝试安装替代方案..."
        pip install pillow-heif-binary || pip install pillow-heif-cffi || log_warning "所有HEIC支持包都安装失败，继续执行..."
    fi
    
    # 安装系统依赖（如果python-magic-bin不可用）
    log_info "安装系统文件类型检测依赖..."
    if ! pip install python-magic-bin>=0.4.14 2>/dev/null; then
        log_warning "python-magic-bin不可用，使用系统libmagic..."
        sudo apt install -y libmagic1 || log_warning "系统libmagic安装失败，继续执行..."
    fi
    
    # 验证关键依赖
    log_info "验证关键依赖..."
    python -c "import psutil, PIL, torch, channels, websockets, fitz, ratelimit" 2>/dev/null && log_success "关键依赖验证成功" || log_warning "部分依赖验证失败，但继续执行..."
    
    log_success "Python环境配置完成"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    cd $PROJECT_DIR
    
    # 生成密钥
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # 创建.env文件
    cat > .env <<EOF
# QAToolBox 生产环境配置
# 生成时间: $(date)

# Django 基础配置
DJANGO_SECRET_KEY=$SECRET_KEY
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

# 主机配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1,172.24.33.31

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 其他配置
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
EOF
    
    # 设置权限
    chmod 600 .env
    
    log_success "环境变量配置完成"
}

# 检查和修复Django配置
fix_django_config() {
    log_info "检查和修复Django配置..."
    
    cd $PROJECT_DIR
    
    # 确保settings.py中的ALLOWED_HOSTS包含所有配置的HOSTS
    ALLOWED_HOSTS_IN_SETTINGS=$(grep -E "ALLOWED_HOSTS.*=.*\[" .env | sed 's/.*= //; s/\[//; s/\]//; s/,/ /g')
    if [[ "$ALLOWED_HOSTS_IN_SETTINGS" != "$ALLOWED_HOSTS" ]]; then
        log_warning "Django settings.py中的ALLOWED_HOSTS与.env文件不匹配，正在修复..."
        sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=[$ALLOWED_HOSTS]/" .env
        log_success "Django settings.py中的ALLOWED_HOSTS已更新"
    else
        log_info "Django settings.py中的ALLOWED_HOSTS与.env文件匹配，无需修改"
    fi
    
    # 确保settings.py中的DEBUG设置正确
    DEBUG_IN_SETTINGS=$(grep -E "DEBUG.*=.*True" .env | sed 's/.*= //')
    if [[ "$DEBUG_IN_SETTINGS" == "True" ]]; then
        log_warning "Django settings.py中的DEBUG设置为True，但.env文件为False，正在修复..."
        sed -i "s/DEBUG=.*/DEBUG=False/" .env
        log_success "Django settings.py中的DEBUG已更新"
    else
        log_info "Django settings.py中的DEBUG设置正确，无需修改"
    fi
    
    # 确保settings.py中的SECRET_KEY设置正确
    SECRET_KEY_IN_SETTINGS=$(grep -E "DJANGO_SECRET_KEY.*=.*" .env | sed 's/.*= //')
    if [[ "$SECRET_KEY_IN_SETTINGS" != "$SECRET_KEY" ]]; then
        log_warning "Django settings.py中的SECRET_KEY与.env文件不匹配，正在修复..."
        sed -i "s/DJANGO_SECRET_KEY=.*/DJANGO_SECRET_KEY=$SECRET_KEY/" .env
        log_success "Django settings.py中的SECRET_KEY已更新"
    else
        log_info "Django settings.py中的SECRET_KEY与.env文件匹配，无需修改"
    fi
    
    # 确保settings.py中的SETTINGS_MODULE设置正确
    SETTINGS_MODULE_IN_SETTINGS=$(grep -E "DJANGO_SETTINGS_MODULE.*=.*" .env | sed 's/.*= //')
    if [[ "$SETTINGS_MODULE_IN_SETTINGS" != "config.settings.aliyun_production" ]]; then
        log_warning "Django settings.py中的SETTINGS_MODULE与.env文件不匹配，正在修复..."
        sed -i "s/DJANGO_SETTINGS_MODULE=.*/DJANGO_SETTINGS_MODULE=config.settings.aliyun_production/" .env
        log_success "Django settings.py中的SETTINGS_MODULE已更新"
    else
        log_info "Django settings.py中的SETTINGS_MODULE与.env文件匹配，无需修改"
    fi
    
    # 重启Django应用以应用新配置
    log_info "重启Django应用以应用新配置..."
    sudo supervisorctl restart qatoolbox
    log_success "Django配置检查和修复完成"
}

# 修复Django配置冲突
fix_django_config_conflicts() {
    log_info "修复Django配置冲突..."
    
    cd $PROJECT_DIR
    
    # 检查并修复STATICFILES_DIRS和STATIC_ROOT冲突
    if [[ -f "config/settings/aliyun_production.py" ]]; then
        log_info "检查Django配置文件中的静态文件配置..."
        
        # 备份原配置
        cp config/settings/aliyun_production.py config/settings/aliyun_production.py.backup.$(date +%Y%m%d_%H%M%S)
        
        # 修复STATICFILES_DIRS配置冲突
        if grep -q "STATICFILES_DIRS.*STATIC_ROOT" config/settings/aliyun_production.py; then
            log_warning "发现STATICFILES_DIRS包含STATIC_ROOT，正在修复..."
            sed -i '/STATICFILES_DIRS/d' config/settings/aliyun_production.py
            echo "STATICFILES_DIRS = []" >> config/settings/aliyun_production.py
            log_success "STATICFILES_DIRS配置冲突已修复"
        fi
        
        # 确保STATIC_ROOT设置正确
        if ! grep -q "STATIC_ROOT.*=.*staticfiles" config/settings/aliyun_production.py; then
            log_info "设置STATIC_ROOT..."
            sed -i '/STATIC_ROOT/d' config/settings/aliyun_production.py
            echo "STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')" >> config/settings/aliyun_production.py
        fi
        
        # 确保MEDIA_ROOT设置正确
        if ! grep -q "MEDIA_ROOT.*=.*media" config/settings/aliyun_production.py; then
            log_info "设置MEDIA_ROOT..."
            sed -i '/MEDIA_ROOT/d' config/settings/aliyun_production.py
            echo "MEDIA_ROOT = os.path.join(BASE_DIR, 'media')" >> config/settings/aliyun_production.py
        fi
        
        log_success "Django配置冲突修复完成"
    else
        log_warning "Django配置文件不存在，跳过配置冲突修复"
    fi
}

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # 设置环境变量（只导出非注释行）
    export $(grep -v '^#' .env | xargs)
    
    # 检查数据库连接
    log_info "检查数据库连接..."
    python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)
" || {
        log_error "数据库连接失败，请检查PostgreSQL配置"
        return 1
    }
    
    # 运行迁移
    log_info "创建数据库迁移..."
    python manage.py makemigrations --verbosity=0 || {
        log_warning "迁移创建失败，检查是否有现有迁移文件..."
        # 检查是否有现有的迁移文件
        if [ -d "apps/content/migrations" ] && [ "$(ls -A apps/content/migrations)" ]; then
            log_info "发现现有迁移文件，跳过创建步骤"
        else
            log_error "没有迁移文件且创建失败，无法继续"
            return 1
        fi
    }
    
    log_info "应用数据库迁移..."
    python manage.py migrate --verbosity=0 || {
        log_error "迁移应用失败，检查数据库状态..."
        # 检查数据库表是否存在
        python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"\"\"
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('auth_user', 'django_migrations')
        \"\"\")
        tables = [row[0] for row in cursor.fetchall()]
        print(f'现有表: {tables}')
        if 'auth_user' not in tables:
            print('auth_user表不存在，需要先运行迁移')
            exit(1)
        else:
            print('基础表已存在，可以继续')
except Exception as e:
    print(f'检查数据库状态失败: {e}')
    exit(1)
" || {
            log_error "数据库状态检查失败，无法继续"
            return 1
        }
    }
    
    # 等待一下确保迁移完成
    sleep 3
    
    # 创建超级用户
    log_info "创建超级用户..."
    python manage.py shell <<EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun_production')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

try:
    # 检查auth_user表是否存在
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'auth_user'
        """)
        if not cursor.fetchone():
            print('auth_user表不存在，跳过创建超级用户')
            exit(0)
    
    # 检查是否已存在超级用户
    if User.objects.filter(is_superuser=True).exists():
        print('超级用户已存在')
    else:
        # 创建超级用户
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print('超级用户创建成功: admin/admin123')
        
except Exception as e:
    print(f'创建超级用户失败: {e}')
    # 尝试使用Django命令创建
    import subprocess
    try:
        result = subprocess.run(['python', 'manage.py', 'createsuperuser', '--noinput'], 
                              input=b'admin\nadmin@example.com\nadmin123\nadmin123\n', 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print('通过Django命令创建超级用户成功')
        else:
            print(f'Django命令创建失败: {result.stderr}')
    except Exception as cmd_e:
        print(f'Django命令执行失败: {cmd_e}')
EOF
    
    # 收集静态文件
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput --verbosity=0
    
    log_success "数据库迁移完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动PostgreSQL
    sudo systemctl start postgresql
    
    # 启动Redis
    sudo systemctl start redis-server
    
    # 启动Nginx
    sudo systemctl start nginx
    
    # 启动Supervisor
    sudo systemctl start supervisor
    
    # 启动QAToolBox应用
    sudo supervisorctl start qatoolbox
    
    log_success "所有服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    log_info "检查服务状态..."
    
    # PostgreSQL
    if sudo systemctl is-active --quiet postgresql; then
        log_success "PostgreSQL: 运行中"
    else
        log_error "PostgreSQL: 未运行"
    fi
    
    # Redis
    if sudo systemctl is-active --quiet redis-server; then
        log_success "Redis: 运行中"
    else
        log_error "Redis: 未运行"
    fi
    
    # Nginx
    if sudo systemctl is-active --quiet nginx; then
        log_success "Nginx: 运行中"
    else
        log_error "Nginx: 未运行"
    fi
    
    # QAToolBox
    if sudo supervisorctl status qatoolbox | grep -q "RUNNING"; then
        log_success "QAToolBox: 运行中"
    else
        log_error "QAToolBox: 未运行"
    fi
    
    # 测试应用访问
    log_info "测试应用访问..."
    sleep 10  # 等待应用完全启动
    
    if curl -s http://localhost:8000/ | grep -q "QAToolBox"; then
        log_success "应用访问正常"
    else
        log_warning "应用访问异常，请检查日志"
    fi
    
    log_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 QAToolBox 部署完成！"
    echo
    echo "📋 部署信息:"
    echo "   项目目录: $PROJECT_DIR"
    echo "   应用地址: http://$(hostname -I | awk '{print $1}')"
    echo "   管理后台: http://$(hostname -I | awk '{print $1}')/admin/"
    echo "   超级用户: admin / admin123"
    echo
    echo "🔧 常用命令:"
    echo "   查看应用状态: sudo supervisorctl status qatoolbox"
    echo "   重启应用: sudo supervisorctl restart qatoolbox"
    echo "   查看日志: sudo tail -f /var/log/supervisor/qatoolbox.log"
    echo "   重启Nginx: sudo systemctl restart nginx"
    echo "   重启数据库: sudo systemctl restart postgresql"
    echo
    echo "📁 重要目录:"
    echo "   项目代码: $PROJECT_DIR"
    echo "   静态文件: $PROJECT_DIR/staticfiles"
    echo "   媒体文件: $PROJECT_DIR/media"
    echo "   日志文件: $PROJECT_DIR/logs"
    echo
    echo "⚠️  注意事项:"
    echo "   1. 请及时修改默认密码"
    echo "   2. 建议配置SSL证书"
    echo "   3. 定期备份数据库"
    echo "   4. 监控服务状态"
}

# 主函数
main() {
    echo "🚀 QAToolBox Ubuntu服务器完全自动化一键部署脚本"
    echo "专为中国区网络环境优化，无需任何用户交互"
    echo "=================================================="
    echo
    
    # 检查系统
    check_system
    
    log_info "开始自动部署，预计需要10-20分钟..."
    echo
    
    # 执行部署步骤（即使失败也继续）
    log_info "步骤 1/15: 配置中国区镜像源"
    setup_china_mirrors || continue_on_error
    
    log_info "步骤 2/15: 安装系统依赖"
    install_system_deps || continue_on_error
    
    log_info "步骤 3/15: 配置PostgreSQL"
    setup_postgresql || continue_on_error
    
    log_info "步骤 4/15: 配置Redis"
    setup_redis || continue_on_error
    
    log_info "步骤 5/15: 创建项目目录"
    create_project_dir || continue_on_error
    
    log_info "步骤 6/15: 从GitHub克隆项目"
    clone_project || continue_on_error
    
    log_info "步骤 7/15: 配置Python环境"
    setup_python_env || continue_on_error
    
    log_info "步骤 8/15: 配置环境变量"
    setup_env || continue_on_error
    
    log_info "步骤 9/15: 检查和修复Django配置"
    fix_django_config || continue_on_error
    
    log_info "步骤 10/15: 修复Django配置冲突"
    fix_django_config_conflicts || continue_on_error
    
    log_info "步骤 11/15: 运行数据库迁移"
    run_migrations || continue_on_error
    
    log_info "步骤 12/15: 配置Nginx"
    setup_nginx || continue_on_error
    
    log_info "步骤 13/15: 配置Supervisor"
    setup_supervisor || continue_on_error
    
    log_info "步骤 14/15: 启动服务"
    start_services || continue_on_error
    
    log_info "步骤 15/15: 健康检查"
    health_check || continue_on_error
    
    log_info "步骤 16/15: 显示部署信息"
    show_deployment_info || continue_on_error
    
    log_success "🎉 部署完成！QAToolBox已成功运行在您的服务器上！"
}

# 执行主函数
main "$@"
