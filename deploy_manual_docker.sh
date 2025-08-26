#!/bin/bash

# QAToolBox 手动Docker安装部署脚本
# 适用于网络不稳定的环境

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

# 检查用户权限
check_user() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 手动安装Docker
install_docker_manual() {
    log_info "手动安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_warning "Docker已安装，跳过安装步骤"
    else
        # 更新包列表
        sudo apt-get update
        
        # 安装必要的包
        sudo apt-get install -y \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加Docker官方GPG密钥
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        
        # 添加Docker仓库
        echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 更新包列表
        sudo apt-get update
        
        # 安装Docker Engine
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        
        log_success "Docker安装完成"
    fi
    
    # 将用户添加到docker组
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
    
    log_success "Docker配置完成"
}

# 安装Docker Compose (使用apt方式)
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log_warning "Docker Compose已安装，跳过安装步骤"
        return
    fi
    
    # 尝试使用apt安装
    if sudo apt-get install -y docker-compose-plugin; then
        log_success "Docker Compose Plugin安装完成"
    else
        log_warning "Plugin安装失败，尝试独立版本..."
        # 备用方案：下载独立版本
        DOCKER_COMPOSE_VERSION="2.20.2"
        sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        log_success "Docker Compose独立版本安装完成"
    fi
}

# 克隆项目
setup_project() {
    log_info "设置项目..."
    
    PROJECT_DIR="$HOME/QAToolBox"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，更新代码..."
        cd "$PROJECT_DIR"
        git pull origin main || log_warning "代码更新失败，继续使用现有代码"
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
        SECRET_KEY=$(openssl rand -base64 50 | tr -d "=+/" | cut -c1-50)
        DB_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-20)
        
        # 获取服务器IP
        SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me || echo "localhost")
        
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

# 创建部署配置
create_deploy_configs() {
    log_info "创建部署配置..."
    
    # 创建deploy目录
    mkdir -p deploy
    
    # 创建Nginx配置
    cat > deploy/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;
    
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /app/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF
    
    # 创建启动脚本
    cat > deploy/start.sh << 'EOF'
#!/bin/bash

# 等待数据库启动
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# 运行数据库迁移
python3 manage.py migrate --noinput

# 创建超级用户（如果不存在）
python3 manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('Superuser created: admin/admin123456')
PYTHON

# 收集静态文件
python3 manage.py collectstatic --noinput

# 启动应用
exec python3 manage.py runserver 0.0.0.0:8000
EOF
    
    chmod +x deploy/start.sh
    
    log_success "部署配置创建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 使用newgrp临时获取docker组权限
    if command -v docker-compose &> /dev/null; then
        newgrp docker << EOF
docker-compose -f docker-compose.china.yml down --remove-orphans
docker-compose -f docker-compose.china.yml up -d --build
EOF
    else
        newgrp docker << EOF
docker compose -f docker-compose.china.yml down --remove-orphans
docker compose -f docker-compose.china.yml up -d --build
EOF
    fi
    
    log_success "服务启动完成"
}

# 检查部署状态
check_deployment() {
    log_info "检查部署状态..."
    
    sleep 10
    
    # 检查容器状态
    if newgrp docker -c "docker ps | grep -q qatoolbox"; then
        log_success "容器启动成功"
        
        # 获取服务器IP
        SERVER_IP=$(curl -s --connect-timeout 5 ifconfig.me || echo "localhost")
        
        log_success "=== 部署完成 ==="
        echo
        log_info "访问地址: http://$SERVER_IP"
        log_info "管理后台: http://$SERVER_IP/admin/"
        log_info "默认管理员账号: admin"
        log_info "默认管理员密码: admin123456"
        echo
        log_warning "请及时修改默认密码！"
    else
        log_error "容器启动失败，请检查日志"
        newgrp docker -c "docker-compose -f docker-compose.china.yml logs" || true
    fi
}

# 主函数
main() {
    log_info "开始QAToolBox手动部署..."
    
    check_user
    install_docker_manual
    install_docker_compose
    setup_project
    setup_environment
    create_deploy_configs
    start_services
    check_deployment
    
    log_success "部署流程完成！"
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
