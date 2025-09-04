#!/bin/bash

# 静态文件问题诊断脚本
echo "=== 静态文件问题诊断 ==="

PROJECT_DIR="/home/admin/QAToolbox"
NGINX_STATIC_DIR="/var/www/static"

echo "1. 检查Django静态文件目录:"
if [ -d "$PROJECT_DIR/staticfiles" ]; then
    echo "✓ Django静态文件目录存在: $PROJECT_DIR/staticfiles"
    ls -la "$PROJECT_DIR/staticfiles" | head -5
    if [ -f "$PROJECT_DIR/staticfiles/geek.css" ]; then
        echo "✓ geek.css 存在于Django目录"
        ls -la "$PROJECT_DIR/staticfiles/geek.css"
    else
        echo "✗ geek.css 不存在于Django目录"
    fi
else
    echo "✗ Django静态文件目录不存在"
fi

echo ""
echo "2. 检查nginx静态文件目录:"
if [ -d "$NGINX_STATIC_DIR" ]; then
    echo "✓ nginx静态文件目录存在: $NGINX_STATIC_DIR"
    ls -la "$NGINX_STATIC_DIR" | head -5
    if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
        echo "✓ geek.css 存在于nginx目录"
        ls -la "$NGINX_STATIC_DIR/geek.css"
    else
        echo "✗ geek.css 不存在于nginx目录"
    fi
else
    echo "✗ nginx静态文件目录不存在"
fi

echo ""
echo "3. 检查nginx配置:"
if [ -f "/etc/nginx/sites-available/default" ]; then
    echo "检查 /etc/nginx/sites-available/default:"
    grep -A 5 -B 5 "location /static/" /etc/nginx/sites-available/default || echo "未找到static配置"
fi

if [ -f "/etc/nginx/nginx.conf" ]; then
    echo "检查 /etc/nginx/nginx.conf:"
    grep -A 5 -B 5 "location /static/" /etc/nginx/nginx.conf || echo "未找到static配置"
fi

echo ""
echo "4. 检查nginx错误日志:"
echo "最近的nginx错误:"
tail -10 /var/log/nginx/error.log 2>/dev/null || echo "无法读取nginx错误日志"

echo ""
echo "5. 检查服务状态:"
echo "nginx状态:"
systemctl status nginx --no-pager -l | head -3

echo "qatoolbox状态:"
supervisorctl status qatoolbox

echo ""
echo "6. 测试文件访问:"
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    echo "测试www-data用户访问:"
    sudo -u www-data test -r "$NGINX_STATIC_DIR/geek.css" && echo "✓ 可读" || echo "✗ 不可读"
    
    echo "测试文件权限:"
    ls -la "$NGINX_STATIC_DIR/geek.css"
    
    echo "测试HTTP访问:"
    curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1
else
    echo "✗ geek.css 文件不存在，无法测试"
fi

echo ""
echo "7. 检查防火墙:"
ufw status 2>/dev/null || echo "防火墙未启用或无法检查"

echo ""
echo "=== 诊断完成 ==="
