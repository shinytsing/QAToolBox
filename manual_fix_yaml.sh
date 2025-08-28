#!/bin/bash
# =============================================================================
# 手动修复YAML语法错误 - 逐行检查版本
# =============================================================================

echo "🔧 手动修复YAML语法错误..."

cd /home/qatoolbox/QAToolBox

# 完全重写docker-compose.yml，确保语法正确
cat > docker-compose.yml << 'YAML_END'
version: '3.8'

services:
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

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network

  web:
    build: .
    restart: unless-stopped
    command: |
      sh -c "
        echo '等待数据库启动...'
        sleep 15
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        python manage.py shell -c \"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('管理员用户创建完成')
        \"
        gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 3
      "
    environment:
      - DEBUG=False
      - DJANGO_SETTINGS_MODULE=config.settings.docker_production
      - DB_NAME=qatoolbox
      - DB_USER=qatoolbox
      - DB_PASSWORD=QAToolBox2024
      - DB_HOST=db
      - REDIS_URL=redis://redis:6379/0
      - ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
    volumes:
      - .:/app
      - static_volume:/app/static
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    networks:
      - qatoolbox_network

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

networks:
  qatoolbox_network:
YAML_END

echo "✅ 新的docker-compose.yml已创建"

# 显示文件内容行号以便调试
echo "📋 检查文件内容（显示行号）:"
cat -n docker-compose.yml | head -60

echo ""
echo "🧪 验证YAML语法..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ YAML语法验证通过"
else
    echo "❌ YAML语法仍有问题，显示详细错误:"
    docker compose config
fi

echo ""
echo "🔨 尝试构建Docker镜像..."
docker compose build --no-cache

echo ""
echo "🚀 启动容器..."
docker compose up -d

echo ""
echo "📊 查看容器状态..."
sleep 10
docker compose ps

echo ""
echo "📋 查看Web容器日志..."
docker compose logs web --tail=20
YAML_END

chmod +x manual_fix_yaml.sh
