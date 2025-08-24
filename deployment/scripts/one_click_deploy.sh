#!/bin/bash

# QAToolBox 一键部署脚本
# 支持CentOS/Ubuntu/Debian系统
# 服务器: 47.103.143.152 (shenyiqing.xin)

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
PROJECT_NAME="QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"
GIT_REPO="https://github.com/shinytsing/QAToolbox.git"
INSTALL_DIR="/opt/QAToolbox"

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VER=$(lsb_release -sr)
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    
    case $OS in
        centos|rhel|rocky|almalinux)
            PKG_MANAGER="yum"
            if command -v dnf >/dev/null 2>&1; then
                PKG_MANAGER="dnf"
            fi
            ;;
        ubuntu|debian)
            PKG_MANAGER="apt"
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
    
    log_info "检测到操作系统: $OS $VER，包管理器: $PKG_MANAGER"
}

# 修复CentOS 8源问题
fix_centos8_repos() {
    if [[ "$OS" == "centos" && "$VER" == "8" ]]; then
        log_warn "检测到CentOS 8，修复源配置..."
        sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
        sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
    fi
}

# 更新系统
update_system() {
    log_step "更新系统包..."
    case $PKG_MANAGER in
        yum|dnf)
            fix_centos8_repos
            $PKG_MANAGER clean all
            $PKG_MANAGER update -y
            ;;
        apt)
            apt update
            apt upgrade -y
            ;;
    esac
}

# 安装基础软件
install_basics() {
    log_step "安装基础软件..."
    case $PKG_MANAGER in
        yum|dnf)
            $PKG_MANAGER install -y curl wget git unzip vim htop net-tools
            ;;
        apt)
            apt install -y curl wget git unzip vim htop net-tools
            ;;
    esac
}

# 创建用户
create_user() {
    log_step "创建部署用户..."
    if ! id "qatoolbox" &>/dev/null; then
        useradd -m -s /bin/bash qatoolbox
        echo "qatoolbox:qatoolbox123" | chpasswd
        log_info "用户qatoolbox已创建，密码: qatoolbox123"
        
        # 添加sudo权限
        case $PKG_MANAGER in
            yum|dnf)
                usermod -aG wheel qatoolbox
                ;;
            apt)
                usermod -aG sudo qatoolbox
                ;;
        esac
    else
        log_info "用户qatoolbox已存在"
    fi
}

# 安装Docker
install_docker() {
    log_step "安装Docker..."
    if ! command -v docker >/dev/null 2>&1; then
        case $PKG_MANAGER in
            yum|dnf)
                $PKG_MANAGER install -y yum-utils device-mapper-persistent-data lvm2
                yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
                $PKG_MANAGER install -y docker-ce docker-ce-cli containerd.io
                ;;
            apt)
                apt install -y apt-transport-https ca-certificates gnupg lsb-release
                curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
                apt update
                apt install -y docker-ce docker-ce-cli containerd.io
                ;;
        esac
        
        systemctl start docker
        systemctl enable docker
        usermod -aG docker qatoolbox
        log_info "Docker安装完成"
    else
        log_info "Docker已安装"
    fi
}

# 安装Docker Compose
install_docker_compose() {
    log_step "安装Docker Compose..."
    if ! command -v docker-compose >/dev/null 2>&1; then
        curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        log_info "Docker Compose安装完成"
    else
        log_info "Docker Compose已安装"
    fi
}

# 配置防火墙
configure_firewall() {
    log_step "配置防火墙..."
    case $PKG_MANAGER in
        yum|dnf)
            if command -v firewall-cmd >/dev/null 2>&1; then
                systemctl start firewalld 2>/dev/null || true
                systemctl enable firewalld 2>/dev/null || true
                firewall-cmd --permanent --add-service=ssh 2>/dev/null || true
                firewall-cmd --permanent --add-service=http 2>/dev/null || true
                firewall-cmd --permanent --add-service=https 2>/dev/null || true
                firewall-cmd --permanent --add-port=8000/tcp 2>/dev/null || true
                firewall-cmd --reload 2>/dev/null || true
            fi
            ;;
        apt)
            if command -v ufw >/dev/null 2>&1; then
                ufw --force enable
                ufw allow ssh
                ufw allow http
                ufw allow https
                ufw allow 8000/tcp
            fi
            ;;
    esac
    log_info "防火墙配置完成"
}

# 克隆项目
clone_project() {
    log_step "获取项目代码..."
    mkdir -p $INSTALL_DIR
    chown -R qatoolbox:qatoolbox $INSTALL_DIR
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        log_warn "项目目录已存在，正在更新..."
        cd $INSTALL_DIR
        sudo -u qatoolbox git pull origin main
    else
        sudo -u qatoolbox git clone $GIT_REPO $INSTALL_DIR
    fi
    
    cd $INSTALL_DIR
    chown -R qatoolbox:qatoolbox $INSTALL_DIR
}

# 生成环境配置
generate_env() {
    log_step "生成环境配置..."
    
    # 生成随机密钥
    DJANGO_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || openssl rand -base64 50)
    DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    cat > $INSTALL_DIR/.env << EOF
# Django配置
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},${SERVER_IP},localhost

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=${DB_PASS}
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://\${DB_USER}:\${DB_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME}

# Redis配置
REDIS_URL=redis://redis:6379/0

# AI API配置（已预配置可用的密钥）
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
OPENAI_API_KEY=
CLAUDE_API_KEY=
GEMINI_API_KEY=

# 搜索和地图API配置（已预配置可用的密钥）
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e

# 天气API配置
OPENWEATHER_API_KEY=

# 图片API配置
PEXELS_API_KEY=
PIXABAY_API_KEY=
UNSPLASH_ACCESS_KEY=

# 社交媒体API配置
XIAOHONGSHU_API_KEY=
DOUYIN_API_KEY=
NETEASE_API_KEY=
WEIBO_API_KEY=
BILIBILI_API_KEY=
ZHIHU_API_KEY=

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@${DOMAIN}

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@${DOMAIN}
ADMIN_PASSWORD=admin123456

# 文件上传配置
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
MAX_UPLOAD_SIZE=104857600

# 缓存配置
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379/1

# 会话配置
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default
SESSION_COOKIE_AGE=1209600

# Celery配置
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=False
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=Asia/Shanghai

# API限制配置
API_RATE_LIMIT_ANON=1000
API_RATE_LIMIT_USER=10000
API_RATE_LIMIT=10/minute

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_PROXY_SSL_HEADER=
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# 静态文件配置
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# CORS配置
CORS_ALLOWED_ORIGINS=http://${DOMAIN},https://${DOMAIN},http://www.${DOMAIN},https://www.${DOMAIN},http://${SERVER_IP}
CORS_ALLOW_CREDENTIALS=True

# 开发工具配置（生产环境关闭）
DEBUG_TOOLBAR=False
INTERNAL_IPS=127.0.0.1,localhost
EOF

    chown qatoolbox:qatoolbox $INSTALL_DIR/.env
    log_info "环境配置已生成"
    log_info "数据库密码: ${DB_PASS}"
}

# 构建和启动服务
deploy_services() {
    log_step "构建和启动服务..."
    cd $INSTALL_DIR
    
    # 创建日志目录
    mkdir -p logs
    chown -R qatoolbox:qatoolbox logs
    
    # 构建镜像
    docker-compose -f deployment/configs/docker-compose.yml build
    
    # 启动服务
    docker-compose -f deployment/configs/docker-compose.yml up -d
    
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    docker-compose -f deployment/configs/docker-compose.yml ps
}

# 健康检查
health_check() {
    log_step "执行健康检查..."
    
    local retries=0
    local max_retries=10
    
    while [ $retries -lt $max_retries ]; do
        if curl -f http://localhost:8000/tools/health/ >/dev/null 2>&1; then
            log_info "✅ 健康检查通过！"
            return 0
        fi
        
        retries=$((retries + 1))
        log_warn "健康检查失败，重试 $retries/$max_retries..."
        sleep 10
    done
    
    log_error "健康检查失败，请检查服务状态"
    return 1
}

# 显示部署信息
show_info() {
    echo ""
    log_info "=== 🎉 QAToolBox 部署完成！ ==="
    echo ""
    log_info "📍 访问地址："
    log_info "   - HTTP: http://${SERVER_IP}"
    log_info "   - HTTP: http://${DOMAIN}"
    log_info "   - 管理后台: http://${DOMAIN}/admin/"
    echo ""
    log_info "👤 系统用户："
    log_info "   - 用户名: qatoolbox"
    log_info "   - 密码: qatoolbox123"
    echo ""
    log_info "👤 Django管理员："
    log_info "   - 用户名: admin"
    log_info "   - 密码: admin123456"
    echo ""
    log_info "🛠️ 服务管理："
    log_info "   cd ${INSTALL_DIR}"
    log_info "   ./deployment/scripts/manage.sh {start|stop|restart|logs|status|update|backup|ssl}"
    echo ""
    log_warn "⚠️ 重要提醒："
    log_warn "1. 请立即修改默认密码"
    log_warn "2. 配置SSL证书: ./deployment/scripts/manage.sh ssl"
    log_warn "3. 定期备份数据"
    log_warn "4. 查看完整文档: ${INSTALL_DIR}/deployment/docs/"
}

# 主函数
main() {
    log_info "开始 QAToolBox 一键部署..."
    log_info "目标服务器: ${SERVER_IP} (${DOMAIN})"
    echo ""
    
    detect_os
    update_system
    install_basics
    create_user
    install_docker
    install_docker_compose
    configure_firewall
    clone_project
    generate_env
    deploy_services
    
    if health_check; then
        show_info
    else
        log_error "部署过程中出现问题，请检查日志"
        exit 1
    fi
}

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
    log_error "请使用root用户运行此脚本"
    log_info "使用方法: sudo $0"
    exit 1
fi

# 执行主函数
main "$@"
