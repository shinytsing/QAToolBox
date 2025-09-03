#!/bin/bash

# QAToolBox 阿里云完整部署脚本（重新安装依赖版本）
# 用于在已有代码基础上重新安装所有依赖并完成部署

set -e

# 颜色定义
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
    log_info "以root用户运行部署脚本"
else
    log_error "请使用root用户运行此脚本"
    exit 1
fi

# 项目目录
PROJECT_DIR="/var/www/qatoolbox"
cd $PROJECT_DIR

log_info "🚀 QAToolBox 阿里云完整部署脚本（重新安装依赖）"
log_info "=================================================="

# 1. 删除现有虚拟环境并重新创建
log_info "🐍 重新创建Python虚拟环境..."
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
log_success "虚拟环境已重新创建"

# 2. 升级pip和基础工具
log_info "⬆️ 升级pip和基础工具..."
pip install --upgrade pip
pip install --upgrade setuptools wheel
log_success "pip和基础工具已升级"

# 3. 安装Python 3.12兼容的科学计算库
log_info "📦 安装Python 3.12兼容的科学计算库..."
pip install numpy==1.26.4
pip install pandas==2.1.4
pip install scipy==1.11.4
pip install scikit-learn==1.3.2
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
log_success "科学计算库安装完成"

# 4. 安装图像和音频处理库
log_info "📦 安装图像和音频处理库..."
pip install Pillow==10.1.0
pip install opencv-python==4.8.1.78
pip install librosa==0.10.1
pip install soundfile==0.12.1
pip install pydub==0.25.1
pip install pytesseract==0.3.10
pip install easyocr==1.7.0
log_success "图像和音频处理库安装完成"

# 5. 安装Django和Web框架相关
log_info "📦 安装Django和Web框架相关..."
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install django-cors-headers==4.3.1
pip install django-extensions==3.2.3
pip install django-debug-toolbar==4.2.0
log_success "Django和Web框架安装完成"

# 6. 安装数据库相关
log_info "📦 安装数据库相关..."
pip install psycopg2-binary==2.9.9
pip install redis==5.0.1
pip install django-redis==5.4.0
log_success "数据库相关库安装完成"

# 7. 安装其他依赖
log_info "📦 安装其他依赖..."
pip install celery==5.3.4
pip install gunicorn==21.2.0
pip install requests==2.31.0
pip install beautifulsoup4==4.12.2
pip install lxml==4.9.3
pip install python-dotenv==1.0.0
pip install python-dateutil==2.8.2
pip install pytz==2023.3
pip install Pillow==10.1.0
pip install reportlab==4.0.7
pip install openpyxl==3.1.2
pip install xlsxwriter==3.1.9
pip install python-magic==0.4.27
pip install chardet==5.2.0
pip install jieba==0.42.1
pip install googletrans==4.0.0rc1
pip install transformers==4.35.2
pip install torch==2.2.0
pip install torchvision==0.17.0
pip install torchaudio==2.2.0
log_success "其他依赖安装完成"

# 8. 安装requirements.txt中的剩余依赖（跳过已安装的）
log_info "📦 安装requirements.txt中的剩余依赖..."
pip install -r requirements.txt --no-deps
log_success "所有依赖安装完成"

# 9. 创建环境变量文件
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
log_success "环境变量文件已创建"

# 10. 运行数据库迁移
log_info "🗄️ 运行数据库迁移..."
python manage.py migrate --settings=config.settings.aliyun_production
log_success "数据库迁移完成"

# 11. 收集静态文件
log_info "📁 收集静态文件..."
python manage.py collectstatic --noinput --settings=config.settings.aliyun_production
log_success "静态文件收集完成"

# 12. 创建超级用户
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
log_success "超级用户配置完成"

# 13. 创建Gunicorn配置
log_info "🔧 创建Gunicorn配置..."
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
daemon = False
pidfile = "/var/www/qatoolbox/gunicorn.pid"
accesslog = "/var/www/qatoolbox/logs/gunicorn_access.log"
errorlog = "/var/www/qatoolbox/logs/gunicorn_error.log"
loglevel = "info"
user = "www-data"
group = "www-data"
EOF
log_success "Gunicorn配置已创建"

# 14. 创建Supervisor配置
log_info "🔧 创建Supervisor配置..."
tee /etc/supervisor/conf.d/qatoolbox.conf > /dev/null << EOF
[program:qatoolbox]
command=/var/www/qatoolbox/.venv/bin/gunicorn --config /var/www/qatoolbox/gunicorn.conf.py config.wsgi:application
directory=/var/www/qatoolbox
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/qatoolbox/logs/supervisor.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PATH="/var/www/qatoolbox/.venv/bin"
EOF
log_success "Supervisor配置已创建"

# 15. 创建Nginx配置
log_info "🔧 创建Nginx配置..."
tee /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin app.shenyiqing.xin;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /var/www/qatoolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
log_success "Nginx配置已创建"

# 16. 启用Nginx站点
log_info "🔧 启用Nginx站点..."
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
log_success "Nginx站点已启用"

# 17. 配置防火墙
log_info "🔒 配置防火墙..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
log_success "防火墙配置完成"

# 18. 启动服务
log_info "🚀 启动服务..."
supervisorctl reread
supervisorctl update
supervisorctl start qatoolbox
systemctl start redis-server
systemctl enable redis-server
systemctl start postgresql
systemctl enable postgresql
systemctl start nginx
systemctl enable nginx
log_success "所有服务已启动"

# 19. 创建日志轮转配置
log_info "📝 配置日志轮转..."
tee /etc/logrotate.d/qatoolbox << EOF
/var/www/qatoolbox/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        supervisorctl restart qatoolbox
    endscript
}
EOF
log_success "日志轮转配置完成"

# 20. 创建管理脚本
log_info "🔧 创建管理脚本..."
cat > manage_qatoolbox.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "启动QAToolBox服务..."
        supervisorctl start qatoolbox
        systemctl start nginx
        systemctl start postgresql
        systemctl start redis-server
        ;;
    stop)
        echo "停止QAToolBox服务..."
        supervisorctl stop qatoolbox
        systemctl stop nginx
        ;;
    restart)
        echo "重启QAToolBox服务..."
        supervisorctl restart qatoolbox
        systemctl restart nginx
        ;;
    status)
        echo "检查QAToolBox服务状态..."
        supervisorctl status qatoolbox
        systemctl status nginx --no-pager
        systemctl status postgresql --no-pager
        systemctl status redis-server --no-pager
        ;;
    logs)
        echo "查看QAToolBox日志..."
        tail -f /var/www/qatoolbox/logs/gunicorn_error.log
        ;;
    update)
        echo "更新QAToolBox..."
        cd /var/www/qatoolbox
        source .venv/bin/activate
        git pull origin main
        python manage.py migrate --settings=config.settings.aliyun_production
        python manage.py collectstatic --noinput --settings=config.settings.aliyun_production
        supervisorctl restart qatoolbox
        ;;
    reinstall)
        echo "重新安装依赖..."
        cd /var/www/qatoolbox
        source .venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        supervisorctl restart qatoolbox
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|update|reinstall}"
        exit 1
        ;;
esac
EOF
chmod +x manage_qatoolbox.sh
log_success "管理脚本已创建"

# 21. 创建定时任务
log_info "⏰ 配置定时任务..."
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/qatoolbox/manage_qatoolbox.sh update") | crontab -
log_success "定时任务已配置"

# 22. 检查服务状态
log_info "🔍 检查服务状态..."
echo "=== Supervisor状态 ==="
supervisorctl status
echo ""
echo "=== 系统服务状态 ==="
systemctl status nginx --no-pager -l
echo ""
systemctl status postgresql --no-pager -l
echo ""
systemctl status redis-server --no-pager -l
echo ""
echo "=== 端口监听状态 ==="
netstat -tlnp | grep -E ':(80|8000|5432|6379)'

# 23. 测试应用
log_info "🧪 测试应用..."
sleep 5
echo "测试健康检查端点..."
curl -s http://localhost/health/ || log_warning "健康检查端点测试失败"
echo ""
echo "测试主页..."
curl -s -I http://localhost/ | head -5

# 24. 显示部署信息
log_success "🎉 QAToolBox部署完成！"
echo ""
echo "=================================="
echo "📋 部署信息"
echo "=================================="
echo "🌐 访问地址: http://47.103.143.152"
echo "🌐 域名: http://shenyiqing.xin"
echo "👤 管理员账号: admin"
echo "🔑 管理员密码: admin123456"
echo "📁 项目目录: /var/www/qatoolbox"
echo "📝 日志目录: /var/www/qatoolbox/logs"
echo "🔧 管理脚本: /var/www/qatoolbox/manage_qatoolbox.sh"
echo ""
echo "=================================="
echo "🛠️ 常用命令"
echo "=================================="
echo "启动服务: ./manage_qatoolbox.sh start"
echo "停止服务: ./manage_qatoolbox.sh stop"
echo "重启服务: ./manage_qatoolbox.sh restart"
echo "查看状态: ./manage_qatoolbox.sh status"
echo "查看日志: ./manage_qatoolbox.sh logs"
echo "更新应用: ./manage_qatoolbox.sh update"
echo "重新安装依赖: ./manage_qatoolbox.sh reinstall"
echo ""
echo "=================================="
echo "📊 服务状态"
echo "=================================="
supervisorctl status qatoolbox
echo ""
log_success "部署完成！请访问 http://47.103.143.152 测试应用"
