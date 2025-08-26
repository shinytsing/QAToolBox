#!/bin/bash

# QAToolBox 用户权限修复和部署脚本

echo "🔧 修复用户权限并部署QAToolBox..."

# 如果是root用户，切换到qatoolbox用户
if [[ $EUID -eq 0 ]]; then
    echo "检测到root用户，切换到qatoolbox用户..."
    
    # 确保qatoolbox用户存在并有sudo权限
    if id "qatoolbox" &>/dev/null; then
        echo "✅ qatoolbox用户已存在"
    else
        echo "创建qatoolbox用户..."
        adduser --disabled-password --gecos "" qatoolbox
    fi
    
    # 添加sudo权限
    usermod -aG sudo qatoolbox
    
    # 设置密码（可选）
    echo "qatoolbox:qatoolbox123" | chpasswd
    
    echo "🚀 切换到qatoolbox用户并开始部署..."
    su - qatoolbox -c 'bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh)'
else
    echo "🚀 使用当前用户部署..."
    bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh)
fi
