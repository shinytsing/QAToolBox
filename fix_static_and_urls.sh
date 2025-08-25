#!/bin/bash

# 修复静态文件403和URL问题的脚本
# 用于 shenyiqing.xin 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始修复静态文件403和URL问题...${NC}"

# 1. 停止服务
echo -e "${YELLOW}1. 停止服务...${NC}"
sudo systemctl stop qatoolbox || true
sudo systemctl stop nginx || true

# 2. 修复静态文件权限
echo -e "${YELLOW}2. 修复静态文件权限...${NC}"
cd /home/qatoolbox/QAToolBox

# 重新收集静态文件
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.full_frontend

# 设置正确的权限
sudo chown -R www-data:www-data /home/qatoolbox/QAToolBox/staticfiles/
sudo chmod -R 755 /home/qatoolbox/QAToolBox/staticfiles/
sudo find /home/qatoolbox/QAToolBox/staticfiles/ -type f -exec chmod 644 {} \;

# 3. 修复URLs配置
echo -e "${YELLOW}3. 修复URLs配置...${NC}"

# 检查主URLs文件
if [ ! -f "urls.py" ]; then
    cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

def home_view(request):
    from django.shortcuts import render
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('', home_view, name='home'),
]

# 动态添加应用URLs
try:
    urlpatterns.append(path('tools/', include('apps.tools.urls')))
except ImportError:
    pass

try:
    urlpatterns.append(path('users/', include('apps.users.urls')))
except ImportError:
    pass

try:
    urlpatterns.append(path('content/', include('apps.content.urls')))
except ImportError:
    pass

try:
    urlpatterns.append(path('share/', include('apps.share.urls')))
except ImportError:
    pass

# 静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF
    sudo chown qatoolbox:qatoolbox urls.py
fi

# 4. 修复users应用的URLs
echo -e "${YELLOW}4. 修复users应用的URLs...${NC}"
if [ ! -f "apps/users/urls.py" ]; then
    cat > apps/users/urls.py << 'EOF'
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('theme/', views.theme_view, name='theme'),
]
EOF
    sudo chown qatoolbox:qatoolbox apps/users/urls.py
fi

# 5. 更新Nginx配置
echo -e "${YELLOW}5. 更新Nginx配置...${NC}"
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name shenyiqing.xin;

    ssl_certificate /etc/ssl/certs/qatoolbox.crt;
    ssl_private_key /etc/ssl/private/qatoolbox.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;
    
    # 静态文件配置
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        
        # 确保所有静态文件都可以被访问
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }
    
    # 媒体文件配置
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
        expires 30d;
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

# 6. 测试Nginx配置
echo -e "${YELLOW}6. 测试Nginx配置...${NC}"
sudo nginx -t

# 7. 运行数据库迁移
echo -e "${YELLOW}7. 运行数据库迁移...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py migrate --settings=config.settings.full_frontend

# 8. 重新检查Django配置
echo -e "${YELLOW}8. 检查Django配置...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py check --settings=config.settings.full_frontend

# 9. 更新systemd服务配置
echo -e "${YELLOW}9. 更新systemd服务配置...${NC}"
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=simple
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=PATH=/home/qatoolbox/QAToolBox/.venv/bin
Environment=PYTHONPATH=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.full_frontend
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 300 --access-logfile - --error-logfile - config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 10. 重新加载systemd配置
sudo systemctl daemon-reload

# 11. 启动服务
echo -e "${YELLOW}11. 启动服务...${NC}"
sudo systemctl start nginx
sudo systemctl start qatoolbox

# 12. 等待服务启动
sleep 5

# 13. 检查服务状态
echo -e "${YELLOW}12. 检查服务状态...${NC}"
echo "Nginx状态:"
sudo systemctl status nginx --no-pager -l

echo -e "\nQAToolBox服务状态:"
sudo systemctl status qatoolbox --no-pager -l

# 14. 测试静态文件访问
echo -e "${YELLOW}13. 测试静态文件访问...${NC}"
echo "测试CSS文件:"
curl -I https://shenyiqing.xin/static/geek.css 2>/dev/null | head -1

echo "测试JS文件:"
curl -I https://shenyiqing.xin/static/js/auth.js 2>/dev/null | head -1

echo "测试favicon:"
curl -I https://shenyiqing.xin/static/favicon.ico 2>/dev/null | head -1

# 15. 测试主页
echo -e "${YELLOW}14. 测试主页访问...${NC}"
echo "测试主页:"
curl -I https://shenyiqing.xin/ 2>/dev/null | head -1

echo -e "${GREEN}修复完成！${NC}"
echo -e "${BLUE}请访问 https://shenyiqing.xin 检查网站是否正常工作${NC}"
echo -e "${BLUE}如果还有问题，请检查以下日志:${NC}"
echo "  - sudo journalctl -u qatoolbox -f"
echo "  - sudo tail -f /var/log/nginx/error.log"
