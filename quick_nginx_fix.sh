#!/bin/bash
# =============================================================================
# 快速修复Nginx配置脚本
# 解决CORS跨域问题
# =============================================================================

set -e

echo "🔧 开始修复Nginx配置..."

# 1. 备份原配置
echo "备份原Nginx配置..."
sudo cp /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-available/qatoolbox.backup.$(date +%s)

# 2. 应用新配置
echo "应用新的Nginx配置..."
sudo cp nginx_fixed.conf /etc/nginx/sites-available/qatoolbox

# 3. 测试配置
echo "测试Nginx配置..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx配置测试通过"
    
    # 4. 重启Nginx
    echo "重启Nginx服务..."
    sudo systemctl restart nginx
    
    # 5. 检查服务状态
    echo "检查Nginx服务状态..."
    sudo systemctl status nginx --no-pager
    
    echo ""
    echo "✅ Nginx配置修复完成！"
    echo ""
    echo "📋 测试命令："
    echo "curl -I http://47.103.143.152/"
    echo "curl -I http://47.103.143.152/users/api/session-status/"
    echo "curl -I http://47.103.143.152/users/generate-progressive-captcha/"
    
else
    echo "❌ Nginx配置测试失败，恢复原配置..."
    sudo cp /etc/nginx/sites-available/qatoolbox.backup.* /etc/nginx/sites-available/qatoolbox
    echo "请检查配置文件语法"
fi
