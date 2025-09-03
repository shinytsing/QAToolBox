#!/bin/bash

# 修复Docker镜像拉取超时问题

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

log_info "修复Docker镜像拉取超时问题..."

# 1. 配置Docker镜像加速器
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

# 2. 重启Docker服务
log_info "重启Docker服务..."
systemctl daemon-reload
systemctl restart docker

# 3. 等待Docker服务启动
log_info "等待Docker服务启动..."
sleep 10

# 4. 验证Docker服务状态
if systemctl is-active --quiet docker; then
    log_success "Docker服务重启成功"
else
    log_error "Docker服务重启失败"
    exit 1
fi

# 5. 测试镜像拉取
log_info "测试镜像拉取..."
if docker pull hello-world:latest; then
    log_success "镜像拉取测试成功"
    docker rmi hello-world:latest 2>/dev/null || true
else
    log_warning "镜像拉取测试失败，但配置已更新"
fi

log_success "Docker镜像加速器配置完成"
