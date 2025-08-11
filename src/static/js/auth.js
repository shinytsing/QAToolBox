/**
 * 用户认证相关JavaScript函数
 * 处理登录、登出、token管理等功能
 */

// 确保在正确的上下文中运行
(function() {
    'use strict';
    
    // 用户登出函数
async function logoutUser() {
    try {
        // 清除所有本地存储的token和用户数据
        clearAllLocalStorage();
        clearAllSessionStorage();
        
        // 调用后端登出API
        const response = await fetch('/users/api/logout/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // 如果API返回清除存储标志，再次确保清除本地存储
            if (result.clear_storage) {
                clearAllLocalStorage();
                clearAllSessionStorage();
            }
            
            // 显示成功消息
            showNotification(result.message || '登出成功', 'success');
            
            // 重定向到首页或指定页面
            setTimeout(() => {
                window.location.href = result.redirect_url || '/';
            }, 1000);
        } else {
            throw new Error(result.message || '登出失败');
        }
        
    } catch (error) {
        console.error('登出失败:', error);
        
        // 即使API调用失败，也要清除本地存储
        clearAllLocalStorage();
        clearAllSessionStorage();
        
        showNotification('登出过程中遇到问题，但本地数据已清除', 'warning');
        
        // 强制重定向到首页
        setTimeout(() => {
            window.location.href = '/';
        }, 1500);
    }
}

// 清除所有localStorage中的用户相关数据
function clearAllLocalStorage() {
    const keysToRemove = [];
    
    // 遍历所有localStorage键
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (shouldClearKey(key)) {
            keysToRemove.push(key);
        }
    }
    
    // 删除所有需要清除的键
    keysToRemove.forEach(key => {
        try {
            localStorage.removeItem(key);
            console.log(`已清除localStorage: ${key}`);
        } catch (error) {
            console.error(`清除localStorage失败 ${key}:`, error);
        }
    });
}

// 清除所有sessionStorage中的用户相关数据
function clearAllSessionStorage() {
    const keysToRemove = [];
    
    // 遍历所有sessionStorage键
    for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (shouldClearKey(key)) {
            keysToRemove.push(key);
        }
    }
    
    // 删除所有需要清除的键
    keysToRemove.forEach(key => {
        try {
            sessionStorage.removeItem(key);
            console.log(`已清除sessionStorage: ${key}`);
        } catch (error) {
            console.error(`清除sessionStorage失败 ${key}:`, error);
        }
    });
}

// 判断是否应该清除某个键
function shouldClearKey(key) {
    if (!key) return false;
    
    // 需要清除的键模式
    const clearPatterns = [
        'token',           // 各种token
        'auth',            // 认证相关
        'user',            // 用户相关
        'boss',            // Boss直聘相关
        'login',           // 登录相关
        'session',         // 会话相关
        'preference',      // 用户偏好
        'profile',         // 用户资料
        'current-theme',   // 当前主题（如果需要重置）
        'preferred-language', // 语言偏好（可选择性保留）
    ];
    
    // 不应该清除的键（可以根据需要调整）
    const preservePatterns = [
        'preferred-language', // 保留语言设置
        'cookie-consent',     // 保留cookie同意状态
        'tour-completed',     // 保留教程完成状态
    ];
    
    // 检查是否应该保留
    const shouldPreserve = preservePatterns.some(pattern => 
        key.toLowerCase().includes(pattern.toLowerCase())
    );
    
    if (shouldPreserve) {
        return false;
    }
    
    // 检查是否应该清除
    return clearPatterns.some(pattern => 
        key.toLowerCase().includes(pattern.toLowerCase())
    );
}

// 清除所有cookie中的认证相关信息
function clearAuthCookies() {
    const cookiesToClear = [
        'sessionid',
        'csrftoken', 
        'boss_token',
        'user_session',
        'auth_token'
    ];
    
    cookiesToClear.forEach(cookieName => {
        // 清除当前域的cookie
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        // 清除子域的cookie
        document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.${window.location.hostname};`;
    });
}

// 获取CSRF Token
function getCSRFToken() {
    // 首先尝试从meta标签获取
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    // 然后尝试从cookie获取
    return getCookie('csrftoken');
}

// 获取Cookie值
function getCookie(name) {
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

// 显示通知消息
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
    `;
    
    notification.innerHTML = `
        <strong>${type === 'success' ? '成功' : type === 'error' ? '错误' : type === 'warning' ? '警告' : '信息'}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 添加到页面
    document.body.appendChild(notification);
    
    // 自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// 完全清除用户认证状态的函数
function completeUserLogout() {
    clearAllLocalStorage();
    clearAllSessionStorage();
    clearAuthCookies();
    
    // 清除任何可能存在的全局变量
    if (window.currentUser) {
        window.currentUser = null;
    }
    if (window.userToken) {
        window.userToken = null;
    }
    
    console.log('用户认证状态已完全清除');
}

// 页面加载时检查登出状态
document.addEventListener('DOMContentLoaded', function() {
    // 检查响应头是否包含清除存储的指令
    const checkLogoutHeaders = () => {
        const clearStorageHeader = document.querySelector('meta[name="clear-storage"]');
        if (clearStorageHeader && clearStorageHeader.content === 'true') {
            completeUserLogout();
        }
    };
    
    checkLogoutHeaders();
    
    // 绑定登出按钮事件
    const logoutButtons = document.querySelectorAll('[data-action="logout"], .logout-btn, #logout-btn');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // 确认对话框
            if (confirm('确定要登出吗？')) {
                logoutUser();
            }
        });
    });
});

// 监听浏览器标签页关闭/刷新事件
window.addEventListener('beforeunload', function() {
    // 在页面卸载前清除敏感的sessionStorage数据
    const sensitiveKeys = ['boss_user_token', 'temp_auth_token', 'api_session'];
    sensitiveKeys.forEach(key => {
        sessionStorage.removeItem(key);
    });
});

// 导出函数供其他脚本使用
window.AuthUtils = {
    logoutUser,
    clearAllLocalStorage,
    clearAllSessionStorage,
    clearAuthCookies,
    completeUserLogout,
    getCSRFToken,
    getCookie,
    showNotification
};
})();
