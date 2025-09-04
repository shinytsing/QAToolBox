#!/bin/bash
# =============================================================================
# QAToolBox 快速修复服务器问题
# 修复CORS、认证和路由问题
# =============================================================================

set -e

echo "🔧 开始快速修复服务器问题..."

# 1. 修复settings.py中的CORS配置
echo "修复CORS配置..."
cat >> settings.py << 'EOF'

# 快速修复CORS配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
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

# 修复认证配置
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# 修复会话配置
SESSION_COOKIE_AGE = 1209600  # 14天
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# 修复CSRF配置
CSRF_TRUSTED_ORIGINS = [
    'http://47.103.143.152',
    'http://shenyiqing.xin',
    'https://shenyiqing.xin',
]
EOF

# 2. 修复urls.py添加accounts重定向
echo "修复URL路由..."
cat >> urls.py << 'EOF'

# 添加accounts重定向路由
from django.views.generic import RedirectView

# 在urlpatterns列表中添加重定向
accounts_redirects = [
    path('accounts/login/', RedirectView.as_view(url='/users/login/', permanent=True), name='accounts_login_redirect'),
    path('accounts/logout/', RedirectView.as_view(url='/users/logout/', permanent=True), name='accounts_logout_redirect'),
    path('accounts/profile/', RedirectView.as_view(url='/users/profile/', permanent=True), name='accounts_profile_redirect'),
    path('accounts/register/', RedirectView.as_view(url='/users/register/', permanent=True), name='accounts_register_redirect'),
]

# 将重定向路由添加到urlpatterns
urlpatterns = accounts_redirects + urlpatterns
EOF

# 3. 创建简单的健康检查API
echo "创建健康检查API..."
mkdir -p apps/users/views
cat > apps/users/views/health_api.py << 'EOF'
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def session_status_api(request):
    """会话状态API"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        if request.user.is_authenticated:
            return JsonResponse({
                'status': 'authenticated',
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                }
            })
        else:
            return JsonResponse({
                'status': 'anonymous',
                'user': None
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def generate_captcha_api(request):
    """生成验证码API"""
    if request.method == 'OPTIONS':
        response = JsonResponse({})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    try:
        # 简单的验证码生成
        import random
        import string
        
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        
        return JsonResponse({
            'success': True,
            'captcha_id': captcha_id,
            'captcha_text': captcha_text,
            'image_url': f'/static/captcha/{captcha_id}.png'  # 简化处理
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
EOF

# 4. 更新用户URLs
echo "更新用户URLs..."
cat >> apps/users/urls.py << 'EOF'

# 添加API路由
from .views.health_api import session_status_api, generate_captcha_api

# 在urlpatterns中添加
urlpatterns += [
    path('api/session-status/', session_status_api, name='session_status_api'),
    path('generate-progressive-captcha/', generate_captcha_api, name='generate_captcha_api'),
]
EOF

# 5. 创建简单的Nginx配置
echo "创建Nginx配置..."
cat > nginx_simple.conf << 'EOF'
server {
    listen 80;
    server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
    
    # CORS头
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization" always;
    add_header Access-Control-Allow-Credentials "true" always;
    
    # 处理预检请求
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
        add_header Access-Control-Allow-Credentials "true";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain; charset=utf-8";
        add_header Content-Length 0;
        return 204;
    }
    
    client_max_body_size 100M;
    
    location /static/ {
        alias /home/qatoolbox/QAToolBox/staticfiles/;
        expires 1M;
        add_header Cache-Control "public, immutable";
        add_header Access-Control-Allow-Origin "*";
    }
    
    location /media/ {
        alias /home/qatoolbox/QAToolBox/media/;
        expires 1w;
        add_header Cache-Control "public";
        add_header Access-Control-Allow-Origin "*";
    }
    
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

# 6. 创建重启脚本
echo "创建重启脚本..."
cat > restart_all.sh << 'EOF'
#!/bin/bash
echo "重启所有服务..."

# 重启Nginx
sudo systemctl restart nginx
echo "Nginx重启完成"

# 重启PostgreSQL
sudo systemctl restart postgresql
echo "PostgreSQL重启完成"

# 重启Redis
sudo systemctl restart redis-server
echo "Redis重启完成"

# 重启应用
sudo supervisorctl restart qatoolbox
echo "QAToolBox应用重启完成"

# 等待服务启动
sleep 5

# 检查状态
echo "检查服务状态..."
sudo systemctl status nginx --no-pager -l
sudo systemctl status postgresql --no-pager -l
sudo systemctl status redis-server --no-pager -l
sudo supervisorctl status qatoolbox

echo "所有服务重启完成！"
EOF

chmod +x restart_all.sh

echo "✅ 快速修复脚本创建完成！"
echo ""
echo "📋 下一步操作："
echo "1. 执行修复: ./quick_fix_server.sh"
echo "2. 更新Nginx: sudo cp nginx_simple.conf /etc/nginx/sites-available/qatoolbox"
echo "3. 重启服务: ./restart_all.sh"
echo "4. 测试访问: curl -I http://47.103.143.152/"
