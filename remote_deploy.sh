#!/bin/bash
# =============================================================================
# QAToolBox 远程部署脚本
# =============================================================================
# 从本地一键部署到远程服务器
# 支持 SSH 密钥认证和密码认证
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
SERVER_IP=""
SERVER_USER="root"
PROJECT_USER="qatoolbox"
SSH_KEY=""
USE_PASSWORD=false
DEPLOY_TYPE="full"  # full, update, docker

# 显示帮助信息
show_help() {
    cat << EOF
使用方法: $0 [选项]

选项:
    -h, --help              显示此帮助信息
    -s, --server SERVER_IP  服务器IP地址 (必需)
    -u, --user USER         服务器用户名 (默认: root)
    -p, --project-user USER 项目用户名 (默认: qatoolbox)
    -k, --key SSH_KEY_PATH  SSH私钥路径
    -w, --password          使用密码认证
    -t, --type TYPE         部署类型: full|update|docker (默认: full)

示例:
    # 完整部署到服务器
    $0 -s 192.168.1.100 -k ~/.ssh/id_rsa

    # 快速更新到服务器
    $0 -s 192.168.1.100 -t update -k ~/.ssh/id_rsa

    # Docker部署到服务器
    $0 -s 192.168.1.100 -t docker -k ~/.ssh/id_rsa

    # 使用密码认证
    $0 -s 192.168.1.100 -w
EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--server)
                SERVER_IP="$2"
                shift 2
                ;;
            -u|--user)
                SERVER_USER="$2"
                shift 2
                ;;
            -p|--project-user)
                PROJECT_USER="$2"
                shift 2
                ;;
            -k|--key)
                SSH_KEY="$2"
                shift 2
                ;;
            -w|--password)
                USE_PASSWORD=true
                shift
                ;;
            -t|--type)
                DEPLOY_TYPE="$2"
                shift 2
                ;;
            *)
                echo -e "${RED}❌ 未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查必需参数
    if [ -z "$SERVER_IP" ]; then
        echo -e "${RED}❌ 必须指定服务器IP地址${NC}"
        show_help
        exit 1
    fi
    
    # 检查部署类型
    if [[ ! "$DEPLOY_TYPE" =~ ^(full|update|docker)$ ]]; then
        echo -e "${RED}❌ 无效的部署类型: $DEPLOY_TYPE${NC}"
        echo -e "   有效类型: full, update, docker"
        exit 1
    fi
}

# 测试SSH连接
test_ssh_connection() {
    echo -e "${BLUE}🔍 测试SSH连接...${NC}"
    
    local ssh_cmd=""
    
    if [ -n "$SSH_KEY" ]; then
        if [ ! -f "$SSH_KEY" ]; then
            echo -e "${RED}❌ SSH私钥文件不存在: $SSH_KEY${NC}"
            exit 1
        fi
        ssh_cmd="ssh -i $SSH_KEY -o ConnectTimeout=10 -o BatchMode=yes $SERVER_USER@$SERVER_IP"
    else
        ssh_cmd="ssh -o ConnectTimeout=10 $SERVER_USER@$SERVER_IP"
    fi
    
    if $ssh_cmd "echo 'SSH连接测试成功'" 2>/dev/null; then
        echo -e "   ✅ SSH连接成功"
    else
        echo -e "${RED}❌ SSH连接失败${NC}"
        if [ "$USE_PASSWORD" = false ]; then
            echo -e "${YELLOW}💡 请检查SSH密钥或使用 -w 选项启用密码认证${NC}"
        fi
        exit 1
    fi
}

# 上传部署脚本
upload_deploy_scripts() {
    echo -e "${BLUE}📤 上传部署脚本...${NC}"
    
    local temp_dir="/tmp/qatoolbox_deploy_$(date +%s)"
    
    # 在服务器上创建临时目录
    ssh_cmd "mkdir -p $temp_dir"
    
    # 上传脚本文件
    if [ "$DEPLOY_TYPE" = "full" ]; then
        scp_cmd "one_click_deploy.sh" "$temp_dir/"
        echo -e "   ✅ 一键部署脚本已上传"
    elif [ "$DEPLOY_TYPE" = "update" ]; then
        scp_cmd "quick_update.sh" "$temp_dir/"
        echo -e "   ✅ 快速更新脚本已上传"
    elif [ "$DEPLOY_TYPE" = "docker" ]; then
        scp_cmd "deploy_ubuntu24_docker.sh" "$temp_dir/"
        echo -e "   ✅ Docker部署脚本已上传"
    fi
    
    # 上传兼容性检查脚本
    scp_cmd "check_python312_compatibility.py" "$temp_dir/"
    echo -e "   ✅ 兼容性检查脚本已上传"
    
    # 上传requirements文件
    if [ -d "requirements" ]; then
        scp_cmd "requirements/" "$temp_dir/"
        echo -e "   ✅ 依赖文件已上传"
    fi
    
    echo -e "   ✅ 所有文件上传完成"
}

# 执行远程部署
execute_remote_deploy() {
    echo -e "${BLUE}🚀 执行远程部署...${NC}"
    
    local temp_dir="/tmp/qatoolbox_deploy_$(date +%s)"
    local script_name=""
    
    case "$DEPLOY_TYPE" in
        "full")
            script_name="one_click_deploy.sh"
            ;;
        "update")
            script_name="quick_update.sh"
            ;;
        "docker")
            script_name="deploy_ubuntu24_docker.sh"
            ;;
    esac
    
    # 设置脚本权限
    ssh_cmd "chmod +x $temp_dir/$script_name"
    ssh_cmd "chmod +x $temp_dir/check_python312_compatibility.py"
    
    # 执行部署脚本
    echo -e "   🚀 开始执行 $script_name..."
    
    if [ "$DEPLOY_TYPE" = "full" ]; then
        # 完整部署需要root权限
        ssh_cmd "cd $temp_dir && sudo ./$script_name"
    else
        # 更新和Docker部署也需要root权限
        ssh_cmd "cd $temp_dir && sudo ./$script_name"
    fi
    
    echo -e "   ✅ 远程部署执行完成"
}

# 清理临时文件
cleanup_temp_files() {
    echo -e "${BLUE}🧹 清理临时文件...${NC}"
    
    local temp_dir="/tmp/qatoolbox_deploy_$(date +%s)"
    
    # 删除临时目录
    ssh_cmd "rm -rf $temp_dir"
    
    echo -e "   ✅ 临时文件清理完成"
}

# 验证部署结果
verify_deployment() {
    echo -e "${BLUE}🔍 验证部署结果...${NC}"
    
    # 检查服务状态
    if ssh_cmd "systemctl is-active --quiet qatoolbox" 2>/dev/null; then
        echo -e "   ✅ Django服务运行正常"
    else
        echo -e "   ❌ Django服务未运行"
        return 1
    fi
    
    # 检查网站是否可访问
    if ssh_cmd "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000" | grep -q "200"; then
        echo -e "   ✅ 网站可正常访问"
    else
        echo -e "   ⚠️ 网站访问测试失败，可能需要等待服务完全启动"
    fi
    
    # 检查端口监听
    if ssh_cmd "netstat -tlnp | grep :8000" 2>/dev/null; then
        echo -e "   ✅ 端口8000监听正常"
    else
        echo -e "   ❌ 端口8000未监听"
        return 1
    fi
    
    echo -e "   ✅ 部署验证完成"
}

# 显示部署信息
show_deployment_info() {
    echo -e "${GREEN}${BOLD}"
    cat << EOF
========================================
🎉 QAToolBox 远程部署完成！
========================================

📋 部署信息:
   • 服务器: $SERVER_IP
   • 部署类型: $DEPLOY_TYPE
   • 项目用户: $PROJECT_USER
   • 部署时间: $(date '+%Y-%m-%d %H:%M:%S')

🌐 访问信息:
   • 网站: http://$SERVER_IP:8000
   • 管理后台: http://$SERVER_IP:8000/admin/

🔧 服务器管理:
   • SSH连接: ssh $SERVER_USER@$SERVER_IP
   • 查看服务状态: systemctl status qatoolbox
   • 查看日志: journalctl -u qatoolbox -f

💡 下一步:
   • 配置域名和SSL证书
   • 设置防火墙规则
   • 配置监控和备份
   • 创建超级用户

========================================
EOF
    echo -e "${NC}"
}

# SSH命令执行函数
ssh_cmd() {
    local cmd="$1"
    local ssh_options=""
    
    if [ -n "$SSH_KEY" ]; then
        ssh_options="-i $SSH_KEY"
    fi
    
    ssh $ssh_options -o ConnectTimeout=30 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" "$cmd"
}

# SCP文件传输函数
scp_cmd() {
    local local_path="$1"
    local remote_path="$2"
    local scp_options=""
    
    if [ -n "$SSH_KEY" ]; then
        scp_options="-i $SSH_KEY"
    fi
    
    scp $scp_options -o ConnectTimeout=30 "$local_path" "$SERVER_USER@$SERVER_IP:$remote_path"
}

# 主函数
main() {
    echo -e "${CYAN}${BOLD}"
    cat << 'EOF'
========================================
🚀 QAToolBox 远程部署脚本
========================================
✨ 特性:
  • 一键远程部署
  • 支持多种部署类型
  • SSH密钥和密码认证
  • 自动验证部署结果
  • 完整的部署日志
========================================
EOF
    echo -e "${NC}"
    
    # 解析命令行参数
    parse_args "$@"
    
    echo -e "${BLUE}📋 部署配置:${NC}"
    echo -e "   服务器: $SERVER_IP"
    echo -e "   用户: $SERVER_USER"
    echo -e "   项目用户: $PROJECT_USER"
    echo -e "   部署类型: $DEPLOY_TYPE"
    echo -e "   认证方式: $([ "$USE_PASSWORD" = true ] && echo "密码" || echo "SSH密钥")"
    echo ""
    
    # 执行部署流程
    test_ssh_connection
    upload_deploy_scripts
    execute_remote_deploy
    cleanup_temp_files
    verify_deployment
    show_deployment_info
    
    echo -e "${GREEN}✅ 远程部署完成！${NC}"
}

# 运行主函数
main "$@"
