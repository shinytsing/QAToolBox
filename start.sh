#!/bin/bash

# QAToolBox 生产环境启动脚本
# 在容器启动时执行必要的初始化步骤

set -e  # 遇到错误立即退出

echo "🚀 启动 QAToolBox 生产环境..."

# 等待数据库连接
echo "⏳ 等待数据库连接..."
python manage.py migrate --noinput --settings=config.settings.production

# 静态文件已在构建阶段收集，无需重复执行
echo "📦 静态文件已在构建阶段收集完成"

# 创建超级用户（如果不存在）
echo "👤 检查超级用户..."
python manage.py shell --settings=config.settings.production << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'admin123')
    print('✅ 创建默认超级用户: admin/admin123')
else:
    print('✅ 超级用户已存在')
EOF

# 启动Gunicorn
echo "🌐 启动 Gunicorn 服务器..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    wsgi:application
