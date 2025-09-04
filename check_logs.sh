#!/bin/bash

# QAToolBox 检查日志脚本
# 诊断400错误原因

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

log_info "=========================================="
log_info "QAToolBox 检查日志脚本"
log_info "=========================================="

# 1. 检查supervisor状态
log_info "检查supervisor状态..."
supervisorctl status qatoolbox

# 2. 检查Django日志
log_info "检查Django日志..."
if [ -f "/var/log/qatoolbox/django.log" ]; then
    log_info "Django日志内容（最后20行）:"
    tail -n 20 /var/log/qatoolbox/django.log
else
    log_warning "Django日志文件不存在"
fi

# 3. 检查应用日志
log_info "检查应用日志..."
if [ -f "/var/log/qatoolbox/app.log" ]; then
    log_info "应用日志内容（最后20行）:"
    tail -n 20 /var/log/qatoolbox/app.log
else
    log_warning "应用日志文件不存在"
fi

# 4. 检查错误日志
log_info "检查错误日志..."
if [ -f "/var/log/qatoolbox/error.log" ]; then
    log_info "错误日志内容（最后20行）:"
    tail -n 20 /var/log/qatoolbox/error.log
else
    log_warning "错误日志文件不存在"
fi

# 5. 检查Nginx日志
log_info "检查Nginx错误日志..."
if [ -f "/var/log/nginx/error.log" ]; then
    log_info "Nginx错误日志内容（最后20行）:"
    tail -n 20 /var/log/nginx/error.log
else
    log_warning "Nginx错误日志文件不存在"
fi

# 6. 检查Nginx访问日志
log_info "检查Nginx访问日志..."
if [ -f "/var/log/nginx/access.log" ]; then
    log_info "Nginx访问日志内容（最后20行）:"
    tail -n 20 /var/log/nginx/access.log
else
    log_warning "Nginx访问日志文件不存在"
fi

# 7. 检查systemd日志
log_info "检查systemd日志..."
journalctl -u qatoolbox --no-pager -n 10

# 8. 测试本地访问
log_info "测试本地访问..."
curl -v http://localhost:8000/ 2>&1 | head -20

# 9. 检查端口监听
log_info "检查端口监听..."
netstat -tlnp | grep :8000

# 10. 检查防火墙状态
log_info "检查防火墙状态..."
ufw status || iptables -L | head -10

log_success "=========================================="
log_success "日志检查完成！"
log_success "=========================================="
