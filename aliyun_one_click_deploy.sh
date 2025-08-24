#!/bin/bash

echo "🚀 阿里云一键部署脚本"
echo "======================"

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.aliyun

# 检查是否在正确的目录
if [ ! -f "manage.py" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 未找到虚拟环境，请先创建: python -m venv venv"
    exit 1
fi

# 安装必要的包
echo "📦 安装必要的Python包..."
pip install xmind xmindparser python-docx python-pptx markdown mistune

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p /opt/QAToolbox/staticfiles
mkdir -p /opt/QAToolbox/media
mkdir -p logs

# 生成和应用数据库迁移
echo "🔄 处理数据库迁移..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput

# 收集静态文件
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput --clear

# 创建超级用户
echo "👤 创建管理员用户..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 管理员用户已创建 (用户名: admin, 密码: admin123)')
else:
    print('ℹ️ 管理员用户已存在')
EOF

# 测试Django配置
echo "🔍 测试Django配置..."
python manage.py check --deploy

# 停止现有服务
echo "🛑 停止现有服务..."
pkill -f gunicorn 2>/dev/null || true
sleep 3

# 启动Gunicorn服务器
echo "🚀 启动Gunicorn服务器..."
gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class sync \
    --timeout 300 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile /tmp/qatoolbox_access.log \
    --error-logfile /tmp/qatoolbox_error.log \
    --log-level info \
    --pid /tmp/qatoolbox.pid \
    --daemon \
    wsgi:application

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
if [ -f "/tmp/qatoolbox.pid" ] && ps -p $(cat /tmp/qatoolbox.pid) > /dev/null; then
    echo "✅ Gunicorn服务已启动"
    echo "📝 进程ID: $(cat /tmp/qatoolbox.pid)"
else
    echo "❌ Gunicorn启动失败，检查错误日志:"
    tail -20 /tmp/qatoolbox_error.log 2>/dev/null || echo "无错误日志"
    exit 1
fi

# 测试服务连接
echo "🔍 测试服务连接..."
sleep 5
if curl -s -I http://localhost:8000/ | head -1 | grep -q "200\|302"; then
    echo "✅ 服务连接成功！"
else
    echo "⚠️ 服务连接测试失败，但服务可能仍在启动中"
fi

# 显示部署信息
echo ""
echo "🎉 部署完成！"
echo "================================"
echo "🌐 访问地址: http://47.103.143.152:8000"
echo "👤 管理员登录: http://47.103.143.152:8000/admin"
echo "   用户名: admin"
echo "   密码: admin123"
echo ""
echo "📋 常用命令:"
echo "查看服务状态: ps aux | grep gunicorn"
echo "查看访问日志: tail -f /tmp/qatoolbox_access.log"
echo "查看错误日志: tail -f /tmp/qatoolbox_error.log"
echo "重启服务: pkill -f gunicorn && bash $0"
echo "停止服务: pkill -f gunicorn"
echo ""
echo "🔧 如遇问题，请运行诊断脚本: bash diagnose_deployment.sh"
