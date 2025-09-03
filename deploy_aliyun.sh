#!/bin/bash

# 阿里云部署脚本
# 用于部署QAToolBox到阿里云服务器

set -e  # 遇到错误立即退出

echo "🚀 开始部署QAToolBox到阿里云..."

# 检查Python版本
echo "📋 检查Python版本..."
python3 --version

# 检查PostgreSQL
echo "📋 检查PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL未安装，请先安装PostgreSQL"
    exit 1
fi

# 检查Redis
echo "📋 检查Redis..."
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis未安装，请先安装Redis"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
python manage.py migrate --settings=config.settings.aliyun_production

# 收集静态文件
echo "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.aliyun_production

# 创建超级用户（如果不存在）
echo "👤 检查超级用户..."
python manage.py shell --settings=config.settings.aliyun_production -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户已创建: admin/admin123')
else:
    print('超级用户已存在')
"

# 设置文件权限
echo "🔐 设置文件权限..."
sudo chown -R www-data:www-data /var/www/qatoolbox/
sudo chmod -R 755 /var/www/qatoolbox/

# 创建systemd服务文件
echo "⚙️ 创建systemd服务..."
sudo tee /etc/systemd/system/qatoolbox.service > /dev/null <<EOF
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/www/qatoolbox
Environment=DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
ExecStart=/var/www/qatoolbox/.venv/bin/python start_aliyun.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 重载systemd并启动服务
echo "🔄 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable qatoolbox
sudo systemctl start qatoolbox

# 检查服务状态
echo "📊 检查服务状态..."
sudo systemctl status qatoolbox --no-pager

# 配置Nginx（如果存在）
if command -v nginx &> /dev/null; then
    echo "🌐 配置Nginx..."
    sudo tee /etc/nginx/sites-available/qatoolbox > /dev/null <<EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin app.shenyiqing.xin;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias /var/www/qatoolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
fi

echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  - 本地: http://localhost:8000"
echo "  - 外网: http://shenyiqing.xin"
echo ""
echo "🔧 管理命令:"
echo "  - 查看日志: sudo journalctl -u qatoolbox -f"
echo "  - 重启服务: sudo systemctl restart qatoolbox"
echo "  - 停止服务: sudo systemctl stop qatoolbox"
echo ""
echo "👤 管理员账户: admin / admin123"