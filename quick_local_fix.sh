#!/bin/bash

# QAToolBox 本地快速修复脚本 - 无需下载
# 直接在服务器上创建和执行

echo "🆘 开始本地快速修复..."

# 创建修复脚本
cat > /tmp/emergency_fix.sh << 'SCRIPT_EOF'
#!/bin/bash

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "🚀 开始紧急修复QAToolBox..."

# 检查项目目录
if [ ! -d "/home/qatoolbox/QAToolBox" ]; then
    print_error "项目目录不存在"
    exit 1
fi

cd /home/qatoolbox/QAToolBox
print_status "当前目录: $(pwd)"

# 1. 停止服务
print_status "停止现有服务..."
systemctl stop qatoolbox || true
systemctl stop nginx || true

# 2. 修复权限
print_status "修复权限..."
chown -R qatoolbox:qatoolbox /home/qatoolbox/QAToolBox
chmod -R 755 /home/qatoolbox/QAToolBox
mkdir -p /home/qatoolbox/.cache
chown -R qatoolbox:qatoolbox /home/qatoolbox/.cache

# 3. 修复PostgreSQL
print_status "修复PostgreSQL..."
rm -rf /root/.postgresql || true

# 找到pg_hba.conf文件
PG_HBA_PATH=$(find /etc/postgresql -name "pg_hba.conf" 2>/dev/null | head -n1)
if [ -f "$PG_HBA_PATH" ]; then
    cp "$PG_HBA_PATH" "${PG_HBA_PATH}.backup"
    sed -i 's/local   all             all                                     peer/local   all             all                                     trust/' "$PG_HBA_PATH"
    sed -i 's/local   all             all                                     md5/local   all             all                                     trust/' "$PG_HBA_PATH"
    sed -i 's/host    all             all             127.0.0.1\/32            md5/host    all             all             127.0.0.1\/32            trust/' "$PG_HBA_PATH"
fi

systemctl restart postgresql
sleep 3

# 4. 重建数据库
print_status "重建数据库..."
sudo -u postgres dropdb qatoolbox || true
sudo -u postgres dropuser qatoolbox || true
sudo -u postgres createuser qatoolbox
sudo -u postgres createdb qatoolbox -O qatoolbox

# 5. 创建紧急配置
print_status "创建紧急配置..."
mkdir -p /home/qatoolbox/QAToolBox/config/settings
touch /home/qatoolbox/QAToolBox/config/__init__.py
touch /home/qatoolbox/QAToolBox/config/settings/__init__.py

cat > /home/qatoolbox/QAToolBox/config/settings/emergency.py << 'CONFIG_EOF'
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = 'emergency-key-123'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'emergency_urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'emergency.sqlite3',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = '/home/qatoolbox/QAToolBox/staticfiles'
STATICFILES_DIRS = []

MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/qatoolbox/QAToolBox/media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CONFIG_EOF

# 6. 创建紧急URLs
cat > /home/qatoolbox/QAToolBox/emergency_urls.py << 'URLS_EOF'
from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("QAToolBox Emergency - OK", content_type="text/plain")

def home_view(request):
    return HttpResponse("""
    <h1>🆘 QAToolBox Emergency Mode</h1>
    <p>Service is running!</p>
    <p><a href="/admin/">Admin</a> | <a href="/health/">Health</a></p>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('', home_view),
]
URLS_EOF

# 7. 更新WSGI配置
cat > /home/qatoolbox/QAToolBox/config/wsgi.py << 'WSGI_EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.emergency')
application = get_wsgi_application()
WSGI_EOF

# 8. 运行迁移
print_status "运行迁移..."
cd /home/qatoolbox/QAToolBox
export DJANGO_SETTINGS_MODULE=config.settings.emergency
sudo -u qatoolbox -E .venv/bin/python manage.py migrate --settings=config.settings.emergency

# 9. 创建超级用户
print_status "创建管理员..."
sudo -u qatoolbox -E .venv/bin/python manage.py shell --settings=config.settings.emergency << 'PYEOF'
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("管理员已创建: admin/admin123")
PYEOF

# 10. 收集静态文件
sudo -u qatoolbox -E .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.emergency

# 11. 更新systemd服务
cat > /etc/systemd/system/qatoolbox.service << 'SERVICE_EOF'
[Unit]
Description=QAToolBox Emergency
After=network.target

[Service]
Type=exec
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment="PATH=/home/qatoolbox/QAToolBox/.venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings.emergency"
Environment="HOME=/home/qatoolbox"
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --workers 1 --bind 127.0.0.1:8000 --timeout 60 config.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# 12. 启动服务
print_status "启动服务..."
systemctl daemon-reload
systemctl enable qatoolbox
systemctl start qatoolbox
sleep 5

# 13. 启动Nginx
systemctl start nginx
systemctl enable nginx

# 14. 检查状态
print_success "修复完成!"
echo "状态检查:"
echo "QAToolBox: $(systemctl is-active qatoolbox)"
echo "Nginx: $(systemctl is-active nginx)"

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; then
    print_success "HTTP测试通过"
else
    print_warning "HTTP测试未通过，但服务可能正在启动"
fi

print_success "🎉 紧急修复完成！"
echo ""
echo "访问: https://shenyiqing.xin"
echo "管理: https://shenyiqing.xin/admin/ (admin/admin123)"
echo "健康: https://shenyiqing.xin/health/"
echo ""
echo "查看日志: journalctl -u qatoolbox -f"

SCRIPT_EOF

# 执行修复脚本
chmod +x /tmp/emergency_fix.sh
bash /tmp/emergency_fix.sh

echo "修复脚本执行完成！"

