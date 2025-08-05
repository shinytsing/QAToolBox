#!/bin/bash

# QAToolBox 快速部署脚本
# 适用于已经配置好的服务器

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

# 服务器配置
SERVER_IP="47.103.143.152"
SERVER_USER="admin"
PROJECT_PATH="/home/admin/QAToolBox"

# 检查SSH连接
check_ssh() {
    log "检查SSH连接..."
    if ! ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
        echo -e "${RED}无法连接到服务器，请检查：${NC}"
        echo "1. 服务器IP是否正确: $SERVER_IP"
        echo "2. 用户名是否正确: $SERVER_USER"
        echo "3. SSH密钥是否已配置"
        echo "4. 服务器是否可访问"
        exit 1
    fi
}

# 快速部署
quick_deploy() {
    log "开始快速部署..."
    
    # 推送代码到Git
    log "推送代码到Git仓库..."
    git push origin main
    
    # 在服务器上更新代码
    log "在服务器上更新代码..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        git pull origin main
        
        # 激活虚拟环境
        source venv/bin/activate
        
        # 安装依赖
        pip install -r requirements/prod.txt
        
        # 运行迁移
        python manage.py migrate
        
        # 收集静态文件
        python manage.py collectstatic --noinput
        
        # 重启服务
        sudo systemctl restart qatoolbox
        sudo systemctl restart nginx
    "
    
    log "部署完成！"
    log "访问地址: http://$SERVER_IP"
}

# 检查服务状态
check_status() {
    log "检查服务状态..."
    ssh $SERVER_USER@$SERVER_IP "
        echo '=== Gunicorn Status ==='
        sudo systemctl status qatoolbox --no-pager
        
        echo '=== Nginx Status ==='
        sudo systemctl status nginx --no-pager
        
        echo '=== 应用响应检查 ==='
        curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/ || echo 'Failed'
    "
}

# 查看日志
show_logs() {
    log "查看最新日志..."
    ssh $SERVER_USER@$SERVER_IP "
        echo '=== Gunicorn 最新日志 ==='
        sudo journalctl -u qatoolbox -n 20 --no-pager
        
        echo '=== Nginx 错误日志 ==='
        sudo tail -n 10 /var/log/nginx/error.log
    "
}

# 主函数
main() {
    case "${1:-deploy}" in
        "deploy")
            check_ssh
            quick_deploy
            ;;
        "status")
            check_ssh
            check_status
            ;;
        "logs")
            check_ssh
            show_logs
            ;;
        "help")
            echo "用法: $0 [deploy|status|logs|help]"
            echo "  deploy - 快速部署（默认）"
            echo "  status - 检查服务状态"
            echo "  logs   - 查看服务日志"
            echo "  help   - 显示帮助信息"
            ;;
        *)
            echo "未知命令: $1"
            echo "使用 '$0 help' 查看帮助"
            exit 1
            ;;
    esac
}

main "$@" 