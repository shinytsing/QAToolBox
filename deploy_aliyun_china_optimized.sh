#!/bin/bash
# QAToolBox 阿里云服务器中国网络环境优化部署脚本
# 专为中国大陆网络环境优化，使用国内镜像源

set -e

# 配置变量
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
DB_PASSWORD="QAToolBox@2024"
LOG_FILE="/var/log/qatoolbox_deploy.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 检查root权限
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "需要root权限运行此脚本"
        exit 1
    fi
}

# 配置国内软件源
setup_china_mirrors() {
    log_step "配置国内软件源"
    
    # 备份原始源
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s) 2>/dev/null || true
    
    # 配置阿里云镜像源
    cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
EOF
    
    log_success "阿里云镜像源配置完成"
}

# 创建项目用户
create_user() {
    log_step "创建项目用户"
    
    if id "$PROJECT_USER" &>/dev/null; then
        log_info "用户 $PROJECT_USER 已存在"
    else
        useradd -m -s /bin/bash $PROJECT_USER
        usermod -aG sudo $PROJECT_USER
        log_success "用户 $PROJECT_USER 创建完成"
    fi
    
    # 确保用户目录权限正确
    chown -R "$PROJECT_USER:$PROJECT_USER" "/home/$PROJECT_USER"
    chmod 755 "/home/$PROJECT_USER"
}

# 克隆项目代码
clone_project() {
    log_step "获取项目代码"
    
    # 删除旧项目
    if [ -d "$PROJECT_DIR" ]; then
        rm -rf "$PROJECT_DIR"
    fi
    
    # 创建项目目录并设置权限
    mkdir -p "$PROJECT_DIR"
    chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    chmod 755 "$PROJECT_DIR"
    
    # 尝试多个源克隆
    CLONE_SUCCESS=false
    
    # 尝试从Gitee克隆
    log_info "尝试从 https://gitee.com/shinytsing/QAToolbox.git 克隆..."
    if sudo -u $PROJECT_USER git clone https://gitee.com/shinytsing/QAToolbox.git $PROJECT_DIR 2>/dev/null; then
        log_success "成功从Gitee克隆项目"
        CLONE_SUCCESS=true
    else
        log_warning "从Gitee克隆失败，尝试下一个..."
        sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
        mkdir -p $PROJECT_DIR
        chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
    fi
    
    # 尝试从GitHub镜像克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://github.com.cnpmjs.org/shinytsing/QAToolbox.git 克隆..."
        if sudo -u $PROJECT_USER git clone https://github.com.cnpmjs.org/shinytsing/QAToolbox.git $PROJECT_DIR 2>/dev/null; then
            log_success "成功从GitHub镜像克隆项目"
            CLONE_SUCCESS=true
        else
            log_warning "从GitHub镜像克隆失败，尝试下一个..."
            sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
            mkdir -p $PROJECT_DIR
            chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
        fi
    fi
    
    # 尝试从FastGit克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://hub.fastgit.xyz/shinytsing/QAToolbox.git 克隆..."
        if sudo -u $PROJECT_USER git clone https://hub.fastgit.xyz/shinytsing/QAToolbox.git $PROJECT_DIR 2>/dev/null; then
            log_success "成功从FastGit克隆项目"
            CLONE_SUCCESS=true
        else
            log_warning "从FastGit克隆失败，尝试下一个..."
            sudo -u $PROJECT_USER rm -rf $PROJECT_DIR 2>/dev/null || true
            mkdir -p $PROJECT_DIR
            chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR
        fi
    fi
    
    # 最后尝试从GitHub克隆
    if [ "$CLONE_SUCCESS" = false ]; then
        log_info "尝试从 https://github.com/shinytsing/QAToolbox.git 克隆..."
        if sudo -u $PROJECT_USER git clone https://github.com/shinytsing/QAToolbox.git $PROJECT_DIR 2>/dev/null; then
            log_success "成功从GitHub克隆项目"
            CLONE_SUCCESS=true
        else
            log_error "无法克隆项目，请检查网络连接"
            exit 1
        fi
    fi
    
    cd $PROJECT_DIR
    sudo -u $PROJECT_USER chmod +x *.sh *.py 2>/dev/null || true
    
    log_success "项目代码获取完成"
}

# 主函数
main() {
    echo "🚀 开始QAToolBox中国网络环境优化部署..."
    
    check_root
    setup_china_mirrors
    create_user
    clone_project
    
    echo "✅ 基础环境配置完成！"
    echo "📁 项目目录: $PROJECT_DIR"
    echo "👤 项目用户: $PROJECT_USER"
    echo ""
    echo "🔧 现在可以继续运行完整的部署脚本："
    echo "   sudo bash deploy_aliyun_ultimate.sh"
}

# 运行主函数
main "$@"
