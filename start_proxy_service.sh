#!/bin/bash

echo "🚀 启动商业化翻墙服务系统..."
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 错误: 未找到虚拟环境 .venv"
    echo "请先运行: python3 -m venv .venv"
    exit 1
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip install -q requests PyYAML

# 启动本地代理服务器（后台运行）
echo "🌐 启动本地代理服务器..."
python local_proxy_server.py &
PROXY_PID=$!

# 等待代理服务器启动
sleep 3

# 检查代理服务器是否启动成功
if ! curl -s http://127.0.0.1:8080 > /dev/null 2>&1; then
    echo "⚠️  本地代理服务器启动失败，继续启动Web服务..."
else
    echo "✅ 本地代理服务器已启动 (端口8080)"
fi

# 启动Django服务器
echo "🌍 启动Django Web服务器..."
echo "💡 访问地址: http://localhost:8001/tools/proxy-dashboard/"
echo "🔧 本地代理: http://127.0.0.1:8080"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=================================="

# 启动Django服务器
python manage.py runserver 8001

# 清理：停止代理服务器
echo ""
echo "🛑 正在停止本地代理服务器..."
kill $PROXY_PID 2>/dev/null
echo "✅ 所有服务已停止"
