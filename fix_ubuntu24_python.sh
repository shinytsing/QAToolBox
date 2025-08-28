#!/bin/bash
# =============================================================================
# Ubuntu 24.04 Python环境修复脚本
# =============================================================================
# 解决Ubuntu 24.04中python3-distutils不存在的问题
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

echo -e "${BLUE}🔧 修复Ubuntu 24.04 Python环境问题...${NC}"

# 检测Ubuntu版本
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}检测到系统: $NAME $VERSION_ID${NC}"
fi

echo -e "${YELLOW}🐍 安装Ubuntu 24.04兼容的Python环境...${NC}"

# Ubuntu 24.04的正确Python包安装
DEBIAN_FRONTEND=noninteractive apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-full \
    python3-setuptools \
    python3-wheel \
    python3-tk \
    python3-dbg

echo -e "${YELLOW}🔧 安装额外的开发工具...${NC}"

# 安装可能需要的额外工具
DEBIAN_FRONTEND=noninteractive apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    autoconf \
    automake \
    libtool

echo -e "${YELLOW}📦 验证Python安装...${NC}"

# 验证Python安装
python3 --version
pip3 --version

# 确保pip是最新版本
python3 -m pip install --upgrade pip

echo -e "${GREEN}✅ Ubuntu 24.04 Python环境修复完成${NC}"

echo -e "${BLUE}💡 继续执行部署脚本...${NC}"

# 现在继续执行完整的部署脚本其余部分
PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/$PROJECT_USER/QAToolBox"

echo -e "${YELLOW}🗄️ 安装数据库服务...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    postgresql postgresql-contrib postgresql-client \
    postgresql-server-dev-all \
    redis-server redis-tools

echo -e "${YELLOW}🌐 安装Web服务器...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    nginx nginx-extras \
    supervisor

echo -e "${YELLOW}🔒 安装开发库...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    libssl-dev libffi-dev libcrypto++-dev \
    libsasl2-dev libldap2-dev \
    libpq-dev postgresql-client \
    libmysqlclient-dev default-libmysqlclient-dev \
    libsqlite3-dev

echo -e "${YELLOW}🖼️ 安装图像处理库...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
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
    libxcb1-dev

echo -e "${YELLOW}🎬 安装音视频处理库...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    ffmpeg \
    libavcodec-dev libavformat-dev libswscale-dev \
    libavresample-dev libavutil-dev \
    libsndfile1-dev libsndfile1 \
    portaudio19-dev \
    libasound2-dev \
    libpulse-dev \
    libmp3lame-dev \
    libvorbis-dev \
    libtheora-dev

echo -e "${YELLOW}🔤 安装OCR和文本处理...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra \
    tesseract-ocr-eng tesseract-ocr-osd \
    libtesseract-dev \
    poppler-utils \
    antiword \
    unrtf \
    ghostscript

echo -e "${YELLOW}🧮 安装科学计算库...${NC}"
DEBIAN_FRONTEND=noninteractive apt install -y \
    libgomp1 libomp-dev \
    libatlas-base-dev liblapack-dev libblas-dev \
    libopenblas-dev \
    libhdf5-dev libhdf5-103 \
    libnetcdf-dev \
    libprotobuf-dev protobuf-compiler \
    libboost-all-dev

echo -e "${GREEN}✅ 所有系统依赖安装完成${NC}"
echo -e "${BLUE}🎯 现在可以继续Python包安装了${NC}"
EOF

chmod +x fix_ubuntu24_python.sh
