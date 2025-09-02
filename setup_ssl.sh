#!/bin/bash

# SSL证书配置脚本
echo "🔐 配置SSL证书 for shenyiqing.xin"

# 检查是否安装了certbot
if ! command -v certbot &> /dev/null; then
    echo "📦 安装certbot..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install certbot
    else
        # Linux
        sudo apt-get update
        sudo apt-get install certbot
    fi
fi

# 创建证书目录
mkdir -p ~/.cloudflared/certs

# 获取SSL证书
echo "🔑 获取SSL证书..."
sudo certbot certonly --standalone -d shenyiqing.xin --email your-email@example.com --agree-tos --non-interactive

# 复制证书到cloudflared目录
echo "📋 复制证书文件..."
sudo cp /etc/letsencrypt/live/shenyiqing.xin/fullchain.pem ~/.cloudflared/certs/cert.pem
sudo cp /etc/letsencrypt/live/shenyiqing.xin/privkey.pem ~/.cloudflared/certs/key.pem

# 设置权限
chmod 600 ~/.cloudflared/certs/cert.pem
chmod 600 ~/.cloudflared/certs/key.pem

echo "✅ SSL证书配置完成！"
echo "📁 证书位置: ~/.cloudflared/certs/"
echo "🔗 现在可以使用: https://shenyiqing.xin/"
