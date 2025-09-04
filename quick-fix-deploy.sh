#!/bin/bash

# QAToolBox 快速修复部署脚本
# 在阿里云服务器上执行此脚本修复部署问题

set -e

echo "🚀 QAToolBox 快速修复部署"
echo "=========================="

# 检查是否在阿里云服务器上
if [ ! -f /etc/aliyun-release ]; then
    echo "⚠️  警告: 此脚本建议在阿里云服务器上运行"
fi

# 停止现有服务
echo "🛑 停止现有服务..."
docker-compose down --remove-orphans || true

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 执行修复脚本
echo "🔧 执行修复脚本..."
chmod +x fix_deployment_issues.sh
./fix_deployment_issues.sh

# 重新构建和启动服务
echo "🔨 重新构建服务..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 运行数据库迁移
echo "📊 运行数据库迁移..."
docker-compose exec web python manage.py migrate

# 收集静态文件
echo "📁 收集静态文件..."
docker-compose exec web python manage.py collectstatic --noinput

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查健康状态..."
sleep 10
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ 修复部署成功！"
    echo "🌐 访问地址: http://47.103.143.152"
    echo "🌐 域名访问: http://shenyiqing.xin"
    echo "🔒 HTTPS访问: https://shenyiqing.xin"
    echo "👤 管理员账号: admin / admin123"
else
    echo "❌ 健康检查失败，请检查日志"
    docker-compose logs web
    exit 1
fi

echo "🎉 修复部署完成！"
echo "📋 管理命令:"
echo "  - 查看状态: ./monitor.sh"
echo "  - 备份数据: ./backup.sh"
echo "  - 查看日志: docker-compose logs -f web"
echo "  - 重启服务: docker-compose restart"
