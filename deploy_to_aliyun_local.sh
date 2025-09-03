#!/bin/bash

# QAToolBox 阿里云部署脚本 - 本地执行版本
# 此脚本将代码上传到服务器并执行部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# 服务器配置
SERVER_IP="47.103.143.152"
SERVER_USER="admin"
SERVER_DIR="/var/www/qatoolbox"
DOMAIN="shenyiqing.xin"

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox 阿里云部署脚本
========================================
✨ 功能:
  • 上传代码到服务器
  • 执行完整部署
  • 配置所有服务
  • 启动应用
========================================
EOF
echo -e "${NC}"

# 检查本地环境
check_local_environment() {
    echo -e "${BLUE}🔍 检查本地环境...${NC}"
    
    # 检查必要工具
    local tools=("rsync" "ssh" "curl")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${RED}❌ 缺少必要工具: $tool${NC}"
            exit 1
        fi
    done
    
    # 检查项目文件
    if [ ! -f "manage.py" ]; then
        echo -e "${RED}❌ 请在项目根目录执行此脚本${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 本地环境检查通过${NC}"
}

# 上传代码到服务器
upload_code() {
    echo -e "${BLUE}📤 上传代码到服务器...${NC}"
    
    # 创建服务器目录
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "sudo mkdir -p $SERVER_DIR && sudo chown $SERVER_USER:$SERVER_USER $SERVER_DIR" || {
        echo -e "${YELLOW}⚠️ 无法创建服务器目录，请检查SSH连接${NC}"
        echo -e "${YELLOW}💡 建议通过阿里云控制台手动连接服务器${NC}"
        return 1
    }
    
    # 上传代码
    echo -e "${YELLOW}📦 同步代码文件...${NC}"
    rsync -avz --progress \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.venv' \
        --exclude='node_modules' \
        --exclude='.DS_Store' \
        --exclude='*.log' \
        ./ "$SERVER_USER@$SERVER_IP:$SERVER_DIR/"
    
    echo -e "${GREEN}✅ 代码上传完成${NC}"
}

# 在服务器上执行部署
deploy_on_server() {
    echo -e "${BLUE}🔧 在服务器上执行部署...${NC}"
    
    # 执行部署脚本
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << EOF
        cd $SERVER_DIR
        
        # 检查是否有部署脚本
        if [ -f "deploy_aliyun_complete.sh" ]; then
            echo "使用完整部署脚本..."
            chmod +x deploy_aliyun_complete.sh
            sudo ./deploy_aliyun_complete.sh
        elif [ -f "one_click_deploy.sh" ]; then
            echo "使用一键部署脚本..."
            chmod +x one_click_deploy.sh
            sudo ./one_click_deploy.sh
        else
            echo "执行基础部署..."
            # 基础部署步骤
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv postgresql redis-server nginx supervisor
            
            # 创建虚拟环境
            python3 -m venv .venv
            source .venv/bin/activate
            
            # 安装依赖
            pip install -r requirements.txt
            
            # 运行迁移
            python manage.py migrate --settings=config.settings.aliyun_production
            
            # 收集静态文件
            python manage.py collectstatic --noinput --settings=config.settings.aliyun_production
            
            # 创建超级用户
            python manage.py shell --settings=config.settings.aliyun_production -c "
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@$DOMAIN', 'admin123456')
                print('超级用户已创建: admin/admin123456')
            "
        fi
EOF
    
    echo -e "${GREEN}✅ 服务器部署完成${NC}"
}

# 配置服务
configure_services() {
    echo -e "${BLUE}⚙️ 配置服务器服务...${NC}"
    
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << EOF
        cd $SERVER_DIR
        
        # 创建Nginx配置
        sudo tee /etc/nginx/sites-available/qatoolbox > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias $SERVER_DIR/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias $SERVER_DIR/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF
        
        # 启用站点
        sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t
        
        # 创建Supervisor配置
        sudo tee /etc/supervisor/conf.d/qatoolbox.conf > /dev/null << 'SUPERVISOR_EOF'
[program:qatoolbox]
command=$SERVER_DIR/.venv/bin/gunicorn wsgi:application --bind 127.0.0.1:8000 --workers 4
directory=$SERVER_DIR
user=$SERVER_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox.log
stderr_logfile=/var/log/qatoolbox_error.log
environment=DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
SUPERVISOR_EOF
        
        # 启动服务
        sudo supervisorctl reread
        sudo supervisorctl update
        sudo supervisorctl start qatoolbox
        sudo systemctl restart nginx
        sudo systemctl enable nginx
EOF
    
    echo -e "${GREEN}✅ 服务配置完成${NC}"
}

# 验证部署
verify_deployment() {
    echo -e "${BLUE}🔍 验证部署结果...${NC}"
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << EOF
        echo "=== 服务状态 ==="
        sudo supervisorctl status qatoolbox
        sudo systemctl status nginx --no-pager -l
        sudo systemctl status postgresql --no-pager -l
        sudo systemctl status redis-server --no-pager -l
        
        echo "=== 端口监听 ==="
        sudo netstat -tlnp | grep -E ':(80|8000|5432|6379)'
        
        echo "=== 测试HTTP访问 ==="
        curl -I http://localhost/ || echo "HTTP访问测试失败"
EOF
    
    # 测试外部访问
    echo -e "${YELLOW}🌐 测试外部访问...${NC}"
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "http://$SERVER_IP/" || echo "000")
    
    if [[ "$http_status" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✅ 外部访问正常 (状态码: $http_status)${NC}"
    else
        echo -e "${YELLOW}⚠️ 外部访问异常 (状态码: $http_status)${NC}"
    fi
}

# 显示部署信息
show_deployment_info() {
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 部署完成！
========================================

🌐 访问信息:
  主站地址: http://$SERVER_IP/
  域名访问: http://$DOMAIN/ (需要配置DNS)
  管理后台: http://$SERVER_IP/admin/

👤 管理员账户:
  用户名: admin
  密码: admin123456

🔧 管理命令:
  ssh $SERVER_USER@$SERVER_IP
  cd $SERVER_DIR
  sudo supervisorctl restart qatoolbox
  sudo systemctl restart nginx

📊 服务状态:
  sudo supervisorctl status qatoolbox
  sudo systemctl status nginx

📁 重要目录:
  项目目录: $SERVER_DIR
  日志文件: /var/log/qatoolbox.log
  Nginx配置: /etc/nginx/sites-available/qatoolbox

🔒 下一步建议:
  1. 配置域名DNS解析指向 $SERVER_IP
  2. 申请SSL证书: sudo certbot --nginx -d $DOMAIN
  3. 修改默认密码
  4. 配置邮件服务

========================================
EOF
    echo -e "${NC}"
}

# 主执行流程
main() {
    echo -e "${BLUE}🚀 开始QAToolBox阿里云部署...${NC}"
    echo ""
    
    check_local_environment
    
    if upload_code; then
        deploy_on_server
        configure_services
        verify_deployment
        show_deployment_info
    else
        echo -e "${RED}❌ 代码上传失败，请检查SSH连接${NC}"
        echo -e "${YELLOW}💡 建议通过阿里云控制台手动连接服务器执行部署${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}🎉 部署流程完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
