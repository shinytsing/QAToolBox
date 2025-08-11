#!/bin/bash

# ASGI服务器启动脚本
echo "🚀 启动ASGI服务器 (支持WebSocket)..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未找到，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  建议在虚拟环境中运行"
    echo "   创建虚拟环境: python3 -m venv venv"
    echo "   激活虚拟环境: source venv/bin/activate"
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import daphne, channels" 2>/dev/null; then
    echo "❌ 缺少必要依赖，正在安装..."
    pip install -r requirements/dev.txt
fi

# 启动服务器
echo "🔌 启动WebSocket服务器..."
python3 run_asgi_server.py
