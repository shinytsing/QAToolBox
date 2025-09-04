#!/bin/bash

# QAToolBox 阿里云一键部署脚本
# 使用方法: ./deploy.sh

set -e

echo "🚀 开始部署 QAToolBox 到阿里云..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env.production ]; then
    echo "❌ 未找到 .env.production 文件，请先配置环境变量"
    exit 1
fi

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 清理旧镜像
echo "🧹 清理旧镜像..."
docker system prune -f

# 构建新镜像
echo "🔨 构建新镜像..."
docker-compose build --no-cache

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 运行数据库迁移
echo "📊 运行数据库迁移..."
docker-compose exec web python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec web python manage.py collectstatic --noinput

# 创建超级用户（如果不存在）
echo "👤 创建超级用户..."
docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

# 检查健康状态
echo "🏥 检查健康状态..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ 部署成功！"
    echo "🌐 访问地址: http://47.103.143.152"
    echo "🌐 域名访问: http://shenyiqing.xin"
    echo "👤 管理员账号: admin / admin123"
else
    echo "❌ 健康检查失败，请检查日志"
    docker-compose logs web
    exit 1
fi

echo "🎉 部署完成！"
