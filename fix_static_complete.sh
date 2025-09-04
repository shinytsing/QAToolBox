#!/bin/bash

# QAToolBox 完整修复静态文件脚本
# 解决静态文件403 Forbidden错误和权限问题

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
log_info "QAToolBox 完整修复静态文件脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查当前状态
log_info "检查当前状态..."
echo "当前用户: $(whoami)"
echo "当前目录: $(pwd)"
echo "Nginx进程:"
ps aux | grep nginx | grep -v grep

# 2. 停止所有相关服务
log_info "停止所有相关服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 3. 重新收集静态文件
log_info "重新收集静态文件..."
python manage.py collectstatic --noinput --clear --settings=config.settings.production

# 4. 修复目录权限
log_info "修复目录权限..."
chown -R admin:admin /home/admin/QAToolbox/
chmod -R 755 /home/admin/QAToolbox/

# 5. 修复静态文件权限
log_info "修复静态文件权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chown -R www-data:www-data /home/admin/QAToolbox/static/
chmod -R 755 /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/static/

# 6. 确保目录存在
log_info "确保目录存在..."
mkdir -p /home/admin/QAToolbox/staticfiles/css
mkdir -p /home/admin/QAToolbox/staticfiles/js
mkdir -p /home/admin/QAToolbox/staticfiles/images
mkdir -p /home/admin/QAToolbox/staticfiles/fonts

# 7. 修复目录权限
log_info "修复目录权限..."
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/staticfiles/

# 8. 检查关键文件
log_info "检查关键文件..."
ls -la /home/admin/QAToolbox/staticfiles/ | head -10
ls -la /home/admin/QAToolbox/staticfiles/css/ 2>/dev/null || log_warning "css目录不存在"
ls -la /home/admin/QAToolbox/staticfiles/js/ 2>/dev/null || log_warning "js目录不存在"

# 9. 测试文件访问权限
log_info "测试文件访问权限..."
if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/geek.css && log_success "geek.css 可读" || log_error "geek.css 不可读"
else
    log_warning "geek.css 不存在"
fi

if [ -f "/home/admin/QAToolbox/staticfiles/responsive.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/responsive.css && log_success "responsive.css 可读" || log_error "responsive.css 不可读"
else
    log_warning "responsive.css 不存在"
fi

# 10. 创建优化的Nginx配置
log_info "创建优化的Nginx配置..."
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 静态文件 - 优化配置
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
        
        # 处理CSS文件
        location ~* \.css$ {
            add_header Content-Type text/css;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理JS文件
        location ~* \.js$ {
            add_header Content-Type application/javascript;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理图片文件
        location ~* \.(png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理字体文件
        location ~* \.(woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # favicon处理
    location = /favicon.ico {
        alias /home/admin/QAToolbox/staticfiles/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    location = /favicon.svg {
        alias /home/admin/QAToolbox/staticfiles/favicon.svg;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        proxy_buffering off;
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 11. 启用站点
log_info "启用站点..."
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 12. 测试Nginx配置
log_info "测试Nginx配置..."
nginx -t

# 13. 启动服务
log_info "启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

# 14. 等待服务启动
log_info "等待服务启动..."
sleep 10

# 15. 检查服务状态
log_info "检查服务状态..."
systemctl status nginx --no-pager -l
supervisorctl status qatoolbox

# 16. 测试静态文件访问
log_info "测试静态文件访问..."
echo "测试CSS文件:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || log_warning "geek.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || log_warning "responsive.css 访问失败"
curl -I http://47.103.143.152/static/css/feature-recommendation.css 2>/dev/null | head -1 || log_warning "feature-recommendation.css 访问失败"

echo "测试JS文件:"
curl -I http://47.103.143.152/static/js/top_ui_functions.js 2>/dev/null | head -1 || log_warning "top_ui_functions.js 访问失败"
curl -I http://47.103.143.152/static/js/auth.js 2>/dev/null | head -1 || log_warning "auth.js 访问失败"

echo "测试favicon:"
curl -I http://47.103.143.152/static/favicon.ico 2>/dev/null | head -1 || log_warning "favicon.ico 访问失败"
curl -I http://47.103.143.152/static/favicon.svg 2>/dev/null | head -1 || log_warning "favicon.svg 访问失败"

# 17. 测试网站访问
log_info "测试网站访问..."
curl -s http://47.103.143.152/ > /dev/null && log_success "网站访问成功" || log_error "网站访问失败"

# 18. 检查错误日志
log_info "检查错误日志..."
echo "Nginx错误日志:"
tail -n 5 /var/log/nginx/error.log

echo "Django日志:"
tail -n 5 /var/log/qatoolbox/django.log 2>/dev/null || log_warning "Django日志不存在"

log_success "=========================================="
log_success "静态文件完整修复完成！"
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
echo "  - Nginx配置: nginx -t"
echo "  - 服务状态: systemctl status nginx && supervisorctl status qatoolbox"
echo "  - 错误日志: tail -f /var/log/nginx/error.log"
echo
log_success "现在静态文件应该可以正常加载了！"
log_success "=========================================="