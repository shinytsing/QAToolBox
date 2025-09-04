#!/bin/bash

# 简单部署方案 - 不使用Docker

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
log_info "QAToolBox 简单部署方案"
log_info "服务器IP: 47.103.143.152"
log_info "域名: shenyiqing.xin"
log_info "=========================================="

# 1. 进入项目目录
log_info "进入项目目录..."
cd /home/admin/QAToolbox

# 2. 检查Python环境
log_info "检查Python环境..."
python3 --version
pip3 --version

# 3. 安装系统依赖
log_info "安装系统依赖..."
apt-get update
apt-get install -y python3-pip python3-venv python3-dev libpq-dev postgresql-client

# 4. 创建虚拟环境
log_info "创建虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 5. 安装Python依赖
log_info "安装Python依赖..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. 配置环境变量
log_info "配置环境变量..."
if [[ ! -f ".env" ]]; then
    cp env.production .env
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -base64 32)
    sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
    
    DB_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/qatoolbox123/$DB_PASSWORD/" .env
    
    REDIS_PASSWORD=$(openssl rand -base64 16)
    sed -i "s/redis123/$REDIS_PASSWORD/" .env
    
    # 更新允许的主机
    sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin/" .env
    
    # 使用SQLite数据库（避免PostgreSQL配置问题）
    sed -i "s/DATABASE_URL=postgresql:\/\/qatoolbox:.*/DATABASE_URL=sqlite:\/\/\/opt\/qatoolbox\/db.sqlite3/" .env
fi

log_success "环境变量配置完成"

# 7. 数据库迁移
log_info "数据库迁移..."
python manage.py migrate

# 8. 创建超级用户
log_info "创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"

# 9. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput

# 10. 安装Gunicorn
log_info "安装Gunicorn..."
pip install gunicorn

# 11. 创建Gunicorn配置文件
log_info "创建Gunicorn配置文件..."
cat > gunicorn.conf.py << 'EOF'
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "/opt/qatoolbox/logs/gunicorn_access.log"
errorlog = "/opt/qatoolbox/logs/gunicorn_error.log"
loglevel = "info"
EOF

# 12. 创建日志目录
log_info "创建日志目录..."
mkdir -p /opt/qatoolbox/logs

# 13. 创建systemd服务文件
log_info "创建systemd服务文件..."
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/home/admin/QAToolbox
Environment=PATH=/home/admin/QAToolbox/venv/bin
ExecStart=/home/admin/QAToolbox/venv/bin/gunicorn --config gunicorn.conf.py QAToolBox.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 14. 启动服务
log_info "启动服务..."
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox

# 15. 等待服务启动
log_info "等待服务启动..."
sleep 10

# 16. 检查服务状态
log_info "检查服务状态..."
systemctl status qatoolbox --no-pager

# 17. 健康检查
log_info "健康检查..."
for i in {1..20}; do
    if curl -f http://localhost:8000/health/ &>/dev/null; then
        log_success "应用健康检查通过"
        break
    else
        log_info "等待应用启动... ($i/20)"
        sleep 15
    fi
done

# 18. 显示部署结果
log_success "=========================================="
log_success "🎉 QAToolBox 部署完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152:8000"
echo "  - 域名地址: http://shenyiqing.xin:8000"
echo "  - 管理后台: http://47.103.143.152:8000/admin/"
echo "  - 健康检查: http://47.103.143.152:8000/health/"
echo
log_info "👤 管理员账户:"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo "  - 邮箱: admin@shenyiqing.xin"
echo
log_info "🛠️  常用管理命令:"
echo "  - 查看服务状态: systemctl status qatoolbox"
echo "  - 查看日志: journalctl -u qatoolbox -f"
echo "  - 重启服务: systemctl restart qatoolbox"
echo "  - 停止服务: systemctl stop qatoolbox"
echo "  - 进入虚拟环境: source /home/admin/QAToolbox/venv/bin/activate"
echo
log_success "✨ 部署成功！请访问 http://47.103.143.152:8000 查看应用"
log_success "=========================================="
