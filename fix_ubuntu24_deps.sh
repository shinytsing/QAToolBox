#!/bin/bash
# Ubuntu 24.04 包依赖冲突修复脚本
# =============================================
# 解决libglib2.0-0和libglib2.0-0t64冲突问题
# 保证所有依赖完整安装
# =============================================

set -e

echo "🔧 修复Ubuntu 24.04包依赖冲突..."

# 1. 更新包数据库
echo "📦 更新包数据库..."
apt update

# 2. 修复破损的包
echo "🛠️ 修复破损的包..."
apt --fix-broken install -y

# 3. 清理自动安装的不需要的包
echo "🧹 清理不需要的包..."
apt autoremove -y

# 4. 解决libglib2.0冲突 - 正确的方法
echo "🔄 解决glib包冲突..."

# 首先检查当前安装的glib版本
dpkg -l | grep libglib2.0 || true

# 方法1: 先卸载旧版本，再安装新版本
echo "方法1: 升级glib包..."
apt remove --purge libglib2.0-0 -y 2>/dev/null || true
apt install libglib2.0-0t64 -y

# 5. 强制升级所有包到最新版本
echo "📈 升级所有包到最新版本..."
apt full-upgrade -y

# 6. 安装基础开发工具
echo "🔨 安装基础开发工具..."
apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config

# 7. 安装系统库 - 分批安装，避免依赖冲突
echo "📚 安装系统库..."

# SSL和加密
apt install -y \
    libssl-dev \
    libffi-dev \
    libcrypto++-dev

# 数据库驱动
apt install -y \
    libpq-dev \
    postgresql-client \
    libmysqlclient-dev

# 图像处理库
apt install -y \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libwebp-dev

# 视频和音频处理
apt install -y \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    ffmpeg

# GUI和显示库
apt install -y \
    libgtk-3-dev \
    libcanberra-gtk-module \
    libcanberra-gtk3-module

# GStreamer
apt install -y \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev

# X11和渲染
apt install -y \
    libgl1-mesa-dri \
    libsm6 \
    libxext6 \
    libxrender1

# 科学计算库
apt install -y \
    libgomp1 \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev

# HDF5和协议缓冲
apt install -y \
    libhdf5-dev \
    libprotobuf-dev \
    protobuf-compiler

# 音频开发库
apt install -y \
    libsndfile1-dev \
    portaudio19-dev

# OCR支持
apt install -y \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra

# 8. 验证关键库是否正确安装
echo "✅ 验证关键库安装..."
echo "检查glib版本:"
pkg-config --modversion glib-2.0 || echo "glib检查失败"

echo "检查其他关键库:"
pkg-config --modversion libssl || echo "libssl检查失败"
pkg-config --modversion libpng || echo "libpng检查失败"
pkg-config --modversion protobuf || echo "protobuf检查失败"

# 9. 最后再次修复任何剩余问题
echo "🔧 最终修复..."
apt --fix-broken install -y
apt autoremove -y

echo "✅ Ubuntu 24.04依赖修复完成！"
echo "📊 安装的包统计:"
dpkg -l | grep -E "(libglib|libssl|libpng|protobuf)" | wc -l
echo "🚀 可以继续部署流程了"
