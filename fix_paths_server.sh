#!/bin/bash
# =============================================================================
# 修复服务器路径脚本
# 将路径从 /home/qatoolbox/QAToolBox 改为 /home/admin/QAToolbox
# =============================================================================

set -e

echo "🔧 修复服务器路径配置..."

# 1. 更新部署脚本中的路径
echo "更新部署脚本路径..."
sed -i 's|/home/qatoolbox/QAToolBox|/home/admin/QAToolbox|g' deploy_gaojie_aliyun.sh
sed -i 's|/home/qatoolbox/QAToolBox|/home/admin/QAToolbox|g' quick_fix_server.sh
sed -i 's|/home/qatoolbox/QAToolBox|/home/admin/QAToolbox|g' ultimate_fix.sh

# 2. 更新Nginx配置中的路径
echo "更新Nginx配置路径..."
sed -i 's|/home/qatoolbox/QAToolBox|/home/admin/QAToolbox|g' nginx_simple.conf
sed -i 's|/home/qatoolbox/QAToolBox|/home/admin/QAToolbox|g' nginx_ultimate.conf

# 3. 创建正确的服务器文件结构展示脚本
echo "创建正确的服务器文件结构展示脚本..."
cat > show_server_structure_correct.sh << 'EOF'
#!/bin/bash
# =============================================================================
# 阿里云服务器文件结构展示脚本 - 正确路径版本
# 服务器路径: /home/admin/QAToolbox
# =============================================================================

echo "🔍 开始分析阿里云服务器文件结构..."

# 1. 显示项目根目录结构
echo "=== 项目根目录结构 ==="
ls -la /home/admin/QAToolbox/

echo ""
echo "=== 项目子目录结构 ==="
ls -la /home/admin/QAToolbox/apps/
ls -la /home/admin/QAToolbox/config/
ls -la /home/admin/QAToolbox/templates/
ls -la /home/admin/QAToolbox/static/

echo ""
echo "=== 用户应用结构 ==="
ls -la /home/admin/QAToolbox/apps/users/
ls -la /home/admin/QAToolbox/apps/tools/
ls -la /home/admin/QAToolbox/apps/content/

echo ""
echo "=== 配置文件 ==="
ls -la /home/admin/QAToolbox/config/settings/
ls -la /home/admin/QAToolbox/*.py | head -10

echo ""
echo "=== Nginx配置 ==="
echo "--- 主配置文件 ---"
cat /etc/nginx/nginx.conf

echo ""
echo "--- 站点配置 ---"
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/

echo ""
echo "--- QAToolBox站点配置 ---"
if [ -f "/etc/nginx/sites-available/qatoolbox" ]; then
    cat /etc/nginx/sites-available/qatoolbox
else
    echo "QAToolBox站点配置文件不存在"
fi

echo ""
echo "=== 服务状态 ==="
systemctl status nginx --no-pager
systemctl status postgresql --no-pager
systemctl status redis-server --no-pager
supervisorctl status qatoolbox

echo ""
echo "=== 日志文件 ==="
ls -la /var/log/qatoolbox/
ls -la /var/log/nginx/

echo ""
echo "=== 环境变量 ==="
if [ -f "/home/admin/QAToolbox/.env" ]; then
    echo "--- .env文件内容 ---"
    cat /home/admin/QAToolbox/.env
else
    echo ".env文件不存在"
fi

echo ""
echo "=== Python环境 ==="
ls -la /home/admin/QAToolbox/.venv/
which python3
python3 --version

echo ""
echo "=== 数据库状态 ==="
sudo -u postgres psql -c "\l" 2>/dev/null || echo "PostgreSQL连接失败"

echo ""
echo "=== 网络连接 ==="
netstat -tlnp | grep -E ':(80|443|5432|6379|8000)\s'

echo ""
echo "=== 磁盘使用 ==="
df -h

echo ""
echo "=== 内存使用 ==="
free -h

echo ""
echo "=== 最近的错误日志 ==="
echo "--- Gunicorn错误日志 ---"
tail -20 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || echo "无Gunicorn错误日志"

echo ""
echo "--- Nginx错误日志 ---"
tail -20 /var/log/nginx/error.log 2>/dev/null || echo "无Nginx错误日志"

echo ""
echo "=== 应用日志 ---"
tail -20 /var/log/qatoolbox/gunicorn.log 2>/dev/null || echo "无应用日志"

echo ""
echo "🔍 服务器结构分析完成！"
echo "请将以上输出内容发送给我，我会根据实际情况创建针对性的修复脚本。"
EOF

chmod +x show_server_structure_correct.sh

# 4. 创建正确的curl测试脚本
echo "创建正确的curl测试脚本..."
cat > test_curl_correct.sh << 'EOF'
#!/bin/bash
# 正确的curl测试脚本

echo "=== 基础连接测试 ==="
curl -I http://47.103.143.152/ 2>/dev/null | head -1
curl -I http://shenyiqing.xin/ 2>/dev/null | head -1

echo ""
echo "=== API端点测试 ==="
curl -I http://47.103.143.152/users/api/session-status/ 2>/dev/null | head -1
curl -I http://47.103.143.152/users/generate-progressive-captcha/ 2>/dev/null | head -1
curl -I http://47.103.143.152/users/theme/ 2>/dev/null | head -1

echo ""
echo "=== 路由测试 ==="
curl -I http://47.103.143.152/users/login/ 2>/dev/null | head -1
curl -I http://47.103.143.152/accounts/login/ 2>/dev/null | head -1

echo ""
echo "=== 静态文件测试 ==="
curl -I http://47.103.143.152/static/ 2>/dev/null | head -1
curl -I http://47.103.143.152/media/ 2>/dev/null | head -1

echo ""
echo "=== 健康检查 ==="
curl -I http://47.103.143.152/health/ 2>/dev/null | head -1

echo ""
echo "=== 详细API测试 ==="
echo "--- 会话状态API详细测试 ---"
curl -v http://47.103.143.152/users/api/session-status/ 2>&1 | head -20

echo ""
echo "--- 验证码API详细测试 ---"
curl -v http://47.103.143.152/users/generate-progressive-captcha/ 2>&1 | head -20
EOF

chmod +x test_curl_correct.sh

# 5. 创建正确的Nginx配置
echo "创建正确的Nginx配置..."
cat > nginx_correct.conf << 'EOF'
server {
    listen 80;
    server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CORS头 - 解决跨域问题
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken" always;
    add_header Access-Control-Allow-Credentials "true" always;
    
    # 处理预检请求
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken";
        add_header Access-Control-Allow-Credentials "true";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain; charset=utf-8";
        add_header Content-Length 0;
        return 204;
    }
    
    client_max_body_size 100M;
    
    # 静态文件
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 1M;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 1w;
        add_header Cache-Control "public";
        add_header Access-Control-Allow-Origin "*";
    }
    
    # 健康检查
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 添加CORS头
        add_header Access-Control-Allow-Origin "*" always;
        add_header Access-Control-Allow-Credentials "true" always;
    }
}
EOF

echo "✅ 路径修复完成！"
echo ""
echo "📋 现在在服务器上执行："
echo "1. 更新代码: git pull origin main"
echo "2. 执行文件结构展示: ./show_server_structure_correct.sh"
echo "3. 执行curl测试: ./test_curl_correct.sh"
echo "4. 更新Nginx配置: sudo cp nginx_correct.conf /etc/nginx/sites-available/qatoolbox"
