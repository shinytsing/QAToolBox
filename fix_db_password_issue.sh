#!/bin/bash

# QAToolBox 修复密码问题脚本
# 修复密码读取和Django连接问题

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
log_info "QAToolBox 修复密码问题脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 重新生成密码并更新PostgreSQL
log_info "重新生成密码并更新PostgreSQL..."
DB_PASSWORD=$(openssl rand -base64 16)
log_info "新密码: $DB_PASSWORD"

# 更新PostgreSQL密码
sudo -u postgres psql -c "ALTER USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"

# 2. 更新.env文件
log_info "更新.env文件..."
# 使用更安全的方式更新密码
sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$DB_PASSWORD|g" .env

# 3. 验证.env文件
log_info "验证.env文件中的密码..."
grep "DB_PASSWORD=" .env

# 4. 设置环境变量
log_info "设置环境变量..."
export DB_NAME=qatoolbox_production
export DB_USER=qatoolbox
export DB_PASSWORD=$DB_PASSWORD
export DB_HOST=localhost
export DB_PORT=5432
export DB_ENGINE=django.db.backends.postgresql

# 5. 测试PostgreSQL连接
log_info "测试PostgreSQL连接..."
sudo -u postgres psql -c "SELECT 1;" -d qatoolbox_production

# 6. 测试Django数据库连接
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

# 7. 手动标记users.0011_auto_20250901_0056迁移为已应用
log_info "手动标记users.0011_auto_20250901_0056迁移为已应用..."
python manage.py shell -c "
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

# 创建迁移记录器
recorder = MigrationRecorder(connection)

# 手动标记迁移为已应用
recorder.record_applied('users', '0011_auto_20250901_0056')
print('✅ 迁移users.0011_auto_20250901_0056已标记为已应用')
"

# 8. 运行剩余迁移
log_info "运行剩余迁移..."
python manage.py migrate

# 9. 创建超级用户
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

# 10. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput

# 11. 测试应用启动
log_info "测试应用启动..."
python manage.py check

log_success "=========================================="
log_success "密码问题修复完成！"
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
