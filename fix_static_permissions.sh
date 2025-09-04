#!/bin/bash

# QAToolBox 修复静态文件权限脚本
# 解决Nginx无法访问静态文件的权限问题

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
log_info "QAToolBox 修复静态文件权限脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查当前权限
log_info "检查当前权限..."
ls -la /home/admin/QAToolbox/staticfiles/ | head -5
ls -la /home/admin/QAToolbox/static/ | head -5

# 2. 检查Nginx用户
log_info "检查Nginx用户..."
ps aux | grep nginx | head -3

# 3. 修复静态文件权限
log_info "修复静态文件权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chown -R www-data:www-data /home/admin/QAToolbox/static/
chmod -R 755 /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/static/

# 4. 修复项目目录权限
log_info "修复项目目录权限..."
chown -R admin:admin /home/admin/QAToolbox/
chmod -R 755 /home/admin/QAToolbox/

# 5. 修复staticfiles目录权限
log_info "修复staticfiles目录权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/staticfiles/

# 6. 检查关键文件权限
log_info "检查关键文件权限..."
ls -la /home/admin/QAToolbox/staticfiles/geek.css
ls -la /home/admin/QAToolbox/staticfiles/responsive.css
ls -la /home/admin/QAToolbox/staticfiles/js/top_ui_functions.js

# 7. 测试文件访问
log_info "测试文件访问..."
sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/geek.css && log_success "geek.css 可读" || log_error "geek.css 不可读"
sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/responsive.css && log_success "responsive.css 可读" || log_error "responsive.css 不可读"
sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/js/top_ui_functions.js && log_success "top_ui_functions.js 可读" || log_error "top_ui_functions.js 不可读"

# 8. 重启Nginx
log_info "重启Nginx..."
systemctl restart nginx

# 9. 等待Nginx启动
log_info "等待Nginx启动..."
sleep 5

# 10. 检查Nginx状态
log_info "检查Nginx状态..."
systemctl status nginx --no-pager -l

# 11. 测试静态文件访问
log_info "测试静态文件访问..."
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || log_warning "geek.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || log_warning "responsive.css 访问失败"
curl -I http://47.103.143.152/static/js/top_ui_functions.js 2>/dev/null | head -1 || log_warning "top_ui_functions.js 访问失败"

# 12. 检查Nginx错误日志
log_info "检查Nginx错误日志..."
tail -n 5 /var/log/nginx/error.log

# 13. 测试网站访问
log_info "测试网站访问..."
curl -s http://47.103.143.152/ > /dev/null && log_success "网站访问成功" || log_error "网站访问失败"

log_success "=========================================="
log_success "静态文件权限修复完成！"
log_success "=========================================="
echo
log_info "📱 测试访问:"
echo "  - 网站: http://47.103.143.152"
echo "  - 静态文件: http://47.103.143.152/static/"
echo "  - CSS文件: http://47.103.143.152/static/geek.css"
echo
log_info "🛠️  如果仍有问题，请检查:"
echo "  - 文件权限: ls -la /home/admin/QAToolbox/staticfiles/"
echo "  - Nginx用户: ps aux | grep nginx"
echo "  - Nginx日志: tail -f /var/log/nginx/error.log"
echo
log_success "现在静态文件应该可以正常加载了！"
log_success "=========================================="