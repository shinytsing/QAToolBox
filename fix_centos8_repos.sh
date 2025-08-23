#!/bin/bash

# CentOS 8源修复脚本
# 由于CentOS 8已停止维护，需要切换到vault源

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "=== CentOS 8 源修复脚本 ==="

# 检查是否为CentOS 8
if [ ! -f /etc/centos-release ]; then
    print_error "此脚本仅适用于CentOS系统"
    exit 1
fi

CENTOS_VERSION=$(cat /etc/centos-release | grep -oE '[0-9]+' | head -1)
if [ "$CENTOS_VERSION" != "8" ]; then
    print_error "此脚本仅适用于CentOS 8系统，当前版本: $CENTOS_VERSION"
    exit 1
fi

print_warning "检测到CentOS 8系统，开始修复源配置..."

# 1. 备份原始源配置
print_info "备份原始源配置..."
sudo mkdir -p /etc/yum.repos.d.backup
sudo cp /etc/yum.repos.d/*.repo /etc/yum.repos.d.backup/ 2>/dev/null || true

# 2. 修复主要源
print_info "修复CentOS主要源..."
sudo sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-*
sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-*

# 3. 修复EPEL源
print_info "修复EPEL源..."
if [ -f /etc/yum.repos.d/CentOS-epel.repo ]; then
    sudo sed -i '/failovermethod/d' /etc/yum.repos.d/CentOS-epel.repo
fi

# 4. 创建新的CentOS-Base.repo
print_info "创建新的基础源配置..."
sudo tee /etc/yum.repos.d/CentOS-Base.repo > /dev/null << 'EOF'
[base]
name=CentOS-8 - Base - vault.centos.org
baseurl=http://vault.centos.org/8.5.2111/BaseOS/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

[appstream]
name=CentOS-8 - AppStream - vault.centos.org
baseurl=http://vault.centos.org/8.5.2111/AppStream/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

[extras]
name=CentOS-8 - Extras - vault.centos.org
baseurl=http://vault.centos.org/8.5.2111/extras/$basearch/os/
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

[powertools]
name=CentOS-8 - PowerTools - vault.centos.org
baseurl=http://vault.centos.org/8.5.2111/PowerTools/$basearch/os/
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

[centosplus]
name=CentOS-8 - Plus - vault.centos.org
baseurl=http://vault.centos.org/8.5.2111/centosplus/$basearch/os/
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial
EOF

# 5. 启用PowerTools仓库
print_info "启用PowerTools仓库..."
sudo dnf config-manager --set-enabled powertools 2>/dev/null || sudo dnf config-manager --set-enabled PowerTools 2>/dev/null || true

# 6. 清理缓存
print_info "清理包管理器缓存..."
sudo dnf clean all

# 7. 测试源配置
print_info "测试源配置..."
if sudo dnf makecache; then
    print_info "✅ 源配置修复成功！"
else
    print_error "❌ 源配置修复失败，请检查网络连接"
    exit 1
fi

# 8. 显示可用仓库
print_info "当前可用仓库："
sudo dnf repolist

echo ""
print_info "=== 修复完成 ==="
print_info "现在可以正常使用 dnf 命令安装软件包了"
print_info ""
print_info "常用命令："
print_info "- 更新系统: sudo dnf update -y"
print_info "- 安装软件: sudo dnf install -y package_name"
print_info "- 搜索软件: dnf search keyword"
print_info ""
print_warning "如需恢复原始配置，请运行："
print_warning "sudo cp /etc/yum.repos.d.backup/*.repo /etc/yum.repos.d/"
