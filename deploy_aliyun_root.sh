#!/bin/bash

# QAToolBox 阿里云Root用户部署脚本
# 服务器: 47.103.143.152 (shenyiqing.xin)
# 系统: CentOS

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
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

print_info "=== QAToolBox 阿里云Root用户部署开始 ==="
print_info "服务器IP: 47.103.143.152"
print_info "域名: shenyiqing.xin"
print_info "当前用户: $(whoami)"
echo ""

# 1. 检查系统和更新
print_step "1/13 检查系统并更新..."
if command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
else
    print_error "不支持的系统，需要CentOS/RHEL系统"
    exit 1
fi

print_info "使用包管理器: $PKG_MANAGER"

# 检查CentOS 8源问题
if [ -f /etc/centos-release ] && grep -q "CentOS Linux release 8" /etc/centos-release; then
    print_warning "检测到CentOS 8，修复源配置..."
    sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
    sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
fi

$PKG_MANAGER clean all
$PKG_MANAGER update -y

# 2. 安装基础软件
print_step "2/13 安装基础软件..."
$PKG_MANAGER install -y curl wget git unzip vim htop

# 3. 创建部署用户
print_step "3/13 创建部署用户..."
if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
    print_info "用户qatoolbox已创建"
else
    print_info "用户qatoolbox已存在"
fi

# 设置用户密码
echo "qatoolbox:qatoolbox123" | chpasswd
print_info "qatoolbox用户密码已设置为: qatoolbox123"

# 4. 安装Docker
print_step "4/13 安装Docker..."
if ! command -v docker &> /dev/null; then
    $PKG_MANAGER install -y yum-utils device-mapper-persistent-data lvm2
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    $PKG_MANAGER install -y docker-ce docker-ce-cli containerd.io
    
    systemctl start docker
    systemctl enable docker
    usermod -aG docker qatoolbox
    
    print_info "Docker安装完成"
else
    print_info "Docker已安装"
fi

# 5. 安装Docker Compose
print_step "5/13 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    print_info "Docker Compose安装完成"
else
    print_info "Docker Compose已安装"
fi

# 6. 配置防火墙
print_step "6/13 配置防火墙..."
if command -v firewall-cmd &> /dev/null; then
    systemctl start firewalld
    systemctl enable firewalld
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-port=8000/tcp
    firewall-cmd --reload
    print_info "防火墙配置完成"
fi

# 7. 创建项目目录
print_step "7/13 创建项目目录..."
PROJECT_DIR="/opt/QAToolbox"
mkdir -p $PROJECT_DIR
chown -R qatoolbox:qatoolbox $PROJECT_DIR

# 8. 克隆或更新项目
print_step "8/13 获取项目代码..."
if [ -d "$PROJECT_DIR/.git" ]; then
    print_warning "项目目录已存在，正在更新..."
    cd $PROJECT_DIR
    sudo -u qatoolbox git pull origin main
else
    cd /opt
    sudo -u qatoolbox git clone https://github.com/shinytsing/QAToolbox.git
    chown -R qatoolbox:qatoolbox $PROJECT_DIR
fi

cd $PROJECT_DIR

# 9. 创建环境变量文件
print_step "9/13 创建环境变量文件..."

# 生成随机密钥
DJANGO_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || openssl rand -base64 50)
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

cat > .env << EOF
# Django配置
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=${DB_PASS}
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://\${DB_USER}:\${DB_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME}

# Redis配置
REDIS_URL=redis://redis:6379/0

# 第三方API配置（可选，根据需要填写）
DEEPSEEK_API_KEY=
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
OPENWEATHER_API_KEY=

# 社交媒体API配置（可选）
XIAOHONGSHU_API_KEY=
DOUYIN_API_KEY=
NETEASE_API_KEY=
WEIBO_API_KEY=
BILIBILI_API_KEY=
ZHIHU_API_KEY=

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@shenyiqing.xin
ADMIN_PASSWORD=admin123456

# 文件上传配置
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
MAX_UPLOAD_SIZE=104857600

# 缓存配置
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379/1

# Celery配置
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# API限制配置
API_RATE_LIMIT_ANON=1000
API_RATE_LIMIT_USER=10000

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_PROXY_SSL_HEADER=

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# CORS配置
CORS_ALLOWED_ORIGINS=http://shenyiqing.xin,https://shenyiqing.xin,http://www.shenyiqing.xin,https://www.shenyiqing.xin,http://47.103.143.152
CORS_ALLOW_CREDENTIALS=True
EOF

chown qatoolbox:qatoolbox .env
print_info "环境变量文件创建完成"
print_info "数据库密码: ${DB_PASS}"

# 10. 创建简化的Docker Compose文件
print_step "10/13 创建Docker Compose配置..."
cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: qatoolbox_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: qatoolbox_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Web应用
  web:
    build: .
    container_name: qatoolbox_web
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/tools/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  # Celery Worker
  celery:
    build: .
    container_name: qatoolbox_celery
    restart: unless-stopped
    command: celery -A QAToolBox worker -l info --concurrency=2
    env_file:
      - .env
    volumes:
      - media_volume:/app/media
      - ./logs:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: qatoolbox_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /var/www/certbot:/var/www/certbot
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
EOF

chown qatoolbox:qatoolbox docker-compose.simple.yml

# 11. 创建Nginx配置
print_step "11/13 创建Nginx配置..."
mkdir -p nginx

cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100M;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location /static/ {
            alias /app/staticfiles/;
            expires 1y;
        }

        location /media/ {
            alias /app/media/;
            expires 1y;
        }

        location /health/ {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

chown -R qatoolbox:qatoolbox nginx/

# 12. 创建管理脚本
print_step "12/13 创建管理脚本..."
cat > manage_service.sh << 'EOF'
#!/bin/bash

PROJECT_DIR="/opt/QAToolbox"
COMPOSE_FILE="docker-compose.simple.yml"

cd $PROJECT_DIR

case "$1" in
    start)
        echo "启动QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    stop)
        echo "停止QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE down
        ;;
    restart)
        echo "重启QAToolBox服务..."
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    logs)
        docker-compose -f $COMPOSE_FILE logs -f --tail=100
        ;;
    status)
        docker-compose -f $COMPOSE_FILE ps
        ;;
    update)
        git pull origin main
        docker-compose -f $COMPOSE_FILE build --no-cache
        docker-compose -f $COMPOSE_FILE down
        docker-compose -f $COMPOSE_FILE up -d
        ;;
    backup)
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U qatoolbox qatoolbox > $BACKUP_FILE
        echo "数据库备份完成: $BACKUP_FILE"
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|logs|status|update|backup}"
        ;;
esac
EOF

chmod +x manage_service.sh
chown qatoolbox:qatoolbox manage_service.sh

# 创建日志目录
mkdir -p logs
chown -R qatoolbox:qatoolbox logs

# 13. 构建并启动服务
print_step "13/13 构建并启动服务..."

# 构建镜像
docker-compose -f docker-compose.simple.yml build

# 启动服务
docker-compose -f docker-compose.simple.yml up -d

# 等待服务启动
print_info "等待服务启动..."
sleep 30

# 检查服务状态
docker-compose -f docker-compose.simple.yml ps

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
print_info "👤 系统用户账户："
print_info "   - 用户名: qatoolbox"
print_info "   - 密码: qatoolbox123"
echo ""
print_info "👤 Django管理员账户："
print_info "   - 用户名: admin"
print_info "   - 密码: admin123456"
echo ""
print_info "🗄️ 数据库信息："
print_info "   - 数据库名: qatoolbox"
print_info "   - 用户名: qatoolbox"
print_info "   - 密码: ${DB_PASS}"
echo ""
print_info "🛠️ 服务管理命令："
print_info "   cd /opt/QAToolbox"
print_info "   ./manage_service.sh start    - 启动服务"
print_info "   ./manage_service.sh stop     - 停止服务"
print_info "   ./manage_service.sh restart  - 重启服务"
print_info "   ./manage_service.sh logs     - 查看日志"
print_info "   ./manage_service.sh status   - 查看状态"
print_info "   ./manage_service.sh update   - 更新服务"
print_info "   ./manage_service.sh backup   - 备份数据"
echo ""
print_warning "重要提醒："
print_warning "1. 系统用户qatoolbox密码: qatoolbox123"
print_warning "2. 请及时修改默认管理员密码"
print_warning "3. 建议配置SSL证书"
print_warning "4. 定期备份数据库"
