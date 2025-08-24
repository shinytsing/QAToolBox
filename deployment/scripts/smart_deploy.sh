#!/bin/bash

# QAToolBox 智能自动修复部署脚本
# 支持自动检测和修复各种系统问题
# 适用于: CentOS 7/8/9, Ubuntu 18.04+, Debian 10+, Rocky Linux, AlmaLinux

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置变量
PROJECT_NAME="QAToolBox"
DOMAIN="shenyiqing.xin"
SERVER_IP="47.103.143.152"
GIT_REPO="https://github.com/shinytsing/QAToolbox.git"
INSTALL_DIR="/opt/QAToolbox"
MIN_MEMORY_GB=2
MIN_DISK_GB=10
REQUIRED_PYTHON_VERSION="3.8"

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }
log_success() { echo -e "${CYAN}[SUCCESS]${NC} $1"; }
log_fix() { echo -e "${PURPLE}[AUTO-FIX]${NC} $1"; }

# 错误处理
handle_error() {
    local exit_code=$?
    local line_number=$1
    log_error "部署失败 (行 $line_number, 退出码 $exit_code)"
    log_info "正在尝试自动修复..."
    auto_fix_common_issues
    exit $exit_code
}

trap 'handle_error $LINENO' ERR

# 系统信息检测
detect_system() {
    log_step "检测系统信息..."
    
    # 检测操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VER=$VERSION_ID
        CODENAME=${VERSION_CODENAME:-}
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
        VER=$(lsb_release -sr)
        CODENAME=$(lsb_release -sc)
    else
        log_error "无法检测操作系统"
        auto_install_lsb_release
        detect_system
        return
    fi
    
    # 标准化OS名称
    case $OS in
        centos|rhel|rocky|almalinux|fedora)
            PKG_MANAGER="yum"
            if command -v dnf >/dev/null 2>&1; then
                PKG_MANAGER="dnf"
            fi
            OS_FAMILY="redhat"
            ;;
        ubuntu|debian|linuxmint)
            PKG_MANAGER="apt"
            OS_FAMILY="debian"
            ;;
        *)
            log_warn "未知操作系统: $OS，尝试自动适配..."
            auto_detect_package_manager
            ;;
    esac
    
    log_info "系统: $OS $VER ($OS_FAMILY)"
    log_info "包管理器: $PKG_MANAGER"
    
    # 检测架构
    ARCH=$(uname -m)
    case $ARCH in
        x86_64|amd64)
            ARCH="amd64"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        *)
            log_warn "未测试的架构: $ARCH"
            ;;
    esac
    log_info "架构: $ARCH"
}

# 自动检测包管理器
auto_detect_package_manager() {
    log_fix "自动检测包管理器..."
    
    if command -v dnf >/dev/null 2>&1; then
        PKG_MANAGER="dnf"
        OS_FAMILY="redhat"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
        OS_FAMILY="redhat"
    elif command -v apt >/dev/null 2>&1; then
        PKG_MANAGER="apt"
        OS_FAMILY="debian"
    elif command -v zypper >/dev/null 2>&1; then
        PKG_MANAGER="zypper"
        OS_FAMILY="suse"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_MANAGER="pacman"
        OS_FAMILY="arch"
    else
        log_error "无法检测包管理器，请手动安装"
        exit 1
    fi
    
    log_success "检测到包管理器: $PKG_MANAGER"
}

# 自动安装lsb-release
auto_install_lsb_release() {
    log_fix "安装系统信息检测工具..."
    
    if command -v yum >/dev/null 2>&1; then
        yum install -y redhat-lsb-core
    elif command -v dnf >/dev/null 2>&1; then
        dnf install -y redhat-lsb-core
    elif command -v apt >/dev/null 2>&1; then
        apt update && apt install -y lsb-release
    fi
}

# 系统要求检查
check_system_requirements() {
    log_step "检查系统要求..."
    
    # 检查内存
    MEMORY_GB=$(free -g | awk 'NR==2{print $2}')
    if [ "$MEMORY_GB" -lt "$MIN_MEMORY_GB" ]; then
        log_warn "内存不足: ${MEMORY_GB}GB < ${MIN_MEMORY_GB}GB"
        log_fix "尝试优化内存使用..."
        optimize_memory_usage
    else
        log_success "内存充足: ${MEMORY_GB}GB"
    fi
    
    # 检查磁盘空间
    DISK_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_GB" -lt "$MIN_DISK_GB" ]; then
        log_warn "磁盘空间不足: ${DISK_GB}GB < ${MIN_DISK_GB}GB"
        log_fix "清理磁盘空间..."
        cleanup_disk_space
    else
        log_success "磁盘空间充足: ${DISK_GB}GB"
    fi
    
    # 检查网络连接
    if ! ping -c 1 google.com >/dev/null 2>&1; then
        log_warn "网络连接异常"
        log_fix "尝试修复网络配置..."
        fix_network_issues
    else
        log_success "网络连接正常"
    fi
}

# 内存优化
optimize_memory_usage() {
    # 清理缓存
    sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
    
    # 调整swap
    if [ ! -f /swapfile ]; then
        log_fix "创建swap文件..."
        fallocate -l 2G /swapfile 2>/dev/null || dd if=/dev/zero of=/swapfile bs=1024 count=2097152
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
        log_success "Swap文件创建完成"
    fi
}

# 磁盘空间清理
cleanup_disk_space() {
    log_fix "清理系统垃圾文件..."
    
    # 清理包管理器缓存
    case $PKG_MANAGER in
        yum|dnf)
            $PKG_MANAGER clean all
            ;;
        apt)
            apt clean && apt autoclean
            ;;
    esac
    
    # 清理临时文件
    find /tmp -type f -atime +7 -delete 2>/dev/null || true
    find /var/tmp -type f -atime +7 -delete 2>/dev/null || true
    
    # 清理日志文件
    journalctl --vacuum-time=3d 2>/dev/null || true
    find /var/log -name "*.log" -type f -size +100M -delete 2>/dev/null || true
    
    log_success "磁盘清理完成"
}

# 网络问题修复
fix_network_issues() {
    # 重启网络服务
    systemctl restart NetworkManager 2>/dev/null || true
    systemctl restart networking 2>/dev/null || true
    
    # 刷新DNS
    systemctl restart systemd-resolved 2>/dev/null || true
    
    # 添加备用DNS
    echo "nameserver 8.8.8.8" >> /etc/resolv.conf
    echo "nameserver 114.114.114.114" >> /etc/resolv.conf
}

# 自动修复CentOS源问题
fix_centos_repos() {
    if [[ "$OS" == "centos" ]]; then
        log_step "检查CentOS源配置..."
        
        if [[ "$VER" == "8" ]]; then
            log_fix "修复CentOS 8源配置..."
            
            # 备份原始源
            mkdir -p /etc/yum.repos.d.backup
            cp /etc/yum.repos.d/*.repo /etc/yum.repos.d.backup/ 2>/dev/null || true
            
            # 替换为vault源
            sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
            sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' /etc/yum.repos.d/CentOS-* 2>/dev/null || true
            
            # 如果vault源也不可用，使用阿里云镜像
            if ! $PKG_MANAGER makecache 2>/dev/null; then
                log_fix "使用阿里云镜像源..."
                cat > /etc/yum.repos.d/CentOS-Base.repo << 'EOF'
[base]
name=CentOS-8 - Base - mirrors.aliyun.com
baseurl=http://mirrors.aliyun.com/centos-vault/8.5.2111/BaseOS/$basearch/os/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[appstream]
name=CentOS-8 - AppStream - mirrors.aliyun.com
baseurl=http://mirrors.aliyun.com/centos-vault/8.5.2111/AppStream/$basearch/os/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official

[extras]
name=CentOS-8 - Extras - mirrors.aliyun.com
baseurl=http://mirrors.aliyun.com/centos-vault/8.5.2111/extras/$basearch/os/
gpgcheck=1
gpgkey=http://mirrors.aliyun.com/centos/RPM-GPG-KEY-CentOS-Official
EOF
            fi
            
            log_success "CentOS 8源配置修复完成"
        fi
    fi
}

# 智能包安装
smart_install_package() {
    local package=$1
    local alternatives=("${@:2}")
    
    log_info "安装软件包: $package"
    
    case $PKG_MANAGER in
        yum|dnf)
            if ! $PKG_MANAGER install -y $package 2>/dev/null; then
                for alt in "${alternatives[@]}"; do
                    log_fix "尝试替代包: $alt"
                    if $PKG_MANAGER install -y $alt 2>/dev/null; then
                        log_success "成功安装: $alt"
                        return 0
                    fi
                done
                return 1
            fi
            ;;
        apt)
            if ! apt install -y $package 2>/dev/null; then
                for alt in "${alternatives[@]}"; do
                    log_fix "尝试替代包: $alt"
                    if apt install -y $alt 2>/dev/null; then
                        log_success "成功安装: $alt"
                        return 0
                    fi
                done
                return 1
            fi
            ;;
    esac
    
    log_success "成功安装: $package"
    return 0
}

# 智能更新系统
smart_update_system() {
    log_step "智能更新系统..."
    
    # 修复源配置
    fix_centos_repos
    
    case $PKG_MANAGER in
        yum|dnf)
            # 清理缓存
            $PKG_MANAGER clean all
            
            # 尝试更新
            if ! $PKG_MANAGER update -y; then
                log_fix "更新失败，尝试修复..."
                
                # 修复GPG密钥问题
                rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-* 2>/dev/null || true
                
                # 跳过有问题的包
                $PKG_MANAGER update -y --skip-broken || true
            fi
            ;;
        apt)
            # 修复dpkg问题
            dpkg --configure -a 2>/dev/null || true
            
            # 更新包列表
            if ! apt update; then
                log_fix "更新失败，尝试修复源..."
                
                # 修复sources.list
                cp /etc/apt/sources.list /etc/apt/sources.list.backup
                
                # 使用阿里云镜像
                if [[ "$OS" == "ubuntu" ]]; then
                    cat > /etc/apt/sources.list << EOF
deb http://mirrors.aliyun.com/ubuntu/ $CODENAME main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $CODENAME-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $CODENAME-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ $CODENAME-backports main restricted universe multiverse
EOF
                elif [[ "$OS" == "debian" ]]; then
                    cat > /etc/apt/sources.list << EOF
deb http://mirrors.aliyun.com/debian/ $CODENAME main contrib non-free
deb http://mirrors.aliyun.com/debian-security/ $CODENAME-security main contrib non-free
deb http://mirrors.aliyun.com/debian/ $CODENAME-updates main contrib non-free
EOF
                fi
                
                apt update
            fi
            
            # 升级系统
            apt upgrade -y || apt --fix-broken install -y
            ;;
    esac
    
    log_success "系统更新完成"
}

# 智能安装基础软件
smart_install_basics() {
    log_step "智能安装基础软件..."
    
    local basic_packages=()
    local dev_packages=()
    
    case $OS_FAMILY in
        redhat)
            basic_packages=(curl wget git unzip vim htop net-tools)
            dev_packages=(gcc gcc-c++ make openssl-devel libffi-devel python3-devel)
            ;;
        debian)
            basic_packages=(curl wget git unzip vim htop net-tools)
            dev_packages=(build-essential libssl-dev libffi-dev python3-dev)
            ;;
    esac
    
    # 安装基础包
    for package in "${basic_packages[@]}"; do
        smart_install_package $package || log_warn "跳过安装: $package"
    done
    
    # 安装开发包
    for package in "${dev_packages[@]}"; do
        smart_install_package $package || log_warn "跳过安装: $package"
    done
    
    log_success "基础软件安装完成"
}

# 智能安装Python
smart_install_python() {
    log_step "检查Python版本..."
    
    # 检查当前Python版本
    if command -v python3 >/dev/null 2>&1; then
        CURRENT_PYTHON=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        log_info "当前Python版本: $CURRENT_PYTHON"
        
        # 版本比较
        if [ "$(printf '%s\n' "$REQUIRED_PYTHON_VERSION" "$CURRENT_PYTHON" | sort -V | head -n1)" = "$REQUIRED_PYTHON_VERSION" ]; then
            log_success "Python版本满足要求"
            return 0
        fi
    fi
    
    log_fix "安装Python $REQUIRED_PYTHON_VERSION+"
    
    case $OS_FAMILY in
        redhat)
            if [[ "$VER" == "7" ]]; then
                # CentOS 7需要从SCL安装Python 3.8+
                smart_install_package centos-release-scl
                smart_install_package rh-python38 python38
                
                # 创建软链接
                ln -sf /opt/rh/rh-python38/root/usr/bin/python3.8 /usr/local/bin/python3
                ln -sf /opt/rh/rh-python38/root/usr/bin/pip3.8 /usr/local/bin/pip3
            else
                smart_install_package python3 python3-pip
            fi
            ;;
        debian)
            # Ubuntu/Debian
            if [[ "$OS" == "ubuntu" && "$VER" < "20.04" ]] || [[ "$OS" == "debian" && "$VER" < "11" ]]; then
                # 旧版本需要添加deadsnakes PPA
                smart_install_package software-properties-common
                add-apt-repository ppa:deadsnakes/ppa -y 2>/dev/null || true
                apt update
                smart_install_package python3.8 python3.8-dev python3.8-venv
                
                # 更新alternatives
                update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
            else
                smart_install_package python3 python3-pip python3-venv
            fi
            ;;
    esac
    
    # 验证安装
    if command -v python3 >/dev/null 2>&1; then
        INSTALLED_PYTHON=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        log_success "Python安装完成: $INSTALLED_PYTHON"
    else
        log_error "Python安装失败"
        return 1
    fi
}

# 智能安装Docker
smart_install_docker() {
    log_step "智能安装Docker..."
    
    if command -v docker >/dev/null 2>&1; then
        log_success "Docker已安装"
        return 0
    fi
    
    # 卸载旧版本
    case $OS_FAMILY in
        redhat)
            $PKG_MANAGER remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine podman runc 2>/dev/null || true
            ;;
        debian)
            apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
            ;;
    esac
    
    # 安装Docker
    case $OS_FAMILY in
        redhat)
            # 安装依赖
            smart_install_package yum-utils device-mapper-persistent-data lvm2
            
            # 添加Docker仓库
            if ! yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo; then
                log_fix "使用阿里云Docker镜像..."
                yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
            fi
            
            # 安装Docker
            smart_install_package docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
        debian)
            # 安装依赖
            smart_install_package apt-transport-https ca-certificates gnupg lsb-release
            
            # 添加Docker GPG密钥
            if ! curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg; then
                log_fix "使用阿里云Docker镜像..."
                curl -fsSL http://mirrors.aliyun.com/docker-ce/linux/$OS/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=$ARCH signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] http://mirrors.aliyun.com/docker-ce/linux/$OS $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
            else
                echo "deb [arch=$ARCH signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
            fi
            
            apt update
            smart_install_package docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            ;;
    esac
    
    # 启动Docker
    systemctl start docker
    systemctl enable docker
    
    # 配置Docker镜像加速
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}
EOF
    
    systemctl restart docker
    
    # 添加用户到docker组
    if ! id "qatoolbox" &>/dev/null; then
        useradd -m -s /bin/bash qatoolbox
        echo "qatoolbox:qatoolbox123" | chpasswd
    fi
    usermod -aG docker qatoolbox
    
    # 验证安装
    if docker --version >/dev/null 2>&1; then
        log_success "Docker安装完成: $(docker --version)"
    else
        log_error "Docker安装失败"
        return 1
    fi
}

# 智能安装Docker Compose
smart_install_docker_compose() {
    log_step "智能安装Docker Compose..."
    
    if command -v docker-compose >/dev/null 2>&1; then
        log_success "Docker Compose已安装"
        return 0
    fi
    
    # 尝试多种安装方法
    local compose_version="v2.21.0"
    local install_methods=(
        "github_release"
        "pip_install"
        "package_manager"
    )
    
    for method in "${install_methods[@]}"; do
        log_fix "尝试安装方法: $method"
        
        case $method in
            github_release)
                if curl -L "https://github.com/docker/compose/releases/download/$compose_version/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose 2>/dev/null; then
                    chmod +x /usr/local/bin/docker-compose
                    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
                    break
                fi
                ;;
            pip_install)
                if command -v pip3 >/dev/null 2>&1; then
                    pip3 install docker-compose
                    break
                fi
                ;;
            package_manager)
                smart_install_package docker-compose && break
                ;;
        esac
    done
    
    # 验证安装
    if command -v docker-compose >/dev/null 2>&1; then
        log_success "Docker Compose安装完成: $(docker-compose --version)"
    else
        log_error "Docker Compose安装失败"
        return 1
    fi
}

# 智能配置防火墙
smart_configure_firewall() {
    log_step "智能配置防火墙..."
    
    local ports=(22 80 443 8000)
    
    # 检测防火墙类型
    if command -v firewall-cmd >/dev/null 2>&1; then
        # firewalld
        systemctl start firewalld 2>/dev/null || true
        systemctl enable firewalld 2>/dev/null || true
        
        for port in "${ports[@]}"; do
            firewall-cmd --permanent --add-port=$port/tcp 2>/dev/null || true
        done
        firewall-cmd --reload 2>/dev/null || true
        
        log_success "防火墙配置完成 (firewalld)"
        
    elif command -v ufw >/dev/null 2>&1; then
        # ufw
        ufw --force enable
        for port in "${ports[@]}"; do
            ufw allow $port/tcp
        done
        
        log_success "防火墙配置完成 (ufw)"
        
    elif command -v iptables >/dev/null 2>&1; then
        # iptables
        for port in "${ports[@]}"; do
            iptables -A INPUT -p tcp --dport $port -j ACCEPT 2>/dev/null || true
        done
        
        # 保存规则
        if command -v iptables-save >/dev/null 2>&1; then
            iptables-save > /etc/iptables/rules.v4 2>/dev/null || true
        fi
        
        log_success "防火墙配置完成 (iptables)"
    else
        log_warn "未检测到防火墙，跳过配置"
    fi
}

# 智能克隆项目
smart_clone_project() {
    log_step "智能获取项目代码..."
    
    mkdir -p $INSTALL_DIR
    chown -R qatoolbox:qatoolbox $INSTALL_DIR 2>/dev/null || true
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "项目目录已存在，正在更新..."
        cd $INSTALL_DIR
        
        # 尝试多种更新方法
        if ! sudo -u qatoolbox git pull origin main 2>/dev/null; then
            log_fix "Git pull失败，尝试重置..."
            sudo -u qatoolbox git reset --hard HEAD
            sudo -u qatoolbox git clean -fd
            sudo -u qatoolbox git pull origin main
        fi
    else
        # 尝试多种克隆方法
        local clone_urls=(
            "$GIT_REPO"
            "https://gitee.com/shinytsing/QAToolbox.git"
            "https://github.com/shinytsing/QAToolbox.git"
        )
        
        for url in "${clone_urls[@]}"; do
            log_fix "尝试从 $url 克隆..."
            if sudo -u qatoolbox git clone $url $INSTALL_DIR 2>/dev/null; then
                log_success "项目克隆成功"
                break
            fi
        done
        
        if [ ! -d "$INSTALL_DIR/.git" ]; then
            log_error "项目克隆失败"
            return 1
        fi
    fi
    
    cd $INSTALL_DIR
    chown -R qatoolbox:qatoolbox $INSTALL_DIR
    
    log_success "项目代码获取完成"
}

# 生成完整环境配置
generate_smart_env() {
    log_step "生成智能环境配置..."
    
    # 生成随机密钥
    DJANGO_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || openssl rand -base64 50)
    DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    cat > $INSTALL_DIR/.env << EOF
# Django配置
DJANGO_SECRET_KEY=${DJANGO_SECRET}
DJANGO_DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
ALLOWED_HOSTS=${DOMAIN},www.${DOMAIN},${SERVER_IP},localhost

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=${DB_PASS}
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://\${DB_USER}:\${DB_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME}

# Redis配置
REDIS_URL=redis://redis:6379/0

# AI API配置（已预配置可用的密钥）
DEEPSEEK_API_KEY=sk-c4a84c8bbff341cbb3006ecaf84030fe
OPENAI_API_KEY=
CLAUDE_API_KEY=
GEMINI_API_KEY=

# 搜索和地图API配置（已预配置可用的密钥）
GOOGLE_API_KEY=
GOOGLE_CSE_ID=
AMAP_API_KEY=a825cd9231f473717912d3203a62c53e

# 天气API配置
OPENWEATHER_API_KEY=

# 图片API配置
PEXELS_API_KEY=
PIXABAY_API_KEY=
UNSPLASH_ACCESS_KEY=

# 社交媒体API配置
XIAOHONGSHU_API_KEY=
DOUYIN_API_KEY=
NETEASE_API_KEY=
WEIBO_API_KEY=
BILIBILI_API_KEY=
ZHIHU_API_KEY=

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@${DOMAIN}

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@${DOMAIN}
ADMIN_PASSWORD=admin123456

# 文件上传配置
DATA_UPLOAD_MAX_MEMORY_SIZE=104857600
FILE_UPLOAD_MAX_MEMORY_SIZE=104857600
MAX_UPLOAD_SIZE=104857600

# 缓存配置
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://redis:6379/1

# 会话配置
SESSION_ENGINE=django.contrib.sessions.backends.cache
SESSION_CACHE_ALIAS=default
SESSION_COOKIE_AGE=1209600

# Celery配置
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=False
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=Asia/Shanghai

# API限制配置
API_RATE_LIMIT_ANON=1000
API_RATE_LIMIT_USER=10000
API_RATE_LIMIT=10/minute

# 安全配置
SECURE_SSL_REDIRECT=False
SECURE_PROXY_SSL_HEADER=
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# 静态文件配置
STATIC_URL=/static/
MEDIA_URL=/media/
STATIC_ROOT=/app/staticfiles
MEDIA_ROOT=/app/media

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/django.log

# CORS配置
CORS_ALLOWED_ORIGINS=http://${DOMAIN},https://${DOMAIN},http://www.${DOMAIN},https://www.${DOMAIN},http://${SERVER_IP}
CORS_ALLOW_CREDENTIALS=True

# 开发工具配置（生产环境关闭）
DEBUG_TOOLBAR=False
INTERNAL_IPS=127.0.0.1,localhost
EOF

    chown qatoolbox:qatoolbox $INSTALL_DIR/.env
    log_success "环境配置生成完成"
    log_info "数据库密码: ${DB_PASS}"
}

# 智能部署服务
smart_deploy_services() {
    log_step "智能部署服务..."
    cd $INSTALL_DIR
    
    # 创建日志目录
    mkdir -p logs
    chown -R qatoolbox:qatoolbox logs
    
    # 检查Docker Compose文件
    local compose_file="deployment/configs/docker-compose.yml"
    if [ ! -f "$compose_file" ]; then
        log_warn "Docker Compose文件不存在，使用备用配置"
        compose_file="docker-compose.simple.yml"
        
        if [ ! -f "$compose_file" ]; then
            log_fix "创建基础Docker Compose配置..."
            create_basic_compose_file
            compose_file="docker-compose.basic.yml"
        fi
    fi
    
    # 构建镜像（重试机制）
    local max_retries=3
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        log_info "构建镜像 (尝试 $((retry+1))/$max_retries)..."
        
        if docker-compose -f $compose_file build --parallel; then
            log_success "镜像构建完成"
            break
        else
            retry=$((retry+1))
            if [ $retry -lt $max_retries ]; then
                log_fix "构建失败，清理后重试..."
                docker system prune -f
                sleep 10
            else
                log_error "镜像构建失败"
                return 1
            fi
        fi
    done
    
    # 启动服务
    log_info "启动服务..."
    docker-compose -f $compose_file up -d
    
    log_success "服务部署完成"
}

# 创建基础Docker Compose文件
create_basic_compose_file() {
    cat > docker-compose.basic.yml << 'EOF'
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: qatoolbox_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    container_name: qatoolbox_redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  web:
    build: .
    container_name: qatoolbox_web
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./logs:/app/logs
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
EOF
}

# 智能健康检查
smart_health_check() {
    log_step "智能健康检查..."
    
    local max_wait=300  # 最大等待时间5分钟
    local wait_time=0
    local check_interval=10
    
    while [ $wait_time -lt $max_wait ]; do
        log_info "健康检查 ($wait_time/$max_wait 秒)..."
        
        # 检查Docker容器
        local running_containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -c "Up" || echo "0")
        if [ "$running_containers" -gt 0 ]; then
            log_info "发现 $running_containers 个运行中的容器"
            
            # 检查Web服务
            if curl -f http://localhost:8000/tools/health/ >/dev/null 2>&1; then
                log_success "✅ Web服务健康检查通过"
                return 0
            elif curl -f http://localhost:8000/ >/dev/null 2>&1; then
                log_success "✅ Web服务可访问"
                return 0
            fi
        fi
        
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
    done
    
    log_warn "健康检查超时，但服务可能仍在启动中"
    
    # 显示服务状态用于调试
    log_info "当前服务状态:"
    docker-compose -f deployment/configs/docker-compose.yml ps 2>/dev/null || docker ps
    
    return 1
}

# 自动修复常见问题
auto_fix_common_issues() {
    log_fix "自动修复常见问题..."
    
    # 修复权限问题
    chown -R qatoolbox:qatoolbox $INSTALL_DIR 2>/dev/null || true
    
    # 修复Docker权限
    usermod -aG docker qatoolbox 2>/dev/null || true
    
    # 重启Docker服务
    systemctl restart docker 2>/dev/null || true
    
    # 清理Docker资源
    docker system prune -f 2>/dev/null || true
    
    # 修复SELinux问题
    if command -v setsebool >/dev/null 2>&1; then
        setsebool -P httpd_can_network_connect 1 2>/dev/null || true
    fi
    
    log_success "常见问题修复完成"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    log_success "=== 🎉 QAToolBox 智能部署完成！ ==="
    echo ""
    log_info "📍 访问地址："
    log_info "   - HTTP: http://${SERVER_IP}"
    log_info "   - HTTP: http://${DOMAIN}"
    log_info "   - 管理后台: http://${DOMAIN}/admin/"
    echo ""
    log_info "👤 系统用户："
    log_info "   - 用户名: qatoolbox"
    log_info "   - 密码: qatoolbox123"
    echo ""
    log_info "👤 Django管理员："
    log_info "   - 用户名: admin"
    log_info "   - 密码: admin123456"
    echo ""
    log_info "🔐 预配置API："
    log_info "   - ✅ DeepSeek AI (智能问答)"
    log_info "   - ✅ 高德地图 (位置服务)"
    echo ""
    log_info "🛠️ 服务管理："
    log_info "   cd ${INSTALL_DIR}"
    log_info "   ./deployment/scripts/manage.sh {start|stop|restart|logs|status|update|backup|ssl}"
    echo ""
    log_info "📊 系统信息："
    log_info "   - 操作系统: $OS $VER"
    log_info "   - 架构: $ARCH"
    log_info "   - 内存: ${MEMORY_GB}GB"
    log_info "   - 磁盘: ${DISK_GB}GB"
    echo ""
    log_warn "⚠️ 重要提醒："
    log_warn "1. 请立即修改默认密码"
    log_warn "2. 配置SSL证书: ./deployment/scripts/manage.sh ssl"
    log_warn "3. 定期备份数据"
    log_warn "4. 监控服务状态"
    echo ""
    log_info "🆘 故障排除："
    log_info "   ./deployment/scripts/manage.sh logs    # 查看日志"
    log_info "   ./deployment/scripts/manage.sh health  # 健康检查"
    log_info "   ./deployment/scripts/manage.sh status  # 服务状态"
}

# 主函数
main() {
    echo ""
    log_info "🚀 开始 QAToolBox 智能自动修复部署..."
    log_info "🎯 目标服务器: ${SERVER_IP} (${DOMAIN})"
    log_info "📦 项目仓库: ${GIT_REPO}"
    echo ""
    
    # 检查root权限
    if [[ $EUID -ne 0 ]]; then
        log_error "请使用root用户运行此脚本"
        log_info "使用方法: sudo $0"
        exit 1
    fi
    
    # 执行智能部署流程
    detect_system
    check_system_requirements
    smart_update_system
    smart_install_basics
    smart_install_python
    smart_install_docker
    smart_install_docker_compose
    smart_configure_firewall
    smart_clone_project
    generate_smart_env
    smart_deploy_services
    
    if smart_health_check; then
        show_deployment_info
        log_success "🎉 智能部署成功完成！"
    else
        log_warn "⚠️ 部署完成但健康检查未通过，请手动检查服务状态"
        show_deployment_info
        exit 1
    fi
}

# 执行主函数
main "$@"
