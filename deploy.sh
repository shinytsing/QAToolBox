#!/bin/bash

# QAToolBox 优化部署脚本
# 支持多种部署环境和配置

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] $1${NC}"
}

# 默认配置
ENVIRONMENT="production"
SERVER_IP=""
SERVER_USER="admin"
PROJECT_PATH="/home/admin/QAToolBox"
GIT_REPO="https://github.com/shinytsing/QAToolbox.git"
BRANCH="main"
SKIP_TESTS=false
SKIP_MIGRATIONS=false

# 显示帮助信息
show_help() {
    echo "QAToolBox 部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -e, --environment ENV    部署环境 (development/production) [默认: production]"
    echo "  -s, --server IP          服务器IP地址"
    echo "  -u, --user USER          服务器用户名 [默认: admin]"
    echo "  -p, --path PATH          项目路径 [默认: /home/admin/QAToolBox]"
    echo "  -b, --branch BRANCH      Git分支 [默认: main]"
    echo "  --skip-tests             跳过测试"
    echo "  --skip-migrations        跳过数据库迁移"
    echo "  -h, --help               显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 -e production -s 47.103.143.152"
    echo "  $0 -e development -s localhost -u root"
    echo ""
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -s|--server)
                SERVER_IP="$2"
                shift 2
                ;;
            -u|--user)
                SERVER_USER="$2"
                shift 2
                ;;
            -p|--path)
                PROJECT_PATH="$2"
                shift 2
                ;;
            -b|--branch)
                BRANCH="$2"
                shift 2
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --skip-migrations)
                SKIP_MIGRATIONS=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 验证配置
validate_config() {
    if [[ -z "$SERVER_IP" ]]; then
        error "请指定服务器IP地址 (-s 选项)"
        exit 1
    fi
    
    if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
        error "环境必须是 development 或 production"
        exit 1
    fi
}

# 检查SSH连接
check_ssh() {
    log "检查SSH连接到 $SERVER_IP..."
    if ! ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
        error "无法连接到服务器 $SERVER_IP"
        echo "请确保："
        echo "1. 服务器IP正确: $SERVER_IP"
        echo "2. 用户名正确: $SERVER_USER"
        echo "3. SSH密钥已配置或密码认证已启用"
        echo "4. 服务器防火墙允许SSH连接"
        exit 1
    fi
    log "SSH连接成功！"
}

# 安装系统依赖
install_system_deps() {
    log "安装系统依赖..."
    ssh $SERVER_USER@$SERVER_IP "
        # 更新系统包
        sudo apt update
        
        # 安装Python和相关工具
        sudo apt install -y python3 python3-pip python3-venv python3-dev
        
        # 安装Git
        sudo apt install -y git
        
        # 安装其他必要工具
        sudo apt install -y curl wget unzip nginx
        
        # 安装Redis（如果不存在）
        if ! command -v redis-server &> /dev/null; then
            sudo apt install -y redis-server
            sudo systemctl enable redis-server
            sudo systemctl start redis-server
        fi
        
        log '系统依赖安装完成'
    "
}

# 克隆或更新项目代码
setup_project() {
    log "设置项目代码..."
    ssh $SERVER_USER@$SERVER_IP "
        # 创建项目目录
        mkdir -p $PROJECT_PATH
        
        # 如果目录已存在，更新代码
        if [ -d \"$PROJECT_PATH/.git\" ]; then
            cd $PROJECT_PATH
            log '更新现有代码...'
            git fetch origin
            git checkout $BRANCH
            git pull origin $BRANCH
        else
            # 克隆项目
            cd $PROJECT_PATH
            git clone -b $BRANCH $GIT_REPO .
        fi
        
        log '项目代码设置完成'
    "
}

# 设置Python环境
setup_python_env() {
    log "设置Python环境..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        
        # 创建虚拟环境
        if [ ! -d \"venv\" ]; then
            python3 -m venv venv
        fi
        
        # 激活虚拟环境并安装依赖
        source venv/bin/activate
        
        # 升级pip
        pip install --upgrade pip
        
        # 根据环境安装依赖
        if [ \"$ENVIRONMENT\" = \"production\" ]; then
            pip install -r requirements/prod.txt
        else
            pip install -r requirements/dev.txt
        fi
        
        log 'Python环境设置完成'
    "
}

# 运行测试
run_tests() {
    if [[ "$SKIP_TESTS" = true ]]; then
        warn "跳过测试"
        return
    fi
    
    log "运行测试..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        source venv/bin/activate
        
        # 运行Django检查
        python manage.py check
        
        # 运行测试
        python manage.py test --verbosity=2
        
        log '测试完成'
    "
}

# 数据库迁移
run_migrations() {
    if [[ "$SKIP_MIGRATIONS" = true ]]; then
        warn "跳过数据库迁移"
        return
    fi
    
    log "运行数据库迁移..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        source venv/bin/activate
        
        # 收集静态文件
        python manage.py collectstatic --noinput
        
        # 运行迁移
        python manage.py migrate
        
        log '数据库迁移完成'
    "
}

# 配置Nginx
setup_nginx() {
    if [[ "$ENVIRONMENT" = "development" ]]; then
        warn "开发环境跳过Nginx配置"
        return
    fi
    
    log "配置Nginx..."
    ssh $SERVER_USER@$SERVER_IP "
        # 创建Nginx配置
        sudo tee /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name _;
    
    location /static/ {
        alias $PROJECT_PATH/staticfiles/;
    }
    
    location /media/ {
        alias $PROJECT_PATH/media/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
        
        log 'Nginx配置完成'
    "
}

# 启动服务
start_services() {
    log "启动服务..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        source venv/bin/activate
        
        # 停止现有服务
        pkill -f 'python manage.py runserver' || true
        pkill -f 'gunicorn' || true
        
        # 启动服务
        if [ \"$ENVIRONMENT\" = \"production\" ]; then
            # 生产环境使用gunicorn
            nohup gunicorn --bind 127.0.0.1:8000 --workers 4 --timeout 120 config.wsgi:application > gunicorn.log 2>&1 &
        else
            # 开发环境使用Django开发服务器
            nohup python manage.py runserver 0.0.0.0:8000 > django.log 2>&1 &
        fi
        
        log '服务启动完成'
    "
}

# 主函数
main() {
    log "开始部署 QAToolBox ($ENVIRONMENT 环境)"
    
    parse_args "$@"
    validate_config
    check_ssh
    install_system_deps
    setup_project
    setup_python_env
    run_tests
    run_migrations
    setup_nginx
    start_services
    
    log "部署完成！"
    info "项目地址: http://$SERVER_IP"
    info "项目路径: $PROJECT_PATH"
    info "环境: $ENVIRONMENT"
}

# 运行主函数
main "$@" 