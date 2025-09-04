#!/bin/bash

# QAToolBox 生产环境稳定部署脚本
# 创建持久化服务，自动重启，监控和日志管理

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
log_info "QAToolBox 生产环境稳定部署脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 创建systemd服务文件
log_info "创建systemd服务文件..."
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
ExecStart=/home/admin/QAToolbox/venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --preload QAToolBox.wsgi:application
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

# 2. 创建Nginx配置文件
log_info "创建Nginx配置文件..."
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # 客户端最大请求体大小
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health/;
    }
}
EOF

# 3. 启用Nginx站点
log_info "启用Nginx站点..."
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 4. 创建日志轮转配置
log_info "创建日志轮转配置..."
cat > /etc/logrotate.d/qatoolbox << 'EOF'
/home/admin/QAToolbox/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 admin admin
    postrotate
        systemctl reload qatoolbox
    endscript
}
EOF

# 5. 创建健康检查脚本
log_info "创建健康检查脚本..."
cat > /home/admin/QAToolbox/health_check.py << 'EOF'
#!/usr/bin/env python3
import os
import sys
import django
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db import connection
from django.core.cache import cache

def health_check():
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        
        # 检查缓存
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        
        print("OK")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(health_check())
EOF

chmod +x /home/admin/QAToolbox/health_check.py

# 6. 创建监控脚本
log_info "创建监控脚本..."
cat > /home/admin/QAToolbox/monitor.sh << 'EOF'
#!/bin/bash
# QAToolBox 监控脚本

LOG_FILE="/home/admin/QAToolbox/logs/monitor.log"
SERVICE_NAME="qatoolbox"

# 检查服务状态
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Service $SERVICE_NAME is not running, restarting..." >> $LOG_FILE
    systemctl restart $SERVICE_NAME
fi

# 检查健康状态
if ! /home/admin/QAToolbox/health_check.py > /dev/null 2>&1; then
    echo "$(date): Health check failed, restarting service..." >> $LOG_FILE
    systemctl restart $SERVICE_NAME
fi

# 检查内存使用
MEMORY_USAGE=$(ps -o pid,ppid,cmd,%mem,%cpu --sort=-%mem -C gunicorn | head -2 | tail -1 | awk '{print $4}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "$(date): High memory usage ($MEMORY_USAGE%), restarting service..." >> $LOG_FILE
    systemctl restart $SERVICE_NAME
fi
EOF

chmod +x /home/admin/QAToolbox/monitor.sh

# 7. 创建定时任务
log_info "创建定时任务..."
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/admin/QAToolbox/monitor.sh") | crontab -

# 8. 重新加载systemd配置
log_info "重新加载systemd配置..."
systemctl daemon-reload

# 9. 启动并启用服务
log_info "启动并启用服务..."
systemctl enable qatoolbox
systemctl start qatoolbox

# 10. 配置Nginx
log_info "配置Nginx..."
nginx -t && systemctl reload nginx

# 11. 设置防火墙
log_info "设置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# 12. 创建启动脚本
log_info "创建启动脚本..."
cat > /home/admin/QAToolbox/start.sh << 'EOF'
#!/bin/bash
# QAToolBox 启动脚本

echo "启动QAToolBox服务..."
systemctl start qatoolbox
systemctl start nginx
systemctl start postgresql
systemctl start redis

echo "检查服务状态..."
systemctl status qatoolbox --no-pager
systemctl status nginx --no-pager

echo "服务启动完成！"
echo "访问地址: http://47.103.143.152"
echo "管理后台: http://47.103.143.152/admin/"
EOF

chmod +x /home/admin/QAToolbox/start.sh

# 13. 创建停止脚本
log_info "创建停止脚本..."
cat > /home/admin/QAToolbox/stop.sh << 'EOF'
#!/bin/bash
# QAToolBox 停止脚本

echo "停止QAToolBox服务..."
systemctl stop qatoolbox
systemctl stop nginx

echo "服务已停止！"
EOF

chmod +x /home/admin/QAToolbox/stop.sh

# 14. 创建重启脚本
log_info "创建重启脚本..."
cat > /home/admin/QAToolbox/restart.sh << 'EOF'
#!/bin/bash
# QAToolBox 重启脚本

echo "重启QAToolBox服务..."
systemctl restart qatoolbox
systemctl reload nginx

echo "服务已重启！"
echo "访问地址: http://47.103.143.152"
EOF

chmod +x /home/admin/QAToolbox/restart.sh

# 15. 检查服务状态
log_info "检查服务状态..."
sleep 5
systemctl status qatoolbox --no-pager
systemctl status nginx --no-pager

log_success "=========================================="
log_success "生产环境稳定部署完成！"
log_success "=========================================="
echo
log_info "🚀 服务管理命令:"
echo "  - 启动: systemctl start qatoolbox"
echo "  - 停止: systemctl stop qatoolbox"
echo "  - 重启: systemctl restart qatoolbox"
echo "  - 状态: systemctl status qatoolbox"
echo "  - 日志: journalctl -u qatoolbox -f"
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo
log_info "🛠️  管理脚本:"
echo "  - 启动: ./start.sh"
echo "  - 停止: ./stop.sh"
echo "  - 重启: ./restart.sh"
echo
log_info "📊 监控功能:"
echo "  - 自动重启: 每5分钟检查一次"
echo "  - 健康检查: 自动检测服务状态"
echo "  - 日志轮转: 自动管理日志文件"
echo "  - 内存监控: 自动处理高内存使用"
echo
log_success "现在你的应用已经具备了生产级的稳定性和持久性！"
log_success "=========================================="
