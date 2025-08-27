#!/bin/bash

# 找出剩余30GB空间藏在哪里的脚本

set -e

print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_header() {
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo -e "\033[1;35m$1\033[0m"
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
}

print_header "🔍 寻找剩余30GB空间的藏身之处"

print_status "📊 当前磁盘情况："
df -h /

print_status "🔍 完整的根目录分析："
du -h --max-depth=1 / 2>/dev/null | sort -hr

print_header "🎯 深入检查可疑目录"

print_status "🔍 /home 目录完整分析："
if [ -d "/home" ]; then
    du -h --max-depth=3 /home 2>/dev/null | sort -hr | head -20
fi

print_status "🔍 /root 目录分析："
if [ -d "/root" ]; then
    du -h --max-depth=2 /root 2>/dev/null | sort -hr
fi

print_status "🔍 /opt 目录分析："
if [ -d "/opt" ]; then
    du -h --max-depth=2 /opt 2>/dev/null | sort -hr
fi

print_status "🔍 /mnt 和 /media 目录："
for dir in /mnt /media; do
    if [ -d "$dir" ]; then
        echo "$dir 内容："
        du -h --max-depth=2 "$dir" 2>/dev/null | sort -hr
    fi
done

print_status "🔍 /snap 目录详细分析："
if [ -d "/snap" ]; then
    du -h --max-depth=2 /snap 2>/dev/null | sort -hr | head -15
fi

print_status "🔍 /var/lib/snapd 详细分析："
if [ -d "/var/lib/snapd" ]; then
    du -h --max-depth=2 /var/lib/snapd 2>/dev/null | sort -hr | head -10
fi

print_header "🚨 查找隐藏的大文件"

print_status "🔍 查找所有超过1GB的文件："
find / -type f -size +1G 2>/dev/null | while read file; do
    ls -lh "$file" 2>/dev/null
done

print_status "🔍 查找所有超过500MB的文件："
find / -type f -size +500M 2>/dev/null | head -30 | while read file; do
    ls -lh "$file" 2>/dev/null
done

print_status "🔍 查找所有超过200MB的文件："
find / -type f -size +200M 2>/dev/null | head -50 | while read file; do
    ls -lh "$file" 2>/dev/null
done

print_header "🐍 Python环境深度分析"

print_status "🔍 查找所有Python site-packages："
find / -name "site-packages" -type d 2>/dev/null | while read dir; do
    echo "发现 site-packages: $dir"
    du -sh "$dir" 2>/dev/null
    echo "  最大的包："
    du -h --max-depth=1 "$dir" 2>/dev/null | sort -hr | head -5
    echo ""
done

print_status "🔍 查找Python缓存和编译文件："
find / -name "__pycache__" -type d 2>/dev/null | head -20 | xargs du -sh 2>/dev/null
find / -name "*.pyc" -size +1M 2>/dev/null | head -20 | xargs ls -lh 2>/dev/null

print_status "🔍 查找pip缓存："
find / -path "*/.cache/pip" -type d 2>/dev/null | while read dir; do
    echo "Pip缓存: $dir"
    du -sh "$dir" 2>/dev/null
done

print_header "🗃️ 数据库和存储深度分析"

print_status "🔍 PostgreSQL详细分析："
if [ -d "/var/lib/postgresql" ]; then
    find /var/lib/postgresql -type f -size +10M 2>/dev/null | xargs ls -lh 2>/dev/null
fi

print_status "🔍 查找所有数据库文件："
find / -name "*.db" -o -name "*.sqlite*" -o -name "*.sql" 2>/dev/null | while read file; do
    size=$(stat -c%s "$file" 2>/dev/null || echo 0)
    if [ "$size" -gt 10485760 ]; then  # >10MB
        ls -lh "$file" 2>/dev/null
    fi
done

print_header "🔄 进程和临时文件分析"

print_status "🔍 检查当前运行进程的打开文件："
lsof +L1 2>/dev/null | grep -E "(deleted|UNLINKED)" | head -20

print_status "🔍 查找大的临时文件："
find /tmp /var/tmp -type f -size +10M 2>/dev/null | xargs ls -lh 2>/dev/null

print_status "🔍 查找最近修改的大文件："
find / -type f -size +100M -mtime -7 2>/dev/null | head -20 | xargs ls -lth 2>/dev/null

print_header "📦 包和软件分析"

print_status "🔍 Docker相关完整分析："
if command -v docker >/dev/null 2>&1; then
    echo "Docker系统信息："
    docker system df 2>/dev/null
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>/dev/null | head -20
    
    if [ -d "/var/lib/docker" ]; then
        echo ""
        echo "Docker目录详细分析："
        du -h --max-depth=2 /var/lib/docker 2>/dev/null | sort -hr | head -15
    fi
fi

print_status "🔍 查找所有可执行文件（可能的下载软件）："
find /usr/local /opt /home -type f -executable -size +50M 2>/dev/null | head -20 | xargs ls -lh 2>/dev/null

print_header "🔍 隐藏目录和特殊文件"

print_status "🔍 查找以点开头的隐藏大目录："
find / -name ".*" -type d -size +100M 2>/dev/null | head -20 | xargs du -sh 2>/dev/null

print_status "🔍 查找所有挂载点："
mount | grep -v tmpfs | grep -v devtmpfs

print_status "🔍 查找最大的目录（全盘搜索）："
timeout 300 find / -type d -exec du -s {} \; 2>/dev/null | sort -rn | head -20 | while read size dir; do
    size_mb=$((size / 1024))
    if [ $size_mb -gt 100 ]; then
        echo "${size_mb}MB  $dir"
    fi
done

print_header "📊 磁盘使用总结"

total_accounted=0
echo "已知占用空间："
echo "  /usr: 4.9GB"
echo "  /var/lib: 1.3GB" 
echo "  /var/log: 0.5GB"
echo "  系统基础: ~2GB"
echo "  总计约: ~9GB"
echo ""
echo "还有约 30GB 空间未找到！"
echo ""

print_warning "如果上述分析仍未找到30GB的占用，可能存在以下情况："
echo "1. 文件系统损坏或有隐藏分区"
echo "2. 某个进程持有大量已删除文件的句柄"
echo "3. 稀疏文件或特殊文件系统特性"
echo "4. 硬链接导致重复计算"

print_status "执行额外检查："
echo ""
echo "inode使用情况："
df -i /

echo ""
echo "文件系统类型："
df -T /

print_success "深度空间分析完成！"






