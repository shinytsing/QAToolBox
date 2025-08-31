#!/bin/bash

# QAToolBox 从GitHub一键部署脚本
# 专为Ubuntu服务器和中国区网络环境优化

set -e

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
GITHUB_REPO="your-username/QAToolBox"  # 请替换为您的GitHub仓库地址
BRANCH="main"  # 或者您的主分支名

# 检查系统
check_system() {
    log_info "检查系统信息..."
    
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        log_error "此脚本仅支持Ubuntu系统"
        exit 1
    fi
    
    log_success "操作系统: $NAME $VERSION"
}

# 安装基础依赖
install_deps() {
    log_info "安装基础依赖..."
    
    # 更新包列表
    sudo apt update
    
    # 安装必要工具
    sudo apt install -y curl wget git python3 python3-pip python3-venv python3-dev
    
    # 安装数据库
    sudo apt install -y postgresql postgresql-contrib postgresql-client
    
    # 安装Redis
    sudo apt install -y redis-server
    
    # 安装Nginx
    sudo apt install -y nginx
    
    # 安装Supervisor
    sudo apt install -y supervisor
    
    # 安装音频处理依赖
    sudo apt install -y ffmpeg libsndfile1-dev
    
    log_success "基础依赖安装完成"
}

# 配置PostgreSQL
setup_postgresql() {
    log_info "配置PostgreSQL..."
    
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    
    # 创建数据库用户和数据库
    sudo -u postgres psql <<EOF
CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';
CREATE DATABASE qatoolbox OWNER qatoolbox;
GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;
ALTER USER qatoolbox CREATEDB;
\q
EOF
    
    log_success "PostgreSQL配置完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis配置完成"
    else
        log_error "Redis配置失败"
        exit 1
    fi
}

# 从GitHub克隆项目
clone_project() {
    log_info "从GitHub克隆项目..."
    
    # 创建项目目录
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    cd $PROJECT_DIR
    
    # 克隆项目
    if [[ -d ".git" ]]; then
        log_info "项目已存在，更新代码..."
        git pull origin $BRANCH
    else
        log_info "克隆新项目..."
        git clone -b $BRANCH https://github.com/$GITHUB_REPO.git .
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
    
    # 配置pip镜像源
    pip install --upgrade pip
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
    
    # 安装依赖
    log_info "安装Python依赖..."
    pip install -r requirements/base.txt
    pip install -r requirements/audio_processing.txt
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

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
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
    }
    
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
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
    
    sudo tee /etc/supervisor/conf.d/qatoolbox.conf > /dev/null <<EOF
[program:qatoolbox]
command=$PROJECT_DIR/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 --timeout 300 config.wsgi:application
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
    
    # 重新加载配置
    sudo supervisorctl reread
    sudo supervisorctl update
    
    log_success "Supervisor配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    sudo systemctl start postgresql
    sudo systemctl start redis-server
    sudo systemctl start nginx
    sudo systemctl start supervisor
    sudo supervisorctl start qatoolbox
    
    log_success "所有服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    if sudo systemctl is-active --quiet postgresql; then
        log_success "PostgreSQL: 运行中"
    else
        log_error "PostgreSQL: 未运行"
    fi
    
    if sudo systemctl is-active --quiet redis-server; then
        log_success "Redis: 运行中"
    else
        log_error "Redis: 未运行"
    fi
    
    if sudo systemctl is-active --quiet nginx; then
        log_success "Nginx: 运行中"
    else
        log_error "Nginx: 未运行"
    fi
    
    if sudo supervisorctl status qatoolbox | grep -q "RUNNING"; then
        log_success "QAToolBox: 运行中"
    else
        log_error "QAToolBox: 未运行"
    fi
    
    log_success "健康检查完成"
}

# 显示部署信息
show_info() {
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
    echo
    echo "⚠️  注意事项:"
    echo "   1. 请及时修改默认密码"
    echo "   2. 建议配置SSL证书"
    echo "   3. 定期备份数据库"
}

# 主函数
main() {
    echo "🚀 QAToolBox GitHub一键部署脚本"
    echo "专为Ubuntu服务器和中国区网络环境优化"
    echo "=================================="
    echo
    
    # 检查系统
    check_system
    
    # 确认部署
    read -p "是否开始部署QAToolBox？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "部署已取消"
        exit 0
    fi
    
    # 执行部署步骤
    install_deps
    setup_postgresql
    setup_redis
    clone_project
    setup_python_env
    setup_env
    run_migrations
    setup_nginx
    setup_supervisor
    start_services
    health_check
    show_info
}

# 执行主函数
main "$@"
