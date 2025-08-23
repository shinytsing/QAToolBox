#!/bin/bash

# QAToolBox 阿里云简化部署脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/gaojie058/QAToolBox/main/deploy_aliyun_simple.sh | bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "=== QAToolBox 阿里云一键部署 ==="
print_info "服务器IP: 47.103.143.152"
print_info "域名: shenyiqing.xin"

# 1. 更新系统
print_info "更新系统..."
sudo apt update -y

# 2. 安装必要软件
print_info "安装必要软件..."
sudo apt install -y curl git

# 3. 安装Docker
print_info "安装Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    print_info "Docker安装完成，请重新登录以使用Docker"
    print_warning "请运行: newgrp docker 或重新登录SSH"
fi

# 4. 安装Docker Compose
print_info "安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 5. 克隆项目
print_info "克隆项目..."
if [ -d "QAToolBox" ]; then
    cd QAToolBox
    git pull
else
    git clone https://github.com/gaojie058/QAToolBox.git
    cd QAToolBox
fi

# 6. 创建环境文件
print_info "创建环境配置..."
cat > .env << EOF
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/0

# Django配置
DJANGO_SECRET_KEY=$(openssl rand -base64 50)
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False

# 域名配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost
EOF

# 7. 启动服务
print_info "启动服务..."
docker-compose -f docker-compose.simple.yml up -d --build

# 8. 等待服务启动
print_info "等待服务启动..."
sleep 30

# 9. 显示结果
print_info "部署完成！"
echo ""
print_info "访问地址: http://47.103.143.152"
print_info "管理后台: http://47.103.143.152/admin/"
print_info "默认管理员: admin / admin123456"
echo ""
print_info "服务管理命令:"
print_info "- 查看状态: docker-compose -f docker-compose.simple.yml ps"
print_info "- 查看日志: docker-compose -f docker-compose.simple.yml logs -f"
print_info "- 重启服务: docker-compose -f docker-compose.simple.yml restart"
print_info "- 停止服务: docker-compose -f docker-compose.simple.yml down"
echo ""
print_warning "如需配置域名和SSL，请参考 DEPLOYMENT_GUIDE.md"