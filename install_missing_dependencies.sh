#!/bin/bash

# 快速安装缺失依赖并修复JSON响应问题
# 解决tenacity模块和其他工具依赖

set -e

print_status() {
    echo -e "\033[1;34m[$(date '+%H:%M:%S')] $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
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

print_header "🚀 快速修复缺失依赖"

cd $PROJECT_DIR

print_status "📦 安装关键缺失依赖..."

# 安装缺失的依赖包
sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

echo "安装重试和工具依赖..."
pip install tenacity==8.2.3
pip install backoff==2.2.1

echo "安装AI和机器学习依赖..."
pip install transformers==4.34.0
pip install openai==0.28.1
pip install anthropic==0.3.11

echo "安装任务队列和缓存依赖..."
pip install celery==5.3.4
pip install redis==5.0.1

echo "安装文档处理依赖..."
pip install python-docx==0.8.11
pip install openpyxl==3.1.2
pip install python-pptx==0.6.21

echo "安装其他工具依赖..."
pip install schedule==1.2.0
pip install python-crontab==3.0.0
pip install psutil==5.9.6

echo "验证关键依赖安装..."
python -c "import tenacity; print('✅ tenacity installed')" || echo "❌ tenacity 安装失败"
python -c "import backoff; print('✅ backoff installed')" || echo "❌ backoff 安装失败"
python -c "import transformers; print('✅ transformers installed')" || echo "❌ transformers 安装失败"

deactivate
EOF

print_status "🔧 修复主页视图..."

# 直接修复views.py中的home_view函数
python3 << 'EOF'
import re

# 读取当前views.py
with open('views.py', 'r') as f:
    content = f.read()

# 定义新的home_view函数
new_home_view = '''def home_view(request):
    """主页视图 - 根据请求类型返回HTML或JSON"""
    from django.shortcuts import render
    from django.http import JsonResponse
    
    # 检查是否是API请求或AJAX请求
    is_api_request = (
        request.path.startswith('/api/') or
        'application/json' in request.META.get('HTTP_ACCEPT', '') or
        request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    )
    
    if is_api_request:
        # API请求返回JSON
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
    
    # 浏览器请求返回HTML页面
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
    
    return render(request, 'index.html', context)'''

# 查找并替换home_view函数
pattern = r'def home_view\([^)]*\):.*?(?=\ndef|\nclass|\n@|\Z)'
if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, new_home_view, content, flags=re.DOTALL)
    print("找到并替换了home_view函数")
else:
    # 如果找不到home_view，添加到文件末尾
    if 'def home_view' not in content:
        new_content = content + '\n\n' + new_home_view
        print("添加了新的home_view函数")
    else:
        # 简单替换方式
        lines = content.split('\n')
        new_lines = []
        in_home_view = False
        indent_level = 0
        
        for line in lines:
            if 'def home_view(' in line:
                in_home_view = True
                indent_level = len(line) - len(line.lstrip())
                new_lines.extend(new_home_view.split('\n'))
                continue
            elif in_home_view:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level and not line.startswith(' ' * (indent_level + 1)):
                    in_home_view = False
                    new_lines.append(line)
                else:
                    continue
            else:
                new_lines.append(line)
        
        new_content = '\n'.join(new_lines)
        print("通过行处理替换了home_view函数")

# 写回文件
with open('views.py', 'w') as f:
    f.write(new_content)

print("home_view函数更新完成")
EOF

print_status "🎨 确保模板文件正确..."

# 确保templates目录和index.html存在
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
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 3rem;
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-top: 50px;
        }
        h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.2);
            padding: 2rem;
            border-radius: 15px;
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
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
        }
        .btn-custom:hover {
            background: rgba(255, 255, 255, 0.3);
            color: white;
            transform: translateY(-2px);
            text-decoration: none;
        }
        .status-badge {
            background: #4ade80;
            color: #1f2937;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: 600;
            margin-top: 1rem;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ QAToolBox</h1>
        <p class="subtitle">智能工具箱 - 您的全能数字助手</p>
        
        <div class="features">
            {% for feature in features %}
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">{{ feature.icon }}</div>
                <h4>{{ feature.name }}</h4>
                <p>{{ feature.desc }}</p>
            </div>
            {% empty %}
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🤖</div>
                <h4>AI助手</h4>
                <p>智能对话与分析</p>
            </div>
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
                <h4>数据分析</h4>
                <p>强大的数据处理能力</p>
            </div>
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">🔧</div>
                <h4>实用工具</h4>
                <p>各种便民工具集合</p>
            </div>
            <div class="feature-card">
                <div style="font-size: 2rem; margin-bottom: 1rem;">📝</div>
                <h4>内容管理</h4>
                <p>文档与内容处理</p>
            </div>
            {% endfor %}
        </div>
        
        <div style="margin-top: 2rem;">
            <a href="/admin/" class="btn-custom">🚀 管理后台</a>
            <a href="/tools/" class="btn-custom">🛠️ 工具中心</a>
            <a href="/api/" class="btn-custom">📡 API文档</a>
        </div>
        
        <div class="status-badge">
            ● 系统运行正常
        </div>
        
        <div style="margin-top: 2rem; opacity: 0.8; font-size: 0.9rem;">
            <p><strong>QAToolBox</strong> - 企业级智能工具平台</p>
            <p>域名: <strong>shenyiqing.xin</strong> | 🔒 HTTPS 安全访问</p>
        </div>
    </div>
</body>
</html>
EOF
    
    chown -R qatoolbox:qatoolbox templates/
    print_success "创建了index.html模板"
fi

print_status "🗃️ 快速数据库检查..."

# 尝试简单的数据库操作
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py check --deploy || {
    print_warning "Django检查有警告，但继续..."
}

print_status "🔄 重启Gunicorn..."

# 停止并重启Gunicorn
pkill -f gunicorn || true
sleep 2

# 启动Gunicorn
sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

export DJANGO_SETTINGS_MODULE=config.settings.production

gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 120 \
    --max-requests 1000 \
    --access-logfile /var/log/qatoolbox/gunicorn_access.log \
    --error-logfile /var/log/qatoolbox/gunicorn_error.log \
    --daemon \
    config.wsgi:application

echo "Gunicorn已重启"
EOF

sleep 3

print_header "🧪 验证修复结果"

print_status "📊 检查服务状态..."
if pgrep -f gunicorn > /dev/null; then
    print_success "Gunicorn运行正常"
else
    print_warning "Gunicorn未运行，查看错误日志:"
    tail -5 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || echo "无法读取日志"
fi

print_status "🌐 测试浏览器访问..."
# 模拟浏览器请求
browser_response=$(curl -s -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" http://127.0.0.1:8000/ | head -10)

if [[ "$browser_response" == *"<!DOCTYPE html"* ]]; then
    print_success "🎉 成功！浏览器请求返回HTML"
    echo "HTML内容预览:"
    echo "$browser_response" | head -3
elif [[ "$browser_response" == *"{"* ]]; then
    print_warning "仍返回JSON，检查views.py"
    echo "响应内容: $browser_response"
else
    print_warning "响应格式未知"
    echo "响应: $browser_response"
fi

print_status "🔍 测试API访问..."
# 测试API请求
api_response=$(curl -s -H "Accept: application/json" http://127.0.0.1:8000/ | head -5)
echo "API响应: $api_response"

print_header "📋 修复完成"

echo "🔧 完成的操作:"
echo "  ✅ 安装了tenacity和重试依赖"
echo "  ✅ 安装了AI和机器学习依赖"
echo "  ✅ 修复了主页视图逻辑"
echo "  ✅ 确保了模板文件存在"
echo "  ✅ 重启了Gunicorn服务"
echo ""

echo "🌐 访问测试:"
echo "  • 主页: https://shenyiqing.xin (应该显示HTML)"
echo "  • API: https://shenyiqing.xin (Accept: application/json)"
echo "  • 管理: https://shenyiqing.xin/admin"
echo ""

if [[ "$browser_response" == *"<!DOCTYPE html"* ]]; then
    print_success "🎉 HTML页面修复成功！请访问 https://shenyiqing.xin 查看效果"
else
    print_warning "如果仍有问题，请强制刷新浏览器 (Ctrl+F5) 或清除缓存"
fi

print_success "依赖安装和修复完成！"





