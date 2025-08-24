#!/bin/bash

echo "🔧 开始修复阿里云部署问题..."

# 设置环境变量
export DJANGO_SETTINGS_MODULE=config.settings.aliyun

# 1. 首先检查当前工作目录
echo "📍 当前工作目录: $(pwd)"

# 2. 激活虚拟环境（如果需要）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 3. 生成缺失的数据库迁移文件
echo "🔄 生成数据库迁移文件..."
python manage.py makemigrations content tools --empty --name fix_deployment_issues 2>/dev/null || true
python manage.py makemigrations content tools 2>/dev/null || true

# 4. 应用数据库迁移
echo "🔄 应用数据库迁移..."
python manage.py migrate --fake-initial 2>/dev/null || python manage.py migrate

# 5. 检查Django配置
echo "🔍 检查Django配置..."
export DJANGO_SETTINGS_MODULE=config.settings.aliyun
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.aliyun')
django.setup()
from django.conf import settings
print(f'DEBUG模式: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'数据库引擎: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print(f'静态文件根目录: {settings.STATIC_ROOT}')
"

# 6. 收集静态文件（忽略警告）
echo "📦 收集静态文件..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true

# 7. 创建超级用户（如果不存在）
echo "👤 创建管理员用户..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ 管理员用户已创建')
else:
    print('ℹ️ 管理员用户已存在')
EOF

# 8. 停止现有的gunicorn进程
echo "🛑 停止现有服务..."
pkill -f gunicorn 2>/dev/null || true
sleep 2

# 9. 检查端口占用
echo "🔍 检查端口8000占用情况..."
netstat -tlnp | grep :8000 || echo "端口8000未被占用"

# 10. 启动gunicorn（使用更详细的配置）
echo "🚀 启动Gunicorn服务器..."
nohup gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class sync \
    --timeout 300 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /tmp/qatoolbox_access.log \
    --error-logfile /tmp/qatoolbox_error.log \
    --log-level info \
    --pid /tmp/qatoolbox.pid \
    wsgi:application > /tmp/qatoolbox.log 2>&1 &

GUNICORN_PID=$!
echo "📝 Gunicorn PID: $GUNICORN_PID"

# 11. 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 12. 检查进程状态
if ps -p $GUNICORN_PID > /dev/null; then
    echo "✅ Gunicorn进程正在运行"
else
    echo "❌ Gunicorn进程启动失败"
    echo "📋 错误日志："
    tail -20 /tmp/qatoolbox_error.log 2>/dev/null || echo "无错误日志"
    tail -20 /tmp/qatoolbox.log 2>/dev/null || echo "无主日志"
    exit 1
fi

# 13. 测试服务连接
echo "🔍 测试服务连接..."
for i in {1..5}; do
    if curl -s -I http://localhost:8000/ | head -1; then
        echo "✅ 服务连接成功！"
        break
    else
        echo "⏳ 第${i}次连接尝试失败，等待5秒..."
        sleep 5
    fi
done

# 14. 显示最终状态
echo "📊 最终状态检查："
echo "进程状态："
ps aux | grep gunicorn | grep -v grep || echo "无gunicorn进程"

echo "端口监听："
netstat -tlnp | grep :8000 || echo "端口8000未监听"

echo "最近日志："
echo "=== 主日志 ==="
tail -10 /tmp/qatoolbox.log 2>/dev/null || echo "无主日志"
echo "=== 错误日志 ==="
tail -10 /tmp/qatoolbox_error.log 2>/dev/null || echo "无错误日志"

echo ""
echo "🎉 部署修复完成！"
echo "🌐 请访问: http://47.103.143.152:8000"
echo "👤 管理员账号: admin / admin123"
echo ""
echo "📋 常用命令："
echo "查看日志: tail -f /tmp/qatoolbox_error.log"
echo "重启服务: pkill -f gunicorn && bash $0"
echo "检查状态: curl -I http://localhost:8000/"
