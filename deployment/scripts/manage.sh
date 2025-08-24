#!/bin/bash

# QAToolBox 服务管理脚本

PROJECT_DIR="/opt/QAToolbox"
COMPOSE_FILE="deployment/configs/docker-compose.yml"
DOMAIN="shenyiqing.xin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查项目目录
check_project_dir() {
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    cd $PROJECT_DIR
}

# 启动服务
start_services() {
    log_info "启动 QAToolBox 服务..."
    docker-compose -f $COMPOSE_FILE up -d
    log_info "服务启动完成"
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 显示服务状态
    docker-compose -f $COMPOSE_FILE ps
}

# 停止服务
stop_services() {
    log_info "停止 QAToolBox 服务..."
    docker-compose -f $COMPOSE_FILE down
    log_info "服务停止完成"
}

# 重启服务
restart_services() {
    log_info "重启 QAToolBox 服务..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d
    log_info "服务重启完成"
    
    # 等待服务启动
    sleep 10
    docker-compose -f $COMPOSE_FILE ps
}

# 查看日志
show_logs() {
    log_info "查看服务日志..."
    if [ -n "$2" ]; then
        docker-compose -f $COMPOSE_FILE logs -f --tail=100 $2
    else
        docker-compose -f $COMPOSE_FILE logs -f --tail=100
    fi
}

# 查看服务状态
show_status() {
    log_info "QAToolBox 服务状态:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "系统资源使用:"
    docker stats --no-stream
    
    echo ""
    log_info "磁盘使用情况:"
    df -h
}

# 更新服务
update_services() {
    log_info "更新 QAToolBox 服务..."
    
    # 拉取最新代码
    log_info "拉取最新代码..."
    git pull origin main
    
    # 重新构建镜像
    log_info "重新构建镜像..."
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # 重启服务
    log_info "重启服务..."
    docker-compose -f $COMPOSE_FILE down
    docker-compose -f $COMPOSE_FILE up -d
    
    log_info "服务更新完成"
    
    # 等待服务启动
    sleep 15
    docker-compose -f $COMPOSE_FILE ps
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    BACKUP_DIR="$PROJECT_DIR/backups"
    mkdir -p $BACKUP_DIR
    
    BACKUP_FILE="$BACKUP_DIR/qatoolbox_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose -f $COMPOSE_FILE exec -T db pg_dump -U qatoolbox qatoolbox > $BACKUP_FILE; then
        log_info "数据库备份完成: $BACKUP_FILE"
        
        # 压缩备份文件
        gzip $BACKUP_FILE
        log_info "备份文件已压缩: ${BACKUP_FILE}.gz"
        
        # 清理7天前的备份
        find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
        log_info "已清理7天前的备份文件"
    else
        log_error "数据库备份失败"
        exit 1
    fi
}

# 恢复数据库
restore_database() {
    if [ -z "$2" ]; then
        log_error "请指定备份文件路径"
        log_info "使用方法: $0 restore /path/to/backup.sql.gz"
        exit 1
    fi
    
    BACKUP_FILE="$2"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "备份文件不存在: $BACKUP_FILE"
        exit 1
    fi
    
    log_warn "警告：这将覆盖当前数据库！"
    read -p "确认继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "操作已取消"
        exit 0
    fi
    
    log_info "恢复数据库..."
    
    if [[ $BACKUP_FILE == *.gz ]]; then
        zcat $BACKUP_FILE | docker-compose -f $COMPOSE_FILE exec -T db psql -U qatoolbox qatoolbox
    else
        cat $BACKUP_FILE | docker-compose -f $COMPOSE_FILE exec -T db psql -U qatoolbox qatoolbox
    fi
    
    log_info "数据库恢复完成"
}

# 配置SSL证书
setup_ssl() {
    log_info "配置 SSL 证书..."
    
    # 检查certbot是否安装
    if ! command -v certbot >/dev/null 2>&1; then
        log_info "安装 certbot..."
        if command -v yum >/dev/null 2>&1; then
            yum install -y epel-release
            yum install -y certbot
        elif command -v apt >/dev/null 2>&1; then
            apt update
            apt install -y certbot
        else
            log_error "无法安装 certbot，请手动安装"
            exit 1
        fi
    fi
    
    # 创建证书目录
    mkdir -p /var/www/certbot
    
    # 获取证书
    log_info "获取 Let's Encrypt 证书..."
    certbot certonly --webroot \
        -w /var/www/certbot \
        -d $DOMAIN \
        -d www.$DOMAIN \
        --non-interactive \
        --agree-tos \
        --email admin@$DOMAIN
    
    if [ $? -eq 0 ]; then
        log_info "SSL 证书获取成功"
        
        # 更新nginx配置启用HTTPS
        log_info "更新 Nginx 配置启用 HTTPS..."
        sed -i 's/# ssl_certificate/ssl_certificate/g' $PROJECT_DIR/deployment/configs/nginx.conf
        
        # 更新环境变量启用SSL重定向
        sed -i 's/SECURE_SSL_REDIRECT=False/SECURE_SSL_REDIRECT=True/g' $PROJECT_DIR/.env
        
        # 重启nginx
        docker-compose -f $COMPOSE_FILE restart nginx
        
        # 设置自动续期
        (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
        
        log_info "SSL 配置完成！网站现在支持 HTTPS"
    else
        log_error "SSL 证书获取失败"
        exit 1
    fi
}

# 清理系统
cleanup() {
    log_info "清理系统..."
    
    # 清理Docker资源
    docker system prune -f
    docker volume prune -f
    
    # 清理日志文件
    find $PROJECT_DIR/logs -name "*.log" -mtime +30 -delete 2>/dev/null || true
    
    log_info "系统清理完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务状态
    if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
        log_error "服务未运行"
        return 1
    fi
    
    # 检查Web服务
    if curl -f http://localhost:8000/tools/health/ >/dev/null 2>&1; then
        log_info "✅ Web服务健康"
    else
        log_error "❌ Web服务异常"
        return 1
    fi
    
    # 检查数据库连接
    if docker-compose -f $COMPOSE_FILE exec -T db pg_isready -U qatoolbox >/dev/null 2>&1; then
        log_info "✅ 数据库连接正常"
    else
        log_error "❌ 数据库连接异常"
        return 1
    fi
    
    # 检查Redis连接
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping >/dev/null 2>&1; then
        log_info "✅ Redis连接正常"
    else
        log_error "❌ Redis连接异常"
        return 1
    fi
    
    log_info "✅ 所有服务健康检查通过"
}

# 显示帮助信息
show_help() {
    echo "QAToolBox 服务管理脚本"
    echo ""
    echo "使用方法: $0 {command} [options]"
    echo ""
    echo "可用命令:"
    echo "  start           启动所有服务"
    echo "  stop            停止所有服务"
    echo "  restart         重启所有服务"
    echo "  logs [service]  查看服务日志 (可选指定服务名)"
    echo "  status          查看服务状态"
    echo "  update          更新代码并重启服务"
    echo "  backup          备份数据库"
    echo "  restore <file>  恢复数据库"
    echo "  ssl             配置SSL证书"
    echo "  cleanup         清理系统资源"
    echo "  health          健康检查"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start              # 启动服务"
    echo "  $0 logs web           # 查看web服务日志"
    echo "  $0 backup             # 备份数据库"
    echo "  $0 restore backup.sql # 恢复数据库"
}

# 主函数
main() {
    check_project_dir
    
    case "$1" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs "$@"
            ;;
        status)
            show_status
            ;;
        update)
            update_services
            ;;
        backup)
            backup_database
            ;;
        restore)
            restore_database "$@"
            ;;
        ssl)
            setup_ssl
            ;;
        cleanup)
            cleanup
            ;;
        health)
            health_check
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
