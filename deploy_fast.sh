#!/bin/bash

# QAToolBox 快速部署脚本 - 优化下载速度
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin

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

log_info "=========================================="
log_info "QAToolBox 快速部署脚本 - 优化版"
log_info "服务器IP: $SERVER_IP"
log_info "域名: $DOMAIN"
log_info "=========================================="

# 配置国内镜像源
setup_mirrors() {
    log_info "配置国内镜像源..."
    
    # 备份原始sources.list
    cp /etc/apt/sources.list /etc/apt/sources.list.backup
    
    # 配置阿里云镜像源
    cat > /etc/apt/sources.list << EOF
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-proposed main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
EOF
    
    apt-get update -y
    log_success "镜像源配置完成"
}

# 快速安装Docker
install_docker_fast() {
    log_info "快速安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
        return 0
    fi
    
    # 使用阿里云Docker镜像源
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    
    # 配置Docker镜像加速器
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com",
        "https://registry.docker-cn.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
EOF
    
    systemctl daemon-reload
    systemctl start docker
    systemctl enable docker
    
    log_success "Docker安装完成"
}

# 快速安装Docker Compose
install_compose_fast() {
    log_info "快速安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装: $(docker-compose --version)"
        return 0
    fi
    
    # 使用apt安装Docker Compose（避免Python环境问题）
    log_info "使用apt安装Docker Compose..."
    apt-get install -y docker-compose-plugin
    
    # 检查是否安装成功
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose安装完成"
    else
        # 如果apt安装失败，尝试直接下载
        log_info "apt安装失败，尝试直接下载..."
        
        # 使用wget下载（比curl更稳定）
        COMPOSE_VERSION="v2.24.0"
        wget -O /usr/local/bin/docker-compose "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"
        
        if [[ -f /usr/local/bin/docker-compose ]]; then
            chmod +x /usr/local/bin/docker-compose
            ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
            log_success "Docker Compose下载安装完成"
        else
            log_error "Docker Compose安装失败"
            exit 1
        fi
    fi
}

# 安装基础依赖
install_dependencies() {
    log_info "安装基础依赖..."
    
    apt-get install -y \
        curl \
        wget \
        git \
        python3 \
        python3-pip \
        python3-venv \
        ufw \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release
    
    log_success "基础依赖安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 8000/tcp
    ufw --force enable
    
    log_success "防火墙配置完成"
}

# 部署项目
deploy_project() {
    log_info "部署项目..."
    
    # 创建项目目录
    mkdir -p $PROJECT_DIR
    cd $PROJECT_DIR
    
    # 克隆项目
    if [[ -d "QAToolbox" ]]; then
        cd QAToolbox
        git pull origin main
    else
        git clone $GITHUB_REPO
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
        
        # 更新允许的主机
        sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin/" .env
    fi
    
    log_success "项目配置完成"
}

# 启动服务
start_services() {
    log_info "启动Docker服务..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 启动服务
    docker-compose up -d --build
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 60
    
    log_success "服务启动完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    
    # 等待数据库启动
    for i in {1..30}; do
        if docker-compose exec -T db pg_isready -U qatoolbox -d qatoolbox_production &>/dev/null; then
            break
        else
            log_info "等待数据库启动... ($i/30)"
            sleep 10
        fi
    done
    
    # 数据库迁移
    docker-compose exec -T web python manage.py migrate
    
    # 创建超级用户
    docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"
    
    # 收集静态文件
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    log_success "数据库初始化完成"
}

# 健康检查
health_check() {
    log_info "健康检查..."
    
    # 检查容器状态
    docker-compose ps
    
    # 检查应用健康状态
    for i in {1..20}; do
        if curl -f http://localhost:8000/health/ &>/dev/null; then
            log_success "应用健康检查通过"
            break
        else
            log_info "等待应用启动... ($i/20)"
            sleep 15
        fi
    done
    
    log_success "健康检查完成"
}

# 显示结果
show_result() {
    log_success "=========================================="
    log_success "🎉 QAToolBox 快速部署完成！"
    log_success "=========================================="
    echo
    log_info "📱 访问信息:"
    echo "  - 应用地址: http://47.103.143.152:8000"
    echo "  - 域名地址: http://shenyiqing.xin:8000"
    echo "  - 管理后台: http://47.103.143.152:8000/admin/"
    echo
    log_info "👤 管理员账户:"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo
    log_success "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
    log_success "=========================================="
}

# 主函数
main() {
    setup_mirrors
    install_dependencies
    install_docker_fast
    install_compose_fast
    configure_firewall
    deploy_project
    start_services
    init_database
    health_check
    show_result
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
