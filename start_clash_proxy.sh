#!/bin/bash

# Clash代理启动脚本

echo "🔧 启动Clash代理服务..."

# 检查Clash配置文件是否存在
CONFIG_FILE="clash_config_youtube_optimized.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ 找不到Clash配置文件: $CONFIG_FILE"
    echo "请确保配置文件存在"
    exit 1
fi

echo "✅ 找到配置文件: $CONFIG_FILE"

# 检查是否已安装Clash
if ! command -v clash &> /dev/null; then
    echo "⚠️  Clash未安装，请先安装Clash"
    echo ""
    echo "macOS安装方法:"
    echo "brew install clash"
    echo ""
    echo "或者下载Clash For macOS客户端"
    exit 1
fi

echo "✅ Clash已安装"

# 创建Clash配置目录
CLASH_DIR="$HOME/.config/clash"
if [ ! -d "$CLASH_DIR" ]; then
    mkdir -p "$CLASH_DIR"
    echo "✅ 创建Clash配置目录: $CLASH_DIR"
fi

# 复制配置文件
cp "$CONFIG_FILE" "$CLASH_DIR/config.yaml"
echo "✅ 配置文件已复制到: $CLASH_DIR/config.yaml"

# 启动Clash
echo "🚀 启动Clash代理服务..."
echo "   HTTP代理端口: 7890"
echo "   SOCKS代理端口: 7891"
echo "   控制面板: http://127.0.0.1:9090"
echo ""
echo "按Ctrl+C停止服务"
echo ""

# 启动Clash（在前台运行）
clash -f "$CLASH_DIR/config.yaml"
