#!/bin/bash

# QAToolBox 直接修复静态文件脚本
# 在服务器上直接运行，解决静态文件403 Forbidden错误

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
log_info "QAToolBox 直接修复静态文件脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查当前状态
log_info "检查当前状态..."
echo "当前用户: $(whoami)"
echo "当前目录: $(pwd)"

# 2. 重新收集静态文件
log_info "重新收集静态文件..."
python manage.py collectstatic --noinput --clear --settings=config.settings.production

# 3. 修复权限
log_info "修复权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/staticfiles/

# 4. 检查关键文件
log_info "检查关键文件..."
ls -la /home/admin/QAToolbox/staticfiles/ | head -10

# 5. 查找CSS文件
log_info "查找CSS文件..."
find /home/admin/QAToolbox/staticfiles/ -name "*.css" | head -10

# 6. 测试文件访问
log_info "测试文件访问..."
if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/geek.css && log_success "geek.css 可读" || log_error "geek.css 不可读"
else
    log_warning "geek.css 不存在，查找其他CSS文件..."
    find /home/admin/QAToolbox/staticfiles/ -name "geek.css" 2>/dev/null || log_warning "未找到geek.css"
fi

# 7. 重启Nginx
log_info "重启Nginx..."
systemctl restart nginx

# 8. 等待服务启动
log_info "等待服务启动..."
sleep 5

# 9. 检查服务状态
log_info "检查服务状态..."
systemctl status nginx --no-pager -l

# 10. 测试静态文件访问
log_info "测试静态文件访问..."
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || log_warning "geek.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || log_warning "responsive.css 访问失败"

# 11. 检查Nginx错误日志
log_info "检查Nginx错误日志..."
tail -n 10 /var/log/nginx/error.log

log_success "=========================================="
log_success "静态文件修复完成！"
log_success "=========================================="
echo
log_info "📱 测试访问:"
echo "  - 网站: http://47.103.143.152"
echo "  - 静态文件: http://47.103.143.152/static/"
echo
log_info "🛠️  如果仍有问题，请检查:"
echo "  - 文件权限: ls -la /home/admin/QAToolbox/staticfiles/"
echo "  - Nginx状态: systemctl status nginx"
echo "  - 错误日志: tail -f /var/log/nginx/error.log"
echo
log_success "现在静态文件应该可以正常加载了！"
log_success "=========================================="
