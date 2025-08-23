#!/bin/bash

# QAToolBox 一键部署脚本
# 作者: 运维团队
# 功能: 自动化部署 QAToolBox 应用到生产环境
# 使用方法: ./deploy/one_click_deploy.sh [production|staging|development]

set -euo pipefail  # 严格模式：遇到错误立即退出

# =============================================================================
# 配置区域
# =============================================================================

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# 项目配置
readonly PROJECT_NAME="QAToolBox"
readonly PROJECT_DIR="/Users/gaojie/PycharmProjects/QAToolBox"
readonly BACKUP_DIR="/var/backups/qatoolbox"
readonly LOG_DIR="/var/log/qatoolbox"
readonly SERVICE_USER="qatoolbox"

# 部署环境
DEPLOY_ENV="${1:-production}"
readonly DEPLOY_ENV

# 版本信息
readonly DEPLOY_TIME=$(date '+%Y%m%d_%H%M%S')
readonly VERSION_TAG="v$(date '+%Y.%m.%d')-${DEPLOY_TIME}"

# =============================================================================
# 工具函数
# =============================================================================

# 日志函数
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

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "命令 '$1' 未找到，请安装后重试"
        exit 1
    fi
}

# 检查服务状态
check_service() {
    local service_name="$1"
    if systemctl is-active --quiet "$service_name"; then
        log_success "服务 $service_name 运行正常"
        return 0
    else
        log_error "服务 $service_name 未运行"
        return 1
    fi
}

# 等待服务启动
wait_for_service() {
    local url="$1"
    local timeout="${2:-60}"
    local count=0
    
    log_info "等待服务启动: $url"
    while [ $count -lt $timeout ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "服务启动成功: $url"
            return 0
        fi
        sleep 1
        ((count++))
        echo -n "."
    done
    
    log_error "服务启动超时: $url"
    return 1
}

# 创建备份
create_backup() {
    log_info "创建备份..."
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR/$DEPLOY_TIME"
    
    # 备份数据库
    if check_service postgresql; then
        log_info "备份数据库..."
        sudo -u postgres pg_dump qatoolbox > "$BACKUP_DIR/$DEPLOY_TIME/database.sql"
        log_success "数据库备份完成"
    fi
    
    # 备份媒体文件
    if [ -d "$PROJECT_DIR/media" ]; then
        log_info "备份媒体文件..."
        tar -czf "$BACKUP_DIR/$DEPLOY_TIME/media.tar.gz" -C "$PROJECT_DIR" media/
        log_success "媒体文件备份完成"
    fi
    
    # 备份静态文件
    if [ -d "$PROJECT_DIR/staticfiles" ]; then
        log_info "备份静态文件..."
        tar -czf "$BACKUP_DIR/$DEPLOY_TIME/staticfiles.tar.gz" -C "$PROJECT_DIR" staticfiles/
        log_success "静态文件备份完成"
    fi
    
    log_success "备份创建完成: $BACKUP_DIR/$DEPLOY_TIME"
}

# 回滚函数
rollback() {
    local backup_time="$1"
    log_warning "开始回滚到备份: $backup_time"
    
    # 停止服务
    docker-compose -f docker-compose.prod.yml down
    
    # 恢复数据库
    if [ -f "$BACKUP_DIR/$backup_time/database.sql" ]; then
        log_info "恢复数据库..."
        sudo -u postgres psql -d qatoolbox < "$BACKUP_DIR/$backup_time/database.sql"
    fi
    
    # 恢复媒体文件
    if [ -f "$BACKUP_DIR/$backup_time/media.tar.gz" ]; then
        log_info "恢复媒体文件..."
        tar -xzf "$BACKUP_DIR/$backup_time/media.tar.gz" -C "$PROJECT_DIR"
    fi
    
    # 恢复静态文件
    if [ -f "$BACKUP_DIR/$backup_time/staticfiles.tar.gz" ]; then
        log_info "恢复静态文件..."
        tar -xzf "$BACKUP_DIR/$backup_time/staticfiles.tar.gz" -C "$PROJECT_DIR"
    fi
    
    log_success "回滚完成"
}

# =============================================================================
# 预检查阶段
# =============================================================================

pre_check() {
    log_info "开始预检查..."
    
    # 检查运行权限
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用 root 用户运行此脚本"
        exit 1
    fi
    
    # 检查必要的命令
    local commands=("docker" "docker-compose" "git" "curl" "python3" "pip3")
    for cmd in "${commands[@]}"; do
        check_command "$cmd"
    done
    
    # 检查项目目录
    if [ ! -d "$PROJECT_DIR" ]; then
        log_error "项目目录不存在: $PROJECT_DIR"
        exit 1
    fi
    
    # 检查环境文件
    if [ ! -f "$PROJECT_DIR/.env.${DEPLOY_ENV}" ]; then
        log_error "环境配置文件不存在: .env.${DEPLOY_ENV}"
        exit 1
    fi
    
    # 检查 Docker 服务
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker 服务未运行"
        exit 1
    fi
    
    # 检查磁盘空间（至少需要 5GB）
    local available_space=$(df "$PROJECT_DIR" | awk 'NR==2 {print $4}')
    local required_space=5242880  # 5GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        log_error "磁盘空间不足，至少需要 5GB 可用空间"
        exit 1
    fi
    
    log_success "预检查完成"
}

# =============================================================================
# 代码更新阶段
# =============================================================================

update_code() {
    log_info "更新代码..."
    
    cd "$PROJECT_DIR"
    
    # 检查 Git 状态
    if [ -d ".git" ]; then
        # 保存本地修改
        git stash push -m "Deploy stash $DEPLOY_TIME"
        
        # 拉取最新代码
        git fetch origin
        git checkout main
        git pull origin main
        
        # 创建版本标签
        git tag "$VERSION_TAG"
        git push origin "$VERSION_TAG" || log_warning "推送标签失败"
        
        log_success "代码更新完成，版本: $VERSION_TAG"
    else
        log_warning "不是 Git 仓库，跳过代码更新"
    fi
}

# =============================================================================
# 依赖安装阶段
# =============================================================================

install_dependencies() {
    log_info "安装依赖..."
    
    cd "$PROJECT_DIR"
    
    # 复制环境文件
    cp ".env.${DEPLOY_ENV}" .env
    
    # 构建 Docker 镜像
    log_info "构建 Docker 镜像..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    log_success "依赖安装完成"
}

# =============================================================================
# 数据库迁移阶段
# =============================================================================

migrate_database() {
    log_info "执行数据库迁移..."
    
    cd "$PROJECT_DIR"
    
    # 启动数据库服务
    docker-compose -f docker-compose.prod.yml up -d db redis
    
    # 等待数据库启动
    sleep 10
    
    # 执行迁移
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py migrate --noinput
    
    # 收集静态文件
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py collectstatic --noinput
    
    # 创建超级用户（如果不存在）
    docker-compose -f docker-compose.prod.yml run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123456')
    print('超级用户创建成功')
else:
    print('超级用户已存在')
"
    
    log_success "数据库迁移完成"
}

# =============================================================================
# 服务部署阶段
# =============================================================================

deploy_services() {
    log_info "部署服务..."
    
    cd "$PROJECT_DIR"
    
    # 停止旧服务
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # 启动所有服务
    docker-compose -f docker-compose.prod.yml up -d
    
    # 等待服务启动
    sleep 30
    
    # 检查服务状态
    docker-compose -f docker-compose.prod.yml ps
    
    log_success "服务部署完成"
}

# =============================================================================
# 健康检查阶段
# =============================================================================

health_check() {
    log_info "执行健康检查..."
    
    local endpoints=(
        "http://localhost:8000/health/"
        "http://localhost:8000/tools/health/"
        "http://localhost:3000/api/health"
        "http://localhost:9090/-/healthy"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if wait_for_service "$endpoint" 60; then
            log_success "健康检查通过: $endpoint"
        else
            log_error "健康检查失败: $endpoint"
            return 1
        fi
    done
    
    # 检查 Docker 容器状态
    local failed_containers=$(docker-compose -f docker-compose.prod.yml ps --services --filter "status=exited")
    if [ -n "$failed_containers" ]; then
        log_error "以下容器启动失败: $failed_containers"
        return 1
    fi
    
    log_success "所有健康检查通过"
}

# =============================================================================
# 性能测试阶段
# =============================================================================

performance_test() {
    log_info "执行性能测试..."
    
    # 等待服务完全启动
    sleep 10
    
    # 简单的负载测试
    if command -v ab &> /dev/null; then
        log_info "执行 Apache Bench 测试..."
        ab -n 100 -c 10 http://localhost:8000/ > /tmp/ab_test.log 2>&1
        
        # 分析结果
        local avg_time=$(grep "Time per request" /tmp/ab_test.log | head -1 | awk '{print $4}')
        local failed_requests=$(grep "Failed requests" /tmp/ab_test.log | awk '{print $3}')
        
        log_info "平均响应时间: ${avg_time}ms"
        log_info "失败请求数: $failed_requests"
        
        if [ "$failed_requests" -gt 5 ]; then
            log_warning "失败请求数过多，可能存在性能问题"
        fi
    else
        log_warning "未安装 Apache Bench，跳过性能测试"
    fi
    
    log_success "性能测试完成"
}

# =============================================================================
# 安全检查阶段
# =============================================================================

security_check() {
    log_info "执行安全检查..."
    
    cd "$PROJECT_DIR"
    
    # 检查敏感文件权限
    local sensitive_files=(".env" "config/settings/production.py")
    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            local perms=$(stat -c "%a" "$file")
            if [ "$perms" != "600" ]; then
                log_warning "文件权限不安全: $file ($perms)"
                chmod 600 "$file"
                log_info "已修复文件权限: $file"
            fi
        fi
    done
    
    # 检查 Docker 安全配置
    local insecure_containers=$(docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E ":0.0.0.0:" || true)
    if [ -n "$insecure_containers" ]; then
        log_warning "发现不安全的端口绑定:"
        echo "$insecure_containers"
    fi
    
    # 检查 SSL 证书（如果存在）
    if [ -f "nginx/ssl/cert.pem" ]; then
        local cert_days=$(openssl x509 -in nginx/ssl/cert.pem -noout -days 2>/dev/null || echo "0")
        if [ "$cert_days" -lt 30 ]; then
            log_warning "SSL 证书将在 $cert_days 天后过期"
        fi
    fi
    
    log_success "安全检查完成"
}

# =============================================================================
# 清理阶段
# =============================================================================

cleanup() {
    log_info "执行清理..."
    
    # 清理旧的 Docker 镜像
    docker image prune -f
    
    # 清理旧的备份（保留最近 10 个）
    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -maxdepth 1 -type d -name "20*" | sort -r | tail -n +11 | xargs rm -rf
        log_info "清理旧备份完成"
    fi
    
    # 清理临时文件
    rm -f /tmp/ab_test.log
    
    log_success "清理完成"
}

# =============================================================================
# 部署通知
# =============================================================================

send_notification() {
    local status="$1"
    local message="$2"
    
    log_info "发送部署通知..."
    
    # 这里可以集成钉钉、企业微信等通知服务
    # 示例：发送到钉钉机器人
    if [ -n "${DINGTALK_WEBHOOK:-}" ]; then
        curl -X POST "$DINGTALK_WEBHOOK" \
            -H 'Content-Type: application/json' \
            -d "{
                \"msgtype\": \"text\",
                \"text\": {
                    \"content\": \"QAToolBox 部署${status}: ${message}\n时间: $(date)\n环境: ${DEPLOY_ENV}\n版本: ${VERSION_TAG}\"
                }
            }" || log_warning "钉钉通知发送失败"
    fi
    
    log_success "通知发送完成"
}

# =============================================================================
# 主流程
# =============================================================================

main() {
    log_info "开始部署 QAToolBox to $DEPLOY_ENV 环境"
    log_info "部署时间: $DEPLOY_TIME"
    log_info "版本标签: $VERSION_TAG"
    
    # 捕获错误信号
    trap 'log_error "部署过程中发生错误，正在清理..."; cleanup; exit 1' ERR
    
    # 执行部署步骤
    pre_check
    create_backup
    update_code
    install_dependencies
    migrate_database
    deploy_services
    
    # 等待服务稳定
    sleep 30
    
    health_check
    performance_test
    security_check
    cleanup
    
    # 发送成功通知
    send_notification "成功" "部署完成，所有检查通过"
    
    log_success "=== 部署完成 ==="
    log_info "应用访问地址: http://localhost:8000"
    log_info "管理后台: http://localhost:8000/admin/"
    log_info "监控面板: http://localhost:3000"
    log_info "版本信息: $VERSION_TAG"
    
    # 显示服务状态
    echo ""
    log_info "服务状态:"
    docker-compose -f docker-compose.prod.yml ps
}

# =============================================================================
# 脚本入口
# =============================================================================

# 显示使用说明
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    echo "用法: $0 [production|staging|development]"
    echo ""
    echo "选项:"
    echo "  production   生产环境部署（默认）"
    echo "  staging      预发布环境部署"
    echo "  development  开发环境部署"
    echo ""
    echo "环境变量:"
    echo "  DINGTALK_WEBHOOK  钉钉机器人 Webhook URL（可选）"
    echo ""
    echo "示例:"
    echo "  $0 production"
    echo "  DINGTALK_WEBHOOK=https://... $0 staging"
    exit 0
fi

# 确认部署
echo "即将部署到 $DEPLOY_ENV 环境，是否继续？[y/N]"
read -r confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    log_info "部署已取消"
    exit 0
fi

# 执行主流程
main "$@"
