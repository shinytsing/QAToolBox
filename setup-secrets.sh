#!/bin/bash

# QAToolBox GitHub Secrets 快速配置脚本
# 使用GitHub CLI自动配置所有必需的Secrets

set -e

echo "🔐 QAToolBox GitHub Secrets 快速配置"
echo "====================================="

# 检查GitHub CLI是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI 未安装"
    echo "请先安装: brew install gh 或 https://cli.github.com/"
    exit 1
fi

# 检查是否已登录GitHub
if ! gh auth status &> /dev/null; then
    echo "🔑 请先登录GitHub CLI..."
    gh auth login
fi

echo "📋 开始配置GitHub Secrets..."

# 服务器连接配置
echo "🖥️  配置服务器连接..."
gh secret set SERVER_HOST --body "47.103.143.152"
gh secret set SERVER_USER --body "root"
gh secret set SERVER_PORT --body "22"

# SSH私钥配置
echo "🔑 配置SSH私钥..."
if [ -f ~/.ssh/qatoolbox_deploy ]; then
    gh secret set SERVER_SSH_KEY --body "$(cat ~/.ssh/qatoolbox_deploy)"
    echo "✅ SSH私钥已配置"
else
    echo "❌ SSH私钥文件不存在: ~/.ssh/qatoolbox_deploy"
    echo "请先运行: ssh-keygen -t rsa -b 4096 -f ~/.ssh/qatoolbox_deploy"
    exit 1
fi

# 邮件通知配置
echo "📧 配置邮件通知..."
gh secret set EMAIL_USERNAME --body "gj00forwork@gmail.com"
gh secret set EMAIL_PASSWORD --body "c9d5&b5z"

# API密钥配置
echo "🔑 配置API密钥..."
gh secret set DEEPSEEK_API_KEY --body "sk-c4a84c8bbff341cbb3006ecaf84030fe"

# 其他可选API密钥
echo "❓ 配置其他API密钥（可选）..."
read -p "是否配置Google API密钥？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入Google API密钥: " GOOGLE_API_KEY
    if [ ! -z "$GOOGLE_API_KEY" ]; then
        gh secret set GOOGLE_API_KEY --body "$GOOGLE_API_KEY"
        echo "✅ Google API密钥已配置"
    fi
    
    read -p "请输入Google搜索引擎ID: " GOOGLE_CSE_ID
    if [ ! -z "$GOOGLE_CSE_ID" ]; then
        gh secret set GOOGLE_CSE_ID --body "$GOOGLE_CSE_ID"
        echo "✅ Google搜索引擎ID已配置"
    fi
fi

read -p "是否配置天气API密钥？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "请输入OpenWeather API密钥: " OPENWEATHER_API_KEY
    if [ ! -z "$OPENWEATHER_API_KEY" ]; then
        gh secret set OPENWEATHER_API_KEY --body "$OPENWEATHER_API_KEY"
        echo "✅ 天气API密钥已配置"
    fi
fi

echo ""
echo "✅ GitHub Secrets 配置完成！"
echo ""
echo "📋 已配置的Secrets:"
gh secret list

echo ""
echo "🧪 测试配置:"
echo "1. 推送代码到develop分支测试CI"
echo "2. 推送代码到main分支测试CD"
echo "3. 手动触发CD-持续交付工作流"
echo "4. 检查邮件: 1009383129@qq.com"
echo ""
echo "🎉 配置完成，CI/CD流水线已就绪！"
