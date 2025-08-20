#!/bin/bash

# 数据库备份脚本
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 配置
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${DATE}.json"
MEDIA_BACKUP_FILE="media_backup_${DATE}.tar.gz"

# 创建备份目录
create_backup_dir() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log_info "创建备份目录: $BACKUP_DIR"
    fi
}

# 数据库备份
backup_database() {
    log_info "开始数据库备份..."
    
    cd "$BACKUP_DIR"
    
    # Django数据导出
    python ../../manage.py dumpdata --exclude auth.permission --exclude contenttypes > "$BACKUP_FILE"
    
    # 压缩备份文件
    gzip "$BACKUP_FILE"
    
    log_info "数据库备份完成: $BACKUP_FILE.gz"
}

# 媒体文件备份
backup_media() {
    log_info "开始媒体文件备份..."
    
    if [ -d "../../media" ]; then
        tar -czf "$BACKUP_DIR/$MEDIA_BACKUP_FILE" -C ../../ media/
        log_info "媒体文件备份完成: $MEDIA_BACKUP_FILE"
    else
        log_warn "媒体目录不存在，跳过媒体文件备份"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份文件..."
    
    # 保留最近30天的备份
    find "$BACKUP_DIR" -name "backup_*.json.gz" -mtime +30 -delete
    find "$BACKUP_DIR" -name "media_backup_*.tar.gz" -mtime +30 -delete
    
    log_info "旧备份清理完成"
}

# 备份验证
verify_backup() {
    log_info "验证备份文件..."
    
    if [ -f "$BACKUP_DIR/$BACKUP_FILE.gz" ]; then
        log_info "数据库备份文件验证成功"
    else
        log_error "数据库备份文件验证失败"
        exit 1
    fi
    
    if [ -f "$BACKUP_DIR/$MEDIA_BACKUP_FILE" ]; then
        log_info "媒体文件备份验证成功"
    fi
}

# 主函数
main() {
    log_info "开始备份流程..."
    
    # 创建备份目录
    create_backup_dir
    
    # 数据库备份
    backup_database
    
    # 媒体文件备份
    backup_media
    
    # 清理旧备份
    cleanup_old_backups
    
    # 验证备份
    verify_backup
    
    log_info "备份流程完成！"
    log_info "备份文件位置: $BACKUP_DIR"
}

# 执行主函数
main "$@"
