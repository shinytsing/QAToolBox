#!/bin/bash

# 服务器端修复脚本
# 解决静态文件权限、API端点和CORS问题

set -e

echo "🚀 开始服务器修复..."

# 1. 停止服务
echo "📦 停止服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 2. 修复静态文件权限
echo "🔧 修复静态文件权限..."
cd /home/admin/QAToolbox

# 重新收集静态文件
python3 manage.py collectstatic --noinput --clear

# 设置正确的权限
chown -R www-data:www-data staticfiles/
chown -R www-data:www-data media/
chmod -R 755 staticfiles/
chmod -R 755 media/

# 确保geek.css可读
if [ -f "staticfiles/geek.css" ]; then
    chmod 644 staticfiles/geek.css
    chown www-data:www-data staticfiles/geek.css
    echo "✅ geek.css 权限已修复"
fi

# 3. 修复Nginx配置
echo "🌐 修复Nginx配置..."
cat > /etc/nginx/sites-available/qatoolbox << 'EOF'
server {
    listen 80;
    server_name 47.103.143.152 shenyiqing.xin www.shenyiqing.xin;
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CORS头 - 解决跨域问题
    add_header Access-Control-Allow-Origin "*" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken" always;
    add_header Access-Control-Allow-Credentials "true" always;
    
    # 处理预检请求
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-CSRFToken";
        add_header Access-Control-Allow-Credentials "true";
        add_header Access-Control-Max-Age 1728000;
        add_header Content-Type "text/plain; charset=utf-8";
        add_header Content-Length 0;
        return 204;
    }
    
    client_max_body_size 100M;
    
    # 静态文件 - 优化配置
    location /static/ {
        alias /home/admin/QAToolbox/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
        
        # 处理CSS文件
        location ~* \.css$ {
            add_header Content-Type text/css;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理JS文件
        location ~* \.js$ {
            add_header Content-Type application/javascript;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理图片文件
        location ~* \.(png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # 处理字体文件
        location ~* \.(woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 媒体文件
    location /media/ {
        alias /home/admin/QAToolbox/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # favicon处理
    location = /favicon.ico {
        alias /home/admin/QAToolbox/staticfiles/favicon.ico;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    location = /favicon.svg {
        alias /home/admin/QAToolbox/staticfiles/favicon.svg;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # 主应用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲设置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # 健康检查
    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
        access_log off;
    }
    
    # 禁止访问敏感文件
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(py|pyc|log|sqlite3)$ {
        deny all;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/qatoolbox /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t

# 4. 修复ProgressiveCaptchaService
echo "🔐 修复验证码服务..."
mkdir -p apps/users/services

cat > apps/users/services/__init__.py << 'EOF'
# Services package
EOF

cat > apps/users/services/progressive_captcha_service.py << 'EOF'
import random
import string
from django.core.cache import cache

class ProgressiveCaptchaService:
    """渐进式验证码服务"""
    
    def generate_captcha(self, session_key):
        """生成验证码"""
        try:
            # 生成简单的验证码
            captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            captcha_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
            
            # 存储到缓存
            cache.set(f'captcha_{session_key}_{captcha_id}', captcha_text, 300)  # 5分钟过期
            
            return {
                'success': True,
                'captcha_id': captcha_id,
                'captcha_text': captcha_text,
                'image_url': f'/static/captcha/{captcha_id}.png'  # 简化处理
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'生成验证码失败: {str(e)}'
            }
    
    def verify_captcha(self, session_key, captcha_id, captcha_type, user_input):
        """验证验证码"""
        try:
            cached_text = cache.get(f'captcha_{session_key}_{captcha_id}')
            if not cached_text:
                return {
                    'success': False,
                    'message': '验证码已过期或不存在'
                }
            
            if user_input.upper() == cached_text.upper():
                # 验证成功后删除缓存
                cache.delete(f'captcha_{session_key}_{captcha_id}')
                return {
                    'success': True,
                    'message': '验证码验证成功'
                }
            else:
                return {
                    'success': False,
                    'message': '验证码错误'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'验证失败: {str(e)}'
            }
EOF

# 5. 修复主题API
echo "🎨 修复主题API..."
if ! grep -q "def theme_api" apps/users/views.py; then
    cat >> apps/users/views.py << 'EOF'

# 主题API
@csrf_exempt
@require_http_methods(["GET", "POST"])
def theme_api(request):
    """主题API"""
    try:
        if request.method == 'GET':
            # 获取用户主题
            if request.user.is_authenticated:
                try:
                    user_theme = UserTheme.objects.get(user=request.user)
                    return JsonResponse({
                        'success': True,
                        'theme': user_theme.theme_name,
                        'custom_css': user_theme.custom_css
                    })
                except UserTheme.DoesNotExist:
                    return JsonResponse({
                        'success': True,
                        'theme': 'default',
                        'custom_css': ''
                    })
            else:
                return JsonResponse({
                    'success': True,
                    'theme': 'default',
                    'custom_css': ''
                })
        
        elif request.method == 'POST':
            # 设置用户主题
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'message': '请先登录'
                }, status=401)
            
            data = json.loads(request.body)
            theme_name = data.get('theme', 'default')
            custom_css = data.get('custom_css', '')
            
            user_theme, created = UserTheme.objects.get_or_create(
                user=request.user,
                defaults={'theme_name': theme_name, 'custom_css': custom_css}
            )
            
            if not created:
                user_theme.theme_name = theme_name
                user_theme.custom_css = custom_css
                user_theme.save()
            
            return JsonResponse({
                'success': True,
                'message': '主题设置成功'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'主题操作失败: {str(e)}'
        }, status=500)
EOF
fi

# 6. 启动服务
echo "🚀 启动服务..."

# 启动Nginx
systemctl start nginx
systemctl enable nginx

# 启动Django应用
supervisorctl start qatoolbox

# 等待服务启动
sleep 10

# 7. 测试修复结果
echo "🧪 测试修复结果..."

# 测试静态文件
echo "测试静态文件访问..."
STATIC_TEST=$(curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1)
echo "静态文件测试: $STATIC_TEST"

# 测试API端点
echo "测试API端点..."
API_TEST1=$(curl -I http://47.103.143.152/users/api/session-status/ 2>/dev/null | head -1)
echo "Session API测试: $API_TEST1"

API_TEST2=$(curl -I http://47.103.143.152/users/generate-progressive-captcha/ 2>/dev/null | head -1)
echo "验证码API测试: $API_TEST2"

# 测试主题API
API_TEST3=$(curl -I http://47.103.143.152/users/theme/ 2>/dev/null | head -1)
echo "主题API测试: $API_TEST3"

# 8. 显示服务状态
echo "📊 服务状态:"
supervisorctl status qatoolbox
systemctl status nginx --no-pager -l

echo "✅ 服务器修复完成！"
echo "🌐 访问地址: http://47.103.143.152"
echo "📁 静态文件: http://47.103.143.152/static/"
echo "🔧 管理后台: http://47.103.143.152/admin/"