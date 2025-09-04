#!/bin/bash

# 一键修复静态文件问题
echo "=== 一键修复静态文件问题 ==="

# 设置变量
PROJECT_DIR="/home/admin/QAToolbox"
NGINX_STATIC_DIR="/var/www/static"
NGINX_MEDIA_DIR="/var/www/media"

# 1. 停止所有服务
echo "1. 停止服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 2. 创建必要的目录
echo "2. 创建目录..."
mkdir -p "$NGINX_STATIC_DIR"
mkdir -p "$NGINX_MEDIA_DIR"
mkdir -p "$PROJECT_DIR/staticfiles"
mkdir -p "$PROJECT_DIR/media"

# 3. 重新收集静态文件
echo "3. 重新收集静态文件..."
cd "$PROJECT_DIR"
python manage.py collectstatic --noinput --clear 2>/dev/null || echo "收集静态文件失败，继续..."

# 4. 复制文件到nginx目录
echo "4. 复制文件到nginx目录..."
if [ -d "$PROJECT_DIR/staticfiles" ]; then
    cp -r "$PROJECT_DIR/staticfiles"/* "$NGINX_STATIC_DIR/" 2>/dev/null || true
    echo "静态文件复制完成"
fi

if [ -d "$PROJECT_DIR/media" ]; then
    cp -r "$PROJECT_DIR/media"/* "$NGINX_MEDIA_DIR/" 2>/dev/null || true
    echo "媒体文件复制完成"
fi

# 5. 设置正确的权限
echo "5. 设置权限..."
chown -R www-data:www-data "$NGINX_STATIC_DIR"
chown -R www-data:www-data "$NGINX_MEDIA_DIR"
chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
chown -R www-data:www-data "$PROJECT_DIR/media"

chmod -R 755 "$NGINX_STATIC_DIR"
chmod -R 755 "$NGINX_MEDIA_DIR"
chmod -R 755 "$PROJECT_DIR/staticfiles"
chmod -R 755 "$PROJECT_DIR/media"

# 6. 检查关键文件
echo "6. 检查关键文件..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    echo "✓ geek.css 存在于nginx目录"
    ls -la "$NGINX_STATIC_DIR/geek.css"
else
    echo "✗ geek.css 不存在，尝试查找..."
    find "$PROJECT_DIR" -name "geek.css" -type f 2>/dev/null | head -3
fi

# 7. 测试权限
echo "7. 测试权限..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    sudo -u www-data test -r "$NGINX_STATIC_DIR/geek.css" && echo "✓ geek.css 可读" || echo "✗ geek.css 不可读"
fi

# 8. 检查nginx配置
echo "8. 检查nginx配置..."
nginx -t && echo "✓ nginx配置正确" || echo "✗ nginx配置错误"

# 9. 启动服务
echo "9. 启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

# 10. 等待启动
echo "10. 等待服务启动..."
sleep 10

# 11. 测试访问
echo "11. 测试访问..."
echo "测试静态文件:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1

echo "测试主页:"
curl -I http://47.103.143.152/ 2>/dev/null | head -1

# 12. 显示状态
echo "12. 服务状态:"
systemctl status nginx --no-pager -l | head -3
supervisorctl status qatoolbox

echo ""
echo "=== 修复完成 ==="
echo "如果仍有问题，请运行: ./diagnose_static_issue.sh"
