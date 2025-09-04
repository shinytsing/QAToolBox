#!/bin/bash

# QAToolBox 绕过systemd解决方案
# 使用supervisor或直接启动

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
log_info "QAToolBox 绕过systemd解决方案"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 停止systemd服务
log_info "停止systemd服务..."
systemctl stop qatoolbox 2>/dev/null || true
systemctl disable qatoolbox 2>/dev/null || true

# 2. 安装supervisor
log_info "安装supervisor..."
apt-get update
apt-get install -y supervisor

# 3. 创建supervisor配置
log_info "创建supervisor配置..."
cat > /etc/supervisor/conf.d/qatoolbox.conf << 'EOF'
[program:qatoolbox]
command=/home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py runserver 0.0.0.0:8000
directory=/home/admin/QAToolbox
user=admin
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/app.log
stderr_logfile=/var/log/qatoolbox/error.log
environment=DB_NAME="qatoolbox_production",DB_USER="qatoolbox",DB_PASSWORD="MFFtE6C4z4V1tUgqum+1sg==",DB_HOST="localhost",DB_PORT="5432",DB_ENGINE="django.db.backends.postgresql",DJANGO_SETTINGS_MODULE="config.settings.production"
EOF

# 4. 创建日志目录
log_info "创建日志目录..."
mkdir -p /var/log/qatoolbox
chown admin:admin /var/log/qatoolbox

# 5. 重新加载supervisor配置
log_info "重新加载supervisor配置..."
supervisorctl reread
supervisorctl update

# 6. 启动应用
log_info "启动应用..."
supervisorctl start qatoolbox

# 7. 等待启动
log_info "等待应用启动..."
sleep 10

# 8. 检查状态
log_info "检查应用状态..."
supervisorctl status qatoolbox

# 9. 测试应用访问
log_info "测试应用访问..."
sleep 5
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "应用访问测试成功！"
else
    log_warning "应用访问测试失败，检查日志..."
    tail -n 20 /var/log/qatoolbox/app.log
    tail -n 20 /var/log/qatoolbox/error.log
fi

# 10. 配置Nginx
log_info "配置Nginx..."
if nginx -t; then
    systemctl reload nginx
    log_success "Nginx配置成功！"
else
    log_error "Nginx配置失败"
    exit 1
fi

# 11. 创建启动脚本
log_info "创建启动脚本..."
cat > /home/admin/start_qatoolbox.sh << 'EOF'
#!/bin/bash
cd /home/admin/QAToolbox
source venv/bin/activate
export DB_NAME=qatoolbox_production
export DB_USER=qatoolbox
export DB_PASSWORD=MFFtE6C4z4V1tUgqum+1sg==
export DB_HOST=localhost
export DB_PORT=5432
export DB_ENGINE=django.db.backends.postgresql
export DJANGO_SETTINGS_MODULE=config.settings.production
exec /home/admin/QAToolbox/venv/bin/python /home/admin/QAToolbox/manage.py runserver 0.0.0.0:8000
EOF

chmod +x /home/admin/start_qatoolbox.sh

# 12. 创建systemd服务（简化版）
log_info "创建简化的systemd服务..."
cat > /etc/systemd/system/qatoolbox-simple.service << 'EOF'
[Unit]
Description=QAToolBox Django Application (Simple)
After=network.target

[Service]
Type=simple
User=admin
Group=admin
WorkingDirectory=/home/admin/QAToolbox
ExecStart=/home/admin/start_qatoolbox.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 13. 启用简化服务
log_info "启用简化服务..."
systemctl daemon-reload
systemctl enable qatoolbox-simple
systemctl start qatoolbox-simple

# 14. 等待启动
log_info "等待简化服务启动..."
sleep 10

# 15. 检查简化服务状态
log_info "检查简化服务状态..."
if systemctl is-active --quiet qatoolbox-simple; then
    log_success "简化服务启动成功！"
    systemctl status qatoolbox-simple --no-pager
else
    log_warning "简化服务启动失败，使用supervisor..."
    systemctl stop qatoolbox-simple 2>/dev/null || true
    systemctl disable qatoolbox-simple 2>/dev/null || true
fi

# 16. 最终测试
log_info "最终测试..."
sleep 5
if curl -s http://localhost:8000/ > /dev/null; then
    log_success "应用最终测试成功！"
else
    log_error "应用最终测试失败"
    log_info "查看supervisor日志..."
    supervisorctl tail qatoolbox
    exit 1
fi

log_success "=========================================="
log_success "绕过systemd解决方案完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo
log_info "🛠️  服务管理:"
echo "  - Supervisor状态: supervisorctl status qatoolbox"
echo "  - Supervisor重启: supervisorctl restart qatoolbox"
echo "  - Supervisor日志: supervisorctl tail qatoolbox"
echo "  - 应用日志: tail -f /var/log/qatoolbox/app.log"
echo "  - 错误日志: tail -f /var/log/qatoolbox/error.log"
echo "  - 简化服务状态: systemctl status qatoolbox-simple"
echo "  - 手动启动: /home/admin/start_qatoolbox.sh"
echo
log_success "现在你的应用应该可以正常访问了！"
log_success "=========================================="
