#!/bin/bash

# QAToolBox 一键部署入口脚本
# 支持多种部署方式：本地开发、生产环境、Docker部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_banner() {
    echo -e "${BLUE}"
    echo "  ___    _    _____           _ ____            "
    echo " / _ \  / \  |_   _|__   ___ | | __ )  _____  __"
    echo "| | | |/ _ \   | |/ _ \ / _ \| |  _ \ / _ \ \/ /"
    echo "| |_| / ___ \  | | (_) | (_) | | |_) | (_) >  < "
    echo " \__\_\_/   \_\ |_|\___/ \___/|_|____/ \___/_/\_\\"
    echo ""
    echo "QAToolBox 智能一键部署系统 v2.0"
    echo -e "${NC}"
}

show_menu() {
    echo "请选择部署方式："
    echo "1) 本地开发环境部署"
    echo "2) 生产环境部署"
    echo "3) Docker容器部署"
    echo "4) 服务管理（启动/停止/重启）"
    echo "5) 查看部署状态"
    echo "6) 清理部署环境"
    echo "7) 显示帮助信息"
    echo "0) 退出"
    echo ""
}

deploy_local() {
    log_info "开始本地开发环境部署..."
    chmod +x deploy/smart_deploy.sh
    ./deploy/smart_deploy.sh --env development
}

deploy_production() {
    log_info "开始生产环境部署..."
    chmod +x deploy/smart_deploy.sh
    
    # 获取服务器IP
    read -p "请输入服务器IP地址（默认: localhost）: " server_ip
    server_ip=${server_ip:-localhost}
    
    ./deploy/smart_deploy.sh --production --host "$server_ip"
}

deploy_docker() {
    log_info "开始Docker容器部署..."
    
    # 检查Docker和Docker Compose
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 创建环境配置文件
    if [ ! -f ".env" ]; then
        log_info "创建环境配置文件..."
        cp deploy/env.template .env
        
        # 生成随机密钥
        SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
        DB_PASSWORD=$(python3 -c 'import secrets; print(secrets.token_urlsafe(16))')
        
        # 替换配置
        sed -i.bak "s/your-secret-key-here-change-in-production/$SECRET_KEY/g" .env
        sed -i.bak "s/your-secure-password-here/$DB_PASSWORD/g" .env
        sed -i.bak "s/DB_HOST=localhost/DB_HOST=db/g" .env
        sed -i.bak "s/REDIS_URL=redis:\/\/localhost:6379\/0/REDIS_URL=redis:\/\/redis:6379\/0/g" .env
        
        rm .env.bak
        log_success "环境配置文件已创建，请编辑 .env 文件配置API密钥"
    fi
    
    # 构建和启动容器
    log_info "构建Docker镜像..."
    docker-compose -f docker-compose.optimized.yml build
    
    log_info "启动Docker容器..."
    docker-compose -f docker-compose.optimized.yml up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 执行数据库迁移
    log_info "执行数据库迁移..."
    docker-compose -f docker-compose.optimized.yml exec web python manage.py migrate
    
    # 创建超级用户
    log_info "创建管理员用户..."
    docker-compose -f docker-compose.optimized.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('管理员用户已创建')
else:
    print('管理员用户已存在')
"
    
    log_success "Docker部署完成！"
    echo "🌐 访问地址: http://localhost:8000"
    echo "👤 管理后台: http://localhost:8000/admin/"
    echo "📋 用户名: admin"
    echo "🔑 密码: admin123"
}

manage_service() {
    echo "服务管理选项："
    echo "1) 启动服务"
    echo "2) 停止服务"
    echo "3) 重启服务"
    echo "4) 查看状态"
    echo ""
    
    read -p "请选择操作 (1-4): " service_action
    
    case $service_action in
        1)
            if [ -f "docker-compose.optimized.yml" ] && [ -f ".env" ]; then
                docker-compose -f docker-compose.optimized.yml up -d
            else
                ./deploy/smart_deploy.sh --start
            fi
            ;;
        2)
            if [ -f "docker-compose.optimized.yml" ]; then
                docker-compose -f docker-compose.optimized.yml down
            else
                ./deploy/smart_deploy.sh --stop
            fi
            ;;
        3)
            if [ -f "docker-compose.optimized.yml" ]; then
                docker-compose -f docker-compose.optimized.yml restart
            else
                ./deploy/smart_deploy.sh --restart
            fi
            ;;
        4)
            if [ -f "docker-compose.optimized.yml" ]; then
                docker-compose -f docker-compose.optimized.yml ps
            else
                ./deploy/smart_deploy.sh --status
            fi
            ;;
        *)
            log_error "无效选择"
            ;;
    esac
}

show_status() {
    log_info "检查部署状态..."
    
    echo "=== 进程状态 ==="
    if pgrep -f "runserver\|gunicorn" > /dev/null; then
        echo "✅ Web服务正在运行"
        ps aux | grep -E "runserver|gunicorn" | grep -v grep
    else
        echo "❌ Web服务未运行"
    fi
    
    echo ""
    echo "=== Docker状态 ==="
    if command -v docker &> /dev/null; then
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q qatoolbox; then
            echo "✅ Docker容器正在运行"
            docker ps --format "table {{.Names}}\t{{.Status}}" | grep qatoolbox
        else
            echo "❌ Docker容器未运行"
        fi
    else
        echo "❌ Docker未安装"
    fi
    
    echo ""
    echo "=== 端口状态 ==="
    if command -v netstat &> /dev/null; then
        netstat -tlnp 2>/dev/null | grep ":8000\|:5432\|:6379" || echo "相关端口未监听"
    elif command -v ss &> /dev/null; then
        ss -tlnp | grep ":8000\|:5432\|:6379" || echo "相关端口未监听"
    fi
    
    echo ""
    echo "=== 服务测试 ==="
    if curl -s -I http://localhost:8000/ | grep -q "200\|302"; then
        echo "✅ HTTP服务响应正常"
    else
        echo "❌ HTTP服务无响应"
    fi
}

cleanup_deployment() {
    log_warning "这将清理所有部署相关的文件和容器，是否继续？(y/N)"
    read -p "请确认: " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        log_info "清理部署环境..."
        
        # 停止服务
        pkill -f "runserver\|gunicorn" 2>/dev/null || true
        
        # 清理Docker
        if command -v docker-compose &> /dev/null && [ -f "docker-compose.optimized.yml" ]; then
            docker-compose -f docker-compose.optimized.yml down -v
        fi
        
        # 清理文件
        rm -rf venv/
        rm -rf staticfiles/
        rm -rf logs/*.log
        
        log_success "清理完成"
    else
        log_info "取消清理操作"
    fi
}

show_help() {
    echo "QAToolBox 部署脚本帮助信息"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --local        本地开发环境部署"
    echo "  --production   生产环境部署"
    echo "  --docker       Docker容器部署"
    echo "  --status       查看部署状态"
    echo "  --cleanup      清理部署环境"
    echo "  --help         显示帮助信息"
    echo ""
    echo "交互模式:"
    echo "  直接运行脚本进入交互式菜单"
    echo ""
    echo "文件说明:"
    echo "  deploy/smart_deploy.sh     智能部署脚本"
    echo "  docker-compose.optimized.yml  Docker编排文件"
    echo "  deploy/env.template        环境配置模板"
    echo "  requirements/              依赖文件目录"
    echo ""
}

main() {
    show_banner
    
    # 命令行参数处理
    case "${1:-}" in
        --local)
            deploy_local
            exit 0
            ;;
        --production)
            deploy_production
            exit 0
            ;;
        --docker)
            deploy_docker
            exit 0
            ;;
        --status)
            show_status
            exit 0
            ;;
        --cleanup)
            cleanup_deployment
            exit 0
            ;;
        --help)
            show_help
            exit 0
            ;;
        "")
            # 交互模式
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
    
    # 交互式菜单
    while true; do
        show_menu
        read -p "请选择 (0-7): " choice
        
        case $choice in
            1)
                deploy_local
                ;;
            2)
                deploy_production
                ;;
            3)
                deploy_docker
                ;;
            4)
                manage_service
                ;;
            5)
                show_status
                ;;
            6)
                cleanup_deployment
                ;;
            7)
                show_help
                ;;
            0)
                log_info "退出部署脚本"
                exit 0
                ;;
            *)
                log_error "无效选择，请输入 0-7"
                ;;
        esac
        
        echo ""
        read -p "按回车键继续..."
        clear
        show_banner
    done
}

# 执行主函数
main "$@"