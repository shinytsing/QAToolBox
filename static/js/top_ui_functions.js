// 顶部栏功能函数库
// 确保所有函数在全局作用域中可用

// 主题切换功能
function toggleTheme() {
    const badge = document.getElementById('topUiBadge');
    if (!badge) {
        console.warn('主题标识元素未找到');
        return;
    }
    
    const themes = ['模式', '生活', '狂暴', 'Emo'];
    const themeModes = ['work', 'life', 'training', 'emo'];
    const currentTheme = badge.textContent;
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    const nextTheme = themes[nextIndex];
    const nextMode = themeModes[nextIndex];
    
    badge.textContent = nextTheme;
    
    // 调用主题切换API
    if (typeof switchTheme === 'function') {
        switchTheme(nextMode);
    } else {
        // 如果没有switchTheme函数，直接更新页面主题
        updatePageTheme(nextMode);
    }

}

// 主题切换函数
function switchTheme(theme) {
    // 发送主题切换请求到后端
    fetch('/users/theme/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            mode: theme  // 修改参数名从 theme 改为 mode
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 更新页面主题
            updatePageTheme(theme);

        } else {
            console.error('主题切换失败:', data.error);
        }
    })
    .catch(error => {
        console.error('主题切换请求失败:', error);
        // 如果请求失败，仍然更新本地主题
        updatePageTheme(theme);
    });
}

// 更新页面主题
function updatePageTheme(theme) {
    // 移除所有主题类
    document.body.classList.remove('theme-work', 'theme-life', 'theme-training', 'theme-emo');
    
    // 添加新主题类
    document.body.classList.add(`theme-${theme}`);
    
    // 动态加载主题CSS文件
    loadThemeCSS(theme);
    
    // 更新主题标识
    const badge = document.getElementById('topUiBadge');
    const themeNames = {
        'work': '极客模式',
        'life': '生活模式', 
        'training': '狂暴模式',
        'emo': 'Emo模式'
    };
    if (badge && themeNames[theme]) {
        badge.textContent = themeNames[theme];
    }
}

// 动态加载主题CSS文件
function loadThemeCSS(theme) {
    const themeCSSMap = {
        'work': '/static/geek.css',
        'life': '/static/life.css',
        'training': '/static/rage.css',
        'emo': '/static/emo.css'
    };
    
    const cssUrl = themeCSSMap[theme];
    if (!cssUrl) return;
    
    // 移除之前的主题CSS
    const existingLink = document.querySelector(`link[href*="${themeCSSMap[theme]}"]`);
    if (existingLink) {
        existingLink.remove();
    }
    
    // 添加新的主题CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.type = 'text/css';
    link.href = cssUrl;
    link.id = `theme-css-${theme}`;
    document.head.appendChild(link);

}

// 显示设置面板
function showSettings() {

    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.style.display = 'block';

    } else {
        // 如果模态框不存在，创建一个

        createSettingsModal();
    }
}

// 切换移动菜单
function toggleMobileMenu() {
    const menuModal = document.getElementById('menuModal');
    if (menuModal) {
        menuModal.style.display = 'block';
    } else {
        // 如果菜单模态框不存在，创建一个
        createMenuModal();
    }
}

// 隐藏顶部UI
function hideTopUI() {
    const topUiBar = document.getElementById('topUiBar');
    if (topUiBar) {
        topUiBar.style.setProperty('transform', 'translateY(-100%)', 'important');
        topUiBar.style.setProperty('opacity', '0', 'important');

        // 3秒后自动显示
        setTimeout(() => {
            topUiBar.style.setProperty('transform', 'translateY(0)', 'important');
            topUiBar.style.setProperty('opacity', '1', 'important');

        }, 3000);
    } else {
        console.error('❌ 未找到topUiBar元素');
    }
}

// 悬浮显示用户下拉菜单
let hideDropdownTimer = null;

function showUserDropdown() {

    // 清除隐藏定时器
    if (hideDropdownTimer) {
        clearTimeout(hideDropdownTimer);
        hideDropdownTimer = null;
    }
    
    const dropdownContent = document.getElementById('userDropdownContent');
    const chevronIcon = document.querySelector('.top-ui-user .fa-chevron-down');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    // 显示菜单
    dropdownContent.style.display = 'block';
    dropdownContent.style.opacity = '1';
    dropdownContent.style.transform = 'scale(1) translateY(0)';
    dropdownContent.classList.add('show');
    
    if (chevronIcon) {
        chevronIcon.style.transform = 'rotate(180deg)';
    }

}

function hideUserDropdownDelayed() {

    // 设置延迟隐藏定时器
    hideDropdownTimer = setTimeout(() => {
        hideUserDropdown();
    }, 300);
}

function hideUserDropdown() {

    const dropdownContent = document.getElementById('userDropdownContent');
    const chevronIcon = document.querySelector('.top-ui-user .fa-chevron-down');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    // 隐藏菜单
    dropdownContent.style.display = 'none';
    dropdownContent.style.opacity = '0';
    dropdownContent.style.transform = 'scale(0.95) translateY(-10px)';
    dropdownContent.classList.remove('show');
    
    if (chevronIcon) {
        chevronIcon.style.transform = 'rotate(0deg)';
    }

}

// 保留切换函数用于调试
function toggleUserDropdown() {

    const dropdownContent = document.getElementById('userDropdownContent');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    const isVisible = dropdownContent.style.display === 'block' && 
                     dropdownContent.style.opacity !== '0' &&
                     !dropdownContent.classList.contains('hidden');
    
    if (isVisible) {
        hideUserDropdown();
    } else {
        showUserDropdown();
    }
}

// 创建设置模态框
function createSettingsModal() {
    const modal = document.createElement('div');
    modal.id = 'settingsModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, rgba(255, 182, 193, 0.95) 0%, rgba(255, 105, 180, 0.95) 50%, rgba(138, 43, 226, 0.95) 100%); 
                    border-radius: 15px; 
                    padding: 30px; 
                    max-width: 500px; 
                    width: 90%; 
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 32px rgba(255, 182, 193, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h3 style="margin: 0; font-size: 1.5rem;">⚙️ 设置</h3>
                <button onclick="closeSettingsModal()" style="background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer;">×</button>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600;">🎨 主题模式</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button onclick="switchTheme('work')" class="theme-btn" data-theme="work" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-weight: 600;">工作模式</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">专注技术</div>
                    </button>
                    <button onclick="switchTheme('life')" class="theme-btn" data-theme="life" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-weight: 600;">生活模式</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">轻松愉悦</div>
                    </button>
                    <button onclick="switchTheme('training')" class="theme-btn" data-theme="training" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-weight: 600;">狂暴模式</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">激情四射</div>
                    </button>
                    <button onclick="switchTheme('emo')" class="theme-btn" data-theme="emo" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <div style="font-weight: 600;">Emo模式</div>
                        <div style="font-size: 0.8rem; opacity: 0.8;">情感表达</div>
                    </button>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; font-weight: 600;">🎵 音乐控制</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <button onclick="toggleMusic()" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <i class="fas fa-play" style="margin-right: 8px;"></i>播放/暂停
                    </button>
                    <button onclick="nextSong()" style="padding: 12px; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease;">
                        <i class="fas fa-forward" style="margin-right: 8px;"></i>下一首
                    </button>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 25px;">
                <button onclick="closeSettingsModal()" style="padding: 12px 30px; border-radius: 8px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease; font-weight: 600;">完成</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// 创建菜单模态框
function createMenuModal() {
    const modal = document.createElement('div');
    modal.id = 'menuModal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 10000;
        display: flex;
        justify-content: center;
        align-items: center;
    `;
    
    modal.innerHTML = `
        <div style="background: linear-gradient(135deg, rgba(255, 182, 193, 0.95) 0%, rgba(255, 105, 180, 0.95) 50%, rgba(138, 43, 226, 0.95) 100%); 
                    border-radius: 15px; 
                    padding: 30px; 
                    max-width: 600px; 
                    width: 90%; 
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 32px rgba(255, 182, 193, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px;">
                <h3 style="margin: 0; font-size: 1.5rem;">🧭 导航菜单</h3>
                <button onclick="closeMenuModal()" style="background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer;">×</button>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 25px;">
                <button onclick="window.location.href='/' + (window.location.pathname.includes('life_mode') ? 'life_mode/' : '')" class="menu-item" style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                    <i class="fas fa-home" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                    <div style="font-weight: 600;">首页</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">返回主页</div>
                </button>
                <button onclick="window.location.href='/tools/' + (window.location.pathname.includes('life_mode') ? 'life_mode/' : '')" class="menu-item" style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                    <i class="fas fa-tools" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                    <div style="font-weight: 600;">工具集</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">实用工具</div>
                </button>
                <button onclick="window.location.href='/tools/chat/' + (window.location.pathname.includes('life_mode') ? 'life_mode/' : '')" class="menu-item" style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                    <i class="fas fa-comments" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                    <div style="font-weight: 600;">聊天室</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">实时交流</div>
                </button>
                <button onclick="window.location.href='/tools/heart_link/' + (window.location.pathname.includes('life_mode') ? 'life_mode/' : '')" class="menu-item" style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.1); color: white; border: 1px solid rgba(255, 255, 255, 0.3); transition: all 0.3s ease; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                    <i class="fas fa-heart" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                    <div style="font-weight: 600;">心链匹配</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">寻找伙伴</div>
                </button>
            </div>
            
            <div style="text-align: center; margin-top: 25px;">
                <button onclick="closeMenuModal()" style="padding: 12px 30px; border-radius: 8px; background: rgba(255, 255, 255, 0.2); color: white; border: 1px solid rgba(255, 255, 255, 0.3); cursor: pointer; transition: all 0.3s ease; font-weight: 600;">关闭</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// 关闭设置模态框
function closeSettingsModal() {
    const modal = document.getElementById('settingsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 关闭菜单模态框
function closeMenuModal() {
    const modal = document.getElementById('menuModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 获取CSRF Token
function getCSRFToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// 音乐控制函数（占位符）
function toggleMusic() {

    alert('音乐控制功能开发中...');
}

function nextSong() {

    alert('下一首歌曲功能开发中...');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {

    // 添加模态框按钮悬停效果
    document.addEventListener('mouseover', function(e) {
        if (e.target.classList.contains('menu-item') || e.target.classList.contains('theme-btn')) {
            e.target.style.transform = 'translateY(-2px)';
            e.target.style.boxShadow = '0 8px 25px rgba(255, 255, 255, 0.2)';
            e.target.style.background = 'rgba(255, 255, 255, 0.15)';
        }
    });
    
    document.addEventListener('mouseout', function(e) {
        if (e.target.classList.contains('menu-item') || e.target.classList.contains('theme-btn')) {
            e.target.style.transform = 'translateY(0)';
            e.target.style.boxShadow = 'none';
            e.target.style.background = 'rgba(255, 255, 255, 0.1)';
        }
    });
    
    // 点击其他地方关闭下拉菜单和模态框
    document.addEventListener('click', function(event) {
        const userDropdown = document.querySelector('.top-ui-user-dropdown');
        const dropdownContent = document.getElementById('userDropdownContent');
        
        if (userDropdown && dropdownContent) {
            if (!userDropdown.contains(event.target)) {
                dropdownContent.classList.remove('show');
            }
        }
        
        // 关闭设置模态框
        const settingsModal = document.getElementById('settingsModal');
        if (settingsModal && event.target === settingsModal) {
            settingsModal.style.display = 'none';
        }
        
        // 关闭菜单模态框
        const menuModal = document.getElementById('menuModal');
        if (menuModal && event.target === menuModal) {
            menuModal.style.display = 'none';
        }
    });
});
