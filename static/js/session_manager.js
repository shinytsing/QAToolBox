/**
 * Session管理器 - 自动延长用户登录状态
 * 功能：
 * 1. 定期检查session状态
 * 2. 在用户活动时自动延长session
 * 3. 在session即将过期时提醒用户
 */

class SessionManager {
    constructor() {
        this.checkInterval = 5 * 60 * 1000; // 每5分钟检查一次
        this.warningThreshold = 7 * 24 * 60 * 60 * 1000; // 7天前提醒
        this.extendThreshold = 3 * 24 * 60 * 60 * 1000; // 3天前自动延长
        this.isLoggedIn = false;
        this.sessionData = null;
        this.checkTimer = null;
        this.activityTimer = null;
        this.lastActivity = Date.now();
        
        this.init();
    }
    
    init() {
        // 检查用户是否已登录
        this.checkLoginStatus();
        
        // 如果已登录，开始session管理
        if (this.isLoggedIn) {
            this.startSessionManagement();
        }
    }
    
    async checkLoginStatus() {
        try {
            const response = await fetch('/users/api/session-status/', {
                method: 'GET',
                credentials: 'include'
            });
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (data.success) {
                    this.isLoggedIn = true;
                    this.sessionData = data.data;
                    console.log('Session状态检查成功:', this.sessionData);
                } else {
                    this.isLoggedIn = false;
                    console.log('用户未登录');
                }
            } else if (response.status === 401) {
                // 401状态码表示未登录，这是正常的
                this.isLoggedIn = false;
                console.log('用户未登录 (401)');
            } else {
                // 其他错误状态码
                this.isLoggedIn = false;
                console.log('Session状态检查失败，状态码:', response.status);
            }
        } catch (error) {
            console.error('检查登录状态失败:', error);
            this.isLoggedIn = false;
        }
    }
    
    startSessionManagement() {
        // 立即检查一次
        this.checkSessionStatus();
        
        // 设置定期检查
        this.checkTimer = setInterval(() => {
            this.checkSessionStatus();
        }, this.checkInterval);
        
        // 监听用户活动
        this.setupActivityListeners();
        
        // 设置活动检测定时器
        this.activityTimer = setInterval(() => {
            this.checkUserActivity();
        }, 60 * 1000); // 每分钟检查一次用户活动
    }
    
    setupActivityListeners() {
        // 监听用户活动事件
        const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
        
        events.forEach(event => {
            document.addEventListener(event, () => {
                this.lastActivity = Date.now();
            }, { passive: true });
        });
    }
    
    async checkSessionStatus() {
        if (!this.isLoggedIn) return;
        
        try {
            const response = await fetch('/users/api/session-status/', {
                method: 'GET',
                credentials: 'include'
            });
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (data.success) {
                    this.sessionData = data.data;
                    this.handleSessionStatus();
                } else {
                    // Session已过期
                    this.handleSessionExpired();
                }
            } else if (response.status === 401) {
                // 401状态码表示session已过期
                console.log('Session已过期 (401)');
                this.handleSessionExpired();
            } else {
                // 其他错误状态码
                console.error('获取session状态失败，状态码:', response.status);
            }
        } catch (error) {
            console.error('检查session状态失败:', error);
        }
    }
    
    handleSessionStatus() {
        const expiresInDays = this.sessionData.expires_in_days;
        
        if (expiresInDays <= 0) {
            // Session已过期
            this.handleSessionExpired();
        } else if (expiresInDays <= 3) {
            // 3天内过期，自动延长
            this.extendSession();
        } else if (expiresInDays <= 7) {
            // 7天内过期，显示提醒
            this.showSessionWarning(expiresInDays);
        }
    }
    
    async extendSession() {
        try {
            const response = await fetch('/users/api/extend-session/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'include'
            });
            
            // 检查响应内容类型
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                if (data.success) {
                    console.log('Session已自动延长');
                    this.sessionData.expires_in_days = 30;
                    this.hideSessionWarning();
                } else {
                    console.error('Session延长失败:', data.message);
                }
            } else if (response.status === 401) {
                // 401状态码表示用户未登录，session延长失败
                console.log('Session延长失败：用户未登录 (401)');
                this.handleSessionExpired();
            } else {
                // 其他错误状态码
                console.error('Session延长请求失败，状态码:', response.status);
            }
        } catch (error) {
            console.error('延长session失败:', error);
        }
    }
    
    checkUserActivity() {
        const now = Date.now();
        const timeSinceLastActivity = now - this.lastActivity;
        
        // 如果用户超过30分钟没有活动，暂停session管理
        if (timeSinceLastActivity > 30 * 60 * 1000) {
            console.log('用户长时间无活动，暂停session管理');
            return;
        }
        
        // 如果用户最近有活动且session即将过期，自动延长
        if (this.sessionData && this.sessionData.expires_in_days <= 3) {
            this.extendSession();
        }
    }
    
    showSessionWarning(daysLeft) {
        // 检查是否已经显示过警告
        if (document.getElementById('session-warning')) {
            return;
        }
        
        const warning = document.createElement('div');
        warning.id = 'session-warning';
        warning.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            max-width: 300px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        warning.innerHTML = `
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 18px; margin-right: 8px;">⚠️</span>
                <strong style="color: #856404;">登录状态提醒</strong>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="margin-left: auto; background: none; border: none; font-size: 18px; cursor: pointer; color: #856404;">×</button>
            </div>
            <p style="margin: 0 0 10px 0; color: #856404; font-size: 14px;">
                您的登录状态将在 ${daysLeft} 天后过期
            </p>
            <div style="display: flex; gap: 8px;">
                <button onclick="sessionManager.extendSession()" 
                        style="background: #007bff; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    延长登录
                </button>
                <button onclick="this.parentElement.parentElement.remove()" 
                        style="background: #6c757d; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    稍后提醒
                </button>
            </div>
        `;
        
        document.body.appendChild(warning);
        
        // 5秒后自动隐藏
        setTimeout(() => {
            if (warning.parentElement) {
                warning.remove();
            }
        }, 5000);
    }
    
    hideSessionWarning() {
        const warning = document.getElementById('session-warning');
        if (warning) {
            warning.remove();
        }
    }
    
    handleSessionExpired() {
        this.isLoggedIn = false;
        this.stopSessionManagement();
        
        // 显示过期提示
        const expired = document.createElement('div');
        expired.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            border: 1px solid #dc3545;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            text-align: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        `;
        
        expired.innerHTML = `
            <div style="margin-bottom: 15px;">
                <span style="font-size: 24px;">🔒</span>
            </div>
            <h3 style="margin: 0 0 10px 0; color: #dc3545;">登录已过期</h3>
            <p style="margin: 0 0 15px 0; color: #6c757d;">您的登录状态已过期，请重新登录</p>
            <button onclick="window.location.href='/users/login/'" 
                    style="background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer;">
                重新登录
            </button>
        `;
        
        document.body.appendChild(expired);
    }
    
    stopSessionManagement() {
        if (this.checkTimer) {
            clearInterval(this.checkTimer);
            this.checkTimer = null;
        }
        if (this.activityTimer) {
            clearInterval(this.activityTimer);
            this.activityTimer = null;
        }
    }
    
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // 手动延长session（供外部调用）
    async manualExtendSession() {
        if (!this.isLoggedIn) {
            console.log('用户未登录，无法延长session');
            return false;
        }
        
        await this.extendSession();
        return true;
    }
    
    // 获取session信息（供外部调用）
    getSessionInfo() {
        return this.sessionData;
    }
}

// 创建全局session管理器实例
const sessionManager = new SessionManager();

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SessionManager;
}
