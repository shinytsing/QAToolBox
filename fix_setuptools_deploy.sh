#!/bin/bash

# 修复setuptools问题的部署方案

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "修复setuptools问题的部署方案"
log_info "服务器IP: 47.103.143.152"
log_info "域名: shenyiqing.xin"
log_info "=========================================="

# 1. 检查系统环境
log_info "检查系统环境..."
python3 --version
pip3 --version

# 2. 进入项目目录
log_info "进入项目目录..."
cd /home/admin/QAToolbox

# 3. 安装系统依赖
log_info "安装系统依赖..."
apt-get update
apt-get install -y python3-pip python3-venv python3-dev libpq-dev postgresql-client redis-tools nginx build-essential

# 4. 创建虚拟环境
log_info "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 修复setuptools问题
log_info "修复setuptools问题..."
pip install --upgrade pip
pip install --upgrade setuptools wheel

# 6. 安装Python依赖（分步安装）
log_info "安装Python依赖..."

# 先安装基础依赖
pip install django
pip install psycopg2-binary
pip install redis
pip install celery
pip install gunicorn
pip install django-cors-headers
pip install django-health-check

# 安装其他依赖
pip install pillow
pip install requests
pip install beautifulsoup4
pip install lxml
pip install openpyxl
pip install python-dotenv
pip install whitenoise

log_success "Python依赖安装完成"

# 7. 配置环境变量
log_info "配置环境变量..."
if [[ ! -f ".env" ]]; then
    cp env.production .env
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    
    DB_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
    
    REDIS_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/redis123/$REDIS_PASSWORD/" .env
    
    # 更新允许的主机
    sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin/" .env
    
    # 使用PostgreSQL数据库
    sed -i "s/DATABASE_URL=.*/DATABASE_URL=postgresql:\/\/qatoolbox:$DB_PASSWORD@localhost:5432\/qatoolbox_production/" .env
fi

log_success "环境变量配置完成"

# 8. 安装和配置PostgreSQL
log_info "安装和配置PostgreSQL..."
apt-get install -y postgresql postgresql-contrib

# 启动PostgreSQL服务
systemctl start postgresql
systemctl enable postgresql

# 创建数据库和用户
log_info "创建数据库和用户..."
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';" || log_warning "用户可能已存在"
sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;" || log_warning "数据库可能已存在"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;"

# 9. 安装和配置Redis
log_info "安装和配置Redis..."
apt-get install -y redis-server

# 配置Redis密码
sed -i "s/# requirepass foobared/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf

# 启动Redis服务
systemctl start redis-server
systemctl enable redis-server

# 10. 数据库迁移
log_info "数据库迁移..."
python manage.py migrate

# 11. 创建超级用户
log_info "创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"

# 12. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput

# 13. 创建Gunicorn配置文件
log_info "创建Gunicorn配置文件..."
cat > gunicorn.conf.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "/opt/qatoolbox/logs/gunicorn_access.log"
errorlog = "/opt/qatoolbox/logs/gunicorn_error.log"
loglevel = "info"
EOF

# 14. 创建日志目录
log_info "创建日志目录..."
mkdir -p /opt/qatoolbox/logs

# 15. 创建systemd服务文件
log_info "创建systemd服务文件..."
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis-server.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/home/admin/QAToolbox
Environment=PATH=/home/admin/QAToolbox/venv/bin
ExecStart=/home/admin/QAToolbox/venv/bin/gunicorn --config gunicorn.conf.py QAToolBox.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 16. 配置Nginx
log_info "配置Nginx..."
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 启用Nginx站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 17. 启动所有服务
log_info "启动所有服务..."
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox
systemctl restart nginx

# 18. 等待服务启动
log_info "等待服务启动..."
sleep 10

# 19. 检查服务状态
log_info "检查服务状态..."
systemctl status qatoolbox --no-pager
systemctl status postgresql --no-pager
systemctl status redis-server --no-pager
systemctl status nginx --no-pager

# 20. 健康检查
log_info "健康检查..."
for i in {1..20}; do
    if curl -f http://localhost:8000/health/ &>/dev/null; then
        log_success "应用健康检查通过"
        break
    else
        log_info "等待应用启动... ($i/20)"
        sleep 15
    fi
done

# 21. 配置防火墙
log_info "配置防火墙..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 22. 显示部署结果
log_success "=========================================="
log_success "🎉 QAToolBox 部署完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 域名地址: http://shenyiqing.xin"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 健康检查: http://47.103.143.152/health/"
echo
log_info "👤 管理员账户:"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo "  - 邮箱: admin@shenyiqing.xin"
echo
log_info "🛠️  常用管理命令:"
echo "  - 查看应用状态: systemctl status qatoolbox"
echo "  - 查看应用日志: journalctl -u qatoolbox -f"
echo "  - 重启应用: systemctl restart qatoolbox"
echo "  - 停止应用: systemctl stop qatoolbox"
echo "  - 查看数据库状态: systemctl status postgresql"
echo "  - 查看Redis状态: systemctl status redis-server"
echo "  - 查看Nginx状态: systemctl status nginx"
echo "  - 进入虚拟环境: source /home/admin/QAToolbox/venv/bin/activate"
echo
log_info "🗄️  数据库信息:"
echo "  - 数据库类型: PostgreSQL"
echo "  - 数据库名: qatoolbox_production"
echo "  - 用户名: qatoolbox"
echo "  - 密码: $DB_PASSWORD"
echo
log_info "🔧 服务配置:"
echo "  - 应用端口: 8000 (内部)"
echo "  - Web端口: 80 (外部)"
echo "  - 数据库端口: 5432"
echo "  - Redis端口: 6379"
echo
log_success "✨ 部署成功！请访问 http://47.103.143.152 查看应用"
log_success "=========================================="
