/**
 * 移动端优化JavaScript
 * 提供移动端特有的交互和功能
 */

class MobileOptimization {
    constructor() {
        this.isMobile = this.detectMobile();
        this.isTouch = 'ontouchstart' in window;
        this.viewport = this.getViewport();
        
        this.init();
    }
    
    init() {
        if (this.isMobile) {
            this.setupMobileUI();
            this.setupTouchEvents();
            this.setupViewportFixes();
            this.setupPerformanceOptimizations();
            this.setupMobileNavigation();
            this.setupMobileForms();
            this.setupImageOptimization();
        }
        
        // 监听窗口变化
        window.addEventListener('resize', this.handleResize.bind(this));
        window.addEventListener('orientationchange', this.handleOrientationChange.bind(this));
    }
    
    // 检测移动设备
    detectMobile() {
        const userAgent = navigator.userAgent.toLowerCase();
        const mobileKeywords = [
            'android', 'iphone', 'ipad', 'ipod', 'blackberry', 
            'windows phone', 'opera mini', 'iemobile', 'mobile'
        ];
        
        return mobileKeywords.some(keyword => userAgent.includes(keyword)) || 
               window.innerWidth <= 768;
    }
    
    // 获取视口信息
    getViewport() {
        return {
            width: window.innerWidth,
            height: window.innerHeight,
            ratio: window.devicePixelRatio || 1
        };
    }
    
    // 设置移动端UI
    setupMobileUI() {
        document.body.classList.add('mobile-optimized');
        
        // 添加元标签
        this.addViewportMeta();
        
        // 添加移动端样式
        this.loadMobileCSS();
        
        // 设置触摸滚动
        document.body.style.webkitOverflowScrolling = 'touch';
    }
    
    // 添加视口元标签
    addViewportMeta() {
        let viewport = document.querySelector('meta[name="viewport"]');
        if (!viewport) {
            viewport = document.createElement('meta');
            viewport.name = 'viewport';
            document.head.appendChild(viewport);
        }
        
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
    }
    
    // 加载移动端CSS
    loadMobileCSS() {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/static/css/mobile.css';
        document.head.appendChild(link);
    }
    
    // 设置触摸事件
    setupTouchEvents() {
        // 防止双击缩放
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = new Date().getTime();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
        
        // 触摸反馈
        this.setupTouchFeedback();
        
        // 滑动手势
        this.setupSwipeGestures();
    }
    
    // 触摸反馈
    setupTouchFeedback() {
        const touchableElements = document.querySelectorAll(
            'button, .btn, .card, .tool-item, .nav-link, a'
        );
        
        touchableElements.forEach(element => {
            element.addEventListener('touchstart', (e) => {
                element.classList.add('touch-active');
            });
            
            element.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    element.classList.remove('touch-active');
                }, 150);
            });
            
            element.addEventListener('touchcancel', (e) => {
                element.classList.remove('touch-active');
            });
        });
    }
    
    // 滑动手势
    setupSwipeGestures() {
        let startX, startY, endX, endY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            
            this.handleSwipe(startX, startY, endX, endY);
            
            startX = startY = endX = endY = null;
        });
    }
    
    // 处理滑动
    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const threshold = 50;
        
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // 水平滑动
            if (Math.abs(deltaX) > threshold) {
                if (deltaX > 0) {
                    this.onSwipeRight();
                } else {
                    this.onSwipeLeft();
                }
            }
        } else {
            // 垂直滑动
            if (Math.abs(deltaY) > threshold) {
                if (deltaY > 0) {
                    this.onSwipeDown();
                } else {
                    this.onSwipeUp();
                }
            }
        }
    }
    
    // 滑动事件处理
    onSwipeLeft() {
        // 向左滑动 - 可以用于关闭侧边栏等
        const sidebar = document.querySelector('.mobile-sidebar');
        if (sidebar && sidebar.classList.contains('active')) {
            this.closeMobileSidebar();
        }
    }
    
    onSwipeRight() {
        // 向右滑动 - 可以用于打开侧边栏等
        if (window.location.pathname !== '/') {
            // 返回手势
            this.showSwipeBackHint();
        }
    }
    
    onSwipeUp() {
        // 向上滑动
        console.log('Swipe up detected');
    }
    
    onSwipeDown() {
        // 向下滑动 - 可以用于刷新
        if (window.scrollY === 0) {
            this.showPullToRefresh();
        }
    }
    
    // 视口修复
    setupViewportFixes() {
        // iOS Safari地址栏问题修复
        const fixIOSViewport = () => {
            if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            }
        };
        
        fixIOSViewport();
        window.addEventListener('resize', fixIOSViewport);
        
        // 阻止缩放
        document.addEventListener('gesturestart', (e) => {
            e.preventDefault();
        });
        
        document.addEventListener('gesturechange', (e) => {
            e.preventDefault();
        });
        
        document.addEventListener('gestureend', (e) => {
            e.preventDefault();
        });
    }
    
    // 性能优化
    setupPerformanceOptimizations() {
        // 图片懒加载
        this.setupLazyLoading();
        
        // 滚动节流
        this.setupScrollThrottle();
        
        // 预加载关键资源
        this.preloadCriticalResources();
    }
    
    // 图片懒加载
    setupLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
        } else {
            // 降级方案
            images.forEach(img => {
                img.src = img.dataset.src;
            });
        }
    }
    
    // 滚动节流
    setupScrollThrottle() {
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.onScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true });
    }
    
    // 滚动事件处理
    onScroll() {
        const scrollY = window.scrollY;
        
        // 显示/隐藏回到顶部按钮
        const backToTop = document.querySelector('.back-to-top');
        if (backToTop) {
            if (scrollY > 300) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        }
        
        // 导航栏滚动效果
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    }
    
    // 预加载关键资源
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/mobile.css',
            '/static/js/common.js'
        ];
        
        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = resource.endsWith('.css') ? 'style' : 'script';
            link.href = resource;
            document.head.appendChild(link);
        });
    }
    
    // 移动端导航
    setupMobileNavigation() {
        this.createMobileMenu();
        this.setupBottomNavigation();
    }
    
    // 创建移动端菜单
    createMobileMenu() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        // 创建菜单按钮
        const menuToggle = document.createElement('button');
        menuToggle.className = 'mobile-menu-toggle';
        menuToggle.innerHTML = '☰';
        menuToggle.setAttribute('aria-label', '打开菜单');
        
        // 创建移动端菜单
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'mobile-menu';
        mobileMenu.innerHTML = `
            <div class="mobile-menu-content">
                <button class="mobile-menu-close" aria-label="关闭菜单">×</button>
                <nav class="mobile-nav">
                    ${this.generateMobileNavItems()}
                </nav>
            </div>
        `;
        
        // 添加到页面
        navbar.appendChild(menuToggle);
        document.body.appendChild(mobileMenu);
        
        // 绑定事件
        menuToggle.addEventListener('click', () => this.openMobileMenu());
        mobileMenu.querySelector('.mobile-menu-close').addEventListener('click', () => this.closeMobileMenu());
        mobileMenu.addEventListener('click', (e) => {
            if (e.target === mobileMenu) {
                this.closeMobileMenu();
            }
        });
    }
    
    // 生成移动端导航项
    generateMobileNavItems() {
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        let items = '';
        
        navLinks.forEach(link => {
            items += `
                <a href="${link.href}" class="mobile-nav-item">
                    ${link.textContent}
                </a>
            `;
        });
        
        return items;
    }
    
    // 打开移动端菜单
    openMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }
    
    // 关闭移动端菜单
    closeMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-menu');
        if (mobileMenu) {
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        }
    }
    
    // 底部导航
    setupBottomNavigation() {
        const bottomNavItems = [
            { icon: '🏠', text: '首页', href: '/' },
            { icon: '🛠️', text: '工具', href: '/tools/' },
            { icon: '💬', text: '聊天', href: '/tools/chat/' },
            { icon: '👤', text: '我的', href: '/users/profile/' }
        ];
        
        const bottomNav = document.createElement('nav');
        bottomNav.className = 'bottom-nav';
        
        bottomNavItems.forEach(item => {
            const navItem = document.createElement('a');
            navItem.className = 'bottom-nav-item';
            navItem.href = item.href;
            navItem.innerHTML = `
                <div class="bottom-nav-icon">${item.icon}</div>
                <div class="bottom-nav-text">${item.text}</div>
            `;
            
            // 标记当前页面
            if (window.location.pathname === item.href) {
                navItem.classList.add('active');
            }
            
            bottomNav.appendChild(navItem);
        });
        
        document.body.appendChild(bottomNav);
        document.body.classList.add('has-bottom-nav');
    }
    
    // 移动端表单优化
    setupMobileForms() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            this.optimizeFormForMobile(form);
        });
    }
    
    // 优化表单
    optimizeFormForMobile(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // 阻止iOS自动缩放
            if (input.type === 'text' || input.type === 'email' || input.type === 'password') {
                input.style.fontSize = '16px';
            }
            
            // 添加适当的inputmode
            this.setInputMode(input);
            
            // 优化虚拟键盘
            this.optimizeVirtualKeyboard(input);
        });
        
        // 表单提交优化
        form.addEventListener('submit', (e) => {
            this.handleFormSubmit(e, form);
        });
    }
    
    // 设置输入模式
    setInputMode(input) {
        const inputModes = {
            'email': 'email',
            'tel': 'tel',
            'number': 'numeric',
            'url': 'url'
        };
        
        if (inputModes[input.type]) {
            input.setAttribute('inputmode', inputModes[input.type]);
        }
    }
    
    // 优化虚拟键盘
    optimizeVirtualKeyboard(input) {
        // 数字输入
        if (input.type === 'number' || input.classList.contains('numeric')) {
            input.setAttribute('pattern', '[0-9]*');
        }
        
        // 电话输入
        if (input.type === 'tel') {
            input.setAttribute('pattern', '[0-9-+()\\s]*');
        }
        
        // 邮箱输入
        if (input.type === 'email') {
            input.setAttribute('autocomplete', 'email');
        }
    }
    
    // 处理表单提交
    handleFormSubmit(e, form) {
        // 显示加载状态
        const submitButton = form.querySelector('[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="loading-spinner"></span> 提交中...';
        }
        
        // 隐藏虚拟键盘
        document.activeElement.blur();
    }
    
    // 图片优化
    setupImageOptimization() {
        // 创建图片查看器
        this.createImageViewer();
        
        // 优化图片加载
        this.optimizeImageLoading();
    }
    
    // 创建图片查看器
    createImageViewer() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            if (img.classList.contains('zoomable')) {
                img.addEventListener('click', () => {
                    this.openImageViewer(img.src);
                });
            }
        });
    }
    
    // 打开图片查看器
    openImageViewer(src) {
        const viewer = document.createElement('div');
        viewer.className = 'image-viewer';
        viewer.innerHTML = `
            <img src="${src}" alt="查看图片">
            <button class="image-viewer-close" aria-label="关闭">×</button>
        `;
        
        document.body.appendChild(viewer);
        document.body.style.overflow = 'hidden';
        
        // 绑定关闭事件
        viewer.querySelector('.image-viewer-close').addEventListener('click', () => {
            this.closeImageViewer(viewer);
        });
        
        viewer.addEventListener('click', (e) => {
            if (e.target === viewer) {
                this.closeImageViewer(viewer);
            }
        });
    }
    
    // 关闭图片查看器
    closeImageViewer(viewer) {
        viewer.remove();
        document.body.style.overflow = '';
    }
    
    // 优化图片加载
    optimizeImageLoading() {
        const images = document.querySelectorAll('img');
        
        images.forEach(img => {
            // 添加加载状态
            img.addEventListener('loadstart', () => {
                img.classList.add('loading');
            });
            
            img.addEventListener('load', () => {
                img.classList.remove('loading');
                img.classList.add('loaded');
            });
            
            img.addEventListener('error', () => {
                img.classList.remove('loading');
                img.classList.add('error');
            });
        });
    }
    
    // 窗口大小变化处理
    handleResize() {
        this.viewport = this.getViewport();
        
        // 重新检测是否为移动设备
        const wasMobile = this.isMobile;
        this.isMobile = this.detectMobile();
        
        if (wasMobile !== this.isMobile) {
            location.reload(); // 切换设备类型时重新加载
        }
    }
    
    // 屏幕方向变化处理
    handleOrientationChange() {
        // 延迟处理，等待方向变化完成
        setTimeout(() => {
            this.viewport = this.getViewport();
            
            // 修复iOS viewport问题
            if (/iPad|iPhone|iPod/.test(navigator.userAgent)) {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            }
        }, 500);
    }
    
    // 显示滑动返回提示
    showSwipeBackHint() {
        // 可以显示一个提示用户可以滑动返回的UI
        console.log('Swipe back hint');
    }
    
    // 显示下拉刷新
    showPullToRefresh() {
        // 实现下拉刷新功能
        console.log('Pull to refresh');
    }
    
    // 公共方法：显示Toast
    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        // 自动移除
        setTimeout(() => {
            toast.remove();
        }, duration);
    }
    
    // 公共方法：显示加载状态
    showLoading(message = '加载中...') {
        const loading = document.createElement('div');
        loading.className = 'loading-overlay';
        loading.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(loading);
        return loading;
    }
    
    // 公共方法：隐藏加载状态
    hideLoading(loadingElement) {
        if (loadingElement && loadingElement.parentNode) {
            loadingElement.remove();
        }
    }
}

// 初始化移动端优化
document.addEventListener('DOMContentLoaded', () => {
    window.mobileOptimization = new MobileOptimization();
});

// 导出供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobileOptimization;
}
