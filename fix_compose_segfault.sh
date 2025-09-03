#!/bin/bash

# 修复Docker Compose段错误问题

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

log_info "修复Docker Compose段错误问题..."

# 1. 删除损坏的Docker Compose
log_info "删除损坏的Docker Compose..."
rm -f /usr/local/bin/docker-compose
rm -f /usr/bin/docker-compose

# 2. 使用apt安装docker-compose-plugin
log_info "使用apt安装docker-compose-plugin..."
apt-get update -y
apt-get install -y docker-compose-plugin

# 3. 检查是否安装成功
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

# 4. 如果apt安装失败，尝试使用pipx
log_info "使用pipx安装Docker Compose..."
apt-get install -y pipx
pipx install docker-compose

# 5. 检查pipx安装结果
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
    exit 0
fi

# 6. 如果都失败，使用snap安装
log_info "使用snap安装Docker Compose..."
apt-get install -y snapd
snap install docker-compose

# 7. 最终检查
if command -v docker-compose &> /dev/null; then
    log_success "Docker Compose安装成功: $(docker-compose --version)"
else
    log_error "所有安装方法都失败了"
    exit 1
fi
