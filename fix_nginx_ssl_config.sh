#!/bin/bash

# 修复Nginx SSL配置错误的脚本
# 用于 shenyiqing.xin 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始修复Nginx SSL配置...${NC}"

# 1. 首先生成SSL证书（如果不存在）
echo -e "${YELLOW}1. 检查并生成SSL证书...${NC}"
sudo mkdir -p /etc/ssl/certs /etc/ssl/private

if [ ! -f "/etc/ssl/certs/qatoolbox.crt" ] || [ ! -f "/etc/ssl/private/qatoolbox.key" ]; then
    echo "生成自签名SSL证书..."
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/qatoolbox.key \
        -out /etc/ssl/certs/qatoolbox.crt \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=QAToolBox/CN=shenyiqing.xin"
fi

# 2. 修复Nginx配置（使用正确的SSL指令）
echo -e "${YELLOW}2. 更新Nginx配置...${NC}"
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name shenyiqing.xin;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name shenyiqing.xin;

    # SSL配置 - 使用正确的指令名
    ssl_certificate /etc/ssl/certs/qatoolbox.crt;
    ssl_certificate_key /etc/ssl/private/qatoolbox.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    client_max_body_size 100M;
    
    # 静态文件配置 - 使用更宽松的权限配置
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        add_header Access-Control-Allow-Origin "*";
        
        # 允许所有用户访问静态文件
        location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Access-Control-Allow-Origin "*";
            access_log off;
            try_files $uri $uri/ =404;
        }
    }
    
    # 媒体文件配置
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
        expires 30d;
        add_header Access-Control-Allow-Origin "*";
    }
    
    # 主应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # 添加CORS头
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With" always;
    }
}
EOF

# 3. 设置SSL证书权限
echo -e "${YELLOW}3. 设置SSL证书权限...${NC}"
sudo chmod 644 /etc/ssl/certs/qatoolbox.crt
sudo chmod 600 /etc/ssl/private/qatoolbox.key
sudo chown root:root /etc/ssl/certs/qatoolbox.crt
sudo chown root:root /etc/ssl/private/qatoolbox.key

# 4. 再次设置静态文件权限
echo -e "${YELLOW}4. 重新设置静态文件权限...${NC}"
cd /home/qatoolbox/QAToolBox

# 重新收集静态文件
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput --clear --settings=config.settings.full_frontend

# 设置更宽松的权限让nginx可以访问
sudo chown -R qatoolbox:www-data /home/qatoolbox/QAToolBox/staticfiles/
sudo chmod -R 755 /home/qatoolbox/QAToolBox/staticfiles/
sudo find /home/qatoolbox/QAToolBox/staticfiles/ -type f -exec chmod 644 {} \;

# 确保nginx用户可以访问父目录
sudo chmod 755 /home/qatoolbox
sudo chmod 755 /home/qatoolbox/QAToolBox

# 5. 启用站点配置
echo -e "${YELLOW}5. 启用站点配置...${NC}"
sudo ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/

# 6. 测试Nginx配置
echo -e "${YELLOW}6. 测试Nginx配置...${NC}"
sudo nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Nginx配置测试通过${NC}"
else
    echo -e "${RED}Nginx配置测试失败${NC}"
    exit 1
fi

# 7. 重启Nginx
echo -e "${YELLOW}7. 重启Nginx...${NC}"
sudo systemctl restart nginx

# 8. 检查QAToolBox服务
echo -e "${YELLOW}8. 检查QAToolBox服务...${NC}"
sudo systemctl restart qatoolbox

# 9. 等待服务启动
sleep 5

# 10. 检查服务状态
echo -e "${YELLOW}9. 检查服务状态...${NC}"
echo "Nginx状态:"
sudo systemctl status nginx --no-pager -l | head -10

echo -e "\nQAToolBox服务状态:"
sudo systemctl status qatoolbox --no-pager -l | head -10

# 11. 测试静态文件访问
echo -e "${YELLOW}10. 测试静态文件访问...${NC}"
echo "测试HTTP重定向:"
curl -I http://shenyiqing.xin/ 2>/dev/null | head -2

echo -e "\n测试HTTPS主页:"
curl -I -k https://shenyiqing.xin/ 2>/dev/null | head -2

echo -e "\n测试CSS文件:"
curl -I -k https://shenyiqing.xin/static/geek.css 2>/dev/null | head -2

echo -e "\n测试JS文件:"
curl -I -k https://shenyiqing.xin/static/js/auth.js 2>/dev/null | head -2

# 12. 显示调试信息
echo -e "${YELLOW}11. 调试信息...${NC}"
echo "静态文件目录权限:"
ls -la /home/qatoolbox/QAToolBox/ | grep staticfiles

echo -e "\n静态文件示例："
ls -la /home/qatoolbox/QAToolBox/staticfiles/ | head -5

echo -e "\nNginx错误日志最后几行："
sudo tail -5 /var/log/nginx/error.log 2>/dev/null || echo "无错误日志"

echo -e "${GREEN}修复完成！${NC}"
echo -e "${BLUE}请访问 https://shenyiqing.xin 检查网站是否正常工作${NC}"
echo -e "${BLUE}如果还有静态文件问题，请检查:${NC}"
echo "  - sudo journalctl -u qatoolbox -f"
echo "  - sudo tail -f /var/log/nginx/error.log"
echo "  - ls -la /home/qatoolbox/QAToolBox/staticfiles/"
