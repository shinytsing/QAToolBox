#!/bin/bash

# QAToolBox 修复域名DNS解析脚本
# 解决shenyiqing.xin域名访问问题

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
log_info "QAToolBox 修复域名DNS解析脚本"
log_info "=========================================="

# 1. 检查域名DNS解析
log_info "检查域名DNS解析..."
log_info "检查 shenyiqing.xin 的A记录:"
nslookup shenyiqing.xin || dig shenyiqing.xin A || log_warning "nslookup/dig命令不可用"

log_info "检查 www.shenyiqing.xin 的A记录:"
nslookup www.shenyiqing.xin || dig www.shenyiqing.xin A || log_warning "nslookup/dig命令不可用"

# 2. 检查本地hosts文件
log_info "检查本地hosts文件..."
if [ -f "/etc/hosts" ]; then
    log_info "当前hosts文件内容:"
    cat /etc/hosts | grep -E "(shenyiqing|47.103.143.152)" || log_info "hosts文件中没有相关记录"
fi

# 3. 测试域名解析
log_info "测试域名解析..."
log_info "测试 shenyiqing.xin 解析:"
ping -c 1 shenyiqing.xin 2>/dev/null && log_success "shenyiqing.xin 解析成功" || log_warning "shenyiqing.xin 解析失败"

log_info "测试 www.shenyiqing.xin 解析:"
ping -c 1 www.shenyiqing.xin 2>/dev/null && log_success "www.shenyiqing.xin 解析成功" || log_warning "www.shenyiqing.xin 解析失败"

# 4. 检查Nginx配置
log_info "检查Nginx配置..."
if [ -f "/etc/nginx/sites-available/qatoolbox" ]; then
    log_info "当前Nginx配置:"
    cat /etc/nginx/sites-available/qatoolbox
else
    log_error "Nginx配置文件不存在"
fi

# 5. 检查Nginx状态
log_info "检查Nginx状态..."
systemctl status nginx --no-pager -l

# 6. 测试Nginx监听
log_info "检查Nginx监听端口..."
netstat -tlnp | grep :80

# 7. 测试本地域名访问
log_info "测试本地域名访问..."
curl -H "Host: shenyiqing.xin" http://127.0.0.1/ 2>/dev/null && log_success "本地域名访问成功" || log_warning "本地域名访问失败"

# 8. 检查防火墙
log_info "检查防火墙状态..."
ufw status || iptables -L | head -10

# 9. 创建临时hosts条目（用于测试）
log_info "创建临时hosts条目用于测试..."
if ! grep -q "shenyiqing.xin" /etc/hosts; then
    echo "47.103.143.152 shenyiqing.xin www.shenyiqing.xin" >> /etc/hosts
    log_success "已添加临时hosts条目"
else
    log_info "hosts条目已存在"
fi

# 10. 测试添加hosts后的访问
log_info "测试添加hosts后的访问..."
sleep 2
curl -s http://shenyiqing.xin/ > /dev/null && log_success "shenyiqing.xin 访问成功" || log_warning "shenyiqing.xin 访问失败"
curl -s http://www.shenyiqing.xin/ > /dev/null && log_success "www.shenyiqing.xin 访问成功" || log_warning "www.shenyiqing.xin 访问失败"

# 11. 检查域名注册商DNS设置
log_info "检查域名注册商DNS设置..."
log_info "请检查以下DNS记录是否正确设置:"
echo "  A记录: shenyiqing.xin -> 47.103.143.152"
echo "  A记录: www.shenyiqing.xin -> 47.103.143.152"
echo "  或者CNAME记录: www.shenyiqing.xin -> shenyiqing.xin"

# 12. 提供DNS配置建议
log_info "DNS配置建议:"
echo "1. 登录你的域名注册商控制面板"
echo "2. 找到DNS管理或域名解析设置"
echo "3. 添加以下记录:"
echo "   类型: A, 主机记录: @, 记录值: 47.103.143.152"
echo "   类型: A, 主机记录: www, 记录值: 47.103.143.152"
echo "4. 等待DNS传播（通常需要几分钟到几小时）"

# 13. 测试外部DNS解析
log_info "测试外部DNS解析..."
log_info "使用公共DNS服务器测试:"
nslookup shenyiqing.xin 8.8.8.8 || log_warning "无法使用8.8.8.8解析"
nslookup shenyiqing.xin 1.1.1.1 || log_warning "无法使用1.1.1.1解析"

log_success "=========================================="
log_success "域名DNS检查完成！"
log_success "=========================================="
echo
log_info "📱 当前状态:"
echo "  - IP访问: http://47.103.143.152 ✅"
echo "  - 域名访问: http://shenyiqing.xin ❌ (需要DNS配置)"
echo "  - 临时解决方案: 已添加hosts条目"
echo
log_info "🔧 解决方案:"
echo "  1. 检查域名注册商的DNS设置"
echo "  2. 确保A记录指向 47.103.143.152"
echo "  3. 等待DNS传播完成"
echo "  4. 或者使用临时hosts条目进行测试"
echo
log_success "=========================================="
