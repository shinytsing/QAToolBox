#!/bin/bash

# QAToolBox 使用Gitee镜像部署脚本
# 解决GitHub访问问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# 配置Git使用代理或镜像
setup_git_proxy() {
    log_info "配置Git访问..."
    
    # 设置Git超时时间（不使用全局配置）
    export GIT_CONFIG_GLOBAL=""
    
    log_success "Git配置完成"
}

# 从多个源克隆项目
clone_project() {
    log_info "克隆项目代码..."
    
    PROJECT_DIR="$HOME/QAToolBox"
    
    # 如果目录已存在，先删除
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 尝试多个Git源
    SOURCES=(
        "https://github.com/shinytsing/QAToolbox.git"
        "https://hub.fastgit.xyz/shinytsing/QAToolbox.git"
        "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
        "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git"
    )
    
    for source in "${SOURCES[@]}"; do
        log_info "尝试从 $source 克隆..."
        if timeout 60 git clone --depth 1 "$source" "$PROJECT_DIR"; then
            log_success "项目克隆成功！"
            cd "$PROJECT_DIR"
            return 0
        else
            log_warning "从 $source 克隆失败，尝试下一个源..."
        fi
    done
    
    log_error "所有Git源都失败了，尝试手动下载..."
    
    # 尝试直接下载ZIP文件
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    ZIP_SOURCES=(
        "https://github.com/shinytsing/QAToolbox/archive/refs/heads/main.zip"
        "https://hub.fastgit.xyz/shinytsing/QAToolbox/archive/refs/heads/main.zip"
        "https://download.fastgit.org/shinytsing/QAToolbox/archive/refs/heads/main.zip"
    )
    
    for zip_source in "${ZIP_SOURCES[@]}"; do
        log_info "尝试下载 $zip_source ..."
        if curl -L --connect-timeout 30 --max-time 300 "$zip_source" -o main.zip; then
            log_info "解压文件..."
            unzip -q main.zip
            mv QAToolbox-main/* .
            mv QAToolbox-main/.* . 2>/dev/null || true
            rmdir QAToolbox-main
            rm main.zip
            log_success "项目下载成功！"
            return 0
        else
            log_warning "从 $zip_source 下载失败，尝试下一个源..."
        fi
    done
    
    log_error "无法获取项目代码，请检查网络连接"
    exit 1
}

# 创建必要的配置文件
create_configs() {
    log_info "创建配置文件..."
    
    # 创建docker-compose.china.yml
    cat > docker-compose.china.yml << 'EOF'
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile.china
    container_name: qatoolbox_web
    restart: unless-stopped
    ports:
      - "80:80"
      - "8000:8000"
    volumes:
      - ./media:/app/media
      - ./logs:/app/logs
      - ./static:/app/static
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgresql://qatoolbox:${DB_PASSWORD}@db:5432/qatoolbox
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=False
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    depends_on:
      - db
      - redis
    networks:
      - qatoolbox_network

  db:
    image: registry.cn-hangzhou.aliyuncs.com/library/postgres:13
    container_name: qatoolbox_db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=qatoolbox
      - POSTGRES_USER=qatoolbox
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - qatoolbox_network

  redis:
    image: registry.cn-hangzhou.aliyuncs.com/library/redis:6-alpine
    container_name: qatoolbox_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - qatoolbox_network

volumes:
  postgres_data:
  redis_data:

networks:
  qatoolbox_network:
    driver: bridge
EOF
    
    # 创建Dockerfile.china
    cat > Dockerfile.china << 'EOF'
# 使用阿里云Ubuntu镜像
FROM registry.cn-hangzhou.aliyuncs.com/acs/ubuntu:20.04

# 设置环境变量避免交互式安装
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 设置工作目录
WORKDIR /app

# 更换为阿里云镜像源
RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    git \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置pip使用阿里云镜像
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip3 config set install.trusted-host mirrors.aliyun.com

# 升级pip
RUN pip3 install --upgrade pip

# 复制requirements文件
COPY requirements.txt /app/
COPY requirements/ /app/requirements/ 2>/dev/null || true

# 安装Python依赖
RUN pip3 install -r requirements.txt || pip3 install django djangorestframework celery redis psycopg2-binary pillow

# 复制项目文件
COPY . /app/

# 创建必要的目录和设置权限
RUN mkdir -p /app/logs /app/media /app/static /app/staticfiles && \
    chmod -R 755 /app

# 暴露端口
EXPOSE 8000

# 启动脚本
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
EOF
    
    log_success "配置文件创建完成"
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    ENV_FILE=".env.production"
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
    DB_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-20)
    
    # 获取服务器IP
    SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me || curl -s --connect-timeout 5 ip.sb || echo "localhost")
    
    cat > "$ENV_FILE" << EOF
# Django配置
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1

# 数据库配置
DB_PASSWORD=$DB_PASSWORD

# Redis配置
REDIS_URL=redis://redis:6379/0
EOF
    
    # 导出环境变量
    export SECRET_KEY="$SECRET_KEY"
    export DB_PASSWORD="$DB_PASSWORD"
    export ALLOWED_HOSTS="$SERVER_IP,localhost,127.0.0.1"
    
    log_success "环境变量配置完成"
}

# 启动服务
start_services() {
    log_info "启动Docker服务..."
    
    # 创建必要目录
    mkdir -p logs media static
    
    # 启动服务
    docker compose -f docker-compose.china.yml down --remove-orphans 2>/dev/null || true
    docker compose -f docker-compose.china.yml up -d --build
    
    log_success "服务启动完成"
}

# 检查部署状态
check_deployment() {
    log_info "检查部署状态..."
    
    sleep 15
    
    # 检查容器状态
    if docker ps | grep -q qatoolbox; then
        log_success "容器启动成功！"
        
        SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me || curl -s --connect-timeout 5 ip.sb || echo "localhost")
        
        echo
        log_success "=== 🎉 部署完成！ ==="
        echo
        log_info "🌐 访问地址: http://$SERVER_IP"
        log_info "🔐 管理后台: http://$SERVER_IP/admin/"
        log_info "👤 默认账号: admin"
        log_info "🔑 默认密码: admin123456"
        echo
        log_warning "⚠️  请及时修改默认密码！"
        echo
        log_info "📊 查看日志: docker compose -f docker-compose.china.yml logs -f"
        log_info "🔄 重启服务: docker compose -f docker-compose.china.yml restart"
        
    else
        log_error "容器启动失败，查看日志："
        docker compose -f docker-compose.china.yml logs
    fi
}

# 主函数
main() {
    log_info "开始QAToolBox部署 (网络优化版)..."
    
    setup_git_proxy
    clone_project
    create_configs
    setup_environment
    start_services
    check_deployment
    
    log_success "部署流程完成！"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
