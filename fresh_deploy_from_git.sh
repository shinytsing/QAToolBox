#!/bin/bash

# 从Git重新拉取项目并完全重新部署
# 用于 shenyiqing.xin 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始从Git重新拉取项目并重新部署...${NC}"

# 1. 停止所有服务
echo -e "${YELLOW}1. 停止所有服务...${NC}"
sudo systemctl stop qatoolbox || true
sudo systemctl stop nginx || true

# 2. 备份当前的.env文件（如果存在）
echo -e "${YELLOW}2. 备份配置文件...${NC}"
if [ -f "/home/qatoolbox/QAToolBox/.env" ]; then
    sudo cp /home/qatoolbox/QAToolBox/.env /tmp/qatoolbox_env_backup
    echo "已备份.env文件到 /tmp/qatoolbox_env_backup"
fi

# 3. 完全删除旧项目目录
echo -e "${YELLOW}3. 删除旧项目目录...${NC}"
sudo rm -rf /home/qatoolbox/QAToolBox || true

# 4. 重新克隆项目
echo -e "${YELLOW}4. 重新克隆项目...${NC}"
cd /home/qatoolbox
sudo -u qatoolbox git clone https://github.com/shinytsing/QAToolbox.git QAToolBox || \
sudo -u qatoolbox git clone https://gitee.com/shinytsing/QAToolbox.git QAToolBox || \
sudo -u qatoolbox git clone https://ghproxy.com/https://github.com/shinytsing/QAToolbox.git QAToolBox

cd /home/qatoolbox/QAToolBox

# 5. 恢复.env文件
echo -e "${YELLOW}5. 恢复配置文件...${NC}"
if [ -f "/tmp/qatoolbox_env_backup" ]; then
    sudo cp /tmp/qatoolbox_env_backup .env
    sudo chown qatoolbox:qatoolbox .env
    echo "已恢复.env文件"
else
    # 创建基本的.env文件
    cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=shenyiqing.xin,127.0.0.1,localhost
EOF
    sudo chown qatoolbox:qatoolbox .env
fi

# 6. 创建并激活虚拟环境
echo -e "${YELLOW}6. 创建虚拟环境...${NC}"
sudo -u qatoolbox python3 -m venv .venv
sudo -u qatoolbox .venv/bin/pip install --upgrade pip

# 7. 安装依赖（使用中国镜像加速）
echo -e "${YELLOW}7. 安装Python依赖...${NC}"
sudo -u qatoolbox .venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

# 8. 创建完整的settings配置
echo -e "${YELLOW}8. 创建Django配置...${NC}"
cat > config/settings/production.py << 'EOF'
from .base import *
import os

# 生产环境配置
DEBUG = False
ALLOWED_HOSTS = ['shenyiqing.xin', '127.0.0.1', 'localhost', '47.103.143.152']

# 数据库配置 - 使用SQLite避免PostgreSQL问题
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 缓存配置
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# 安全配置
SECURE_SSL_REDIRECT = False  # Nginx处理SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/home/qatoolbox/QAToolBox/logs/django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# 确保所有应用都在INSTALLED_APPS中
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'apps.users',
    'apps.content',
    'apps.tools',
    'apps.share',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
EOF

sudo chown qatoolbox:qatoolbox config/settings/production.py

# 9. 更新wsgi.py
echo -e "${YELLOW}9. 更新WSGI配置...${NC}"
cat > config/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
application = get_wsgi_application()
EOF

sudo chown qatoolbox:qatoolbox config/wsgi.py

# 10. 创建日志目录
echo -e "${YELLOW}10. 创建日志目录...${NC}"
sudo -u qatoolbox mkdir -p logs media staticfiles

# 11. 运行Django检查和迁移
echo -e "${YELLOW}11. 运行Django命令...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py check --settings=config.settings.production
sudo -u qatoolbox .venv/bin/python manage.py migrate --settings=config.settings.production
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production

# 12. 创建超级用户（如果不存在）
echo -e "${YELLOW}12. 创建超级用户...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py shell --settings=config.settings.production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("超级用户已创建: admin/admin123")
else:
    print("超级用户admin已存在")
EOF

# 13. 设置文件权限
echo -e "${YELLOW}13. 设置文件权限...${NC}"
sudo chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
sudo chmod -R 755 /home/qatoolbox/QAToolBox/staticfiles
sudo chmod -R 755 /home/qatoolbox/QAToolBox/media

# 14. 创建systemd服务
echo -e "${YELLOW}14. 创建systemd服务...${NC}"
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
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 300 --access-logfile - --error-logfile - config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 15. 生成SSL证书
echo -e "${YELLOW}15. 生成SSL证书...${NC}"
sudo mkdir -p /etc/ssl/certs /etc/ssl/private
if [ ! -f "/etc/ssl/certs/qatoolbox.crt" ]; then
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/qatoolbox.key \
        -out /etc/ssl/certs/qatoolbox.crt \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/CN=shenyiqing.xin"
fi

# 16. 配置Nginx
echo -e "${YELLOW}16. 配置Nginx...${NC}"
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
    ssl_certificate_key /etc/ssl/private/qatoolbox.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 100M;
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
        expires 30d;
    }
    
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

sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/

# 17. 测试配置
echo -e "${YELLOW}17. 测试配置...${NC}"
sudo nginx -t

# 18. 重新加载systemd并启动服务
echo -e "${YELLOW}18. 启动服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable qatoolbox
sudo systemctl start qatoolbox
sudo systemctl start nginx

# 19. 等待服务启动
sleep 5

# 20. 检查服务状态
echo -e "${YELLOW}19. 检查服务状态...${NC}"
echo "QAToolBox服务状态:"
sudo systemctl status qatoolbox --no-pager -l | head -10

echo -e "\nNginx服务状态:"
sudo systemctl status nginx --no-pager -l | head -10

# 21. 测试访问
echo -e "${YELLOW}20. 测试访问...${NC}"
echo "测试HTTP重定向:"
curl -I http://shenyiqing.xin/ 2>/dev/null | head -2

echo -e "\n测试HTTPS主页:"
curl -I -k https://shenyiqing.xin/ 2>/dev/null | head -2

echo -e "\n测试静态文件:"
curl -I -k https://shenyiqing.xin/static/base.css 2>/dev/null | head -2

# 22. 显示完成信息
echo -e "${GREEN}部署完成！${NC}"
echo -e "${BLUE}网站地址: https://shenyiqing.xin${NC}"
echo -e "${BLUE}管理后台: https://shenyiqing.xin/admin${NC}"
echo -e "${BLUE}超级用户: admin / admin123${NC}"
echo -e "${BLUE}如有问题，请检查日志:${NC}"
echo "  - sudo journalctl -u qatoolbox -f"
echo "  - sudo tail -f /var/log/nginx/error.log"
echo "  - tail -f /home/qatoolbox/QAToolBox/logs/django.log"
