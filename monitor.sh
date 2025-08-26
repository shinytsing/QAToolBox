#!/bin/bash

# QAToolBox 服务监控脚本

set -e

echo "📊 QAToolBox 服务状态监控"
echo "================================"

# 检查Docker服务
echo "🐳 Docker服务状态:"
if systemctl is-active --quiet docker; then
    echo "✅ Docker服务运行正常"
else
    echo "❌ Docker服务未运行"
fi

# 检查容器状态
echo ""
echo "📦 容器状态:"
docker-compose -f docker-compose.china.yml ps

# 检查磁盘使用情况
echo ""
echo "💾 磁盘使用情况:"
df -h / | tail -1 | awk '{print "使用: " $3 "/" $2 " (" $5 ")"}'

# 检查内存使用情况
echo ""
echo "🧠 内存使用情况:"
free -h | grep "Mem:" | awk '{print "使用: " $3 "/" $2}'

# 检查Web服务响应
echo ""
echo "🌐 Web服务检查:"
if curl -f -s http://localhost:80 > /dev/null; then
    echo "✅ Web服务响应正常"
else
    echo "❌ Web服务无响应"
fi

# 检查最近的错误日志
echo ""
echo "📝 最近错误日志 (最后10行):"
if [ -f "logs/django_error.log" ]; then
    tail -10 logs/django_error.log
else
    echo "暂无错误日志"
fi

echo ""
echo "================================"
echo "监控完成 - $(date)"

