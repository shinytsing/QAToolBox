#!/bin/bash
# =============================================================================
# QAToolBox 阿里云完整功能部署脚本 v3.0
# =============================================================================
# 保持所有功能和依赖，适用于已下载项目文件的情况
# 支持机器学习、数据处理、文档处理、OCR等完整功能
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# 配置变量
readonly SERVER_IP="${SERVER_IP:-47.103.143.152}"
readonly DOMAIN="${DOMAIN:-shenyiqing.xin}"
readonly PROJECT_USER="${PROJECT_USER:-qatoolbox}"
readonly PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"
readonly DB_PASSWORD="${DB_PASSWORD:-QAToolBox@2024@$(date +%s)}"
readonly ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123456}"

# 重试配置
readonly MAX_RETRIES=3
readonly RETRY_DELAY=5

# 日志文件
readonly LOG_FILE="/tmp/qatoolbox_complete_deploy_$(date +%Y%m%d_%H%M%S).log"

# 执行记录
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🚀 QAToolBox 完整功能部署 v3.0
========================================
✨ 特性:
  • 保持所有项目功能
  • 完整依赖安装 (ML/AI/数据处理)
  • 修复配置冲突
  • 生产级优化
  • 中国地区加速
========================================
EOF
echo -e "${NC}"

# 检查root权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}❌ 请使用root权限运行此脚本${NC}"
        echo -e "${YELLOW}💡 使用命令: sudo $0${NC}"
        exit 1
    fi
}

# 显示进度
show_progress() {
    local step=$1
    local total=$2
    local desc=$3
    local percent=$((step * 100 / total))
    echo -e "${CYAN}${BOLD}[${step}/${total}] (${percent}%) ${desc}${NC}"
}

# 重试机制
retry_command() {
    local command="$1"
    local description="$2"
    local max_attempts="${3:-$MAX_RETRIES}"
    local delay="${4:-$RETRY_DELAY}"
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -e "${YELLOW}🔄 尝试 ${attempt}/${max_attempts}: ${description}${NC}"
        
        if eval "$command"; then
            echo -e "${GREEN}✅ 成功: ${description}${NC}"
            return 0
        else
            if [ $attempt -eq $max_attempts ]; then
                echo -e "${RED}❌ 失败: ${description} (已达最大重试次数)${NC}"
                return 1
            fi
            echo -e "${YELLOW}⚠️ 失败，${delay}秒后重试...${NC}"
            sleep $delay
            ((attempt++))
        fi
    done
}

# 错误处理
handle_error() {
    local error_msg="$1"
    local suggestion="$2"
    echo -e "${RED}❌ 错误: ${error_msg}${NC}"
    echo -e "${YELLOW}💡 建议: ${suggestion}${NC}"
    echo -e "${BLUE}📋 详细日志: ${LOG_FILE}${NC}"
    exit 1
}

# 检测系统信息
detect_system() {
    echo -e "${BLUE}🔍 检测系统信息...${NC}"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        handle_error "无法检测操作系统" "请确保使用受支持的Linux发行版"
    fi
    
    echo -e "${GREEN}操作系统: $OS $VER${NC}"
    echo -e "${GREEN}架构: $(uname -m)${NC}"
    echo -e "${GREEN}内核: $(uname -r)${NC}"
    echo -e "${GREEN}内存: $(free -h | awk '/^Mem:/ {print $2}')${NC}"
    echo -e "${GREEN}磁盘: $(df -h / | awk 'NR==2 {print $4}') 可用${NC}"
}

# 配置中国镜像源
setup_china_mirrors() {
    show_progress "1" "15" "配置中国镜像源加速"
    
    echo -e "${YELLOW}🔧 配置apt镜像源...${NC}"
    
    # 备份原始sources.list
    cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s)
    
    # 检测Ubuntu版本并配置相应的阿里云镜像
    local ubuntu_codename=$(lsb_release -cs)
    
    cat > /etc/apt/sources.list << EOF
# 阿里云Ubuntu镜像源
deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename} main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-security main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-updates main restricted universe multiverse

deb http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ ${ubuntu_codename}-backports main restricted universe multiverse
EOF

    # 配置pip中国镜像源
    mkdir -p /etc/pip
    cat > /etc/pip/pip.conf << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
EOF

    echo -e "${GREEN}✅ 中国镜像源配置完成${NC}"
}

# 更新系统并修复依赖
update_system() {
    show_progress "2" "15" "更新系统并修复依赖冲突"
    
    echo -e "${YELLOW}📦 更新包列表...${NC}"
    retry_command "apt update" "更新包列表"
    
    echo -e "${YELLOW}🔧 修复破损的包...${NC}"
    apt --fix-broken install -y || true
    apt autoremove -y || true
    apt autoclean || true
    
    echo -e "${YELLOW}⬆️ 升级系统包...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt upgrade -y" "升级系统包"
    
    echo -e "${GREEN}✅ 系统更新完成${NC}"
}

# 安装完整系统依赖
install_complete_system_dependencies() {
    show_progress "3" "15" "安装完整系统依赖（包含ML/AI支持）"
    
    echo -e "${YELLOW}📦 安装基础开发工具...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        curl wget git unzip vim nano htop tree jq \
        software-properties-common apt-transport-https \
        ca-certificates gnupg lsb-release \
        build-essential gcc g++ make cmake pkg-config \
        autoconf automake libtool" "安装基础工具"
    
    echo -e "${YELLOW}🐍 安装完整Python开发环境...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        python3 python3-pip python3-venv python3-dev \
        python3-setuptools python3-wheel python3-distutils \
        python3-tk python3-dbg" "安装Python环境"
    
    echo -e "${YELLOW}🗄️ 安装数据库服务...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        postgresql postgresql-contrib postgresql-client \
        postgresql-server-dev-all \
        redis-server redis-tools" "安装数据库服务"
    
    echo -e "${YELLOW}🌐 安装Web服务器...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        nginx nginx-extras \
        supervisor" "安装Web服务器"
    
    echo -e "${YELLOW}🔒 安装安全和加密库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libssl-dev libffi-dev libcrypto++-dev \
        libsasl2-dev libldap2-dev" "安装安全库"
    
    echo -e "${YELLOW}🗃️ 安装数据库驱动和连接库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libpq-dev postgresql-client \
        libmysqlclient-dev default-libmysqlclient-dev \
        libsqlite3-dev" "安装数据库驱动"
    
    echo -e "${YELLOW}🖼️ 安装完整图像处理库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libjpeg-dev libjpeg8-dev libjpeg-turbo8-dev \
        libpng-dev libpng16-16 \
        libtiff-dev libtiff5-dev \
        libwebp-dev libwebp6 \
        libfreetype6-dev \
        liblcms2-dev \
        libopenjp2-7-dev \
        zlib1g-dev \
        libimagequant-dev \
        libraqm-dev \
        libxcb1-dev" "安装图像处理库"
    
    echo -e "${YELLOW}🎬 安装音视频处理库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        ffmpeg \
        libavcodec-dev libavformat-dev libswscale-dev \
        libavresample-dev libavutil-dev \
        libsndfile1-dev libsndfile1 \
        portaudio19-dev \
        libasound2-dev \
        libpulse-dev \
        libmp3lame-dev \
        libvorbis-dev \
        libtheora-dev" "安装音视频库"
    
    echo -e "${YELLOW}🔤 安装OCR和文本处理...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
        tesseract-ocr-eng tesseract-ocr-osd \
        libtesseract-dev \
        poppler-utils \
        antiword \
        unrtf \
        ghostscript" "安装OCR库"
    
    echo -e "${YELLOW}🖥️ 安装GUI和显示库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libgtk-3-dev libgtk-3-0 \
        libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
        libcanberra-gtk-module libcanberra-gtk3-module \
        libgl1-mesa-dri libgl1-mesa-glx \
        libglu1-mesa-dev \
        libsm6 libxext6 libxrender1 \
        libfontconfig1-dev \
        libcairo2-dev libgirepository1.0-dev" "安装GUI库"
    
    echo -e "${YELLOW}🧮 安装科学计算库...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libgomp1 libomp-dev \
        libatlas-base-dev liblapack-dev libblas-dev \
        libopenblas-dev \
        libhdf5-dev libhdf5-103 \
        libnetcdf-dev \
        libprotobuf-dev protobuf-compiler \
        libboost-all-dev" "安装科学计算库"
    
    echo -e "${YELLOW}📊 安装数据科学工具...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        r-base r-base-dev \
        octave \
        pandoc \
        texlive-latex-base \
        graphviz \
        libtiff-tools" "安装数据科学工具"
    
    echo -e "${YELLOW}🌐 安装浏览器和自动化工具...${NC}"
    # 安装Chrome
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - || true
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list || true
    apt update || true
    apt install -y google-chrome-stable || apt install -y chromium-browser || apt install -y chromium || echo "⚠️ 浏览器安装跳过"
    
    echo -e "${YELLOW}📁 安装文档处理工具...${NC}"
    retry_command "DEBIAN_FRONTEND=noninteractive apt install -y \
        libreoffice \
        pandoc \
        wkhtmltopdf \
        imagemagick \
        pdftk \
        qpdf" "安装文档处理工具"
    
    echo -e "${GREEN}✅ 完整系统依赖安装完成${NC}"
}

# 配置系统服务
setup_system_services() {
    show_progress "4" "15" "配置PostgreSQL、Redis、Nginx等服务"
    
    echo -e "${YELLOW}🚀 启动系统服务...${NC}"
    systemctl enable postgresql redis-server nginx supervisor
    systemctl start postgresql redis-server nginx supervisor
    
    echo -e "${YELLOW}🗄️ 配置PostgreSQL数据库...${NC}"
    
    sudo -u postgres psql -c "SELECT 1" > /dev/null 2>&1 || handle_error "PostgreSQL启动失败" "检查PostgreSQL服务状态"
    
    # 删除已存在的数据库和用户
    sudo -u postgres psql -c "DROP DATABASE IF EXISTS qatoolbox;" 2>/dev/null || true
    sudo -u postgres psql -c "DROP USER IF EXISTS qatoolbox;" 2>/dev/null || true
    
    # 创建新的数据库和用户
    sudo -u postgres psql -c "CREATE USER qatoolbox WITH PASSWORD '$DB_PASSWORD';"
    sudo -u postgres psql -c "ALTER USER qatoolbox CREATEDB;"
    sudo -u postgres psql -c "CREATE DATABASE qatoolbox OWNER qatoolbox;"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE qatoolbox TO qatoolbox;"
    
    # 配置PostgreSQL以支持UTF-8
    sudo -u postgres psql -c "ALTER DATABASE qatoolbox SET client_encoding TO 'utf8';"
    sudo -u postgres psql -c "ALTER DATABASE qatoolbox SET default_transaction_isolation TO 'read committed';"
    sudo -u postgres psql -c "ALTER DATABASE qatoolbox SET timezone TO 'Asia/Shanghai';"
    
    echo -e "${YELLOW}🔒 配置Redis...${NC}"
    # 配置Redis
    sed -i 's/^# maxmemory <bytes>/maxmemory 256mb/' /etc/redis/redis.conf || true
    sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf || true
    systemctl restart redis-server
    
    echo -e "${GREEN}✅ 系统服务配置完成${NC}"
}

# 创建项目用户和目录
setup_project_user() {
    show_progress "5" "15" "创建项目用户和目录结构"
    
    if ! id "$PROJECT_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$PROJECT_USER"
        usermod -aG sudo "$PROJECT_USER"
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 创建成功${NC}"
    else
        echo -e "${GREEN}✅ 用户 $PROJECT_USER 已存在${NC}"
    fi
    
    # 创建必要目录
    mkdir -p /var/www/qatoolbox/{static,media}
    mkdir -p /var/log/qatoolbox
    mkdir -p /tmp/qatoolbox
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/www/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/log/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /tmp/qatoolbox
    chmod -R 755 /var/www/qatoolbox
    chmod -R 755 /var/log/qatoolbox
    chmod -R 755 /tmp/qatoolbox
    
    # 为项目用户配置pip源
    sudo -u "$PROJECT_USER" mkdir -p "/home/$PROJECT_USER/.pip"
    sudo -u "$PROJECT_USER" cat > "/home/$PROJECT_USER/.pip/pip.conf" << 'EOF'
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com
timeout = 120
retries = 5
extra-index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
EOF

    echo -e "${GREEN}✅ 项目用户和目录配置完成${NC}"
}

# 验证项目代码
verify_project_code() {
    show_progress "6" "15" "验证项目代码完整性"
    
    if [ ! -d "$PROJECT_DIR" ]; then
        handle_error "项目目录不存在: $PROJECT_DIR" "请确保项目代码已正确放置"
    fi
    
    cd "$PROJECT_DIR"
    
    # 验证关键文件
    local required_files=(
        "manage.py"
        "wsgi.py" 
        "urls.py"
        "requirements.txt"
        "config/settings"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -e "$file" ]; then
            handle_error "缺少关键文件: $file" "请检查项目结构完整性"
        fi
    done
    
    # 验证Django应用
    local apps=("apps/users" "apps/tools" "apps/content")
    for app in "${apps[@]}"; do
        if [ -d "$app" ]; then
            echo -e "${GREEN}✅ 发现应用: $app${NC}"
        else
            echo -e "${YELLOW}⚠️ 应用不存在: $app${NC}"
        fi
    done
    
    # 设置目录权限
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    echo -e "${GREEN}✅ 项目代码验证完成${NC}"
}

# 创建完整Python环境并安装所有依赖
setup_complete_python_environment() {
    show_progress "7" "15" "创建完整Python环境并安装所有依赖"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🐍 创建Python虚拟环境...${NC}"
    if [ -d ".venv" ]; then
        rm -rf ".venv"
    fi
    
    sudo -u "$PROJECT_USER" python3 -m venv .venv
    
    # 升级pip工具
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install --upgrade pip setuptools wheel" "升级pip工具"
    
    echo -e "${YELLOW}📦 安装核心Django框架...${NC}"
    local core_django=(
        "Django==4.2.7"
        "djangorestframework==3.14.0"
        "django-cors-headers==4.3.1"
        "django-crispy-forms==2.0"
        "django-filter==23.3"
        "crispy-bootstrap5==0.7"
        "django-simple-captcha==0.6.0"
        "django-ratelimit==4.1.0"
        "django-ranged-response==0.2.0"
        "django-extensions==3.2.3"
    )
    
    for package in "${core_django[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装异步和实时通信...${NC}"
    local async_packages=(
        "channels==4.0.0"
        "channels-redis==4.1.0"
        "daphne==4.0.0"
        "asgiref==3.8.1"
    )
    
    for package in "${async_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装数据库和缓存...${NC}"
    local db_packages=(
        "psycopg2-binary==2.9.7"
        "redis==4.6.0"
        "django-redis==5.4.0"
        "django-cacheops==7.0.2"
        "django-db-connection-pool==1.2.4"
    )
    
    for package in "${db_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装任务队列...${NC}"
    local celery_packages=(
        "celery==5.3.4"
        "django-celery-beat==2.5.0"
        "kombu==5.3.4"
        "billiard==4.2.0"
        "vine==5.1.0"
        "amqp==5.2.0"
    )
    
    for package in "${celery_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装Web服务器和部署...${NC}"
    local web_packages=(
        "gunicorn==21.2.0"
        "whitenoise==6.6.0"
        "python-dotenv==1.0.0"
        "django-environ==0.11.2"
    )
    
    for package in "${web_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装HTTP和网络库...${NC}"
    local http_packages=(
        "requests==2.31.0"
        "urllib3==1.26.18"
        "beautifulsoup4==4.12.2"
        "lxml==4.9.3"
        "html5lib==1.1"
        "httpx"
        "aiohttp"
    )
    
    for package in "${http_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装图像处理库...${NC}"
    local image_packages=(
        "Pillow==9.5.0"
        "opencv-python==4.8.1.78"
        "scikit-image"
        "imageio"
        "matplotlib==3.7.5"
    )
    
    for package in "${image_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装数据处理和分析...${NC}"
    local data_packages=(
        "pandas==2.0.3"
        "numpy==1.24.4"
        "scipy==1.9.3"
        "scikit-learn==1.3.2"
        "pyecharts==2.0.4"
        "plotly"
        "seaborn"
    )
    
    for package in "${data_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装机器学习框架...${NC}"
    # PyTorch (CPU版本，适合生产环境)
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu" "安装PyTorch CPU版本" 2 5
    
    # TensorFlow
    retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install tensorflow-cpu" "安装TensorFlow" 2 5
    
    echo -e "${YELLOW}📦 安装文档处理库...${NC}"
    local doc_packages=(
        "python-docx==1.1.0"
        "python-pptx==0.6.22"
        "openpyxl==3.1.2"
        "xlrd==2.0.1"
        "xlwt==1.3.0"
        "reportlab==4.0.9"
        "pypdfium2==4.23.1"
        "pdfplumber==0.10.3"
        "pdfminer.six==20221105"
        "PyMuPDF==1.23.26"
        "pdf2docx==0.5.6"
        "docx2pdf==0.1.8"
        "xmind==1.2.0"
    )
    
    for package in "${doc_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装OCR和文本处理...${NC}"
    local ocr_packages=(
        "pytesseract==0.3.10"
        "easyocr"
        "paddlepaddle"
        "paddleocr"
    )
    
    for package in "${ocr_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 5
    done
    
    echo -e "${YELLOW}📦 安装音频处理库...${NC}"
    local audio_packages=(
        "pydub==0.25.1"
        "mutagen==1.47.0"
        "librosa==0.10.1"
        "soundfile==0.12.1"
        "audioread==3.0.1"
        "resampy==0.4.2"
        "speech-recognition"
        "pyaudio"
    )
    
    for package in "${audio_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装浏览器自动化...${NC}"
    local browser_packages=(
        "selenium==4.15.2"
        "webdriver-manager==4.0.1"
        "playwright"
        "pyppeteer"
    )
    
    for package in "${browser_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装加密和安全库...${NC}"
    local security_packages=(
        "cryptography==41.0.7"
        "pycryptodome"
        "bcrypt"
        "passlib"
        "python-jose"
    )
    
    for package in "${security_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装工具库...${NC}"
    local util_packages=(
        "tenacity==8.2.3"
        "prettytable==3.9.0"
        "qrcode==7.4.2"
        "python-dateutil==2.8.2"
        "pytz==2023.3"
        "simplejson==3.19.3"
        "six==1.17.0"
        "click==8.1.7"
        "tqdm"
        "rich"
        "typer"
    )
    
    for package in "${util_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装金融和数据获取...${NC}"
    local finance_packages=(
        "yfinance==0.2.28"
        "multitasking==0.0.11"
        "akshare"
        "tushare"
    )
    
    for package in "${finance_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装数据库ORM...${NC}"
    local orm_packages=(
        "peewee==3.17.9"
        "sqlalchemy"
        "pymongo"
    )
    
    for package in "${orm_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 安装监控和日志...${NC}"
    local monitoring_packages=(
        "sentry-sdk[django]==1.38.0"
        "structlog==23.2.0"
        "django-debug-toolbar==4.2.0"
        "django-csp==3.7"
        "gevent==23.9.1"
    )
    
    for package in "${monitoring_packages[@]}"; do
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install '$package'" "安装 $package" 2 3
    done
    
    echo -e "${YELLOW}📦 从requirements.txt安装剩余依赖...${NC}"
    if [ -f "requirements.txt" ]; then
        retry_command "sudo -u '$PROJECT_USER' .venv/bin/pip install -r requirements.txt" "安装requirements.txt中的依赖" 2 5
    fi
    
    echo -e "${GREEN}✅ 完整Python环境配置完成${NC}"
}

# 修复Django配置以支持完整功能
fix_django_configuration() {
    show_progress "8" "15" "修复Django配置以支持完整功能"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}⚙️ 修复阿里云生产配置...${NC}"
    
    # 备份现有配置
    if [ -f "config/settings/aliyun_production.py" ]; then
        cp config/settings/aliyun_production.py config/settings/aliyun_production.py.backup
    fi
    
    # 修复配置文件中的问题
    cat > config/settings/aliyun_production_fixed.py << 'EOF'
"""
QAToolBox 阿里云生产环境配置 - 完整功能版本
支持所有特性：ML/AI、数据处理、文档处理、OCR等
"""
import os
import sys
from pathlib import Path

# 基础配置
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / 'apps'))

# 尝试导入环境变量库
try:
    import environ
    env = environ.Env(DEBUG=(bool, False))
    # 尝试读取.env文件
    env_file = BASE_DIR / '.env'
    if env_file.exists():
        environ.Env.read_env(env_file)
except ImportError:
    try:
        from decouple import config
        env = lambda key, default=None, cast=str: config(key, default=default, cast=cast)
    except ImportError:
        env = lambda key, default=None, cast=str: cast(os.environ.get(key, default)) if cast != bool else os.environ.get(key, str(default)).lower() == 'true'

# 基础Django设置
SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env('DEBUG', default=False, cast=bool)

# 允许的主机
ALLOWED_HOSTS_STR = env('ALLOWED_HOSTS', default='localhost,127.0.0.1,shenyiqing.xin,47.103.143.152')
if isinstance(ALLOWED_HOSTS_STR, str):
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_STR.split(',') if host.strip()]
else:
    ALLOWED_HOSTS = ALLOWED_HOSTS_STR

ALLOWED_HOSTS.append('testserver')

# 站点配置
SITE_ID = 1

# 文件上传设置
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# Django核心应用
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

# 第三方应用 - 安全地添加
THIRD_PARTY_APPS = []
optional_third_party = [
    'rest_framework',
    'corsheaders', 
    'captcha',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'channels',
    'django_extensions',
    'debug_toolbar',
]

for app in optional_third_party:
    try:
        __import__(app)
        THIRD_PARTY_APPS.append(app)
        print(f"✅ 已添加第三方应用: {app}")
    except ImportError:
        print(f"⚠️ 跳过未安装的应用: {app}")

# 本地应用 - 安全地添加
LOCAL_APPS = []
local_app_candidates = [
    'apps.users',
    'apps.content', 
    'apps.tools',
    'apps.share',
]

for app in local_app_candidates:
    app_path = BASE_DIR / app.replace('.', '/')
    if app_path.exists() and (app_path / '__init__.py').exists():
        LOCAL_APPS.append(app)
        print(f"✅ 已添加本地应用: {app}")
    else:
        print(f"⚠️ 跳过不存在的应用: {app}")

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 中间件配置 - 只包含安全的中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 安全地添加中间件
if 'corsheaders' in THIRD_PARTY_APPS:
    MIDDLEWARE.insert(2, 'corsheaders.middleware.CorsMiddleware')

if 'debug_toolbar' in THIRD_PARTY_APPS and DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

# 安全地添加自定义中间件
custom_middlewares = [
    ('apps.users.middleware.SessionExtensionMiddleware', 'SessionExtensionMiddleware'),
]

for middleware_path, middleware_name in custom_middlewares:
    try:
        module_path = '.'.join(middleware_path.split('.')[:-1])
        __import__(module_path)
        MIDDLEWARE.append(middleware_path)
        print(f"✅ 已添加自定义中间件: {middleware_name}")
    except ImportError as e:
        print(f"⚠️ 跳过有问题的中间件: {middleware_name} - {e}")

ROOT_URLCONF = 'urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

# Channels配置 (如果安装了)
if 'channels' in THIRD_PARTY_APPS:
    ASGI_APPLICATION = 'asgi.application'
    
    # Channel Layers配置
    if 'channels_redis' in [app for app in THIRD_PARTY_APPS]:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [env('REDIS_URL', default='redis://localhost:6379/0')],
                },
            },
        }
    else:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer'
            }
        }

# 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='qatoolbox'),
        'USER': env('DB_USER', default='qatoolbox'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
        'OPTIONS': {
            'connect_timeout': 60,
            'sslmode': 'prefer',
        },
        'CONN_MAX_AGE': 60,
    }
}

# Redis缓存配置
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'qatoolbox',
        'VERSION': 1,
    }
}

# 会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1209600  # 14天
SESSION_COOKIE_SECURE = False  # SSL后改为True
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = False

# 国际化
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/qatoolbox/static/'

# 收集静态文件的目录
STATICFILES_DIRS = []
static_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'src' / 'static',
]

for static_dir in static_dirs:
    if static_dir.exists():
        STATICFILES_DIRS.append(static_dir)

# 静态文件存储配置
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/qatoolbox/media/'

# 确保媒体目录存在
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

# 默认主键字段类型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 完整日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/qatoolbox/django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/qatoolbox/django_error.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'qatoolbox': {
            'handlers': ['file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 确保日志目录存在
Path('/var/log/qatoolbox').mkdir(parents=True, exist_ok=True)

# Django REST Framework配置
if 'rest_framework' in THIRD_PARTY_APPS:
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ],
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.FormParser',
            'rest_framework.parsers.MultiPartParser',
        ],
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '1000/hour',
            'user': '10000/hour',
        },
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    }

# CORS配置
if 'corsheaders' in THIRD_PARTY_APPS:
    CORS_ALLOWED_ORIGINS = [
        "https://shenyiqing.xin",
        "https://www.shenyiqing.xin",
        "http://47.103.143.152",
    ]
    
    CORS_ALLOW_CREDENTIALS = True
    
    CORS_ALLOWED_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]

# Crispy Forms配置
if 'crispy_forms' in THIRD_PARTY_APPS:
    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

# 验证码配置
if 'captcha' in THIRD_PARTY_APPS:
    CAPTCHA_IMAGE_SIZE = (120, 40)
    CAPTCHA_LENGTH = 4
    CAPTCHA_TIMEOUT = 5
    CAPTCHA_BACKGROUND_COLOR = '#ffffff'
    CAPTCHA_FOREGROUND_COLOR = '#333333'

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# SSL配置 (初期关闭)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

# CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'https://shenyiqing.xin',
    'https://www.shenyiqing.xin',
    'http://47.103.143.152',
    'http://47.103.143.152:8000',
]

# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery配置
if 'celery' in [app.split('.')[-1] for app in INSTALLED_APPS]:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = TIME_ZONE
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Debug Toolbar配置
if 'debug_toolbar' in THIRD_PARTY_APPS and DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]

# 自定义设置
CUSTOM_SETTINGS = {
    'DEPLOYMENT_TYPE': 'aliyun_production_complete',
    'REGION': 'china',
    'SERVER_LOCATION': 'aliyun',
    'VERSION': '3.0.0',
    'FEATURES': [
        'machine_learning',
        'data_processing', 
        'document_processing',
        'ocr',
        'audio_processing',
        'browser_automation',
        'real_time_communication',
    ]
}

print(f"✅ QAToolBox 完整功能配置加载完成")
print(f"安装的应用数量: {len(INSTALLED_APPS)}")
print(f"Django应用: {len(DJANGO_APPS)}")
print(f"第三方应用: {len(THIRD_PARTY_APPS)}")
print(f"本地应用: {len(LOCAL_APPS)}")
print(f"支持的功能: {', '.join(CUSTOM_SETTINGS['FEATURES'])}")
EOF

    # 使用修复后的配置
    mv config/settings/aliyun_production_fixed.py config/settings/aliyun_production.py
    
    echo -e "${YELLOW}⚙️ 创建环境变量文件...${NC}"
    
    # 创建环境变量文件
    cat > .env << EOF
# Django基础配置
DJANGO_SECRET_KEY=django-aliyun-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.aliyun_production

# 主机配置
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 生产环境配置
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False

# 邮件配置
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# AI和API配置
DEEPSEEK_API_KEY=your-deepseek-api-key
GOOGLE_API_KEY=your-google-api-key
OPENWEATHER_API_KEY=your-openweather-api-key

# 日志配置
LOG_LEVEL=INFO
EOF
    
    # 设置文件权限
    chown "$PROJECT_USER:$PROJECT_USER" .env
    chmod 600 .env
    
    echo -e "${GREEN}✅ Django配置修复完成${NC}"
}

# 初始化Django应用
initialize_django_application() {
    show_progress "9" "15" "初始化Django应用和数据库"
    
    cd "$PROJECT_DIR"
    
    echo -e "${YELLOW}🧪 测试Django配置...${NC}"
    
    # 设置环境变量
    export DJANGO_SETTINGS_MODULE=config.settings.aliyun_production
    
    # 测试配置是否正确
    if ! sudo -u "$PROJECT_USER" DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python -c "import django; django.setup(); print('✅ Django配置测试成功')"; then
        handle_error "Django配置测试失败" "检查配置文件和依赖"
    fi
    
    echo -e "${YELLOW}📊 创建数据库迁移...${NC}"
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py makemigrations --noinput" "创建数据库迁移" 2 5
    
    echo -e "${YELLOW}📊 执行数据库迁移...${NC}"
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py migrate --noinput" "执行数据库迁移" 2 5
    
    echo -e "${YELLOW}📁 收集静态文件...${NC}"
    retry_command "sudo -u '$PROJECT_USER' DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py collectstatic --noinput" "收集静态文件" 2 5
    
    echo -e "${YELLOW}👑 创建管理员用户...${NC}"
    
    # 创建管理员用户
    sudo -u "$PROJECT_USER" DJANGO_SETTINGS_MODULE=config.settings.aliyun_production .venv/bin/python manage.py shell << PYTHON_EOF
import os
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# 删除已存在的admin用户
User.objects.filter(username='admin').delete()

# 创建新的管理员用户
admin_user = User.objects.create_superuser(
    username='admin',
    email='admin@${DOMAIN}',
    password='${ADMIN_PASSWORD}'
)

print(f"✅ 管理员用户创建成功: {admin_user.username}")
print(f"邮箱: {admin_user.email}")
PYTHON_EOF
    
    echo -e "${GREEN}✅ Django应用初始化完成${NC}"
}

# 配置Web服务
setup_web_services() {
    show_progress "10" "15" "配置Nginx和Supervisor服务"
    
    echo -e "${YELLOW}🌐 配置高性能Nginx...${NC}"
    
    # 创建优化的Nginx配置
    cat > /etc/nginx/sites-available/qatoolbox << EOF
# QAToolBox 高性能Nginx配置
upstream qatoolbox_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 文件上传大小限制
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    client_body_timeout 60s;
    client_header_timeout 60s;
    
    # 连接优化
    keepalive_timeout 65;
    keepalive_requests 100;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml
        font/truetype
        font/opentype
        application/vnd.ms-fontobject;
    
    # 静态文件缓存
    location /static/ {
        alias /var/www/qatoolbox/static/;
        expires 1M;
        add_header Cache-Control "public, immutable";
        add_header Vary "Accept-Encoding";
        access_log off;
        
        # 字体文件CORS
        location ~* \.(woff|woff2|ttf|eot)$ {
            add_header Access-Control-Allow-Origin "*";
        }
    }
    
    # 媒体文件
    location /media/ {
        alias /var/www/qatoolbox/media/;
        expires 1w;
        add_header Cache-Control "public";
        
        # 安全措施：防止执行上传的脚本
        location ~* \.(php|py|pl|sh|cgi|asp|aspx|jsp)$ {
            deny all;
        }
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # 机器人文件
    location = /robots.txt {
        return 200 "User-agent: *\\nDisallow: /admin/\\nDisallow: /api/\\nSitemap: https://$DOMAIN/sitemap.xml\\n";
        add_header Content-Type text/plain;
    }
    
    # Django应用代理
    location / {
        proxy_pass http://qatoolbox_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
        
        # WebSocket支持
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;
    }
    
    # 错误页面
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    # 限制访问敏感文件
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~ ~$ {
        deny all;
        access_log off;
        log_not_found off;
    }
}

# WebSocket升级映射
map \$http_upgrade \$connection_upgrade {
    default upgrade;
    '' close;
}
EOF
    
    # 启用站点配置
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    nginx -t || handle_error "Nginx配置语法错误" "检查配置文件语法"
    
    echo -e "${YELLOW}⚡ 配置Supervisor...${NC}"
    
    # 创建Supervisor配置
    cat > /etc/supervisor/conf.d/qatoolbox.conf << EOF
[program:qatoolbox]
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/qatoolbox/gunicorn.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=3
stderr_logfile=/var/log/qatoolbox/gunicorn_error.log
stderr_logfile_maxbytes=50MB
stderr_logfile_backups=3

# Gunicorn详细配置
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production",PATH="$PROJECT_DIR/.venv/bin"
command=$PROJECT_DIR/.venv/bin/gunicorn wsgi:application 
    --bind 127.0.0.1:8000 
    --workers 4
    --worker-class sync
    --worker-connections 1000
    --max-requests 1000
    --max-requests-jitter 100
    --timeout 60
    --keepalive 5
    --preload
    --access-logfile /var/log/qatoolbox/gunicorn_access.log
    --error-logfile /var/log/qatoolbox/gunicorn_error.log
    --log-level info

# 进程管理
killasgroup=true
stopasgroup=true
stopsignal=TERM
stopwaitsecs=10
startretries=3
EOF
    
    # 如果支持Celery，添加Celery配置
    if sudo -u "$PROJECT_USER" "$PROJECT_DIR/.venv/bin/python" -c "import celery" 2>/dev/null; then
        echo -e "${YELLOW}⚡ 配置Celery Worker...${NC}"
        
        cat > /etc/supervisor/conf.d/celery.conf << EOF
[program:celery_worker]
command=$PROJECT_DIR/.venv/bin/celery -A QAToolBox worker --loglevel=info
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox/celery.log
stderr_logfile=/var/log/qatoolbox/celery_error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production"

[program:celery_beat]
command=$PROJECT_DIR/.venv/bin/celery -A QAToolBox beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=$PROJECT_DIR
user=$PROJECT_USER
autostart=true
autorestart=true
stdout_logfile=/var/log/qatoolbox/celery_beat.log
stderr_logfile=/var/log/qatoolbox/celery_beat_error.log
environment=DJANGO_SETTINGS_MODULE="config.settings.aliyun_production"
EOF
    fi
    
    # 重新加载Supervisor配置
    supervisorctl reread
    supervisorctl update
    
    # 重启服务
    systemctl restart nginx
    supervisorctl restart qatoolbox
    
    if sudo -u "$PROJECT_USER" "$PROJECT_DIR/.venv/bin/python" -c "import celery" 2>/dev/null; then
        supervisorctl restart celery_worker celery_beat 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✅ Web服务配置完成${NC}"
}

# 配置防火墙和安全
setup_security() {
    show_progress "11" "15" "配置防火墙和高级安全"
    
    echo -e "${YELLOW}🔒 配置UFW防火墙...${NC}"
    
    # 安装并配置UFW
    apt install -y ufw
    
    # 重置防火墙规则
    ufw --force reset
    
    # 设置默认策略
    ufw default deny incoming
    ufw default allow outgoing
    
    # 允许必要端口
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # 限制SSH连接
    ufw limit ssh
    
    # 启用防火墙
    ufw --force enable
    
    echo -e "${YELLOW}🛡️ 配置系统安全...${NC}"
    
    # 禁用不必要的服务
    systemctl disable apache2 2>/dev/null || true
    systemctl stop apache2 2>/dev/null || true
    
    # 设置文件权限
    chmod 640 "$PROJECT_DIR/.env"
    chmod -R 755 "$PROJECT_DIR"
    chown -R "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
    
    # 设置日志权限
    chmod -R 755 /var/log/qatoolbox
    chown -R "$PROJECT_USER:$PROJECT_USER" /var/log/qatoolbox
    
    echo -e "${GREEN}✅ 安全配置完成${NC}"
}

# 优化系统性能
optimize_performance() {
    show_progress "12" "15" "优化系统性能"
    
    echo -e "${YELLOW}⚡ 优化系统参数...${NC}"
    
    # 优化内核参数
    cat >> /etc/sysctl.conf << EOF

# QAToolBox 性能优化
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_keepalive_intvl = 15
net.ipv4.tcp_keepalive_probes = 5
vm.swappiness = 10
fs.file-max = 65535
EOF
    
    sysctl -p
    
    echo -e "${YELLOW}⚡ 优化Nginx...${NC}"
    
    # 优化Nginx工作进程数
    worker_processes=$(nproc)
    sed -i "s/worker_processes auto;/worker_processes $worker_processes;/" /etc/nginx/nginx.conf || true
    
    echo -e "${YELLOW}⚡ 优化PostgreSQL...${NC}"
    
    # 基础PostgreSQL优化
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONFIG="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    if [ -f "$PG_CONFIG" ]; then
        # 获取系统内存
        TOTAL_MEM=$(free -m | awk '/^Mem:/{print $2}')
        SHARED_BUFFERS=$((TOTAL_MEM / 4))
        EFFECTIVE_CACHE_SIZE=$((TOTAL_MEM * 3 / 4))
        
        # 优化PostgreSQL配置
        sed -i "s/#shared_buffers = 128MB/shared_buffers = ${SHARED_BUFFERS}MB/" "$PG_CONFIG" || true
        sed -i "s/#effective_cache_size = 4GB/effective_cache_size = ${EFFECTIVE_CACHE_SIZE}MB/" "$PG_CONFIG" || true
        sed -i "s/#work_mem = 4MB/work_mem = 16MB/" "$PG_CONFIG" || true
        sed -i "s/#maintenance_work_mem = 64MB/maintenance_work_mem = 256MB/" "$PG_CONFIG" || true
        
        systemctl restart postgresql
    fi
    
    echo -e "${GREEN}✅ 性能优化完成${NC}"
}

# 安装监控工具
setup_monitoring() {
    show_progress "13" "15" "安装系统监控工具"
    
    echo -e "${YELLOW}📊 安装监控工具...${NC}"
    
    # 安装系统监控工具
    apt install -y htop iotop nethogs ncdu
    
    # 创建系统监控脚本
    cat > /usr/local/bin/qatoolbox-status << 'EOF'
#!/bin/bash
echo "=== QAToolBox 系统状态 ==="
echo ""
echo "🖥️ 系统信息:"
echo "  操作系统: $(lsb_release -d | cut -f2)"
echo "  内核版本: $(uname -r)"
echo "  运行时间: $(uptime -p)"
echo "  负载: $(uptime | awk -F'load average:' '{print $2}')"
echo ""
echo "💾 内存使用:"
free -h
echo ""
echo "💽 磁盘使用:"
df -h /
echo ""
echo "🔧 服务状态:"
for service in nginx postgresql redis-server supervisor; do
    if systemctl is-active --quiet $service; then
        echo "  ✅ $service: 运行中"
    else
        echo "  ❌ $service: 停止"
    fi
done
echo ""
echo "📱 应用状态:"
supervisorctl status | grep qatoolbox
echo ""
echo "🌐 网络连接:"
netstat -tlnp | grep -E ':(80|443|5432|6379|8000)\s'
EOF

    chmod +x /usr/local/bin/qatoolbox-status
    
    echo -e "${GREEN}✅ 监控工具安装完成${NC}"
}

# 创建备份脚本
setup_backup() {
    show_progress "14" "15" "配置自动备份"
    
    echo -e "${YELLOW}💾 创建备份脚本...${NC}"
    
    # 创建备份目录
    mkdir -p /backup/qatoolbox/{database,media,code}
    chown -R "$PROJECT_USER:$PROJECT_USER" /backup/qatoolbox
    
    # 创建数据库备份脚本
    cat > /usr/local/bin/qatoolbox-backup << EOF
#!/bin/bash
BACKUP_DIR="/backup/qatoolbox"
DATE=\$(date +%Y%m%d_%H%M%S)

echo "开始备份 QAToolBox..."

# 数据库备份
echo "备份数据库..."
sudo -u postgres pg_dump qatoolbox > "\$BACKUP_DIR/database/qatoolbox_\$DATE.sql"

# 媒体文件备份
echo "备份媒体文件..."
rsync -av /var/www/qatoolbox/media/ "\$BACKUP_DIR/media/"

# 代码备份
echo "备份项目代码..."
tar -czf "\$BACKUP_DIR/code/qatoolbox_code_\$DATE.tar.gz" -C /home/$PROJECT_USER QAToolBox

# 清理旧备份（保留7天）
find "\$BACKUP_DIR/database" -name "*.sql" -mtime +7 -delete
find "\$BACKUP_DIR/code" -name "*.tar.gz" -mtime +7 -delete

echo "备份完成: \$DATE"
EOF

    chmod +x /usr/local/bin/qatoolbox-backup
    
    # 添加定时任务
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/qatoolbox-backup >> /var/log/qatoolbox/backup.log 2>&1") | crontab -
    
    echo -e "${GREEN}✅ 备份配置完成${NC}"
}

# 最终验证和信息显示
final_verification() {
    show_progress "15" "15" "最终验证和系统信息"
    
    echo -e "${YELLOW}🔍 等待服务启动...${NC}"
    sleep 20
    
    echo -e "${YELLOW}🔍 检查所有服务状态...${NC}"
    
    # 检查系统服务
    local services=("nginx" "postgresql" "redis-server" "supervisor")
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            echo -e "${GREEN}✅ $service 运行正常${NC}"
        else
            echo -e "${RED}❌ $service 状态异常${NC}"
        fi
    done
    
    # 检查Supervisor管理的应用
    local supervisor_status=$(supervisorctl status qatoolbox | head -1)
    if echo "$supervisor_status" | grep -q "RUNNING"; then
        echo -e "${GREEN}✅ QAToolBox应用运行正常${NC}"
    else
        echo -e "${RED}❌ QAToolBox应用状态异常${NC}"
        echo -e "${YELLOW}状态: $supervisor_status${NC}"
    fi
    
    # 检查Celery（如果安装了）
    if supervisorctl status | grep -q celery; then
        if supervisorctl status | grep celery | grep -q RUNNING; then
            echo -e "${GREEN}✅ Celery任务队列运行正常${NC}"
        else
            echo -e "${YELLOW}⚠️ Celery任务队列状态异常${NC}"
        fi
    fi
    
    echo -e "${YELLOW}🌐 测试HTTP访问...${NC}"
    
    # 测试本地访问
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "000")
    
    if [[ "$http_status" =~ ^(200|301|302)$ ]]; then
        echo -e "${GREEN}✅ HTTP访问正常 (状态码: $http_status)${NC}"
    else
        echo -e "${YELLOW}⚠️ HTTP访问异常 (状态码: $http_status)${NC}"
    fi
    
    # 测试数据库连接
    if sudo -u "$PROJECT_USER" DJANGO_SETTINGS_MODULE=config.settings.aliyun_production "$PROJECT_DIR/.venv/bin/python" -c "
import django
django.setup()
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('数据库连接正常')
" 2>/dev/null; then
        echo -e "${GREEN}✅ 数据库连接正常${NC}"
    else
        echo -e "${YELLOW}⚠️ 数据库连接异常${NC}"
    fi
    
    # 检查Python包安装
    local key_packages=("Django" "psycopg2" "redis" "gunicorn" "celery" "torch" "opencv-python")
    echo -e "${YELLOW}🐍 检查关键Python包...${NC}"
    
    for package in "${key_packages[@]}"; do
        if sudo -u "$PROJECT_USER" "$PROJECT_DIR/.venv/bin/python" -c "import $package" 2>/dev/null; then
            local version=$(sudo -u "$PROJECT_USER" "$PROJECT_DIR/.venv/bin/python" -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
            echo -e "${GREEN}✅ $package: $version${NC}"
        else
            echo -e "${YELLOW}⚠️ $package: 未安装或有问题${NC}"
        fi
    done
    
    # 显示最终部署信息
    echo -e "${CYAN}${BOLD}"
    cat << EOF

========================================
🎉 QAToolBox 完整功能部署成功！
========================================

🌐 访问信息:
  主站地址: http://$DOMAIN/
  IP访问:   http://$SERVER_IP/
  管理后台: http://$DOMAIN/admin/

👑 管理员账户:
  用户名: admin
  密码:   $ADMIN_PASSWORD
  邮箱:   admin@$DOMAIN

📊 系统信息:
  项目目录: $PROJECT_DIR
  数据库:   PostgreSQL (qatoolbox)
  缓存:     Redis
  Python:   $(python3 --version 2>&1)
  Django:   $(sudo -u $PROJECT_USER $PROJECT_DIR/.venv/bin/python -c "import django; print(django.get_version())" 2>/dev/null || echo "未知")

🚀 完整功能支持:
  ✅ 机器学习 (PyTorch, TensorFlow, scikit-learn)
  ✅ 计算机视觉 (OpenCV, PIL, scikit-image)
  ✅ 数据分析 (pandas, numpy, matplotlib)
  ✅ 文档处理 (Word, Excel, PDF, PPT)
  ✅ OCR识别 (Tesseract, EasyOCR, PaddleOCR)
  ✅ 音频处理 (pydub, librosa, 语音识别)
  ✅ 浏览器自动化 (Selenium, Playwright)
  ✅ 实时通信 (WebSocket, Channels)
  ✅ 任务队列 (Celery, Redis)
  ✅ API框架 (DRF, CORS支持)

🔧 管理命令:
  系统状态: qatoolbox-status
  数据备份: qatoolbox-backup
  重启应用: sudo supervisorctl restart qatoolbox
  查看日志: sudo tail -f /var/log/qatoolbox/gunicorn.log
  重启服务: sudo systemctl restart nginx
  
🔗 快速链接:
  Supervisor: sudo supervisorctl status
  系统监控: htop
  磁盘使用: df -h
  网络连接: netstat -tlnp

📋 日志文件:
  部署日志: $LOG_FILE
  应用日志: /var/log/qatoolbox/gunicorn.log
  Django日志: /var/log/qatoolbox/django.log
  Nginx日志: /var/log/nginx/access.log
  错误日志: /var/log/qatoolbox/gunicorn_error.log

🔒 安全配置:
  防火墙: UFW已启用 (SSH, HTTP, HTTPS)
  SSL配置: 待配置 (建议使用Let's Encrypt)
  数据库密码: $DB_PASSWORD
  文件权限: 已优化设置

📝 下一步建议:
  1. 配置域名DNS解析指向 $SERVER_IP
  2. 申请SSL证书 (certbot --nginx -d $DOMAIN)
  3. 配置邮件服务 (可选)
  4. 设置API密钥 (编辑 .env 文件)
  5. 定期执行系统更新和备份

========================================
EOF
    echo -e "${NC}"
    
    echo -e "${BLUE}🧪 快速测试命令:${NC}"
    echo -e "  curl -I http://localhost/"
    echo -e "  curl -I http://$SERVER_IP/"
    echo -e "  qatoolbox-status"
    echo ""
    
    echo -e "${CYAN}🎊 恭喜！QAToolBox完整功能部署成功完成！${NC}"
    echo -e "${BLUE}现在您可以享受所有AI和数据处理功能了！${NC}"
}

# 主执行流程
main() {
    # 检查权限
    check_root
    
    # 设置错误处理
    trap 'echo -e "${RED}❌ 部署过程中出现错误，请查看日志: $LOG_FILE${NC}"; exit 1' ERR
    
    echo -e "${BLUE}🚀 开始QAToolBox完整功能阿里云部署...${NC}"
    echo -e "${BLUE}📋 详细日志: $LOG_FILE${NC}"
    echo ""
    
    # 执行部署步骤
    detect_system
    setup_china_mirrors
    update_system
    install_complete_system_dependencies
    setup_system_services
    setup_project_user
    verify_project_code
    setup_complete_python_environment
    fix_django_configuration
    initialize_django_application
    setup_web_services
    setup_security
    optimize_performance
    setup_monitoring
    setup_backup
    final_verification
    
    echo -e "${GREEN}🎉 QAToolBox完整功能阿里云部署成功完成！${NC}"
}

# 检查是否为脚本直接执行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
