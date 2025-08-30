/**
 * 聊天消息通知系统
 * 用于在右上角显示未读消息提示
 */

class ChatNotificationManager {
    constructor() {
        this.unreadCount = 0;
        this.notifications = [];
        this.isVisible = false;
        this.pollInterval = null;
        this.isDragging = false;
        this.currentX = 0;
        this.currentY = 0;
        this.xOffset = 0;
        this.yOffset = 0;
        this.init();
    }

    init() {
        this.createNotificationUI();
        this.startPolling();
        this.bindEvents();
    }

    createNotificationUI() {
        // 如果已存在，先移除
        const existing = document.getElementById('chat-notification-manager');
        if (existing) {
            existing.remove();
        }

        // 创建通知区域
        const notificationArea = document.createElement('div');
        notificationArea.id = 'chat-notification-manager';
        notificationArea.className = 'chat-notification-manager';
        notificationArea.innerHTML = `
            <div class="notification-icon" id="notification-icon">
                <i class="fas fa-comment-dots"></i>
                <span class="notification-badge" id="notification-badge" style="display: none;">0</span>
            </div>
            <div class="notification-dropdown" id="notification-dropdown" style="display: none;">
                <div class="notification-header">
                    <h3>未读消息</h3>
                    <button class="clear-all-btn" id="clear-all-notifications">全部标记已读</button>
                </div>
                <div class="drag-hint">
                    <small>💡 提示：拖拽图标可移动位置，双击可重置</small>
                </div>
                <div class="notification-list" id="notification-list">
                    <div class="no-notifications">暂无未读消息</div>
                </div>
            </div>
        `;

        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .chat-notification-manager {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                user-select: none;
                transition: none;
            }

            .chat-notification-manager.dragging {
                transition: none !important;
            }

            .notification-icon {
                position: relative;
                width: 50px;
                height: 50px;
                background: #007bff;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                cursor: move;
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
                transition: all 0.3s ease;
            }

            .notification-icon.dragging {
                cursor: grabbing;
                transform: scale(1.05);
                box-shadow: 0 8px 24px rgba(0, 123, 255, 0.5);
            }

            .notification-icon:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
            }

            .notification-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background: #dc3545;
                color: white;
                border-radius: 50%;
                min-width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                font-weight: bold;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .notification-dropdown {
                position: absolute;
                top: 60px;
                right: 0;
                width: 350px;
                max-height: 400px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                border: 1px solid #e9ecef;
                overflow: hidden;
            }

            .notification-header {
                background: #f8f9fa;
                padding: 15px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .notification-header h3 {
                margin: 0;
                font-size: 16px;
                color: #333;
            }

            .clear-all-btn {
                background: #6c757d;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-size: 12px;
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .clear-all-btn:hover {
                background: #5a6268;
            }

            .drag-hint {
                background: #e9ecef;
                padding: 8px 15px;
                border-bottom: 1px solid #dee2e6;
                text-align: center;
            }

            .drag-hint small {
                color: #6c757d;
                font-size: 11px;
            }

            .notification-list {
                max-height: 300px;
                overflow-y: auto;
            }

            .notification-item {
                padding: 12px 15px;
                border-bottom: 1px solid #f1f3f4;
                cursor: pointer;
                transition: background-color 0.2s;
            }

            .notification-item:hover {
                background: #f8f9fa;
            }

            .notification-item:last-child {
                border-bottom: none;
            }

            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }

            .notification-info {
                flex: 1;
            }

            .notification-sender {
                font-weight: bold;
                color: #007bff;
                font-size: 14px;
                margin-bottom: 4px;
            }

            .notification-message {
                color: #666;
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 4px;
            }

            .notification-time {
                color: #999;
                font-size: 11px;
            }

            .notification-room {
                color: #28a745;
                font-size: 12px;
                font-weight: 500;
            }

            .no-notifications {
                padding: 30px;
                text-align: center;
                color: #999;
                font-size: 14px;
            }

            .notification-count {
                background: #007bff;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-size: 11px;
                min-width: 16px;
                text-align: center;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(notificationArea);
    }

    bindEvents() {
        const icon = document.getElementById('notification-icon');
        const dropdown = document.getElementById('notification-dropdown');
        const clearAllBtn = document.getElementById('clear-all-notifications');
        const manager = document.getElementById('chat-notification-manager');

        // 加载保存的位置
        this.loadPosition();

        // 简化的拖拽事件处理
        let startX, startY, hasMoved = false;
        
        icon.addEventListener('mousedown', (e) => {
            console.log('鼠标按下开始拖拽');
            this.isDragging = true;
            hasMoved = false;
            startX = e.clientX - this.xOffset;
            startY = e.clientY - this.yOffset;
            
            icon.style.cursor = 'grabbing';
            manager.classList.add('dragging');
            
            e.preventDefault();
            e.stopPropagation();
        });

        document.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            
            console.log('正在拖拽移动');
            hasMoved = true;
            e.preventDefault();
            
            this.currentX = e.clientX - startX;
            this.currentY = e.clientY - startY;
            
            this.xOffset = this.currentX;
            this.yOffset = this.currentY;
            
            this.setTranslate(this.currentX, this.currentY);
        });

        document.addEventListener('mouseup', () => {
            if (this.isDragging) {
                console.log('拖拽结束，移动了吗:', hasMoved);
                this.isDragging = false;
                icon.style.cursor = 'move';
                manager.classList.remove('dragging');
                
                this.savePosition();
                
                // 如果有移动，延迟一点时间再允许点击
                if (hasMoved) {
                    setTimeout(() => {
                        // 重置移动标志
                        hasMoved = false;
                    }, 100);
                }
            }
        });

        // 点击图标切换显示/隐藏（只有在没有拖拽时才触发）
        icon.addEventListener('click', (e) => {
            console.log('click事件触发，isDragging:', this.isDragging, 'hasMoved:', hasMoved);
            e.stopPropagation();
            if (!this.isDragging && !hasMoved) {
                this.toggleDropdown();
            }
        });

        // 双击重置位置
        icon.addEventListener('dblclick', (e) => {
            e.stopPropagation();
            this.resetPosition();
        });

        // 点击其他地方关闭下拉框
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.chat-notification-manager')) {
                this.hideDropdown();
            }
        });

        // 清除所有通知
        clearAllBtn.addEventListener('click', () => {
            this.clearAllNotifications();
        });
    }



    setTranslate(xPos, yPos) {
        const manager = document.getElementById('chat-notification-manager');
        manager.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }



    savePosition() {
        localStorage.setItem('chatNotificationPosition', JSON.stringify({
            x: this.currentX,
            y: this.currentY
        }));
    }

    loadPosition() {
        const savedPosition = localStorage.getItem('chatNotificationPosition');
        if (savedPosition) {
            const position = JSON.parse(savedPosition);
            this.currentX = position.x;
            this.currentY = position.y;
            this.xOffset = this.currentX;
            this.yOffset = this.currentY;
            this.setTranslate(this.currentX, this.currentY);
        }
    }

    resetPosition() {
        this.currentX = 0;
        this.currentY = 0;
        this.xOffset = 0;
        this.yOffset = 0;
        this.setTranslate(0, 0);
        localStorage.removeItem('chatNotificationPosition');
        
        // 显示提示
        const icon = document.getElementById('notification-icon');
        icon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            icon.style.transform = '';
        }, 200);
    }

    startPolling() {
        // 立即获取一次
        this.fetchNotifications();
        
        // 每5秒轮询一次
        this.pollInterval = setInterval(() => {
            this.fetchNotifications();
        }, 5000);
    }

    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
        }
    }

    async fetchNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/summary/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.success) {
                        this.updateNotificationCount(data.total_unread);
                        
                        // 如果下拉框是打开的，获取详细通知
                        if (this.isVisible) {
                            this.fetchDetailedNotifications();
                        }
                    }
                } else {
                    console.warn('通知API返回了非JSON响应，可能用户未登录');
                }
            } else if (response.status === 403 || response.status === 401) {
                console.warn('通知API访问被拒绝，用户可能未登录');
            }
        } catch (error) {
            console.error('获取通知摘要失败:', error);
        }
    }

    async fetchDetailedNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/unread/', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const data = await response.json();
                    if (data.success) {
                        this.notifications = data.notifications;
                        this.updateNotificationList();
                    }
                } else {
                    console.warn('详细通知API返回了非JSON响应，可能用户未登录');
                }
            } else if (response.status === 403 || response.status === 401) {
                console.warn('详细通知API访问被拒绝，用户可能未登录');
            }
        } catch (error) {
            console.error('获取详细通知失败:', error);
        }
    }

    updateNotificationCount(count) {
        this.unreadCount = count;
        const badge = document.getElementById('notification-badge');
        
        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'flex';
        } else {
            badge.style.display = 'none';
        }
    }

    updateNotificationList() {
        const list = document.getElementById('notification-list');
        
        if (this.notifications.length === 0) {
            list.innerHTML = '<div class="no-notifications">暂无未读消息</div>';
            return;
        }

        const html = this.notifications.map(notification => `
            <div class="notification-item" onclick="chatNotificationManager.openChatRoom('${notification.room_id}')">
                <div class="notification-content">
                    <div class="notification-info">
                        <div class="notification-room">${notification.room_name}</div>
                        <div class="notification-sender">${notification.sender_username}</div>
                        <div class="notification-message">${notification.message_preview}</div>
                        <div class="notification-time">${this.formatTime(notification.created_at)}</div>
                    </div>
                </div>
            </div>
        `).join('');

        list.innerHTML = html;
    }

    toggleDropdown() {
        if (this.isVisible) {
            this.hideDropdown();
        } else {
            this.showDropdown();
        }
    }

    showDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        dropdown.style.display = 'block';
        this.isVisible = true;
        
        // 获取详细通知
        this.fetchDetailedNotifications();
    }

    hideDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        dropdown.style.display = 'none';
        this.isVisible = false;
    }

    async openChatRoom(roomId) {
        // 标记该聊天室的通知为已读
        await this.markRoomAsRead(roomId);
        
        // 跳转到聊天室
        window.location.href = `/tools/heart_link/chat/${roomId}/`;
    }

    async markRoomAsRead(roomId) {
        try {
            const response = await fetch('/tools/api/notifications/mark-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin',
                body: JSON.stringify({ room_id: roomId })
            });

            if (response.ok) {
                // 刷新通知
                this.fetchNotifications();
            }
        } catch (error) {
            console.error('标记已读失败:', error);
        }
    }

    async clearAllNotifications() {
        try {
            const response = await fetch('/tools/api/notifications/clear-all/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                this.updateNotificationCount(0);
                this.notifications = [];
                this.updateNotificationList();
                this.hideDropdown();
            }
        } catch (error) {
            console.error('清除通知失败:', error);
        }
    }

    formatTime(timeString) {
        const date = new Date(timeString);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return '刚刚';
        if (minutes < 60) return `${minutes}分钟前`;
        if (hours < 24) return `${hours}小时前`;
        if (days < 7) return `${days}天前`;
        
        return date.toLocaleDateString();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    destroy() {
        this.stopPolling();
        const element = document.getElementById('chat-notification-manager');
        if (element) {
            element.remove();
        }
    }
}

// 全局实例
let chatNotificationManager = null;

// 初始化通知管理器
document.addEventListener('DOMContentLoaded', function() {
    // 只在登录用户才启用通知
    if (document.querySelector('[name=csrfmiddlewaretoken]')) {
        chatNotificationManager = new ChatNotificationManager();
    }
});

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (chatNotificationManager) {
        chatNotificationManager.destroy();
    }
});
