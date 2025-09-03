#!/bin/bash

# Docker Compose 快速修复脚本
# 解决下载失败和Python环境问题

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

log_info "修复Docker Compose安装问题..."

# 方法1: 使用apt安装docker-compose-plugin
log_info "方法1: 使用apt安装docker-compose-plugin..."
apt-get update -y
apt-get install -y docker-compose-plugin

# 检查是否安装成功
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

# 方法2: 直接下载特定版本
log_info "方法2: 直接下载Docker Compose v2.24.0..."
COMPOSE_VERSION="v2.24.0"
COMPOSE_URL="https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)"

# 使用wget下载
log_info "下载地址: $COMPOSE_URL"
wget -O /usr/local/bin/docker-compose "$COMPOSE_URL"

if [[ -f /usr/local/bin/docker-compose ]]; then
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    log_success "Docker Compose下载安装成功"
else
    log_error "Docker Compose下载失败"
    exit 1
fi

# 验证安装
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装验证成功: $(docker-compose --version)"
else
    log_error "Docker Compose安装验证失败"
    exit 1
fi
