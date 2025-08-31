#!/bin/bash
# QAToolBox Docker 一键部署脚本 - 超级简单版
# 适用于阿里云 Ubuntu 服务器

echo "🚀 QAToolBox Docker 一键部署开始..."

# 安装 Docker
echo "📦 安装 Docker..."
curl -fsSL https://get.docker.com | bash
systemctl start docker
systemctl enable docker

# 创建项目目录
mkdir -p /opt/qatoolbox
cd /opt/qatoolbox

# 创建 Docker Compose 文件
echo "📝 创建 Docker 配置..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: qatoolbox
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: qatoolbox123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  web:
    image: python:3.12-slim
    command: >
      bash -c "
        apt-get update && 
        apt-get install -y git build-essential libpq-dev && 
        pip install Django gunicorn psycopg2-binary redis python-dotenv && 
        git clone https://github.com/shinytsing/QAToolbox.git /app || true &&
        cd /app && 
        echo 'DEBUG=False
ALLOWED_HOSTS=*
DB_NAME=qatoolbox
DB_USER=qatoolbox  
DB_PASSWORD=qatoolbox123
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
SECRET_KEY=docker-secret-key-123456' > .env &&
        python manage.py migrate --noinput &&
        python manage.py collectstatic --noinput &&
        echo \"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None\" | python manage.py shell &&
        gunicorn --bind 0.0.0.0:8000 --workers 2 wsgi:application
      "
    ports:
      - "80:8000"
    depends_on:
      - db
      - redis
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.base

volumes:
  postgres_data:
EOF

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查状态
echo "✅ 检查服务状态..."
docker-compose ps

echo "🎉 部署完成！"
echo "访问地址: http://$(curl -s ifconfig.me)"
echo "管理后台: http://$(curl -s ifconfig.me)/admin/"
echo "用户名: admin"
echo "密码: admin123"
echo ""
echo "管理命令:"
echo "查看日志: docker-compose logs -f"
echo "重启服务: docker-compose restart"
echo "停止服务: docker-compose down"
