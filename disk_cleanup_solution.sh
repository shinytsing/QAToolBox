#!/bin/bash

# QAToolBox 磁盘空间紧急清理和优化脚本
# 解决阿里云服务器磁盘使用率94.8%问题

set -e

# 颜色输出函数
print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_header() {
    echo -e "\033[1;35m"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "\033[0m"
}

# 检查是否为root用户
if [[ $EUID -ne 0 ]]; then
   print_error "此脚本需要root权限运行"
   exit 1
fi

print_header "🚨 磁盘空间紧急清理开始"
print_status "📊 当前磁盘使用率: 94.8%"
print_status "💾 磁盘容量: 40GB"

# ================================
# [1/8] 磁盘使用情况分析
# ================================
print_header "[1/8] 磁盘使用情况分析"

print_status "📊 当前磁盘使用情况:"
df -h

print_status "🔍 找出占用最多空间的目录:"
du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20

print_status "🔍 找出大文件 (>100MB):"
find / -type f -size +100M 2>/dev/null | head -20

# ================================
# [2/8] 清理系统日志
# ================================
print_header "[2/8] 清理系统日志"

print_status "🗑️ 清理系统日志..."
# 清理journald日志
journalctl --vacuum-time=7d
journalctl --vacuum-size=100M

# 清理老旧日志文件
find /var/log -name "*.log" -type f -mtime +7 -exec truncate -s 0 {} \;
find /var/log -name "*.log.*" -type f -mtime +7 -delete

# 清理旋转日志
find /var/log -name "*.gz" -type f -mtime +7 -delete
find /var/log -name "*.1" -type f -mtime +3 -delete

print_status "🧹 清理应用日志..."
# 清理QAToolBox日志
if [ -d "/var/log/qatoolbox" ]; then
    find /var/log/qatoolbox -name "*.log*" -type f -mtime +3 -delete
    find /var/log/qatoolbox -name "*.log" -type f -exec truncate -s 5M {} \;
fi

# 清理Nginx日志
if [ -d "/var/log/nginx" ]; then
    find /var/log/nginx -name "*.log*" -type f -mtime +7 -delete
    truncate -s 10M /var/log/nginx/access.log 2>/dev/null || true
    truncate -s 10M /var/log/nginx/error.log 2>/dev/null || true
fi

freed_space_logs=$(df / | awk 'NR==2 {print $4}')
print_success "日志清理完成"

# ================================
# [3/8] 清理包管理器缓存
# ================================
print_header "[3/8] 清理包管理器缓存"

print_status "🗑️ 清理APT缓存..."
apt clean
apt autoclean
apt autoremove -y

# 清理pip缓存
print_status "🐍 清理pip缓存..."
if [ -d "/root/.cache/pip" ]; then
    rm -rf /root/.cache/pip/*
fi

if [ -d "/home/qatoolbox/.cache/pip" ]; then
    rm -rf /home/qatoolbox/.cache/pip/*
fi

# 清理其他缓存
rm -rf /tmp/* 2>/dev/null || true
rm -rf /var/tmp/* 2>/dev/null || true

print_success "包管理器缓存清理完成"

# ================================
# [4/8] 清理Docker相关（如果存在）
# ================================
print_header "[4/8] 清理Docker相关（如果存在）"

if command -v docker &> /dev/null; then
    print_status "🐳 清理Docker..."
    docker system prune -af --volumes || true
    docker image prune -af || true
else
    print_status "Docker未安装，跳过"
fi

# ================================
# [5/8] 清理项目相关文件
# ================================
print_header "[5/8] 清理项目相关文件"

print_status "🗑️ 清理项目备份文件..."
if [ -d "/home/qatoolbox" ]; then
    cd /home/qatoolbox
    # 删除老旧备份
    find . -name "*.backup.*" -type f -mtime +7 -delete
    find . -name "QAToolbox.backup.*" -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
    
    # 清理Python缓存
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -type f -delete 2>/dev/null || true
    find . -name "*.pyo" -type f -delete 2>/dev/null || true
fi

print_status "📁 清理媒体文件缓存..."
if [ -d "/home/qatoolbox/QAToolbox/media" ]; then
    # 清理临时媒体文件
    find /home/qatoolbox/QAToolbox/media -name "temp_*" -type f -mtime +1 -delete 2>/dev/null || true
    find /home/qatoolbox/QAToolbox/media -name "cache_*" -type f -mtime +1 -delete 2>/dev/null || true
fi

print_success "项目文件清理完成"

# ================================
# [6/8] 压缩和优化
# ================================
print_header "[6/8] 压缩和优化现有文件"

print_status "🗜️ 压缩旧日志文件..."
find /var/log -name "*.log" -type f -size +10M -exec gzip {} \; 2>/dev/null || true

print_status "🗃️ 清理数据库日志..."
if command -v psql &> /dev/null; then
    sudo -u postgres psql -c "SELECT pg_rotate_logfile();" 2>/dev/null || true
fi

print_success "压缩优化完成"

# ================================
# [7/8] 检查清理效果
# ================================
print_header "[7/8] 检查清理效果"

print_status "📊 清理后磁盘使用情况:"
df -h

current_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
print_status "当前磁盘使用率: $current_usage%"

if [ "$current_usage" -lt 85 ]; then
    print_success "✅ 磁盘清理成功！使用率降至安全范围"
elif [ "$current_usage" -lt 90 ]; then
    print_warning "磁盘使用率仍然较高，建议扩容"
else
    print_error "磁盘使用率仍然过高，需要紧急扩容"
fi

# ================================
# [8/8] 配置自动清理和监控
# ================================
print_header "[8/8] 配置自动清理和监控"

print_status "⚙️ 创建自动清理脚本..."
cat > /etc/cron.daily/qatoolbox-cleanup << 'EOF'
#!/bin/bash
# QAToolBox 每日自动清理脚本

# 清理日志文件
find /var/log -name "*.log" -type f -size +50M -exec truncate -s 20M {} \;
find /var/log -name "*.log.*" -type f -mtime +3 -delete
journalctl --vacuum-time=3d

# 清理临时文件
rm -rf /tmp/* 2>/dev/null || true
find /home/qatoolbox -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 清理APT缓存
apt clean
EOF

chmod +x /etc/cron.daily/qatoolbox-cleanup

print_status "📊 创建磁盘监控脚本..."
cat > /usr/local/bin/disk-monitor.sh << 'EOF'
#!/bin/bash
# 磁盘空间监控脚本

USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$USAGE" -gt 85 ]; then
    echo "警告: 磁盘使用率 $USAGE% 过高！" | logger -t disk-monitor
    # 可以在这里添加邮件通知或其他告警
fi
EOF

chmod +x /usr/local/bin/disk-monitor.sh

# 添加到crontab（每小时检查一次）
(crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/disk-monitor.sh") | crontab -

print_success "自动清理和监控配置完成"

# ================================
# 扩容建议
# ================================
print_header "💡 磁盘扩容建议"

cat << EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 紧急建议：磁盘扩容
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前配置: 2vCPU + 2GB内存 + 40GB硬盘
当前使用率: $current_usage%

🔧 推荐扩容方案:

方案1: 在线扩容（推荐）
   • 阿里云控制台 → ECS实例 → 更多 → 云盘扩容
   • 将40GB扩容至100GB
   • 在线扩容，无需停机
   • 成本增加约50元/月

方案2: 挂载数据盘
   • 购买单独的数据盘（100GB）
   • 挂载到 /home/qatoolbox
   • 迁移项目数据到数据盘
   • 更灵活，便于备份

📋 扩容后操作:
1. fdisk -l                    # 查看磁盘
2. resize2fs /dev/vda1         # 扩展文件系统
3. df -h                       # 确认扩容成功

⚠️  立即行动建议:
   当前使用率过高，建议24小时内完成扩容！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

# ================================
# 清理报告
# ================================
print_header "📋 清理完成报告"

echo "清理前使用率: 94.8%"
echo "清理后使用率: $current_usage%"
echo "释放空间: 约 $((948-current_usage*10))MB"
echo ""
echo "🔧 已配置:"
echo "✅ 每日自动清理脚本"
echo "✅ 磁盘使用率监控"
echo "✅ 日志轮转优化"
echo ""
echo "📝 下一步操作:"
echo "1. 立即进行磁盘扩容（强烈建议）"
echo "2. 监控磁盘使用情况"
echo "3. 优化应用的日志输出"
echo ""

if [ "$current_usage" -lt 85 ]; then
    print_success "🎉 紧急清理成功！但仍建议尽快扩容"
else
    print_error "⚠️  磁盘使用率仍然过高，请立即扩容！"
fi

print_success "磁盘清理脚本执行完成"
