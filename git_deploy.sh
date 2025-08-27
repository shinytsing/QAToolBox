#!/bin/bash
# =============================================================================
# QAToolBox Git提交和部署脚本
# =============================================================================
# 自动提交代码到Git仓库并在阿里云服务器上执行一键部署
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

# 默认配置
readonly DEFAULT_BRANCH="main"
readonly DEFAULT_COMMIT_MSG="更新部署配置和一键部署脚本"

# 显示帮助信息
show_help() {
    cat << EOF
${CYAN}${BOLD}QAToolBox Git部署脚本${NC}

${YELLOW}用法:${NC}
  $0 [选项]

${YELLOW}选项:${NC}
  -m, --message MSG     提交信息 (默认: "$DEFAULT_COMMIT_MSG")
  -b, --branch BRANCH   目标分支 (默认: "$DEFAULT_BRANCH")
  -s, --server IP       服务器IP地址 (用于自动部署)
  -u, --user USER       服务器用户名 (默认: root)
  -k, --key PATH        SSH私钥路径
  --commit-only         仅提交代码，不执行部署
  --deploy-only         仅执行部署，不提交代码
  -h, --help            显示此帮助信息

${YELLOW}示例:${NC}
  # 提交代码并自动部署到服务器
  $0 -m "添加新功能" -s 47.103.143.152

  # 仅提交代码到Git
  $0 --commit-only -m "修复bug"

  # 仅在服务器上部署
  $0 --deploy-only -s 47.103.143.152

  # 使用SSH密钥连接服务器
  $0 -s 47.103.143.152 -k ~/.ssh/id_rsa
EOF
}

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查Git仓库状态
check_git_status() {
    log_info "检查Git仓库状态..."
    
    # 检查是否在Git仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "当前目录不是Git仓库"
        exit 1
    fi
    
    # 检查是否有未提交的更改
    if ! git diff-index --quiet HEAD --; then
        log_info "发现未提交的更改"
        git status --short
        return 0
    fi
    
    # 检查是否有未跟踪的文件
    if [ -n "$(git ls-files --others --exclude-standard)" ]; then
        log_info "发现未跟踪的文件"
        git ls-files --others --exclude-standard
        return 0
    fi
    
    log_warning "没有发现需要提交的更改"
    return 1
}

# 提交代码到Git
commit_to_git() {
    local commit_message="$1"
    local branch="$2"
    
    log_info "开始提交代码到Git仓库..."
    
    # 检查当前分支
    local current_branch=$(git branch --show-current)
    log_info "当前分支: $current_branch"
    
    # 如果指定了不同的分支，则切换
    if [ "$branch" != "$current_branch" ]; then
        log_info "切换到分支: $branch"
        git checkout -b "$branch" 2>/dev/null || git checkout "$branch"
    fi
    
    # 添加所有更改
    log_info "添加所有更改到暂存区..."
    git add .
    
    # 显示即将提交的更改
    echo -e "${CYAN}即将提交的更改:${NC}"
    git status --short
    
    # 确认提交
    echo -e "${YELLOW}提交信息: $commit_message${NC}"
    read -p "确认提交? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "用户取消提交"
        return 1
    fi
    
    # 执行提交
    git commit -m "$commit_message"
    log_success "代码提交成功"
    
    # 推送到远程仓库
    log_info "推送到远程仓库..."
    if git push origin "$branch"; then
        log_success "推送成功"
    else
        log_warning "推送失败，可能需要先pull最新代码"
        read -p "是否执行 git pull --rebase? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git pull --rebase origin "$branch"
            git push origin "$branch"
            log_success "推送成功"
        else
            log_error "推送失败"
            return 1
        fi
    fi
    
    # 显示提交信息
    echo -e "${CYAN}最新提交:${NC}"
    git log --oneline -1
}

# 检查服务器连接
check_server_connection() {
    local server="$1"
    local user="$2"
    local key_path="$3"
    
    log_info "检查服务器连接: $user@$server"
    
    local ssh_cmd="ssh"
    if [ -n "$key_path" ]; then
        ssh_cmd="ssh -i $key_path"
    fi
    
    # 设置SSH选项
    ssh_cmd="$ssh_cmd -o ConnectTimeout=10 -o StrictHostKeyChecking=no"
    
    if $ssh_cmd "$user@$server" "echo 'SSH连接成功'" >/dev/null 2>&1; then
        log_success "服务器连接正常"
        return 0
    else
        log_error "无法连接到服务器 $user@$server"
        return 1
    fi
}

# 在服务器上执行部署
deploy_to_server() {
    local server="$1"
    local user="$2"
    local key_path="$3"
    
    log_info "开始在服务器上执行部署..."
    
    local ssh_cmd="ssh"
    if [ -n "$key_path" ]; then
        ssh_cmd="ssh -i $key_path"
    fi
    
    # 设置SSH选项
    ssh_cmd="$ssh_cmd -o StrictHostKeyChecking=no"
    
    # 创建部署脚本
    local deploy_script=$(cat << 'DEPLOY_SCRIPT'
#!/bin/bash
set -e

echo "=== 开始QAToolBox阿里云部署 ==="
echo "时间: $(date)"
echo "用户: $(whoami)"
echo "系统: $(uname -a)"
echo ""

# 下载最新的部署脚本
SCRIPT_URL="https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun.sh"
SCRIPT_PATH="/tmp/deploy_aliyun.sh"

echo "📥 下载最新部署脚本..."
if curl -fsSL "$SCRIPT_URL" -o "$SCRIPT_PATH"; then
    echo "✅ 部署脚本下载成功"
else
    echo "❌ 部署脚本下载失败，请检查网络连接"
    exit 1
fi

# 设置执行权限
chmod +x "$SCRIPT_PATH"

# 执行部署脚本
echo "🚀 执行部署脚本..."
"$SCRIPT_PATH"

echo ""
echo "=== QAToolBox部署完成 ==="
echo "时间: $(date)"
DEPLOY_SCRIPT
)
    
    # 在服务器上执行部署
    echo "$deploy_script" | $ssh_cmd "$user@$server" 'bash -s'
    
    if [ $? -eq 0 ]; then
        log_success "服务器部署完成"
        
        # 显示访问信息
        echo -e "${CYAN}${BOLD}"
        cat << EOF

========================================
🎉 部署成功完成！
========================================

🌐 访问地址:
  http://$server/
  http://$server/admin/

👑 管理员账户:
  用户名: admin
  密码: admin123456

🔧 远程管理:
  SSH连接: $ssh_cmd $user@$server
  查看日志: sudo tail -f /var/log/qatoolbox/gunicorn.log
  重启应用: sudo supervisorctl restart qatoolbox

========================================
EOF
        echo -e "${NC}"
    else
        log_error "服务器部署失败"
        return 1
    fi
}

# 主函数
main() {
    local commit_message="$DEFAULT_COMMIT_MSG"
    local branch="$DEFAULT_BRANCH"
    local server=""
    local user="root"
    local key_path=""
    local commit_only=false
    local deploy_only=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--message)
                commit_message="$2"
                shift 2
                ;;
            -b|--branch)
                branch="$2"
                shift 2
                ;;
            -s|--server)
                server="$2"
                shift 2
                ;;
            -u|--user)
                user="$2"
                shift 2
                ;;
            -k|--key)
                key_path="$2"
                shift 2
                ;;
            --commit-only)
                commit_only=true
                shift
                ;;
            --deploy-only)
                deploy_only=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 显示配置信息
    echo -e "${CYAN}${BOLD}QAToolBox Git部署脚本${NC}"
    echo -e "${BLUE}配置信息:${NC}"
    echo -e "  提交信息: $commit_message"
    echo -e "  目标分支: $branch"
    [ -n "$server" ] && echo -e "  目标服务器: $user@$server"
    [ -n "$key_path" ] && echo -e "  SSH密钥: $key_path"
    echo ""
    
    # 执行相应操作
    if [ "$deploy_only" = true ]; then
        # 仅部署
        if [ -z "$server" ]; then
            log_error "部署模式需要指定服务器地址 (-s)"
            exit 1
        fi
        
        check_server_connection "$server" "$user" "$key_path"
        deploy_to_server "$server" "$user" "$key_path"
        
    elif [ "$commit_only" = true ]; then
        # 仅提交
        if check_git_status; then
            commit_to_git "$commit_message" "$branch"
        fi
        
    else
        # 提交并部署
        local committed=false
        
        # 提交代码
        if check_git_status; then
            commit_to_git "$commit_message" "$branch"
            committed=true
        fi
        
        # 执行部署
        if [ -n "$server" ]; then
            if [ "$committed" = true ]; then
                log_info "等待Git同步..."
                sleep 5
            fi
            
            check_server_connection "$server" "$user" "$key_path"
            deploy_to_server "$server" "$user" "$key_path"
        else
            log_warning "未指定服务器地址，跳过自动部署"
            echo -e "${YELLOW}手动部署命令:${NC}"
            echo -e "  wget -O deploy.sh https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun.sh"
            echo -e "  chmod +x deploy.sh"
            echo -e "  sudo ./deploy.sh"
        fi
    fi
    
    log_success "操作完成"
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    # 检查必需的命令
    local required_commands=("git" "curl")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少必需的依赖: ${missing_deps[*]}"
        echo -e "${YELLOW}请安装缺少的依赖后重试${NC}"
        exit 1
    fi
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_dependencies
    main "$@"
fi
