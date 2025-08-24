#!/bin/bash

# QAToolBox 本地部署脚本 - 解决网络连接问题
# 直接复制此脚本内容到服务器执行

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_info "=== QAToolBox 本地部署开始 ==="

# 1. 修复CentOS 8源
print_step "1/10 修复CentOS 8源配置..."
sudo mkdir -p /etc/yum.repos.d.backup
sudo cp /etc/yum.repos.d/*.repo /etc/yum.repos.d.backup/ 2>/dev/null || true
sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*
sudo sed -i '/failovermethod/d' /etc/yum.repos.d/CentOS-epel.repo 2>/dev/null || true

# 2. 更新系统
print_step "2/10 更新系统..."
sudo dnf clean all
sudo dnf update -y

# 3. 安装基础软件
print_step "3/10 安装基础软件..."
sudo dnf install -y curl wget git unzip epel-release
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y openssl-devel libffi-devel python3-devel

# 4. 安装Docker
print_step "4/10 安装Docker..."
sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine 2>/dev/null || true
sudo dnf install -y yum-utils device-mapper-persistent-data lvm2
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# 5. 安装Docker Compose
print_step "5/10 安装Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 6. 配置防火墙
print_step "6/10 配置防火墙..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# 7. 克隆项目
print_step "7/10 克隆项目..."
cd /home/$USER
if [ -d "QAToolbox" ]; then
    cd QAToolbox
    git pull origin main
else
    git clone https://github.com/shinytsing/QAToolbox.git
    cd QAToolbox
fi

# 8. 创建环境文件
print_step "8/10 创建环境配置..."
cat > .env << EOF
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
DJANGO_SECRET_KEY=$(openssl rand -base64 50)
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@shenyiqing.xin
ADMIN_PASSWORD=admin123456
EOF

# 9. 创建简化Docker配置
print_step "9/10 创建Docker配置..."
cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: qatoolbox123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  web:
    build:
      context: .
      dockerfile: Dockerfile.simple
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=postgres://qatoolbox:qatoolbox123@db:5432/qatoolbox
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=False
      - ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost
    ports:
      - "80:8000"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
EOF

# 10. 启动服务
print_step "10/10 启动服务..."
mkdir -p logs
newgrp docker << 'EONG'
docker-compose -f docker-compose.simple.yml up -d --build
EONG

print_info "=== 部署完成 ==="
print_info "访问地址: http://47.103.143.152"
print_info "管理后台: http://47.103.143.152/admin/"
print_info "默认账户: admin / admin123456"
