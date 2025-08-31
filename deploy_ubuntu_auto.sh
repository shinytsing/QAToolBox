#!/bin/bash

# QAToolBox Ubuntu服务器完全自动化一键部署脚本
# 专为中国区网络环境优化，无需任何用户交互

set -e  # 遇到错误立即退出

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
    server_name _;
    
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
    pip install librosa>=0.10.0 numpy>=1.24.0 scipy>=1.10.0 soundfile>=0.12.0 pydub>=0.25.0 audioread>=3.0.0 resampy>=0.4.0
    
    # 安装生产环境依赖
    log_info "安装生产环境依赖..."
    pip install -r requirements/production.txt
    
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
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1

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

# 运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # 设置环境变量
    export $(cat .env | xargs)
    
    # 运行迁移
    python manage.py makemigrations
    python manage.py migrate
    
    # 创建超级用户
    log_info "创建超级用户..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
    
    # 收集静态文件
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput
    
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
    
    # 执行部署步骤
    setup_china_mirrors
    install_system_deps
    setup_postgresql
    setup_redis
    create_project_dir
    clone_project
    setup_python_env
    setup_env
    run_migrations
    setup_nginx
    setup_supervisor
    start_services
    health_check
    show_deployment_info
    
    log_success "🎉 部署完成！QAToolBox已成功运行在您的服务器上！"
}

# 执行主函数
main "$@"
