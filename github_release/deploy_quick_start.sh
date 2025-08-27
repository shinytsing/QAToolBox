#!/bin/bash
# QAToolBox 快速部署脚本
# =============================================
# 一行命令部署到服务器 47.103.143.152
# 域名: https://shenyiqing.xin/
# =============================================

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 QAToolBox 快速部署开始...${NC}"

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请使用root权限运行: sudo $0${NC}"
    exit 1
fi

# 更新系统
echo -e "${YELLOW}📦 更新系统包...${NC}"
apt update && apt upgrade -y

# 安装基础依赖
echo -e "${YELLOW}📦 安装基础依赖...${NC}"
apt install -y python3 python3-pip python3-venv git nginx postgresql redis-server supervisor

# 创建项目用户
echo -e "${YELLOW}👤 创建项目用户...${NC}"
useradd -m -s /bin/bash qatoolbox 2>/dev/null || true

# 克隆或复制项目
echo -e "${YELLOW}📁 部署项目...${NC}"
PROJECT_DIR="/home/qatoolbox/QAToolBox"
if [ -d "$PROJECT_DIR" ]; then
    rm -rf "$PROJECT_DIR"
fi

# 如果当前目录有项目文件，复制过去
if [ -f "$(pwd)/manage.py" ]; then
    cp -r "$(pwd)" "$PROJECT_DIR"
else
    # 创建基础项目结构
    mkdir -p "$PROJECT_DIR"
    echo "请手动上传项目文件到 $PROJECT_DIR"
fi

chown -R qatoolbox:qatoolbox "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 创建虚拟环境
echo -e "${YELLOW}🐍 创建虚拟环境...${NC}"
sudo -u qatoolbox python3 -m venv .venv
sudo -u qatoolbox .venv/bin/pip install --upgrade pip

# 安装依赖
echo -e "${YELLOW}📦 安装Python依赖...${NC}"
if [ -f "requirements_complete.txt" ]; then
    sudo -u qatoolbox .venv/bin/pip install -r requirements_complete.txt
elif [ -f "requirements.txt" ]; then
    sudo -u qatoolbox .venv/bin/pip install -r requirements.txt
    # 补充关键依赖
    sudo -u qatoolbox .venv/bin/pip install torch torchvision django-environ opencv-python
fi

# 配置数据库
echo -e "${YELLOW}🗄️ 配置数据库...${NC}"
systemctl start postgresql
sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD 'QAToolBox@2024';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;" 2>/dev/null || true

# 配置环境变量
echo -e "${YELLOW}⚙️ 配置环境变量...${NC}"
cat > .env << 'EOF'
SECRET_KEY=django-quick-deploy-key
DEBUG=False
ALLOWED_HOSTS=shenyiqing.xin,47.103.143.152,localhost
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=settings
EOF

chown qatoolbox:qatoolbox .env

# Django初始化
echo -e "${YELLOW}🚀 Django初始化...${NC}"
export DJANGO_SETTINGS_MODULE=settings
sudo -u qatoolbox -E .venv/bin/python manage.py migrate --noinput 2>/dev/null || true
sudo -u qatoolbox -E .venv/bin/python manage.py collectstatic --noinput 2>/dev/null || true

# 配置Nginx
echo -e "${YELLOW}🌐 配置Nginx...${NC}"
cat > /etc/nginx/sites-available/qatoolbox << 'NGINX_EOF'
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/static/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 配置Supervisor
echo -e "${YELLOW}⚡ 配置进程管理...${NC}"
cat > /etc/supervisor/conf.d/qatoolbox.conf << 'SUPERVISOR_EOF'
[program:qatoolbox]
command=/home/qatoolbox/QAToolBox/.venv/bin/python manage.py runserver 0.0.0.0:8000
directory=/home/qatoolbox/QAToolBox
user=qatoolbox
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
SUPERVISOR_EOF

supervisorctl reread
supervisorctl update
supervisorctl start qatoolbox

# 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"
systemctl enable nginx postgresql redis-server supervisor
systemctl start nginx postgresql redis-server supervisor

echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================="
echo "🌐 访问地址: http://shenyiqing.xin/"
echo "🌐 访问地址: http://47.103.143.152/"
echo "📁 项目目录: /home/qatoolbox/QAToolBox"
echo "📊 查看日志: tail -f /var/log/qatoolbox.log"
echo "🔧 重启服务: supervisorctl restart qatoolbox"
echo "=========================="
