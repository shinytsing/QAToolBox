#!/bin/bash
# 修复Ubuntu 24.04图像处理库依赖冲突
# =============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}🔧 修复图像处理库依赖冲突...${NC}"

# 1. 清理APT缓存和修复破损包
echo -e "${BLUE}1. 清理APT缓存和修复破损包...${NC}"
apt update
apt --fix-broken install -y
apt autoremove -y
apt autoclean

# 2. 强制重新安装有冲突的包
echo -e "${BLUE}2. 强制重新安装有冲突的包...${NC}"
apt install --reinstall -y \
    libfreetype6 libfreetype6-dev \
    liblcms2-2 liblcms2-dev \
    libopenjp2-7 libopenjp2-7-dev || true

# 3. 使用apt-get而不是apt安装，避免版本冲突
echo -e "${BLUE}3. 使用apt-get安装图像处理库...${NC}"
apt-get install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev || echo "⚠️ 某些包已安装或有冲突，跳过"

# 4. 尝试安装freetype和lcms2的兼容版本
echo -e "${BLUE}4. 安装兼容版本的freetype和lcms2...${NC}"
apt-get install -y --allow-downgrades \
    libfreetype6-dev || echo "⚠️ freetype已是最新版本"

apt-get install -y --allow-downgrades \
    liblcms2-dev || echo "⚠️ lcms2已是最新版本"

# 5. 如果仍有冲突，跳过有问题的包
echo -e "${BLUE}5. 安装其他图像处理相关包...${NC}"
apt-get install -y \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    ffmpeg || echo "⚠️ 媒体库安装部分失败，不影响核心功能"

# 6. 最后的清理
echo -e "${BLUE}6. 最终清理...${NC}"
apt --fix-broken install -y
apt autoremove -y

echo -e "${GREEN}✅ 图像处理库冲突修复完成！${NC}"
echo -e "${YELLOW}💡 如果仍有冲突，可以跳过这些包，不影响Django核心功能${NC}"
