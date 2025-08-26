#!/bin/bash

# 提交部署方案到GitHub

echo "🚀 准备提交QAToolBox中国一键部署方案到GitHub..."

# 添加所有部署相关文件
git add \
    deploy_china.sh \
    docker-compose.china.yml \
    Dockerfile.china \
    install.sh \
    quick_deploy.sh \
    backup.sh \
    monitor.sh \
    docker-health-check.sh \
    Makefile.china \
    env.template.china \
    DEPLOY_CHINA_README.md \
    QUICK_START_CHINA.md \
    DEPLOYMENT_COMPLETE.md \
    .github/workflows/deploy.yml

echo "📝 提交文件..."
git commit -m "🚀 添加中国一键部署方案

✨ 新增功能:
- 适配中国网络环境的Docker部署
- 使用阿里云镜像源优化下载速度
- 一键安装脚本 (install.sh)
- 完整部署脚本 (deploy_china.sh)
- Docker编排配置 (docker-compose.china.yml)
- 运维管理工具 (Makefile.china)
- 数据备份和监控脚本
- GitHub Actions自动部署
- 详细部署文档

🎯 部署特点:
- 权限安全处理
- 依赖完整安装
- 无脑简单操作
- 中国网络优化

📋 使用方法:
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/install.sh | bash"

echo "📤 推送到GitHub..."
git push origin main

echo "✅ 提交完成！"
echo ""
echo "🌐 现在你可以在阿里云Ubuntu服务器上运行以下命令一键部署:"
echo "curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/install.sh | bash"
echo ""
echo "📚 查看详细文档:"
echo "- QUICK_START_CHINA.md - 快速开始"
echo "- DEPLOY_CHINA_README.md - 详细指南"
echo "- DEPLOYMENT_COMPLETE.md - 完整说明"
