#!/bin/bash

# 修复apt_pkg模块缺失问题

echo "🔧 修复apt_pkg模块缺失问题..."

# 方法1: 重新安装python3-apt
echo "重新安装python3-apt..."
sudo apt-get update
sudo apt-get install --reinstall python3-apt -y

# 方法2: 如果方法1失败，尝试修复Python链接
if ! python3 -c "import apt_pkg" 2>/dev/null; then
    echo "尝试修复Python链接..."
    
    # 获取Python版本
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    
    # 创建符号链接
    sudo ln -sf /usr/lib/python3/dist-packages/apt_pkg.cpython-*-x86_64-linux-gnu.so /usr/lib/python3/dist-packages/apt_pkg.so
    
    # 重新安装相关包
    sudo apt-get install --reinstall python3-distutils python3-lib2to3 -y
fi

# 验证修复
if python3 -c "import apt_pkg" 2>/dev/null; then
    echo "✅ apt_pkg模块修复成功"
else
    echo "❌ apt_pkg模块修复失败，尝试其他方法..."
    
    # 方法3: 完全重新安装Python3相关包
    sudo apt-get remove --purge python3-apt -y
    sudo apt-get autoremove -y
    sudo apt-get install python3-apt -y
fi

echo "🔧 修复完成，现在可以继续部署..."
