#!/bin/bash

# QAToolBox 一键部署脚本 - 适配中国网络环境
# 适用于阿里云Ubuntu服务器

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
        log_info "建议创建普通用户: sudo adduser qatoolbox && sudo usermod -aG sudo qatoolbox"
        exit 1
    fi
}

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    # 检查Ubuntu版本
    if ! grep -q "Ubuntu" /etc/os-release; then
        log_error "此脚本仅支持Ubuntu系统"
        exit 1
    fi
    
    # 检查网络连接
    if ! ping -c 1 mirrors.aliyun.com &> /dev/null; then
        log_warning "无法连接到阿里云镜像源，可能影响下载速度"
    fi
    
    log_success "系统环境检查完成"
}

# 更新系统并安装基础依赖
install_dependencies() {
    log_info "更新系统并安装基础依赖..."
    
    # 备份原始sources.list
    sudo cp /etc/apt/sources.list /etc/apt/sources.list.backup
    
    # 更换为阿里云镜像源
    sudo tee /etc/apt/sources.list > /dev/null <<EOF
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs) main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-backports main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $(lsb_release -cs)-security main restricted universe multiverse
EOF
    
    sudo apt-get update
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        wget \
        unzip
    
    log_success "基础依赖安装完成"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    if command -v docker &> /dev/null; then
        log_warning "Docker已安装，跳过安装步骤"
        return
    fi
    
    # 添加阿里云Docker镜像源
    curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] http://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
    
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
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

# 克隆或更新项目
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

# 创建部署配置文件
create_deploy_configs() {
    log_info "创建部署配置文件..."
    
    # 创建Nginx配置
    mkdir -p deploy
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
    
    # 创建Supervisor配置
    cat > deploy/supervisord.conf << 'EOF'
[supervisord]
nodaemon=true
user=root

[program:django]
command=python3 manage.py runserver 0.0.0.0:8000
directory=/app
user=www-data
autostart=true
autorestart=true
stdout_logfile=/app/logs/django.log
stderr_logfile=/app/logs/django_error.log

[program:nginx]
command=nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/app/logs/nginx.log
stderr_logfile=/app/logs/nginx_error.log

[program:redis]
command=redis-server
autostart=true
autorestart=true
stdout_logfile=/app/logs/redis.log
stderr_logfile=/app/logs/redis_error.log
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

# 启动supervisor
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
EOF
    
    chmod +x deploy/start.sh
    
    # 创建数据库初始化脚本
    cat > deploy/init.sql << 'EOF'
-- 数据库初始化脚本
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
EOF
    
    log_success "部署配置文件创建完成"
}

# 构建和启动服务
deploy_application() {
    log_info "构建和启动应用..."
    
    # 停止现有容器
    docker-compose -f docker-compose.china.yml down --remove-orphans
    
    # 构建镜像
    docker-compose -f docker-compose.china.yml build --no-cache
    
    # 启动服务
    docker-compose -f docker-compose.china.yml up -d
    
    log_success "应用部署完成"
}

# 检查部署状态
check_deployment() {
    log_info "检查部署状态..."
    
    # 等待服务启动
    sleep 10
    
    # 检查容器状态
    if docker-compose -f docker-compose.china.yml ps | grep -q "Up"; then
        log_success "容器启动成功"
    else
        log_error "容器启动失败"
        docker-compose -f docker-compose.china.yml logs
        exit 1
    fi
    
    # 检查Web服务
    if curl -f http://localhost:80 &> /dev/null; then
        log_success "Web服务运行正常"
    else
        log_warning "Web服务可能还在启动中，请稍后检查"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "=== 部署完成 ==="
    echo
    log_info "访问地址: http://$(curl -s ifconfig.me || echo 'your-server-ip')"
    log_info "管理后台: http://$(curl -s ifconfig.me || echo 'your-server-ip')/admin/"
    log_info "默认管理员账号: admin"
    log_info "默认管理员密码: admin123456"
    echo
    log_info "常用命令:"
    echo "  查看日志: docker-compose -f docker-compose.china.yml logs -f"
    echo "  重启服务: docker-compose -f docker-compose.china.yml restart"
    echo "  停止服务: docker-compose -f docker-compose.china.yml down"
    echo "  更新代码: git pull && docker-compose -f docker-compose.china.yml up -d --build"
    echo
    log_warning "请及时修改默认密码！"
}

# 主函数
main() {
    log_info "开始QAToolBox一键部署..."
    
    check_root
    check_system
    install_dependencies
    install_docker
    install_docker_compose
    setup_project
    setup_environment
    create_deploy_configs
    deploy_application
    check_deployment
    show_deployment_info
    
    log_success "部署完成！"
}

# 如果脚本被直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi

