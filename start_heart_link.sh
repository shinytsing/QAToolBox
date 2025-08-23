#!/bin/bash

# 心动链接启动脚本
# 确保WebSocket功能正常工作

echo "🚀 启动心动链接WebSocket服务器..."

# 激活虚拟环境
source .venv/bin/activate

# 设置Django设置模块
export DJANGO_SETTINGS_MODULE=config.settings.development

# 停止所有现有的服务器进程
echo "🛑 停止现有服务器进程..."
pkill -f "runserver"
pkill -f "daphne"
sleep 2

# 检查端口8000是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ 端口8000被占用，尝试释放..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# 启动daphne服务器（支持WebSocket）
echo "🔌 启动daphne ASGI服务器..."
daphne -b 0.0.0.0 -p 8000 -v 2 asgi:application

echo "✅ 心动链接服务器已启动"
echo "📱 访问地址: http://localhost:8000/"
echo "💬 心动链接: http://localhost:8000/tools/heart_link/"
echo "🧪 WebSocket测试: http://localhost:8000/tools/heart_link/test/"
