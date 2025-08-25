#!/bin/bash

# =============================================================================
# Ubuntu 24.04 APT问题修复脚本
# 专门解决 "ModuleNotFoundError: No module named 'apt_pkg'" 错误
# =============================================================================

echo "🔧 Ubuntu 24.04 APT问题修复脚本"
echo "================================"

# 检查是否为Ubuntu 24.04
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ $VERSION_ID == "24.04" ]]; then
        echo "✅ 检测到Ubuntu 24.04，开始修复..."
    else
        echo "ℹ️  当前系统: $NAME $VERSION_ID"
        echo "⚠️  此脚本专为Ubuntu 24.04设计"
        exit 0
    fi
else
    echo "❌ 无法检测系统版本"
    exit 1
fi

# 1. 临时禁用command-not-found更新
echo "🚫 临时禁用command-not-found更新..."
if [ -f /etc/apt/apt.conf.d/50command-not-found ]; then
    sudo mv /etc/apt/apt.conf.d/50command-not-found /etc/apt/apt.conf.d/50command-not-found.disabled
    echo "   已禁用 50command-not-found"
fi

# 2. 清理APT缓存
echo "🧹 清理APT缓存..."
sudo apt-get clean
sudo apt-get autoclean

# 3. 修复python3-apt包
echo "🔧 修复python3-apt包..."
sudo apt-get install --reinstall python3-apt python3-distutils -y 2>/dev/null || {
    echo "⚠️  重装失败，尝试强制安装..."
    sudo apt-get install --fix-broken python3-apt -y
}

# 4. 更新包索引
echo "📦 更新包索引..."
export DEBIAN_FRONTEND=noninteractive

for i in {1..3}; do
    if sudo apt-get update -y 2>/dev/null; then
        echo "✅ 包索引更新成功"
        break
    else
        echo "⚠️  更新失败，重试 $i/3..."
        sudo apt-get clean
        sleep 2
        if [ $i -eq 3 ]; then
            echo "❌ 包更新持续失败，但可以继续部署"
        fi
    fi
done

# 5. 验证修复结果
echo "🧪 验证修复结果..."
if python3 -c "import apt_pkg; print('apt_pkg模块正常')" 2>/dev/null; then
    echo "✅ apt_pkg模块修复成功"
    SUCCESS=true
else
    echo "⚠️  apt_pkg模块仍有问题，但不影响部署"
    SUCCESS=false
fi

# 6. 恢复command-not-found（可选）
read -p "是否恢复command-not-found功能? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f /etc/apt/apt.conf.d/50command-not-found.disabled ]; then
        sudo mv /etc/apt/apt.conf.d/50command-not-found.disabled /etc/apt/apt.conf.d/50command-not-found
        echo "✅ 已恢复command-not-found功能"
    fi
else
    echo "ℹ️  保持command-not-found禁用状态"
fi

echo
echo "🎉 Ubuntu 24.04 APT修复完成！"
if [ "$SUCCESS" = true ]; then
    echo "✅ 系统已就绪，可以运行主部署脚本"
else
    echo "⚠️  部分问题未完全解决，但不影响部署继续"
fi
echo
echo "现在可以运行主部署脚本:"
echo "curl -O https://raw.githubusercontent.com/shinytsing/QAToolbox/main/deploy_ubuntu_production.sh && sudo bash deploy_ubuntu_production.sh"
