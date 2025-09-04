#!/bin/bash

# 完整修复静态文件问题
echo "=== 完整修复静态文件问题 ==="

PROJECT_DIR="/home/admin/QAToolbox"
NGINX_STATIC_DIR="/var/www/static"
NGINX_MEDIA_DIR="/var/www/media"

# 1. 停止服务
echo "1. 停止服务..."
supervisorctl stop qatoolbox 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true

# 2. 进入项目目录
echo "2. 进入项目目录..."
cd "$PROJECT_DIR"

# 3. 检查源静态文件目录
echo "3. 检查源静态文件目录..."
echo "检查 src/static 目录:"
if [ -d "src/static" ]; then
    ls -la src/static/ | head -10
    echo "查找关键文件:"
    find src/static -name "geek.css" -o -name "feature-recommendation.css" -o -name "auth.js" -o -name "feature-recommendation.js" 2>/dev/null
else
    echo "src/static 目录不存在"
fi

echo "检查 static 目录:"
if [ -d "static" ]; then
    ls -la static/ | head -10
    echo "查找关键文件:"
    find static -name "geek.css" -o -name "feature-recommendation.css" -o -name "auth.js" -o -name "feature-recommendation.js" 2>/dev/null
else
    echo "static 目录不存在"
fi

# 4. 手动复制静态文件到staticfiles目录
echo "4. 手动复制静态文件..."
mkdir -p staticfiles

# 复制src/static中的文件
if [ -d "src/static" ]; then
    echo "复制 src/static 中的文件..."
    cp -r src/static/* staticfiles/ 2>/dev/null || true
fi

# 复制static中的文件
if [ -d "static" ]; then
    echo "复制 static 中的文件..."
    cp -r static/* staticfiles/ 2>/dev/null || true
fi

# 5. 检查Django应用中的静态文件
echo "5. 检查Django应用中的静态文件..."
find apps -name "static" -type d 2>/dev/null | while read app_static; do
    echo "复制 $app_static 中的文件..."
    cp -r "$app_static"/* staticfiles/ 2>/dev/null || true
done

# 6. 创建缺失的CSS文件（如果不存在）
echo "6. 创建缺失的CSS文件..."
mkdir -p staticfiles/css

# 创建geek.css（基础主题文件）
if [ ! -f "staticfiles/geek.css" ]; then
    echo "创建 geek.css..."
    cat > staticfiles/geek.css << 'EOF'
/* Geek主题样式 */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
    --body-bg: #ffffff;
    --text-color: #212529;
    --border-color: #dee2e6;
    --shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    background-color: var(--body-bg);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

.btn {
    display: inline-block;
    padding: 0.375rem 0.75rem;
    margin-bottom: 0;
    font-size: 1rem;
    font-weight: 400;
    line-height: 1.5;
    text-align: center;
    text-decoration: none;
    vertical-align: middle;
    cursor: pointer;
    border: 1px solid transparent;
    border-radius: 0.25rem;
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.btn-primary {
    color: #fff;
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-primary:hover {
    color: #fff;
    background-color: #0056b3;
    border-color: #004085;
}

.card {
    position: relative;
    display: flex;
    flex-direction: column;
    min-width: 0;
    word-wrap: break-word;
    background-color: #fff;
    background-clip: border-box;
    border: 1px solid var(--border-color);
    border-radius: 0.25rem;
    box-shadow: var(--shadow);
}

.card-body {
    flex: 1 1 auto;
    padding: 1.25rem;
}

.card-title {
    margin-bottom: 0.75rem;
    font-size: 1.25rem;
    font-weight: 500;
}

.text-center {
    text-align: center !important;
}

.mb-3 {
    margin-bottom: 1rem !important;
}

.mt-3 {
    margin-top: 1rem !important;
}

.p-3 {
    padding: 1rem !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 0 10px;
    }
    
    .card-body {
        padding: 1rem;
    }
}
EOF
fi

# 创建feature-recommendation.css
if [ ! -f "staticfiles/css/feature-recommendation.css" ]; then
    echo "创建 feature-recommendation.css..."
    cat > staticfiles/css/feature-recommendation.css << 'EOF'
/* 功能推荐样式 */
.feature-recommendation {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin: 1rem 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.feature-recommendation h3 {
    margin-top: 0;
    font-size: 1.5rem;
    font-weight: 600;
}

.feature-recommendation p {
    margin-bottom: 1rem;
    font-size: 1.1rem;
    opacity: 0.9;
}

.feature-recommendation .btn {
    background: rgba(255, 255, 255, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    text-decoration: none;
    display: inline-block;
    transition: all 0.3s ease;
}

.feature-recommendation .btn:hover {
    background: rgba(255, 255, 255, 0.3);
    border-color: rgba(255, 255, 255, 0.5);
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    .feature-recommendation {
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
    
    .feature-recommendation h3 {
        font-size: 1.3rem;
    }
    
    .feature-recommendation p {
        font-size: 1rem;
    }
}
EOF
fi

# 7. 创建缺失的JS文件
echo "7. 创建缺失的JS文件..."
mkdir -p staticfiles/js

# 创建auth.js
if [ ! -f "staticfiles/js/auth.js" ]; then
    echo "创建 auth.js..."
    cat > staticfiles/js/auth.js << 'EOF'
// 认证相关JavaScript
class AuthManager {
    constructor() {
        this.isAuthenticated = false;
        this.user = null;
        this.init();
    }

    init() {
        this.checkAuthStatus();
        this.bindEvents();
    }

    checkAuthStatus() {
        // 检查本地存储的认证状态
        const token = localStorage.getItem('auth_token');
        if (token) {
            this.isAuthenticated = true;
            this.user = JSON.parse(localStorage.getItem('user') || '{}');
        }
    }

    bindEvents() {
        // 绑定登录/登出事件
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (loginBtn) {
            loginBtn.addEventListener('click', () => this.showLogin());
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }
    }

    showLogin() {
        // 显示登录模态框或跳转到登录页面
        window.location.href = '/users/login/';
    }

    logout() {
        // 清除认证信息
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        this.isAuthenticated = false;
        this.user = null;
        
        // 刷新页面或跳转到首页
        window.location.href = '/';
    }

    isLoggedIn() {
        return this.isAuthenticated;
    }

    getCurrentUser() {
        return this.user;
    }
}

// 初始化认证管理器
const authManager = new AuthManager();

// 导出到全局作用域
window.AuthManager = AuthManager;
window.authManager = authManager;
EOF
fi

# 创建feature-recommendation.js
if [ ! -f "staticfiles/js/feature-recommendation.js" ]; then
    echo "创建 feature-recommendation.js..."
    cat > staticfiles/js/feature-recommendation.js << 'EOF'
// 功能推荐JavaScript
class FeatureRecommendation {
    constructor() {
        this.recommendations = [];
        this.init();
    }

    init() {
        this.loadRecommendations();
        this.bindEvents();
    }

    loadRecommendations() {
        // 模拟推荐数据
        this.recommendations = [
            {
                id: 1,
                title: 'PDF转Word工具',
                description: '快速将PDF文档转换为可编辑的Word格式',
                icon: '📄',
                url: '/tools/pdf-to-word/'
            },
            {
                id: 2,
                title: '图片压缩工具',
                description: '智能压缩图片大小，保持清晰度',
                icon: '🖼️',
                url: '/tools/image-compress/'
            },
            {
                id: 3,
                title: '二维码生成器',
                description: '快速生成各种类型的二维码',
                icon: '📱',
                url: '/tools/qr-generator/'
            }
        ];
    }

    bindEvents() {
        // 绑定推荐卡片点击事件
        document.addEventListener('click', (e) => {
            if (e.target.closest('.feature-card')) {
                const card = e.target.closest('.feature-card');
                const url = card.dataset.url;
                if (url) {
                    window.location.href = url;
                }
            }
        });
    }

    renderRecommendations(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const html = this.recommendations.map(rec => `
            <div class="feature-card card mb-3" data-url="${rec.url}">
                <div class="card-body">
                    <div class="d-flex align-items-center">
                        <div class="me-3" style="font-size: 2rem;">${rec.icon}</div>
                        <div>
                            <h5 class="card-title mb-1">${rec.title}</h5>
                            <p class="card-text text-muted">${rec.description}</p>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 初始化功能推荐
const featureRecommendation = new FeatureRecommendation();

// 页面加载完成后渲染推荐
document.addEventListener('DOMContentLoaded', () => {
    featureRecommendation.renderRecommendations('feature-recommendations');
});

// 导出到全局作用域
window.FeatureRecommendation = FeatureRecommendation;
window.featureRecommendation = featureRecommendation;
EOF
fi

# 8. 复制静态文件到nginx目录
echo "8. 复制静态文件到nginx目录..."
mkdir -p "$NGINX_STATIC_DIR"
mkdir -p "$NGINX_MEDIA_DIR"

cp -r staticfiles/* "$NGINX_STATIC_DIR/" 2>/dev/null || true
cp -r media/* "$NGINX_MEDIA_DIR/" 2>/dev/null || true

# 9. 设置权限
echo "9. 设置权限..."
chown -R www-data:www-data "$NGINX_STATIC_DIR"
chown -R www-data:www-data "$NGINX_MEDIA_DIR"
chown -R www-data:www-data "$PROJECT_DIR/staticfiles"
chown -R www-data:www-data "$PROJECT_DIR/media"

chmod -R 755 "$NGINX_STATIC_DIR"
chmod -R 755 "$NGINX_MEDIA_DIR"
chmod -R 755 "$PROJECT_DIR/staticfiles"
chmod -R 755 "$PROJECT_DIR/media"

# 10. 检查关键文件
echo "10. 检查关键文件..."
echo "检查 geek.css:"
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    echo "✓ geek.css 存在"
    ls -la "$NGINX_STATIC_DIR/geek.css"
else
    echo "✗ geek.css 不存在"
fi

echo "检查 feature-recommendation.css:"
if [ -f "$NGINX_STATIC_DIR/css/feature-recommendation.css" ]; then
    echo "✓ feature-recommendation.css 存在"
    ls -la "$NGINX_STATIC_DIR/css/feature-recommendation.css"
else
    echo "✗ feature-recommendation.css 不存在"
fi

echo "检查 auth.js:"
if [ -f "$NGINX_STATIC_DIR/js/auth.js" ]; then
    echo "✓ auth.js 存在"
    ls -la "$NGINX_STATIC_DIR/js/auth.js"
else
    echo "✗ auth.js 不存在"
fi

# 11. 测试文件访问
echo "11. 测试文件访问..."
if [ -f "$NGINX_STATIC_DIR/geek.css" ]; then
    sudo -u www-data test -r "$NGINX_STATIC_DIR/geek.css" && echo "✓ geek.css 可读" || echo "✗ geek.css 不可读"
fi

# 12. 启动服务
echo "12. 启动服务..."
systemctl start nginx
supervisorctl start qatoolbox

# 13. 等待启动
echo "13. 等待服务启动..."
sleep 10

# 14. 测试访问
echo "14. 测试访问..."
echo "测试 geek.css:"
curl -I http://47.103.143.152/static/geek.css 2>/dev/null | head -1

echo "测试 feature-recommendation.css:"
curl -I http://47.103.143.152/static/css/feature-recommendation.css 2>/dev/null | head -1

echo "测试 auth.js:"
curl -I http://47.103.143.152/static/js/auth.js 2>/dev/null | head -1

echo "测试主页:"
curl -I http://47.103.143.152/ 2>/dev/null | head -1

# 15. 显示状态
echo "15. 服务状态:"
systemctl status nginx --no-pager -l | head -3
supervisorctl status qatoolbox

echo ""
echo "=== 修复完成 ==="
echo "如果仍有问题，请检查:"
echo "1. nginx错误日志: tail -f /var/log/nginx/error.log"
echo "2. Django日志: tail -f $PROJECT_DIR/logs/django.log"
echo "3. 静态文件目录: ls -la $NGINX_STATIC_DIR"
