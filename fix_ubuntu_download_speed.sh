#!/bin/bash

# Ubuntu部署下载速度优化脚本
# 用于在部署过程中途优化下载速度

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用sudo运行此脚本"
    exit 1
fi

PROJECT_USER="qatoolbox"
PROJECT_DIR="/opt/qatoolbox"

log_info "🚀 开始优化Ubuntu部署下载速度"

# 1. 配置系统APT使用阿里云镜像源
log_info "配置APT使用阿里云镜像源"
cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%Y%m%d_%H%M%S)

# 检测Ubuntu版本
UBUNTU_CODENAME=$(lsb_release -cs)
log_info "检测到Ubuntu版本: $UBUNTU_CODENAME"

# 配置阿里云镜像源
tee /etc/apt/sources.list > /dev/null << EOF
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-backports main restricted universe multiverse

## 源码仓库（可选）
# deb-src http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-security main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-updates main restricted universe multiverse
# deb-src http://mirrors.aliyun.com/ubuntu/ $UBUNTU_CODENAME-backports main restricted universe multiverse
EOF

log_success "APT镜像源配置完成"

# 2. 更新APT缓存
log_info "更新APT缓存"
apt update

# 3. 配置pip使用清华大学镜像源
if [ -d "$PROJECT_DIR" ] && id "$PROJECT_USER" &>/dev/null; then
    log_info "配置pip使用清华大学镜像源"
    
    # 创建pip配置目录
    sudo -u $PROJECT_USER mkdir -p /home/$PROJECT_USER/.pip
    
    # 配置pip镜像源
    sudo -u $PROJECT_USER tee /home/$PROJECT_USER/.pip/pip.conf > /dev/null << 'EOF'
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120
retries = 5

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
EOF
    
    log_success "pip镜像源配置完成"
    
    # 4. 如果虚拟环境存在，尝试重新安装依赖
    if [ -f "$PROJECT_DIR/.venv/bin/pip" ]; then
        log_info "使用新镜像源重新安装Python依赖"
        cd $PROJECT_DIR
        
        # 停止可能正在运行的pip进程
        pkill -f "pip install" || true
        sleep 2
        
        # 升级pip
        log_info "升级pip"
        sudo -u $PROJECT_USER $PROJECT_DIR/.venv/bin/pip install --upgrade pip \
            -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
        
        # 安装核心依赖
        log_info "安装核心依赖包"
        sudo -u $PROJECT_USER $PROJECT_DIR/.venv/bin/pip install \
            Django gunicorn psycopg2-binary redis wheel setuptools \
            -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
        
        # 安装完整依赖
        log_info "安装项目完整依赖"
        sudo -u $PROJECT_USER $PROJECT_DIR/.venv/bin/pip install -r requirements.txt \
            -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
        
        log_success "Python依赖重新安装完成"
    else
        log_warning "未找到虚拟环境，跳过Python依赖安装"
    fi
else
    log_warning "项目目录或用户不存在，跳过pip配置"
fi

# 5. 配置Git使用国内镜像
log_info "配置Git全局设置优化下载"
git config --global http.postBuffer 524288000
git config --global http.maxRequestBuffer 100M
git config --global core.compression 0

# 6. 显示网络测试
log_info "测试网络连接速度"
echo "测试GitHub连接:"
timeout 5 curl -I https://github.com 2>/dev/null && echo "✓ GitHub可达" || echo "✗ GitHub不可达"

echo "测试Gitee连接:"
timeout 5 curl -I https://gitee.com 2>/dev/null && echo "✓ Gitee可达" || echo "✗ Gitee不可达"

echo "测试清华PyPI镜像:"
timeout 5 curl -I https://pypi.tuna.tsinghua.edu.cn 2>/dev/null && echo "✓ 清华PyPI可达" || echo "✗ 清华PyPI不可达"

echo "测试阿里云APT镜像:"
timeout 5 curl -I http://mirrors.aliyun.com 2>/dev/null && echo "✓ 阿里云镜像可达" || echo "✗ 阿里云镜像不可达"

log_success "🎉 下载速度优化完成！"
log_info "💡 现在可以继续部署或重新运行部署脚本，下载速度应该会显著提升"

# 7. 提供后续操作建议
echo
echo "📋 后续操作建议:"
echo "1. 如果pip安装仍在进行，可以先按Ctrl+C中断"
echo "2. 然后重新运行部署脚本: bash deploy_ubuntu_production.sh"
echo "3. 或者手动进入项目目录继续安装依赖:"
echo "   cd $PROJECT_DIR"
echo "   sudo -u $PROJECT_USER .venv/bin/pip install -r requirements.txt \\"
echo "       -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn"
