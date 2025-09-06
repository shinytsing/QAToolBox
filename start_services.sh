#!/bin/bash

# QAToolBox 多平台服务启动脚本
# 启动 Django 后端、Vue3 管理后台、Vue3 用户界面等所有服务

echo "🚀 启动 QAToolBox 多平台服务..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip list | grep -q "Django" || { echo "❌ Django 未安装"; exit 1; }
pip list | grep -q "djangorestframework" || { echo "❌ DRF 未安装"; exit 1; }

# 检查数据库迁移
echo "🗄️ 检查数据库迁移..."
python manage.py migrate --check || {
    echo "⚠️ 发现未应用的迁移，正在应用..."
    python manage.py migrate
}

# 启动 Django 后端服务器
echo "🐍 启动 Django 后端服务器 (端口 8000)..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# 等待 Django 启动
sleep 5

# 检查 Django 是否启动成功
if ! curl -s http://localhost:8000/api/v1/ > /dev/null; then
    echo "❌ Django 服务器启动失败"
    kill $DJANGO_PID 2>/dev/null
    exit 1
fi

echo "✅ Django 后端服务器启动成功 (PID: $DJANGO_PID)"

# 检查前端项目是否存在
if [ -d "frontend/admin-dashboard" ]; then
    echo "🎨 启动 Vue3 管理后台 (端口 3000)..."
    cd frontend/admin-dashboard
    npm run dev -- --port 3000 &
    ADMIN_PID=$!
    cd ../..
    echo "✅ Vue3 管理后台启动成功 (PID: $ADMIN_PID)"
else
    echo "⚠️ Vue3 管理后台项目不存在，跳过"
fi

if [ -d "frontend/user-interface" ]; then
    echo "🎨 启动 Vue3 用户界面 (端口 5173)..."
    cd frontend/user-interface
    npm run dev -- --port 5173 &
    USER_PID=$!
    cd ../..
    echo "✅ Vue3 用户界面启动成功 (PID: $USER_PID)"
else
    echo "⚠️ Vue3 用户界面项目不存在，跳过"
fi

# 显示服务状态
echo ""
echo "🎉 所有服务启动完成！"
echo "📊 服务状态："
echo "  - Django 后端: http://localhost:8000 (PID: $DJANGO_PID)"
echo "  - API 文档: http://localhost:8000/api/v1/"
echo "  - 统一登录: http://localhost:8000/api/v1/auth/unified/login/"

if [ ! -z "$ADMIN_PID" ]; then
    echo "  - Vue3 管理后台: http://localhost:3000 (PID: $ADMIN_PID)"
fi

if [ ! -z "$USER_PID" ]; then
    echo "  - Vue3 用户界面: http://localhost:5173 (PID: $USER_PID)"
fi

echo ""
echo "🔧 测试 API："
echo "  curl -X POST http://localhost:8000/api/v1/auth/unified/login/ \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"testuser\",\"password\":\"testpass123\",\"device_type\":\"web\"}'"

echo ""
echo "⏹️ 停止所有服务："
echo "  kill $DJANGO_PID $ADMIN_PID $USER_PID 2>/dev/null"

# 保存进程 ID
echo "$DJANGO_PID $ADMIN_PID $USER_PID" > .service_pids

echo ""
echo "✨ 服务已启动，按 Ctrl+C 停止所有服务"

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止所有服务..."; kill $DJANGO_PID $ADMIN_PID $USER_PID 2>/dev/null; rm -f .service_pids; echo "✅ 所有服务已停止"; exit 0' INT

# 保持脚本运行
wait