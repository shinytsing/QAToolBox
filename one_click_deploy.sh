#!/bin/bash

# QAToolBox 阿里云一键部署脚本
# 在阿里云服务器上直接执行此脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🚀 QAToolBox 阿里云一键部署脚本"
echo "=================================="
echo ""

# 1. 安装git（如果没有）
log_info "📦 检查并安装git..."
if ! command -v git &> /dev/null; then
    apt update
    apt install -y git
fi

# 2. 克隆或更新代码
log_info "📥 下载/更新QAToolBox代码..."
if [ -d "/var/www/qatoolbox" ]; then
    log_info "项目目录已存在，更新代码..."
    cd /var/www/qatoolbox
    git pull origin main
else
    log_info "首次部署，克隆代码..."
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/shinytsing/QAToolbox.git qatoolbox
    cd qatoolbox
fi

# 3. 给部署脚本执行权限
log_info "🔧 设置脚本权限..."
chmod +x deploy_aliyun_ubuntu.sh
chmod +x quick_deploy.sh
chmod +x deploy_to_aliyun.sh
chmod +x switch_env.sh
chmod +x start_*.py

# 4. 执行部署
log_info "🚀 开始执行部署..."
./deploy_aliyun_ubuntu.sh

log_success "✅ 部署完成！"
echo ""
echo "🌐 访问地址:"
echo "  - 本地: http://localhost"
echo "  - 外网: http://47.103.143.152"
echo "  - 域名: http://shenyiqing.xin (需要配置DNS)"
echo ""
echo "👤 管理员账户: admin / admin123456"
echo ""
echo "🔧 管理命令:"
echo "  cd /var/www/qatoolbox"
echo "  ./manage_qatoolbox.sh status"
echo "  ./manage_qatoolbox.sh logs"
echo ""
echo "📊 服务状态:"
cd /var/www/qatoolbox
./manage_qatoolbox.sh status