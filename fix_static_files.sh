#!/bin/bash

# QAToolBox 修复静态文件配置脚本
# 解决静态文件403 Forbidden错误

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
log_info "QAToolBox 修复静态文件配置脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查静态文件目录
log_info "检查静态文件目录..."
ls -la static/ 2>/dev/null || log_warning "static目录不存在"
ls -la staticfiles/ 2>/dev/null || log_warning "staticfiles目录不存在"

# 2. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.production

# 3. 检查静态文件权限
log_info "检查静态文件权限..."
chown -R admin:admin /home/admin/QAToolbox/staticfiles/
chown -R admin:admin /home/admin/QAToolbox/static/
chmod -R 755 /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/static/

# 4. 检查Nginx静态文件配置
log_info "检查Nginx静态文件配置..."
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 静态文件 - 修复权限和路径
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
        # 允许所有文件类型
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
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
    
    # favicon.ico
    location = /favicon.ico {
        alias /home/admin/QAToolbox/staticfiles/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # favicon.svg
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

# 5. 测试Nginx配置
log_info "测试Nginx配置..."
nginx -t

# 6. 重新加载Nginx
log_info "重新加载Nginx..."
systemctl reload nginx

# 7. 检查静态文件是否存在
log_info "检查关键静态文件..."
if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
    log_success "geek.css 存在"
else
    log_warning "geek.css 不存在"
fi

if [ -f "/home/admin/QAToolbox/staticfiles/feature-recommendation.css" ]; then
    log_success "feature-recommendation.css 存在"
else
    log_warning "feature-recommendation.css 不存在"
fi

if [ -f "/home/admin/QAToolbox/staticfiles/responsive.css" ]; then
    log_success "responsive.css 存在"
else
    log_warning "responsive.css 不存在"
fi

# 8. 测试静态文件访问
log_info "测试静态文件访问..."
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || log_warning "geek.css 访问失败"
curl -I http://47.103.143.152/static/feature-recommendation.css 2>/dev/null | head -1 || log_warning "feature-recommendation.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || log_warning "responsive.css 访问失败"

# 9. 检查Django设置中的静态文件配置
log_info "检查Django静态文件设置..."
grep -A 5 -B 5 "STATIC" config/settings/production.py

# 10. 重启Django应用
log_info "重启Django应用..."
supervisorctl restart qatoolbox

# 11. 等待应用启动
log_info "等待应用启动..."
sleep 10

# 12. 检查应用状态
log_info "检查应用状态..."
supervisorctl status qatoolbox

# 13. 测试网站访问
log_info "测试网站访问..."
curl -s http://47.103.143.152/ > /dev/null && log_success "网站访问成功" || log_error "网站访问失败"

# 14. 检查Nginx错误日志
log_info "检查Nginx错误日志..."
tail -n 10 /var/log/nginx/error.log

log_success "=========================================="
log_success "静态文件配置修复完成！"
log_success "=========================================="
echo
log_info "📱 测试访问:"
echo "  - 网站: http://47.103.143.152"
echo "  - 静态文件: http://47.103.143.152/static/"
echo "  - CSS文件: http://47.103.143.152/static/geek.css"
echo
log_info "🛠️  如果仍有问题，请检查:"
echo "  - 静态文件是否存在: ls -la /home/admin/QAToolbox/staticfiles/"
echo "  - 文件权限: chmod -R 755 /home/admin/QAToolbox/staticfiles/"
echo "  - Nginx日志: tail -f /var/log/nginx/error.log"
echo
log_success "现在静态文件应该可以正常加载了！"
log_success "=========================================="
