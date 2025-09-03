#!/bin/bash

# 快速部署命令 - 复制到终端执行

echo "🚀 开始部署QAToolBox到阿里云服务器 47.103.143.152"
echo ""

# 1. 上传代码
echo "📤 步骤1: 上传代码到服务器..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
    ./ admin@47.103.143.152:/var/www/qatoolbox/

echo "✅ 代码上传完成"
echo ""

# 2. 执行部署
echo "🔧 步骤2: 在服务器上执行部署..."
ssh admin@47.103.143.152 << 'EOF'
cd /var/www/qatoolbox
chmod +x deploy_aliyun_ubuntu.sh
./deploy_aliyun_ubuntu.sh
EOF

echo "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  - http://47.103.143.152"
echo "  - http://shenyiqing.xin (需要配置DNS)"
echo ""
echo "👤 管理员账户: admin / admin123456"
echo ""
echo "🔧 管理命令:"
echo "  ssh admin@47.103.143.152"
echo "  cd /var/www/qatoolbox"
echo "  ./manage_qatoolbox.sh status"
