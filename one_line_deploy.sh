#!/bin/bash

# QAToolBox 一行命令部署脚本
# 使用方法: bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/one_line_deploy.sh)

echo "🚀 QAToolBox 一行命令部署开始..."
echo "📍 仓库地址: https://github.com/shinytsing/QAToolbox.git"

# 直接下载并执行完整部署脚本
bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh)

echo "✅ 一行命令部署完成！"
