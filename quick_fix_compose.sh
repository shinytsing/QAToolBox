#!/bin/bash
# =============================================================================
# 快速修复docker-compose.yml语法错误
# =============================================================================

set -e

echo "🔧 修复docker-compose.yml语法错误..."

cd /home/qatoolbox/QAToolBox

# 创建正确的docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: QAToolBox2024
      POSTGRES_HOST_AUTH_METHOD: trust
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qatoolbox"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis缓存
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # QAToolBox主应用
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    restart: unless-stopped
    command: >
      sh -c "
        echo '等待数据库启动...' &&
        sleep 15 &&
        python manage.py migrate --noinput &&
        python manage.py collectstatic --noinput &&
        python manage.py shell -c \"
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456');
    print('管理员用户创建完成');
else:
    print('管理员用户已存在');
        \" &&
        echo '启动Gunicorn服务器...' &&
        gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60 --log-level info
      "
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DJANGO_SECRET_KEY=django-docker-secret-key-12345
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=QAToolBox2024
      - DB_HOST=db
      - DB_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1,web
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - qatoolbox_network

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  static_volume:
    driver: local
  media_volume:
    driver: local

networks:
  qatoolbox_network:
    driver: bridge
EOF

echo "✅ docker-compose.yml修复完成"

# 验证YAML语法
echo "🧪 验证YAML语法..."
docker compose config

echo "🔨 开始构建Docker镜像..."
docker compose build --no-cache

echo "🚀 启动容器..."
docker compose up -d

echo "📊 查看容器状态..."
sleep 10
docker compose ps

echo "✅ 修复完成！"
EOF

chmod +x quick_fix_compose.sh
