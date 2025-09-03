#!/bin/bash

# QAToolBox 阿里云Docker一键部署脚本
# 使用方法: ./deploy_aliyun_docker.sh

set -e  # 遇到错误立即退出

# 颜色输出
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
        log_warning "建议不要使用root用户运行此脚本"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统要求
check_system() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    . /etc/os-release
    log_info "检测到操作系统: $NAME $VERSION"
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [[ $total_mem -lt 2048 ]]; then
        log_warning "系统内存不足2GB，可能影响性能"
    fi
    
    # 检查磁盘空间
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1048576 ]]; then  # 1GB in KB
        log_warning "可用磁盘空间不足1GB"
    fi
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装，版本: $(docker --version)"
        return 0
    fi
    
    # 更新包索引
    sudo apt-get update
    
    # 安装必要的包
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 设置稳定版仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 更新包索引
    sudo apt-get update
    
    # 安装Docker Engine
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到docker组
    sudo usermod -aG docker $USER
    
    log_success "Docker安装完成"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装，版本: $(docker-compose --version)"
        return 0
    fi
    
    # 下载Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 添加执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
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

# 创建项目目录
setup_project() {
    log_info "设置项目目录..."
    
    PROJECT_DIR="/opt/qatoolbox"
    
    # 创建项目目录
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    
    # 进入项目目录
    cd $PROJECT_DIR
    
    log_success "项目目录设置完成: $PROJECT_DIR"
}

# 克隆项目代码
clone_project() {
    log_info "克隆项目代码..."
    
    # 检查是否已存在项目
    if [[ -d "QAToolbox" ]]; then
        log_warning "项目目录已存在，是否更新?"
        read -p "选择操作: [u]更新 [s]跳过 [d]删除重建: " -n 1 -r
        echo
        
        case $REPLY in
            [Uu]* )
                cd QAToolbox
                git pull origin main
                ;;
            [Dd]* )
                rm -rf QAToolbox
                git clone https://github.com/shinytsing/QAToolbox.git
                cd QAToolbox
                ;;
            [Ss]* )
                cd QAToolbox
                ;;
            * )
                log_info "跳过代码更新"
                cd QAToolbox
                ;;
        esac
    else
        # 克隆项目
        git clone https://github.com/shinytsing/QAToolbox.git
        cd QAToolbox
    fi
    
    log_success "项目代码准备完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    # 检查是否存在.env文件
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.production" ]]; then
            cp env.production .env
            log_info "已复制生产环境配置文件"
        else
            log_warning "未找到环境配置文件，请手动创建.env文件"
        fi
    fi
    
    # 生成随机密钥
    if grep -q "your-super-secret-key-change-this-in-production" .env; then
        SECRET_KEY=$(openssl rand -base64 32)
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
        log_info "已生成新的Django密钥"
    fi
    
    # 设置数据库密码
    if grep -q "qatoolbox123" .env; then
        DB_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
        log_info "已生成新的数据库密码"
    fi
    
    # 设置Redis密码
    if grep -q "redis123" .env; then
        REDIS_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/redis123/$REDIS_PASSWORD/" .env
        log_info "已生成新的Redis密码"
    fi
    
    log_success "环境变量配置完成"
}

# 构建和启动服务
start_services() {
    log_info "构建和启动服务..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose exec web python manage.py migrate
    
    # 创建超级用户
    log_info "创建超级用户..."
    docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com || true
    
    # 收集静态文件
    log_info "收集静态文件..."
    docker-compose exec web python manage.py collectstatic --noinput
    
    log_success "服务启动完成"
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
    echo "  - 应用地址: http://47.103.143.152:8000"
    echo "  - 域名地址: http://shenyiqing.xin:8000"
    echo "  - 本地地址: http://localhost:8000"
    echo "  - 管理后台: http://47.103.143.152:8000/admin/"
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
    log_info "开始QAToolBox阿里云Docker部署..."
    
    check_root
    check_system
    install_docker
    install_docker_compose
    configure_firewall
    setup_project
    clone_project
    setup_environment
    start_services
    check_services
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"