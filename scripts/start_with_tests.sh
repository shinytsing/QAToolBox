#!/bin/bash

# QAToolBox 启动脚本 - 包含自动化测试
# 使用方法: ./scripts/start_with_tests.sh [环境]

set -e

# 颜色定义
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

# 默认环境
ENVIRONMENT=${1:-development}
SETTINGS_MODULE="config.settings.${ENVIRONMENT}"

log_info "启动 QAToolBox (环境: ${ENVIRONMENT})"

# 检查环境变量文件
if [ ! -f ".env" ]; then
    log_warning ".env 文件不存在，使用默认配置"
fi

# 函数：等待服务启动
wait_for_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=30
    local attempt=1
    
    log_info "等待 ${service_name} 启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$service_url" > /dev/null 2>&1; then
            log_success "${service_name} 已启动"
            return 0
        fi
        
        log_info "尝试 ${attempt}/${max_attempts} - ${service_name} 尚未就绪，等待 10 秒..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    log_error "${service_name} 启动超时"
    return 1
}

# 函数：运行数据库迁移
run_migrations() {
    log_info "运行数据库迁移..."
    python manage.py migrate --settings="$SETTINGS_MODULE"
    log_success "数据库迁移完成"
}

# 函数：收集静态文件
collect_static() {
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE"
    log_success "静态文件收集完成"
}

# 函数：运行健康检查
run_health_check() {
    log_info "运行健康检查..."
    python manage.py health_check --settings="$SETTINGS_MODULE"
    if [ $? -eq 0 ]; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        return 1
    fi
}

# 函数：运行缓存测试
run_cache_test() {
    log_info "运行缓存测试..."
    python manage.py cache_test --settings="$SETTINGS_MODULE"
    if [ $? -eq 0 ]; then
        log_success "缓存测试通过"
    else
        log_warning "缓存测试失败"
    fi
}

# 函数：运行API测试
run_api_test() {
    log_info "运行API测试..."
    python manage.py api_test --settings="$SETTINGS_MODULE"
    if [ $? -eq 0 ]; then
        log_success "API测试通过"
    else
        log_warning "API测试失败"
    fi
}

# 函数：运行单元测试
run_unit_tests() {
    log_info "运行单元测试..."
    python manage.py test --settings="$SETTINGS_MODULE" --verbosity=2
    if [ $? -eq 0 ]; then
        log_success "单元测试通过"
    else
        log_error "单元测试失败"
        return 1
    fi
}

# 函数：启动Celery
start_celery() {
    log_info "启动 Celery 工作进程..."
    celery -A QAToolBox worker -l info --concurrency=4 &
    CELERY_PID=$!
    
    # 等待Celery启动
    sleep 5
    
    # 检查Celery是否启动成功
    if kill -0 $CELERY_PID 2>/dev/null; then
        log_success "Celery 工作进程已启动 (PID: $CELERY_PID)"
    else
        log_error "Celery 工作进程启动失败"
        return 1
    fi
}

# 函数：启动Celery Beat
start_celery_beat() {
    log_info "启动 Celery Beat 调度器..."
    celery -A QAToolBox beat -l info &
    BEAT_PID=$!
    
    # 等待Beat启动
    sleep 3
    
    # 检查Beat是否启动成功
    if kill -0 $BEAT_PID 2>/dev/null; then
        log_success "Celery Beat 调度器已启动 (PID: $BEAT_PID)"
    else
        log_error "Celery Beat 调度器启动失败"
        return 1
    fi
}

# 函数：启动Django服务器
start_django() {
    log_info "启动 Django 服务器..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # 生产环境使用 Gunicorn
        gunicorn QAToolBox.wsgi:application \
            --bind 0.0.0.0:8000 \
            --workers 4 \
            --worker-class gevent \
            --worker-connections 1000 \
            --max-requests 1000 \
            --max-requests-jitter 100 \
            --timeout 30 \
            --keep-alive 2 \
            --access-logfile - \
            --error-logfile - \
            --log-level info
    else
        # 开发环境使用 Django 开发服务器
        python manage.py runserver 0.0.0.0:8000 --settings="$SETTINGS_MODULE"
    fi
}

# 函数：清理函数
cleanup() {
    log_info "清理进程..."
    
    # 停止Celery进程
    if [ ! -z "$CELERY_PID" ]; then
        kill $CELERY_PID 2>/dev/null || true
        log_info "Celery 工作进程已停止"
    fi
    
    # 停止Beat进程
    if [ ! -z "$BEAT_PID" ]; then
        kill $BEAT_PID 2>/dev/null || true
        log_info "Celery Beat 调度器已停止"
    fi
    
    # 停止Django进程
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
        log_info "Django 服务器已停止"
    fi
}

# 设置信号处理
trap cleanup EXIT INT TERM

# 主函数
main() {
    log_info "开始启动流程..."
    
    # 1. 运行数据库迁移
    run_migrations
    
    # 2. 收集静态文件
    collect_static
    
    # 3. 运行健康检查
    if ! run_health_check; then
        log_error "健康检查失败，停止启动"
        exit 1
    fi
    
    # 4. 运行缓存测试
    run_cache_test
    
    # 5. 运行API测试
    run_api_test
    
    # 6. 运行单元测试（可选，可通过环境变量控制）
    if [ "$RUN_UNIT_TESTS" = "true" ]; then
        if ! run_unit_tests; then
            log_error "单元测试失败，停止启动"
            exit 1
        fi
    else
        log_info "跳过单元测试 (设置 RUN_UNIT_TESTS=true 启用)"
    fi
    
    # 7. 启动Celery工作进程
    if ! start_celery; then
        log_error "Celery启动失败，停止启动"
        exit 1
    fi
    
    # 8. 启动Celery Beat调度器
    if ! start_celery_beat; then
        log_error "Celery Beat启动失败，停止启动"
        exit 1
    fi
    
    # 9. 等待服务完全启动
    log_info "等待服务完全启动..."
    sleep 10
    
    # 10. 最终健康检查
    log_info "执行最终健康检查..."
    if ! run_health_check; then
        log_error "最终健康检查失败"
        exit 1
    fi
    
    log_success "所有服务启动完成！"
    log_info "Django 服务器: http://localhost:8000"
    log_info "健康检查: http://localhost:8000/tools/health/"
    log_info "系统状态: http://localhost:8000/tools/system/status/"
    
    # 11. 启动Django服务器
    start_django
}

# 检查Python环境
if ! command -v python &> /dev/null; then
    log_error "Python 未安装"
    exit 1
fi

# 检查Django
if ! python -c "import django" &> /dev/null; then
    log_error "Django 未安装"
    exit 1
fi

# 运行主函数
main "$@"
