#!/bin/bash

# QAToolBox 部署问题修复脚本
# 修复CORS、HTTPS、API路由等问题

set -e

echo "🔧 开始修复部署问题..."

# 1. 修复生产环境设置
echo "📝 修复生产环境设置..."
cat > config/settings/production.py << 'EOF'
"""
生产环境配置
"""
from .base import *

# 生产环境特定配置
DEBUG = False

# 安全配置 - 禁用HTTPS重定向避免CORS问题
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 0  # 禁用HSTS
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'  # 改为SAMEORIGIN避免CORS问题

# 生产环境数据库配置 - 使用PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'qatoolbox_production'),
        'USER': os.environ.get('DB_USER', 'qatoolbox'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}

# 生产环境缓存配置 - 使用本地内存缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# 生产环境会话配置
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# 生产环境静态文件配置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# 生产环境邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@qatoolbox.com')

# 生产环境日志配置
LOGGING['handlers']['file']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps.tools']['level'] = 'INFO'
LOGGING['loggers']['apps.users']['level'] = 'INFO'

# 生产环境Celery配置 - 简化为同步执行
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = 'django-db://'
CELERY_RESULT_BACKEND = 'django-db'

# 生产环境API限制
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100/minute',
    'user': '1000/minute'
}

# 生产环境CORS配置 - 允许所有来源避免CORS问题
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# 允许的主机 - 配置外网访问
ALLOWED_HOSTS = [
    'shenyiqing.xin',
    'www.shenyiqing.xin',
    '47.103.143.152',
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '*',  # 允许所有主机用于外网访问
]

# 生产环境安全头 - 禁用可能导致CORS问题的头
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

# 生产环境文件上传限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 500MB
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500MB

# 文件上传超时设置
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
DATA_UPLOAD_MAX_NUMBER_FILES = 1000
EOF

# 2. 修复用户URL配置
echo "🔗 修复用户URL配置..."
cat > apps/users/urls.py << 'EOF'
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # 验证码相关
    path('generate-progressive-captcha/', views.generate_progressive_captcha, name='generate_progressive_captcha'),
    path('verify-progressive-captcha/', views.verify_progressive_captcha, name='verify_progressive_captcha'),
    
    # 管理员用户管理
    path('admin/users/', views.admin_user_management, name='admin_user_management'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/logs/', views.admin_user_logs, name='admin_user_logs'),
    path('admin/monitoring/', views.admin_user_monitoring, name='admin_user_monitoring'),
    
    # 管理员用户管理API
    path('api/admin/change-status/<int:user_id>/', views.admin_change_user_status_api, name='admin_change_user_status_api'),
    path('api/admin/change-membership/<int:user_id>/', views.admin_change_membership_api, name='admin_change_membership_api'),
    path('api/admin/change-role/<int:user_id>/', views.admin_change_role_api, name='admin_change_role_api'),
    path('api/admin/delete-user/<int:user_id>/', views.admin_delete_user_api, name='admin_delete_user_api'),
    path('api/admin/batch-operation/', views.admin_batch_operation_api, name='admin_batch_operation_api'),
    path('api/admin/monitoring-stats/', views.admin_monitoring_stats_api, name='admin_monitoring_stats_api'),
    path('api/admin/force-logout/<int:user_id>/', views.admin_force_logout_api, name='admin_force_logout_api'),
    
    # 主题API
    path('theme/', views.theme_api, name='theme_api'),
    
    # 头像上传API
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
    
    # 头像上传测试页面
    path('avatar_test/', views.avatar_test_view, name='avatar_test'),
    
    # 用户认证API - 修复路径
    path('api/session-status/', views.session_status_api, name='session_status_api'),
    path('api/logout/', views.user_logout_api, name='user_logout_api'),
    path('api/extend-session/', views.extend_session_api, name='extend_session_api'),
    
    # 测试页面
    path('test-logout/', views.test_logout_view, name='test_logout'),
]
EOF

# 3. 修复验证码服务
echo "🔐 修复验证码服务..."
cat > apps/users/services/progressive_captcha_service.py << 'EOF'
"""
渐进式验证码服务 - 简化版
"""
import random
import json
import time
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import uuid


class ProgressiveCaptchaService:
    """渐进式验证码服务类"""
    
    def __init__(self):
        self.max_failures = 3
        self.reset_time = 180
        self.lock_duration = 180
    
    def get_user_failure_info(self, session_key):
        """获取用户验证失败信息"""
        cache_key = f'captcha_failures_{session_key}'
        failure_info = cache.get(cache_key, {
            'count': 0,
            'level': 0,
            'last_failure': None,
            'locked_until': None
        })
        return failure_info
    
    def record_failure(self, session_key):
        """记录验证失败"""
        failure_info = self.get_user_failure_info(session_key)
        failure_info['count'] += 1
        failure_info['last_failure'] = timezone.now().isoformat()
        
        # 如果失败次数达到阈值，锁定用户
        if failure_info['count'] >= self.max_failures:
            locked_until = timezone.now() + timedelta(seconds=self.lock_duration)
            failure_info['locked_until'] = locked_until.isoformat()
        
        cache_key = f'captcha_failures_{session_key}'
        cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return failure_info
    
    def record_success(self, session_key):
        """记录验证成功"""
        failure_info = self.get_user_failure_info(session_key)
        failure_info['count'] = 0
        failure_info['level'] = 0
        failure_info['last_failure'] = None
        failure_info['locked_until'] = None
        
        cache_key = f'captcha_failures_{session_key}'
        cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return failure_info
    
    def is_locked(self, session_key):
        """检查用户是否被锁定"""
        failure_info = self.get_user_failure_info(session_key)
        
        if failure_info.get('locked_until'):
            locked_until = timezone.datetime.fromisoformat(failure_info['locked_until'])
            if timezone.now() < locked_until:
                return True, locked_until
            else:
                # 锁定时间已过，清除锁定状态
                failure_info['locked_until'] = None
                cache_key = f'captcha_failures_{session_key}'
                cache.set(cache_key, failure_info, timeout=self.reset_time)
        
        return False, None
    
    def generate_captcha(self, session_key):
        """生成简单数学验证码"""
        # 检查是否被锁定
        is_locked, locked_until = self.is_locked(session_key)
        if is_locked:
            return {
                'success': False,
                'message': f'验证失败过多，请在 {locked_until.strftime("%H:%M:%S")} 后再试',
                'locked_until': locked_until.isoformat()
            }
        
        failure_info = self.get_user_failure_info(session_key)
        captcha_id = str(uuid.uuid4())
        
        # 生成简单数学题
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(['+', '-', '*'])
        
        if operation == '+':
            answer = num1 + num2
            question = f"{num1} + {num2} = ?"
        elif operation == '-':
            answer = num1 - num2
            question = f"{num1} - {num2} = ?"
        else:  # *
            answer = num1 * num2
            question = f"{num1} × {num2} = ?"
        
        # 存储答案到缓存
        cache_key = f'captcha_answer_{captcha_id}'
        cache.set(cache_key, str(answer), timeout=300)  # 5分钟过期
        
        captcha_data = {
            'id': captcha_id,
            'type': 'simple_math',
            'question': question,
            'answer': str(answer),
            'level': failure_info.get('level', 0),
            'failure_count': failure_info.get('count', 0),
            'max_failures': self.max_failures
        }
        
        return {
            'success': True,
            'data': captcha_data
        }
    
    def verify_captcha(self, session_key, captcha_id, captcha_type, user_input):
        """验证验证码"""
        try:
            cache_key = f'captcha_answer_{captcha_id}'
            correct_answer = cache.get(cache_key)
            
            if not correct_answer:
                return {
                    'success': False,
                    'message': '验证码已过期，请重新获取'
                }
            
            if str(user_input).strip() == str(correct_answer).strip():
                # 验证成功
                self.record_success(session_key)
                cache.delete(cache_key)  # 删除已使用的验证码
                return {
                    'success': True,
                    'message': '验证成功'
                }
            else:
                # 验证失败
                self.record_failure(session_key)
                return {
                    'success': False,
                    'message': '答案错误，请重试'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'验证失败: {str(e)}'
            }
EOF

# 4. 更新Nginx配置支持HTTPS
echo "🌐 更新Nginx配置..."
cat > nginx.production.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    # 基础配置
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 500M;
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # 上游服务器
    upstream django {
        server web:8000;
    }
    
    # HTTP服务器配置 - 重定向到HTTPS
    server {
        listen 80;
        server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
        
        # 重定向所有HTTP请求到HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    # HTTPS服务器配置
    server {
        listen 443 ssl http2;
        server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/shenyiqing.xin+3.pem;
        ssl_certificate_key /etc/nginx/ssl/shenyiqing.xin+3-key.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # 安全头
        add_header X-Frame-Options SAMEORIGIN;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        
        # 健康检查
        location /health/ {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 静态文件
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 媒体文件
        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public";
        }
        
        # 主应用
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            
            # 超时设置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # 缓冲设置
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }
    }
}
EOF

# 5. 更新Docker Compose配置
echo "🐳 更新Docker Compose配置..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL数据库
  db:
    image: postgres:15-alpine
    container_name: qatoolbox_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: qatoolbox_production
      POSTGRES_USER: qatoolbox
      POSTGRES_PASSWORD: ${DB_PASSWORD:-qatoolbox123}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U qatoolbox -d qatoolbox_production"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: qatoolbox_redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis123}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Django应用
  web:
    build: .
    container_name: qatoolbox_web
    restart: unless-stopped
    environment:
      # Django配置
      DJANGO_SETTINGS_MODULE: config.settings.production
      DJANGO_SECRET_KEY: ${DJANGO_SECRET_KEY:-django-insecure-change-this-in-production}
      DJANGO_DEBUG: "False"
      
      # 数据库配置
      DB_NAME: qatoolbox_production
      DB_USER: qatoolbox
      DB_PASSWORD: ${DB_PASSWORD:-qatoolbox123}
      DB_HOST: db
      DB_PORT: 5432
      
      # Redis配置
      REDIS_URL: redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      
      # 第三方API配置
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      GOOGLE_CSE_ID: ${GOOGLE_CSE_ID}
      OPENWEATHER_API_KEY: ${OPENWEATHER_API_KEY}
      
      # 邮件配置
      EMAIL_HOST: ${EMAIL_HOST:-smtp.gmail.com}
      EMAIL_PORT: ${EMAIL_PORT:-587}
      EMAIL_HOST_USER: ${EMAIL_HOST_USER}
      EMAIL_HOST_PASSWORD: ${EMAIL_HOST_PASSWORD}
      DEFAULT_FROM_EMAIL: ${DEFAULT_FROM_EMAIL:-noreply@shenyiqing.xin}
      
      # 安全配置
      SECURE_SSL_REDIRECT: "False"
      
      # 允许的主机
      ALLOWED_HOSTS: 47.103.143.152,shenyiqing.xin,www.shenyiqing.xin,localhost,127.0.0.1,0.0.0.0
    volumes:
      - media_data:/app/media
      - static_data:/app/staticfiles
      - logs_data:/app/logs
      - task_storage_data:/app/task_storage
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: qatoolbox_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.production.conf:/etc/nginx/nginx.conf:ro
      - ./ssl_certs:/etc/nginx/ssl:ro
      - static_data:/var/www/static:ro
      - media_data:/var/www/media:ro
    depends_on:
      - web
    networks:
      - qatoolbox_network
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

# 数据卷
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  media_data:
    driver: local
  static_data:
    driver: local
  logs_data:
    driver: local
  task_storage_data:
    driver: local

# 网络
networks:
  qatoolbox_network:
    driver: bridge
EOF

echo "✅ 修复完成！"
echo "🔄 重启服务以应用修复..."
echo "运行以下命令重启服务："
echo "docker-compose down && docker-compose up -d"
