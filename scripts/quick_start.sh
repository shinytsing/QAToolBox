#!/bin/bash

# QAToolBox 快速启动脚本
# 用于开发和测试环境快速启动

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

log_info "快速启动 QAToolBox (环境: ${ENVIRONMENT})"

# 检查Python环境
if ! command -v python &> /dev/null; then
    log_error "Python 未安装"
    exit 1
fi

# 检查Django
if ! python -c "import django" &> /dev/null; then
    log_error "Django 未安装，请先安装依赖"
    exit 1
fi

# 快速启动函数
quick_start() {
    log_info "开始快速启动..."
    
    # 1. 运行数据库迁移
    log_info "运行数据库迁移..."
    python manage.py migrate --settings="$SETTINGS_MODULE" --verbosity=0
    
    # 2. 收集静态文件
    log_info "收集静态文件..."
    python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" --verbosity=0
    
    # 3. 快速健康检查
    log_info "运行快速健康检查..."
    if python manage.py health_check --settings="$SETTINGS_MODULE" --verbosity=0; then
        log_success "健康检查通过"
    else
        log_warning "健康检查失败，但继续启动"
    fi
    
    # 4. 启动Django服务器
    log_success "启动完成！"
    log_info "Django 服务器: http://localhost:8000"
    log_info "健康检查: http://localhost:8000/tools/health/"
    log_info "管理后台: http://localhost:8000/admin/"
    
    # 启动开发服务器
    python manage.py runserver 0.0.0.0:8000 --settings="$SETTINGS_MODULE"
}

# 开发环境启动
dev_start() {
    log_info "开发环境启动..."
    
    # 创建超级用户（如果不存在）
    if ! python manage.py shell --settings="$SETTINGS_MODULE" -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" 2>/dev/null | grep -q "True"; then
        log_info "创建超级用户..."
        echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell --settings="$SETTINGS_MODULE"
        log_success "超级用户创建完成 (用户名: admin, 密码: admin123)"
    fi
    
    quick_start
}

# 测试环境启动
test_start() {
    log_info "测试环境启动..."
    
    # 运行测试
    log_info "运行测试..."
    python manage.py test --settings="$SETTINGS_MODULE" --verbosity=2
    
    quick_start
}

# 生产环境启动
prod_start() {
    log_info "生产环境启动..."
    
    # 检查环境变量
    if [ ! -f ".env" ]; then
        log_warning ".env 文件不存在，请确保环境变量已正确配置"
    fi
    
    # 运行完整启动脚本
    ./scripts/start_with_tests.sh production
}

# 根据环境选择启动方式
case $ENVIRONMENT in
    "development"|"dev")
        dev_start
        ;;
    "testing"|"test")
        test_start
        ;;
    "production"|"prod")
        prod_start
        ;;
    *)
        log_error "未知环境: $ENVIRONMENT"
        log_info "支持的环境: development, testing, production"
        exit 1
        ;;
esac
