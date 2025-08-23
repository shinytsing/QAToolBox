#!/bin/bash

# 好心人攻略功能启动脚本
# 用于快速启动和测试好心人攻略功能

echo "🤝 WanderAI 好心人攻略功能启动脚本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查Django项目是否存在
if [ ! -f "manage.py" ]; then
    echo "❌ 错误: 未找到manage.py文件，请确保在Django项目根目录下运行此脚本"
    exit 1
fi

# 检查数据库迁移
echo "📊 检查数据库迁移..."
python3 manage.py makemigrations --dry-run > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移状态正常"
else
    echo "⚠️ 建议运行数据库迁移: python3 manage.py makemigrations && python3 manage.py migrate"
fi

# 检查静态文件
echo "📁 检查静态文件..."
if [ ! -d "staticfiles" ]; then
    echo "📦 收集静态文件..."
    python3 manage.py collectstatic --noinput
fi

# 启动开发服务器
echo "🚀 启动开发服务器..."
echo "📍 服务器地址: http://localhost:8000"
echo "🎯 好心人攻略页面: http://localhost:8000/tools/travel_guide/"
echo "🧪 测试页面: http://localhost:8000/test_good_people_guide.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
python3 manage.py runserver 0.0.0.0:8000
