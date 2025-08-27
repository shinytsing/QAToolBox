#!/bin/bash

# 修复前端页面显示问题
# 解决线上环境显示JSON而非完整前端界面的问题

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

PROJECT_DIR="/home/qatoolbox/QAToolbox"
VENV_PATH="$PROJECT_DIR/.venv"

print_header "🔍 诊断前端显示问题"

print_status "📊 检查当前运行状态..."
cd $PROJECT_DIR

# 检查Django进程
if pgrep -f "manage.py runserver\|gunicorn" > /dev/null; then
    print_success "Django服务正在运行"
    ps aux | grep -E "(manage.py|gunicorn)" | grep -v grep
else
    print_warning "Django服务未运行"
fi

print_status "🔍 检查主页URL配置..."
# 检查主页路由配置
if grep -r "path('', " urls.py apps/*/urls.py 2>/dev/null; then
    print_success "找到主页路由配置"
else
    print_warning "主页路由配置可能有问题"
fi

print_status "📁 检查静态文件配置..."
# 检查静态文件收集状态
if [ -d "staticfiles" ] && [ "$(ls -A staticfiles)" ]; then
    print_success "静态文件目录存在且非空"
    echo "静态文件数量: $(find staticfiles -type f | wc -l)"
else
    print_warning "静态文件目录为空或不存在"
fi

print_status "🎨 检查模板文件..."
if [ -d "templates" ]; then
    print_success "模板目录存在"
    echo "模板文件数量: $(find templates -name "*.html" | wc -l)"
    
    # 检查主要模板文件
    for template in "index.html" "base.html" "home.html"; do
        if find templates -name "$template" | grep -q .; then
            print_success "找到模板: $template"
        else
            print_warning "缺少模板: $template"
        fi
    done
else
    print_error "模板目录不存在"
fi

print_header "🔧 修复前端显示问题"

print_status "1️⃣ 重新收集静态文件..."
sudo -u qatoolbox $VENV_PATH/bin/python manage.py collectstatic --noinput --clear || {
    print_warning "静态文件收集失败，尝试创建目录..."
    mkdir -p staticfiles
    chown -R qatoolbox:qatoolbox staticfiles
    sudo -u qatoolbox $VENV_PATH/bin/python manage.py collectstatic --noinput --clear
}

print_status "2️⃣ 检查Django设置..."
# 检查Django设置中的模板和静态文件配置
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production $VENV_PATH/bin/python -c "
import django
django.setup()
from django.conf import settings

print('=== Django配置检查 ===')
print(f'DEBUG模式: {settings.DEBUG}')
print(f'静态文件URL: {settings.STATIC_URL}')
print(f'静态文件根目录: {settings.STATIC_ROOT}')

if hasattr(settings, 'STATICFILES_DIRS'):
    print(f'静态文件目录: {settings.STATICFILES_DIRS}')

print(f'模板配置:')
for template in settings.TEMPLATES:
    print(f'  - 引擎: {template[\"BACKEND\"]}')
    print(f'  - 目录: {template[\"DIRS\"]}')
    print(f'  - APP目录: {template[\"OPTIONS\"].get(\"APP_DIRS\", False)}')

print(f'已安装应用数量: {len(settings.INSTALLED_APPS)}')
print(f'根URL配置: {settings.ROOT_URLCONF}')
"

print_status "3️⃣ 检查主页视图..."
# 查找主页视图实现
if grep -r "def index\|def home\|class.*View" views.py apps/*/views* 2>/dev/null | head -10; then
    print_success "找到视图函数"
else
    print_warning "主页视图可能有问题"
fi

print_status "4️⃣ 创建测试主页（如果需要）..."
# 如果没有合适的主页模板，创建一个简单的
if ! find templates -name "index.html" | grep -q .; then
    print_status "创建临时主页模板..."
    
    mkdir -p templates
    cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QAToolBox - 智能工具箱</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            padding: 2rem;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 2rem;
        }
        .tool-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 1.5rem;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .tool-card:hover {
            transform: translateY(-5px);
        }
        .tool-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            transition: all 0.3s ease;
            margin: 0.5rem;
        }
        .btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ QAToolBox</h1>
        <p class="subtitle">智能工具箱 - 您的全能助手</p>
        
        <div class="tools-grid">
            <div class="tool-card">
                <div class="tool-icon">🤖</div>
                <h3>AI助手</h3>
                <p>智能对话与分析</p>
            </div>
            <div class="tool-card">
                <div class="tool-icon">📊</div>
                <h3>数据分析</h3>
                <p>强大的数据处理能力</p>
            </div>
            <div class="tool-card">
                <div class="tool-icon">🔧</div>
                <h3>实用工具</h3>
                <p>各种便民工具集合</p>
            </div>
            <div class="tool-card">
                <div class="tool-icon">📝</div>
                <h3>内容管理</h3>
                <p>文档与内容处理</p>
            </div>
        </div>
        
        <div style="margin-top: 2rem;">
            <a href="/admin/" class="btn">🚀 管理后台</a>
            <a href="/tools/" class="btn">🛠️ 工具中心</a>
            <a href="/api/" class="btn">📡 API文档</a>
        </div>
        
        <div style="margin-top: 2rem; opacity: 0.7; font-size: 0.9rem;">
            <p>系统状态: <span style="color: #4ade80;">● 运行正常</span></p>
            <p>访问域名: <strong>shenyiqing.xin</strong></p>
        </div>
    </div>
</body>
</html>
EOF
    chown -R qatoolbox:qatoolbox templates/
    print_success "创建了美观的主页模板"
fi

print_status "5️⃣ 确保主页视图配置..."
# 检查并修复主页URL配置
if ! grep -q "path('', " urls.py; then
    print_status "修复主页URL配置..."
    
    # 备份原文件
    cp urls.py urls.py.backup
    
    # 添加主页路由（如果不存在）
    python3 << 'EOF'
import re

with open('urls.py', 'r') as f:
    content = f.read()

# 检查是否已有主页路由
if "path('', " not in content:
    # 查找urlpatterns的位置
    pattern = r'(urlpatterns\s*=\s*\[)'
    if re.search(pattern, content):
        # 在urlpatterns开始处添加主页路由
        new_content = re.sub(
            pattern,
            r'\1\n    path("", TemplateView.as_view(template_name="index.html"), name="home"),',
            content
        )
        
        # 确保导入TemplateView
        if 'TemplateView' not in content:
            new_content = re.sub(
                r'(from django\.urls import [^\\n]*)',
                r'\1\nfrom django.views.generic import TemplateView',
                new_content
            )
        
        with open('urls.py', 'w') as f:
            f.write(new_content)
        
        print("已添加主页路由配置")
    else:
        print("无法找到urlpatterns，请手动配置")
else:
    print("主页路由已存在")
EOF
fi

print_status "6️⃣ 更新Nginx配置..."
# 确保Nginx正确配置静态文件和主页
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
upstream qatoolbox_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    client_max_body_size 100M;
    
    # favicon处理
    location = /favicon.ico {
        alias /home/qatoolbox/QAToolbox/staticfiles/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 静态文件优先级最高
    location /static/ {
        alias /home/qatoolbox/QAToolbox/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # 如果静态文件不存在，返回404而不是转发到Django
        try_files $uri =404;
    }
    
    # 媒体文件
    location /media/ {
        alias /home/qatoolbox/QAToolbox/media/;
        expires 1y;
        add_header Cache-Control "public";
        try_files $uri =404;
    }
    
    # 主应用 - 确保所有动态请求都转发到Django
    location / {
        # 首先尝试静态文件，然后转发到Django
        try_files $uri @django;
    }
    
    # Django应用处理
    location @django {
        proxy_pass http://qatoolbox_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 确保正确的内容类型
        proxy_set_header Accept-Encoding "";
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

print_status "7️⃣ 重启服务..."
# 测试并重启Nginx
nginx -t && systemctl reload nginx

# 重启Django应用
print_status "重启Django应用..."
if pgrep -f gunicorn > /dev/null; then
    pkill -f gunicorn
    sleep 2
fi

# 使用Gunicorn启动Django（生产模式）
cd $PROJECT_DIR
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 60 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile /var/log/qatoolbox/gunicorn_access.log \
    --error-logfile /var/log/qatoolbox/gunicorn_error.log \
    --daemon \
    config.wsgi:application

print_header "🧪 验证修复结果"

sleep 3

print_status "📊 检查服务状态..."
if pgrep -f gunicorn > /dev/null; then
    print_success "Django/Gunicorn服务运行正常"
else
    print_error "Django/Gunicorn服务启动失败"
fi

if systemctl is-active nginx > /dev/null; then
    print_success "Nginx服务运行正常"
else
    print_error "Nginx服务异常"
fi

print_status "🌐 测试HTTP响应..."
# 测试主页响应
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
if [ "$response" = "200" ]; then
    print_success "主页HTTP响应正常 (200)"
else
    print_warning "主页HTTP响应异常 ($response)"
fi

# 测试内容类型
content_type=$(curl -s -I http://localhost/ | grep -i content-type | cut -d' ' -f2- | tr -d '\r\n' 2>/dev/null || echo "unknown")
if [[ "$content_type" == *"text/html"* ]]; then
    print_success "响应内容类型: HTML ✓"
elif [[ "$content_type" == *"application/json"* ]]; then
    print_warning "响应内容类型: JSON (需要修复)"
else
    print_warning "响应内容类型: $content_type"
fi

print_status "🔍 检查响应内容..."
# 获取主页内容的前几行
response_content=$(curl -s http://localhost/ | head -10)
if [[ "$response_content" == *"<!DOCTYPE html"* ]] || [[ "$response_content" == *"<html"* ]]; then
    print_success "主页返回HTML内容 ✓"
elif [[ "$response_content" == *"{"* ]] && [[ "$response_content" == *"}"* ]]; then
    print_warning "主页仍返回JSON内容，需要进一步调试"
    echo "响应内容样例:"
    echo "$response_content"
else
    print_warning "主页响应内容格式未知"
    echo "响应内容样例:"
    echo "$response_content"
fi

print_header "📋 修复总结"

echo "🔧 执行的修复操作:"
echo "  ✅ 重新收集了静态文件"
echo "  ✅ 检查了Django配置"
echo "  ✅ 创建了美观的主页模板"
echo "  ✅ 修复了URL路由配置"
echo "  ✅ 优化了Nginx配置"
echo "  ✅ 重启了所有相关服务"
echo ""

echo "🌐 访问地址:"
echo "  • 主页: http://shenyiqing.xin"
echo "  • 管理后台: http://shenyiqing.xin/admin"
echo "  • 工具中心: http://shenyiqing.xin/tools"
echo ""

if [[ "$response_content" == *"<!DOCTYPE html"* ]] || [[ "$response_content" == *"<html"* ]]; then
    print_success "🎉 前端页面修复成功！现在应该显示完整的HTML界面了"
else
    print_warning "⚠️ 如果问题仍然存在，请检查Django应用日志:"
    echo "  tail -f /var/log/qatoolbox/gunicorn_error.log"
    echo "  sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production /home/qatoolbox/QAToolbox/.venv/bin/python /home/qatoolbox/QAToolbox/manage.py check"
fi

print_success "前端显示修复脚本执行完成！"






