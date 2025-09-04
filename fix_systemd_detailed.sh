#!/bin/bash

# QAToolBox 详细systemd诊断和修复脚本
# 彻底解决203/EXEC错误

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
log_info "QAToolBox 详细systemd诊断和修复脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 详细诊断
log_info "开始详细诊断..."

# 检查用户和组
log_info "检查用户和组..."
id admin || {
    log_error "admin用户不存在"
    exit 1
}

# 检查目录权限
log_info "检查目录权限..."
ls -la /home/admin/QAToolbox/
ls -la /home/admin/QAToolbox/venv/bin/

# 检查文件权限
log_info "检查文件权限..."
chmod +x /home/admin/QAToolbox/venv/bin/python
chmod +x /home/admin/QAToolbox/venv/bin/gunicorn
chmod +x /home/admin/QAToolbox/manage.py

# 2. 测试gunicorn直接执行
log_info "测试gunicorn直接执行..."
timeout 10s /home/admin/QAToolbox/venv/bin/gunicorn --version || {
    log_error "gunicorn版本检查失败"
    exit 1
}

# 3. 测试gunicorn启动（模拟systemd环境）
log_info "测试gunicorn启动（模拟systemd环境）..."
timeout 15s /home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 30 wsgi:application || {
    log_warning "gunicorn启动测试失败，使用manage.py"
    USE_MANAGE_PY=true
}

# 4. 创建日志目录
log_info "创建日志目录..."
mkdir -p /var/log/qatoolbox
chown admin:admin /var/log/qatoolbox

# 5. 创建正确的systemd服务配置
log_info "创建正确的systemd服务配置..."

if [ "$USE_MANAGE_PY" = "true" ]; then
    # 使用manage.py runserver
    cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
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
ReadWritePaths=/var/log/qatoolbox

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
else
    # 使用gunicorn
    cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
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
ExecStart=/home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 30 --access-logfile /var/log/qatoolbox/gunicorn_access.log --error-logfile /var/log/qatoolbox/gunicorn_error.log wsgi:application
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
ReadWritePaths=/var/log/qatoolbox

# 资源限制
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
fi

# 6. 创建日志文件
log_info "创建日志文件..."
touch /var/log/qatoolbox/gunicorn_access.log
touch /var/log/qatoolbox/gunicorn_error.log
chown admin:admin /var/log/qatoolbox/gunicorn_access.log
chown admin:admin /var/log/qatoolbox/gunicorn_error.log

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
sleep 10

# 11. 检查服务状态
log_info "检查服务状态..."
if systemctl is-active --quiet qatoolbox; then
    log_success "服务启动成功！"
    systemctl status qatoolbox --no-pager
else
    log_error "服务启动失败，查看详细日志..."
    journalctl -u qatoolbox --no-pager -n 30
    
    # 尝试手动启动诊断
    log_info "尝试手动启动诊断..."
    cd /home/admin/QAToolbox
    source venv/bin/activate
    
    if [ "$USE_MANAGE_PY" = "true" ]; then
        log_info "手动启动manage.py runserver..."
        timeout 30s /home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py runserver 0.0.0.0:8000 &
        MANAGE_PID=$!
        sleep 5
        if kill -0 $MANAGE_PID 2>/dev/null; then
            log_success "manage.py runserver启动成功！"
            kill $MANAGE_PID
        else
            log_error "manage.py runserver启动失败"
        fi
    else
        log_info "手动启动gunicorn..."
        timeout 30s /home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 30 wsgi:application &
        GUNICORN_PID=$!
        sleep 5
        if kill -0 $GUNICORN_PID 2>/dev/null; then
            log_success "gunicorn启动成功！"
            kill $GUNICORN_PID
        else
            log_error "gunicorn启动失败"
        fi
    fi
    
    exit 1
fi

# 12. 测试应用访问
log_info "测试应用访问..."
sleep 5
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
log_success "详细systemd诊断和修复完成！"
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
echo "  - 应用日志: tail -f /var/log/qatoolbox/*.log"
echo
log_success "现在你的应用应该可以正常访问了！"
log_success "=========================================="
