/**
 * QAToolBox 分享功能 JavaScript 库
 * 提供社交媒体分享、PWA安装、二维码生成等功能
 */

class ShareManager {
    constructor(options = {}) {
        this.options = {
            apiUrl: '/share/record/',
            csrfToken: this.getCookie('csrftoken'),
            ...options
        };
        
        this.deferredPrompt = null;
        this.init();
    }
    
    init() {
        // 监听PWA安装事件
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallButton();
        });
        
        // 监听PWA安装完成事件
        window.addEventListener('appinstalled', () => {
            this.hideInstallButton();
            this.showToast('应用安装成功！');
        });
    }
    
    /**
     * 分享到指定平台
     * @param {string} platform 平台名称
     * @param {string} url 分享URL
     * @param {string} title 分享标题
     * @param {string} description 分享描述
     * @param {string} imageUrl 分享图片
     */
    shareTo(platform, url, title, description, imageUrl) {
        const shareData = {
            platform,
            page_url: url,
            page_title: title || document.title
        };
        
        // 记录分享行为
        this.recordShare(shareData);
        
        // 根据平台类型执行不同的分享方式
        const shareConfig = this.getShareConfig(platform, url, title, description);
        
        switch (shareConfig.type) {
            case 'popup':
                this.openPopup(shareConfig.url, platform);
                break;
            case 'qrcode':
                this.showQRCode(shareConfig.url);
                break;
            case 'direct':
                window.location.href = shareConfig.url;
                break;
            case 'copy':
                this.copyToClipboard(url);
                break;
            case 'native':
                this.nativeShare(shareData);
                break;
        }
    }
    
    /**
     * 获取分享配置
     */
    getShareConfig(platform, url, title, description) {
        const encodedUrl = encodeURIComponent(url);
        const encodedTitle = encodeURIComponent(title || '');
        const encodedDescription = encodeURIComponent(description || '');
        
        const configs = {
            wechat: {
                name: '微信',
                icon: 'fab fa-weixin',
                color: '#07C160',
                url: `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodedUrl}`,
                type: 'qrcode'
            },
            weibo: {
                name: '微博',
                icon: 'fab fa-weibo',
                color: '#E6162D',
                url: `https://service.weibo.com/share/share.php?url=${encodedUrl}&title=${encodedTitle}`,
                type: 'popup'
            },
            douyin: {
                name: '抖音',
                icon: 'fab fa-tiktok',
                color: '#000000',
                url: `https://www.douyin.com/share?url=${encodedUrl}&title=${encodedTitle}`,
                type: 'popup'
            },
            xiaohongshu: {
                name: '小红书',
                icon: 'fas fa-book',
                color: '#FF2442',
                url: `https://www.xiaohongshu.com/share?url=${encodedUrl}&title=${encodedTitle}`,
                type: 'popup'
            },
            qq: {
                name: 'QQ',
                icon: 'fab fa-qq',
                color: '#12B7F5',
                url: `https://connect.qq.com/widget/shareqq/index.html?url=${encodedUrl}&title=${encodedTitle}&desc=${encodedDescription}`,
                type: 'popup'
            },
            linkedin: {
                name: 'LinkedIn',
                icon: 'fab fa-linkedin',
                color: '#0077B5',
                url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
                type: 'popup'
            },
            twitter: {
                name: 'Twitter',
                icon: 'fab fa-twitter',
                color: '#1DA1F2',
                url: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
                type: 'popup'
            },
            facebook: {
                name: 'Facebook',
                icon: 'fab fa-facebook',
                color: '#1877F2',
                url: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
                type: 'popup'
            },
            telegram: {
                name: 'Telegram',
                icon: 'fab fa-telegram',
                color: '#0088CC',
                url: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
                type: 'popup'
            },
            whatsapp: {
                name: 'WhatsApp',
                icon: 'fab fa-whatsapp',
                color: '#25D366',
                url: `https://wa.me/?text=${encodedTitle}%20${encodedUrl}`,
                type: 'popup'
            },
            email: {
                name: '邮件',
                icon: 'fas fa-envelope',
                color: '#EA4335',
                url: `mailto:?subject=${encodedTitle}&body=${encodedDescription}%0A%0A${encodedUrl}`,
                type: 'direct'
            },
            link: {
                name: '复制链接',
                icon: 'fas fa-link',
                color: '#6C757D',
                url: url,
                type: 'copy'
            },
            qrcode: {
                name: '二维码',
                icon: 'fas fa-qrcode',
                color: '#000000',
                url: `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodedUrl}`,
                type: 'qrcode'
            }
        };
        
        return configs[platform] || configs.link;
    }
    
    /**
     * 打开弹窗分享
     */
    openPopup(url, platform) {
        const width = 600;
        const height = 400;
        const left = (screen.width - width) / 2;
        const top = (screen.height - height) / 2;
        
        window.open(url, platform, 
            `width=${width},height=${height},left=${left},top=${top},scrollbars=yes,resizable=yes`
        );
    }
    
    /**
     * 显示二维码
     */
    showQRCode(url) {
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(url)}`;
        
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'qr-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(5px);
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
            position: relative;
        `;
        
        content.innerHTML = `
            <button onclick="this.closest('.qr-modal').remove()" style="
                position: absolute;
                top: 10px;
                right: 15px;
                background: none;
                border: none;
                font-size: 2rem;
                cursor: pointer;
                color: #666;
            ">&times;</button>
            <h3>扫码分享</h3>
            <img src="${qrUrl}" alt="二维码" style="max-width: 100%; height: auto; border-radius: 10px; margin: 20px 0;">
            <p>使用微信、支付宝等扫码分享</p>
        `;
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
        // 点击外部关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    /**
     * 复制到剪贴板
     */
    copyToClipboard(text) {
        this.copyTextOnly(text);
    }
    
        /**
     * 复制文本到剪贴板
     */
    copyTextOnly(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('链接已复制到剪贴板');
            }).catch(() => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }
    
    /**
     * 降级复制方案
     */
    fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showToast('链接已复制到剪贴板');
        } catch (err) {
            this.showToast('复制失败，请手动复制');
        }
        
        document.body.removeChild(textArea);
    }
    
    /**
     * 原生分享API
     */
    nativeShare(shareData) {
        if (navigator.share) {
            navigator.share({
                title: shareData.page_title,
                text: shareData.page_title,
                url: shareData.page_url
            }).then(() => {
                this.showToast('分享成功');
            }).catch((error) => {
                console.log('分享失败:', error);
            });
        } else {
            // 降级到弹窗分享
            this.showShareDialog(shareData);
        }
    }
    
    /**
     * 显示分享对话框
     */
    showShareDialog(shareData) {
        const platforms = ['wechat', 'weibo', 'douyin', 'xiaohongshu', 'qq', 'link'];
        const modal = document.createElement('div');
        modal.className = 'share-dialog';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const content = document.createElement('div');
        content.style.cssText = `
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            max-width: 400px;
            width: 90%;
        `;
        
        content.innerHTML = `
            <h3>选择分享方式</h3>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                ${platforms.map(platform => {
                    const config = this.getShareConfig(platform, shareData.page_url, shareData.page_title);
                    return `
                        <button onclick="shareManager.shareTo('${platform}', '${shareData.page_url}', '${shareData.page_title}'); this.closest('.share-dialog').remove();" style="
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            padding: 15px;
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            background: white;
                            cursor: pointer;
                            transition: all 0.3s ease;
                        " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <i class="${config.icon}" style="font-size: 2rem; color: ${config.color}; margin-bottom: 5px;"></i>
                            <span style="font-size: 0.8rem;">${config.name}</span>
                        </button>
                    `;
                }).join('')}
            </div>
            <button onclick="this.closest('.share-dialog').remove()" style="
                background: #666;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            ">取消</button>
        `;
        
        modal.appendChild(content);
        document.body.appendChild(modal);
        
        // 点击外部关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    /**
     * 记录分享行为
     */
    recordShare(shareData) {
        fetch(this.options.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.options.csrfToken
            },
            body: JSON.stringify(shareData)
        }).catch(error => {
            console.log('分享记录失败:', error);
        });
    }
    
    /**
     * 安装PWA
     */
    installPWA() {
        if (this.deferredPrompt) {
            this.deferredPrompt.prompt();
            this.deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    this.showToast('应用安装成功！');
                }
                this.deferredPrompt = null;
            });
        } else {
            this.showToast('请使用浏览器的安装功能');
        }
    }
    
    /**
     * 显示安装按钮
     */
    showInstallButton() {
        const installBtn = document.getElementById('installPWA');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }
    
    /**
     * 隐藏安装按钮
     */
    hideInstallButton() {
        const installBtn = document.getElementById('installPWA');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }
    
    /**
     * 显示提示消息
     */
    showToast(message, duration = 2000) {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, duration);
    }
    
    /**
     * 获取Cookie
     */
    getCookie(name) {
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
    
    /**
     * 检测是否为移动设备
     */
    isMobile() {
        return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }
    
    /**
     * 检测是否支持原生分享
     */
    supportsNativeShare() {
        return 'share' in navigator;
    }
}

// 全局分享管理器实例
window.shareManager = new ShareManager();

// 添加动画样式
if (!document.getElementById('share-animations')) {
    const style = document.createElement('style');
    style.id = 'share-animations';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ShareManager;
}
