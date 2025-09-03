#!/bin/bash

# 部署到阿里云服务器的命令脚本
# 服务器信息: 47.103.143.152, admin@172.24.33.31

set -e

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🚀 开始部署QAToolBox到阿里云服务器..."
echo "服务器: 47.103.143.152"
echo "用户: admin"
echo ""

# 1. 上传代码到服务器
log_info "📤 上传代码到服务器..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.venv' \
    ./ admin@47.103.143.152:/var/www/qatoolbox/

# 2. 在服务器上执行部署脚本
log_info "🔧 在服务器上执行部署..."
ssh admin@47.103.143.152 << 'EOF'
cd /var/www/qatoolbox
chmod +x deploy_aliyun_ubuntu.sh
./deploy_aliyun_ubuntu.sh
EOF

# 3. 检查部署状态
log_info "📊 检查部署状态..."
ssh admin@47.103.143.152 << 'EOF'
cd /var/www/qatoolbox
./manage_qatoolbox.sh status
EOF

log_success "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  - http://47.103.143.152"
echo "  - http://shenyiqing.xin (需要配置DNS)"
echo ""
echo "👤 管理员账户: admin / admin123456"
echo ""
echo "🔧 后续操作:"
echo "  1. 配置SSL证书"
echo "  2. 配置域名DNS解析"
echo "  3. 修改默认密码"
echo "  4. 配置邮件服务"
