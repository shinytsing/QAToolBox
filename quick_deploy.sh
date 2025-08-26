#!/bin/bash

# QAToolBox 快速部署脚本 - 超简单版本
# 一行命令完成所有部署工作

set -e

echo "🚀 QAToolBox 快速部署开始..."

# 检查是否安装了curl
if ! command -v curl &> /dev/null; then
    echo "安装curl..."
    sudo apt-get update && sudo apt-get install -y curl
fi

# 下载并执行完整部署脚本
echo "📥 下载部署脚本..."
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh -o deploy_china.sh

echo "🔧 开始部署..."
chmod +x deploy_china.sh
./deploy_china.sh

echo "✅ 部署完成！"
echo "🌐 访问地址: http://$(curl -s ifconfig.me || echo 'your-server-ip')"

