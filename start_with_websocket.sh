#!/bin/bash

# QAToolBox WebSocket支持启动脚本
# 使用uvicorn启动ASGI应用以支持WebSocket连接

echo "🚀 启动QAToolBox（支持WebSocket）..."

# 检查uvicorn是否已安装
if ! command -v uvicorn &> /dev/null; then
    echo "⚠️  uvicorn未安装，正在安装..."
    pip install uvicorn
fi

# 停止可能运行的Django开发服务器
echo "🛑 停止现有服务器..."
pkill -f "python.*runserver" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# 等待端口释放
sleep 2

# 启动uvicorn ASGI服务器
echo "🔧 启动ASGI服务器（支持WebSocket）..."
echo "📍 服务器地址: http://localhost:8000"
echo "💬 WebSocket支持: ✅"
echo "🎯 表情功能: ✅"
echo "📁 文件发送: ✅"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

uvicorn asgi:application --host 0.0.0.0 --port 8000 --reload
