#!/bin/bash
# 推送到GitHub

echo "🔄 准备推送到GitHub..."

# 检查是否已初始化git
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git仓库初始化完成"
fi

# 添加所有文件
git add .

# 创建提交
git commit -m "feat: 添加完整的一键部署脚本

- 🚀 支持阿里云服务器一键部署
- ✅ 解决torch、environ等依赖问题  
- 🔧 包含完整的系统配置
- 🌐 配置Nginx、PostgreSQL、Redis
- 📱 支持域名https://shenyiqing.xin/
- 🧪 包含部署验证脚本

部署命令:
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_aliyun_one_click.sh | sudo bash"

echo "📤 准备推送到GitHub（请先设置远程仓库）"
echo ""
echo "设置远程仓库命令："
echo "git remote add origin https://github.com/shinytsing/QAToolbox.git"
echo ""
echo "推送命令："
echo "git branch -M main"
echo "git push -u origin main"
