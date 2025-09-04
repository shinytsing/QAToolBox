#!/bin/bash

# QAToolBox 修复缺失静态文件脚本
# 解决geek.css、responsive.css等文件缺失问题

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
log_info "QAToolBox 修复缺失静态文件脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查static目录中的文件
log_info "检查static目录中的文件..."
ls -la static/ | head -10

# 2. 查找缺失的CSS文件
log_info "查找缺失的CSS文件..."
find static/ -name "*.css" | head -10

# 3. 查找缺失的JS文件
log_info "查找缺失的JS文件..."
find static/ -name "*.js" | head -10

# 4. 检查Django设置中的静态文件配置
log_info "检查Django静态文件设置..."
grep -A 10 -B 5 "STATIC" config/settings/production.py

# 5. 手动复制缺失的文件
log_info "手动复制缺失的文件..."

# 复制CSS文件
if [ -f "static/geek.css" ]; then
    cp static/geek.css staticfiles/
    log_success "复制 geek.css"
else
    log_warning "geek.css 不存在于static目录"
fi

if [ -f "static/responsive.css" ]; then
    cp static/responsive.css staticfiles/
    log_success "复制 responsive.css"
else
    log_warning "responsive.css 不存在于static目录"
fi

if [ -f "static/css/feature-recommendation.css" ]; then
    mkdir -p staticfiles/css
    cp static/css/feature-recommendation.css staticfiles/css/
    log_success "复制 feature-recommendation.css"
else
    log_warning "feature-recommendation.css 不存在于static目录"
fi

# 复制JS文件
if [ -f "static/js/top_ui_functions.js" ]; then
    mkdir -p staticfiles/js
    cp static/js/top_ui_functions.js staticfiles/js/
    log_success "复制 top_ui_functions.js"
else
    log_warning "top_ui_functions.js 不存在于static目录"
fi

if [ -f "static/js/theme_manager.js" ]; then
    cp static/js/theme_manager.js staticfiles/js/
    log_success "复制 theme_manager.js"
else
    log_warning "theme_manager.js 不存在于static目录"
fi

if [ -f "static/js/session_manager.js" ]; then
    cp static/js/session_manager.js staticfiles/js/
    log_success "复制 session_manager.js"
else
    log_warning "session_manager.js 不存在于static目录"
fi

if [ -f "static/js/feature-recommendation.js" ]; then
    cp static/js/feature-recommendation.js staticfiles/js/
    log_success "复制 feature-recommendation.js"
else
    log_warning "feature-recommendation.js 不存在于static目录"
fi

if [ -f "static/js/auth.js" ]; then
    cp static/js/auth.js staticfiles/js/
    log_success "复制 auth.js"
else
    log_warning "auth.js 不存在于static目录"
fi

# 复制favicon文件
if [ -f "static/favicon.ico" ]; then
    cp static/favicon.ico staticfiles/
    log_success "复制 favicon.ico"
else
    log_warning "favicon.ico 不存在于static目录"
fi

if [ -f "static/favicon.svg" ]; then
    cp static/favicon.svg staticfiles/
    log_success "复制 favicon.svg"
else
    log_warning "favicon.svg 不存在于static目录"
fi

# 6. 修复权限
log_info "修复权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/staticfiles/

# 7. 检查复制后的文件
log_info "检查复制后的文件..."
ls -la staticfiles/ | head -10
ls -la staticfiles/css/ 2>/dev/null || log_warning "css目录不存在"
ls -la staticfiles/js/ 2>/dev/null || log_warning "js目录不存在"

# 8. 测试文件访问
log_info "测试文件访问..."
if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/geek.css && log_success "geek.css 可读" || log_error "geek.css 不可读"
else
    log_warning "geek.css 仍然不存在"
fi

if [ -f "/home/admin/QAToolbox/staticfiles/responsive.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/responsive.css && log_success "responsive.css 可读" || log_error "responsive.css 不可读"
else
    log_warning "responsive.css 仍然不存在"
fi

# 9. 重启Nginx
log_info "重启Nginx..."
systemctl restart nginx

# 10. 等待服务启动
log_info "等待服务启动..."
sleep 5

# 11. 测试静态文件访问
log_info "测试静态文件访问..."
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || log_warning "geek.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || log_warning "responsive.css 访问失败"
curl -I http://47.103.143.152/static/css/feature-recommendation.css 2>/dev/null | head -1 || log_warning "feature-recommendation.css 访问失败"

# 12. 检查Nginx错误日志
log_info "检查Nginx错误日志..."
tail -n 5 /var/log/nginx/error.log

log_success "=========================================="
log_success "缺失静态文件修复完成！"
log_success "=========================================="
echo
log_info "📱 测试访问:"
echo "  - 网站: http://47.103.143.152"
echo "  - 静态文件: http://47.103.143.152/static/"
echo "  - CSS文件: http://47.103.143.152/static/geek.css"
echo "  - JS文件: http://47.103.143.152/static/js/top_ui_functions.js"
echo
log_info "🛠️  如果仍有问题，请检查:"
echo "  - 文件权限: ls -la /home/admin/QAToolbox/staticfiles/"
echo "  - Nginx状态: systemctl status nginx"
echo "  - 错误日志: tail -f /var/log/nginx/error.log"
echo
log_success "现在静态文件应该可以正常加载了！"
log_success "=========================================="
