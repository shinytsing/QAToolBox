#!/bin/bash

# QAToolBox 阿里云CentOS简化部署脚本
# 使用方法: chmod +x deploy_aliyun_simple.sh && ./deploy_aliyun_simple.sh

set -e

echo "🚀 开始部署 QAToolBox 到阿里云CentOS..."

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
        log_error "请不要使用root用户运行此脚本！"
        exit 1
    fi
}

# 检查系统
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if ! grep -q "CentOS\|Red Hat" /etc/os-release; then
        log_warning "此脚本针对CentOS优化，其他系统可能需要调整"
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "系统环境检查通过"
}

# 创建环境变量文件
create_env_file() {
    log_info "创建环境变量文件..."
    
    if [ ! -f .env ]; then
        log_info "创建 .env 文件..."
        
        # 生成随机密钥（不依赖Python3）
        SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        DB_PASSWORD=$(openssl rand -base64 32)
        
        cat > .env << EOF
# Django配置
DJANGO_SECRET_KEY=${SECRET_KEY}
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production

# 数据库配置
DB_PASSWORD=${DB_PASSWORD}

# 允许的主机（请修改为你的域名或IP）
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,your-server-ip

# Redis配置
REDIS_URL=redis://redis:6379/0

# 邮件配置（可选）
EMAIL_HOST=smtp.your-provider.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=True

# Grafana配置（如果使用监控）
GRAFANA_PASSWORD=admin123
EOF
        
        log_success "已创建 .env 文件，请根据需要修改配置"
        log_warning "重要：请修改 .env 文件中的 ALLOWED_HOSTS 为你的实际域名或IP"
    else
        log_info ".env 文件已存在，跳过创建"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p media
    mkdir -p staticfiles
    
    log_success "目录创建完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    
    docker-compose -f docker-compose.simple.yml build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 停止已存在的服务
    docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
    
    # 启动服务
    docker-compose -f docker-compose.simple.yml up -d
    
    log_success "服务启动完成"
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."
    
    # 等待数据库就绪
    log_info "等待数据库启动..."
    for i in {1..30}; do
        if docker-compose -f docker-compose.simple.yml exec -T db pg_isready -U postgres -d qatoolbox >/dev/null 2>&1; then
            log_success "数据库已就绪"
            break
        fi
        sleep 2
    done
    
    # 等待Redis就绪
    log_info "等待Redis启动..."
    for i in {1..30}; do
        if docker-compose -f docker-compose.simple.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
            log_success "Redis已就绪"
            break
        fi
        sleep 2
    done
    
    sleep 10  # 额外等待时间
}

# 数据库初始化
init_database() {
    log_info "初始化数据库..."
    
    # 运行数据库迁移
    docker-compose -f docker-compose.simple.yml exec web python manage.py migrate
    
    # 收集静态文件
    docker-compose -f docker-compose.simple.yml exec web python manage.py collectstatic --noinput
    
    log_success "数据库初始化完成"
}

# 创建超级用户
create_superuser() {
    log_info "创建管理员用户..."
    
    echo "请输入管理员信息："
    docker-compose -f docker-compose.simple.yml exec web python manage.py createsuperuser
    
    log_success "管理员用户创建完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    echo "=== Docker 容器状态 ==="
    docker-compose -f docker-compose.simple.yml ps
    
    echo -e "\n=== 服务健康检查 ==="
    
    # 检查Web服务
    if curl -f http://localhost:8000 >/dev/null 2>&1; then
        log_success "Web服务运行正常 (http://localhost:8000)"
    else
        log_warning "Web服务可能还在启动中，请稍后检查"
    fi
    
    # 检查数据库
    if docker-compose -f docker-compose.simple.yml exec -T db pg_isready -U postgres -d qatoolbox >/dev/null 2>&1; then
        log_success "数据库服务运行正常"
    else
        log_error "数据库服务异常"
    fi
    
    # 检查Redis
    if docker-compose -f docker-compose.simple.yml exec -T redis redis-cli ping >/dev/null 2>&1; then
        log_success "Redis服务运行正常"
    else
        log_error "Redis服务异常"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 部署完成！"
    
    echo -e "\n${GREEN}=== 部署信息 ===${NC}"
    echo "Web服务地址: http://localhost:8000"
    echo "管理后台: http://localhost:8000/admin/"
    echo ""
    echo "=== 常用命令 ==="
    echo "查看日志: docker-compose -f docker-compose.simple.yml logs"
    echo "重启服务: docker-compose -f docker-compose.simple.yml restart"
    echo "停止服务: docker-compose -f docker-compose.simple.yml down"
    echo "查看状态: docker-compose -f docker-compose.simple.yml ps"
    echo ""
    echo "=== 下一步操作 ==="
    echo "1. 配置Nginx反向代理（参考 ALIYUN_CENTOS_DEPLOYMENT.md）"
    echo "2. 设置SSL证书"
    echo "3. 配置防火墙规则"
    echo "4. 设置定期备份"
    echo ""
    log_warning "请确保修改 .env 文件中的 ALLOWED_HOSTS 为你的实际域名或IP"
}

# 主函数
main() {
    echo "🔧 QAToolBox 阿里云CentOS简化部署脚本"
    echo "========================================"
    
    check_root
    check_system
    create_env_file
    create_directories
    build_images
    start_services
    wait_for_services
    init_database
    
    # 询问是否创建超级用户
    read -p "是否创建管理员用户？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    check_services
    show_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
