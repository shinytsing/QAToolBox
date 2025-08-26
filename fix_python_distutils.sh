#!/bin/bash

# 修复python3-distutils包依赖问题
# 适配Ubuntu不同版本的包名变化

set -e

print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_status "🔧 修复Python distutils包依赖问题"

# 检测Ubuntu版本
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS_VERSION="$VERSION_ID"
    print_status "📋 检测到系统: $NAME $VERSION"
fi

print_status "🐍 安装Python生态系统（修复版）..."

# 基础Python包
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

# 根据不同Ubuntu版本处理distutils
if [[ "$OS_VERSION" == "22.04" ]] || [[ "$OS_VERSION" == "24.04" ]]; then
    print_status "🔧 Ubuntu $OS_VERSION - 使用新的包名..."
    # 新版本Ubuntu中distutils包含在python3-setuptools中
    apt install -y python3-setuptools-whl || print_warning "python3-setuptools-whl 安装失败，继续..."
    
    # 如果仍然需要distutils，尝试手动安装
    if ! python3 -c "import distutils" 2>/dev/null; then
        print_status "📦 手动安装distutils..."
        python3 -m pip install setuptools --break-system-packages || print_warning "pip安装setuptools失败"
    fi
else
    print_status "🔧 Ubuntu $OS_VERSION - 使用传统包名..."
    apt install -y python3-distutils || {
        print_warning "python3-distutils安装失败，尝试替代方案..."
        apt install -y python3-setuptools python3-pkg-resources
    }
fi

print_success "Python依赖修复完成"

# 验证Python环境
print_status "🔍 验证Python环境..."
python3 --version
python3 -m pip --version

if python3 -c "import distutils" 2>/dev/null; then
    print_success "distutils模块可用"
else
    print_warning "distutils模块不可用，但setuptools应该能替代"
fi

print_status "🚀 继续企业级部署..."

# 继续执行企业级部署脚本
curl -fsSL https://raw.githubusercontent.com/shinytsing/QAToolbox/main/enterprise_full_deploy.sh | bash

print_success "修复完成，部署继续执行"
