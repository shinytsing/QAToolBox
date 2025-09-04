#!/bin/bash

# 修复nginx配置脚本 v2
echo "=== 修复nginx配置 v2 ==="

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

# 尝试不同的python命令
if command -v python3 &> /dev/null; then
    python3 manage.py collectstatic --noinput --clear
elif command -v python &> /dev/null; then
    python manage.py collectstatic --noinput --clear
else
    echo "警告: 找不到python命令，跳过收集静态文件"
fi

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

# 6. 检查nginx配置结构
echo "6. 检查nginx配置结构..."
echo "检查 /etc/nginx/nginx.conf:"
if grep -q "include /etc/nginx/sites-enabled" /etc/nginx/nginx.conf; then
    echo "使用 sites-enabled 结构"
    NGINX_CONFIG="/etc/nginx/sites-available/default"
    NGINX_ENABLED="/etc/nginx/sites-enabled/default"
elif grep -q "include /etc/nginx/conf.d" /etc/nginx/nginx.conf; then
    echo "使用 conf.d 结构"
    NGINX_CONFIG="/etc/nginx/conf.d/default.conf"
    NGINX_ENABLED="/etc/nginx/conf.d/default.conf"
else
    echo "使用主配置文件"
    NGINX_CONFIG="/etc/nginx/nginx.conf"
    NGINX_ENABLED="/etc/nginx/nginx.conf"
fi

# 7. 备份现有配置
echo "7. 备份现有配置..."
if [ -f "$NGINX_CONFIG" ]; then
    cp "$NGINX_CONFIG" "${NGINX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "✓ 已备份现有配置: $NGINX_CONFIG"
fi

# 8. 创建nginx配置
echo "8. 创建nginx配置..."

if [[ "$NGINX_CONFIG" == *"sites-available"* ]]; then
    # 使用 sites-available 结构
    cat > "$NGINX_CONFIG" << 'EOF'
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

    # 创建软链接
    ln -sf "$NGINX_CONFIG" "$NGINX_ENABLED" 2>/dev/null || true
    echo "✓ 已创建 sites-available 配置并启用"

elif [[ "$NGINX_CONFIG" == *"conf.d"* ]]; then
    # 使用 conf.d 结构
    cat > "$NGINX_CONFIG" << 'EOF'
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
    echo "✓ 已创建 conf.d 配置"

else
    # 直接修改主配置文件
    echo "直接修改主配置文件..."
    # 这里需要更复杂的逻辑来修改主配置文件
    echo "警告: 需要手动修改主配置文件"
fi

# 9. 测试nginx配置
echo "9. 测试nginx配置..."
nginx -t && echo "✓ nginx配置语法正确" || echo "✗ nginx配置语法错误"

# 10. 启动nginx
echo "10. 启动nginx..."
systemctl start nginx
systemctl enable nginx

# 11. 启动应用
echo "11. 启动应用..."
supervisorctl start qatoolbox

# 12. 等待启动
echo "12. 等待服务启动..."
sleep 10

# 13. 检查文件
echo "13. 检查关键文件..."
echo "nginx静态文件目录内容:"
ls -la "$NGINX_STATIC_DIR" | head -10

echo "查找CSS文件:"
find "$NGINX_STATIC_DIR" -name "*.css" -type f | head -5

# 14. 测试访问
echo "14. 测试访问..."
echo "测试静态文件:"
curl -I http://47.103.143.152/static/admin/css/base.css 2>/dev/null | head -1

echo "测试主页:"
curl -I http://47.103.143.152/ 2>/dev/null | head -1

# 15. 显示状态
echo "15. 服务状态:"
systemctl status nginx --no-pager -l | head -3
supervisorctl status qatoolbox

echo ""
echo "=== 修复完成 ==="
echo "配置文件位置: $NGINX_CONFIG"
echo "如果还有问题，请检查:"
echo "1. nginx错误日志: tail -f /var/log/nginx/error.log"
echo "2. Django日志: tail -f $PROJECT_DIR/logs/django.log"
