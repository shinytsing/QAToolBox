#!/bin/bash
set -e

# QAToolBox 一键部署脚本
# 支持开发、测试、生产环境的自动化部署

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
ENVIRONMENT="development"
RUN_TESTS=true
SKIP_BACKUP=false
FORCE_REBUILD=false
USE_DOCKER=false

# 显示帮助信息
show_help() {
    cat << EOF
QAToolBox 一键部署脚本

使用方法:
    $0 [选项] [环境]

环境:
    development     开发环境 (默认)
    testing         测试环境
    production      生产环境

选项:
    -h, --help         显示帮助信息
    -t, --skip-tests   跳过测试
    -b, --skip-backup  跳过备份 (仅生产环境)
    -f, --force        强制重新构建
    -d, --docker       使用Docker部署
    --no-static        跳过静态文件收集
    --migrate-only     仅执行数据库迁移

示例:
    $0 development                    # 开发环境部署
    $0 production --skip-tests       # 生产环境部署，跳过测试
    $0 testing --docker             # 测试环境Docker部署
EOF
}

# 解析命令行参数
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -t|--skip-tests)
                RUN_TESTS=false
                shift
                ;;
            -b|--skip-backup)
                SKIP_BACKUP=true
                shift
                ;;
            -f|--force)
                FORCE_REBUILD=true
                shift
                ;;
            -d|--docker)
                USE_DOCKER=true
                shift
                ;;
            --no-static)
                SKIP_STATIC=true
                shift
                ;;
            --migrate-only)
                MIGRATE_ONLY=true
                shift
                ;;
            development|testing|production)
                ENVIRONMENT=$1
                shift
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查系统依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    local dependencies=("python3" "pip" "git")
    
    if [[ "$USE_DOCKER" == true ]]; then
        dependencies+=("docker" "docker-compose")
    else
        dependencies+=("postgresql-client" "redis-cli")
    fi
    
    for cmd in "${dependencies[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "缺少依赖: $cmd"
            exit 1
        fi
    done
    
    log_success "依赖检查完成"
}

# 检查环境变量
check_environment() {
    log_info "检查环境变量..."
    
    local env_file="$PROJECT_DIR/.env"
    if [[ ! -f "$env_file" ]]; then
        log_warning "未找到 .env 文件，创建默认配置..."
        cp "$PROJECT_DIR/env.example" "$env_file"
    fi
    
    # 加载环境变量
    set -a
    source "$env_file"
    set +a
    
    # 检查必需的环境变量
    local required_vars=("DJANGO_SECRET_KEY")
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        required_vars+=("DB_PASSWORD" "REDIS_URL")
    fi
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            log_error "缺少环境变量: $var"
            exit 1
        fi
    done
    
    log_success "环境变量检查完成"
}

# 备份数据（仅生产环境）
backup_data() {
    if [[ "$ENVIRONMENT" != "production" ]] || [[ "$SKIP_BACKUP" == true ]]; then
        return 0
    fi
    
    log_info "开始数据备份..."
    
    local backup_dir="$PROJECT_DIR/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据库
    if [[ "$USE_DOCKER" == true ]]; then
        docker-compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$backup_dir/database.sql"
    else
        pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$backup_dir/database.sql"
    fi
    
    # 备份媒体文件
    if [[ -d "$PROJECT_DIR/media" ]]; then
        tar -czf "$backup_dir/media.tar.gz" -C "$PROJECT_DIR" media/
    fi
    
    # 备份静态文件
    if [[ -d "$PROJECT_DIR/staticfiles" ]]; then
        tar -czf "$backup_dir/staticfiles.tar.gz" -C "$PROJECT_DIR" staticfiles/
    fi
    
    log_success "数据备份完成: $backup_dir"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    cd "$PROJECT_DIR"
    
    # 创建虚拟环境（如果不存在）
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    case $ENVIRONMENT in
        "development")
            pip install -r requirements/dev.txt
            ;;
        "testing")
            pip install -r requirements/testing.txt
            ;;
        "production")
            pip install -r requirements/prod.txt
            ;;
    esac
    
    log_success "Python依赖安装完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 设置Django设置模块
    case $ENVIRONMENT in
        "development")
            export DJANGO_SETTINGS_MODULE="config.settings.development"
            ;;
        "testing")
            export DJANGO_SETTINGS_MODULE="config.settings.development"
            ;;
        "production")
            export DJANGO_SETTINGS_MODULE="config.settings.production"
            ;;
    esac
    
    # 检查数据库连接
    python manage.py check --database default
    
    # 执行数据库迁移
    python manage.py migrate
    
    # 创建超级用户（仅开发环境）
    if [[ "$ENVIRONMENT" == "development" ]]; then
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'admin123')" | python manage.py shell
    fi
    
    log_success "数据库配置完成"
}

# 收集静态文件
collect_static() {
    if [[ "$SKIP_STATIC" == true ]]; then
        return 0
    fi
    
    log_info "收集静态文件..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 清理旧的静态文件
    if [[ -d "staticfiles" ]]; then
        rm -rf staticfiles/*
    fi
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    # 压缩静态文件（生产环境）
    if [[ "$ENVIRONMENT" == "production" ]]; then
        python manage.py compress --force
    fi
    
    log_success "静态文件收集完成"
}

# 运行测试
run_tests() {
    if [[ "$RUN_TESTS" != true ]]; then
        return 0
    fi
    
    log_info "运行测试..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 设置测试环境
    export DJANGO_SETTINGS_MODULE="config.settings.development"
    export DJANGO_TEST_PROCESSES=auto
    
    # 运行测试
    python -m pytest \
        --cov=apps \
        --cov-report=html \
        --cov-report=term \
        --html=test_reports/report.html \
        --self-contained-html \
        -v
    
    # 检查测试结果
    if [[ $? -ne 0 ]]; then
        log_error "测试失败，部署中止"
        exit 1
    fi
    
    log_success "测试通过"
}

# Docker部署
deploy_docker() {
    log_info "使用Docker部署..."
    
    cd "$PROJECT_DIR"
    
    # 构建镜像
    if [[ "$FORCE_REBUILD" == true ]]; then
        docker-compose -f docker-compose.prod.yml build --no-cache
    else
        docker-compose -f docker-compose.prod.yml build
    fi
    
    # 启动服务
    docker-compose -f docker-compose.prod.yml up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    docker-compose -f docker-compose.prod.yml ps
    
    log_success "Docker部署完成"
}

# 传统部署
deploy_traditional() {
    log_info "使用传统方式部署..."
    
    cd "$PROJECT_DIR"
    source venv/bin/activate
    
    # 启动Celery（后台）
    if [[ "$ENVIRONMENT" == "production" ]]; then
        pkill -f celery || true
        celery -A QAToolBox worker -D --loglevel=info --pidfile=celery.pid
        celery -A QAToolBox beat -D --loglevel=info --pidfile=celerybeat.pid
    fi
    
    # 启动应用服务器
    case $ENVIRONMENT in
        "development")
            python manage.py runserver 0.0.0.0:8000
            ;;
        "testing"|"production")
            pkill -f gunicorn || true
            gunicorn --bind 0.0.0.0:8000 \
                     --workers 4 \
                     --worker-class gthread \
                     --threads 2 \
                     --worker-connections 1000 \
                     --max-requests 1000 \
                     --max-requests-jitter 50 \
                     --preload \
                     --access-logfile logs/access.log \
                     --error-logfile logs/error.log \
                     --daemon \
                     wsgi:application
            ;;
    esac
    
    log_success "传统部署完成"
}

# 部署后检查
post_deploy_check() {
    log_info "执行部署后检查..."
    
    local url="http://localhost:8000"
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$url/health/" > /dev/null; then
            log_success "健康检查通过"
            break
        else
            log_warning "健康检查失败，重试中... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        fi
    done
    
    if [[ $attempt -gt $max_attempts ]]; then
        log_error "健康检查失败，部署可能有问题"
        exit 1
    fi
    
    # 运行冒烟测试
    log_info "运行冒烟测试..."
    python "$SCRIPT_DIR/smoke_test.py" --url "$url"
    
    log_success "部署后检查完成"
}

# 清理函数
cleanup() {
    if [[ $? -ne 0 ]]; then
        log_error "部署失败，正在清理..."
        # 这里可以添加回滚逻辑
    fi
}

# 主函数
main() {
    # 设置错误处理
    trap cleanup EXIT
    
    # 解析参数
    parse_arguments "$@"
    
    log_info "开始 $ENVIRONMENT 环境部署..."
    log_info "项目目录: $PROJECT_DIR"
    log_info "使用Docker: $USE_DOCKER"
    
    # 如果只执行迁移
    if [[ "$MIGRATE_ONLY" == true ]]; then
        check_environment
        setup_database
        log_success "数据库迁移完成"
        exit 0
    fi
    
    # 执行部署步骤
    check_dependencies
    check_environment
    backup_data
    
    if [[ "$USE_DOCKER" == true ]]; then
        deploy_docker
    else
        install_dependencies
        run_tests
        setup_database
        collect_static
        deploy_traditional
    fi
    
    post_deploy_check
    
    log_success "🎉 部署成功完成！"
    log_info "应用地址: http://localhost:8000"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log_info "生产环境部署完成，请检查所有服务状态"
        log_info "监控面板: http://localhost:3000 (Grafana)"
        log_info "日志分析: http://localhost:5601 (Kibana)"
    fi
}

# 执行主函数
main "$@"
