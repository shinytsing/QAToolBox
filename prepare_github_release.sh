#!/bin/bash
# 准备GitHub发布的脚本
# =============================================

echo "🚀 准备QAToolBox GitHub发布..."

# 创建发布目录
mkdir -p github_release
cd github_release

# 复制必要文件
echo "📋 复制部署文件..."
cp ../deploy_complete_with_all_deps.sh .
cp ../deploy_quick_start.sh .
cp ../deploy_aliyun_one_click.sh .
cp ../test_deployment.sh .
cp ../requirements_complete.txt .
cp ../env.production.complete .
cp ../README_DEPLOY.md .
cp ../DEPLOYMENT_GUIDE.md .

# 创建Git提交和推送脚本
cat > git_push_to_github.sh << 'EOF'
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
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/QAToolBox/main/deploy_aliyun_one_click.sh | sudo bash"

echo "📤 准备推送到GitHub（请先设置远程仓库）"
echo ""
echo "设置远程仓库命令："
echo "git remote add origin https://github.com/YOUR_USERNAME/QAToolBox.git"
echo ""
echo "推送命令："
echo "git branch -M main"
echo "git push -u origin main"
EOF

chmod +x git_push_to_github.sh

echo "✅ GitHub发布准备完成！"
echo ""
echo "📁 发布文件位置: ./github_release/"
echo ""
echo "🔗 下一步操作："
echo "1. cd github_release"
echo "2. 设置GitHub仓库: git remote add origin https://github.com/YOUR_USERNAME/QAToolBox.git"
echo "3. 推送: ./git_push_to_github.sh"
echo ""
