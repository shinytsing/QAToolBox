#!/bin/bash

# QAToolBox 修复WSGI路径脚本
# 使用正确的WSGI文件路径

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "QAToolBox 修复WSGI路径脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查项目结构
log_info "检查项目结构..."
ls -la

# 2. 检查WSGI文件
log_info "检查WSGI文件..."
if [ -f "wsgi.py" ]; then
    log_success "找到wsgi.py文件"
elif [ -f "QAToolBox/wsgi.py" ]; then
    log_success "找到QAToolBox/wsgi.py文件"
else
    log_error "未找到WSGI文件"
    exit 1
fi

# 3. 检查gunicorn是否安装
log_info "检查gunicorn是否安装..."
if ! pip show gunicorn > /dev/null 2>&1; then
    log_info "安装gunicorn..."
    pip install gunicorn
fi

# 4. 测试gunicorn启动（使用正确的WSGI路径）
log_info "测试gunicorn启动..."
if [ -f "wsgi.py" ]; then
    WSGI_PATH="wsgi:application"
else
    WSGI_PATH="QAToolBox.wsgi:application"
fi

log_info "使用WSGI路径: $WSGI_PATH"

timeout 10s /home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 30 $WSGI_PATH || {
    log_warning "gunicorn启动测试失败，尝试使用manage.py"
    # 使用manage.py runserver作为备选方案
    cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=admin
Group=admin
WorkingDirectory=/home/admin/QAToolbox
Environment=PATH=/home/admin/QAToolbox/venv/bin
Environment=DB_NAME=qatoolbox_production
Environment=DB_USER=qatoolbox
Environment=DB_PASSWORD=MFFtE6C4z4V1tUgqum+1sg==
Environment=DB_HOST=localhost
Environment=DB_PORT=5432
Environment=DB_ENGINE=django.db.backends.postgresql
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
ExecStart=/home/admin/QAToolbox/venv/bin/python manage.py runserver 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qatoolbox

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/admin/QAToolbox
ReadWritePaths=/var/log

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
}

# 5. 重新加载systemd配置
log_info "重新加载systemd配置..."
systemctl daemon-reload

# 6. 停止现有服务
log_info "停止现有服务..."
systemctl stop qatoolbox 2>/dev/null || true

# 7. 启动服务
log_info "启动服务..."
systemctl start qatoolbox

# 8. 等待服务启动
log_info "等待服务启动..."
sleep 5

# 9. 检查服务状态
log_info "检查服务状态..."
if systemctl is-active --quiet qatoolbox; then
    log_success "服务启动成功！"
    systemctl status qatoolbox --no-pager
else
    log_error "服务启动失败，查看详细日志..."
    journalctl -u qatoolbox --no-pager -n 20
    exit 1
fi

# 10. 测试应用访问
log_info "测试应用访问..."
sleep 3
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "应用访问测试成功！"
else
    log_warning "应用访问测试失败，但服务正在运行"
fi

# 11. 配置Nginx
log_info "配置Nginx..."
if nginx -t; then
    systemctl reload nginx
    log_success "Nginx配置成功！"
else
    log_error "Nginx配置失败"
    exit 1
fi

log_success "=========================================="
log_success "WSGI路径修复完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo
log_info "🛠️  服务管理:"
echo "  - 状态: systemctl status qatoolbox"
echo "  - 重启: systemctl restart qatoolbox"
echo "  - 日志: journalctl -u qatoolbox -f"
echo
log_success "现在你的应用应该可以正常访问了！"
log_success "=========================================="