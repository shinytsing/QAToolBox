#!/bin/bash

# QAToolBox 简单修复静态文件脚本
# 直接解决权限问题

set -e

echo "=========================================="
echo "QAToolBox 简单修复静态文件脚本"
echo "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

echo "1. 检查当前权限..."
ls -la /home/admin/QAToolbox/staticfiles/ | head -5

echo "2. 停止所有服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

echo "3. 彻底修复权限..."
# 修复项目目录权限
chown -R admin:admin /home/admin/QAToolbox/
chmod -R 755 /home/admin/QAToolbox/

# 修复staticfiles目录权限
chown -R www-data:www-data /home/admin/QAToolbox/staticfiles/
chmod -R 755 /home/admin/QAToolbox/staticfiles/

# 确保所有子目录权限正确
find /home/admin/QAToolbox/staticfiles/ -type d -exec chmod 755 {} \;
find /home/admin/QAToolbox/staticfiles/ -type f -exec chmod 644 {} \;

echo "4. 检查关键文件权限..."
ls -la /home/admin/QAToolbox/staticfiles/geek.css 2>/dev/null || echo "geek.css 不存在"
ls -la /home/admin/QAToolbox/staticfiles/responsive.css 2>/dev/null || echo "responsive.css 不存在"
ls -la /home/admin/QAToolbox/staticfiles/css/feature-recommendation.css 2>/dev/null || echo "feature-recommendation.css 不存在"

echo "5. 测试文件访问权限..."
if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/geek.css && echo "geek.css 可读" || echo "geek.css 不可读"
fi

if [ -f "/home/admin/QAToolbox/staticfiles/responsive.css" ]; then
    sudo -u www-data test -r /home/admin/QAToolbox/staticfiles/responsive.css && echo "responsive.css 可读" || echo "responsive.css 不可读"
fi

echo "6. 创建简单的Nginx配置..."
cat > /etc/nginx/sites-available/qatoolbox << 'NGINX_EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 静态文件
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 30d;
        access_log off;
    }
    
    # favicon
    location = /favicon.ico {
        alias /home/admin/QAToolbox/staticfiles/favicon.ico;
        expires 1y;
        access_log off;
    }
    
    location = /favicon.svg {
        alias /home/admin/QAToolbox/staticfiles/favicon.svg;
        expires 1y;
        access_log off;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

echo "7. 启用站点..."
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "8. 测试Nginx配置..."
nginx -t

echo "9. 启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

echo "10. 等待服务启动..."
sleep 10

echo "11. 检查服务状态..."
systemctl status nginx --no-pager -l
supervisorctl status qatoolbox

echo "12. 测试静态文件访问..."
echo "测试CSS文件:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1 || echo "geek.css 访问失败"
curl -I http://47.103.143.152/static/responsive.css 2>/dev/null | head -1 || echo "responsive.css 访问失败"
curl -I http://47.103.143.152/static/css/feature-recommendation.css 2>/dev/null | head -1 || echo "feature-recommendation.css 访问失败"

echo "测试JS文件:"
curl -I http://47.103.143.152/static/js/top_ui_functions.js 2>/dev/null | head -1 || echo "top_ui_functions.js 访问失败"
curl -I http://47.103.143.152/static/js/auth.js 2>/dev/null | head -1 || echo "auth.js 访问失败"

echo "测试favicon:"
curl -I http://47.103.143.152/static/favicon.ico 2>/dev/null | head -1 || echo "favicon.ico 访问失败"
curl -I http://47.103.143.152/static/favicon.svg 2>/dev/null | head -1 || echo "favicon.svg 访问失败"

echo "13. 测试网站访问..."
curl -s http://47.103.143.152/ > /dev/null && echo "网站访问成功" || echo "网站访问失败"

echo "14. 检查错误日志..."
echo "Nginx错误日志:"
tail -n 5 /var/log/nginx/error.log

echo "=========================================="
echo "静态文件修复完成！"
echo "=========================================="
echo
echo "测试访问:"
echo "  - 网站: http://47.103.143.152"
echo "  - 静态文件: http://47.103.143.152/static/"
echo "  - CSS文件: http://47.103.143.152/static/geek.css"
echo "  - JS文件: http://47.103.143.152/static/js/top_ui_functions.js"
echo
echo "如果仍有问题，请检查:"
echo "  - 文件权限: ls -la /home/admin/QAToolbox/staticfiles/"
echo "  - Nginx配置: nginx -t"
echo "  - 服务状态: systemctl status nginx && supervisorctl status qatoolbox"
echo "  - 错误日志: tail -f /var/log/nginx/error.log"
echo
echo "现在静态文件应该可以正常加载了！"
echo "=========================================="
