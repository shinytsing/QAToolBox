#!/bin/bash

# 修复certbot SSL证书安装问题
# 解决 _cffi_backend 模块缺失和依赖冲突

set -e

print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_header() {
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
    echo -e "\033[1;35m$1\033[0m"
    echo -e "\033[1;35m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
}

print_header "🔒 修复SSL证书安装问题"

print_status "🔍 诊断当前问题..."
python3 -c "import _cffi_backend" 2>/dev/null && print_success "cffi后端正常" || print_warning "cffi后端缺失"

print_header "方案1: 修复系统certbot"

print_status "🔧 修复Python依赖..."
# 修复cffi依赖
apt update
apt install -y python3-cffi libffi-dev python3-dev

# 重新安装cryptography相关包
apt install -y --reinstall python3-cryptography python3-openssl

# 修复可能的包冲突
apt install -y --fix-broken

print_status "🧹 清理certbot缓存..."
apt remove --purge certbot python3-certbot-nginx -y || true
apt autoremove -y
apt autoclean

print_status "📦 重新安装certbot..."
apt update
apt install -y certbot python3-certbot-nginx

print_status "🔍 测试certbot..."
if certbot --version; then
    print_success "certbot修复成功！"
    
    print_status "🔒 开始SSL证书申请..."
    print_warning "请确保域名 shenyiqing.xin 已正确解析到 47.103.143.152"
    
    # 申请SSL证书
    certbot --nginx -d shenyiqing.xin --non-interactive --agree-tos --email admin@shenyiqing.xin || {
        print_error "SSL证书申请失败，可能原因:"
        echo "1. 域名解析问题"
        echo "2. 防火墙阻止443端口"
        echo "3. Let's Encrypt速率限制"
        
        print_status "🔧 手动验证域名解析..."
        nslookup shenyiqing.xin
        
        print_status "🔧 检查80/443端口..."
        netstat -tlnp | grep -E ":(80|443)"
    }
else
    print_warning "系统certbot仍有问题，尝试方案2..."
    
    print_header "方案2: 使用Snap安装certbot"
    
    print_status "📦 安装snap版本的certbot..."
    apt remove --purge certbot python3-certbot-nginx -y || true
    
    # 安装snap版certbot
    snap install core; snap refresh core
    snap install --classic certbot
    
    # 创建符号链接
    ln -sf /snap/bin/certbot /usr/bin/certbot
    
    print_status "🔍 测试snap certbot..."
    if /snap/bin/certbot --version; then
        print_success "snap certbot安装成功！"
        
        print_status "🔒 使用snap certbot申请SSL证书..."
        /snap/bin/certbot --nginx -d shenyiqing.xin --non-interactive --agree-tos --email admin@shenyiqing.xin || {
            print_error "SSL证书申请失败"
            print_status "🔧 手动申请SSL证书..."
            echo "执行以下命令手动申请:"
            echo "/snap/bin/certbot --nginx -d shenyiqing.xin"
        }
    else
        print_header "方案3: 手动配置SSL"
        
        print_status "🔧 创建自签名证书（临时方案）..."
        mkdir -p /etc/ssl/private
        
        # 生成自签名证书
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout /etc/ssl/private/shenyiqing.xin.key \
            -out /etc/ssl/certs/shenyiqing.xin.crt \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/CN=shenyiqing.xin"
        
        # 更新Nginx配置支持HTTPS
        cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
upstream qatoolbox_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    return 301 https://$server_name$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # SSL配置
    ssl_certificate /etc/ssl/certs/shenyiqing.xin.crt;
    ssl_certificate_key /etc/ssl/private/shenyiqing.xin.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    client_max_body_size 100M;
    
    # favicon处理
    location = /favicon.ico {
        alias /home/qatoolbox/QAToolbox/static/favicon.ico;
        expires 1y;
        access_log off;
    }
    
    # 静态文件
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 媒体文件
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # 主应用
    location / {
        proxy_pass http://qatoolbox_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF
        
        # 重新加载Nginx
        nginx -t && systemctl reload nginx
        
        print_success "自签名SSL证书配置完成！"
        print_warning "这是临时方案，浏览器会显示安全警告"
    fi
fi

print_header "🔍 验证SSL配置"

print_status "📊 检查SSL端口..."
netstat -tlnp | grep ":443" && print_success "443端口正在监听" || print_warning "443端口未监听"

print_status "🌐 测试HTTPS访问..."
curl -k -I https://shenyiqing.xin/ 2>/dev/null && print_success "HTTPS访问正常" || print_warning "HTTPS访问失败"

print_header "📋 SSL配置总结"

echo "🔒 SSL配置状态:"
echo "• HTTP访问: http://shenyiqing.xin"
echo "• HTTPS访问: https://shenyiqing.xin"
echo "• 管理后台: https://shenyiqing.xin/admin"
echo ""

if [ -f "/etc/letsencrypt/live/shenyiqing.xin/fullchain.pem" ]; then
    print_success "✅ Let's Encrypt SSL证书配置成功"
    echo "证书有效期: $(openssl x509 -in /etc/letsencrypt/live/shenyiqing.xin/cert.pem -noout -dates)"
elif [ -f "/etc/ssl/certs/shenyiqing.xin.crt" ]; then
    print_warning "⚠️ 使用自签名证书（临时方案）"
    echo "建议申请正式的Let's Encrypt证书"
else
    print_error "❌ SSL证书未配置成功"
fi

print_success "SSL修复脚本执行完成！"






