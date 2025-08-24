#!/bin/bash

# QAToolBox Python 3.9 一键部署脚本
# 在服务器上以普通用户身份运行: bash complete_deploy_py39.sh

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
   print_info "正确用法: su - admin && bash complete_deploy_py39.sh"
   exit 1
fi

print_info "=== QAToolBox Python 3.9 一键部署开始 ==="
print_info "用户: $(whoami)"
print_info "目录: $(pwd)"

# 1. 检查Python 3.9
print_step "1/12 检查Python 3.9..."
if ! command -v python3.9 &> /dev/null; then
    print_error "Python 3.9 未找到！"
    print_info "请先安装: sudo dnf install -y python39 python39-pip python39-devel"
    exit 1
fi

PYTHON_VERSION=$(python3.9 --version)
print_info "Python版本: $PYTHON_VERSION"

# 2. 进入项目目录
print_step "2/12 进入项目目录..."
cd /home/$(whoami)/QAToolbox
print_info "当前目录: $(pwd)"

# 3. 清理旧环境
print_step "3/12 清理旧的虚拟环境..."
if [ -d "venv" ]; then
    print_warning "删除旧的虚拟环境..."
    rm -rf venv
fi

# 4. 创建Python 3.9虚拟环境
print_step "4/12 创建Python 3.9虚拟环境..."
python3.9 -m venv venv
print_info "虚拟环境创建完成"

# 5. 激活虚拟环境
print_step "5/12 激活虚拟环境..."
source venv/bin/activate
VENV_PYTHON_VERSION=$(python --version)
print_info "虚拟环境Python版本: $VENV_PYTHON_VERSION"
print_info "Python路径: $(which python)"

# 6. 升级pip
print_step "6/12 升级pip..."
pip install --upgrade pip
PIP_VERSION=$(pip --version)
print_info "Pip版本: $PIP_VERSION"

# 7. 安装Python依赖
print_step "7/12 安装Python依赖..."
print_info "安装Django 4.2和相关依赖..."

# 直接安装兼容的依赖版本
pip install \
    Django==4.2.7 \
    psycopg2-binary \
    redis \
    gunicorn \
    celery \
    Pillow \
    djangorestframework \
    django-cors-headers \
    python-decouple

# 验证Django安装
print_info "验证Django安装..."
DJANGO_VERSION=$(python -c "import django; print(django.get_version())")
print_info "Django版本: $DJANGO_VERSION"

# 8. 创建环境配置
print_step "8/12 创建环境配置..."
cat > .env << 'ENVEOF'
# Django配置
DJANGO_SETTINGS_MODULE=config.settings.production
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
ENVEOF

# 生成Django SECRET_KEY
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
echo "DJANGO_SECRET_KEY=$SECRET_KEY" >> .env

print_info "环境配置文件创建完成"

# 9. 加载环境变量
print_step "9/12 加载环境变量..."
export $(cat .env | grep -v '^#' | xargs)
print_info "环境变量已加载"

# 10. 检查Django配置
print_step "10/12 检查Django配置..."
python manage.py check --deploy || print_warning "Django配置检查有警告，但继续部署"

# 11. 运行数据库迁移
print_step "11/12 运行数据库迁移..."
python manage.py migrate
if [ $? -eq 0 ]; then
    print_info "数据库迁移完成"
else
    print_error "数据库迁移失败，请检查数据库连接"
    print_info "确保PostgreSQL正在运行: sudo systemctl status postgresql"
    exit 1
fi

# 12. 收集静态文件和创建管理员
print_step "12/12 收集静态文件和创建管理员..."
python manage.py collectstatic --noinput
print_info "静态文件收集完成"

python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@shenyiqing.xin')
password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'✅ 管理员用户创建成功: {username}/{password}')
else:
    print('ℹ️  管理员用户已存在')
"

# 创建服务管理脚本
print_info "创建服务管理脚本..."
mkdir -p logs

cat > start_server.sh << 'STARTEOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
source venv/bin/activate
export $(cat .env | grep -v '^#' | xargs)

# 检查端口是否被占用
if netstat -tuln | grep -q :8000; then
    echo "⚠️  端口8000已被占用，尝试停止现有服务..."
    pkill -f gunicorn || true
    sleep 2
fi

# 启动Gunicorn
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 30 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --pid logs/gunicorn.pid \
    --daemon

sleep 2

if [ -f logs/gunicorn.pid ] && kill -0 $(cat logs/gunicorn.pid) 2>/dev/null; then
    echo "🚀 服务启动成功！"
    echo "🌐 访问地址: http://47.103.143.152:8000"
    echo "🔧 管理后台: http://47.103.143.152:8000/admin/"
    echo "👤 管理员: admin/admin123456"
else
    echo "❌ 服务启动失败，请查看日志: tail -f logs/error.log"
fi
STARTEOF

cat > stop_server.sh << 'STOPEOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
if [ -f logs/gunicorn.pid ]; then
    kill $(cat logs/gunicorn.pid) 2>/dev/null || true
    rm -f logs/gunicorn.pid
    echo "🛑 服务已停止"
else
    echo "ℹ️  服务未运行"
fi
# 强制杀死所有gunicorn进程
pkill -f gunicorn || true
STOPEOF

cat > restart_server.sh << 'RESTARTEOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
echo "🔄 重启服务..."
./stop_server.sh
sleep 2
./start_server.sh
RESTARTEOF

cat > status_server.sh << 'STATUSEOF'
#!/bin/bash
cd /home/$(whoami)/QAToolbox
if [ -f logs/gunicorn.pid ] && kill -0 $(cat logs/gunicorn.pid) 2>/dev/null; then
    echo "✅ 服务正在运行 PID: $(cat logs/gunicorn.pid)"
    echo "🌐 访问地址: http://47.103.143.152:8000"
    echo "🔧 管理后台: http://47.103.143.152:8000/admin/"
    echo "👤 管理员: admin/admin123456"
    echo ""
    echo "📊 进程信息:"
    ps aux | grep gunicorn | grep -v grep
else
    echo "❌ 服务未运行"
    echo ""
    echo "🔍 检查端口占用:"
    netstat -tuln | grep :8000 || echo "端口8000未被占用"
fi
STATUSEOF

chmod +x start_server.sh stop_server.sh restart_server.sh status_server.sh

# 测试Django应用
print_info "测试Django应用..."
python manage.py runserver 0.0.0.0:8001 &
TEST_PID=$!
sleep 5

if curl -s http://localhost:8001 > /dev/null 2>&1; then
    print_info "✅ Django应用测试成功"
    kill $TEST_PID 2>/dev/null || true
else
    print_warning "⚠️  Django应用测试失败，但继续部署"
    kill $TEST_PID 2>/dev/null || true
fi

echo ""
print_info "=== 🎉 部署完成！ ==="
echo ""
print_info "📁 项目目录: /home/$(whoami)/QAToolbox"
print_info "🐍 Python版本: $VENV_PYTHON_VERSION"
print_info "🎯 Django版本: $DJANGO_VERSION"
print_info "👤 管理员账户: admin / admin123456"
echo ""
print_info "🚀 启动服务: ./start_server.sh"
print_info "🛑 停止服务: ./stop_server.sh"
print_info "🔄 重启服务: ./restart_server.sh"
print_info "📊 查看状态: ./status_server.sh"
echo ""
print_info "📝 查看日志:"
print_info "   tail -f logs/error.log    # 错误日志"
print_info "   tail -f logs/access.log   # 访问日志"
echo ""
print_info "🌐 访问地址:"
print_info "   - 主站: http://47.103.143.152:8000"
print_info "   - 管理后台: http://47.103.143.152:8000/admin/"
echo ""
print_warning "⚠️  重要提醒:"
print_warning "1. 请及时修改默认管理员密码"
print_warning "2. 确保PostgreSQL和Redis服务正在运行"
print_warning "3. 如需配置域名，请设置Nginx反向代理"
echo ""
print_info "🎯 现在运行 ./start_server.sh 启动服务！"
