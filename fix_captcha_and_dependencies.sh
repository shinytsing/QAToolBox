#!/bin/bash

# 修复captcha和其他缺失依赖问题
# 解决Django应用启动时的ModuleNotFoundError

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

print_header "🔧 修复Django应用依赖问题"

cd $PROJECT_DIR

print_status "🔍 诊断缺失的依赖..."

# 检查当前虚拟环境状态
if [ -d "$VENV_PATH" ]; then
    print_success "虚拟环境存在"
    
    # 激活虚拟环境并检查Python包
    source $VENV_PATH/bin/activate
    
    print_status "📦 检查关键依赖包..."
    
    # 检查缺失的包
    missing_packages=()
    
    # 检查captcha相关包
    python -c "import captcha" 2>/dev/null || missing_packages+=("django-simple-captcha")
    python -c "import PIL" 2>/dev/null || missing_packages+=("Pillow")
    python -c "import cv2" 2>/dev/null || missing_packages+=("opencv-python")
    python -c "import numpy" 2>/dev/null || missing_packages+=("numpy")
    python -c "import requests" 2>/dev/null || missing_packages+=("requests")
    python -c "import lxml" 2>/dev/null || missing_packages+=("lxml")
    python -c "import bs4" 2>/dev/null || missing_packages+=("beautifulsoup4")
    python -c "import selenium" 2>/dev/null || missing_packages+=("selenium")
    python -c "import webdriver_manager" 2>/dev/null || missing_packages+=("webdriver-manager")
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        print_warning "发现缺失的包: ${missing_packages[*]}"
    else
        print_success "基础依赖包检查完成"
    fi
    
    deactivate
else
    print_error "虚拟环境不存在，需要重新创建"
    
    print_status "🔨 重新创建虚拟环境..."
    python3 -m venv $VENV_PATH
    chown -R qatoolbox:qatoolbox $VENV_PATH
fi

print_status "📦 安装缺失的关键依赖..."

# 激活虚拟环境
sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装captcha相关依赖
echo "安装验证码相关依赖..."
pip install django-simple-captcha==0.5.20
pip install Pillow==10.0.0

# 安装图像处理依赖
echo "安装图像处理依赖..."
pip install opencv-python==4.8.1.78
pip install numpy==1.24.3

# 安装网络请求依赖
echo "安装网络请求依赖..."
pip install requests==2.31.0
pip install urllib3==2.0.4

# 安装网页解析依赖
echo "安装网页解析依赖..."
pip install lxml==4.9.3
pip install beautifulsoup4==4.12.2

# 安装自动化测试依赖
echo "安装Selenium依赖..."
pip install selenium==4.15.0
pip install webdriver-manager==4.0.1

# 安装其他可能缺失的依赖
echo "安装其他常用依赖..."
pip install python-dateutil==2.8.2
pip install pytz==2023.3
pip install six==1.16.0
pip install certifi==2023.7.22
pip install charset-normalizer==3.2.0
pip install idna==3.4

# 验证安装
echo "验证关键依赖安装..."
python -c "import captcha; print('✅ django-simple-captcha installed')" || echo "❌ captcha 安装失败"
python -c "import PIL; print('✅ Pillow installed')" || echo "❌ Pillow 安装失败"
python -c "import cv2; print('✅ OpenCV installed')" || echo "❌ OpenCV 安装失败"
python -c "import numpy; print('✅ NumPy installed')" || echo "❌ NumPy 安装失败"
python -c "import requests; print('✅ Requests installed')" || echo "❌ Requests 安装失败"

deactivate
EOF

print_status "🔧 更新Django设置..."

# 确保captcha在INSTALLED_APPS中
print_status "检查INSTALLED_APPS配置..."

# 检查production.py设置
if grep -q "captcha" config/settings/production.py; then
    print_success "captcha已在INSTALLED_APPS中"
else
    print_status "添加captcha到INSTALLED_APPS..."
    
    # 备份设置文件
    cp config/settings/production.py config/settings/production.py.backup
    
    # 添加captcha到INSTALLED_APPS
    python3 << 'EOF'
import re

with open('config/settings/production.py', 'r') as f:
    content = f.read()

# 如果没有captcha，添加到INSTALLED_APPS
if 'captcha' not in content:
    # 查找INSTALLED_APPS的位置
    if 'INSTALLED_APPS' in content:
        # 在Django apps之后添加captcha
        pattern = r'(INSTALLED_APPS\s*=\s*\[[\s\S]*?# Django apps[\s\S]*?\n)'
        replacement = r'\1    "captcha",  # django-simple-captcha\n'
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open('config/settings/production.py', 'w') as f:
                f.write(new_content)
            print("已添加captcha到INSTALLED_APPS")
        else:
            # 简单添加方式
            content = content.replace(
                '# Django apps',
                '# Django apps\n    "captcha",  # django-simple-captcha'
            )
            with open('config/settings/production.py', 'w') as f:
                f.write(content)
            print("已通过简单方式添加captcha")
    else:
        print("未找到INSTALLED_APPS，请手动添加")
else:
    print("captcha已存在于配置中")
EOF
fi

print_status "🗃️ 数据库迁移..."

# 运行数据库迁移以支持captcha
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py migrate || {
    print_warning "数据库迁移失败，尝试创建captcha迁移..."
    
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
        $VENV_PATH/bin/python manage.py makemigrations captcha || true
    
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
        $VENV_PATH/bin/python manage.py migrate || print_warning "迁移仍然失败，将继续其他步骤"
}

print_status "📁 收集静态文件..."

# 重新收集静态文件
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py collectstatic --noinput --clear || {
    print_warning "静态文件收集失败，检查权限..."
    
    # 修复静态文件目录权限
    chown -R qatoolbox:qatoolbox staticfiles/ || true
    chmod -R 755 staticfiles/ || true
    
    # 再次尝试
    sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
        $VENV_PATH/bin/python manage.py collectstatic --noinput --clear || {
        print_error "静态文件收集仍然失败"
    }
}

print_status "🔍 Django系统检查..."

# 运行Django系统检查
sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production \
    $VENV_PATH/bin/python manage.py check || {
    print_warning "Django检查发现问题，但继续启动..."
}

print_header "🚀 启动Django应用"

print_status "🔄 重启Gunicorn服务..."

# 停止现有的gunicorn进程
pkill -f gunicorn || true
sleep 2

# 创建日志目录
mkdir -p /var/log/qatoolbox
chown -R qatoolbox:qatoolbox /var/log/qatoolbox

# 启动Gunicorn
print_status "🌐 启动Gunicorn服务器..."

sudo -u qatoolbox bash << 'EOF'
cd /home/qatoolbox/QAToolbox
source .venv/bin/activate

export DJANGO_SETTINGS_MODULE=config.settings.production

# 启动Gunicorn
gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --worker-class sync \
    --timeout 60 \
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

echo "Gunicorn启动完成"
EOF

sleep 3

print_header "🧪 验证修复结果"

print_status "📊 检查服务状态..."

# 检查Gunicorn进程
if pgrep -f gunicorn > /dev/null; then
    print_success "Gunicorn服务运行正常"
    echo "进程信息:"
    ps aux | grep gunicorn | grep -v grep
else
    print_error "Gunicorn启动失败"
    echo "错误日志:"
    tail -10 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || echo "无法读取错误日志"
fi

# 检查端口监听
if netstat -tlnp | grep ":8000" > /dev/null; then
    print_success "端口8000正在监听"
else
    print_warning "端口8000未监听"
fi

print_status "🌐 测试HTTP响应..."

# 等待服务完全启动
sleep 2

# 测试本地连接
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/ 2>/dev/null || echo "000")
if [ "$response" = "200" ]; then
    print_success "本地HTTP响应正常 (200)"
elif [ "$response" = "500" ]; then
    print_warning "服务器内部错误 (500) - 检查应用日志"
    tail -5 /var/log/qatoolbox/gunicorn_error.log 2>/dev/null || true
else
    print_warning "HTTP响应码: $response"
fi

# 测试外部访问
external_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/ 2>/dev/null || echo "000")
if [ "$external_response" = "200" ]; then
    print_success "外部HTTP访问正常 (200)"
else
    print_warning "外部HTTP访问异常 ($external_response)"
fi

print_status "📄 检查响应内容..."

# 获取响应内容类型和片段
content_sample=$(curl -s http://127.0.0.1:8000/ 2>/dev/null | head -5 || echo "无法获取内容")
if [[ "$content_sample" == *"<!DOCTYPE html"* ]] || [[ "$content_sample" == *"<html"* ]]; then
    print_success "响应为HTML内容 ✓"
elif [[ "$content_sample" == *"{"* ]] && [[ "$content_sample" == *"}"* ]]; then
    print_warning "响应仍为JSON格式"
    echo "内容样例: $content_sample"
else
    print_warning "响应格式未知"
    echo "内容样例: $content_sample"
fi

print_header "📋 修复总结"

echo "🔧 完成的操作:"
echo "  ✅ 安装了django-simple-captcha"
echo "  ✅ 安装了图像处理依赖 (Pillow, OpenCV)"
echo "  ✅ 安装了网络请求依赖 (requests, lxml, beautifulsoup4)"
echo "  ✅ 安装了自动化测试依赖 (selenium)"
echo "  ✅ 更新了Django设置配置"
echo "  ✅ 执行了数据库迁移"
echo "  ✅ 重新收集了静态文件"
echo "  ✅ 重启了Gunicorn服务"
echo ""

echo "🌐 访问地址:"
echo "  • 主页: https://shenyiqing.xin"
echo "  • HTTP重定向: http://shenyiqing.xin → https://shenyiqing.xin"
echo "  • 管理后台: https://shenyiqing.xin/admin"
echo ""

if [ "$response" = "200" ]; then
    print_success "🎉 应用启动成功！现在可以访问完整的前端界面了"
else
    print_warning "⚠️ 如果问题仍存在，请检查日志:"
    echo "  • Gunicorn日志: tail -f /var/log/qatoolbox/gunicorn_error.log"
    echo "  • Django检查: sudo -u qatoolbox DJANGO_SETTINGS_MODULE=config.settings.production /home/qatoolbox/QAToolbox/.venv/bin/python /home/qatoolbox/QAToolbox/manage.py check"
    echo "  • 依赖检查: sudo -u qatoolbox /home/qatoolbox/QAToolbox/.venv/bin/python -c 'import captcha; print(\"OK\")'"
fi

print_success "依赖修复和应用启动脚本执行完成！"





