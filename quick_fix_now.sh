#!/bin/bash

# =============================================================================
# QAToolBox 立即修复脚本 - 解决当前502和迁移问题
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${GREEN}========================================"
echo "    🔧 QAToolBox 立即修复"
echo "========================================"
echo -e "${NC}"

# 检查root权限
if [[ $EUID -ne 0 ]]; then
    log_error "需要root权限运行此脚本"
    echo "请使用: sudo bash $0"
    exit 1
fi

log_info "开始立即修复流程..."

# 停止服务
log_info "停止现有服务"
systemctl stop qatoolbox 2>/dev/null || true
pkill -f "gunicorn.*qatoolbox" 2>/dev/null || true
sleep 3

# 检查项目目录
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录不存在: $PROJECT_DIR"
    exit 1
fi

cd $PROJECT_DIR

# 重置数据库（解决迁移问题）
log_info "重置数据库解决迁移问题"
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"

# 检查并安装缺失依赖
log_info "安装缺失的Python依赖"
if [ -d ".venv" ]; then
    sudo -u $PROJECT_USER .venv/bin/pip install django-environ==0.11.2 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
else
    log_error "虚拟环境不存在，请先运行完整部署脚本"
    exit 1
fi

# 清理迁移文件
log_info "清理旧的迁移文件"
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete 2>/dev/null || true
find . -path "*/migrations/*.pyc" -delete 2>/dev/null || true

# 重新创建迁移
log_info "重新创建迁移文件"
sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations

# 执行迁移
log_info "执行数据库迁移"
sudo -u $PROJECT_USER .venv/bin/python manage.py migrate

# 收集静态文件
log_info "收集静态文件"
sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput

# 创建管理员用户
log_info "创建管理员用户"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'QAToolBox@2024')" | sudo -u $PROJECT_USER .venv/bin/python manage.py shell

# 修复systemd服务配置（解决Gunicorn参数问题）
log_info "修复systemd服务配置"
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
Environment=PATH=/home/qatoolbox/QAToolBox/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --preload \
    --access-logfile /var/log/qatoolbox/access.log \
    --error-logfile /var/log/qatoolbox/error.log \
    config.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 创建日志目录
mkdir -p /var/log/qatoolbox
chown qatoolbox:qatoolbox /var/log/qatoolbox

# 重新加载并启动服务
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox

# 等待服务启动
log_info "等待服务启动"
sleep 15

# 检查服务状态
if systemctl is-active --quiet qatoolbox; then
    log_success "应用服务启动成功"
else
    log_error "应用服务启动失败"
    echo "错误日志:"
    journalctl -u qatoolbox -n 30 --no-pager
    exit 1
fi

# 重启Nginx
systemctl restart nginx

# 测试连接
log_info "测试连接"
sleep 5

if curl -s -f http://127.0.0.1:8000/health/ > /dev/null 2>&1; then
    log_success "本地应用连接正常"
elif curl -s -f http://127.0.0.1:8000/ > /dev/null 2>&1; then
    log_success "本地应用连接正常（主页响应）"
else
    log_error "本地应用连接失败"
    journalctl -u qatoolbox -n 10 --no-pager
    exit 1
fi

echo
echo -e "${GREEN}========================================"
echo "        🎉 修复完成！"
echo "========================================"
echo -e "${NC}"
echo -e "${GREEN}访问地址: https://shenyiqing.xin${NC}"
echo -e "${GREEN}管理后台: https://shenyiqing.xin/admin/${NC}"
echo -e "${GREEN}用户名: admin, 密码: QAToolBox@2024${NC}"
echo
echo "服务状态:"
echo "  应用服务: $(systemctl is-active qatoolbox)"
echo "  Nginx服务: $(systemctl is-active nginx)"
echo "  PostgreSQL: $(systemctl is-active postgresql)"
echo "  Redis: $(systemctl is-active redis-server)"
echo
echo -e "${BLUE}如果还有问题，查看日志:${NC}"
echo "  sudo journalctl -u qatoolbox -f"
