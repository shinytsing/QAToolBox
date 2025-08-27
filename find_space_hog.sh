#!/bin/bash

# 精准找出磁盘空间占用大户的脚本
# 专门解决40GB异常占用问题

set -e

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
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo -e "\033[1;35m$1\033[0m"
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
}

print_header "🔍 精准定位40GB空间占用大户"

print_status "📊 当前磁盘使用："
df -h /

print_header "🎯 逐级深入分析"

print_status "🔍 根目录一级分析："
timeout 30 du -h --max-depth=1 / 2>/dev/null | sort -hr | head -15

print_status "🔍 /usr 目录详细分析（系统软件）："
timeout 30 du -h --max-depth=2 /usr 2>/dev/null | sort -hr | head -15

print_status "🔍 /var 目录详细分析（变量数据）："
timeout 30 du -h --max-depth=2 /var 2>/dev/null | sort -hr | head -15

print_status "🔍 /home 目录详细分析："
if [ -d "/home" ]; then
    timeout 30 du -h --max-depth=2 /home 2>/dev/null | sort -hr | head -15
fi

print_status "🔍 /root 目录分析："
if [ -d "/root" ]; then
    timeout 30 du -h --max-depth=2 /root 2>/dev/null | sort -hr | head -10
fi

print_header "🚨 查找超大文件"

print_status "🔍 查找 >500MB 的文件："
timeout 60 find / -type f -size +500M 2>/dev/null | head -20 | while read file; do
    ls -lh "$file" 2>/dev/null || echo "无法访问: $file"
done

print_status "🔍 查找 >200MB 的文件："
timeout 60 find / -type f -size +200M 2>/dev/null | head -30 | while read file; do
    ls -lh "$file" 2>/dev/null || echo "无法访问: $file"
done

print_header "🔍 特定目录深入分析"

print_status "🔍 /var/lib 目录分析（数据库、包等）："
if [ -d "/var/lib" ]; then
    timeout 30 du -h --max-depth=2 /var/lib 2>/dev/null | sort -hr | head -15
fi

print_status "🔍 /var/cache 目录分析（缓存）："
if [ -d "/var/cache" ]; then
    timeout 30 du -h --max-depth=2 /var/cache 2>/dev/null | sort -hr | head -15
fi

print_status "🔍 /opt 目录分析（可选软件）："
if [ -d "/opt" ]; then
    timeout 30 du -h --max-depth=2 /opt 2>/dev/null | sort -hr | head -10
fi

print_status "🔍 /snap 目录分析（Snap包）："
if [ -d "/snap" ]; then
    timeout 30 du -h --max-depth=2 /snap 2>/dev/null | sort -hr | head -10
fi

print_header "🐍 Python相关分析"

print_status "🔍 查找Python相关大文件："
timeout 60 find / -name "*.whl" -o -name "*.egg" -o -name "site-packages" 2>/dev/null | while read item; do
    if [ -f "$item" ]; then
        size=$(stat -f%z "$item" 2>/dev/null || stat -c%s "$item" 2>/dev/null || echo 0)
        if [ "$size" -gt 10485760 ]; then  # >10MB
            ls -lh "$item" 2>/dev/null
        fi
    elif [ -d "$item" ]; then
        du -h "$item" 2>/dev/null | tail -1
    fi
done | sort -hr | head -20

print_status "🔍 pip缓存目录："
for cache_dir in "/root/.cache/pip" "/home/*/.cache/pip" "/home/qatoolbox/.cache"; do
    if [ -d "$cache_dir" ]; then
        echo "$cache_dir: $(du -sh "$cache_dir" 2>/dev/null | cut -f1)"
    fi
done

print_header "🗃️ 数据库和存储分析"

print_status "🔍 PostgreSQL数据目录："
for pg_dir in "/var/lib/postgresql" "/usr/local/var/postgres"; do
    if [ -d "$pg_dir" ]; then
        timeout 30 du -h --max-depth=2 "$pg_dir" 2>/dev/null | sort -hr | head -10
    fi
done

print_status "🔍 Redis数据文件："
for redis_file in "/var/lib/redis/dump.rdb" "/usr/local/var/db/redis/dump.rdb"; do
    if [ -f "$redis_file" ]; then
        ls -lh "$redis_file"
    fi
done

print_header "📦 包管理和软件"

print_status "🔍 Docker相关："
if command -v docker >/dev/null 2>&1; then
    echo "Docker系统使用："
    docker system df 2>/dev/null || echo "无法获取Docker信息"
    
    if [ -d "/var/lib/docker" ]; then
        echo "Docker目录大小："
        timeout 30 du -h --max-depth=2 /var/lib/docker 2>/dev/null | sort -hr | head -10
    fi
else
    echo "Docker未安装"
fi

print_status "🔍 最大的已安装包："
dpkg-query -Wf '${Installed-Size}\t${Package}\n' 2>/dev/null | sort -n | tail -15 | awk '{printf "%.1f MB\t%s\n", $1/1024, $2}'

print_header "🔧 快速清理建议"

# 计算可清理空间
journal_size=$(journalctl --disk-usage 2>/dev/null | grep -o '[0-9.]*[KMGT]B' | head -1 || echo "0B")
apt_cache_size=$(du -sh /var/cache/apt 2>/dev/null | cut -f1 || echo "0B")
pip_cache_size=$(find /root/.cache /home/*/.cache -name "pip" -type d -exec du -sh {} \; 2>/dev/null | awk '{sum+=$1} END {print sum "B"}' || echo "0B")

cat << EOF

📋 清理建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗑️ 立即可清理的项目：
   • Journal日志: $journal_size (执行: journalctl --vacuum-time=3d)
   • APT缓存: $apt_cache_size (执行: apt clean)
   • pip缓存: $pip_cache_size (执行: rm -rf ~/.cache/pip/*)
   • 临时文件: $(du -sh /tmp 2>/dev/null | cut -f1) (执行: rm -rf /tmp/*)

⚠️  需要检查的异常项目：
   • 查看上述分析中超过1GB的目录
   • 查看是否有异常大的数据库文件
   • 查看是否有程序在持续写大文件

🚀 快速清理命令：
   sudo journalctl --vacuum-time=3d
   sudo apt clean && sudo apt autoremove -y
   sudo rm -rf /tmp/* /var/tmp/*
   sudo find /root/.cache /home/*/.cache -name "pip" -exec rm -rf {} + 2>/dev/null

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

print_warning "正常Django项目 + 依赖应该 < 5GB，40GB使用率明显异常！"
print_warning "请仔细检查上述分析中超过1GB的目录！"

print_success "磁盘占用分析完成！"





