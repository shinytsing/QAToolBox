#!/bin/bash

# QAToolBox 一键部署脚本 - 修复版
# 适用于阿里云Ubuntu服务器，解决apt_pkg问题

set -e

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        log_info "建议切换到普通用户: su - qatoolbox"
        exit 1
    fi
}

# 修复apt_pkg问题
fix_apt_pkg() {
    log_info "检查并修复apt_pkg模块..."
    
    if ! python3 -c "import apt_pkg" 2>/dev/null; then
        log_warning "检测到apt_pkg模块问题，正在修复..."
        
        # 重新安装python3-apt
        sudo apt-get update
        sudo apt-get install --reinstall python3-apt -y
        
        # 如果还是失败，尝试其他方法
        if ! python3 -c "import apt_pkg" 2>/dev/null; then
            log_info "尝试修复Python链接..."
            sudo ln -sf /usr/lib/python3/dist-packages/apt_pkg.cpython-*-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so 2>/dev/null || true
            sudo apt-get install --reinstall python3-distutils python3-lib2to3 -y
        fi
        
        log_success "apt_pkg模块修复完成"
    else
        log_success "apt_pkg模块正常"
    fi
}

# 安装Docker (不使用add-apt-repository)
install_docker_manual() {
    log_info "手动安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_warning "Docker已安装，跳过安装步骤"
        return
    fi
    
    # 直接下载并安装Docker
    curl -fsSL https://get.docker.com | sudo sh
    
    # 将当前用户添加到docker组
    sudo usermod -aG docker $USER
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 配置Docker镜像加速器
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
    "registry-mirrors": [
        "https://mirror.ccs.tencentyun.com",
        "https://registry.cn-hangzhou.aliyuncs.com",
        "https://docker.mirrors.ustc.edu.cn"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "10m",
        "max-file": "3"
    }
}
EOF
    
    sudo systemctl restart docker
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose已安装，跳过安装步骤"
        return
    fi
    
    # 使用国内镜像下载
    DOCKER_COMPOSE_VERSION="2.20.2"
    sudo curl -L "https://get.daocloud.io/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log_success "Docker Compose安装完成"
}

# 克隆项目
setup_project() {
    log_info "设置项目..."
    
    PROJECT_DIR="$HOME/QAToolBox"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，更新代码..."
        cd "$PROJECT_DIR"
        git pull origin main
    else
        log_info "克隆项目..."
        git clone https://github.com/shinytsing/QAToolbox.git "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    
    # 创建必要的目录
    mkdir -p logs media static deploy
    
    log_success "项目设置完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    ENV_FILE=".env.production"
    
    if [ ! -f "$ENV_FILE" ]; then
        log_info "创建环境配置文件..."
        
        # 生成随机密钥
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(20))")
        
        # 获取服务器IP
        SERVER_IP=$(curl -s ifconfig.me || echo "localhost")
        
        cat > "$ENV_FILE" << EOF
# Django配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1

# 数据库配置
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://qatoolbox:$DB_PASSWORD@db:5432/qatoolbox

# Redis配置
REDIS_URL=redis://redis:6379/0

# 其他配置
DJANGO_SETTINGS_MODULE=config.settings.production
EOF
        
        log_success "环境配置文件创建完成"
    else
        log_warning "环境配置文件已存在，跳过创建"
    fi
}

# 主函数
main() {
    log_info "开始QAToolBox一键部署 (修复版)..."
    
    check_root
    fix_apt_pkg
    install_docker_manual
    install_docker_compose
    setup_project
    setup_environment
    
    log_success "部署准备完成！"
    log_info "请重新登录以使Docker组权限生效，然后运行："
    log_info "cd ~/QAToolBox && docker-compose -f docker-compose.china.yml up -d --build"
}

# 如果脚本被直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
