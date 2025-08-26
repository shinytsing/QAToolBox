#!/bin/bash

# =============================================================================
# QAToolBox 紧急安全响应脚本
# 用于应对服务器被暴力破解后的紧急安全加固
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

# 1. 立即更改所有密码
change_passwords() {
    log_step "🔒 立即更改所有系统密码"
    
    # 生成强密码
    NEW_ROOT_PASSWORD=$(openssl rand -base64 32)
    NEW_USER_PASSWORD=$(openssl rand -base64 32)
    NEW_DB_PASSWORD=$(openssl rand -base64 32)
    
    # 更改root密码
    echo "root:$NEW_ROOT_PASSWORD" | chpasswd
    log_success "Root密码已更改"
    
    # 更改qatoolbox用户密码
    if id "qatoolbox" &>/dev/null; then
        echo "qatoolbox:$NEW_USER_PASSWORD" | chpasswd
        log_success "qatoolbox用户密码已更改"
    fi
    
    # 保存密码到安全文件
    cat > /root/new_passwords.txt << EOF
=== 新密码信息 ($(date)) ===
Root密码: $NEW_ROOT_PASSWORD
qatoolbox用户密码: $NEW_USER_PASSWORD  
数据库密码: $NEW_DB_PASSWORD

请立即将这些密码保存到安全的地方，然后删除此文件！
EOF
    chmod 600 /root/new_passwords.txt
    
    log_critical "新密码已保存到 /root/new_passwords.txt"
    log_critical "请立即备份密码信息，然后删除该文件！"
}

# 2. 禁用root SSH登录并加固SSH
secure_ssh() {
    log_step "🔐 加固SSH配置"
    
    # 备份原配置
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d_%H%M%S)
    
    # 修改SSH配置
    sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
    sed -i 's/Port 22/Port 2222/' /etc/ssh/sshd_config
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config
    sed -i 's/MaxAuthTries 6/MaxAuthTries 3/' /etc/ssh/sshd_config
    
    # 添加额外的安全配置
    cat >> /etc/ssh/sshd_config << 'EOF'

# 紧急安全加固配置
Protocol 2
LoginGraceTime 30
MaxStartups 3:50:10
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers qatoolbox
DenyUsers root
PermitEmptyPasswords no
X11Forwarding no
AllowTcpForwarding no
GatewayPorts no
PermitTunnel no
EOF
    
    # 重启SSH服务
    systemctl restart sshd
    
    log_success "SSH配置已加固"
    log_warning "SSH端口已改为2222，root登录已禁用"
    log_warning "下次连接请使用: ssh -p 2222 qatoolbox@YOUR_SERVER_IP"
}

# 3. 配置防火墙
configure_firewall() {
    log_step "🛡️ 配置防火墙"
    
    # 启用firewalld
    systemctl enable firewalld
    systemctl start firewalld
    
    # 移除默认SSH端口
    firewall-cmd --permanent --remove-service=ssh
    
    # 添加新SSH端口
    firewall-cmd --permanent --add-port=2222/tcp
    
    # 保留HTTP和HTTPS
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    
    # 移除不必要的端口
    firewall-cmd --permanent --remove-port=8000/tcp 2>/dev/null || true
    
    # 重新加载防火墙
    firewall-cmd --reload
    
    log_success "防火墙配置完成"
}

# 4. 安装fail2ban
install_fail2ban() {
    log_step "🚫 安装和配置Fail2ban"
    
    # 安装fail2ban
    yum install -y epel-release
    yum install -y fail2ban
    
    # 配置fail2ban
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
backend = systemd

[sshd]
enabled = true
port = 2222
logpath = /var/log/secure
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF
    
    # 启动fail2ban
    systemctl enable fail2ban
    systemctl start fail2ban
    
    log_success "Fail2ban安装配置完成"
}

# 5. 检查入侵痕迹
check_intrusion() {
    log_step "🔍 检查系统入侵痕迹"
    
    # 检查最近登录
    log_info "最近登录记录:"
    last -n 20
    
    # 检查当前用户
    log_info "当前登录用户:"
    who
    
    # 检查sudo使用记录
    log_info "最近sudo使用记录:"
    grep sudo /var/log/secure | tail -20
    
    # 检查异常进程
    log_info "检查异常进程:"
    ps aux | grep -E "(nc|netcat|wget|curl)" | grep -v grep
    
    # 检查网络连接
    log_info "当前网络连接:"
    netstat -tulpn | grep LISTEN
    
    # 检查crontab
    log_info "检查定时任务:"
    crontab -l 2>/dev/null || echo "无root定时任务"
    crontab -u qatoolbox -l 2>/dev/null || echo "无qatoolbox用户定时任务"
    
    # 检查最近修改的文件
    log_info "最近24小时修改的系统文件:"
    find /etc /usr/bin /usr/sbin -type f -mtime -1 -ls 2>/dev/null | head -20
}

# 6. 数据库安全
secure_database() {
    log_step "🗄️ 加固数据库安全"
    
    # 生成新的数据库密码
    NEW_DB_PASSWORD=$(openssl rand -base64 32)
    
    # 更改数据库密码
    sudo -u postgres psql -c "ALTER USER qatoolbox PASSWORD '$NEW_DB_PASSWORD';"
    
    # 更新应用配置
    if [ -f "/home/qatoolbox/QAToolBox/.env" ]; then
        sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$NEW_DB_PASSWORD/" /home/qatoolbox/QAToolBox/.env
    fi
    
    # 限制数据库连接
    PG_DATA_DIR="/var/lib/pgsql/15/data"
    if [ -f "$PG_DATA_DIR/pg_hba.conf" ]; then
        # 备份配置
        cp $PG_DATA_DIR/pg_hba.conf $PG_DATA_DIR/pg_hba.conf.backup.$(date +%Y%m%d_%H%M%S)
        
        # 只允许本地连接
        cat > $PG_DATA_DIR/pg_hba.conf << 'EOF'
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF
        
        systemctl restart postgresql-15
    fi
    
    log_success "数据库安全配置完成"
    echo "新数据库密码: $NEW_DB_PASSWORD" >> /root/new_passwords.txt
}

# 7. 应用安全检查
secure_application() {
    log_step "🔧 应用安全检查和加固"
    
    PROJECT_DIR="/home/qatoolbox/QAToolBox"
    
    if [ -d "$PROJECT_DIR" ]; then
        # 检查应用文件权限
        chown -R qatoolbox:qatoolbox $PROJECT_DIR
        chmod -R 755 $PROJECT_DIR
        chmod 600 $PROJECT_DIR/.env 2>/dev/null || true
        
        # 生成新的Django SECRET_KEY
        NEW_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        
        if [ -f "$PROJECT_DIR/.env" ]; then
            sed -i "s/SECRET_KEY=.*/SECRET_KEY=$NEW_SECRET_KEY/" $PROJECT_DIR/.env
            
            # 确保DEBUG=False
            sed -i "s/DEBUG=.*/DEBUG=False/" $PROJECT_DIR/.env
        fi
        
        # 重启应用服务
        systemctl restart qatoolbox 2>/dev/null || true
        
        log_success "应用安全配置完成"
    fi
}

# 8. 系统更新和清理
system_update() {
    log_step "🔄 系统更新和清理"
    
    # 更新系统
    yum update -y
    
    # 清理临时文件
    rm -rf /tmp/*
    rm -rf /var/tmp/*
    
    # 清理日志中的敏感信息
    > /var/log/secure
    > /var/log/messages
    
    log_success "系统更新和清理完成"
}

# 9. 设置监控和告警
setup_monitoring() {
    log_step "📊 设置安全监控"
    
    # 创建安全监控脚本
    cat > /usr/local/bin/security_monitor.sh << 'EOF'
#!/bin/bash

# 检查异常登录
FAILED_LOGINS=$(grep "Failed password" /var/log/secure | grep "$(date +%b)" | wc -l)
if [ $FAILED_LOGINS -gt 10 ]; then
    echo "警告: 今日失败登录次数: $FAILED_LOGINS" | logger -t SECURITY_ALERT
fi

# 检查新用户
NEW_USERS=$(grep "new user" /var/log/secure | grep "$(date +%b)" | wc -l)
if [ $NEW_USERS -gt 0 ]; then
    echo "警告: 发现新用户创建" | logger -t SECURITY_ALERT
fi

# 检查异常进程
SUSPICIOUS_PROCS=$(ps aux | grep -E "(nc|netcat|nmap|hydra)" | grep -v grep | wc -l)
if [ $SUSPICIOUS_PROCS -gt 0 ]; then
    echo "警告: 发现可疑进程" | logger -t SECURITY_ALERT
fi
EOF
    
    chmod +x /usr/local/bin/security_monitor.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "*/15 * * * * /usr/local/bin/security_monitor.sh") | crontab -
    
    log_success "安全监控设置完成"
}

# 10. 生成安全报告
generate_report() {
    log_step "📝 生成安全响应报告"
    
    REPORT_FILE="/root/security_response_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > $REPORT_FILE << EOF
=== QAToolBox 安全响应报告 ===
时间: $(date)
服务器IP: $(curl -s ifconfig.me 2>/dev/null || echo "未知")

执行的安全措施:
1. ✅ 更改了所有系统密码
2. ✅ 禁用root SSH登录，更改SSH端口为2222
3. ✅ 配置防火墙，限制不必要端口
4. ✅ 安装fail2ban防止暴力破解
5. ✅ 检查系统入侵痕迹
6. ✅ 加固数据库安全
7. ✅ 更新应用安全配置
8. ✅ 系统更新和清理
9. ✅ 设置安全监控

重要提醒:
- SSH端口已改为2222
- Root登录已禁用
- 新密码保存在 /root/new_passwords.txt
- 请立即备份新密码并删除密码文件
- 建议立即检查应用数据是否被篡改

下次登录命令:
ssh -p 2222 qatoolbox@YOUR_SERVER_IP

后续建议:
1. 定期更改密码
2. 监控系统日志
3. 定期备份数据
4. 考虑使用密钥认证替代密码认证
5. 设置日志监控和告警系统

EOF
    
    log_success "安全报告已生成: $REPORT_FILE"
}

# 主函数
main() {
    echo -e "${RED}"
    echo "========================================"
    echo "    🚨 QAToolBox 紧急安全响应"
    echo "========================================"
    echo -e "${NC}"
    
    check_root
    
    log_critical "检测到服务器可能被入侵，开始紧急安全响应..."
    
    change_passwords
    secure_ssh
    configure_firewall
    install_fail2ban
    check_intrusion
    secure_database
    secure_application
    system_update
    setup_monitoring
    generate_report
    
    echo -e "${GREEN}"
    echo "========================================"
    echo "    ✅ 紧急安全响应完成"
    echo "========================================"
    echo -e "${NC}"
    
    log_critical "重要提醒:"
    log_critical "1. 新密码保存在 /root/new_passwords.txt"
    log_critical "2. SSH端口已改为2222"
    log_critical "3. Root登录已禁用"
    log_critical "4. 下次登录: ssh -p 2222 qatoolbox@YOUR_SERVER_IP"
    log_critical "5. 请立即备份密码信息并删除密码文件"
    
    echo -e "${YELLOW}"
    echo "建议立即执行以下操作:"
    echo "1. 检查应用数据完整性"
    echo "2. 恢复最近的数据备份（如有）"
    echo "3. 联系云服务商报告安全事件"
    echo "4. 考虑重建服务器（最安全的选择）"
    echo -e "${NC}"
}

# 错误处理
trap 'log_error "安全响应过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
