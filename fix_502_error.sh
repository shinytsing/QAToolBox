#!/bin/bash

# =============================================================================
# QAToolBox 502错误快速修复脚本
# 专门解决Nginx 502 Bad Gateway错误
# 适用于已部署但出现502错误的情况
# =============================================================================

set -e

# 配置
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_welcome() {
    clear
    echo -e "${GREEN}"
    echo "========================================"
    echo "    🔧 QAToolBox 502错误快速修复"
    echo "========================================"
    echo "  域名: $DOMAIN"
    echo "  功能: 快速诊断并修复502错误"
    echo "========================================"
    echo -e "${NC}"
}

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "需要root权限运行此脚本"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 诊断服务状态
diagnose_services() {
    echo -e "${BLUE}🔍 诊断服务状态${NC}"
    echo "----------------------------------------"
    
    # 检查Nginx状态
    echo "Nginx状态:"
    if systemctl is-active --quiet nginx; then
        echo -e "  ${GREEN}✓ Nginx运行中${NC}"
    else
        echo -e "  ${RED}✗ Nginx未运行${NC}"
    fi
    
    # 检查应用服务状态
    echo "应用服务状态:"
    if systemctl is-active --quiet $PROJECT_USER; then
        echo -e "  ${GREEN}✓ 应用服务运行中${NC}"
    else
        echo -e "  ${RED}✗ 应用服务未运行${NC}"
    fi
    
    # 检查端口监听
    echo "端口监听状态:"
    if ss -tulpn | grep -q ":8000"; then
        echo -e "  ${GREEN}✓ 端口8000已监听${NC}"
    else
        echo -e "  ${RED}✗ 端口8000未监听${NC}"
    fi
    
    if ss -tulpn | grep -q ":80"; then
        echo -e "  ${GREEN}✓ 端口80已监听${NC}"
    else
        echo -e "  ${RED}✗ 端口80未监听${NC}"
    fi
    
    if ss -tulpn | grep -q ":443"; then
        echo -e "  ${GREEN}✓ 端口443已监听${NC}"
    else
        echo -e "  ${RED}✗ 端口443未监听${NC}"
    fi
    
    echo
}

# 修复应用服务
fix_app_service() {
    log_info "修复应用服务"
    
    # 停止服务
    systemctl stop $PROJECT_USER 2>/dev/null || true
    
    # 杀死残留进程
    pkill -f "gunicorn.*$PROJECT_USER" 2>/dev/null || true
    pkill -f "python.*manage.py" 2>/dev/null || true
    sleep 3
    
    # 检查项目目录
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "项目目录不存在: $PROJECT_DIR"
        return 1
    fi
    
    cd $PROJECT_DIR
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        log_warning "虚拟环境不存在，创建新环境"
        sudo -u $PROJECT_USER python3.9 -m venv .venv
        sudo -u $PROJECT_USER .venv/bin/pip install --upgrade pip
        sudo -u $PROJECT_USER .venv/bin/pip install Django gunicorn psycopg2-binary redis python-dotenv
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        log_warning "环境变量文件不存在，创建默认配置"
        cat > .env << EOF
DB_NAME=$PROJECT_USER
DB_USER=$PROJECT_USER
DB_PASSWORD=QAToolBox@2024
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=$(python3.9 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,$SERVER_IP,localhost,127.0.0.1
REDIS_URL=redis://localhost:6379/0
DJANGO_SETTINGS_MODULE=config.settings.production
EOF
        chown $PROJECT_USER:$PROJECT_USER .env
        chmod 600 .env
    fi
    
    # 测试Django配置
    log_info "测试Django配置"
    if ! sudo -u $PROJECT_USER .venv/bin/python manage.py check --deploy; then
        log_error "Django配置检查失败"
        return 1
    fi
    
    # 重新创建systemd服务
    log_info "更新systemd服务配置"
    cat > /etc/systemd/system/$PROJECT_USER.service << EOF
[Unit]
Description=QAToolBox Django Application
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service

[Service]
Type=exec
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=DJANGO_SETTINGS_MODULE=config.settings.production
Environment=PATH=$PROJECT_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=$PROJECT_DIR/.venv/bin/gunicorn \\
    --bind 127.0.0.1:8000 \\
    --workers 3 \\
    --worker-class sync \\
    --timeout 120 \\
    --keepalive 5 \\
    --max-requests 1000 \\
    --max-requests-jitter 100 \\
    --preload \\
    --access-logfile /var/log/$PROJECT_USER/access.log \\
    --error-logfile /var/log/$PROJECT_USER/error.log \\
    --log-level info \\
    config.wsgi:application

ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建日志目录
    mkdir -p /var/log/$PROJECT_USER
    chown $PROJECT_USER:$PROJECT_USER /var/log/$PROJECT_USER
    
    # 重新加载并启动服务
    systemctl daemon-reload
    systemctl enable $PROJECT_USER
    systemctl start $PROJECT_USER
    
    # 等待服务启动
    sleep 10
    
    if systemctl is-active --quiet $PROJECT_USER; then
        log_success "应用服务修复成功"
        return 0
    else
        log_error "应用服务启动失败"
        echo "错误日志:"
        journalctl -u $PROJECT_USER -n 20 --no-pager
        return 1
    fi
}

# 修复Nginx配置
fix_nginx_config() {
    log_info "修复Nginx配置"
    
    # 备份现有配置
    if [ -f "/etc/nginx/sites-available/$PROJECT_USER" ]; then
        cp "/etc/nginx/sites-available/$PROJECT_USER" "/etc/nginx/sites-available/$PROJECT_USER.backup.$(date +%s)"
    fi
    
    # 创建新的Nginx配置
    cat > /etc/nginx/sites-available/$PROJECT_USER << EOF
upstream ${PROJECT_USER}_backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    server_name $DOMAIN $SERVER_IP;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN $SERVER_IP;
    
    # SSL配置
    ssl_certificate $PROJECT_DIR/ssl/cert.pem;
    ssl_certificate_key $PROJECT_DIR/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    client_max_body_size 100M;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 主应用代理
    location / {
        proxy_pass http://${PROJECT_USER}_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 错误处理
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
    
    # 静态文件
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        access_log off;
    }
    
    # 媒体文件
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        access_log off;
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # favicon
    location /favicon.ico {
        alias $PROJECT_DIR/static/favicon.ico;
        expires 30d;
        access_log off;
    }
}
EOF
    
    # 确保SSL证书存在
    if [ ! -f "$PROJECT_DIR/ssl/cert.pem" ]; then
        log_warning "SSL证书不存在，生成自签名证书"
        mkdir -p $PROJECT_DIR/ssl
        openssl req -x509 -newkey rsa:4096 -keyout $PROJECT_DIR/ssl/key.pem -out $PROJECT_DIR/ssl/cert.pem -days 365 -nodes \
            -subj "/C=CN/ST=Shanghai/L=Shanghai/O=QAToolBox/OU=Production/CN=$DOMAIN"
        chown -R $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/ssl
        chmod 600 $PROJECT_DIR/ssl/key.pem
        chmod 644 $PROJECT_DIR/ssl/cert.pem
    fi
    
    # 启用站点
    ln -sf /etc/nginx/sites-available/$PROJECT_USER /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    if nginx -t; then
        log_success "Nginx配置测试通过"
        systemctl restart nginx
        return 0
    else
        log_error "Nginx配置测试失败"
        return 1
    fi
}

# 检查数据库连接
check_database() {
    log_info "检查数据库连接"
    
    # 检查PostgreSQL服务
    if ! systemctl is-active --quiet postgresql; then
        log_warning "PostgreSQL未运行，尝试启动"
        systemctl start postgresql
        sleep 5
    fi
    
    # 测试数据库连接
    if PGPASSWORD="QAToolBox@2024" psql -h localhost -U $PROJECT_USER -d $PROJECT_USER -c "SELECT 1;" &>/dev/null; then
        log_success "数据库连接正常"
        return 0
    else
        log_error "数据库连接失败"
        return 1
    fi
}

# 检查Redis连接
check_redis() {
    log_info "检查Redis连接"
    
    # 检查Redis服务
    if ! systemctl is-active --quiet redis-server; then
        log_warning "Redis未运行，尝试启动"
        systemctl start redis-server
        sleep 3
    fi
    
    # 测试Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis连接正常"
        return 0
    else
        log_error "Redis连接失败"
        return 1
    fi
}

# 执行连接测试
test_connections() {
    log_info "测试连接"
    
    # 等待服务启动
    sleep 5
    
    # 测试本地应用
    if curl -s -f http://127.0.0.1:8000/health/ > /dev/null; then
        log_success "本地应用连接正常"
    else
        log_error "本地应用连接失败"
        echo "应用日志:"
        journalctl -u $PROJECT_USER -n 10 --no-pager
        return 1
    fi
    
    # 测试Nginx代理
    if curl -s -f -k https://localhost/health/ > /dev/null; then
        log_success "Nginx代理连接正常"
    else
        log_error "Nginx代理连接失败"
        echo "Nginx错误日志:"
        tail -n 10 /var/log/nginx/error.log
        return 1
    fi
    
    return 0
}

# 显示修复结果
show_result() {
    echo
    echo -e "${GREEN}"
    echo "========================================"
    echo "        🎉 修复完成！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${GREEN}访问地址: https://$DOMAIN${NC}"
    echo -e "${GREEN}健康检查: https://$DOMAIN/health/${NC}"
    echo
    echo -e "${BLUE}服务状态检查:${NC}"
    echo -e "  应用服务: $(systemctl is-active $PROJECT_USER)"
    echo -e "  Nginx服务: $(systemctl is-active nginx)"
    echo -e "  PostgreSQL: $(systemctl is-active postgresql)"
    echo -e "  Redis: $(systemctl is-active redis-server)"
    echo
    echo -e "${BLUE}管理命令:${NC}"
    echo -e "  重启应用: ${GREEN}systemctl restart $PROJECT_USER${NC}"
    echo -e "  查看日志: ${GREEN}journalctl -u $PROJECT_USER -f${NC}"
    echo -e "  Nginx日志: ${GREEN}tail -f /var/log/nginx/error.log${NC}"
}

# 主函数
main() {
    show_welcome
    check_root
    
    log_info "开始502错误修复流程..."
    
    # 诊断当前状态
    diagnose_services
    
    # 检查基础服务
    check_database
    check_redis
    
    # 修复应用服务
    if ! fix_app_service; then
        log_error "应用服务修复失败"
        exit 1
    fi
    
    # 修复Nginx配置
    if ! fix_nginx_config; then
        log_error "Nginx配置修复失败"
        exit 1
    fi
    
    # 测试连接
    if test_connections; then
        show_result
    else
        log_error "连接测试失败，请检查日志"
        exit 1
    fi
}

# 错误处理
trap 'log_error "修复过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
