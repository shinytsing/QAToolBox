#!/bin/bash

# 终极静态文件权限修复脚本
# 解决nginx配置路径不匹配和权限问题

echo "=== 终极静态文件权限修复脚本 ==="
echo "开始修复静态文件访问问题..."

# 设置变量
PROJECT_DIR="/home/admin/QAToolbox"
NGINX_STATIC_DIR="/var/www/static"
NGINX_MEDIA_DIR="/var/www/media"
DJANGO_STATIC_DIR="$PROJECT_DIR/staticfiles"
DJANGO_MEDIA_DIR="$PROJECT_DIR/media"

# 停止服务
echo "1. 停止服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 创建nginx静态文件目录
echo "2. 创建nginx静态文件目录..."
mkdir -p "$NGINX_STATIC_DIR"
mkdir -p "$NGINX_MEDIA_DIR"

# 复制静态文件到nginx目录
echo "3. 复制静态文件到nginx目录..."
if [ -d "$DJANGO_STATIC_DIR" ]; then
    cp -r "$DJANGO_STATIC_DIR"/* "$NGINX_STATIC_DIR/" 2>/dev/null || true
    echo "静态文件复制完成"
else
    echo "警告: Django静态文件目录不存在: $DJANGO_STATIC_DIR"
fi

# 复制媒体文件到nginx目录
if [ -d "$DJANGO_MEDIA_DIR" ]; then
    cp -r "$DJANGO_MEDIA_DIR"/* "$NGINX_MEDIA_DIR/" 2>/dev/null || true
    echo "媒体文件复制完成"
else
    echo "警告: Django媒体文件目录不存在: $DJANGO_MEDIA_DIR"
fi

# 设置正确的权限
echo "4. 设置正确的权限..."
chown -R www-data:www-data "$NGINX_STATIC_DIR"
chown -R www-data:www-data "$NGINX_MEDIA_DIR"
chmod -R 755 "$NGINX_STATIC_DIR"
chmod -R 755 "$NGINX_MEDIA_DIR"

# 同时修复Django静态文件目录权限
if [ -d "$DJANGO_STATIC_DIR" ]; then
    chown -R www-data:www-data "$DJANGO_STATIC_DIR"
    chmod -R 755 "$DJANGO_STATIC_DIR"
fi

if [ -d "$DJANGO_MEDIA_DIR" ]; then
    chown -R www-data:www-data "$DJANGO_MEDIA_DIR"
    chmod -R 755 "$DJANGO_MEDIA_DIR"
fi

# 检查关键文件是否存在
echo "5. 检查关键文件..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    echo "✓ geek.css 存在于nginx目录"
    ls -la "$NGINX_STATIC_DIR/geek.css"
else
    echo "✗ geek.css 不存在于nginx目录"
    echo "尝试从Django目录复制..."
    if [ -f "$DJANGO_STATIC_DIR/geek.css" ]; then
        cp "$DJANGO_STATIC_DIR/geek.css" "$NGINX_STATIC_DIR/"
        chown www-data:www-data "$NGINX_STATIC_DIR/geek.css"
        chmod 644 "$NGINX_STATIC_DIR/geek.css"
        echo "✓ geek.css 已复制到nginx目录"
    else
        echo "✗ geek.css 在Django目录中也不存在"
    fi
fi

# 测试文件访问权限
echo "6. 测试文件访问权限..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    sudo -u www-data test -r "$NGINX_STATIC_DIR/geek.css" && echo "✓ geek.css 可读" || echo "✗ geek.css 不可读"
else
    echo "✗ geek.css 文件不存在，无法测试"
fi

# 检查nginx配置
echo "7. 检查nginx配置..."
if [ -f "/etc/nginx/sites-available/default" ]; then
    echo "检查默认nginx配置..."
    grep -n "location /static/" /etc/nginx/sites-available/default || echo "未找到static配置"
fi

if [ -f "/etc/nginx/nginx.conf" ]; then
    echo "检查主nginx配置..."
    grep -n "location /static/" /etc/nginx/nginx.conf || echo "未找到static配置"
fi

# 重新加载nginx配置
echo "8. 重新加载nginx配置..."
nginx -t && echo "✓ nginx配置语法正确" || echo "✗ nginx配置语法错误"
systemctl reload nginx 2>/dev/null || true

# 启动服务
echo "9. 启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

# 等待服务启动
echo "10. 等待服务启动..."
sleep 10

# 测试访问
echo "11. 测试访问..."
echo "测试静态文件访问:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1

echo "测试主页访问:"
curl -I http://47.103.143.152/ 2>/dev/null | head -1

# 显示最终状态
echo "12. 最终状态检查..."
echo "=== 目录权限 ==="
ls -la "$NGINX_STATIC_DIR" | head -5
echo "=== 服务状态 ==="
systemctl status nginx --no-pager -l | head -3
supervisorctl status qatoolbox

echo "=== 修复完成 ==="
echo "如果仍有问题，请检查:"
echo "1. nginx错误日志: tail -f /var/log/nginx/error.log"
echo "2. Django日志: tail -f $PROJECT_DIR/logs/django.log"
echo "3. 防火墙设置: ufw status"
