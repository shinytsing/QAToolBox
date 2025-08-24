#!/bin/bash

# QAToolBox 智能一键部署脚本
# 支持本地开发和生产环境部署
# 作者: AI Assistant
# 版本: 2.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 命令不存在"
        return 1
    fi
}

# 检查Python版本
check_python_version() {
    log_info "检查Python版本..."
    
    if command -v python3.9 &> /dev/null; then
        PYTHON_CMD="python3.9"
    elif command -v python3.10 &> /dev/null; then
        PYTHON_CMD="python3.10"
    elif command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        log_error "未找到Python 3.9+版本"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
    log_success "使用Python版本: $PYTHON_VERSION"
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/redhat-release ]; then
            OS="centos"
            PKG_MANAGER="yum"
        elif [ -f /etc/debian_version ]; then
            OS="ubuntu"
            PKG_MANAGER="apt-get"
        else
            OS="linux"
            PKG_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PKG_MANAGER="brew"
    else
        OS="unknown"
        PKG_MANAGER="unknown"
    fi
    
    log_info "检测到操作系统: $OS"
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    case $OS in
        "centos")
            sudo yum update -y
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y postgresql postgresql-server postgresql-contrib redis python3-devel gcc gcc-c++ make libpq-dev
            ;;
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y build-essential postgresql postgresql-contrib redis-server python3-dev libpq-dev
            ;;
        "macos")
            if command -v brew &> /dev/null; then
                brew install postgresql redis
            else
                log_warning "请先安装Homebrew或手动安装PostgreSQL和Redis"
            fi
            ;;
        *)
            log_warning "未知操作系统，请手动安装PostgreSQL和Redis"
            ;;
    esac
}

# 创建虚拟环境
create_venv() {
    log_info "创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        log_warning "虚拟环境已存在，删除重建..."
        rm -rf venv
    fi
    
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    log_success "虚拟环境创建完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    source venv/bin/activate
    
    # 根据环境选择依赖文件
    case $DEPLOY_ENV in
        "production")
            pip install -r requirements/production.txt
            ;;
        "development")
            pip install -r requirements/development.txt
            ;;
        *)
            pip install -r requirements/base.txt
            ;;
    esac
    
    log_success "Python依赖安装完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    # 启动PostgreSQL服务
    case $OS in
        "centos")
            if [ ! -d "/var/lib/pgsql/data" ] || [ -z "$(ls -A /var/lib/pgsql/data)" ]; then
                sudo postgresql-setup initdb
            fi
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
            ;;
        "ubuntu")
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
            ;;
        "macos")
            brew services start postgresql
            ;;
    esac
    
    # 创建数据库和用户
    sudo -u postgres psql -c "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || true
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || true
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" || true
    sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" || true
    
    log_success "数据库配置完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    case $OS in
        "centos"|"ubuntu")
            sudo systemctl enable redis
            sudo systemctl start redis
            ;;
        "macos")
            brew services start redis
            ;;
    esac
    
    log_success "Redis配置完成"
}

# 生成环境配置文件
generate_env_file() {
    log_info "生成环境配置文件..."
    
    # 生成随机密钥
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    cat > .env << EOF
# QAToolBox 环境配置
DJANGO_SECRET_KEY=$SECRET_KEY
DEBUG=$DEBUG_MODE
DJANGO_SETTINGS_MODULE=config.settings.$DEPLOY_ENV

# 允许的主机
ALLOWED_HOSTS=$ALLOWED_HOSTS

# 数据库配置
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT

# Redis配置
REDIS_URL=$REDIS_URL

# API密钥（请根据需要配置）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
AMAP_API_KEY=your_amap_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 其他配置
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
EOF
    
    log_success "环境配置文件已生成: .env"
}

# Django设置
setup_django() {
    log_info "配置Django应用..."
    
    source venv/bin/activate
    
    # 检查Django配置
    python manage.py check
    
    # 创建数据库迁移
    python manage.py makemigrations
    
    # 应用数据库迁移
    python manage.py migrate
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    # 创建超级用户（如果不存在）
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
    
    log_success "Django应用配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    source venv/bin/activate
    
    # 停止现有进程
    pkill -f "runserver\|gunicorn" 2>/dev/null || true
    
    case $DEPLOY_ENV in
        "production")
            log_info "启动Gunicorn生产服务器..."
            nohup gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 300 --max-requests 1000 --preload config.wsgi:application > logs/gunicorn.log 2>&1 &
            ;;
        "development")
            log_info "启动Django开发服务器..."
            nohup python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
            ;;
        *)
            log_info "启动Django开发服务器..."
            nohup python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
            ;;
    esac
    
    sleep 10
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 检查进程
    if pgrep -f "runserver\|gunicorn" > /dev/null; then
        log_success "服务进程运行正常"
    else
        log_error "服务进程未运行"
        return 1
    fi
    
    # 检查HTTP响应
    sleep 5
    if curl -s -I http://localhost:8000/ | grep -q "200\|302"; then
        log_success "HTTP服务响应正常"
    else
        log_warning "HTTP服务响应异常，请检查日志"
    fi
    
    log_success "部署验证完成"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "🎉 QAToolBox 部署完成！"
    echo "======================================"
    echo "🌐 网站地址: http://localhost:8000"
    echo "🌐 外网地址: http://$SERVER_IP:8000 (如果配置了外网IP)"
    echo "👤 管理后台: http://localhost:8000/admin/"
    echo "📋 管理员账号: admin"
    echo "🔑 管理员密码: admin123"
    echo "📂 项目目录: $(pwd)"
    echo "📝 日志目录: $(pwd)/logs/"
    echo "⚙️ 环境配置: .env"
    echo "======================================"
    echo ""
    echo "📋 常用命令:"
    echo "  启动服务: ./deploy/smart_deploy.sh --start"
    echo "  停止服务: ./deploy/smart_deploy.sh --stop"
    echo "  重启服务: ./deploy/smart_deploy.sh --restart"
    echo "  查看日志: tail -f logs/*.log"
    echo "  进入虚拟环境: source venv/bin/activate"
    echo ""
}

# 服务管理
manage_service() {
    case $1 in
        "start")
            start_services
            ;;
        "stop")
            log_info "停止服务..."
            pkill -f "runserver\|gunicorn" 2>/dev/null || true
            log_success "服务已停止"
            ;;
        "restart")
            log_info "重启服务..."
            pkill -f "runserver\|gunicorn" 2>/dev/null || true
            sleep 2
            start_services
            ;;
        "status")
            if pgrep -f "runserver\|gunicorn" > /dev/null; then
                log_success "服务正在运行"
                ps aux | grep -E "runserver|gunicorn" | grep -v grep
            else
                log_warning "服务未运行"
            fi
            ;;
        *)
            log_error "未知服务管理命令: $1"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    # 默认配置
    DEPLOY_ENV="development"
    DEBUG_MODE="True"
    DB_NAME="qatoolbox"
    DB_USER="qatoolbox"
    DB_PASSWORD="qatoolbox123"
    DB_HOST="localhost"
    DB_PORT="5432"
    REDIS_URL="redis://localhost:6379/0"
    ALLOWED_HOSTS="localhost,127.0.0.1"
    SERVER_IP="localhost"
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                DEPLOY_ENV="$2"
                shift 2
                ;;
            --production)
                DEPLOY_ENV="production"
                DEBUG_MODE="False"
                shift
                ;;
            --host)
                ALLOWED_HOSTS="$2"
                SERVER_IP="$2"
                shift 2
                ;;
            --start|--stop|--restart|--status)
                manage_service "${1#--}"
                exit 0
                ;;
            --help)
                echo "QAToolBox 智能部署脚本"
                echo ""
                echo "用法: $0 [选项]"
                echo ""
                echo "选项:"
                echo "  --env ENV          设置环境 (development|production)"
                echo "  --production       生产环境部署"
                echo "  --host HOST        设置允许的主机"
                echo "  --start            启动服务"
                echo "  --stop             停止服务"
                echo "  --restart          重启服务"
                echo "  --status           查看服务状态"
                echo "  --help             显示帮助"
                echo ""
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    log_info "开始QAToolBox智能部署..."
    log_info "部署环境: $DEPLOY_ENV"
    
    # 创建日志目录
    mkdir -p logs
    
    # 执行部署步骤
    detect_os
    check_python_version
    install_system_deps
    create_venv
    install_python_deps
    setup_database
    setup_redis
    generate_env_file
    setup_django
    start_services
    verify_deployment
    show_deployment_info
    
    log_success "QAToolBox部署完成！"
}

# 运行主函数
main "$@"
