#!/bin/bash

# QAToolBox 沈一清专用一键部署脚本
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# Python版本: 3.12.3

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置信息
SERVER_IP="47.103.143.152"
DOMAIN="shenyiqing.xin"
GITHUB_REPO="https://github.com/shinytsing/QAToolbox.git"
PROJECT_DIR="/opt/qatoolbox"

log_info "开始部署QAToolBox到沈一清服务器..."
log_info "服务器IP: $SERVER_IP"
log_info "域名: $DOMAIN"
log_info "GitHub仓库: $GITHUB_REPO"

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查Python版本
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python版本: $PYTHON_VERSION"
        if [[ "$PYTHON_VERSION" == "3.12.3" ]]; then
            log_success "Python版本匹配"
        else
            log_warning "Python版本不匹配，建议使用3.12.3"
        fi
    else
        log_error "未找到Python3"
        exit 1
    fi
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    log_info "系统内存: ${total_mem}MB"
    if [[ $total_mem -lt 2048 ]]; then
        log_warning "系统内存不足2GB，可能影响性能"
    fi
    
    # 检查磁盘空间
    available_space=$(df / | awk 'NR==2 {print $4}')
    log_info "可用磁盘空间: $((available_space/1024/1024))GB"
    if [[ $available_space -lt 1048576 ]]; then
        log_warning "可用磁盘空间不足1GB"
    fi
}

# 安装Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
        return 0
    fi
    
    log_info "安装Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_compose() {
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装: $(docker-compose --version)"
        return 0
    fi
    
    log_info "安装Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    log_success "Docker Compose安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        # 允许SSH
        sudo ufw allow ssh
        
        # 允许HTTP和HTTPS
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # 允许应用端口
        sudo ufw allow 8000/tcp
        
        # 启用防火墙
        sudo ufw --force enable
        
        log_success "防火墙配置完成"
    else
        log_warning "未检测到UFW防火墙，请手动配置防火墙规则"
    fi
}

# 部署项目
deploy_project() {
    log_info "部署QAToolBox项目..."
    
    # 创建项目目录
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 克隆项目
    if [[ -d "QAToolbox" ]]; then
        log_info "项目目录已存在，更新代码..."
        cd QAToolbox
        git pull origin main
    else
        log_info "克隆项目代码..."
        git clone $GITHUB_REPO
        cd QAToolbox
    fi
    
    # 配置环境
    if [[ ! -f ".env" ]]; then
        log_info "配置环境变量..."
        cp env.production .env
        
        # 生成随机密钥
        SECRET_KEY=$(openssl rand -base64 32)
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
        
        DB_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
        
        REDIS_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/redis123/$REDIS_PASSWORD/" .env
        
        log_success "环境变量配置完成"
    else
        log_info "环境变量文件已存在，跳过配置"
    fi
    
    # 启动服务
    log_info "启动Docker服务..."
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 初始化数据库
    log_info "初始化数据库..."
    docker-compose exec web python manage.py migrate
    
    # 创建超级用户
    log_info "创建超级用户..."
    docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@shenyiqing.xin || true
    
    # 收集静态文件
    log_info "收集静态文件..."
    docker-compose exec web python manage.py collectstatic --noinput
    
    log_success "项目部署完成！"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查容器状态
    docker-compose ps
    
    # 检查健康状态
    log_info "检查应用健康状态..."
    for i in {1..10}; do
        if curl -f http://localhost:8000/health/ &>/dev/null; then
            log_success "应用健康检查通过"
            break
        else
            log_info "等待应用启动... ($i/10)"
            sleep 10
        fi
    done
    
    # 显示访问信息
    log_success "部署完成！"
    echo
    log_info "访问信息:"
    echo "  - 应用地址: http://$SERVER_IP:8000"
    echo "  - 域名地址: http://$DOMAIN:8000"
    echo "  - 管理后台: http://$SERVER_IP:8000/admin/"
    echo
    log_info "默认管理员账户:"
    echo "  - 用户名: admin"
    echo "  - 密码: 请通过以下命令设置:"
    echo "    docker-compose exec web python manage.py changepassword admin"
    echo
    log_info "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 更新代码: git pull && docker-compose up -d --build"
}

# 主函数
main() {
    log_info "开始QAToolBox沈一清专用部署..."
    check_system
    install_docker
    install_compose
    configure_firewall
    deploy_project
    check_services
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
