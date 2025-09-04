#!/bin/bash
# =============================================================================
# QAToolBox 服务器问题修复脚本
# 修复CORS、路由和认证问题
# =============================================================================

set -e

# 颜色定义
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

echo -e "${CYAN}${BOLD}"
cat << 'EOF'
========================================
🔧 QAToolBox 服务器问题修复脚本
========================================
修复CORS、路由和认证问题
========================================
EOF
echo -e "${NC}"

# 检查是否在项目目录
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 修复CORS配置
echo -e "${YELLOW}🔧 修复CORS配置...${NC}"

# 备份原始settings.py
cp settings.py settings.py.backup.$(date +%s)

# 更新CORS配置
cat > settings_cors_fix.py << 'EOF'
# CORS配置修复
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://47.103.143.152",
    "http://47.103.143.152:8000",
    "https://shenyiqing.xin",
    "https://www.shenyiqing.xin",
]

CORS_ALLOW_ALL_ORIGINS = True  # 临时允许所有来源，生产环境应关闭
CORS_ALLOW_CREDENTIALS = True

# 允许的请求头
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

# 允许的HTTP方法
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
EOF

# 将CORS修复添加到settings.py
echo "" >> settings.py
echo "# CORS修复配置" >> settings.py
cat settings_cors_fix.py >> settings.py
rm settings_cors_fix.py

echo -e "${GREEN}✅ CORS配置修复完成${NC}"

# 2. 修复URL路由问题
echo -e "${YELLOW}🔧 修复URL路由问题...${NC}"

# 在urls.py中添加accounts重定向
cat > urls_accounts_fix.py << 'EOF'
# 添加accounts重定向路由
from django.urls import path
from django.views.generic import RedirectView

# 在urlpatterns中添加以下路由
accounts_redirects = [
    # 重定向旧的accounts路径到新的users路径
    path('accounts/login/', RedirectView.as_view(url='/users/login/', permanent=True), name='accounts_login_redirect'),
    path('accounts/logout/', RedirectView.as_view(url='/users/logout/', permanent=True), name='accounts_logout_redirect'),
    path('accounts/profile/', RedirectView.as_view(url='/users/profile/', permanent=True), name='accounts_profile_redirect'),
    path('accounts/register/', RedirectView.as_view(url='/users/register/', permanent=True), name='accounts_register_redirect'),
]
EOF

# 备份原始urls.py
cp urls.py urls.py.backup.$(date +%s)

# 在urls.py中添加重定向路由
sed -i '/urlpatterns = \[/a\    # Accounts重定向路由\n    path("accounts/login/", RedirectView.as_view(url="/users/login/", permanent=True), name="accounts_login_redirect"),\n    path("accounts/logout/", RedirectView.as_view(url="/users/logout/", permanent=True), name="accounts_logout_redirect"),\n    path("accounts/profile/", RedirectView.as_view(url="/users/profile/", permanent=True), name="accounts_profile_redirect"),\n    path("accounts/register/", RedirectView.as_view(url="/users/register/", permanent=True), name="accounts_register_redirect"),' urls.py

echo -e "${GREEN}✅ URL路由修复完成${NC}"

# 3. 修复认证中间件问题
echo -e "${YELLOW}🔧 修复认证中间件问题...${NC}"

# 检查并修复中间件配置
if ! grep -q "corsheaders.middleware.CorsMiddleware" settings.py; then
    echo "添加CORS中间件..."
    sed -i '/MIDDLEWARE = \[/a\    "corsheaders.middleware.CorsMiddleware",' settings.py
fi

echo -e "${GREEN}✅ 认证中间件修复完成${NC}"

# 4. 创建生产环境配置
echo -e "${YELLOW}🔧 创建生产环境配置...${NC}"

cat > .env.production << EOF
# 生产环境配置
DJANGO_SECRET_KEY=django-production-key-$(openssl rand -hex 32)
DEBUG=False
DJANGO_SETTINGS_MODULE=settings

# 主机配置
ALLOWED_HOSTS=shenyiqing.xin,www.shenyiqing.xin,47.103.143.152,localhost,127.0.0.1

# 数据库配置
DB_NAME=qatoolbox
DB_USER=qatoolbox
DB_PASSWORD=QAToolBox@2024@$(date +%s)
DB_HOST=localhost
DB_PORT=5432

# Redis配置
REDIS_URL=redis://localhost:6379/0

# CORS配置
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True

# 安全配置
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# 日志级别
LOG_LEVEL=INFO
EOF

echo -e "${GREEN}✅ 生产环境配置创建完成${NC}"

# 5. 修复静态文件问题
echo -e "${YELLOW}🔧 修复静态文件问题...${NC}"

# 确保静态文件目录存在
mkdir -p staticfiles
mkdir -p media

# 收集静态文件
python manage.py collectstatic --noinput

echo -e "${GREEN}✅ 静态文件修复完成${NC}"

# 6. 创建Nginx配置修复
echo -e "${YELLOW}🔧 创建Nginx配置修复...${NC}"

cat > nginx_fix.conf << 'EOF'
# Nginx配置修复
server {
    listen 80;
    server_name shenyiqing.xin www.shenyiqing.xin 47.103.143.152;
    
    # 安全头配置
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # CORS头配置
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

echo -e "${GREEN}✅ Nginx配置修复创建完成${NC}"

# 7. 创建重启脚本
echo -e "${YELLOW}🔧 创建重启脚本...${NC}"

cat > restart_services.sh << 'EOF'
#!/bin/bash
# 重启所有服务

echo "重启Nginx..."
sudo systemctl restart nginx

echo "重启PostgreSQL..."
sudo systemctl restart postgresql

echo "重启Redis..."
sudo systemctl restart redis-server

echo "重启QAToolBox应用..."
sudo supervisorctl restart qatoolbox

echo "检查服务状态..."
sudo systemctl status nginx --no-pager
sudo systemctl status postgresql --no-pager
sudo systemctl status redis-server --no-pager
sudo supervisorctl status qatoolbox

echo "服务重启完成！"
EOF

chmod +x restart_services.sh

echo -e "${GREEN}✅ 重启脚本创建完成${NC}"

# 8. 显示修复总结
echo -e "${CYAN}${BOLD}"
cat << EOF

========================================
🎉 服务器问题修复完成！
========================================

🔧 修复内容:
  ✅ CORS配置 - 允许所有来源和凭据
  ✅ URL路由 - 添加accounts重定向
  ✅ 认证中间件 - 添加CORS中间件
  ✅ 生产环境配置 - 创建.env.production
  ✅ 静态文件 - 重新收集静态文件
  ✅ Nginx配置 - 添加CORS头支持
  ✅ 重启脚本 - 创建restart_services.sh

📋 下一步操作:
  1. 更新Nginx配置:
     sudo cp nginx_fix.conf /etc/nginx/sites-available/qatoolbox
     sudo nginx -t
     sudo systemctl restart nginx

  2. 重启所有服务:
     ./restart_services.sh

  3. 检查服务状态:
     curl -I http://47.103.143.152/
     curl -I http://shenyiqing.xin/

  4. 查看日志:
     tail -f /var/log/qatoolbox/gunicorn.log
     tail -f /var/log/nginx/error.log

========================================
EOF
echo -e "${NC}"

echo -e "${GREEN}🎉 修复脚本执行完成！${NC}"
