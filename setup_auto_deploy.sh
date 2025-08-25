#!/bin/bash

# =============================================================================
# GitHub Actions 自动部署设置脚本
# 帮助设置SSH密钥和GitHub Secrets
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

show_welcome() {
    clear
    echo -e "${CYAN}"
    echo "========================================"
    echo "    🚀 GitHub Actions 自动部署设置"
    echo "========================================"
    echo "  功能: 设置SSH密钥和GitHub Secrets"
    echo "  目标: 实现一键自动部署"
    echo "========================================"
    echo -e "${NC}"
}

# 检查SSH密钥
check_ssh_keys() {
    log_step "检查SSH密钥"
    
    if [ -f ~/.ssh/id_rsa ]; then
        log_info "发现现有SSH私钥"
        read -p "是否使用现有密钥? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            USE_EXISTING=true
        else
            USE_EXISTING=false
        fi
    else
        USE_EXISTING=false
    fi
    
    if [ "$USE_EXISTING" = false ]; then
        log_info "生成新的SSH密钥对"
        read -p "请输入你的邮箱: " EMAIL
        ssh-keygen -t rsa -b 4096 -C "$EMAIL" -f ~/.ssh/id_rsa -N ""
        log_success "SSH密钥生成完成"
    fi
}

# 显示密钥信息
show_keys() {
    log_step "SSH密钥信息"
    
    echo
    echo -e "${YELLOW}=== 公钥 (需要添加到服务器) ===${NC}"
    echo -e "${GREEN}"
    cat ~/.ssh/id_rsa.pub
    echo -e "${NC}"
    
    echo
    echo -e "${YELLOW}=== 私钥 (需要添加到GitHub Secrets) ===${NC}"
    echo -e "${GREEN}"
    cat ~/.ssh/id_rsa
    echo -e "${NC}"
    echo
}

# 显示服务器配置指令
show_server_setup() {
    log_step "服务器配置指令"
    
    echo -e "${YELLOW}在你的阿里云服务器上执行以下命令:${NC}"
    echo
    echo -e "${CYAN}# 1. 创建.ssh目录${NC}"
    echo "mkdir -p ~/.ssh"
    echo "chmod 700 ~/.ssh"
    echo
    echo -e "${CYAN}# 2. 添加公钥到authorized_keys${NC}"
    echo "echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys"
    echo "chmod 600 ~/.ssh/authorized_keys"
    echo
    echo -e "${CYAN}# 3. 重启SSH服务${NC}"
    echo "sudo systemctl restart ssh"
    echo
}

# 显示GitHub设置指令
show_github_setup() {
    log_step "GitHub Secrets 设置"
    
    echo -e "${YELLOW}在GitHub仓库中设置以下Secrets:${NC}"
    echo
    echo -e "${CYAN}1. 访问: https://github.com/shinytsing/QAToolbox/settings/secrets/actions${NC}"
    echo
    echo -e "${CYAN}2. 点击 'New repository secret' 并添加:${NC}"
    echo
    echo -e "${GREEN}Secret 1:${NC}"
    echo "Name: SERVER_HOST"
    echo "Value: 47.103.143.152"
    echo
    echo -e "${GREEN}Secret 2:${NC}"
    echo "Name: SERVER_USER"
    echo "Value: root"
    echo
    echo -e "${GREEN}Secret 3:${NC}"
    echo "Name: SERVER_PORT"
    echo "Value: 22"
    echo
    echo -e "${GREEN}Secret 4:${NC}"
    echo "Name: SERVER_SSH_KEY"
    echo "Value: (复制下面的私钥内容)"
    echo -e "${BLUE}--- 私钥内容开始 ---${NC}"
    cat ~/.ssh/id_rsa
    echo -e "${BLUE}--- 私钥内容结束 ---${NC}"
    echo
}

# 测试连接
test_connection() {
    log_step "测试SSH连接"
    
    read -p "是否测试SSH连接? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "测试连接到服务器..."
        if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@47.103.143.152 'echo "SSH连接成功!"'; then
            log_success "SSH连接测试成功!"
        else
            log_error "SSH连接测试失败，请检查配置"
        fi
    fi
}

# 显示使用说明
show_usage() {
    log_step "自动部署使用说明"
    
    echo -e "${YELLOW}设置完成后，你可以:${NC}"
    echo
    echo -e "${GREEN}1. 手动触发部署:${NC}"
    echo "   - 访问: https://github.com/shinytsing/QAToolbox/actions"
    echo "   - 点击 'Auto Deploy to Aliyun Server'"
    echo "   - 点击 'Run workflow'"
    echo
    echo -e "${GREEN}2. 自动触发部署:${NC}"
    echo "   - 提交代码到main分支"
    echo "   - GitHub会自动部署到服务器"
    echo
    echo -e "${GREEN}3. 查看部署状态:${NC}"
    echo "   - 在Actions页面查看部署日志"
    echo "   - 部署成功后访问: https://shenyiqing.xin"
    echo
}

# 主函数
main() {
    show_welcome
    
    check_ssh_keys
    show_keys
    
    echo -e "${YELLOW}请按任意键继续...${NC}"
    read -n 1 -s
    
    show_server_setup
    
    echo -e "${YELLOW}请按任意键继续...${NC}"
    read -n 1 -s
    
    show_github_setup
    
    echo -e "${YELLOW}请按任意键继续...${NC}"
    read -n 1 -s
    
    test_connection
    show_usage
    
    echo
    echo -e "${GREEN}========================================"
    echo "        ✅ 设置指南完成！"
    echo "========================================"
    echo -e "${NC}"
    echo -e "${CYAN}按照上述步骤操作后，你就可以享受一键自动部署了！${NC}"
    echo
}

# 运行主函数
main "$@"
