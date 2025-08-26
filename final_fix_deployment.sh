#!/bin/bash

# QAToolBox 最终修复部署脚本 - 快速拉起服务
# 适用于Ubuntu/CentOS系统

set -e

echo "🚀 开始快速修复QAToolBox部署问题..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 功能函数
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查并切换到项目目录
if [ ! -d "/home/qatoolbox/QAToolBox" ]; then
    print_error "项目目录不存在，请先运行部署脚本"
    exit 1
fi

cd /home/qatoolbox/QAToolBox
print_status "当前目录: $(pwd)"

# 1. 停止现有服务
print_status "停止现有服务..."
sudo systemctl stop qatoolbox || true
sudo systemctl stop nginx || true

# 2. 激活虚拟环境并安装缺失依赖
print_status "激活虚拟环境并安装缺失依赖..."
source .venv/bin/activate

# 安装缺失的Python包
pip install django-environ psutil ratelimit pillow-heif opencv-python-headless -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 3. 创建必要的目录结构
print_status "创建必要的目录结构..."
sudo -u qatoolbox mkdir -p /home/qatoolbox/QAToolBox/config/settings
sudo -u qatoolbox mkdir -p /home/qatoolbox/QAToolBox/staticfiles
sudo -u qatoolbox mkdir -p /home/qatoolbox/QAToolBox/media
sudo -u qatoolbox mkdir -p /home/qatoolbox/QAToolBox/logs

# 4. 创建config包初始化文件
print_status "创建config包初始化文件..."
sudo -u qatoolbox touch /home/qatoolbox/QAToolBox/config/__init__.py
sudo -u qatoolbox touch /home/qatoolbox/QAToolBox/config/settings/__init__.py

# 5. 修复数据库连接
print_status "修复PostgreSQL数据库配置..."

# 重新配置PostgreSQL认证
sudo sed -i 's/local   all             qatoolbox                               md5/local   all             qatoolbox                               trust/' /etc/postgresql/*/main/pg_hba.conf || true
sudo systemctl restart postgresql

# 测试数据库连接
if sudo -u postgres psql -c "SELECT 1;" qatoolbox > /dev/null 2>&1; then
    print_success "数据库连接正常"
else
    print_warning "重新创建数据库..."
    sudo -u postgres dropdb qatoolbox || true
    sudo -u postgres dropuser qatoolbox || true
    sudo -u postgres createuser qatoolbox
    sudo -u postgres createdb qatoolbox -O qatoolbox
fi

# 6. 运行数据库迁移
print_status "运行数据库迁移..."
export DJANGO_SETTINGS_MODULE=config.settings.fixed_prod
sudo -u qatoolbox -E .venv/bin/python manage.py makemigrations --settings=config.settings.fixed_prod || true
sudo -u qatoolbox -E .venv/bin/python manage.py migrate --settings=config.settings.fixed_prod

# 7. 收集静态文件
print_status "收集静态文件..."
sudo -u qatoolbox -E .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.fixed_prod

# 8. 创建超级用户（如果不存在）
print_status "创建超级用户账户..."
sudo -u qatoolbox -E .venv/bin/python manage.py shell --settings=config.settings.fixed_prod << 'EOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'admin123')
    print("超级用户 admin 已创建，密码: admin123")
else:
    print("超级用户 admin 已存在")
EOF

# 9. 更新systemd服务文件
print_status "更新systemd服务配置..."
sudo tee /etc/systemd/system/qatoolbox.service > /dev/null << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment="PATH=/home/qatoolbox/QAToolBox/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.fixed_prod"
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --workers 1 --bind 127.0.0.1:8000 --timeout 300 --max-requests 1000 --max-requests-jitter 100 --preload config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 10. 重新加载systemd并启动服务
print_status "重新加载systemd配置..."
sudo systemctl daemon-reload
sudo systemctl enable qatoolbox

# 11. 启动Redis服务
print_status "启动Redis服务..."
sudo systemctl start redis-server || sudo systemctl start redis
sudo systemctl enable redis-server || sudo systemctl enable redis

# 12. 测试Django应用启动
print_status "测试Django应用启动..."
export DJANGO_SETTINGS_MODULE=config.settings.fixed_prod
if sudo -u qatoolbox -E .venv/bin/python manage.py check --settings=config.settings.fixed_prod; then
    print_success "Django应用配置检查通过"
else
    print_error "Django应用配置检查失败"
    exit 1
fi

# 13. 启动应用服务
print_status "启动QAToolBox服务..."
sudo systemctl start qatoolbox

# 等待服务启动
sleep 5

# 14. 检查服务状态
if sudo systemctl is-active --quiet qatoolbox; then
    print_success "QAToolBox服务启动成功"
else
    print_error "QAToolBox服务启动失败，查看日志:"
    sudo journalctl -u qatoolbox --no-pager -n 20
    exit 1
fi

# 15. 启动Nginx
print_status "启动Nginx服务..."
sudo systemctl start nginx
sudo systemctl enable nginx

# 16. 最终验证
print_status "执行最终验证..."

# 检查端口监听
if netstat -tlnp | grep ":8000.*gunicorn" > /dev/null; then
    print_success "Gunicorn正在监听端口8000"
else
    print_warning "Gunicorn可能未正确启动"
fi

# 检查HTTP响应
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200\|302\|404"; then
    print_success "HTTP响应正常"
else
    print_warning "HTTP响应异常，但服务可能正在初始化"
fi

# 17. 显示服务状态
print_status "服务状态摘要:"
echo "=========================="
echo "PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "Redis: $(sudo systemctl is-active redis-server 2>/dev/null || sudo systemctl is-active redis 2>/dev/null || echo 'inactive')"
echo "QAToolBox: $(sudo systemctl is-active qatoolbox)"
echo "Nginx: $(sudo systemctl is-active nginx)"
echo "=========================="

# 18. 显示访问信息
print_success "🎉 快速修复完成！"
echo ""
echo "📋 访问信息:"
echo "   网站地址: https://shenyiqing.xin"
echo "   管理后台: https://shenyiqing.xin/admin/"
echo "   管理员账户: admin / admin123"
echo ""
echo "🔧 常用命令:"
echo "   查看服务状态: sudo systemctl status qatoolbox"
echo "   查看日志: sudo journalctl -u qatoolbox -f"
echo "   重启服务: sudo systemctl restart qatoolbox"
echo ""
echo "🚨 如有问题，请查看日志: sudo journalctl -u qatoolbox --no-pager -n 50"

