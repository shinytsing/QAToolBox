#!/bin/bash

# 快速修复Docker Compose安装问题
# 使用多种方法确保快速安装

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

log_info "快速修复Docker Compose安装..."

# 停止当前下载
pkill -f "wget.*docker-compose" 2>/dev/null || true
pkill -f "curl.*docker-compose" 2>/dev/null || true

# 方法1: 使用apt安装docker-compose-plugin
log_info "方法1: 使用apt安装docker-compose-plugin..."
apt-get update -y
apt-get install -y docker-compose-plugin

# 检查是否安装成功
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

# 方法2: 使用国内镜像源下载
log_info "方法2: 使用国内镜像源下载..."

# 尝试多个国内镜像源
MIRROR_URLS=(
    "https://mirror.ghproxy.com/https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64"
    "https://get.daocloud.io/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64"
    "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64"
)

for url in "${MIRROR_URLS[@]}"; do
    log_info "尝试从 $url 下载..."
    if wget --timeout=30 --tries=3 -O /usr/local/bin/docker-compose "$url"; then
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        log_success "Docker Compose下载安装成功"
        exit 0
    else
        log_warning "下载失败，尝试下一个镜像源..."
    fi
done

# 方法3: 使用pipx安装（避免Python环境问题）
log_info "方法3: 使用pipx安装..."
apt-get install -y pipx
pipx install docker-compose

# 检查是否安装成功
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

# 方法4: 使用snap安装
log_info "方法4: 使用snap安装..."
apt-get install -y snapd
snap install docker-compose

# 检查是否安装成功
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

log_error "所有安装方法都失败了"
exit 1