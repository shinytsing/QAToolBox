#!/bin/bash

# QAToolBox 阿里云快速部署脚本
# 使用方法: curl -sSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/quick_deploy_aliyun.sh | bash

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

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查是否为Ubuntu/Debian
    if [[ ! -f /etc/os-release ]]; then
        log_error "不支持的操作系统"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        log_warning "建议使用Ubuntu或Debian系统"
    fi
    
    log_info "系统: $NAME $VERSION"
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

# 部署项目
deploy_project() {
    log_info "部署QAToolBox项目..."
    
    PROJECT_DIR="/opt/qatoolbox"
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 克隆项目
    if [[ -d "QAToolbox" ]]; then
        cd QAToolbox
        git pull origin main
    else
        git clone https://github.com/shinytsing/QAToolbox.git
        cd QAToolbox
    fi
    
    # 配置环境
    if [[ ! -f ".env" ]]; then
        cp env.production .env
        # 生成随机密钥
        SECRET_KEY=$(openssl rand -base64 32)
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
        DB_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
        REDIS_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/redis123/$REDIS_PASSWORD/" .env
    fi
    
    # 启动服务
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 初始化数据库
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput
    
    log_success "部署完成！"
    
    # 显示访问信息
    echo
    log_info "访问信息:"
    echo "  - 应用地址: http://47.103.143.152:8000"
    echo "  - 域名地址: http://shenyiqing.xin:8000"
    echo "  - 管理后台: http://47.103.143.152:8000/admin/"
    echo
    log_info "设置管理员密码:"
    echo "  docker-compose exec web python manage.py changepassword admin"
}

# 主函数
main() {
    log_info "开始QAToolBox快速部署..."
    check_system
    install_docker
    install_compose
    deploy_project
    log_success "部署完成！"
}

main "$@"