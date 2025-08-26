#!/bin/bash

# =============================================================================
# QAToolBox 服务启动脚本
# 快速启动所有相关服务
# =============================================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}========================================"
echo "    🚀 QAToolBox 服务启动"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限启动系统服务"
    echo "请使用: sudo bash $0"
    exit 1
fi

# 启动数据库服务
log_info "启动PostgreSQL数据库"
if systemctl start postgresql; then
    log_success "PostgreSQL已启动"
else
    log_warning "PostgreSQL启动可能有问题"
fi

# 启动Redis服务
log_info "启动Redis缓存服务"
if systemctl start redis-server; then
    log_success "Redis已启动"
else
    log_warning "Redis启动可能有问题"
fi

# 等待数据库完全启动
sleep 3

# 启动QAToolBox应用
log_info "启动QAToolBox Django应用"
if systemctl start qatoolbox; then
    log_success "QAToolBox应用已启动"
else
    log_error "QAToolBox应用启动失败"
    log_info "查看详细错误信息:"
    journalctl -u qatoolbox --no-pager -n 10
fi

# 启动Nginx
log_info "启动Nginx Web服务器"
if systemctl start nginx; then
    log_success "Nginx已启动"
else
    log_error "Nginx启动失败"
    log_info "检查Nginx配置:"
    nginx -t
fi

# 等待服务完全启动
log_info "等待服务完全启动..."
sleep 10

# 检查服务状态
echo
echo -e "${BLUE}========================================"
echo "        📊 服务状态检查"
echo "========================================"
echo -e "${NC}"

# 检查PostgreSQL
POSTGRES_STATUS=$(systemctl is-active postgresql)
if [ "$POSTGRES_STATUS" = "active" ]; then
    echo -e "PostgreSQL: ${GREEN}✅ 运行中${NC}"
else
    echo -e "PostgreSQL: ${RED}❌ $POSTGRES_STATUS${NC}"
fi

# 检查Redis
REDIS_STATUS=$(systemctl is-active redis-server)
if [ "$REDIS_STATUS" = "active" ]; then
    echo -e "Redis: ${GREEN}✅ 运行中${NC}"
else
    echo -e "Redis: ${RED}❌ $REDIS_STATUS${NC}"
fi

# 检查QAToolBox
QATOOLBOX_STATUS=$(systemctl is-active qatoolbox)
if [ "$QATOOLBOX_STATUS" = "active" ]; then
    echo -e "QAToolBox: ${GREEN}✅ 运行中${NC}"
else
    echo -e "QAToolBox: ${RED}❌ $QATOOLBOX_STATUS${NC}"
fi

# 检查Nginx
NGINX_STATUS=$(systemctl is-active nginx)
if [ "$NGINX_STATUS" = "active" ]; then
    echo -e "Nginx: ${GREEN}✅ 运行中${NC}"
else
    echo -e "Nginx: ${RED}❌ $NGINX_STATUS${NC}"
fi

# HTTP响应测试
log_info "测试HTTP响应"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "HTTP响应: ${GREEN}✅ $HTTP_CODE (正常)${NC}"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "HTTP响应: ${YELLOW}⚠️ $HTTP_CODE (重定向)${NC}"
else
    echo -e "HTTP响应: ${RED}❌ $HTTP_CODE (异常)${NC}"
fi

# 端口检查
log_info "检查端口占用"
if netstat -tlnp | grep :8000 > /dev/null; then
    echo -e "端口8000: ${GREEN}✅ 已占用 (Django)${NC}"
else
    echo -e "端口8000: ${RED}❌ 未占用${NC}"
fi

if netstat -tlnp | grep :80 > /dev/null; then
    echo -e "端口80: ${GREEN}✅ 已占用 (Nginx)${NC}"
else
    echo -e "端口80: ${RED}❌ 未占用${NC}"
fi

# 显示最终结果
echo
if [ "$QATOOLBOX_STATUS" = "active" ] && [ "$NGINX_STATUS" = "active" ]; then
    echo -e "${GREEN}========================================"
    echo "        🎉 所有服务启动成功！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${GREEN}🌐 网站地址: http://shenyiqing.xin${NC}"
    echo -e "${GREEN}🔧 管理后台: http://shenyiqing.xin/admin/${NC}"
    echo -e "${GREEN}📊 API状态: http://shenyiqing.xin/api/status/${NC}"
    echo -e "${GREEN}👤 管理员: admin / QAToolBox@2024${NC}"
    echo
    echo -e "${BLUE}💡 有用的命令:${NC}"
    echo "• 查看应用日志: journalctl -u qatoolbox -f"
    echo "• 重启应用: systemctl restart qatoolbox"
    echo "• 停止所有服务: systemctl stop qatoolbox nginx"
    echo "• 检查服务状态: systemctl status qatoolbox nginx postgresql redis-server"
else
    echo -e "${YELLOW}========================================"
    echo "        ⚠️ 部分服务可能有问题"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${YELLOW}建议检查步骤:${NC}"
    echo "1. 查看QAToolBox日志: journalctl -u qatoolbox -f"
    echo "2. 查看Nginx日志: journalctl -u nginx -f"
    echo "3. 检查配置文件: nginx -t"
    echo "4. 重新运行修复脚本"
    
    if [ "$QATOOLBOX_STATUS" != "active" ]; then
        echo
        echo -e "${RED}QAToolBox服务异常，最近日志:${NC}"
        journalctl -u qatoolbox --no-pager -n 5
    fi
fi
