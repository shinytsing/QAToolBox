#!/bin/bash

# QAToolBox 重新设置数据库密码脚本
# 重新生成密码并确保环境变量正确

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
log_info "QAToolBox 重新设置数据库密码脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 生成新的数据库密码
DB_PASSWORD=$(openssl rand -base64 16)
log_info "生成新的数据库密码: $DB_PASSWORD"

# 2. 重新设置PostgreSQL用户密码
log_info "重新设置PostgreSQL用户密码..."

# 确保PostgreSQL服务运行
systemctl start postgresql
systemctl enable postgresql

# 重新设置用户密码
sudo -u postgres psql -c "ALTER USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
sudo -u postgres psql -c "ALTER USER qatoolbox SUPERUSER;"

# 3. 更新.env文件
log_info "更新.env文件..."

# 更新DB_PASSWORD
if grep -q "DB_PASSWORD=" .env; then
    sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env
else
    echo "DB_PASSWORD=$DB_PASSWORD" >> .env
fi

# 确保其他数据库环境变量存在
if ! grep -q "DB_NAME=" .env; then
    echo "DB_NAME=qatoolbox_production" >> .env
fi

if ! grep -q "DB_USER=" .env; then
    echo "DB_USER=qatoolbox" >> .env
fi

if ! grep -q "DB_HOST=" .env; then
    echo "DB_HOST=localhost" >> .env
fi

if ! grep -q "DB_PORT=" .env; then
    echo "DB_PORT=5432" >> .env
fi

if ! grep -q "DB_ENGINE=" .env; then
    echo "DB_ENGINE=django.db.backends.postgresql" >> .env
fi

# 4. 验证.env文件
log_info "验证.env文件内容..."
log_info "数据库相关环境变量："
grep -E "DB_|DATABASE_" .env || echo "未找到数据库环境变量"

# 5. 设置环境变量并测试连接
log_info "设置环境变量并测试连接..."
export DB_NAME=qatoolbox_production
export DB_USER=qatoolbox
export DB_PASSWORD=$DB_PASSWORD
export DB_HOST=localhost
export DB_PORT=5432
export DB_ENGINE=django.db.backends.postgresql

# 直接测试PostgreSQL连接
log_info "测试PostgreSQL连接..."
sudo -u postgres psql -c "SELECT 1;" -d qatoolbox_production

# 测试Django数据库连接
log_info "测试Django数据库连接..."
python manage.py shell -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('✅ Django数据库连接成功')
except Exception as e:
    print(f'❌ Django数据库连接失败: {e}')
    exit(1)
"

# 6. 使用--fake-initial运行迁移
log_info "使用--fake-initial运行迁移..."
python manage.py migrate --fake-initial

# 7. 运行剩余迁移
log_info "运行剩余迁移..."
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
log_success "数据库密码重新设置完成！"
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
