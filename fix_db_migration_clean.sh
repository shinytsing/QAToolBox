#!/bin/bash

# QAToolBox 数据库迁移清理修复脚本
# 清理数据库表并重新迁移

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
log_info "QAToolBox 数据库迁移清理修复脚本"
log_info "=========================================="

# 进入项目目录
cd /home/admin/QAToolbox

# 激活虚拟环境
source venv/bin/activate

# 1. 设置环境变量
log_info "设置环境变量..."
export DB_NAME=qatoolbox_production
export DB_USER=qatoolbox
export DB_PASSWORD=$(grep "DB_PASSWORD=" .env | cut -d'=' -f2)
export DB_HOST=localhost
export DB_PORT=5432
export DB_ENGINE=django.db.backends.postgresql

log_info "数据库连接信息:"
echo "  - 数据库: $DB_NAME"
echo "  - 用户: $DB_USER"
echo "  - 主机: $DB_HOST:$DB_PORT"

# 2. 清理数据库表
log_info "清理数据库表..."

# 连接到PostgreSQL并删除所有表
sudo -u postgres psql -d qatoolbox_production -c "
DO \$\$ 
DECLARE
    r RECORD;
BEGIN
    -- 删除所有表
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
    
    -- 删除所有序列
    FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public')
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || quote_ident(r.sequence_name) || ' CASCADE';
    END LOOP;
    
    -- 删除所有视图
    FOR r IN (SELECT viewname FROM pg_views WHERE schemaname = 'public')
    LOOP
        EXECUTE 'DROP VIEW IF EXISTS ' || quote_ident(r.viewname) || ' CASCADE';
    END LOOP;
    
    -- 删除所有函数
    FOR r IN (SELECT proname, oidvectortypes(proargtypes) as args FROM pg_proc INNER JOIN pg_namespace ns ON (pg_proc.pronamespace = ns.oid) WHERE ns.nspname = 'public')
    LOOP
        EXECUTE 'DROP FUNCTION IF EXISTS ' || quote_ident(r.proname) || '(' || r.args || ') CASCADE';
    END LOOP;
END \$\$;
"

log_success "数据库表清理完成"

# 3. 重置Django迁移状态
log_info "重置Django迁移状态..."
python manage.py migrate --fake-initial

# 4. 运行数据库迁移
log_info "运行数据库迁移..."
python manage.py migrate

# 5. 创建超级用户
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

# 6. 收集静态文件
log_info "收集静态文件..."
python manage.py collectstatic --noinput

# 7. 测试应用启动
log_info "测试应用启动..."
python manage.py check

log_success "=========================================="
log_success "数据库迁移清理修复完成！"
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
