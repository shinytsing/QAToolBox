#!/bin/bash

# QAToolBox 阿里云服务器部署脚本
# 服务器信息：
# IP: 47.103.143.152
# 用户: admin@172.24.33.31

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# 服务器配置
SERVER_IP="47.103.143.152"
SERVER_USER="admin"
SERVER_PORT="22"
PROJECT_NAME="QAToolBox"
PROJECT_PATH="/home/admin/QAToolBox"
GIT_REPO="https://github.com/shinytsing/QAToolbox.git"

# 检查本地Git状态
check_git_status() {
    log "检查本地Git状态..."
    
    if ! git status --porcelain | grep -q .; then
        log "本地没有未提交的更改"
    else
        warn "本地有未提交的更改，请先提交或暂存"
        git status --short
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "部署已取消"
            exit 1
        fi
    fi
}

# 推送代码到远程仓库
push_to_remote() {
    log "推送代码到远程仓库..."
    
    if git push origin main; then
        log "代码推送成功"
    else
        error "代码推送失败"
        exit 1
    fi
}

# 连接到服务器并执行命令
run_on_server() {
    local command="$1"
    log "在服务器上执行: $command"
    
    ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP "$command"
}

# 复制文件到服务器
copy_to_server() {
    local local_file="$1"
    local remote_path="$2"
    
    log "复制 $local_file 到服务器..."
    scp -P $SERVER_PORT "$local_file" "$SERVER_USER@$SERVER_IP:$remote_path"
}

# 在服务器上安装依赖
install_server_dependencies() {
    log "在服务器上安装系统依赖..."
    
    run_on_server "
        # 更新系统包
        sudo apt update
        
        # 安装Python和相关工具
        sudo apt install -y python3 python3-pip python3-venv python3-dev
        
        # 安装PostgreSQL
        sudo apt install -y postgresql postgresql-contrib libpq-dev
        
        # 安装Redis
        sudo apt install -y redis-server
        
        # 安装Nginx
        sudo apt install -y nginx
        
        # 安装其他必要工具
        sudo apt install -y git curl wget unzip build-essential
        
        # 启动并启用服务
        sudo systemctl enable postgresql
        sudo systemctl enable redis-server
        sudo systemctl enable nginx
        
        sudo systemctl start postgresql
        sudo systemctl start redis-server
        sudo systemctl start nginx
    "
}

# 配置PostgreSQL数据库
setup_database() {
    log "配置PostgreSQL数据库..."
    
    run_on_server "
        # 创建数据库用户和数据库
        sudo -u postgres psql -c \"CREATE USER qatoolbox WITH PASSWORD 'qatoolbox123456';\" || true
        sudo -u postgres psql -c \"CREATE DATABASE qatoolbox OWNER qatoolbox;\" || true
        sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;\" || true
        
        # 配置PostgreSQL允许本地连接
        sudo sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/'\" /etc/postgresql/*/main/postgresql.conf
        sudo systemctl restart postgresql
    "
}

# 配置Nginx
setup_nginx() {
    log "配置Nginx..."
    
    # 创建Nginx配置文件
    cat > nginx_qatoolbox.conf << 'EOF'
server {
    listen 80;
    server_name 47.103.143.152;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 47.103.143.152;
    
    # SSL配置（需要先配置SSL证书）
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;
    
    # 临时禁用SSL重定向
    # ssl_protocols TLSv1.2 TLSv1.3;
    # ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    # ssl_prefer_server_ciphers off;
    
    # 客户端最大上传大小
    client_max_body_size 50M;
    
    # 静态文件
    location /static/ {
        alias /home/admin/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolBox/media/;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # 代理到Django应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
}
EOF
    
    # 复制配置文件到服务器
    copy_to_server "nginx_qatoolbox.conf" "/tmp/"
    
    # 在服务器上配置Nginx
    run_on_server "
        sudo mv /tmp/nginx_qatoolbox.conf /etc/nginx/sites-available/qatoolbox
        sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t
        sudo systemctl reload nginx
    "
    
    # 清理本地临时文件
    rm nginx_qatoolbox.conf
}

# 创建Gunicorn服务文件
setup_gunicorn_service() {
    log "配置Gunicorn服务..."
    
    # 创建systemd服务文件
    cat > qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Gunicorn daemon
After=network.target

[Service]
User=admin
Group=admin
WorkingDirectory=/home/admin/QAToolBox
Environment="PATH=/home/admin/QAToolBox/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.production"
ExecStart=/home/admin/QAToolBox/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
    
    # 复制服务文件到服务器
    copy_to_server "qatoolbox.service" "/tmp/"
    
    # 在服务器上配置服务
    run_on_server "
        sudo mv /tmp/qatoolbox.service /etc/systemd/system/
        sudo systemctl daemon-reload
        sudo systemctl enable qatoolbox
    "
    
    # 清理本地临时文件
    rm qatoolbox.service
}

# 部署项目代码
deploy_project() {
    log "部署项目代码..."
    
    run_on_server "
        # 创建项目目录
        mkdir -p $PROJECT_PATH
        
        # 如果目录已存在，备份当前版本
        if [ -d \"$PROJECT_PATH/.git\" ]; then
            cd $PROJECT_PATH
            git stash
            git pull origin main
        else
            cd $PROJECT_PATH
            git clone $GIT_REPO .
        fi
        
        # 创建虚拟环境
        python3 -m venv venv
        source venv/bin/activate
        
        # 安装Python依赖
        pip install --upgrade pip
        pip install -r requirements/prod.txt
        
        # 设置环境变量
        export DJANGO_SETTINGS_MODULE=config.settings.production
        export DB_NAME=qatoolbox
        export DB_USER=qatoolbox
        export DB_PASSWORD=qatoolbox123456
        export DB_HOST=localhost
        export DB_PORT=5432
        export REDIS_URL=redis://localhost:6379/1
        
        # 运行数据库迁移
        python manage.py migrate
        
        # 收集静态文件
        python manage.py collectstatic --noinput
        
        # 创建超级用户（如果不存在）
        echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'admin123456')\" | python manage.py shell
        
        # 设置文件权限
        chmod +x manage.py
        chmod +x deploy.py
    "
}

# 启动服务
start_services() {
    log "启动服务..."
    
    run_on_server "
        # 启动Gunicorn服务
        sudo systemctl start qatoolbox
        sudo systemctl status qatoolbox
        
        # 检查服务状态
        echo '=== Gunicorn Status ==='
        sudo systemctl status qatoolbox --no-pager
        
        echo '=== Nginx Status ==='
        sudo systemctl status nginx --no-pager
        
        echo '=== PostgreSQL Status ==='
        sudo systemctl status postgresql --no-pager
        
        echo '=== Redis Status ==='
        sudo systemctl status redis-server --no-pager
    "
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    # 等待服务启动
    sleep 10
    
    # 检查服务是否响应
    if curl -f http://47.103.143.152/health/ > /dev/null 2>&1; then
        log "✅ 健康检查通过！应用已成功部署"
        log "🌐 访问地址: http://47.103.143.152"
    else
        warn "⚠️  健康检查失败，请检查服务状态"
        run_on_server "
            echo '=== 查看Gunicorn日志 ==='
            sudo journalctl -u qatoolbox -n 20 --no-pager
            
            echo '=== 查看Nginx日志 ==='
            sudo tail -n 20 /var/log/nginx/error.log
        "
    fi
}

# 显示部署信息
show_deployment_info() {
    log "部署完成！"
    echo
    echo "=========================================="
    echo "           QAToolBox 部署信息"
    echo "=========================================="
    echo "服务器IP: 47.103.143.152"
    echo "项目路径: $PROJECT_PATH"
    echo "访问地址: http://47.103.143.152"
    echo "管理员账号: admin"
    echo "管理员密码: admin123456"
    echo "数据库: PostgreSQL (qatoolbox)"
    echo "缓存: Redis"
    echo "Web服务器: Nginx + Gunicorn"
    echo "=========================================="
    echo
    echo "常用命令："
    echo "  查看服务状态: ssh $SERVER_USER@$SERVER_IP 'sudo systemctl status qatoolbox'"
    echo "  重启服务: ssh $SERVER_USER@$SERVER_IP 'sudo systemctl restart qatoolbox'"
    echo "  查看日志: ssh $SERVER_USER@$SERVER_IP 'sudo journalctl -u qatoolbox -f'"
    echo "  进入项目目录: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH'"
    echo
}

# 主部署流程
main() {
    log "开始部署QAToolBox到阿里云服务器..."
    
    # 检查本地Git状态
    check_git_status
    
    # 推送代码到远程仓库
    push_to_remote
    
    # 在服务器上安装依赖
    install_server_dependencies
    
    # 配置数据库
    setup_database
    
    # 配置Nginx
    setup_nginx
    
    # 配置Gunicorn服务
    setup_gunicorn_service
    
    # 部署项目代码
    deploy_project
    
    # 启动服务
    start_services
    
    # 健康检查
    health_check
    
    # 显示部署信息
    show_deployment_info
}

# 执行主函数
main "$@" 