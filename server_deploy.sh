#!/bin/bash

# QAToolBox 服务器部署脚本
# 专门用于在 47.103.143.152 服务器上部署

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] $1${NC}"
}

# 服务器配置
SERVER_IP="47.103.143.152"
SERVER_USER="admin"
PROJECT_PATH="/home/admin/QAToolBox"
GIT_REPO="https://github.com/shinytsing/QAToolbox.git"

# 检查SSH连接
check_ssh() {
    log "检查SSH连接到 $SERVER_IP..."
    if ! ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP "echo 'SSH连接成功'" 2>/dev/null; then
        error "无法连接到服务器 $SERVER_IP"
        echo "请确保："
        echo "1. 服务器IP正确: $SERVER_IP"
        echo "2. 用户名正确: $SERVER_USER"
        echo "3. SSH密钥已配置或密码认证已启用"
        echo "4. 服务器防火墙允许SSH连接"
        exit 1
    fi
    log "SSH连接成功！"
}

# 安装系统依赖
install_system_deps() {
    log "安装系统依赖..."
    ssh $SERVER_USER@$SERVER_IP "
        # 更新系统包
        sudo apt update
        
        # 安装Python和相关工具
        sudo apt install -y python3 python3-pip python3-venv python3-dev
        
        # 安装Git
        sudo apt install -y git
        
        # 安装其他必要工具
        sudo apt install -y curl wget unzip
        
        log '系统依赖安装完成'
    "
}

# 克隆项目代码
clone_project() {
    log "克隆项目代码..."
    ssh $SERVER_USER@$SERVER_IP "
        # 创建项目目录
        mkdir -p $PROJECT_PATH
        
        # 如果目录已存在，备份并重新克隆
        if [ -d \"$PROJECT_PATH/.git\" ]; then
            cd $PROJECT_PATH
            log '备份现有代码...'
            mv .git .git.backup
            rm -rf *
            mv .git.backup .git
        fi
        
        # 克隆项目
        cd $PROJECT_PATH
        git clone $GIT_REPO .
        
        log '项目代码克隆完成'
    "
}

# 设置Python环境
setup_python_env() {
    log "设置Python环境..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        
        # 创建虚拟环境
        python3 -m venv venv
        
        # 激活虚拟环境
        source venv/bin/activate
        
        # 升级pip
        pip install --upgrade pip
        
        # 安装依赖
        if [ -f 'requirements.txt' ]; then
            pip install -r requirements.txt
        elif [ -f 'requirements/prod.txt' ]; then
            pip install -r requirements/prod.txt
        else
            # 安装基本依赖
            pip install django djangorestframework django-cors-headers
        fi
        
        log 'Python环境设置完成'
    "
}

# 配置Django
setup_django() {
    log "配置Django..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        source venv/bin/activate
        
        # 设置环境变量
        export DJANGO_SETTINGS_MODULE=settings
        export DJANGO_DEBUG=False
        export DJANGO_SECRET_KEY='your-secret-key-here'
        
        # 运行数据库迁移
        python manage.py migrate
        
        # 收集静态文件
        python manage.py collectstatic --noinput
        
        # 创建超级用户（如果不存在）
        echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@qatoolbox.com', 'admin123456')\" | python manage.py shell
        
        log 'Django配置完成'
    "
}

# 创建启动脚本
create_startup_script() {
    log "创建启动脚本..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        
        # 创建启动脚本
        cat > start_server.sh << 'EOF'
#!/bin/bash
cd $PROJECT_PATH
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=settings
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='your-secret-key-here'
python manage.py runserver 0.0.0.0:8000
EOF
        
        chmod +x start_server.sh
        
        # 创建后台启动脚本
        cat > start_server_background.sh << 'EOF'
#!/bin/bash
cd $PROJECT_PATH
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=settings
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='your-secret-key-here'
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
echo \$! > server.pid
echo '服务器已启动，PID: '\$(cat server.pid)
echo '查看日志: tail -f server.log'
EOF
        
        chmod +x start_server_background.sh
        
        # 创建停止脚本
        cat > stop_server.sh << 'EOF'
#!/bin/bash
if [ -f server.pid ]; then
    PID=\$(cat server.pid)
    if kill -0 \$PID 2>/dev/null; then
        kill \$PID
        echo '服务器已停止 (PID: '\$PID')'
    else
        echo '服务器进程不存在'
    fi
    rm -f server.pid
else
    echo '未找到PID文件'
fi
EOF
        
        chmod +x stop_server.sh
        
        log '启动脚本创建完成'
    "
}

# 启动服务器
start_server() {
    log "启动服务器..."
    ssh $SERVER_USER@$SERVER_IP "
        cd $PROJECT_PATH
        
        # 停止现有服务器
        if [ -f stop_server.sh ]; then
            ./stop_server.sh
        fi
        
        # 启动服务器
        ./start_server_background.sh
        
        # 等待服务器启动
        sleep 5
        
        # 检查服务器状态
        if curl -s http://localhost:8000/ > /dev/null; then
            log '服务器启动成功！'
        else
            warn '服务器启动可能有问题，请检查日志'
        fi
    "
}

# 显示部署信息
show_deployment_info() {
    log "部署完成！"
    echo
    echo "=========================================="
    echo "           QAToolBox 部署信息"
    echo "=========================================="
    echo "服务器IP: $SERVER_IP"
    echo "项目路径: $PROJECT_PATH"
    echo "访问地址: http://$SERVER_IP:8000"
    echo "管理员账号: admin"
    echo "管理员密码: admin123456"
    echo "=========================================="
    echo
    echo "常用命令："
    echo "  启动服务器: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && ./start_server_background.sh'"
    echo "  停止服务器: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && ./stop_server.sh'"
    echo "  查看日志: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH && tail -f server.log'"
    echo "  进入项目目录: ssh $SERVER_USER@$SERVER_IP 'cd $PROJECT_PATH'"
    echo
}

# 主部署流程
main() {
    log "开始部署QAToolBox到服务器 $SERVER_IP..."
    
    # 检查SSH连接
    check_ssh
    
    # 安装系统依赖
    install_system_deps
    
    # 克隆项目代码
    clone_project
    
    # 设置Python环境
    setup_python_env
    
    # 配置Django
    setup_django
    
    # 创建启动脚本
    create_startup_script
    
    # 启动服务器
    start_server
    
    # 显示部署信息
    show_deployment_info
}

# 执行主函数
main "$@" 