#!/bin/bash
# QAToolBox 一键安装脚本 - 最简单版本
# 用法: curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/one_click_install.sh | bash

echo "🚀 QAToolBox 一键部署开始..."

# 下载并运行智能部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/smart_deploy.sh -o /tmp/smart_deploy.sh
chmod +x /tmp/smart_deploy.sh
/tmp/smart_deploy.sh

echo "✅ 部署完成！"
