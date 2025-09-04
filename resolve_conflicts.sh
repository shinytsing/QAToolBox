#!/bin/bash
# =============================================================================
# 解决Git冲突脚本
# 处理服务器上的本地修改
# =============================================================================

set -e

echo "🔧 解决Git冲突..."

# 1. 查看当前状态
echo "查看当前Git状态..."
git status

# 2. 备份本地修改
echo "备份本地修改..."
mkdir -p backup_$(date +%Y%m%d_%H%M%S)
cp config/settings/testing.py backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "testing.py不存在"
cp env.production backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "env.production不存在"
cp pyproject.toml backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "pyproject.toml不存在"
cp quick_fix_compose.sh backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "quick_fix_compose.sh不存在"
cp requirements.txt backup_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || echo "requirements.txt不存在"

# 3. 重置到远程状态
echo "重置到远程状态..."
git fetch origin main
git reset --hard origin/main

# 4. 验证更新
echo "验证更新..."
git status
git log --oneline -5

# 5. 检查文件是否存在
echo "检查修复脚本..."
ls -la comprehensive_fix.sh
ls -la nginx_comprehensive.conf

# 6. 执行修复
echo "执行综合修复..."
chmod +x comprehensive_fix.sh
./comprehensive_fix.sh

echo "✅ 冲突解决完成！"
echo ""
echo "📋 下一步操作："
echo "1. 更新Nginx: sudo cp nginx_comprehensive.conf /etc/nginx/sites-available/qatoolbox"
echo "2. 重启服务: ./restart_all.sh"
echo "3. 测试修复: ./test_comprehensive.sh"
