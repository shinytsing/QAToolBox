#!/bin/bash

# QAToolBox 数据备份脚本

set -e

BACKUP_DIR="/home/$(whoami)/backups"
DATE=$(date +%Y%m%d_%H%M%S)

echo "🗄️ 开始备份数据..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份数据库
echo "备份数据库..."
docker-compose -f docker-compose.china.yml exec -T db pg_dump -U qatoolbox qatoolbox > "$BACKUP_DIR/db_backup_$DATE.sql"

# 备份媒体文件
echo "备份媒体文件..."
tar -czf "$BACKUP_DIR/media_backup_$DATE.tar.gz" -C . media/

# 备份配置文件
echo "备份配置文件..."
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" .env.production docker-compose.china.yml

# 清理7天前的备份
find "$BACKUP_DIR" -name "*backup*" -mtime +7 -delete

echo "✅ 备份完成！备份文件保存在: $BACKUP_DIR"
echo "数据库备份: db_backup_$DATE.sql"
echo "媒体文件备份: media_backup_$DATE.tar.gz"
echo "配置文件备份: config_backup_$DATE.tar.gz"

