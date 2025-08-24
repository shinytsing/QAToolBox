#!/bin/bash

echo "🔍 阿里云部署问题诊断工具"
echo "================================"

# 1. 基本环境检查
echo "📋 1. 基本环境信息"
echo "操作系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Python版本: $(python --version)"
echo "当前目录: $(pwd)"
echo "当前用户: $(whoami)"

# 2. 虚拟环境检查
echo ""
echo "📋 2. 虚拟环境状态"
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 虚拟环境已激活: $VIRTUAL_ENV"
else
    echo "⚠️ 虚拟环境未激活"
    if [ -d "venv" ]; then
        echo "发现venv目录，建议运行: source venv/bin/activate"
    fi
fi

# 3. Django配置检查
echo ""
echo "📋 3. Django配置检查"
python -c "
try:
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    django.setup()
    from django.conf import settings
    print('✅ Django配置加载成功')
    print(f'   DEBUG: {settings.DEBUG}')
    print(f'   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
    print(f'   SECRET_KEY存在: {bool(settings.SECRET_KEY)}')
    print(f'   数据库: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
    print(f'   静态文件目录: {getattr(settings, \"STATIC_ROOT\", \"未设置\")}')
except Exception as e:
    print(f'❌ Django配置错误: {e}')
"

# 4. 数据库连接检查
echo ""
echo "📋 4. 数据库连接检查"
python manage.py check --database default 2>/dev/null && echo "✅ 数据库连接正常" || echo "❌ 数据库连接异常"

# 5. 迁移状态检查
echo ""
echo "📋 5. 数据库迁移状态"
python manage.py showmigrations 2>/dev/null | tail -10

# 6. 端口占用检查
echo ""
echo "📋 6. 端口占用检查"
echo "端口8000状态:"
netstat -tlnp | grep :8000 || echo "端口8000未被占用"

# 7. 进程检查
echo ""
echo "📋 7. 相关进程检查"
echo "Gunicorn进程:"
ps aux | grep gunicorn | grep -v grep || echo "无gunicorn进程运行"

# 8. 日志文件检查
echo ""
echo "📋 8. 日志文件检查"
for logfile in "/tmp/qatoolbox.log" "/tmp/qatoolbox_error.log" "/tmp/qatoolbox_access.log"; do
    if [ -f "$logfile" ]; then
        echo "📄 $logfile (最后10行):"
        tail -10 "$logfile"
        echo "---"
    else
        echo "📄 $logfile: 文件不存在"
    fi
done

# 9. 磁盘空间检查
echo ""
echo "📋 9. 磁盘空间检查"
df -h | grep -E "(Filesystem|/dev/)"

# 10. 内存使用检查
echo ""
echo "📋 10. 内存使用检查"
free -h

# 11. 防火墙检查
echo ""
echo "📋 11. 防火墙检查"
if command -v firewall-cmd &> /dev/null; then
    echo "FirewallD状态:"
    firewall-cmd --state 2>/dev/null || echo "FirewallD未运行"
    firewall-cmd --list-ports 2>/dev/null || echo "无法获取端口列表"
elif command -v ufw &> /dev/null; then
    echo "UFW状态:"
    ufw status 2>/dev/null || echo "UFW未运行"
else
    echo "未检测到常见防火墙工具"
fi

# 12. 网络连接测试
echo ""
echo "📋 12. 网络连接测试"
echo "测试本地连接:"
curl -s -I http://localhost:8000/ | head -1 2>/dev/null || echo "本地连接失败"

echo ""
echo "🔍 诊断完成！"
echo "如果发现问题，请运行修复脚本: bash fix_aliyun_deployment.sh"
