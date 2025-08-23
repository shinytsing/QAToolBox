# QAToolBox 数据库迁移和维护指南

## 📋 概述
本指南详细说明了QAToolBox项目的数据库迁移、备份恢复和日常维护操作。

## 🗄️ 数据库迁移

### 初次部署迁移
```bash
# 进入项目目录
cd /opt/QAToolbox

# 运行初始迁移
docker-compose -f docker-compose.simple.yml exec web python manage.py migrate

# 创建超级用户
docker-compose -f docker-compose.simple.yml exec web python manage.py createsuperuser

# 收集静态文件
docker-compose -f docker-compose.simple.yml exec web python manage.py collectstatic --noinput
```

### 应用更新后的迁移
```bash
# 拉取最新代码
git pull origin main

# 重新构建镜像
docker-compose -f docker-compose.simple.yml build

# 停止服务
docker-compose -f docker-compose.simple.yml down

# 启动数据库服务
docker-compose -f docker-compose.simple.yml up -d db redis

# 等待数据库启动
sleep 10

# 运行迁移
docker-compose -f docker-compose.simple.yml run --rm web python manage.py migrate

# 收集静态文件
docker-compose -f docker-compose.simple.yml run --rm web python manage.py collectstatic --noinput

# 启动所有服务
docker-compose -f docker-compose.simple.yml up -d
```

### 查看迁移状态
```bash
# 查看所有应用的迁移状态
docker-compose -f docker-compose.simple.yml exec web python manage.py showmigrations

# 查看特定应用的迁移状态
docker-compose -f docker-compose.simple.yml exec web python manage.py showmigrations tools

# 查看未应用的迁移
docker-compose -f docker-compose.simple.yml exec web python manage.py showmigrations --plan
```

## 💾 数据库备份

### 创建备份脚本
```bash
# 创建备份目录
sudo mkdir -p /opt/backups/qatoolbox
sudo chown $USER:$USER /opt/backups/qatoolbox

# 创建备份脚本
cat > /opt/backups/backup_qatoolbox.sh << 'EOF'
#!/bin/bash

# QAToolBox 数据库备份脚本
BACKUP_DIR="/opt/backups/qatoolbox"
DATE=$(date +"%Y%m%d_%H%M%S")
PROJECT_DIR="/opt/QAToolbox"

echo "开始备份 QAToolBox 数据库..."

# 创建备份目录
mkdir -p $BACKUP_DIR/db
mkdir -p $BACKUP_DIR/media

# 备份数据库
cd $PROJECT_DIR
docker-compose -f docker-compose.simple.yml exec -T db pg_dump -U postgres -d qatoolbox > $BACKUP_DIR/db/backup_$DATE.sql

# 压缩数据库备份
gzip $BACKUP_DIR/db/backup_$DATE.sql

# 备份媒体文件
tar -czf $BACKUP_DIR/media/media_backup_$DATE.tar.gz -C $PROJECT_DIR media/

# 备份环境配置
cp $PROJECT_DIR/.env $BACKUP_DIR/.env_$DATE

echo "数据库备份完成: $BACKUP_DIR/db/backup_$DATE.sql.gz"
echo "媒体备份完成: $BACKUP_DIR/media/media_backup_$DATE.tar.gz"

# 清理7天前的备份
find $BACKUP_DIR/db -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR/media -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -name ".env_*" -mtime +7 -delete

echo "旧备份清理完成"
EOF

# 添加执行权限
chmod +x /opt/backups/backup_qatoolbox.sh
```

### 手动备份
```bash
# 运行备份脚本
/opt/backups/backup_qatoolbox.sh

# 或者直接备份数据库
docker-compose -f docker-compose.simple.yml exec -T db pg_dump -U postgres -d qatoolbox > backup_$(date +%Y%m%d).sql
```

### 自动备份设置
```bash
# 编辑crontab
crontab -e

# 添加以下行，每天凌晨2点备份
0 2 * * * /opt/backups/backup_qatoolbox.sh >> /var/log/qatoolbox_backup.log 2>&1

# 查看crontab设置
crontab -l
```

## 🔄 数据库恢复

### 从备份恢复
```bash
# 停止应用服务（保留数据库服务）
docker-compose -f docker-compose.simple.yml stop web celery

# 进入数据库容器
docker-compose -f docker-compose.simple.yml exec db bash

# 在容器内执行恢复
dropdb -U postgres qatoolbox
createdb -U postgres qatoolbox

# 退出容器
exit

# 从宿主机恢复数据
gunzip -c /opt/backups/qatoolbox/db/backup_YYYYMMDD_HHMMSS.sql.gz | \
docker-compose -f docker-compose.simple.yml exec -T db psql -U postgres -d qatoolbox

# 重启所有服务
docker-compose -f docker-compose.simple.yml restart
```

### 恢复媒体文件
```bash
# 停止web服务
docker-compose -f docker-compose.simple.yml stop web

# 恢复媒体文件
cd /opt/QAToolbox
tar -xzf /opt/backups/qatoolbox/media/media_backup_YYYYMMDD_HHMMSS.tar.gz

# 重启web服务
docker-compose -f docker-compose.simple.yml start web
```

## 🔧 数据库维护

### 数据库优化
```bash
# 分析数据库性能
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT schemaname,tablename,attname,n_distinct,correlation 
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY n_distinct DESC;
"

# 重建索引
docker-compose -f docker-compose.simple.yml exec web python manage.py shell -c "
from django.core.management import call_command
from django.db import connection
cursor = connection.cursor()
cursor.execute('REINDEX DATABASE qatoolbox;')
"

# 更新统计信息
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "ANALYZE;"
```

### 清理过期数据
```bash
# 创建数据清理脚本
cat > /opt/QAToolbox/cleanup_data.py << 'EOF'
#!/usr/bin/env python
import os
import django
from datetime import datetime, timedelta

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry

def cleanup_old_data():
    """清理过期数据"""
    now = datetime.now()
    
    # 清理过期会话（30天前）
    expired_sessions = Session.objects.filter(expire_date__lt=now - timedelta(days=30))
    sessions_count = expired_sessions.count()
    expired_sessions.delete()
    print(f"已删除 {sessions_count} 个过期会话")
    
    # 清理旧的日志记录（90天前）
    old_logs = LogEntry.objects.filter(action_time__lt=now - timedelta(days=90))
    logs_count = old_logs.count()
    old_logs.delete()
    print(f"已删除 {logs_count} 条旧日志记录")
    
    print("数据清理完成")

if __name__ == '__main__':
    cleanup_old_data()
EOF

# 运行数据清理
docker-compose -f docker-compose.simple.yml exec web python /app/cleanup_data.py
```

### 监控数据库大小
```bash
# 检查数据库大小
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE pg_database.datname = 'qatoolbox';
"

# 检查表大小
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.'||tablename) DESC;
"
```

## 📊 数据库监控

### 连接数监控
```bash
# 查看当前连接数
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT count(*) as connections FROM pg_stat_activity;
"

# 查看连接详情
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT datname, usename, state, query_start 
FROM pg_stat_activity 
WHERE datname = 'qatoolbox';
"
```

### 性能监控
```bash
# 查看慢查询
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
"

# 查看锁等待
docker-compose -f docker-compose.simple.yml exec db psql -U postgres -d qatoolbox -c "
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
"
```

## 🛠️ 故障排除

### 常见问题解决

1. **迁移失败**
```bash
# 查看详细错误信息
docker-compose -f docker-compose.simple.yml exec web python manage.py migrate --verbosity=2

# 假迁移（不实际执行）
docker-compose -f docker-compose.simple.yml exec web python manage.py migrate --fake

# 回滚到特定迁移
docker-compose -f docker-compose.simple.yml exec web python manage.py migrate tools 0001
```

2. **数据库连接问题**
```bash
# 检查数据库服务状态
docker-compose -f docker-compose.simple.yml ps db

# 查看数据库日志
docker-compose -f docker-compose.simple.yml logs db

# 测试数据库连接
docker-compose -f docker-compose.simple.yml exec web python manage.py dbshell
```

3. **权限问题**
```bash
# 检查文件权限
ls -la /opt/QAToolbox/

# 修复权限
sudo chown -R $USER:$USER /opt/QAToolbox/
```

## 📝 最佳实践

1. **定期备份**：设置自动备份，建议每日备份
2. **监控空间**：定期检查数据库和存储空间
3. **测试恢复**：定期测试备份恢复流程
4. **版本管理**：升级前先备份
5. **日志监控**：监控数据库和应用日志
6. **性能调优**：定期分析慢查询和优化

## ⚠️ 注意事项

- 在生产环境执行迁移前务必备份
- 大型迁移可能需要停机时间
- 监控迁移过程中的锁等待
- 确保有足够的磁盘空间进行备份
- 定期清理日志和临时文件

---

📞 **如有问题**，请查看日志文件：
- 应用日志：`docker-compose logs web`
- 数据库日志：`docker-compose logs db`
- 系统日志：`/var/log/messages`
