#!/bin/bash

# QAToolBox 完整部署脚本 - 沈一清专用
# 服务器: 47.103.143.152
# 域名: shenyiqing.xin
# 包含: Docker安装、项目部署、数据库迁移、用户创建等所有操作

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
log_info "QAToolBox 完整部署脚本 - 沈一清专用"
log_info "服务器IP: $SERVER_IP"
log_info "域名: $DOMAIN"
log_info "GitHub仓库: $GITHUB_REPO"
log_info "=========================================="

# 1. 系统更新和基础软件安装
install_system_dependencies() {
    log_info "步骤1: 更新系统并安装基础依赖..."
    
    # 配置国内镜像源
    log_info "配置国内镜像源..."
    cat > /etc/apt/sources.list << EOF
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-proposed main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
EOF
    
    # 更新包列表
    apt-get update -y
    
    # 安装基础工具
    apt-get install -y \
        curl \
        wget \
        git \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        build-essential \
        libpq-dev \
        postgresql-client \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        libwebp-dev \
        zlib1g-dev \
        libsndfile1 \
        ffmpeg \
        tesseract-ocr \
        tesseract-ocr-chi-sim \
        chromium-browser \
        chromium-chromedriver
    
    log_success "系统依赖安装完成"
}

# 2. 安装Docker
install_docker() {
    log_info "步骤2: 安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_info "Docker已安装: $(docker --version)"
    else
        # 使用国内镜像源安装Docker
        log_info "使用国内镜像源安装Docker..."
        
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # 设置稳定版仓库（使用国内镜像）
        echo \
            "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu \
            $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 更新包索引
        apt-get update -y
        
        # 安装Docker Engine
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # 配置Docker镜像加速器
        mkdir -p /etc/docker
        cat > /etc/docker/daemon.json << EOF
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ],
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    }
}
EOF
        
        # 启动Docker服务
        systemctl daemon-reload
        systemctl start docker
        systemctl enable docker
        
        log_success "Docker安装完成"
    fi
}

# 3. 安装Docker Compose
install_docker_compose() {
    log_info "步骤3: 安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装: $(docker-compose --version)"
    else
        # 使用国内镜像源下载Docker Compose
        log_info "使用国内镜像源下载Docker Compose..."
        
        # 尝试多个镜像源
        COMPOSE_URLS=(
            "https://mirror.ghproxy.com/https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
            "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
            "https://get.daocloud.io/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
        )
        
        for url in "${COMPOSE_URLS[@]}"; do
            log_info "尝试从 $url 下载..."
            if curl -L --connect-timeout 10 --max-time 60 "$url" -o /usr/local/bin/docker-compose; then
                log_success "Docker Compose下载成功"
                break
            else
                log_warning "下载失败，尝试下一个镜像源..."
            fi
        done
        
        # 检查是否下载成功
        if [[ ! -f /usr/local/bin/docker-compose ]]; then
            log_error "Docker Compose下载失败，使用apt安装..."
            apt-get install -y docker-compose-plugin
        else
            # 添加执行权限
            chmod +x /usr/local/bin/docker-compose
            
            # 创建软链接
            ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        fi
        
        log_success "Docker Compose安装完成"
    fi
}

# 4. 配置防火墙
configure_firewall() {
    log_info "步骤4: 配置防火墙..."
    
    # 安装UFW
    apt-get install -y ufw
    
    # 重置防火墙规则
    ufw --force reset
    
    # 设置默认策略
    ufw default deny incoming
    ufw default allow outgoing
    
    # 允许SSH
    ufw allow ssh
    
    # 允许HTTP和HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 允许应用端口
    ufw allow 8000/tcp
    
    # 启用防火墙
    ufw --force enable
    
    log_success "防火墙配置完成"
}

# 5. 创建项目目录和用户
setup_project_environment() {
    log_info "步骤5: 设置项目环境..."
    
    # 创建项目目录
    mkdir -p $PROJECT_DIR
    chown -R root:root $PROJECT_DIR
    
    # 进入项目目录
    cd $PROJECT_DIR
    
    log_success "项目环境设置完成"
}

# 6. 克隆项目代码
clone_project() {
    log_info "步骤6: 克隆项目代码..."
    
    # 检查是否已存在项目
    if [[ -d "QAToolbox" ]]; then
        log_warning "项目目录已存在，更新代码..."
        cd QAToolbox
        git pull origin main
    else
        log_info "克隆项目代码..."
        git clone $GITHUB_REPO
        cd QAToolbox
    fi
    
    log_success "项目代码准备完成"
}

# 7. 配置环境变量
setup_environment() {
    log_info "步骤7: 配置环境变量..."
    
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

# 8. 构建和启动Docker服务
start_docker_services() {
    log_info "步骤8: 构建和启动Docker服务..."
    
    # 停止现有服务
    docker-compose down 2>/dev/null || true
    
    # 清理旧的镜像和容器
    docker system prune -f
    
    # 构建镜像
    log_info "构建Docker镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    log_info "启动Docker服务..."
    docker-compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 60
    
    log_success "Docker服务启动完成"
}

# 9. 数据库迁移和初始化
setup_database() {
    log_info "步骤9: 数据库迁移和初始化..."
    
    # 等待数据库服务完全启动
    log_info "等待数据库服务启动..."
    for i in {1..30}; do
        if docker-compose exec -T db pg_isready -U qatoolbox -d qatoolbox_production &>/dev/null; then
            log_info "数据库服务已就绪"
            break
        else
            log_info "等待数据库启动... ($i/30)"
            sleep 10
        fi
    done
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose exec -T web python manage.py migrate
    
    # 创建超级用户
    log_info "创建超级用户..."
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
    log_info "收集静态文件..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    
    log_success "数据库初始化完成"
}

# 10. 服务健康检查
health_check() {
    log_info "步骤10: 服务健康检查..."
    
    # 检查容器状态
    log_info "检查容器状态..."
    docker-compose ps
    
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
    
    # 检查数据库连接
    log_info "检查数据库连接..."
    docker-compose exec -T web python manage.py check --database default
    
    # 检查Redis连接
    log_info "检查Redis连接..."
    docker-compose exec -T web python manage.py shell -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, decode_responses=True)
    r.ping()
    print('Redis连接正常')
except Exception as e:
    print(f'Redis连接失败: {e}')
"
    
    log_success "健康检查完成"
}

# 11. 显示部署结果
show_deployment_result() {
    log_success "=========================================="
    log_success "🎉 QAToolBox 部署完成！"
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
    echo "  - 查看服务状态: docker-compose ps"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 重启服务: docker-compose restart"
    echo "  - 停止服务: docker-compose down"
    echo "  - 更新代码: git pull && docker-compose up -d --build"
    echo "  - 进入容器: docker-compose exec web bash"
    echo
    log_info "📊 系统信息:"
    echo "  - 服务器IP: 47.103.143.152"
    echo "  - 域名: shenyiqing.xin"
    echo "  - Python版本: 3.12"
    echo "  - Django版本: 4.2.7"
    echo "  - 数据库: PostgreSQL 15"
    echo "  - 缓存: Redis 7"
    echo
    log_success "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
    log_success "=========================================="
}

# 主函数
main() {
    log_info "开始QAToolBox完整部署流程..."
    
    install_system_dependencies
    install_docker
    install_docker_compose
    configure_firewall
    setup_project_environment
    clone_project
    setup_environment
    start_docker_services
    setup_database
    health_check
    show_deployment_result
    
    log_success "所有部署步骤完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
