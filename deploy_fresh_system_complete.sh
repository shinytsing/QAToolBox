#!/bin/bash
# QAToolBox 完整功能一键部署脚本 v5.0
# 适用于重制的 Ubuntu 24.04 系统
# 支持 Python 3.12 + PostgreSQL + Redis + Nginx + Gunicorn

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="QAToolBox"
PROJECT_DIR="/home/qatoolbox/$PROJECT_NAME"
VENV_NAME="venv_py312"
GITHUB_REPO="https://github.com/shinytsing/QAToolbox.git"
DB_NAME="qatoolbox"
DB_USER="qatoolbox"
DB_PASSWORD="QAToolBox2024!"
SECRET_KEY="QAToolBox-$(openssl rand -base64 32 | tr -d '+/=')"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"

# GitHub 镜像源
GITHUB_MIRRORS=(
    "https://github.com/shinytsing/QAToolbox.git"
    "https://github.com.cnpmjs.org/shinytsing/QAToolbox.git"
    "https://hub.fastgit.xyz/shinytsing/QAToolbox.git"
    "https://gitclone.com/github.com/shinytsing/QAToolbox.git"
)

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

# 步骤1: 系统更新和基础软件安装
echo_step "步骤1: 更新系统并安装基础软件包"
apt update && apt upgrade -y
apt install -y \
    wget curl git vim htop unzip software-properties-common \
    build-essential pkg-config python3-dev libpq-dev \
    nginx redis-server postgresql postgresql-contrib \
    ufw fail2ban supervisor

# 步骤2: 安装 Python 3.12
echo_step "步骤2: 安装 Python 3.12"
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y python3.12 python3.12-venv python3.12-dev

# 安装 pip for Python 3.12
if ! python3.12 -m pip --version > /dev/null 2>&1; then
    echo_step "安装 pip for Python 3.12"
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
fi

echo_success "Python 3.12 安装完成: $(python3.12 --version)"

# 步骤3: 配置 PostgreSQL
echo_step "步骤3: 配置 PostgreSQL 数据库"
systemctl start postgresql
systemctl enable postgresql

# 创建数据库用户和数据库
sudo -u postgres psql -c "DROP USER IF EXISTS $DB_USER;" || true
sudo -u postgres psql -c "DROP DATABASE IF EXISTS $DB_NAME;" || true
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

# 配置 PostgreSQL 认证
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '(?<=PostgreSQL )\d+\.\d+')
PG_CONFIG_DIR="/etc/postgresql/$PG_VERSION/main"

# 备份并修改 pg_hba.conf
cp "$PG_CONFIG_DIR/pg_hba.conf" "$PG_CONFIG_DIR/pg_hba.conf.backup"
sed -i "s/local   all             all                                     peer/local   all             all                                     md5/" "$PG_CONFIG_DIR/pg_hba.conf"

systemctl restart postgresql

# 测试数据库连接
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -d $DB_NAME -h localhost -c "SELECT 1;" > /dev/null
echo_success "PostgreSQL 配置完成并测试连接成功"

# 步骤4: 配置 Redis
echo_step "步骤4: 配置 Redis"
systemctl start redis-server
systemctl enable redis-server
echo_success "Redis 配置完成"

# 步骤5: 创建项目用户和目录
echo_step "步骤5: 创建项目用户和目录结构"
if ! id "qatoolbox" &>/dev/null; then
    useradd -m -s /bin/bash qatoolbox
    echo_success "用户 qatoolbox 创建完成"
else
    echo_success "用户 qatoolbox 已存在"
fi

mkdir -p /home/qatoolbox
chown qatoolbox:qatoolbox /home/qatoolbox

# 步骤6: 克隆项目代码
echo_step "步骤6: 从 GitHub 克隆项目代码"
cd /home/qatoolbox

# 删除已存在的项目目录
if [ -d "$PROJECT_NAME" ]; then
    rm -rf "$PROJECT_NAME"
fi

# 尝试从多个 GitHub 镜像克隆
CLONE_SUCCESS=false
for mirror in "${GITHUB_MIRRORS[@]}"; do
    echo_step "尝试从 $mirror 克隆代码"
    if git clone "$mirror" "$PROJECT_NAME"; then
        CLONE_SUCCESS=true
        echo_success "成功从 $mirror 克隆代码"
        break
    else
        echo_warning "从 $mirror 克隆失败，尝试下一个镜像"
    fi
done

if [ "$CLONE_SUCCESS" = false ]; then
    echo_error "所有 GitHub 镜像克隆失败"
    exit 1
fi

chown -R qatoolbox:qatoolbox "/home/qatoolbox/$PROJECT_NAME"
cd "$PROJECT_DIR"

# 步骤7: 创建 Python 虚拟环境
echo_step "步骤7: 创建 Python 3.12 虚拟环境"
sudo -u qatoolbox python3.12 -m venv "$PROJECT_DIR/$VENV_NAME"
source "$PROJECT_DIR/$VENV_NAME/bin/activate"

# 升级 pip 和安装基础包
pip install --upgrade pip setuptools wheel

echo_success "Python 虚拟环境创建完成"

# 步骤8: 安装 Python 依赖包
echo_step "步骤8: 安装 Python 依赖包"

# 配置 pip 使用国内镜像源加速下载
echo_step "配置 pip 镜像源"
mkdir -p /home/qatoolbox/.pip
cat > /home/qatoolbox/.pip/pip.conf << EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 3
EOF

# 设置 pip 环境变量
export PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
export PIP_TRUSTED_HOST=mirrors.aliyun.com
export PIP_TIMEOUT=120
export PIP_RETRIES=3

# 优先尝试从 requirements.txt 安装
if [ -f "requirements/base.txt" ]; then
    echo_step "从 requirements/base.txt 安装依赖"
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 -r requirements/base.txt || echo_warning "requirements/base.txt 安装部分失败"
elif [ -f "requirements.txt" ]; then
    echo_step "从 requirements.txt 安装依赖"
    pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 -r requirements.txt || echo_warning "requirements.txt 安装部分失败"
fi

# 分批安装核心依赖包（避免大包下载超时）
echo_step "分批安装核心依赖包"

# 第一批：核心框架包
echo_step "📦 安装批次 1: Django 核心框架"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "Django>=4.2.0,<5.0" \
    "psycopg2-binary>=2.9.0" \
    "redis>=4.5.0" \
    "gunicorn>=21.2.0" \
    "python-dotenv>=1.0.0" || echo_warning "批次 1 部分包安装失败"

# 第二批：Django 扩展包
echo_step "📦 安装批次 2: Django 扩展包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "django-cors-headers>=4.3.0" \
    "django-crispy-forms>=2.0" \
    "crispy-bootstrap5>=0.7" \
    "django-simple-captcha>=0.5.20" \
    "django-extensions>=3.2.0" \
    "django-filter>=23.3" \
    "django-redis>=5.4.0" || echo_warning "批次 2 部分包安装失败"

# 第三批：Web 相关包
echo_step "📦 安装批次 3: Web 和异步包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "requests>=2.31.0" \
    "beautifulsoup4>=4.12.0" \
    "lxml>=4.9.0" \
    "channels>=4.0.0" \
    "channels-redis>=4.1.0" \
    "daphne>=4.0.0" \
    "ratelimit>=2.2.0" || echo_warning "批次 3 部分包安装失败"

# 第四批：图像处理包
echo_step "📦 安装批次 4: 图像处理包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "Pillow>=10.0.0" \
    "pillow-heif>=0.13.0" \
    "pytesseract>=0.3.10" || echo_warning "批次 4 部分包安装失败"

# 第五批：数据处理包（小包先装）
echo_step "📦 安装批次 5: 数据处理基础包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "openpyxl>=3.1.0" \
    "cryptography>=41.0.0" \
    "tenacity>=8.2.0" \
    "prettytable>=3.9.0" \
    "qrcode>=7.4.0" \
    "python-dateutil>=2.8.0" || echo_warning "批次 5 部分包安装失败"

# 第六批：系统监控包
echo_step "📦 安装批次 6: 系统监控包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "psutil>=5.9.0" \
    "GPUtil>=1.4.0" \
    "py-cpuinfo>=9.0.0" \
    "celery>=5.3.0" || echo_warning "批次 6 部分包安装失败"

# 第七批：科学计算包（这些包比较大）
echo_step "📦 安装批次 7: 科学计算包 (大包，耐心等待)"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "numpy>=1.26.0" || echo_warning "numpy 安装失败"

pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "pandas>=2.1.0" || echo_warning "pandas 安装失败"

pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "scipy>=1.11.0" || echo_warning "scipy 安装失败"

pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "scikit-learn>=1.3.0" || echo_warning "scikit-learn 安装失败"

# 第八批：可视化包
echo_step "📦 安装批次 8: 可视化包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 120 \
    "matplotlib>=3.7.0" \
    "seaborn>=0.12.0" \
    "xmind>=1.2.0" || echo_warning "批次 8 部分包安装失败"

# 第九批：音频处理包
echo_step "📦 安装批次 9: 音频处理包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "pydub>=0.25.0" || echo_warning "pydub 安装失败"

pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "librosa>=0.10.0" || echo_warning "librosa 安装失败"

# 第十批：计算机视觉包（最大的包）
echo_step "📦 安装批次 10: 计算机视觉包 (最大包，请耐心等待)"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 600 \
    "opencv-python-headless>=4.8.0" || echo_warning "opencv 安装失败"

# 第十一批：自动化测试包
echo_step "📦 安装批次 11: 自动化测试包"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 300 \
    "selenium>=4.15.0" \
    "webdriver-manager>=4.0.0" || echo_warning "批次 11 部分包安装失败"

# 第十二批：OCR 和 AI 包（可选）
echo_step "📦 安装批次 12: OCR 和 AI 包 (可选，失败不影响核心功能)"
pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 600 \
    "easyocr>=1.7.0" || echo_warning "easyocr 安装失败 (可选包)"

pip install -i https://mirrors.aliyun.com/pypi/simple/ --timeout 600 \
    "tensorflow-cpu>=2.15.0" || echo_warning "tensorflow 安装失败 (可选包)"

echo_success "Python 依赖包安装完成"

# 步骤9: 配置环境变量
echo_step "步骤9: 配置环境变量"
cat > "$PROJECT_DIR/.env" << EOF
DEBUG=False
DJANGO_SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
EOF

chown qatoolbox:qatoolbox "$PROJECT_DIR/.env"
echo_success "环境变量配置完成"

# 步骤10: Django 应用配置
echo_step "步骤10: Django 应用配置"
export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

# 检查 Django 配置
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    python manage.py check
"

# 运行数据库迁移
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
echo_step "创建超级用户"
sudo -u qatoolbox -E bash -c "
    cd '$PROJECT_DIR'
    source '$VENV_NAME/bin/activate'
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    echo \"from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')\" | python manage.py shell
"

echo_success "Django 应用配置完成"

# 步骤11: 配置 Gunicorn 服务
echo_step "步骤11: 配置 Gunicorn 系统服务"
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

# 启动 Gunicorn 服务
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox

echo_success "Gunicorn 服务配置完成"

# 步骤12: 配置 Nginx
echo_step "步骤12: 配置 Nginx 反向代理"
cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;

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

# 启用站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
nginx -t

# 启动 Nginx
systemctl enable nginx
systemctl restart nginx

echo_success "Nginx 配置完成"

# 步骤13: 配置防火墙
echo_step "步骤13: 配置防火墙"
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8000

echo_success "防火墙配置完成"

# 步骤14: 配置系统服务自启
echo_step "步骤14: 配置系统服务自启动"
systemctl enable postgresql
systemctl enable redis-server
systemctl enable nginx
systemctl enable qatoolbox

echo_success "系统服务自启动配置完成"

# 步骤15: 最终测试
echo_step "步骤15: 系统部署测试"

# 等待服务启动
sleep 5

# 检查服务状态
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
    echo_warning "HTTP 响应测试失败，检查日志"
fi

# 显示部署信息
echo_step "部署完成！"
echo -e "${GREEN}"
echo "=========================================="
echo "  QAToolBox 部署成功！"
echo "=========================================="
echo "项目目录: $PROJECT_DIR"
echo "虚拟环境: $PROJECT_DIR/$VENV_NAME"
echo "数据库: PostgreSQL ($DB_NAME)"
echo "缓存: Redis"
echo "Web服务器: Nginx + Gunicorn"
echo ""
echo "访问地址:"
echo "  http://$DOMAIN"
echo "  http://www.$DOMAIN"
echo "  http://$SERVER_IP"
echo ""
echo "管理员账户:"
echo "  用户名: admin"
echo "  密码: admin123456"
echo "  登录地址: http://$DOMAIN/admin/"
echo ""
echo "服务管理命令:"
echo "  重启服务: systemctl restart qatoolbox"
echo "  查看日志: journalctl -u qatoolbox -f"
echo "  重启Nginx: systemctl restart nginx"
echo ""
echo "注意事项:"
echo "1. 请在阿里云安全组中开放80和443端口"
echo "2. 如需HTTPS，请配置SSL证书"
echo "3. 请修改默认管理员密码"
echo "=========================================="
echo -e "${NC}"

# 显示服务状态
echo_step "当前服务状态:"
systemctl status qatoolbox --no-pager -l
systemctl status nginx --no-pager -l

echo_success "QAToolBox 部署脚本执行完成！"
