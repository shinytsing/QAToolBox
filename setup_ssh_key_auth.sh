#!/bin/bash

# =============================================================================
# SSH密钥认证配置脚本
# 将SSH登录方式从密码改为密钥认证，提高安全性
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限运行"
        log_info "请使用: sudo bash $0"
        exit 1
    fi
}

# 1. 为qatoolbox用户生成SSH密钥对
generate_ssh_keys() {
    log_step "🔑 为qatoolbox用户生成SSH密钥对"
    
    # 确保qatoolbox用户存在
    if ! id "qatoolbox" &>/dev/null; then
        log_error "qatoolbox用户不存在，请先创建用户"
        exit 1
    fi
    
    # 切换到qatoolbox用户的home目录
    USER_HOME="/home/qatoolbox"
    SSH_DIR="$USER_HOME/.ssh"
    
    # 创建.ssh目录
    sudo -u qatoolbox mkdir -p "$SSH_DIR"
    sudo -u qatoolbox chmod 700 "$SSH_DIR"
    
    # 生成SSH密钥对
    if [ ! -f "$SSH_DIR/id_rsa" ]; then
        log_info "生成新的SSH密钥对..."
        sudo -u qatoolbox ssh-keygen -t rsa -b 4096 -f "$SSH_DIR/id_rsa" -N "" -C "qatoolbox@$(hostname)"
        log_success "SSH密钥对生成完成"
    else
        log_info "SSH密钥对已存在"
    fi
    
    # 设置正确的权限
    sudo -u qatoolbox chmod 600 "$SSH_DIR/id_rsa"
    sudo -u qatoolbox chmod 644 "$SSH_DIR/id_rsa.pub"
    
    # 将公钥添加到authorized_keys
    sudo -u qatoolbox cp "$SSH_DIR/id_rsa.pub" "$SSH_DIR/authorized_keys"
    sudo -u qatoolbox chmod 600 "$SSH_DIR/authorized_keys"
    
    log_success "SSH密钥配置完成"
}

# 2. 配置SSH服务器
configure_ssh_server() {
    log_step "🔧 配置SSH服务器"
    
    # 备份原配置
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)
    
    # 创建新的SSH配置
    cat > /etc/ssh/sshd_config << 'EOF'
# SSH服务器安全配置
Port 22
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key

# 认证配置
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# 用户访问控制
PermitRootLogin no
AllowUsers qatoolbox
DenyUsers root

# 连接限制
MaxAuthTries 3
MaxSessions 3
MaxStartups 3:50:10
LoginGraceTime 30

# 会话配置
ClientAliveInterval 300
ClientAliveCountMax 2
TCPKeepAlive yes

# 安全配置
X11Forwarding no
AllowTcpForwarding no
GatewayPorts no
PermitTunnel no
Compression no
UseDNS no

# 日志配置
SyslogFacility AUTH
LogLevel VERBOSE

# 其他安全设置
StrictModes yes
IgnoreRhosts yes
HostbasedAuthentication no
PermitUserEnvironment no
AcceptEnv LANG LC_*
PrintMotd no
PrintLastLog yes
EOF
    
    # 测试SSH配置
    if sshd -t; then
        log_success "SSH配置语法正确"
    else
        log_error "SSH配置有误，恢复备份"
        cp /etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S) /etc/ssh/sshd_config
        exit 1
    fi
    
    log_success "SSH服务器配置完成"
}

# 3. 重启SSH服务
restart_ssh_service() {
    log_step "🔄 重启SSH服务"
    
    # 重启SSH服务
    systemctl restart sshd
    
    # 检查服务状态
    if systemctl is-active --quiet sshd; then
        log_success "SSH服务重启成功"
    else
        log_error "SSH服务重启失败"
        exit 1
    fi
}

# 4. 配置防火墙（如果需要）
configure_firewall() {
    log_step "🛡️ 配置防火墙"
    
    if systemctl is-active --quiet firewalld; then
        # 确保SSH端口开放
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
        log_success "防火墙配置完成"
    else
        log_info "防火墙未启用，跳过配置"
    fi
}

# 5. 安装fail2ban保护SSH
install_fail2ban() {
    log_step "🚫 安装Fail2ban保护SSH"
    
    # 安装fail2ban
    if ! command -v fail2ban-server &> /dev/null; then
        yum install -y epel-release
        yum install -y fail2ban
    fi
    
    # 配置fail2ban
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = ssh
logpath = /var/log/secure
maxretry = 3
bantime = 86400
EOF
    
    # 启动fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    
    log_success "Fail2ban安装配置完成"
}

# 6. 创建密钥下载包
create_key_package() {
    log_step "📦 创建密钥下载包"
    
    USER_HOME="/home/qatoolbox"
    SSH_DIR="$USER_HOME/.ssh"
    PACKAGE_DIR="/tmp/ssh_keys_$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$PACKAGE_DIR"
    
    # 复制私钥
    cp "$SSH_DIR/id_rsa" "$PACKAGE_DIR/qatoolbox_private_key"
    cp "$SSH_DIR/id_rsa.pub" "$PACKAGE_DIR/qatoolbox_public_key.pub"
    
    # 创建使用说明
    cat > "$PACKAGE_DIR/README.txt" << EOF
=== SSH密钥使用说明 ===

1. 下载这些文件到您的本地计算机
2. 将私钥文件保存到安全位置（如 ~/.ssh/qatoolbox_key）
3. 设置正确的权限：chmod 600 ~/.ssh/qatoolbox_key
4. 使用以下命令连接服务器：
   ssh -i ~/.ssh/qatoolbox_key qatoolbox@YOUR_SERVER_IP

安全提醒：
- 私钥文件务必妥善保管，不要泄露
- 建议为私钥设置密码保护
- 定期更换密钥对
- 不要在不安全的网络中传输私钥

连接示例：
ssh -i ~/.ssh/qatoolbox_key qatoolbox@$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")

Windows用户可以使用PuTTY或WSL来连接
MacOS/Linux用户直接使用上述命令

生成时间：$(date)
EOF
    
    # 设置权限
    chmod 600 "$PACKAGE_DIR/qatoolbox_private_key"
    chmod 644 "$PACKAGE_DIR/qatoolbox_public_key.pub"
    chmod 644 "$PACKAGE_DIR/README.txt"
    
    # 创建压缩包
    cd /tmp
    tar -czf "ssh_keys_$(date +%Y%m%d_%H%M%S).tar.gz" "$(basename $PACKAGE_DIR)"
    
    log_success "密钥包已创建：/tmp/ssh_keys_$(date +%Y%m%d_%H%M%S).tar.gz"
    log_critical "请立即下载密钥文件并妥善保管！"
}

# 7. 测试连接
test_connection() {
    log_step "🧪 测试SSH连接"
    
    USER_HOME="/home/qatoolbox"
    SSH_DIR="$USER_HOME/.ssh"
    
    # 测试本地连接
    if sudo -u qatoolbox ssh -i "$SSH_DIR/id_rsa" -o StrictHostKeyChecking=no qatoolbox@localhost "echo 'SSH密钥认证测试成功'" 2>/dev/null; then
        log_success "SSH密钥认证测试成功"
    else
        log_warning "SSH密钥认证测试失败，请检查配置"
    fi
}

# 8. 生成配置报告
generate_report() {
    log_step "📝 生成配置报告"
    
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "未知")
    REPORT_FILE="/root/ssh_key_setup_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $REPORT_FILE << EOF
=== SSH密钥认证配置报告 ===
时间: $(date)
服务器IP: $SERVER_IP

配置内容:
✅ 为qatoolbox用户生成SSH密钥对
✅ 配置SSH服务器禁用密码认证
✅ 启用公钥认证
✅ 禁用root登录
✅ 配置连接限制和安全选项
✅ 安装fail2ban防护
✅ 创建密钥下载包

SSH连接命令:
ssh -i ~/.ssh/qatoolbox_key qatoolbox@$SERVER_IP

重要提醒:
1. 密码登录已完全禁用
2. 只能通过SSH密钥连接
3. 私钥文件务必妥善保管
4. 建议定期更换密钥对

密钥文件位置:
- 服务器端：/home/qatoolbox/.ssh/
- 下载包：/tmp/ssh_keys_*.tar.gz

安全建议:
1. 立即下载私钥文件
2. 在本地设置正确的文件权限
3. 考虑为私钥设置密码
4. 定期检查authorized_keys文件
5. 监控SSH登录日志

EOF
    
    log_success "配置报告已生成: $REPORT_FILE"
}

# 主函数
main() {
    echo -e "${CYAN}"
    echo "========================================"
    echo "     🔐 SSH密钥认证配置"
    echo "========================================"
    echo -e "${NC}"
    
    check_root
    
    log_info "开始配置SSH密钥认证..."
    
    generate_ssh_keys
    configure_ssh_server
    restart_ssh_service
    configure_firewall
    install_fail2ban
    create_key_package
    test_connection
    generate_report
    
    echo -e "${GREEN}"
    echo "========================================"
    echo "    ✅ SSH密钥认证配置完成"
    echo "========================================"
    echo -e "${NC}"
    
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR_SERVER_IP")
    
    log_critical "重要提醒："
    log_critical "1. 密码登录已完全禁用"
    log_critical "2. 请立即下载 /tmp/ssh_keys_*.tar.gz 文件"
    log_critical "3. 使用私钥连接：ssh -i ~/.ssh/qatoolbox_key qatoolbox@$SERVER_IP"
    log_critical "4. 私钥文件务必妥善保管"
    
    echo -e "${YELLOW}"
    echo "下载密钥文件后的操作步骤："
    echo "1. 解压下载的文件"
    echo "2. 将私钥保存到 ~/.ssh/qatoolbox_key"
    echo "3. 设置权限：chmod 600 ~/.ssh/qatoolbox_key"
    echo "4. 测试连接：ssh -i ~/.ssh/qatoolbox_key qatoolbox@$SERVER_IP"
    echo -e "${NC}"
}

# 错误处理
trap 'log_error "配置过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
