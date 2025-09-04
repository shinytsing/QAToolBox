#!/bin/bash

# QAToolBox 监控脚本
# 使用方法: ./monitor.sh

echo "🔍 QAToolBox 服务监控"
echo "========================"

# 检查Docker服务状态
echo "📊 Docker 服务状态:"
docker-compose ps

echo ""

# 检查容器资源使用情况
echo "💻 容器资源使用情况:"
docker stats --no-stream

echo ""

# 检查磁盘使用情况
echo "💾 磁盘使用情况:"
df -h

echo ""

# 检查内存使用情况
echo "🧠 内存使用情况:"
free -h

echo ""

# 检查网络连接
echo "🌐 网络连接状态:"
netstat -tlnp | grep -E ':(80|443|8000|5432|6379)'

echo ""

# 检查应用健康状态
echo "🏥 应用健康检查:"
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ 应用运行正常"
else
    echo "❌ 应用健康检查失败"
fi

echo ""

# 检查最近的日志
echo "📝 最近的错误日志:"
docker-compose logs --tail=10 web | grep -i error || echo "无错误日志"

echo ""

# 检查数据库连接
echo "🗄️ 数据库连接状态:"
docker-compose exec -T db pg_isready -U qatoolbox -d qatoolbox_production && echo "✅ 数据库连接正常" || echo "❌ 数据库连接失败"

echo ""

# 检查Redis连接
echo "🔴 Redis连接状态:"
docker-compose exec -T redis redis-cli ping && echo "✅ Redis连接正常" || echo "❌ Redis连接失败"

echo ""
echo "�� 监控完成！"
