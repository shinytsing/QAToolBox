#!/bin/bash

# QAToolBox 备份脚本
# 使用方法: ./backup.sh

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="qatoolbox_backup_${DATE}.tar.gz"

echo "📦 开始备份 QAToolBox..."

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
echo "🗄️ 备份数据库..."
docker-compose exec -T db pg_dump -U qatoolbox qatoolbox_production > $BACKUP_DIR/db_backup_${DATE}.sql

# 备份媒体文件
echo "📁 备份媒体文件..."
docker-compose exec -T web tar -czf - /app/media > $BACKUP_DIR/media_backup_${DATE}.tar.gz

# 备份静态文件
echo "🎨 备份静态文件..."
docker-compose exec -T web tar -czf - /app/staticfiles > $BACKUP_DIR/static_backup_${DATE}.tar.gz

# 备份日志文件
echo "📝 备份日志文件..."
docker-compose exec -T web tar -czf - /app/logs > $BACKUP_DIR/logs_backup_${DATE}.tar.gz

# 创建完整备份
echo "📦 创建完整备份..."
tar -czf $BACKUP_DIR/$BACKUP_FILE \
    $BACKUP_DIR/db_backup_${DATE}.sql \
    $BACKUP_DIR/media_backup_${DATE}.tar.gz \
    $BACKUP_DIR/static_backup_${DATE}.tar.gz \
    $BACKUP_DIR/logs_backup_${DATE}.tar.gz

# 清理临时文件
rm -f $BACKUP_DIR/db_backup_${DATE}.sql
rm -f $BACKUP_DIR/media_backup_${DATE}.tar.gz
rm -f $BACKUP_DIR/static_backup_${DATE}.tar.gz
rm -f $BACKUP_DIR/logs_backup_${DATE}.tar.gz

echo "✅ 备份完成: $BACKUP_DIR/$BACKUP_FILE"

# 保留最近7天的备份
echo "🧹 清理旧备份..."
find $BACKUP_DIR -name "qatoolbox_backup_*.tar.gz" -mtime +7 -delete

echo "🎉 备份任务完成！"
