#!/bin/bash

# 修复nginx配置脚本
echo "=== 修复nginx配置 ==="

PROJECT_DIR="/home/admin/QAToolbox"
NGINX_STATIC_DIR="/var/www/static"
NGINX_MEDIA_DIR="/var/www/media"

# 1. 停止服务
echo "1. 停止服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 2. 创建nginx静态文件目录
echo "2. 创建nginx静态文件目录..."
mkdir -p "$NGINX_STATIC_DIR"
mkdir -p "$NGINX_MEDIA_DIR"

# 3. 重新收集静态文件
echo "3. 重新收集静态文件..."
cd "$PROJECT_DIR"
python manage.py collectstatic --noinput --clear

# 4. 复制静态文件到nginx目录
echo "4. 复制静态文件到nginx目录..."
cp -r "$PROJECT_DIR/staticfiles"/* "$NGINX_STATIC_DIR/" 2>/dev/null || true
cp -r "$PROJECT_DIR/media"/* "$NGINX_MEDIA_DIR/" 2>/dev/null || true

# 5. 设置权限
echo "5. 设置权限..."
chown -R www-data:www-data "$NGINX_STATIC_DIR"
chown -R www-data:www-data "$NGINX_MEDIA_DIR"
chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
chown -R www-data:www-data "$PROJECT_DIR/media"

chmod -R 755 "$NGINX_STATIC_DIR"
chmod -R 755 "$NGINX_MEDIA_DIR"
chmod -R 755 "$PROJECT_DIR/staticfiles"
chmod -R 755 "$PROJECT_DIR/media"

# 6. 备份现有nginx配置
echo "6. 备份现有nginx配置..."
if [ -f "/etc/nginx/sites-available/default" ]; then
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ 已备份现有配置"
fi

# 7. 创建新的nginx配置
echo "7. 创建新的nginx配置..."
cat > /etc/nginx/sites-available/default << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin 47.103.143.152 localhost;
    
    # 静态文件配置
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 媒体文件配置
    location /media/ {
        alias /var/www/media/;
        expires 1y;
        add_header Cache-Control "public";
        access_log off;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 8. 测试nginx配置
echo "8. 测试nginx配置..."
nginx -t && echo "✓ nginx配置语法正确" || echo "✗ nginx配置语法错误"

# 9. 重新加载nginx
echo "9. 重新加载nginx..."
systemctl reload nginx

# 10. 启动服务
echo "10. 启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

# 11. 等待启动
echo "11. 等待服务启动..."
sleep 10

# 12. 检查文件
echo "12. 检查关键文件..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    echo "✓ geek.css 存在于nginx目录"
    ls -la "$NGINX_STATIC_DIR/geek.css"
else
    echo "✗ geek.css 不存在，查找所有CSS文件:"
    find "$NGINX_STATIC_DIR" -name "*.css" -type f | head -5
fi

# 13. 测试访问
echo "13. 测试访问..."
echo "测试静态文件:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1

echo "测试主页:"
curl -I http://47.103.143.152/ 2>/dev/null | head -1

# 14. 显示状态
echo "14. 服务状态:"
systemctl status nginx --no-pager -l | head -3
supervisorctl status qatoolbox

echo ""
echo "=== 修复完成 ==="
echo "如果还有问题，请检查:"
echo "1. nginx错误日志: tail -f /var/log/nginx/error.log"
echo "2. Django日志: tail -f $PROJECT_DIR/logs/django.log"
