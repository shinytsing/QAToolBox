#!/bin/bash

# QAToolBox 前端页面问题诊断脚本

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

print_header "🔍 QAToolBox 前端页面问题诊断"

# ================================
# [1] 基础连接测试
# ================================
print_header "[1] 基础连接测试"

print_status "🌐 测试本地连接..."
echo "测试 localhost:80:"
curl -I http://localhost/ 2>/dev/null || echo "❌ localhost:80 连接失败"

echo ""
echo "测试 localhost:8000:"
curl -I http://localhost:8000/ 2>/dev/null || echo "❌ localhost:8000 连接失败"

echo ""
echo "测试外部域名:"
curl -I http://shenyiqing.xin/ 2>/dev/null || echo "❌ 外部域名连接失败"

# ================================
# [2] 服务状态检查
# ================================
print_header "[2] 服务状态检查"

print_status "📊 系统服务状态:"
echo "Nginx: $(systemctl is-active nginx)"
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Redis: $(systemctl is-active redis-server)"
echo "Supervisor: $(systemctl is-active supervisor)"

print_status "📊 Django应用状态:"
supervisorctl status

# ================================
# [3] 端口监听检查
# ================================
print_header "[3] 端口监听检查"

print_status "🔌 检查端口监听:"
echo "端口 80 (Nginx):"
netstat -tlnp | grep ":80 " || echo "❌ 端口80未监听"

echo ""
echo "端口 8000 (Django):"
netstat -tlnp | grep ":8000 " || echo "❌ 端口8000未监听"

echo ""
echo "端口 5432 (PostgreSQL):"
netstat -tlnp | grep ":5432 " || echo "✅ PostgreSQL正常"

echo ""
echo "端口 6379 (Redis):"
netstat -tlnp | grep ":6379 " || echo "✅ Redis正常"

# ================================
# [4] Nginx配置检查
# ================================
print_header "[4] Nginx配置检查"

print_status "🌐 Nginx配置测试:"
nginx -t

print_status "📄 Nginx配置文件:"
if [ -f "/etc/nginx/sites-enabled/qatoolbox" ]; then
    echo "✅ QAToolBox站点配置存在"
    echo "配置文件位置: /etc/nginx/sites-enabled/qatoolbox"
else
    echo "❌ QAToolBox站点配置不存在"
fi

print_status "📋 Nginx错误日志:"
if [ -f "/var/log/nginx/error.log" ]; then
    echo "最新错误日志:"
    tail -10 /var/log/nginx/error.log
else
    echo "无错误日志文件"
fi

# ================================
# [5] Django应用检查
# ================================
print_header "[5] Django应用检查"

print_status "🐍 Django应用日志:"
if [ -f "/var/log/qatoolbox/supervisor.log" ]; then
    echo "最新应用日志:"
    tail -20 /var/log/qatoolbox/supervisor.log
elif [ -f "/home/qatoolbox/logs/supervisor.log" ]; then
    echo "最新应用日志:"
    tail -20 /home/qatoolbox/logs/supervisor.log
else
    echo "❌ 找不到Django应用日志"
fi

print_status "🔧 Gunicorn进程检查:"
ps aux | grep gunicorn || echo "❌ 没有发现Gunicorn进程"

# ================================
# [6] Django配置检查
# ================================
print_header "[6] Django配置检查"

if [ -d "/home/qatoolbox/QAToolbox" ]; then
    cd /home/qatoolbox/QAToolbox
    
    print_status "📁 Django项目文件:"
    echo "manage.py: $([ -f manage.py ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "urls.py: $([ -f urls.py ] && echo '✅ 存在' || echo '❌ 不存在')"
    echo "wsgi.py: $([ -f wsgi.py ] && echo '✅ 存在' || echo '❌ 不存在')"
    
    print_status "⚙️ 虚拟环境:"
    echo "虚拟环境: $([ -d .venv ] && echo '✅ 存在' || echo '❌ 不存在')"
    
    if [ -d .venv ]; then
        print_status "🐍 测试Django启动:"
        echo "测试Django配置:"
        sudo -u qatoolbox .venv/bin/python manage.py check --deploy 2>&1 | head -10
    fi
    
    print_status "📁 静态文件:"
    echo "staticfiles目录: $([ -d staticfiles ] && echo '✅ 存在' || echo '❌ 不存在')"
    if [ -d staticfiles ]; then
        echo "静态文件数量: $(find staticfiles -type f | wc -l)"
    fi
else
    echo "❌ Django项目目录不存在"
fi

# ================================
# [7] 网络和DNS检查
# ================================
print_header "[7] 网络和DNS检查"

print_status "🌍 DNS解析检查:"
echo "shenyiqing.xin 解析到:"
nslookup shenyiqing.xin | grep "Address:" | tail -1 || echo "❌ DNS解析失败"

print_status "🔧 防火墙状态:"
ufw status

# ================================
# [8] 生成修复建议
# ================================
print_header "[8] 自动修复建议"

print_status "🔧 生成修复脚本..."

cat > /tmp/fix_frontend.sh << 'EOF'
#!/bin/bash
# 自动修复前端问题

echo "🚀 开始修复前端问题..."

# 重启Nginx
echo "🌐 重启Nginx..."
systemctl restart nginx

# 检查Django是否运行
if ! pgrep -f gunicorn > /dev/null; then
    echo "🐍 启动Django应用..."
    cd /home/qatoolbox/QAToolbox
    
    # 检查虚拟环境
    if [ ! -d .venv ]; then
        echo "📦 重建虚拟环境..."
        sudo -u qatoolbox python3 -m venv .venv
        sudo -u qatoolbox .venv/bin/pip install gunicorn django
    fi
    
    # 启动Django
    supervisorctl restart qatoolbox
fi

# 检查Nginx配置
if [ ! -f /etc/nginx/sites-enabled/qatoolbox ]; then
    echo "⚙️ 重建Nginx配置..."
    cat > /etc/nginx/sites-available/qatoolbox << 'NGINXEOF'
upstream qatoolbox_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 1y;
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 1y;
    }
    
    location / {
        proxy_pass http://qatoolbox_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINXEOF
    
    ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
fi

# 最终测试
echo "🔍 测试结果:"
curl -I http://localhost/ 2>/dev/null && echo "✅ 本地访问正常" || echo "❌ 本地访问失败"
curl -I http://shenyiqing.xin/ 2>/dev/null && echo "✅ 外部访问正常" || echo "❌ 外部访问失败"

echo "✅ 修复完成"
EOF

chmod +x /tmp/fix_frontend.sh

print_success "🎯 诊断完成！"

echo ""
echo "📋 修复建议:"
echo "1. 查看上述诊断结果，找出问题所在"
echo "2. 执行自动修复: sudo bash /tmp/fix_frontend.sh"
echo "3. 如果仍有问题，手动检查日志文件"
echo ""
echo "🌐 应该能访问的地址:"
echo "• http://shenyiqing.xin"
echo "• http://47.103.143.152"
echo "• http://shenyiqing.xin/admin"

print_warning "如果诊断发现问题，请执行: sudo bash /tmp/fix_frontend.sh"
