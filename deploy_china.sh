#!/bin/bash

# QAToolBox 国内优化部署脚本

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

log_info "=========================================="
log_info "QAToolBox 国内优化部署脚本"
log_info "服务器IP: $SERVER_IP"
log_info "域名: $DOMAIN"
log_info "=========================================="

# 1. 配置Docker镜像加速器
setup_docker_mirrors() {
    log_info "配置Docker镜像加速器..."
    
    mkdir -p /etc/docker
    
    cat > /etc/docker/daemon.json << EOF
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com",
        "https://registry.docker-cn.com",
        "https://dockerhub.azk8s.cn",
        "https://reg-mirror.qiniu.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "insecure-registries": [],
    "debug": false,
    "experimental": false
}
EOF
    
    # 重启Docker服务
    systemctl daemon-reload
    systemctl restart docker
    
    # 等待Docker服务启动
    sleep 10
    
    log_success "Docker镜像加速器配置完成"
}

# 2. 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装"
        exit 1
    fi
    
    log_success "Docker已安装: $(docker --version)"
    
    # 检查Docker Compose插件
    if docker compose version &> /dev/null; then
        log_success "Docker Compose插件可用: $(docker compose version)"
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        log_success "Docker Compose可用: $(docker-compose --version)"
        COMPOSE_CMD="docker-compose"
    else
        log_error "Docker Compose不可用"
        exit 1
    fi
}

# 3. 检查项目目录
check_project_directory() {
    log_info "检查项目目录..."
    
    # 如果当前在项目目录中，直接使用
    if [[ -f "manage.py" ]]; then
        log_info "当前目录就是项目目录，直接使用"
        PROJECT_PATH="."
    elif [[ -d "QAToolBox" && -f "QAToolBox/manage.py" ]]; then
        log_info "项目在QAToolBox子目录中"
        PROJECT_PATH="QAToolBox"
    elif [[ -d "QAToolbox" && -f "QAToolbox/manage.py" ]]; then
        log_info "项目在QAToolbox子目录中"
        PROJECT_PATH="QAToolbox"
    else
        log_error "未找到项目文件，请确保在正确的项目目录中运行此脚本"
        exit 1
    fi
    
    log_success "项目目录检查完成: $PROJECT_PATH"
}

# 4. 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    # 进入项目目录
    cd $PROJECT_PATH
    
    # 检查是否存在.env文件
    if [[ ! -f ".env" ]]; then
        if [[ -f "env.production" ]]; then
            cp env.production .env
            log_info "已复制生产环境配置文件"
        else
            log_error "未找到环境配置文件"
            exit 1
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
    
    # 确保允许的主机包含服务器IP和域名
    if ! grep -q "47.103.143.152" .env; then
        sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin/" .env
        log_info "已更新允许的主机列表"
    fi
    
    log_success "环境变量配置完成"
}

# 5. 启动Docker服务
start_services() {
    log_info "启动Docker服务..."
    
    # 停止现有服务
    $COMPOSE_CMD down 2>/dev/null || true
    
    # 清理旧的镜像和容器
    docker system prune -f
    
    # 构建镜像
    log_info "构建Docker镜像..."
    $COMPOSE_CMD build --no-cache
    
    # 启动服务
    log_info "启动Docker服务..."
    $COMPOSE_CMD up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 60
    
    log_success "Docker服务启动完成"
}

# 6. 数据库迁移和初始化
setup_database() {
    log_info "数据库迁移和初始化..."
    
    # 等待数据库服务完全启动
    log_info "等待数据库服务启动..."
    for i in {1..30}; do
        if $COMPOSE_CMD exec -T db pg_isready -U qatoolbox -d qatoolbox_production &>/dev/null; then
            log_info "数据库服务已就绪"
            break
        else
            log_info "等待数据库启动... ($i/30)"
            sleep 10
        fi
    done
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    $COMPOSE_CMD exec -T web python manage.py migrate
    
    # 创建超级用户
    log_info "创建超级用户..."
    $COMPOSE_CMD exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"
    
    # 收集静态文件
    log_info "收集静态文件..."
    $COMPOSE_CMD exec -T web python manage.py collectstatic --noinput
    
    log_success "数据库初始化完成"
}

# 7. 健康检查
health_check() {
    log_info "健康检查..."
    
    # 检查容器状态
    log_info "检查容器状态..."
    $COMPOSE_CMD ps
    
    # 检查应用健康状态
    log_info "检查应用健康状态..."
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

# 8. 显示部署结果
show_result() {
    log_success "=========================================="
    log_success "🎉 QAToolBox 国内优化部署完成！"
    log_success "=========================================="
    echo
    log_info "📱 访问信息:"
    echo "  - 应用地址: http://47.103.143.152:8000"
    echo "  - 域名地址: http://shenyiqing.xin:8000"
    echo "  - 管理后台: http://47.103.143.152:8000/admin/"
    echo "  - 健康检查: http://47.103.143.152:8000/health/"
    echo
    log_info "👤 管理员账户:"
    echo "  - 用户名: admin"
    echo "  - 密码: admin123456"
    echo "  - 邮箱: admin@shenyiqing.xin"
    echo
    log_info "🛠️  常用管理命令:"
    echo "  - 查看服务状态: $COMPOSE_CMD ps"
    echo "  - 查看日志: $COMPOSE_CMD logs -f"
    echo "  - 重启服务: $COMPOSE_CMD restart"
    echo "  - 停止服务: $COMPOSE_CMD down"
    echo "  - 进入容器: $COMPOSE_CMD exec web bash"
    echo
    log_success "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
    log_success "=========================================="
}

# 主函数
main() {
    log_info "开始QAToolBox国内优化部署..."
    
    setup_docker_mirrors
    check_docker
    check_project_directory
    setup_environment
    start_services
    setup_database
    health_check
    show_result
    
    log_success "所有部署步骤完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
