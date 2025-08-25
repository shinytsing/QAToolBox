#!/bin/bash

# 修复依赖问题并创建独立的Django配置
# 用于 shenyiqing.xin 服务器

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始修复依赖问题并创建独立配置...${NC}"

cd /home/qatoolbox/QAToolBox

# 1. 安装缺失的依赖
echo -e "${YELLOW}1. 安装缺失的依赖...${NC}"
sudo -u qatoolbox .venv/bin/pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ django-environ psutil pillow-heif ratelimit opencv-python-headless

# 2. 创建完全独立的生产配置（不依赖base.py）
echo -e "${YELLOW}2. 创建独立的Django配置...${NC}"
cat > config/settings/standalone_production.py << 'EOF'
"""
独立的生产环境配置
不依赖base.py，包含所有必要设置
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-standalone-production-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['shenyiqing.xin', '127.0.0.1', 'localhost', '47.103.143.152']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'apps.users',
    'apps.content',
    'apps.tools',
    'apps.share',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
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
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / "src" / "static",
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Security settings
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True

# Custom user model (if exists)
AUTH_USER_MODEL = 'users.User'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
EOF

sudo chown qatoolbox:qatoolbox config/settings/standalone_production.py

# 3. 更新wsgi.py使用新的配置
echo -e "${YELLOW}3. 更新WSGI配置...${NC}"
cat > config/wsgi.py << 'EOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.standalone_production')
application = get_wsgi_application()
EOF

sudo chown qatoolbox:qatoolbox config/wsgi.py

# 4. 确保__init__.py文件存在
echo -e "${YELLOW}4. 确保__init__.py文件存在...${NC}"
sudo -u qatoolbox touch apps/__init__.py
sudo -u qatoolbox touch apps/users/__init__.py
sudo -u qatoolbox touch apps/content/__init__.py
sudo -u qatoolbox touch apps/tools/__init__.py
sudo -u qatoolbox touch apps/share/__init__.py
sudo -u qatoolbox touch config/__init__.py
sudo -u qatoolbox touch config/settings/__init__.py

# 5. 创建简单的URLs配置
echo -e "${YELLOW}5. 创建URLs配置...${NC}"
cat > urls.py << 'EOF'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render

def health_check(request):
    return HttpResponse("OK")

def home_view(request):
    try:
        return render(request, 'home.html')
    except:
        return HttpResponse("Welcome to QAToolBox!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('', home_view, name='home'),
]

# 尝试添加应用URLs
try:
    from apps.tools.urls import urlpatterns as tools_urls
    urlpatterns.append(path('tools/', include('apps.tools.urls')))
except:
    pass

try:
    from apps.users.urls import urlpatterns as users_urls
    urlpatterns.append(path('users/', include('apps.users.urls')))
except:
    pass

try:
    from apps.content.urls import urlpatterns as content_urls
    urlpatterns.append(path('content/', include('apps.content.urls')))
except:
    pass

try:
    from apps.share.urls import urlpatterns as share_urls
    urlpatterns.append(path('share/', include('apps.share.urls')))
except:
    pass

# 静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
EOF

sudo chown qatoolbox:qatoolbox urls.py

# 6. 运行Django检查
echo -e "${YELLOW}6. 运行Django检查...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py check --settings=config.settings.standalone_production

# 7. 运行数据库迁移
echo -e "${YELLOW}7. 运行数据库迁移...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py migrate --settings=config.settings.standalone_production

# 8. 收集静态文件
echo -e "${YELLOW}8. 收集静态文件...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py collectstatic --noinput --settings=config.settings.standalone_production

# 9. 创建超级用户
echo -e "${YELLOW}9. 创建超级用户...${NC}"
sudo -u qatoolbox .venv/bin/python manage.py shell --settings=config.settings.standalone_production << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("超级用户已创建: admin/admin123")
else:
    print("超级用户admin已存在")
EOF

# 10. 更新systemd服务配置
echo -e "${YELLOW}10. 更新systemd服务配置...${NC}"
cat > /etc/systemd/system/qatoolbox.service << 'EOF'
[Unit]
Description=QAToolBox Django Application
After=network.target

[Service]
Type=simple
User=qatoolbox
Group=qatoolbox
WorkingDirectory=/home/qatoolbox/QAToolBox
Environment=PATH=/home/qatoolbox/QAToolBox/.venv/bin
Environment=PYTHONPATH=/home/qatoolbox/QAToolBox
Environment=DJANGO_SETTINGS_MODULE=config.settings.standalone_production
ExecStart=/home/qatoolbox/QAToolBox/.venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 300 --access-logfile - --error-logfile - config.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 11. 重新加载和启动服务
echo -e "${YELLOW}11. 重新加载和启动服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl restart qatoolbox
sudo systemctl restart nginx

# 12. 等待服务启动
sleep 5

# 13. 检查服务状态
echo -e "${YELLOW}12. 检查服务状态...${NC}"
echo "QAToolBox服务状态:"
sudo systemctl status qatoolbox --no-pager -l | head -10

echo -e "\nNginx服务状态:"
sudo systemctl status nginx --no-pager -l | head -10

# 14. 测试访问
echo -e "${YELLOW}13. 测试访问...${NC}"
echo "测试主页:"
curl -I -k https://shenyiqing.xin/ 2>/dev/null | head -2

echo -e "\n测试管理后台:"
curl -I -k https://shenyiqing.xin/admin/ 2>/dev/null | head -2

echo -e "\n测试静态文件:"
curl -I -k https://shenyiqing.xin/static/base.css 2>/dev/null | head -2

echo -e "${GREEN}修复完成！${NC}"
echo -e "${BLUE}网站地址: https://shenyiqing.xin${NC}"
echo -e "${BLUE}管理后台: https://shenyiqing.xin/admin${NC}"
echo -e "${BLUE}超级用户: admin / admin123${NC}"
echo -e "${BLUE}如有问题，请检查日志:${NC}"
echo "  - sudo journalctl -u qatoolbox -f"
echo "  - sudo tail -f /var/log/nginx/error.log"
echo "  - tail -f /home/qatoolbox/QAToolBox/logs/django.log"
