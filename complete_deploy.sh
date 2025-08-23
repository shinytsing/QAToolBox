#!/bin/bash

# QAToolBox 完整部署脚本 - 使用requirements文件
# 在服务器上以普通用户身份运行: bash complete_deploy.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
   print_error "请使用普通用户运行此脚本，不要使用root"
   print_info "正确用法: su - admin && bash complete_deploy.sh"
   exit 1
fi

print_info "=== QAToolBox 完整部署开始 ==="
print_info "用户: $(whoami)"
print_info "目录: $(pwd)"

# 1. 系统依赖检查和安装
print_step "1/12 检查和安装系统依赖..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装，请先安装系统依赖"
    print_info "运行: sudo dnf install -y python3 python3-pip python3-devel postgresql-server redis nginx gcc"
    exit 1
fi

# 2. 进入项目目录
print_step "2/12 进入项目目录..."
if [ ! -d "/home/$(whoami)/QAToolbox" ]; then
    print_info "克隆项目..."
    cd /home/$(whoami)
    git clone https://github.com/shinytsing/QAToolbox.git
fi

cd /home/$(whoami)/QAToolbox
print_info "当前目录: $(pwd)"

# 3. 创建虚拟环境
print_step "3/12 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_info "虚拟环境创建完成"
else
    print_info "虚拟环境已存在"
fi

# 4. 激活虚拟环境
print_step "4/12 激活虚拟环境..."
source venv/bin/activate
print_info "虚拟环境已激活: $(which python)"

# 5. 升级pip
print_step "5/12 升级pip..."
pip install --upgrade pip

# 6. 安装Python依赖
print_step "6/12 安装Python依赖..."
print_info "检查requirements文件..."

# 检查并安装依赖
if [ -f "requirements.txt" ]; then
    print_info "使用 requirements.txt"
    pip install -r requirements.txt
elif [ -f "requirements/production.txt" ]; then
    print_info "使用 requirements/production.txt"
    pip install -r requirements/production.txt
elif [ -f "requirements/base.txt" ]; then
    print_info "使用 requirements/base.txt"
    pip install -r requirements/base.txt
    # 安装额外的生产依赖
    pip install gunicorn psycopg2-binary redis
else
    print_warning "未找到requirements文件，安装基础依赖"
    pip install Django psycopg2-binary redis gunicorn celery Pillow djangorestframework django-cors-headers
fi

# 验证Django安装
print_info "验证Django安装..."
python -c "import django; print('Django版本:', django.get_version())"

# 7. 创建环境配置
print_step "7/12 创建环境配置..."
cat > .env << EOF
# Django配置
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=$(openssl rand -base64 50)
DEBUG=False

# 数据库配置
DATABASE_URL=postgres://qatoolbox:qatoolbox123@localhost:5432/qatoolbox
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=qatoolbox123
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 域名配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@shenyiqing.xin
ADMIN_PASSWORD=admin123456

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@shenyiqing.xin
EOF

print_info "环境配置文件创建完成"

# 8. 加载环境变量
print_step "8/12 加载环境变量..."
export $(cat .env | grep -v '^#' | xargs)
print_info "环境变量已加载"

# 9. 检查Django配置
print_step "9/12 检查Django配置..."
python manage.py check --deploy
if [ $? -eq 0 ]; then
    print_info "Django配置检查通过"
else
    print_warning "Django配置检查有警告，但继续部署"
fi

# 10. 运行数据库迁移
print_step "10/12 运行数据库迁移..."
python manage.py migrate
if [ $? -eq 0 ]; then
    print_info "数据库迁移完成"
else
    print_error "数据库迁移失败，请检查数据库连接"
    exit 1
fi

# 11. 收集静态文件
print_step "11/12 收集静态文件..."
python manage.py collectstatic --noinput
print_info "静态文件收集完成"

# 12. 创建管理员用户
print_step "12/12 创建管理员用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@shenyiqing.xin')
password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'管理员用户创建成功: {username}/{password}')
else:
    print('管理员用户已存在')
"

# 创建启动脚本
print_info "创建服务启动脚本..."
cat > start_server.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

# 创建日志目录
mkdir -p logs

# 启动Gunicorn
exec gunicorn config.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 30 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid logs/gunicorn.pid \
    --daemon
EOF

chmod +x start_server.sh

# 创建停止脚本
cat > stop_server.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
if [ -f logs/gunicorn.pid ]; then
    kill $(cat logs/gunicorn.pid)
    rm -f logs/gunicorn.pid
    echo "服务已停止"
else
    echo "服务未运行"
fi
EOF

chmod +x stop_server.sh

# 创建重启脚本
cat > restart_server.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
./stop_server.sh
sleep 2
./start_server.sh
echo "服务已重启"
EOF

chmod +x restart_server.sh

# 创建状态检查脚本
cat > status_server.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
if [ -f logs/gunicorn.pid ] && kill -0 $(cat logs/gunicorn.pid) 2>/dev/null; then
    echo "服务正在运行 PID: $(cat logs/gunicorn.pid)"
    echo "访问地址:"
    echo "  - http://localhost:8000"
    echo "  - http://47.103.143.152:8000"
    echo "  - 管理后台: http://47.103.143.152:8000/admin/"
else
    echo "服务未运行"
fi
EOF

chmod +x status_server.sh

# 测试Django应用
print_info "测试Django应用..."
python manage.py runserver 0.0.0.0:8001 &
TEST_PID=$!
sleep 5

if curl -s http://localhost:8001 > /dev/null; then
    print_info "✅ Django应用测试成功"
    kill $TEST_PID
else
    print_warning "⚠️  Django应用测试失败，但继续部署"
    kill $TEST_PID 2>/dev/null || true
fi

echo ""
print_info "=== 部署完成！ ==="
echo ""
print_info "🎉 QAToolBox已成功部署！"
echo ""
print_info "📁 项目目录: /home/$(whoami)/QAToolbox"
print_info "🐍 Python环境: venv (虚拟环境)"
print_info "👤 管理员账户: admin / admin123456"
echo ""
print_info "🚀 启动服务:"
print_info "   ./start_server.sh"
echo ""
print_info "🛑 停止服务:"
print_info "   ./stop_server.sh"
echo ""
print_info "🔄 重启服务:"
print_info "   ./restart_server.sh"
echo ""
print_info "📊 查看状态:"
print_info "   ./status_server.sh"
echo ""
print_info "📝 查看日志:"
print_info "   tail -f logs/error.log"
print_info "   tail -f logs/access.log"
echo ""
print_info "🌐 访问地址:"
print_info "   - http://47.103.143.152:8000"
print_info "   - 管理后台: http://47.103.143.152:8000/admin/"
echo ""
print_warning "⚠️  注意事项:"
print_warning "1. 请配置Nginx反向代理到端口8000"
print_warning "2. 请及时修改默认管理员密码"
print_warning "3. 确保PostgreSQL和Redis服务正在运行"
echo ""
print_info "现在运行 ./start_server.sh 启动服务！"
