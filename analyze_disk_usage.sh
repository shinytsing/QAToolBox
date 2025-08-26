#!/bin/bash

# QAToolBox 磁盘空间占用分析脚本
# 找出为什么Django项目占用了近40GB空间

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

print_header "🔍 QAToolBox 磁盘空间占用分析"
print_status "正在分析为什么Django项目占用了近40GB空间..."

# ================================
# [1] 总体磁盘使用情况
# ================================
print_header "[1] 总体磁盘使用情况"

print_status "📊 当前磁盘使用情况："
df -h

print_status "📊 根目录各子目录大小："
du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20

# ================================
# [2] 系统目录详细分析
# ================================
print_header "[2] 系统目录详细分析"

print_status "🔍 /var 目录分析（通常是日志和缓存的大户）："
if [ -d "/var" ]; then
    du -h --max-depth=2 /var 2>/dev/null | sort -hr | head -20
fi

print_status "🔍 /usr 目录分析（系统程序和包）："
if [ -d "/usr" ]; then
    du -h --max-depth=2 /usr 2>/dev/null | sort -hr | head -15
fi

print_status "🔍 /tmp 和 /var/tmp 临时文件："
du -h /tmp /var/tmp 2>/dev/null || true

# ================================
# [3] 日志文件分析
# ================================
print_header "[3] 日志文件分析"

print_status "📝 查找大于100MB的日志文件："
find /var/log -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -20

print_status "📝 /var/log 目录详细分析："
if [ -d "/var/log" ]; then
    du -h --max-depth=2 /var/log 2>/dev/null | sort -hr | head -20
fi

print_status "📝 systemd journal 大小："
journalctl --disk-usage 2>/dev/null || echo "无法获取journal大小"

# ================================
# [4] QAToolBox项目分析
# ================================
print_header "[4] QAToolBox项目分析"

if [ -d "/home/qatoolbox" ]; then
    print_status "📁 /home/qatoolbox 目录大小分析："
    du -h --max-depth=2 /home/qatoolbox 2>/dev/null | sort -hr
    
    if [ -d "/home/qatoolbox/QAToolbox" ]; then
        print_status "📁 QAToolbox项目内部分析："
        cd /home/qatoolbox/QAToolbox
        du -h --max-depth=2 . 2>/dev/null | sort -hr | head -20
        
        print_status "🔍 查找项目中的大文件（>50MB）："
        find . -type f -size +50M -exec ls -lh {} \; 2>/dev/null | head -20
        
        print_status "🐍 Python虚拟环境大小："
        if [ -d ".venv" ]; then
            du -h --max-depth=2 .venv 2>/dev/null | sort -hr | head -10
        fi
        
        print_status "📁 媒体文件大小："
        if [ -d "media" ]; then
            du -h --max-depth=2 media 2>/dev/null | sort -hr | head -10
        fi
        
        print_status "📁 静态文件大小："
        if [ -d "staticfiles" ]; then
            du -h staticfiles 2>/dev/null
        fi
        if [ -d "static" ]; then
            du -h static 2>/dev/null
        fi
        
        print_status "📦 Python缓存文件："
        find . -name "__pycache__" -type d -exec du -sh {} \; 2>/dev/null | head -10
        
        print_status "🗂️ 备份文件："
        find . -name "*.backup*" -type f -exec ls -lh {} \; 2>/dev/null | head -10
        find . -name "QAToolbox.backup.*" -type d -exec du -sh {} \; 2>/dev/null
    fi
else
    print_warning "QAToolBox项目目录不存在"
fi

# ================================
# [5] 包管理器缓存分析
# ================================
print_header "[5] 包管理器缓存分析"

print_status "📦 APT缓存大小："
du -h /var/cache/apt 2>/dev/null || echo "APT缓存目录不存在"

print_status "🐍 pip缓存大小："
if [ -d "/root/.cache/pip" ]; then
    du -h /root/.cache/pip 2>/dev/null
fi
if [ -d "/home/qatoolbox/.cache" ]; then
    du -h /home/qatoolbox/.cache 2>/dev/null
fi

print_status "📦 Snap包大小："
if [ -d "/var/lib/snapd" ]; then
    du -h /var/lib/snapd 2>/dev/null
fi

# ================================
# [6] Docker和容器分析
# ================================
print_header "[6] Docker和容器分析"

if command -v docker &> /dev/null; then
    print_status "🐳 Docker空间使用情况："
    docker system df 2>/dev/null || echo "无法获取Docker信息"
    
    print_status "🐳 Docker根目录大小："
    du -h /var/lib/docker 2>/dev/null | tail -1 || echo "Docker目录不存在"
else
    print_status "Docker未安装"
fi

# ================================
# [7] 数据库文件分析
# ================================
print_header "[7] 数据库文件分析"

print_status "🗃️ PostgreSQL数据文件大小："
if [ -d "/var/lib/postgresql" ]; then
    du -h --max-depth=2 /var/lib/postgresql 2>/dev/null | sort -hr
fi

print_status "🗃️ Redis数据文件大小："
if [ -f "/var/lib/redis/dump.rdb" ]; then
    ls -lh /var/lib/redis/dump.rdb
fi

# ================================
# [8] 系统包和软件分析
# ================================
print_header "[8] 系统包和软件分析"

print_status "📦 已安装包大小分析："
dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n | tail -20 | awk '{printf "%.2f MB\t%s\n", $1/1024, $2}'

print_status "🔍 查找系统中最大的文件（前20个）："
find / -type f -size +100M 2>/dev/null | head -20 | xargs ls -lh 2>/dev/null | sort -k5 -hr | head -20

# ================================
# [9] 异常大文件检测
# ================================
print_header "[9] 异常大文件检测"

print_status "🚨 查找异常大的文件（>500MB）："
find / -type f -size +500M 2>/dev/null | head -20 | xargs ls -lh 2>/dev/null

print_status "🚨 查找异常大的目录（>1GB）："
find / -type d -size +1G 2>/dev/null | head -10 | xargs du -sh 2>/dev/null || echo "没有发现异常大的目录"

# ================================
# [10] 可清理空间预估
# ================================
print_header "[10] 可清理空间预估"

total_cleanable=0

# 日志文件
log_size=$(find /var/log -type f -name "*.log*" -size +10M 2>/dev/null | xargs du -ch 2>/dev/null | tail -1 | cut -f1 | sed 's/G/000M/; s/M//; s/K/0.001M/' | cut -d. -f1 2>/dev/null || echo "0")
print_status "📝 可清理日志文件: ${log_size}MB"

# APT缓存
apt_size=$(du -sm /var/cache/apt 2>/dev/null | cut -f1 || echo "0")
print_status "📦 APT缓存: ${apt_size}MB"

# 临时文件
tmp_size=$(du -sm /tmp /var/tmp 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
print_status "🗑️ 临时文件: ${tmp_size}MB"

# Python缓存
python_cache_size=0
if [ -d "/home/qatoolbox" ]; then
    python_cache_size=$(find /home/qatoolbox -name "__pycache__" -type d -exec du -sm {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
fi
print_status "🐍 Python缓存: ${python_cache_size}MB"

total_cleanable=$((log_size + apt_size + tmp_size + python_cache_size))
print_status "💾 预估可清理空间: ${total_cleanable}MB"

# ================================
# 分析总结
# ================================
print_header "📋 分析总结"

current_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
used_space=$(df / | awk 'NR==2 {print $3}')
used_gb=$((used_space / 1024 / 1024))

cat << EOF
🔍 磁盘使用分析总结:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 当前状态:
   • 磁盘使用率: ${current_usage}%
   • 已用空间: ~${used_gb}GB
   • 总容量: 40GB

🔍 主要占用空间的目录:
$(du -h --max-depth=1 / 2>/dev/null | sort -hr | head -10 | sed 's/^/   • /')

💡 建议操作:
   1. 立即清理日志文件和缓存 (预估释放: ${total_cleanable}MB)
   2. 检查是否有异常大的文件需要删除
   3. 考虑将媒体文件移至对象存储
   4. 磁盘扩容至100GB

🚨 异常检查:
   • 检查是否有程序在疯狂写日志
   • 检查是否有大文件被意外下载
   • 检查数据库是否有异常增长

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

print_success "磁盘空间分析完成！"

# 生成清理建议脚本
print_status "📝 生成针对性清理脚本..."
cat > /tmp/targeted_cleanup.sh << 'EOF'
#!/bin/bash
# 基于分析结果的针对性清理脚本

echo "🚀 开始针对性清理..."

# 清理大日志文件
find /var/log -type f -size +50M -exec truncate -s 10M {} \;
find /var/log -name "*.log.*" -mtime +3 -delete

# 清理系统缓存
apt clean
apt autoclean

# 清理临时文件
rm -rf /tmp/* /var/tmp/* 2>/dev/null || true

# 清理Python缓存
find /home/qatoolbox -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# 清理journal日志
journalctl --vacuum-time=3d

echo "✅ 针对性清理完成"
df -h
EOF

chmod +x /tmp/targeted_cleanup.sh
print_status "针对性清理脚本已生成: /tmp/targeted_cleanup.sh"

echo ""
print_warning "正常情况下，一个Django项目（包含虚拟环境）应该只占用几百MB到几GB空间"
print_warning "40GB的占用明显异常，请仔细检查上述分析结果！"
