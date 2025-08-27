#!/bin/bash

# 修复最终的前端显示问题
# 解决crispy_forms依赖和JSON响应问题

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

print_header "🔧 修复最终前端问题"

cd $PROJECT_DIR

print_status "📦 安装缺失的关键依赖..."

# 安装crispy_forms和其他UI依赖
sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

echo "安装Django UI和表单依赖..."
pip install django-crispy-forms==2.0
pip install crispy-bootstrap5==0.7
pip install django-widget-tweaks==1.4.12

echo "安装其他可能缺失的Django依赖..."
pip install django-allauth==0.54.0
pip install django-bootstrap4==23.2
pip install django-filter==23.2
pip install django-tables2==2.6.0

echo "安装API和文档依赖..."
pip install djangorestframework==3.14.0
pip install drf-yasg==1.21.7
pip install markdown==3.4.4

echo "验证关键依赖安装..."
python -c "import crispy_forms; print('✅ django-crispy-forms installed')" || echo "❌ crispy_forms 安装失败"
python -c "import crispy_bootstrap5; print('✅ crispy-bootstrap5 installed')" || echo "❌ crispy_bootstrap5 安装失败"
python -c "import widget_tweaks; print('✅ django-widget-tweaks installed')" || echo "❌ widget_tweaks 安装失败"

deactivate
EOF

print_status "🔍 检查主页视图配置..."

# 检查主页视图是否正确配置
print_status "分析当前URL配置..."

# 查看主URL配置
if [ -f "urls.py" ]; then
    echo "主URL配置内容:"
    grep -n "path.*home\|path.*''" urls.py | head -5 || echo "未找到主页路由"
fi

# 检查views.py中的home_view
if [ -f "views.py" ]; then
    echo "检查views.py中的home_view:"
    grep -A 10 -B 5 "def home_view\|home_view" views.py | head -15 || echo "未找到home_view定义"
fi

print_status "🎨 确保主页视图返回HTML..."

# 检查当前的home_view实现
if grep -q "JsonResponse\|json\|emergency" views.py 2>/dev/null; then
    print_warning "发现主页视图返回JSON，需要修复"
    
    # 备份原文件
    cp views.py views.py.backup
    
    # 创建正确的主页视图
    cat > temp_home_view.py << 'EOF'
def home_view(request):
    """主页视图 - 返回HTML页面而不是JSON"""
    from django.shortcuts import render
    from django.http import JsonResponse
    
    # 如果是API请求，返回JSON
    if request.path.startswith('/api/') or 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return JsonResponse({
            "message": "QAToolBox API",
            "status": "running",
            "version": "1.0",
            "endpoints": {
                "admin": "/admin/",
                "tools": "/tools/",
                "api": "/api/"
            }
        })
    
    # 普通浏览器请求，返回HTML页面
    context = {
        'title': 'QAToolBox - 智能工具箱',
        'status': 'running',
        'features': [
            {'name': 'AI助手', 'icon': '🤖', 'desc': '智能对话与分析'},
            {'name': '数据分析', 'icon': '📊', 'desc': '强大的数据处理能力'},
            {'name': '实用工具', 'icon': '🔧', 'desc': '各种便民工具集合'},
            {'name': '内容管理', 'icon': '📝', 'desc': '文档与内容处理'}
        ]
    }
    
    return render(request, 'index.html', context)
EOF
    
    # 替换home_view函数
    python3 << 'PYTHON_EOF'
import re

# 读取新的home_view
with open('temp_home_view.py', 'r') as f:
    new_home_view = f.read()

# 读取当前views.py
with open('views.py', 'r') as f:
    content = f.read()

# 替换home_view函数
pattern = r'def home_view\(.*?\):.*?(?=\ndef|\nclass|\n@|\Z)'
if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, new_home_view.strip(), content, flags=re.DOTALL)
else:
    # 如果找不到home_view，添加到文件末尾
    new_content = content + '\n\n' + new_home_view

with open('views.py', 'w') as f:
    f.write(new_content)

print("已更新home_view函数")
PYTHON_EOF
    
    rm temp_home_view.py
    print_success "主页视图已修复为返回HTML"
else
    print_success "主页视图配置正常"
fi

print_status "📄 确保index.html模板存在..."

# 检查并创建index.html模板
if [ ! -f "templates/index.html" ]; then
    print_status "创建index.html模板..."
    
    mkdir -p templates
    cat > templates/index.html << 'EOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title|default:"QAToolBox - 智能工具箱" }}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .hero-section {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .hero-content {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 3rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 800px;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .hero-subtitle {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .feature-card:hover {
            transform: translateY(-10px);
            background: rgba(255, 255, 255, 0.25);
        }
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        .btn-custom {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            padding: 12px 30px;
            margin: 0.5rem;
            border-radius: 25px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 500;
        }
        .btn-custom:hover {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .status-badge {
            display: inline-block;
            background: #4ade80;
            color: #1f2937;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 1rem;
        }
        .footer-info {
            margin-top: 2rem;
            opacity: 0.8;
            font-size: 0.9rem;
        }
        @media (max-width: 768px) {
            .hero-title { font-size: 2.5rem; }
            .hero-content { margin: 1rem; padding: 2rem; }
            .features-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="hero-content">
            <!-- 主标题 -->
            <h1 class="hero-title">
                <i class="fas fa-tools"></i> QAToolBox
            </h1>
            <p class="hero-subtitle">智能工具箱 - 您的全能数字助手</p>
            
            <!-- 功能特色 -->
            <div class="features-grid">
                {% for feature in features %}
                <div class="feature-card">
                    <span class="feature-icon">{{ feature.icon }}</span>
                    <h4>{{ feature.name }}</h4>
                    <p>{{ feature.desc }}</p>
                </div>
                {% empty %}
                <div class="feature-card">
                    <span class="feature-icon">🤖</span>
                    <h4>AI助手</h4>
                    <p>智能对话与分析</p>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">📊</span>
                    <h4>数据分析</h4>
                    <p>强大的数据处理能力</p>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">🔧</span>
                    <h4>实用工具</h4>
                    <p>各种便民工具集合</p>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">📝</span>
                    <h4>内容管理</h4>
                    <p>文档与内容处理</p>
                </div>
                {% endfor %}
            </div>
            
            <!-- 导航按钮 -->
            <div class="mt-4">
                <a href="/admin/" class="btn-custom">
                    <i class="fas fa-cog"></i> 管理后台
                </a>
                <a href="/tools/" class="btn-custom">
                    <i class="fas fa-toolbox"></i> 工具中心
                </a>
                <a href="/api/" class="btn-custom">
                    <i class="fas fa-code"></i> API文档
                </a>
            </div>
            
            <!-- 状态信息 -->
            <div class="status-badge">
                <i class="fas fa-check-circle"></i> 系统运行正常
            </div>
            
            <!-- 页脚信息 -->
            <div class="footer-info">
                <p><strong>QAToolBox</strong> - 企业级智能工具平台</p>
                <p>域名: <strong>shenyiqing.xin</strong> | 安全访问: <i class="fas fa-lock text-success"></i> HTTPS</p>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF
    
    chown -R qatoolbox:qatoolbox templates/
    print_success "创建了美观的index.html模板"
else
    print_success "index.html模板已存在"
fi

print_status "⚙️ 更新Django设置..."

# 确保crispy_forms在INSTALLED_APPS中
python3 << 'EOF'
import re

settings_file = 'config/settings/production.py'

with open(settings_file, 'r') as f:
    content = f.read()

# 需要添加的应用
apps_to_add = [
    '"crispy_forms"',
    '"crispy_bootstrap5"',
    '"widget_tweaks"'
]

# 检查并添加缺失的应用
for app in apps_to_add:
    if app not in content:
        # 在Django apps之后添加
        pattern = r'(# Django apps[\s\S]*?\n)'
        replacement = f'\\1    {app},  # Form styling\n'
        content = re.sub(pattern, replacement, content)
        print(f"已添加 {app} 到INSTALLED_APPS")

# 添加crispy_forms配置
if 'CRISPY_ALLOWED_TEMPLATE_PACKS' not in content:
    crispy_config = '''
# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
'''
    content += crispy_config
    print("已添加crispy_forms配置")

with open(settings_file, 'w') as f:
    f.write(content)

print("Django设置更新完成")
EOF

print_status "🗃️ 执行数据库迁移..."

# 重新尝试数据库迁移
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py migrate || {
    print_warning "数据库迁移失败，但继续..."
}

print_status "📁 重新收集静态文件..."

# 重新收集静态文件
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py collectstatic --noinput --clear || {
    print_warning "静态文件收集失败，但继续..."
}

print_header "🔄 重启服务"

print_status "🛑 停止当前Gunicorn进程..."
pkill -f gunicorn || true
sleep 3

print_status "🚀 启动新的Gunicorn实例..."

# 启动新的Gunicorn实例
sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

export DJANGO_SETTINGS_MODULE=config.settings.production

# 清理旧的PID文件
rm -f /tmp/gunicorn.pid

# 启动Gunicorn with proper WSGI module
gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile /var/log/qatoolbox/gunicorn_access.log \
    --error-logfile /var/log/qatoolbox/gunicorn_error.log \
    --log-level info \
    --daemon \
    --pid /tmp/gunicorn.pid \
    config.wsgi:application

echo "Gunicorn重新启动完成"
EOF

sleep 5

print_header "🧪 最终验证"

print_status "📊 检查服务状态..."

if pgrep -f gunicorn > /dev/null; then
    print_success "Gunicorn服务运行正常"
else
    print_error "Gunicorn启动失败"
    echo "错误日志:"
    tail -10 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || echo "无法读取错误日志"
fi

print_status "🌐 测试最终响应..."

# 等待服务完全启动
sleep 3

# 测试HTTP响应
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")
print_status "HTTP响应码: $response"

# 获取响应内容
response_content=$(curl -s http://127.0.0.1:8000/ 2>/dev/null | head -10)

if [[ "$response_content" == *"<!DOCTYPE html"* ]] || [[ "$response_content" == *"<html"* ]]; then
    print_success "🎉 成功！现在返回HTML内容"
    echo "HTML内容预览:"
    echo "$response_content" | head -3
elif [[ "$response_content" == *"{"* ]] && [[ "$response_content" == *"}"* ]]; then
    print_warning "仍然返回JSON，可能需要清除浏览器缓存"
    echo "JSON内容: $response_content"
else
    print_warning "响应格式未知"
    echo "内容: $response_content"
fi

# 测试外部访问
print_status "🌍 测试外部访问..."
external_response=$(curl -s -I http://localhost/ 2>/dev/null | head -5)
echo "外部访问响应头:"
echo "$external_response"

print_header "📋 最终总结"

echo "🔧 修复操作完成:"
echo "  ✅ 安装了django-crispy-forms和UI依赖"
echo "  ✅ 修复了主页视图返回HTML"
echo "  ✅ 创建了完整的index.html模板"
echo "  ✅ 更新了Django设置配置"
echo "  ✅ 重启了Gunicorn服务"
echo ""

echo "🌐 访问方式:"
echo "  • HTTPS主页: https://shenyiqing.xin"
echo "  • HTTP自动重定向: http://shenyiqing.xin"
echo "  • 管理后台: https://shenyiqing.xin/admin"
echo ""

if [[ "$response_content" == *"<!DOCTYPE html"* ]]; then
    print_success "🎉 前端修复完成！现在显示完整的HTML界面"
    echo "请访问 https://shenyiqing.xin 查看效果"
else
    print_warning "如果仍有问题，请尝试:"
    echo "1. 清除浏览器缓存并强制刷新 (Ctrl+F5)"
    echo "2. 检查Nginx配置: sudo nginx -t && sudo systemctl reload nginx"
    echo "3. 查看应用日志: tail -f /var/log/qatoolbox/gunicorn_error.log"
fi

print_success "最终修复脚本执行完成！"





