#!/bin/bash
# =============================================================================
# QAToolBox Python 3.12 优化部署脚本
# =============================================================================
# 专为Python 3.12优化，利用新特性提升性能
# 支持Ubuntu 24.04+ 和 CentOS/RHEL 8+
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# 配置变量
readonly PROJECT_USER="${PROJECT_USER:-qatoolbox}"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly PYTHON_VERSION="3.12"
readonly VENV_NAME="venv_py312"

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_py312_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox Python 3.12 优化部署
========================================
✨ 特性:
  • Python 3.12 完全支持
  • 利用新特性提升性能
  • 优化的依赖管理
  • 现代化的部署流程
  • 完整的监控和日志
========================================
EOF
echo -e "${NC}"

# 检查系统
check_system() {
    echo -e "${BLUE}🔍 检查系统环境...${NC}"
    
    # 检查操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo -e "   操作系统: $PRETTY_NAME"
        echo -e "   版本: $VERSION"
    fi
    
    # 检查Python版本
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        echo -e "   ✅ Python 3.12 已安装"
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION_CHECK=$(python3 --version 2>&1 | grep -o '3\.[0-9]\+')
        if [[ "$PYTHON_VERSION_CHECK" == "3.12" ]]; then
            PYTHON_CMD="python3"
            echo -e "   ✅ Python 3.12 已安装"
        else
            echo -e "   ❌ 需要 Python 3.12，当前版本: $PYTHON_VERSION_CHECK"
            exit 1
        fi
    else
        echo -e "   ❌ Python 3 未安装"
        exit 1
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        echo -e "   ✅ pip3 已安装"
    else
        echo -e "   ❌ pip3 未安装"
        exit 1
    fi
}

# 创建项目用户
create_project_user() {
    echo -e "${BLUE}👤 创建项目用户...${NC}"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        echo -e "   ✅ 用户 $PROJECT_USER 创建成功"
    else
        echo -e "   ℹ️ 用户 $PROJECT_USER 已存在"
    fi
    
    # 添加到sudo组
    usermod -aG sudo "$PROJECT_USER"
    echo -e "   ✅ 用户已添加到sudo组"
}

# 安装系统依赖
install_system_dependencies() {
    echo -e "${BLUE}📦 安装系统依赖...${NC}"
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y \
            python3.12-venv \
            python3.12-dev \
            python3-pip \
            build-essential \
            libpq-dev \
            libmysqlclient-dev \
            libsqlite3-dev \
            libjpeg-dev \
            libpng-dev \
            libfreetype6-dev \
            libssl-dev \
            libffi-dev \
            curl \
            git \
            nginx \
            redis-server \
            postgresql \
            postgresql-contrib
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum update -y
        yum groupinstall -y "Development Tools"
        yum install -y \
            python3-devel \
            python3-pip \
            postgresql-devel \
            mysql-devel \
            sqlite-devel \
            libjpeg-devel \
            libpng-devel \
            freetype-devel \
            openssl-devel \
            libffi-devel \
            curl \
            git \
            nginx \
            redis \
            postgresql \
            postgresql-server
    else
        echo -e "   ❌ 不支持的包管理器"
        exit 1
    fi
    
    echo -e "   ✅ 系统依赖安装完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    echo -e "${BLUE}🐍 创建Python虚拟环境...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 创建虚拟环境
    $PYTHON_CMD -m venv "$VENV_NAME"
    echo -e "   ✅ 虚拟环境创建成功: $VENV_NAME"
    
    # 激活虚拟环境
    source "$VENV_NAME/bin/activate"
    
    # 升级pip和setuptools
    pip install --upgrade pip setuptools wheel
    echo -e "   ✅ pip 升级完成"
    
    # 安装基础依赖
    pip install -r requirements/base.txt
    echo -e "   ✅ 基础依赖安装完成"
}

# 安装项目依赖
install_project_dependencies() {
    echo -e "${BLUE}📚 安装项目依赖...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 安装开发依赖
    if [ -f "requirements/development.txt" ]; then
        pip install -r requirements/development.txt
        echo -e "   ✅ 开发依赖安装完成"
    fi
    
    # 安装可选依赖
    if [ -f "requirements/optional.txt" ]; then
        pip install -r requirements/optional.txt
        echo -e "   ✅ 可选依赖安装完成"
    fi
    
    # 安装测试依赖
    if [ -f "requirements/testing.txt" ]; then
        pip install -r requirements/testing.txt
        echo -e "   ✅ 测试依赖安装完成"
    fi
}

# 配置环境变量
configure_environment() {
    echo -e "${BLUE}⚙️ 配置环境变量...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 创建.env文件
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# QAToolBox 环境配置
DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
ALLOWED_HOSTS=localhost,127.0.0.1,*

# 数据库配置
DATABASE_URL=sqlite:///db.sqlite3

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 静态文件配置
STATIC_ROOT=/home/$PROJECT_USER/QAToolBox/staticfiles
MEDIA_ROOT=/home/$PROJECT_USER/QAToolBox/media

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/home/$PROJECT_USER/QAToolBox/logs/django.log

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1
EOF
        echo -e "   ✅ .env 文件创建完成"
    else
        echo -e "   ℹ️ .env 文件已存在"
    fi
}

# 运行数据库迁移
run_migrations() {
    echo -e "${BLUE}🗄️ 运行数据库迁移...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 创建必要目录
    mkdir -p logs media staticfiles
    
    # 运行迁移
    python manage.py makemigrations
    python manage.py migrate
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    echo -e "   ✅ 数据库迁移完成"
}

# 创建服务文件
create_service_files() {
    echo -e "${BLUE}🔧 创建服务文件...${NC}"
    
    # Django Gunicorn服务
    cat > /etc/systemd/system/qatoolbox.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=notify
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/gunicorn --workers 4 --bind unix:$PROJECT_DIR/qatoolbox.sock config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Celery服务
    cat > /etc/systemd/system/qatoolbox-celery.service << EOF
[Unit]
Description=QAToolBox Celery Worker
After=network.target

[Service]
Type=forking
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/celery multi start worker1 -A QAToolBox -l info
ExecStop=$PROJECT_DIR/$VENV_NAME/bin/celery multi stopwait worker1 -A QAToolBox
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Celery Beat服务
    cat > /etc/systemd/system/qatoolbox-celerybeat.service << EOF
[Unit]
Description=QAToolBox Celery Beat
After=network.target

[Service]
Type=simple
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/$VENV_NAME/bin
ExecStart=$PROJECT_DIR/$VENV_NAME/bin/celery -A QAToolBox beat -l info
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    echo -e "   ✅ 服务文件创建完成"
}

# 配置Nginx
configure_nginx() {
    echo -e "${BLUE}🌐 配置Nginx...${NC}"
    
    # 创建Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location /static/ {
        alias /home/$PROJECT_USER/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /home/$PROJECT_USER/QAToolBox/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/$PROJECT_USER/QAToolBox/qatoolbox.sock;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # 启用站点
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    
    # 测试配置
    nginx -t
    
    echo -e "   ✅ Nginx配置完成"
}

# 启动服务
start_services() {
    echo -e "${BLUE}🚀 启动服务...${NC}"
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启动服务
    systemctl enable qatoolbox
    systemctl start qatoolbox
    
    systemctl enable qatoolbox-celery
    systemctl start qatoolbox-celery
    
    systemctl enable qatoolbox-celerybeat
    systemctl start qatoolbox-celerybeat
    
    # 重启Nginx
    systemctl restart nginx
    
    echo -e "   ✅ 所有服务启动完成"
}

# 运行兼容性检查
run_compatibility_check() {
    echo -e "${BLUE}🔍 运行兼容性检查...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 运行Python 3.12兼容性检查
    if [ -f "check_python312_compatibility.py" ]; then
        python check_python312_compatibility.py
    fi
    
    # Django检查
    python manage.py check --deploy
    
    echo -e "   ✅ 兼容性检查完成"
}

# 显示部署信息
show_deployment_info() {
    echo -e "${GREEN}${BOLD}"
    cat << EOF
========================================
🎉 QAToolBox Python 3.12 部署完成！
========================================

📋 部署信息:
   • 项目目录: $PROJECT_DIR
   • 虚拟环境: $PROJECT_DIR/$VENV_NAME
   • Python版本: $PYTHON_VERSION
   • 用户: $PROJECT_USER

🌐 访问信息:
   • 网站: http://$(hostname -I | awk '{print $1}')
   • 管理后台: http://$(hostname -I | awk '{print $1}')/admin/

🔧 服务状态:
   • Django: systemctl status qatoolbox
   • Celery: systemctl status qatoolbox-celery
   • Nginx: systemctl status nginx

📝 日志文件:
   • Django: $PROJECT_DIR/logs/django.log
   • 部署: $LOG_FILE

💡 下一步:
   • 创建超级用户: python manage.py createsuperuser
   • 配置域名和SSL证书
   • 设置监控和备份
   • 配置防火墙规则

========================================
EOF
    echo -e "${NC}"
}

# 主函数
main() {
    echo -e "${CYAN}🚀 开始部署 QAToolBox (Python 3.12)...${NC}"
    
    check_system
    create_project_user
    install_system_dependencies
    create_virtual_environment
    install_project_dependencies
    configure_environment
    run_migrations
    create_service_files
    configure_nginx
    start_services
    run_compatibility_check
    show_deployment_info
    
    echo -e "${GREEN}✅ 部署完成！详细日志请查看: $LOG_FILE${NC}"
}

# 运行主函数
main "$@"
