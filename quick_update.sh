#!/bin/bash
# =============================================================================
# QAToolBox 快速更新脚本
# =============================================================================
# 快速更新已有部署到最新版本
# 保持数据不丢失，只更新代码和依赖
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# 配置变量
readonly PROJECT_USER="${PROJECT_USER:-qatoolbox}"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly VENV_NAME="venv_py312"
readonly BACKUP_DIR="/home/$PROJECT_USER/backups"

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_quick_update_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🔄 QAToolBox 快速更新脚本
========================================
✨ 特性:
  • 快速更新到最新版本
  • 保持数据不丢失
  • 自动备份重要文件
  • 智能依赖更新
  • 最小化停机时间
========================================
EOF
echo -e "${NC}"

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
        echo -e "${YELLOW}💡 使用命令: sudo $0${NC}"
        exit 1
    fi
}

# 检查项目是否存在
check_project() {
    echo -e "${BLUE}🔍 检查项目状态...${NC}"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}❌ 项目目录不存在: $PROJECT_DIR${NC}"
        echo -e "${YELLOW}💡 请先运行完整部署脚本${NC}"
        exit 1
    fi
    
    if [ ! -d "$PROJECT_DIR/$VENV_NAME" ]; then
        echo -e "${RED}❌ 虚拟环境不存在: $PROJECT_DIR/$VENV_NAME${NC}"
        echo -e "${YELLOW}💡 请先运行完整部署脚本${NC}"
        exit 1
    fi
    
    echo -e "   ✅ 项目检查通过"
}

# 创建备份
create_backup() {
    echo -e "${BLUE}💾 创建备份...${NC}"
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
        cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
        echo -e "   ✅ 数据库备份完成"
    fi
    
    # 备份环境配置
    if [ -f "$PROJECT_DIR/.env" ]; then
        cp "$PROJECT_DIR/.env" "$BACKUP_DIR/env_backup_$(date +%Y%m%d_%H%M%S).env"
        echo -e "   ✅ 环境配置备份完成"
    fi
    
    # 备份媒体文件
    if [ -d "$PROJECT_DIR/media" ]; then
        tar -czf "$BACKUP_DIR/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz" -C "$PROJECT_DIR" media
        echo -e "   ✅ 媒体文件备份完成"
    fi
    
    echo -e "   ✅ 所有备份完成"
}

# 停止服务
stop_services() {
    echo -e "${BLUE}🛑 停止服务...${NC}"
    
    # 停止Django服务
    if systemctl is-active --quiet qatoolbox; then
        systemctl stop qatoolbox
        echo -e "   ✅ Django服务已停止"
    fi
    
    # 停止Celery服务
    if systemctl is-active --quiet qatoolbox-celery; then
        systemctl stop qatoolbox-celery
        echo -e "   ✅ Celery服务已停止"
    fi
    
    # 停止Celery Beat服务
    if systemctl is-active --quiet qatoolbox-celerybeat; then
        systemctl stop qatoolbox-celerybeat
        echo -e "   ✅ Celery Beat服务已停止"
    fi
    
    echo -e "   ✅ 所有服务已停止"
}

# 更新代码
update_code() {
    echo -e "${BLUE}📥 更新代码...${NC}"
    
    cd "$PROJECT_DIR"
    
    # 保存当前分支
    CURRENT_BRANCH=$(git branch --show-current)
    echo -e "   当前分支: $CURRENT_BRANCH"
    
    # 获取最新代码
    git fetch origin
    
    # 检查是否有更新
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/main)
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        echo -e "   ℹ️ 代码已是最新版本"
        return 0
    fi
    
    # 更新到最新版本
    git reset --hard origin/main
    
    # 设置权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "   ✅ 代码更新完成"
}

# 更新依赖
update_dependencies() {
    echo -e "${BLUE}📚 更新依赖...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 升级pip
    pip install --upgrade pip setuptools wheel
    
    # 更新基础依赖
    pip install -r requirements/base.txt --upgrade
    
    # 更新开发依赖（如果存在）
    if [ -f "requirements/development.txt" ]; then
        pip install -r requirements/development.txt --upgrade
    fi
    
    # 更新可选依赖（如果存在）
    if [ -f "requirements/optional.txt" ]; then
        pip install -r requirements/optional.txt --upgrade
    fi
    
    # 设置权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$VENV_NAME"
    
    echo -e "   ✅ 依赖更新完成"
}

# 运行迁移
run_migrations() {
    echo -e "${BLUE}🗄️ 运行数据库迁移...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 运行迁移
    python manage.py makemigrations
    python manage.py migrate
    
    # 收集静态文件
    python manage.py collectstatic --noinput
    
    echo -e "   ✅ 数据库迁移完成"
}

# 启动服务
start_services() {
    echo -e "${BLUE}🚀 启动服务...${NC}"
    
    # 重新加载systemd
    systemctl daemon-reload
    
    # 启动服务
    systemctl start qatoolbox
    systemctl start qatoolbox-celery
    systemctl start qatoolbox-celerybeat
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if systemctl is-active --quiet qatoolbox; then
        echo -e "   ✅ Django服务启动成功"
    else
        echo -e "   ❌ Django服务启动失败"
        return 1
    fi
    
    if systemctl is-active --quiet qatoolbox-celery; then
        echo -e "   ✅ Celery服务启动成功"
    else
        echo -e "   ❌ Celery服务启动失败"
        return 1
    fi
    
    echo -e "   ✅ 所有服务启动完成"
}

# 运行兼容性检查
run_compatibility_check() {
    echo -e "${BLUE}🔍 运行兼容性检查...${NC}"
    
    cd "$PROJECT_DIR"
    source "$VENV_NAME/bin/activate"
    
    # 运行Python 3.12兼容性检查
    if [ -f "check_python312_compatibility.py" ]; then
        python check_python312_compatibility.py
    fi
    
    # Django检查
    python manage.py check --deploy
    
    echo -e "   ✅ 兼容性检查完成"
}

# 清理备份
cleanup_backups() {
    echo -e "${BLUE}🧹 清理旧备份...${NC}"
    
    # 保留最近5个备份
    cd "$BACKUP_DIR"
    
    # 清理数据库备份（保留最近5个）
    ls -t db_backup_*.sqlite3 2>/dev/null | tail -n +6 | xargs -r rm -f
    
    # 清理环境配置备份（保留最近5个）
    ls -t env_backup_*.env 2>/dev/null | tail -n +6 | xargs -r rm -f
    
    # 清理媒体文件备份（保留最近3个）
    ls -t media_backup_*.tar.gz 2>/dev/null | tail -n +3 | xargs -r rm -f
    
    echo -e "   ✅ 旧备份清理完成"
}

# 显示更新信息
show_update_info() {
    echo -e "${GREEN}${BOLD}"
    cat << EOF
========================================
🎉 QAToolBox 快速更新完成！
========================================

📋 更新信息:
   • 项目目录: $PROJECT_DIR
   • 虚拟环境: $PROJECT_DIR/$VENV_NAME
   • 备份目录: $BACKUP_DIR

🌐 访问信息:
   • 网站: http://$(hostname -I | awk '{print $1}')
   • 管理后台: http://$(hostname -I | awk '{print $1}')/admin/

🔧 服务状态:
   • Django: systemctl status qatoolbox
   • Celery: systemctl status qatoolbox-celery
   • Nginx: systemctl status nginx

📝 日志文件:
   • Django: $PROJECT_DIR/logs/django.log
   • 更新: $LOG_FILE

💡 注意事项:
   • 所有数据已备份到: $BACKUP_DIR
   • 如果遇到问题，可以回滚到备份版本
   • 建议在更新后测试所有功能

========================================
EOF
    echo -e "${NC}"
}

# 主函数
main() {
    echo -e "${CYAN}🔄 开始快速更新 QAToolBox...${NC}"
    
    check_root
    check_project
    create_backup
    stop_services
    update_code
    update_dependencies
    run_migrations
    start_services
    run_compatibility_check
    cleanup_backups
    show_update_info
    
    echo -e "${GREEN}✅ 快速更新完成！详细日志请查看: $LOG_FILE${NC}"
}

# 运行主函数
main "$@"
