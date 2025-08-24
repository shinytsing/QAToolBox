#!/bin/bash

# 阿里云QAToolBox一键部署脚本
# 作者: QAToolBox Team
# 版本: 1.0
# 更新时间: $(date +%Y-%m-%d)

set -e  # 遇到错误立即退出

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

# 检查是否为root用户
check_root() {
    if [ "$EUID" -eq 0 ]; then
        log_warning "检测到root用户，建议使用普通用户运行"
        read -p "是否继续？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检查系统要求
check_system() {
    log_info "检查系统要求..."
    
    # 检查操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "操作系统: $PRETTY_NAME"
    else
        log_error "无法识别的操作系统"
        exit 1
    fi
    
    # 检查Python版本
    if command -v python3.9 &> /dev/null; then
        PYTHON_CMD=python3.9
    elif command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [ "$(echo "$PYTHON_VERSION >= 3.8" | bc -l 2>/dev/null)" == "1" ] 2>/dev/null; then
            PYTHON_CMD=python3
        else
            log_error "需要Python 3.8或更高版本，当前版本: $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "未找到Python 3，请先安装Python"
        exit 1
    fi
    
    log_success "Python版本检查通过: $($PYTHON_CMD --version)"
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1048576 ]; then  # 1GB in KB
        log_warning "磁盘空间不足1GB，可能影响部署"
    fi
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
    if [ "$TOTAL_MEM" -lt 1024 ]; then
        log_warning "内存不足1GB，可能影响性能"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    if command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum update -y
        sudo yum install -y git curl wget gcc gcc-c++ make openssl-dev libffi-dev python3-dev
    elif command -v apt &> /dev/null; then
        # Ubuntu/Debian
        sudo apt update
        sudo apt install -y git curl wget build-essential libssl-dev libffi-dev python3-dev
    else
        log_warning "无法自动安装依赖，请手动安装git, curl, wget, gcc等"
    fi
}

# 下载或更新项目
setup_project() {
    log_info "设置项目..."
    
    PROJECT_DIR="/opt/QAToolBox"
    
    if [ -d "$PROJECT_DIR" ]; then
        log_info "项目目录已存在，更新代码..."
        cd "$PROJECT_DIR"
        git pull origin main || log_warning "Git更新失败，继续使用现有代码"
    else
        log_info "克隆项目..."
        sudo mkdir -p /opt
        sudo git clone https://github.com/yourusername/QAToolBox.git "$PROJECT_DIR"
        sudo chown -R $(whoami):$(whoami) "$PROJECT_DIR"
        cd "$PROJECT_DIR"
    fi
    
    log_success "项目设置完成"
}

# 设置虚拟环境
setup_virtualenv() {
    log_info "设置Python虚拟环境..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
    fi
    
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # 安装额外的包
    pip install xmind xmindparser python-docx python-pptx markdown mistune gunicorn
    
    log_success "虚拟环境设置完成"
}

# 配置Django
configure_django() {
    log_info "配置Django..."
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun
    
    # 创建必要的目录
    sudo mkdir -p /opt/QAToolbox/staticfiles
    sudo mkdir -p /opt/QAToolbox/media
    sudo mkdir -p logs
    sudo chown -R $(whoami):$(whoami) /opt/QAToolbox
    
    # 生成和应用数据库迁移
    python manage.py makemigrations --noinput 2>/dev/null || true
    python manage.py migrate --noinput
    
    # 收集静态文件
    python manage.py collectstatic --noinput --clear
    
    # 创建超级用户
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('管理员用户已创建')
else:
    print('管理员用户已存在')
EOF
    
    # 检查Django配置
    python manage.py check --deploy --fail-level WARNING 2>/dev/null || log_warning "Django配置检查发现警告"
    
    log_success "Django配置完成"
}

# 启动服务
start_service() {
    log_info "启动Gunicorn服务..."
    
    # 停止现有服务
    pkill -f gunicorn 2>/dev/null || true
    sleep 3
    
    # 启动新服务
    gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 2 \
        --worker-class sync \
        --timeout 300 \
        --keepalive 2 \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --access-logfile /tmp/qatoolbox_access.log \
        --error-logfile /tmp/qatoolbox_error.log \
        --log-level info \
        --pid /tmp/qatoolbox.pid \
        --daemon \
        wsgi:application
    
    log_success "Gunicorn服务已启动"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 等待服务启动
    sleep 10
    
    # 检查进程
    if [ -f "/tmp/qatoolbox.pid" ] && ps -p $(cat /tmp/qatoolbox.pid) > /dev/null; then
        log_success "Gunicorn进程正在运行 (PID: $(cat /tmp/qatoolbox.pid))"
    else
        log_error "Gunicorn进程启动失败"
        log_info "错误日志:"
        tail -10 /tmp/qatoolbox_error.log 2>/dev/null || echo "无错误日志"
        return 1
    fi
    
    # 测试HTTP连接
    local max_attempts=5
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -I http://localhost:8000/ | head -1 | grep -q "200\|302"; then
            log_success "HTTP服务测试成功"
            break
        else
            log_warning "第${attempt}次连接测试失败，等待5秒后重试..."
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "HTTP服务测试失败"
        return 1
    fi
    
    return 0
}

# 显示部署信息
show_deployment_info() {
    local server_ip=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
    
    echo
    echo "================================="
    log_success "🎉 部署完成！"
    echo "================================="
    echo
    echo "🌐 访问地址:"
    echo "   主页: http://${server_ip}:8000"
    echo "   管理后台: http://${server_ip}:8000/admin"
    echo
    echo "👤 管理员账号:"
    echo "   用户名: admin"
    echo "   密码: admin123"
    echo
    echo "📋 服务管理命令:"
    echo "   查看状态: ps aux | grep gunicorn"
    echo "   查看日志: tail -f /tmp/qatoolbox_error.log"
    echo "   重启服务: pkill -f gunicorn && $0"
    echo "   停止服务: pkill -f gunicorn"
    echo
    echo "🔒 安全提醒:"
    echo "   1. 请及时修改管理员密码"
    echo "   2. 配置防火墙规则"
    echo "   3. 考虑使用Nginx反向代理"
    echo
    echo "📞 技术支持:"
    echo "   GitHub: https://github.com/yourusername/QAToolBox"
    echo "   文档: ./ALIYUN_DEPLOYMENT_GUIDE.md"
    echo
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 这里可以添加清理逻辑
}

# 信号处理
trap cleanup EXIT

# 主函数
main() {
    echo "================================="
    echo "🚀 QAToolBox 阿里云一键部署脚本"
    echo "================================="
    echo
    
    # 检查是否在项目目录中
    if [ ! -f "manage.py" ]; then
        log_info "未在项目目录中，将自动下载项目..."
        setup_project
        cd /opt/QAToolBox
    fi
    
    check_root
    check_system
    install_dependencies
    setup_virtualenv
    configure_django
    start_service
    
    if verify_deployment; then
        show_deployment_info
        log_success "部署成功完成！"
        exit 0
    else
        log_error "部署验证失败，请检查日志"
        exit 1
    fi
}

# 运行主函数
main "$@"
