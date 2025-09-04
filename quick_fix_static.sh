#!/bin/bash

# 快速修复静态文件问题
echo "=== 快速修复静态文件问题 ==="

# 停止服务
supervisorctl stop qatoolbox
systemctl stop nginx

# 创建nginx静态文件目录并复制文件
mkdir -p /var/www/static
mkdir -p /var/www/media

# 复制静态文件
cp -r /home/admin/QAToolbox/staticfiles/* /var/www/static/ 2>/dev/null || true
cp -r /home/admin/QAToolbox/media/* /var/www/media/ 2>/dev/null || true

# 设置权限
chown -R www-data:www-data /var/www/static
chown -R www-data:www-data /var/www/media
chmod -R 755 /var/www/static
chmod -R 755 /var/www/media

# 检查geek.css
if [ -f "/var/www/static/geek.css" ]; then
    echo "✓ geek.css 已复制到nginx目录"
    ls -la /var/www/static/geek.css
else
    echo "✗ geek.css 未找到，尝试从Django目录复制"
    if [ -f "/home/admin/QAToolbox/staticfiles/geek.css" ]; then
        cp /home/admin/QAToolbox/staticfiles/geek.css /var/www/static/
        chown www-data:www-data /var/www/static/geek.css
        chmod 644 /var/www/static/geek.css
        echo "✓ geek.css 已复制"
    fi
fi

# 测试权限
sudo -u www-data test -r /var/www/static/geek.css && echo "✓ geek.css 可读" || echo "✗ geek.css 不可读"

# 启动服务
systemctl start nginx
supervisorctl start qatoolbox

# 等待启动
sleep 5

# 测试访问
echo "测试访问:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1

echo "修复完成！"
