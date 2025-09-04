#!/bin/bash

# QAToolBox 修复systemd服务配置脚本
# 解决203/EXEC错误

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
log_info "QAToolBox 修复systemd服务配置脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查文件权限
log_info "检查文件权限..."
chmod +x /home/admin/QAToolbox/venv/bin/python
chmod +x /home/admin/QAToolbox/venv/bin/gunicorn
chmod +x /home/admin/QAToolbox/manage.py

# 2. 检查文件是否存在
log_info "检查关键文件..."
if [ ! -f "/home/admin/QAToolbox/venv/bin/python" ]; then
    log_error "Python可执行文件不存在"
    exit 1
fi

if [ ! -f "/home/admin/QAToolbox/manage.py" ]; then
    log_error "manage.py文件不存在"
    exit 1
fi

if [ ! -f "/home/admin/QAToolbox/venv/bin/gunicorn" ]; then
    log_error "gunicorn可执行文件不存在"
    exit 1
fi

log_success "所有关键文件存在"

# 3. 测试Python路径
log_info "测试Python路径..."
/home/admin/QAToolbox/venv/bin/python --version || {
    log_error "Python路径测试失败"
    exit 1
}

# 4. 测试manage.py
log_info "测试manage.py..."
timeout 10s /home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py check || {
    log_error "manage.py测试失败"
    exit 1
}

# 5. 创建正确的systemd服务配置
log_info "创建正确的systemd服务配置..."

# 使用gunicorn的配置
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
ExecStart=/home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 30 --access-logfile /var/log/gunicorn_access.log --error-logfile /var/log/gunicorn_error.log wsgi:application
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

# 6. 创建日志文件
log_info "创建日志文件..."
touch /var/log/gunicorn_access.log
touch /var/log/gunicorn_error.log
chown admin:admin /var/log/gunicorn_access.log
chown admin:admin /var/log/gunicorn_error.log

# 7. 重新加载systemd配置
log_info "重新加载systemd配置..."
systemctl daemon-reload

# 8. 停止现有服务
log_info "停止现有服务..."
systemctl stop qatoolbox 2>/dev/null || true

# 9. 启动服务
log_info "启动服务..."
systemctl start qatoolbox

# 10. 等待服务启动
log_info "等待服务启动..."
sleep 5

# 11. 检查服务状态
log_info "检查服务状态..."
if systemctl is-active --quiet qatoolbox; then
    log_success "服务启动成功！"
    systemctl status qatoolbox --no-pager
else
    log_error "服务启动失败，查看详细日志..."
    journalctl -u qatoolbox --no-pager -n 20
    log_info "尝试使用备选方案..."
    
    # 备选方案：使用manage.py runserver
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
ExecStart=/home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py runserver 0.0.0.0:8000
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

    systemctl daemon-reload
    systemctl start qatoolbox
    sleep 5
    
    if systemctl is-active --quiet qatoolbox; then
        log_success "备选方案启动成功！"
        systemctl status qatoolbox --no-pager
    else
        log_error "备选方案也失败，查看详细日志..."
        journalctl -u qatoolbox --no-pager -n 20
        exit 1
    fi
fi

# 12. 测试应用访问
log_info "测试应用访问..."
sleep 3
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "应用访问测试成功！"
else
    log_warning "应用访问测试失败，但服务正在运行"
fi

# 13. 配置Nginx
log_info "配置Nginx..."
if nginx -t; then
    systemctl reload nginx
    log_success "Nginx配置成功！"
else
    log_error "Nginx配置失败"
    exit 1
fi

log_success "=========================================="
log_success "systemd服务配置修复完成！"
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
echo "  - Gunicorn日志: tail -f /var/log/gunicorn_*.log"
echo
log_success "现在你的应用应该可以正常访问了！"
log_success "=========================================="
