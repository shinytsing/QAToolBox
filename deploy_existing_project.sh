#!/bin/bash
# QAToolBox 已有项目快速部署脚本 v6.0
# 适用于已下载项目代码的情况
# 专注核心功能，避免依赖冲突

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查项目目录
if [ ! -d "/home/qatoolbox/QAToolBox" ]; then
    echo_error "项目目录 /home/qatoolbox/QAToolBox 不存在"
    echo "请确保项目已下载到正确位置"
    exit 1
fi

PROJECT_DIR="/home/qatoolbox/QAToolBox"
VENV_NAME="venv_py312"
DB_NAME="qatoolbox"
DB_USER="qatoolbox"
DB_PASSWORD="QAToolBox2024!"
SECRET_KEY="QAToolBox-$(openssl rand -base64 32 | tr -d '+/=')"

echo_step "🚀 开始部署 QAToolBox (已有项目模式)"
echo_step "项目目录: $PROJECT_DIR"

# 步骤1: 更新系统并安装必要软件
echo_step "步骤1: 安装系统依赖"
apt update
apt install -y \
    python3.12 python3.12-venv python3.12-dev \
    postgresql postgresql-contrib \
    redis-server nginx \
    build-essential pkg-config libpq-dev \
    curl wget git supervisor ufw

# 安装 pip for Python 3.12
if ! python3.12 -m pip --version > /dev/null 2>&1; then
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
fi

echo_success "系统依赖安装完成"

# 步骤2: 配置 PostgreSQL
echo_step "步骤2: 配置 PostgreSQL"
systemctl start postgresql
systemctl enable postgresql

# 创建数据库用户和数据库
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" 2>/dev/null || true
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 配置 PostgreSQL 认证
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '(?<=PostgreSQL )\d+')
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

if [ -f "$PG_CONFIG_DIR/pg_hba.conf" ]; then
    cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup" 2>/dev/null || true
    sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" "$PG_CONFIG_DIR/pg_hba.conf"
    systemctl restart postgresql
fi

# 测试数据库连接
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h localhost -c "SELECT 1;" > /dev/null
echo_success "PostgreSQL 配置完成"

# 步骤3: 配置 Redis
echo_step "步骤3: 配置 Redis"
systemctl start redis-server
systemctl enable redis-server
echo_success "Redis 配置完成"

# 步骤4: 创建用户（如果不存在）
echo_step "步骤4: 配置项目用户"
if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
fi
chown -R qatoolbox:qatoolbox /home/qatoolbox
echo_success "用户配置完成"

# 步骤5: 创建虚拟环境
echo_step "步骤5: 创建 Python 虚拟环境"
cd "$PROJECT_DIR"

# 删除旧的虚拟环境
if [ -d "$VENV_NAME" ]; then
    rm -rf "$VENV_NAME"
fi

# 创建新的虚拟环境
sudo -u qatoolbox python3.12 -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# 升级 pip
pip install --upgrade pip setuptools wheel

echo_success "Python 虚拟环境创建完成"

# 步骤6: 配置 pip 镜像源
echo_step "步骤6: 配置 pip 镜像源"
mkdir -p /home/qatoolbox/.pip
cat > /home/qatoolbox/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 3
EOF
chown -R qatoolbox:qatoolbox /home/qatoolbox/.pip

# 步骤7: 安装核心依赖包（精简版）
echo_step "步骤7: 安装核心依赖包"

# 核心 Web 框架
echo_step "安装 Django 核心框架"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "Django>=4.2.0,<5.0" \
    "gunicorn>=21.2.0" \
    "python-dotenv>=1.0.0"

# 数据库和缓存
echo_step "安装数据库和缓存支持"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "psycopg2-binary>=2.9.0" \
    "redis>=4.5.0" \
    "django-redis>=5.4.0"

# Django 扩展（核心功能）
echo_step "安装 Django 扩展"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "django-cors-headers>=4.3.0" \
    "django-crispy-forms>=2.0" \
    "crispy-bootstrap5>=0.7" \
    "django-extensions>=3.2.0"

# Web 和工具库
echo_step "安装基础工具库"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "requests>=2.31.0" \
    "beautifulsoup4>=4.12.0" \
    "Pillow>=10.0.0" \
    "openpyxl>=3.1.0" \
    "python-dateutil>=2.8.0"

# 可选包（单独安装，失败不影响核心功能）
echo_step "安装可选功能包"
OPTIONAL_PACKAGES=(
    "numpy>=1.26.0"
    "pandas>=2.1.0"
    "matplotlib>=3.7.0"
    "django-simple-captcha>=0.5.20"
    "channels>=4.0.0"
    "celery>=5.3.0"
    "ratelimit>=2.2.0"
    "psutil>=5.9.0"
)

for package in "${OPTIONAL_PACKAGES[@]}"; do
    echo_step "尝试安装 $package"
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 "$package" || echo_warning "$package 安装失败，跳过"
done

echo_success "依赖包安装完成"

# 步骤8: 配置环境变量
echo_step "步骤8: 配置环境变量"
cat > "$PROJECT_DIR/.env" << EOF
DEBUG=False
DJANGO_SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EOF

chown qatoolbox:qatoolbox "$PROJECT_DIR/.env"
echo_success "环境变量配置完成"

# 步骤9: Django 配置和迁移
echo_step "步骤9: Django 应用配置"
export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

# 检查 Django 配置
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    python manage.py check
"

# 数据库迁移
echo_step "运行数据库迁移"
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    python manage.py makemigrations --noinput || true
    python manage.py migrate --noinput
"

# 收集静态文件
echo_step "收集静态文件"
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    python manage.py collectstatic --noinput --clear
"

# 创建超级用户
echo_step "创建管理员用户"
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    echo \"from django.contrib.auth.models import User; User.objects.filter(username='admin').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')\" | python manage.py shell
" 2>/dev/null || echo_warning "管理员用户创建可能失败，稍后可手动创建"

echo_success "Django 应用配置完成"

# 步骤10: 配置 Gunicorn 服务
echo_step "步骤10: 配置 Gunicorn 系统服务"
cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Gunicorn daemon
After=network.target

[Service]
User=qatoolbox
Group=qatoolbox
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/$VENV_NAME/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.aliyun_production"
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 --timeout 120 --access-logfile - --error-logfile - wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox

echo_success "Gunicorn 服务配置完成"

# 步骤11: 配置 Nginx
echo_step "步骤11: 配置 Nginx"
cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152 _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t
systemctl enable nginx
systemctl restart nginx

echo_success "Nginx 配置完成"

# 步骤12: 配置防火墙
echo_step "步骤12: 配置防火墙"
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443

echo_success "防火墙配置完成"

# 步骤13: 启动所有服务
echo_step "步骤13: 启动系统服务"
systemctl enable postgresql redis-server nginx qatoolbox
systemctl restart qatoolbox

# 等待服务启动
sleep 5

# 最终测试
echo_step "步骤14: 系统测试"
echo_step "检查服务状态"
systemctl is-active postgresql && echo_success "PostgreSQL 运行正常" || echo_error "PostgreSQL 未运行"
systemctl is-active redis-server && echo_success "Redis 运行正常" || echo_error "Redis 未运行"
systemctl is-active nginx && echo_success "Nginx 运行正常" || echo_error "Nginx 未运行"
systemctl is-active qatoolbox && echo_success "QAToolBox 运行正常" || echo_error "QAToolBox 未运行"

# 测试 HTTP 响应
echo_step "测试 HTTP 响应"
if curl -s -I http://localhost/ | grep -q "200 OK"; then
    echo_success "HTTP 响应测试通过"
else
    echo_warning "HTTP 响应测试失败，检查日志: journalctl -u qatoolbox -n 20"
fi

# 显示部署信息
echo_step "🎉 部署完成！"
echo -e "${GREEN}"
echo "=========================================="
echo "  QAToolBox 部署成功！"
echo "=========================================="
echo "访问地址:"
echo "  http://47.103.143.152"
echo "  http://shenyiqing.xin"
echo ""
echo "管理后台:"
echo "  http://47.103.143.152/admin/"
echo "  用户名: admin"
echo "  密码: admin123456"
echo ""
echo "服务管理:"
echo "  重启应用: sudo systemctl restart qatoolbox"
echo "  查看日志: sudo journalctl -u qatoolbox -f"
echo "  重启Nginx: sudo systemctl restart nginx"
echo ""
echo "文件位置:"
echo "  项目目录: $PROJECT_DIR"
echo "  虚拟环境: $PROJECT_DIR/$VENV_NAME"
echo "  配置文件: $PROJECT_DIR/.env"
echo "=========================================="
echo -e "${NC}"

echo_success "🚀 QAToolBox 部署脚本执行完成！"
echo_step "现在可以通过浏览器访问你的应用了！"
