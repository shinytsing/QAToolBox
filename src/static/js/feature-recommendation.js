/**
 * 功能推荐系统前端组件
 * 处理推荐弹窗显示、用户交互和数据通信
 */

// 确保在正确的上下文中运行
(function() {
    'use strict';
    
    class FeatureRecommendation {
    constructor() {
        this.baseUrl = '/tools/api';
        this.currentRecommendations = [];
        this.currentSessionId = null;
        this.isPopupOpen = false;
        this.init();
    }

    init() {
        // 页面加载时检查是否需要显示推荐
        if (this.shouldCheckRecommendation()) {
            setTimeout(() => {
                this.checkAndShowRecommendation();
            }, 2000); // 延迟2秒显示，避免干扰页面加载
        }

        // 绑定全局事件
        this.bindGlobalEvents();
    }

    shouldCheckRecommendation() {
        // 检查是否为登录用户且不在管理员页面
        if (document.body.dataset.userAuthenticated !== 'true' || 
            window.location.pathname.includes('/admin/')) {
            return false;
        }
        
        // 检查今日是否已经显示过推荐
        return !this.hasShownToday();
    }

    hasShownToday() {
        const today = new Date().toDateString();
        const lastShownDate = localStorage.getItem('featureRecommendationLastShown');
        return lastShownDate === today;
    }

    markAsShownToday() {
        const today = new Date().toDateString();
        localStorage.setItem('featureRecommendationLastShown', today);
    }

    async checkAndShowRecommendation() {
        try {
            const response = await fetch(`${this.baseUrl}/feature_recommendations/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            // 检查是否应该显示推荐
            if (data.success && data.data && data.data.length > 0) {
                this.currentRecommendations = data.data;
                this.showRecommendationPopup();
            }
        } catch (error) {
            console.error('获取推荐失败:', error);
        }
    }

    showRecommendationPopup() {
        if (this.isPopupOpen) return;

        const recommendation = this.currentRecommendations[0]; // 显示第一个推荐
        if (!recommendation) return;

        this.currentSessionId = recommendation.metadata?.session_id || this.generateSessionId();
        this.isPopupOpen = true;

        // 创建弹窗HTML
        const popupHtml = this.createPopupHtml(recommendation);
        
        // 添加到页面
        document.body.insertAdjacentHTML('beforeend', popupHtml);
        
        // 绑定弹窗事件
        this.bindPopupEvents();
        
        // 显示动画
        setTimeout(() => {
            const popup = document.getElementById('feature-recommendation-popup');
            if (popup) {
                popup.classList.add('show');
            }
        }, 100);

        // 记录展示行为
        this.recordAction(recommendation.id, 'shown');
        
        // 标记为今日已显示
        this.markAsShownToday();
    }

    createPopupHtml(recommendation) {
        return `
            <div id="feature-recommendation-popup" class="feature-recommendation-popup">
                <div class="popup-overlay"></div>
                <div class="popup-content">
                    <div class="popup-header">
                        <h3><i class="fas fa-magic"></i> 猜你喜欢</h3>
                        <button class="close-btn" data-action="dismiss">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    <div class="popup-body">
                        <div class="feature-card">
                            <div class="feature-icon" style="color: ${recommendation.icon_color}">
                                <i class="${recommendation.icon_class}"></i>
                            </div>
                            <div class="feature-info">
                                <h4 class="feature-name">${recommendation.name}</h4>
                                <p class="feature-description">${recommendation.description}</p>
                                <div class="feature-meta">
                                    <span class="feature-category">${recommendation.category_display}</span>
                                    <span class="recommendation-reason">${recommendation.recommendation_reason}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="popup-footer">
                        <button class="btn btn-secondary" data-action="not_interested">
                            <i class="fas fa-thumbs-down"></i> 不感兴趣
                        </button>
                        <button class="btn btn-primary" data-action="clicked" data-url="${recommendation.url_name}">
                            <i class="fas fa-rocket"></i> 立即体验
                        </button>
                    </div>
                    
                    <div class="popup-tips">
                        <small><i class="fas fa-info-circle"></i> 我们会根据您的偏好优化推荐内容</small>
                    </div>
                </div>
            </div>
        `;
    }

    bindPopupEvents() {
        const popup = document.getElementById('feature-recommendation-popup');
        if (!popup) return;

        // 关闭按钮和遮罩层点击
        popup.addEventListener('click', (e) => {
            if (e.target.classList.contains('popup-overlay') || 
                e.target.classList.contains('close-btn') || 
                e.target.closest('.close-btn')) {
                this.closePopup('dismissed');
            }
        });

        // 按钮点击事件
        popup.addEventListener('click', (e) => {
            const action = e.target.dataset.action || e.target.closest('[data-action]')?.dataset.action;
            if (action) {
                e.preventDefault();
                this.handlePopupAction(action, e.target);
            }
        });

        // ESC键关闭
        document.addEventListener('keydown', this.handleEscKey.bind(this));
    }

    handlePopupAction(action, element) {
        const recommendation = this.currentRecommendations[0];
        if (!recommendation) return;

        switch (action) {
            case 'clicked':
                this.recordAction(recommendation.id, 'clicked');
                this.closePopup();
                // 使用URL解析API跳转到功能页面
                const urlName = element.dataset.url;
                if (urlName) {
                    this.navigateToFeature(urlName);
                }
                break;

            case 'not_interested':
                this.recordAction(recommendation.id, 'not_interested');
                this.closePopup();
                break;

            case 'dismiss':
                this.recordAction(recommendation.id, 'dismissed');
                this.closePopup();
                break;
        }
    }

    closePopup(action = 'dismissed') {
        const popup = document.getElementById('feature-recommendation-popup');
        if (!popup) return;

        popup.classList.add('closing');
        
        setTimeout(() => {
            popup.remove();
            this.isPopupOpen = false;
            document.removeEventListener('keydown', this.handleEscKey.bind(this));
        }, 300);
    }

    handleEscKey(e) {
        if (e.key === 'Escape' && this.isPopupOpen) {
            this.closePopup('dismissed');
        }
    }

    async recordAction(featureId, action) {
        try {
            const response = await fetch(`${this.baseUrl}/feature_recommendations/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    feature_id: featureId,
                    action: action,
                    session_id: this.currentSessionId
                })
            });

            const data = await response.json();
            if (!data.success) {
                console.warn('记录推荐行为失败:', data.error);
            }
        } catch (error) {
            console.error('记录推荐行为失败:', error);
        }
    }

    bindGlobalEvents() {
        // 可以在这里添加全局事件监听
        // 比如监听页面切换、用户行为等
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name=csrf-token]')?.content ||
                     document.querySelector('input[name=csrfmiddlewaretoken]')?.value;
        return token || '';
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // 手动触发推荐（用于测试或特殊场景）
    async showRecommendationManually(algorithm = 'smart') {
        try {
            const response = await fetch(`${this.baseUrl}/feature_recommendations/?algorithm=${algorithm}&force_show=true`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            const data = await response.json();
            
            // 检查是否有推荐
            if (data.status === 'success' && data.should_show) {
                // 将单个推荐转换为数组格式以兼容现有逻辑
                this.currentRecommendations = [data.data];
                this.showRecommendationPopup();
            } else {

            }
        } catch (error) {
            console.error('获取推荐失败:', error);
        }
    }

    // 使用URL解析API导航到功能页面
    async navigateToFeature(urlName) {
        try {
            const response = await fetch(`/tools/api/resolve-url/?url_name=${urlName}`);
            const data = await response.json();
            
            if (data.success) {
                window.location.href = data.url;
            } else {
                // 降级处理：直接拼接URL
                console.warn('URL解析失败，使用降级处理:', data.error);
                window.location.href = `/tools/${urlName}/`;
            }
        } catch (error) {
            console.error('URL解析API调用失败:', error);
            // 降级处理：直接拼接URL
            window.location.href = `/tools/${urlName}/`;
        }
    }
}

// 工具函数：获取功能列表
class FeatureDiscovery {
    constructor() {
        this.baseUrl = '/tools/api';
    }

    async getFeatures(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const url = `${this.baseUrl}/feature-list/${queryString ? '?' + queryString : ''}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            return await response.json();
        } catch (error) {
            console.error('获取功能列表失败:', error);
            return { success: false, error: error.message };
        }
    }

    async getRecommendationStats(days = 30) {
        try {
            const response = await fetch(`${this.baseUrl}/recommendation-stats/?days=${days}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            return await response.json();
        } catch (error) {
            console.error('获取推荐统计失败:', error);
            return { success: false, error: error.message };
        }
    }
}



// 导出类供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { FeatureRecommendation, FeatureDiscovery };
}

    // 页面加载完成后初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 初始化推荐系统
        window.featureRecommendation = new FeatureRecommendation();
        window.featureDiscovery = new FeatureDiscovery();
        
        // 添加调试方法到全局（仅在开发环境）
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            window.showRecommendation = () => window.featureRecommendation.showRecommendationManually();
        }
    });
})();
