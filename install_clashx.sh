#!/bin/bash

echo "🚀 ClashX安装脚本"
echo "==================="

# 检查是否已安装Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未检测到Homebrew"
    echo "请先安装Homebrew："
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo ""
    echo "或者手动下载ClashX："
    echo "https://github.com/yichengchen/clashX/releases"
    exit 1
fi

echo "✅ 检测到Homebrew"

# 检查是否已安装ClashX
if ls /Applications/ClashX.app &> /dev/null; then
    echo "✅ ClashX已经安装"
    echo "📱 正在启动ClashX..."
    open -a ClashX
else
    echo "📥 正在安装ClashX..."
    brew install --cask clashx
    
    if [ $? -eq 0 ]; then
        echo "✅ ClashX安装成功！"
        echo "📱 正在启动ClashX..."
        open -a ClashX
    else
        echo "❌ ClashX安装失败"
        exit 1
    fi
fi

# 等待应用启动
echo "⏳ 等待ClashX启动..."
sleep 3

# 检查配置文件
if [ -f "clash_config_youtube_optimized.yaml" ]; then
    echo "✅ 找到配置文件: clash_config_youtube_optimized.yaml"
    echo ""
    echo "📋 接下来的步骤："
    echo "1. 在ClashX菜单栏图标上右键"
    echo "2. 选择 '配置' -> '导入配置文件'"
    echo "3. 选择文件: $(pwd)/clash_config_youtube_optimized.yaml"
    echo "4. 开启 '设置为系统代理'"
    echo "5. 选择 '规则模式'"
    echo ""
    echo "🎯 完成后，Google.com将正常显示，不再乱码！"
else
    echo "⚠️  未找到配置文件，请确保clash_config_youtube_optimized.yaml存在"
fi

echo ""
echo "🔗 有用的链接："
echo "- ClashX使用教程: https://github.com/yichengchen/clashX/wiki"
echo "- 故障排除指南: $(pwd)/CLASH_SETUP_GUIDE.md"
echo "- 诊断工具: $(pwd)/proxy_diagnostic.html"
