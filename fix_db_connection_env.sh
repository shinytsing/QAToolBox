#!/bin/bash

# QAToolBox 环境变量数据库连接修复脚本
# 正确设置Django需要的环境变量

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

log_info "=========================================="
log_info "QAToolBox 环境变量数据库连接修复脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 检查当前环境变量配置
log_info "检查当前环境变量配置..."
if [[ -f ".env" ]]; then
    log_info "当前.env文件内容："
    cat .env
else
    log_error ".env文件不存在"
    exit 1
fi

# 2. 生成数据库密码
DB_PASSWORD=$(openssl rand -base64 16)
log_info "生成数据库密码: $DB_PASSWORD"

# 3. 修复PostgreSQL用户权限
log_info "修复PostgreSQL用户权限..."

# 确保PostgreSQL服务运行
systemctl start postgresql
systemctl enable postgresql

# 修改现有用户密码和权限
log_info "修改现有qatoolbox用户密码和权限..."
sudo -u postgres psql -c "ALTER USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
sudo -u postgres psql -c "ALTER USER qatoolbox SUPERUSER;"

# 重新创建数据库
log_info "重新创建数据库..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox_production;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE qatoolbox_production OWNER qatoolbox;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox_production TO qatoolbox;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON SCHEMA public TO qatoolbox;"

# 4. 更新环境变量 - 设置Django需要的单独变量
log_info "更新环境变量..."

# 更新或添加Django需要的数据库环境变量
if grep -q "DB_NAME=" .env; then
    sed -i "s|DB_NAME=.*|DB_NAME=qatoolbox_production|g" .env
else
    echo "DB_NAME=qatoolbox_production" >> .env
fi

if grep -q "DB_USER=" .env; then
    sed -i "s|DB_USER=.*|DB_USER=qatoolbox|g" .env
else
    echo "DB_USER=qatoolbox" >> .env
fi

if grep -q "DB_PASSWORD=" .env; then
    sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env
else
    echo "DB_PASSWORD=$DB_PASSWORD" >> .env
fi

if grep -q "DB_HOST=" .env; then
    sed -i "s|DB_HOST=.*|DB_HOST=localhost|g" .env
else
    echo "DB_HOST=localhost" >> .env
fi

if grep -q "DB_PORT=" .env; then
    sed -i "s|DB_PORT=.*|DB_PORT=5432|g" .env
else
    echo "DB_PORT=5432" >> .env
fi

# 设置数据库引擎
if grep -q "DB_ENGINE=" .env; then
    sed -i "s|DB_ENGINE=.*|DB_ENGINE=django.db.backends.postgresql|g" .env
else
    echo "DB_ENGINE=django.db.backends.postgresql" >> .env
fi

# 检查是否已有SECRET_KEY
if ! grep -q "DJANGO_SECRET_KEY" .env; then
    SECRET_KEY=$(openssl rand -base64 32)
    echo "DJANGO_SECRET_KEY=$SECRET_KEY" >> .env
fi

# 检查是否已有ALLOWED_HOSTS
if ! grep -q "ALLOWED_HOSTS" .env; then
    echo "ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,47.103.143.152,shenyiqing.xin,www.shenyiqing.xin" >> .env
fi

# 5. 验证环境变量
log_info "验证环境变量..."
log_info "更新后的.env文件内容："
cat .env

# 6. 设置环境变量并测试数据库连接
log_info "设置环境变量并测试数据库连接..."
export DB_NAME=qatoolbox_production
export DB_USER=qatoolbox
export DB_PASSWORD=$DB_PASSWORD
export DB_HOST=localhost
export DB_PORT=5432
export DB_ENGINE=django.db.backends.postgresql

python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('✅ 数据库连接成功')
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

# 7. 运行数据库迁移
log_info "运行数据库迁移..."
python manage.py migrate

# 8. 创建超级用户
log_info "创建超级用户..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@shenyiqing.xin', 'admin123456')
    print('✅ 超级用户创建成功')
else:
    print('ℹ️  超级用户已存在')
"

# 9. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput

# 10. 测试应用启动
log_info "测试应用启动..."
python manage.py check

log_success "=========================================="
log_success "数据库连接修复完成！"
log_success "=========================================="
echo
log_info "📱 访问信息:"
echo "  - 应用地址: http://47.103.143.152"
echo "  - 管理后台: http://47.103.143.152/admin/"
echo "  - 用户名: admin"
echo "  - 密码: admin123456"
echo
log_info "🗄️  数据库信息:"
echo "  - 数据库: qatoolbox_production"
echo "  - 用户: qatoolbox"
echo "  - 密码: $DB_PASSWORD"
echo
log_info "🛠️  下一步操作:"
echo "  - 启动应用: systemctl start qatoolbox"
echo "  - 查看状态: systemctl status qatoolbox"
echo "  - 查看日志: journalctl -u qatoolbox -f"
echo
log_success "现在可以启动应用了！"
log_success "=========================================="
