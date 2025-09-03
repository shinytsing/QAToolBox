#!/bin/bash

# 阿里云Ubuntu一键部署脚本
# 适用于华东2(上海)区域，中国区环境优化

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   log_error "请不要使用root用户运行此脚本"
   exit 1
fi

log_info "🚀 开始部署QAToolBox到阿里云Ubuntu服务器..."

# 1. 更新系统包
log_info "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装基础依赖
log_info "🔧 安装基础依赖..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    build-essential \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git \
    curl \
    wget \
    unzip \
    supervisor \
    htop \
    vim \
    ufw \
    certbot \
    python3-certbot-nginx

# 3. 配置中国区pip源
log_info "🇨🇳 配置中国区pip源..."
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
EOF

# 4. 配置PostgreSQL
log_info "🗄️ 配置PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql << EOF
-- 创建数据库
CREATE DATABASE qatoolbox_production;
CREATE DATABASE qatoolbox_test;

-- 创建用户
CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;
GRANT ALL PRIVILEGES ON DATABASE qatoolbox_test TO qatoolbox;

-- 连接到数据库并授权schema
\c qatoolbox_production;
GRANT ALL ON SCHEMA public TO qatoolbox;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO qatoolbox;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO qatoolbox;

\c qatoolbox_test;
GRANT ALL ON SCHEMA public TO qatoolbox;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO qatoolbox;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO qatoolbox;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO qatoolbox;

\q
EOF

# 配置PostgreSQL允许本地连接
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
sudo systemctl restart postgresql

# 5. 配置Redis
log_info "🔴 配置Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 配置Redis密码
sudo sed -i 's/# requirepass foobared/requirepass redis123/' /etc/redis/redis.conf
sudo systemctl restart redis-server

# 6. 创建项目目录
log_info "📁 创建项目目录..."
sudo mkdir -p /var/www/qatoolbox
sudo chown $USER:$USER /var/www/qatoolbox
cd /var/www/qatoolbox

# 7. 创建虚拟环境
log_info "🐍 创建Python虚拟环境..."
python3 -m venv .venv
source .venv/bin/activate

# 8. 升级pip
log_info "⬆️ 升级pip..."
pip install --upgrade pip

# 9. 安装Python依赖
log_info "📦 安装完整Python依赖..."
pip install -r requirements.txt

# 安装系统级依赖（如果需要）
log_info "📦 安装系统级依赖..."
sudo apt install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    libtesseract-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    ffmpeg \
    libsndfile1

# 10. 创建环境变量文件
log_info "⚙️ 创建环境变量配置..."
cat > .env << EOF
# 数据库配置
DB_NAME=qatoolbox_production
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://:redis123@localhost:6379/0

# Django配置
DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,app.shenyiqing.xin

# 邮件配置
EMAIL_HOST=smtp.aliyun.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# Celery配置
CELERY_BROKER_URL=redis://:redis123@localhost:6379/1
CELERY_RESULT_BACKEND=redis://:redis123@localhost:6379/1

# 安全配置
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
EOF

# 11. 运行数据库迁移
log_info "🗄️ 运行数据库迁移..."
python manage.py migrate --settings=config.settings.aliyun_production

# 12. 收集静态文件
log_info "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.aliyun_production

# 13. 创建超级用户
log_info "👤 创建超级用户..."
python manage.py shell --settings=config.settings.aliyun_production -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户已创建: admin/admin123456')
else:
    print('超级用户已存在')
"

# 14. 创建Gunicorn配置
log_info "⚙️ 创建Gunicorn配置..."
cat > gunicorn.conf.py << EOF
# Gunicorn配置文件
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn/qatoolbox.pid"
user = "$USER"
group = "$USER"
tmp_upload_dir = None
errorlog = "/var/log/qatoolbox/gunicorn_error.log"
accesslog = "/var/log/qatoolbox/gunicorn_access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
EOF

# 15. 创建Supervisor配置
log_info "👨‍💼 创建Supervisor配置..."
sudo mkdir -p /var/log/qatoolbox
sudo chown $USER:$USER /var/log/qatoolbox

sudo tee /etc/supervisor/conf.d/qatoolbox.conf > /dev/null << EOF
[program:qatoolbox]
command=/var/www/qatoolbox/.venv/bin/gunicorn --config /var/www/qatoolbox/gunicorn.conf.py QAToolBox.wsgi:application
directory=/var/www/qatoolbox
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/supervisor.log
environment=DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
EOF

# 16. 创建Nginx配置
log_info "🌐 创建Nginx配置..."
sudo tee /etc/nginx/sites-available/qatoolbox > /dev/null << EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin app.shenyiqing.xin 47.103.143.152;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 客户端最大上传大小
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /var/www/qatoolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF

# 17. 启用Nginx站点
sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t

# 18. 配置防火墙
log_info "🔥 配置防火墙..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# 19. 启动服务
log_info "🚀 启动服务..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start qatoolbox
sudo systemctl restart nginx
sudo systemctl enable nginx

# 20. 创建日志轮转配置
log_info "📝 配置日志轮转..."
sudo tee /etc/logrotate.d/qatoolbox > /dev/null << EOF
/var/log/qatoolbox/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        sudo supervisorctl restart qatoolbox
    endscript
}
EOF

# 21. 创建管理脚本
log_info "📜 创建管理脚本..."
cat > manage_qatoolbox.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        sudo supervisorctl start qatoolbox
        sudo systemctl start nginx
        echo "QAToolBox started"
        ;;
    stop)
        sudo supervisorctl stop qatoolbox
        sudo systemctl stop nginx
        echo "QAToolBox stopped"
        ;;
    restart)
        sudo supervisorctl restart qatoolbox
        sudo systemctl restart nginx
        echo "QAToolBox restarted"
        ;;
    status)
        sudo supervisorctl status qatoolbox
        sudo systemctl status nginx --no-pager
        ;;
    logs)
        sudo tail -f /var/log/qatoolbox/supervisor.log
        ;;
    update)
        cd /var/www/qatoolbox
        source .venv/bin/activate
        git pull
        pip install -r requirements.txt
        python manage.py migrate --settings=config.settings.aliyun_production
        python manage.py collectstatic --noinput --settings=config.settings.aliyun_production
        sudo supervisorctl restart qatoolbox
        echo "QAToolBox updated"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|update}"
        exit 1
        ;;
esac
EOF

chmod +x manage_qatoolbox.sh

# 22. 创建定时任务
log_info "⏰ 创建定时任务..."
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/qatoolbox/manage_qatoolbox.sh update") | crontab -

# 23. 检查服务状态
log_info "📊 检查服务状态..."
sleep 5
sudo supervisorctl status qatoolbox
sudo systemctl status nginx --no-pager

# 24. 测试应用
log_info "🧪 测试应用..."
curl -I http://localhost/health/ || log_warning "健康检查失败，请检查应用状态"

# 25. 显示部署信息
log_success "✅ 部署完成！"
echo ""
echo "🌐 访问信息:"
echo "  - 本地访问: http://localhost"
echo "  - 外网访问: http://47.103.143.152"
echo "  - 域名访问: http://shenyiqing.xin"
echo ""
echo "👤 管理员账户:"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo ""
echo "🔧 管理命令:"
echo "  - 启动: ./manage_qatoolbox.sh start"
echo "  - 停止: ./manage_qatoolbox.sh stop"
echo "  - 重启: ./manage_qatoolbox.sh restart"
echo "  - 状态: ./manage_qatoolbox.sh status"
echo "  - 日志: ./manage_qatoolbox.sh logs"
echo "  - 更新: ./manage_qatoolbox.sh update"
echo ""
echo "📊 服务状态:"
echo "  - PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "  - Redis: $(sudo systemctl is-active redis-server)"
echo "  - Nginx: $(sudo systemctl is-active nginx)"
echo "  - QAToolBox: $(sudo supervisorctl status qatoolbox | awk '{print $2}')"
echo ""
echo "📁 重要目录:"
echo "  - 项目目录: /var/www/qatoolbox"
echo "  - 日志目录: /var/log/qatoolbox"
echo "  - 配置文件: /etc/nginx/sites-available/qatoolbox"
echo "  - Supervisor配置: /etc/supervisor/conf.d/qatoolbox.conf"
echo ""
log_warning "⚠️ 请记得:"
echo "  1. 配置SSL证书: sudo certbot --nginx -d shenyiqing.xin -d www.shenyiqing.xin"
echo "  2. 修改默认密码"
echo "  3. 配置邮件服务"
echo "  4. 定期备份数据库"
