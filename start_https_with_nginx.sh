#!/bin/bash

# QAToolBox HTTPS启动脚本 (使用Nginx反向代理)

echo "🔐 启动QAToolBox HTTPS服务..."
echo "📍 HTTPS地址: https://192.168.0.118:8443"
echo "📍 本地访问: https://localhost:8443"
echo "⚠️  浏览器会提示证书不安全，请点击'继续访问'"
echo "------------------------------------------------------------"

# 检查nginx是否安装
if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx未安装，正在安装..."
    if command -v brew &> /dev/null; then
        brew install nginx
    else
        echo "❌ 请先安装Homebrew，然后运行: brew install nginx"
        exit 1
    fi
fi

# 检查HTTP服务器是否运行
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ Django HTTP服务器未运行，请先启动HTTP服务器"
    echo "运行: python3 manage.py runserver 0.0.0.0:8000"
    exit 1
fi

# 启动nginx
echo "🚀 启动Nginx HTTPS代理..."
sudo nginx -c "$(pwd)/nginx_https.conf" -g "daemon off;"
