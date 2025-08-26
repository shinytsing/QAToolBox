#!/bin/bash

# QAToolBox 超简单一键安装脚本
# 适用于阿里云Ubuntu服务器，中国网络环境优化

echo "🚀 QAToolBox 一键安装开始..."

# 一行命令完成所有部署
bash <(curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_china.sh)

echo "✅ 安装完成！"