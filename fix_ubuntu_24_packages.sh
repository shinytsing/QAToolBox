#!/bin/bash

# Ubuntu 24.04 包依赖修复脚本
set -e

log_info() {
    echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
    echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

PROJECT_USER="qatoolbox"
PROJECT_DIR="/home/qatoolbox/QAToolBox"

log_info "🔧 修复Ubuntu 24.04包依赖问题"

# 1. 更新包列表
apt update

# 2. 安装Ubuntu 24.04兼容的OpenGL包
log_info "安装Ubuntu 24.04兼容的OpenGL和图像处理包"
apt install -y \
    libopengl0 \
    libglx0 \
    libgl1 \
    libglu1-mesa \
    libglib2.0-0t64 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    python3-dev \
    build-essential \
    cmake \
    pkg-config

log_success "系统包安装完成"

# 3. 进入项目目录并修复OpenCV
if [ -d "$PROJECT_DIR" ]; then
    cd $PROJECT_DIR
    
    log_info "修复OpenCV依赖"
    # 卸载可能有问题的opencv-python
    sudo -u $PROJECT_USER .venv/bin/pip uninstall opencv-python opencv-contrib-python -y || true
    
    # 安装无头版本的OpenCV
    sudo -u $PROJECT_USER .venv/bin/pip install opencv-python-headless \
        -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    
    log_success "OpenCV修复完成"
    
    # 4. 安装其他可能缺失的依赖
    log_info "安装其他缺失的Python依赖"
    sudo -u $PROJECT_USER .venv/bin/pip install \
        django-environ \
        psutil \
        -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
    
    # 5. 测试Django配置
    log_info "测试Django配置"
    if sudo -u $PROJECT_USER .venv/bin/python manage.py check --settings=config.settings.production; then
        log_success "Django配置检查通过"
    else
        log_warning "Django配置检查失败，但继续执行"
    fi
    
    # 6. 执行数据库迁移
    log_info "执行数据库迁移"
    sudo -u $PROJECT_USER .venv/bin/python manage.py makemigrations --settings=config.settings.production || true
    sudo -u $PROJECT_USER .venv/bin/python manage.py migrate --settings=config.settings.production || true
    
    # 7. 收集静态文件
    log_info "收集静态文件"
    sudo -u $PROJECT_USER mkdir -p staticfiles media
    sudo -u $PROJECT_USER .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.production || true
    
else
    log_warning "项目目录不存在，跳过Python相关配置"
fi

log_success "🎉 Ubuntu 24.04兼容性修复完成"

echo
echo "📋 后续操作："
echo "1. 创建超级用户："
echo "   cd $PROJECT_DIR"
echo "   sudo -u $PROJECT_USER .venv/bin/python manage.py createsuperuser --settings=config.settings.production"
echo
echo "2. 启动服务："
echo "   systemctl restart qatoolbox nginx"
echo
echo "3. 检查服务状态："
echo "   systemctl status qatoolbox nginx postgresql redis-server"
