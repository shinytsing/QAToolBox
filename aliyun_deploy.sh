#!/bin/bash

# QAToolBox 阿里云一键部署脚本
# 使用方法: curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/aliyun_deploy.sh | bash

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   print_error "请不要使用root用户运行此脚本"
   exit 1
fi

print_info "=== QAToolBox 阿里云一键部署开始 ==="
print_info "服务器IP: 47.103.143.152"
print_info "域名: shenyiqing.xin"
echo ""

# 1. 更新系统
print_step "1/15 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装基础软件
print_step "2/15 安装基础软件..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# 3. 安装Docker
print_step "3/15 安装Docker..."
if ! command -v docker &> /dev/null; then
    # 添加Docker官方GPG密钥
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # 添加Docker仓库
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 更新包列表并安装Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # 将用户添加到docker组
    sudo usermod -aG docker $USER
    
    # 启动Docker服务
    sudo systemctl enable docker
    sudo systemctl start docker
    
    print_info "Docker安装完成"
else
    print_info "Docker已安装"
fi

# 4. 安装Docker Compose
print_step "4/15 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_info "Docker Compose安装完成"
else
    print_info "Docker Compose已安装"
fi

# 5. 安装Nginx
print_step "5/15 安装Nginx..."
sudo apt install -y nginx

# 6. 安装Certbot (SSL证书)
print_step "6/15 安装Certbot..."
sudo apt install -y certbot python3-certbot-nginx

# 7. 配置防火墙
print_step "7/15 配置防火墙..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 8. 克隆项目
print_step "8/15 克隆QAToolBox项目..."
cd /home/$USER
if [ -d "QAToolbox" ]; then
    print_warning "项目目录已存在，正在更新..."
    cd QAToolbox
    git pull origin main
else
    git clone https://github.com/shinytsing/QAToolbox.git
    cd QAToolbox
fi

# 9. 创建环境变量文件
print_step "9/15 创建环境变量文件..."
cat > .env << EOF
# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$(openssl rand -base64 32)
DB_HOST=db
DB_PORT=5432

# Redis配置
REDIS_URL=redis://redis:6379/0

# Django配置
DJANGO_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False

# 域名配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# SSL配置
SECURE_SSL_REDIRECT=False

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@shenyiqing.xin
ADMIN_PASSWORD=admin123456
EOF

print_info "环境变量文件创建完成"

# 10. 创建生产环境Docker Compose文件
print_step "10/15 创建生产环境配置..."
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # 数据库
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Web应用
  web:
    build:
      context: .
      dockerfile: Dockerfile.prod
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Celery Worker
  celery:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A QAToolBox worker -l info --concurrency=2
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Celery Beat (定时任务)
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.prod
    command: celery -A QAToolBox beat -l info
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Nginx
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot
    restart: unless-stopped
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
EOF

# 11. 创建生产环境Dockerfile
print_step "11/15 创建生产环境Dockerfile..."
cat > Dockerfile.prod << 'EOF'
# 多阶段构建
FROM python:3.11-slim as builder

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制requirements文件
COPY requirements/ /app/requirements/

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/production.txt

# 生产阶段
FROM python:3.11-slim as production

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd --create-home --shell /bin/bash qatoolbox

# 设置工作目录
WORKDIR /app

# 从builder阶段复制Python包
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY . /app/

# 创建必要的目录
RUN mkdir -p /app/logs /app/media /app/staticfiles

# 设置权限
RUN chown -R qatoolbox:qatoolbox /app

# 切换到非root用户
USER qatoolbox

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/tools/health/ || exit 1

# 启动脚本
COPY --chown=qatoolbox:qatoolbox start_prod.sh /app/start_prod.sh
RUN chmod +x /app/start_prod.sh

CMD ["/app/start_prod.sh"]
EOF

# 12. 创建启动脚本
print_step "12/15 创建启动脚本..."
cat > start_prod.sh << 'EOF'
#!/bin/bash

set -e

echo "等待数据库连接..."
while ! nc -z db 5432; do
  sleep 1
done
echo "数据库已连接"

echo "等待Redis连接..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis已连接"

echo "运行数据库迁移..."
python manage.py migrate --noinput

echo "收集静态文件..."
python manage.py collectstatic --noinput --clear

echo "创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@shenyiqing.xin')
password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'超级用户创建成功: {username}/{password}')
else:
    print('超级用户已存在')
"

echo "启动Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 5 \
    --access-logfile /app/logs/access.log \
    --error-logfile /app/logs/error.log \
    --log-level info \
    config.wsgi:application
EOF

chmod +x start_prod.sh

# 13. 创建Nginx配置
print_step "13/15 创建Nginx配置..."
mkdir -p nginx

cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # 基本设置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # 客户端设置
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    client_header_buffer_size 3m;
    large_client_header_buffers 4 256k;

    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # 上游服务器
    upstream django {
        server web:8000;
        keepalive 32;
    }

    # HTTP服务器 (重定向到HTTPS或直接服务)
    server {
        listen 80;
        server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;

        # Let's Encrypt验证路径
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        # 静态文件
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # 媒体文件
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # 健康检查
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # 主应用
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }
    }

    # HTTPS服务器 (SSL证书配置后启用)
    server {
        listen 443 ssl http2;
        server_name shenyiqing.xin www.shenyiqing.xin;

        # SSL证书路径 (获取证书后取消注释)
        # ssl_certificate /etc/letsencrypt/live/shenyiqing.xin/fullchain.pem;
        # ssl_certificate_key /etc/letsencrypt/live/shenyiqing.xin/privkey.pem;

        # SSL安全配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

        # 静态文件
        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # 媒体文件
        location /media/ {
            alias /app/media/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }

        # 健康检查
        location /health/ {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # 主应用
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }
    }
}
EOF

# 14. 创建管理脚本
print_step "14/15 创建管理脚本..."
cat > manage_service.sh << 'EOF'
#!/bin/bash

# QAToolBox服务管理脚本

PROJECT_DIR="/home/$USER/QAToolbox"
COMPOSE_FILE="docker-compose.prod.yml"

cd $PROJECT_DIR

case "$1" in
    start)
        echo "启动QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE up -d
        echo "服务启动完成"
        ;;
    stop)
        echo "停止QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE down
        echo "服务停止完成"
        ;;
    restart)
        echo "重启QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d
        echo "服务重启完成"
        ;;
    logs)
        echo "查看服务日志..."
        docker-compose -f $COMPOSE_FILE logs -f --tail=100
        ;;
    status)
        echo "服务状态..."
        docker-compose -f $COMPOSE_FILE ps
        ;;
    update)
        echo "更新服务..."
        git pull origin main
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d
        echo "服务更新完成"
        ;;
    backup)
        echo "备份数据库..."
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U qatoolbox qatoolbox > $BACKUP_FILE
        echo "数据库备份完成: $BACKUP_FILE"
        ;;
    ssl)
        echo "配置SSL证书..."
        sudo certbot certonly --webroot -w /var/www/certbot -d shenyiqing.xin -d www.shenyiqing.xin --non-interactive --agree-tos --email admin@shenyiqing.xin
        echo "SSL证书配置完成，请重启Nginx服务"
        ;;
    *)
        echo "QAToolBox服务管理"
        echo "使用方法: $0 {start|stop|restart|logs|status|update|backup|ssl}"
        echo ""
        echo "命令说明:"
        echo "  start   - 启动所有服务"
        echo "  stop    - 停止所有服务"
        echo "  restart - 重启所有服务"
        echo "  logs    - 查看服务日志"
        echo "  status  - 查看服务状态"
        echo "  update  - 更新代码并重启服务"
        echo "  backup  - 备份数据库"
        echo "  ssl     - 配置SSL证书"
        exit 1
        ;;
esac
EOF

chmod +x manage_service.sh

# 15. 创建日志目录
mkdir -p logs

# 16. 构建和启动服务
print_step "15/15 构建和启动服务..."
newgrp docker << EONG
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
EONG

# 17. 等待服务启动
print_info "等待服务启动..."
sleep 45

# 18. 检查服务状态
print_info "检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

# 19. 创建系统服务
print_info "创建系统服务..."
sudo tee /etc/systemd/system/qatoolbox.service > /dev/null << EOF
[Unit]
Description=QAToolBox Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/$USER/QAToolbox
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0
User=$USER

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable qatoolbox.service

echo ""
print_info "=== 部署完成！ ==="
echo ""
print_info "🎉 QAToolBox已成功部署到阿里云！"
echo ""
print_info "📍 访问地址："
print_info "   - HTTP: http://47.103.143.152"
print_info "   - HTTP: http://shenyiqing.xin"
print_info "   - 管理后台: http://shenyiqing.xin/admin/"
echo ""
print_info "👤 默认管理员账户："
print_info "   - 用户名: admin"
print_info "   - 密码: admin123456"
echo ""
print_info "🛠️ 服务管理命令："
print_info "   ./manage_service.sh start    - 启动服务"
print_info "   ./manage_service.sh stop     - 停止服务"
print_info "   ./manage_service.sh restart  - 重启服务"
print_info "   ./manage_service.sh logs     - 查看日志"
print_info "   ./manage_service.sh status   - 查看状态"
print_info "   ./manage_service.sh update   - 更新服务"
print_info "   ./manage_service.sh backup   - 备份数据"
print_info "   ./manage_service.sh ssl      - 配置SSL"
echo ""
print_info "🔒 配置HTTPS (可选)："
print_info "   1. 运行: ./manage_service.sh ssl"
print_info "   2. 修改nginx配置启用SSL"
print_info "   3. 重启服务: ./manage_service.sh restart"
echo ""
print_info "📝 重要提醒："
print_info "   - 请及时修改默认管理员密码"
print_info "   - 定期备份数据库"
print_info "   - 监控服务日志"
echo ""
print_warning "如遇问题，请查看日志: ./manage_service.sh logs"
