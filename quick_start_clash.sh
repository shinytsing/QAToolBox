#!/bin/bash

echo "🚀 快速启动Clash翻墙系统"
echo "=================================="

# 检查Clash是否运行
echo "🔍 检查Clash代理状态..."

if lsof -i :7890 > /dev/null 2>&1; then
    echo "✅ HTTP代理端口7890已启用"
    HTTP_PROXY_AVAILABLE=true
else
    echo "❌ HTTP代理端口7890未启用"
    HTTP_PROXY_AVAILABLE=false
fi

if lsof -i :7891 > /dev/null 2>&1; then
    echo "✅ SOCKS5代理端口7891已启用"
    SOCKS5_PROXY_AVAILABLE=true
else
    echo "❌ SOCKS5代理端口7891未启用"
    SOCKS5_PROXY_AVAILABLE=false
fi

# 如果代理不可用，提供启动建议
if [ "$HTTP_PROXY_AVAILABLE" = false ] && [ "$SOCKS5_PROXY_AVAILABLE" = false ]; then
    echo ""
    echo "⚠️  Clash代理未运行！"
    echo "💡 请先启动Clash客户端："
    echo "   1. 打开Clash应用"
    echo "   2. 导入您的配置文件"
    echo "   3. 确保代理已启用"
    echo "   4. 重新运行此脚本"
    echo ""
    echo "🔧 或者使用命令行启动："
    echo "   clash -d ~/.config/clash/"
    echo ""
    exit 1
fi

# 测试代理连接
echo ""
echo "🧪 测试代理连接..."

if [ "$HTTP_PROXY_AVAILABLE" = true ]; then
    echo "📡 测试HTTP代理 (7890)..."
    if curl -s -x http://127.0.0.1:7890 --connect-timeout 5 http://httpbin.org/ip > /dev/null 2>&1; then
        echo "   ✅ HTTP代理连接正常"
    else
        echo "   ❌ HTTP代理连接失败"
    fi
fi

if [ "$SOCKS5_PROXY_AVAILABLE" = true ]; then
    echo "📡 测试SOCKS5代理 (7891)..."
    if curl -s --socks5 127.0.0.1:7891 --connect-timeout 5 http://httpbin.org/ip > /dev/null 2>&1; then
        echo "   ✅ SOCKS5代理连接正常"
    else
        echo "   ❌ SOCKS5代理连接失败"
    fi
fi

# 启动Django服务器
echo ""
echo "🌐 启动Django翻墙系统..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip install -q requests PyYAML "requests[socks]"

# 检查Django是否运行
if lsof -i :8001 > /dev/null 2>&1; then
    echo "✅ Django服务器已在端口8001运行"
else
    echo "🚀 启动Django服务器..."
    python manage.py runserver 8001 &
    DJANGO_PID=$!
    echo "   Django服务器已启动 (PID: $DJANGO_PID)"
    echo "   💡 访问地址: http://localhost:8001/tools/proxy-dashboard/"
fi

# 运行翻墙测试
echo ""
echo "🧪 运行翻墙功能测试..."
python test_clash_proxy.py

echo ""
echo "🎯 系统启动完成！"
echo "=================================="
echo "💡 使用说明:"
echo "1. 访问: http://localhost:8001/tools/proxy-dashboard/"
echo "2. 登录系统"
echo "3. 使用Web翻墙浏览器访问外网"
echo "4. 享受无障碍的全球网络访问！"
echo ""
echo "🔧 如果遇到问题，请检查："
echo "   - Clash客户端是否正在运行"
echo "   - 代理端口7890/7891是否可用"
echo "   - Django服务器是否正常启动"
echo ""
echo "📞 技术支持: 查看 START_CLASH.md 文档"
