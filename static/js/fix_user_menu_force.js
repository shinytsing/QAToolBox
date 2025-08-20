// 强制修复用户菜单问题
console.log('🔧 加载强制修复脚本');

// 等待页面完全加载
window.addEventListener('load', function() {
    console.log('🔧 页面完全加载，开始强制修复');
    
    // 强制修复用户菜单
    forceFixUserMenu();
    

});

// 强制修复用户菜单
function forceFixUserMenu() {
    console.log('🔧 开始强制修复用户菜单');
    
    const dropdownContent = document.getElementById('userDropdownContent');
    const userButton = document.querySelector('.top-ui-user');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    if (!userButton) {
        console.error('❌ 用户头像按钮未找到');
        return;
    }
    
    console.log('✅ 找到菜单元素和按钮');
    
    // 强制设置初始状态
    dropdownContent.style.display = 'none';
    dropdownContent.style.opacity = '0';
    dropdownContent.style.transform = 'scale(0.95) translateY(-10px)';
    dropdownContent.classList.remove('show');
    
    // 移除可能冲突的事件监听器
    const newUserButton = userButton.cloneNode(true);
    userButton.parentNode.replaceChild(newUserButton, userButton);
    
    // 重新绑定点击事件
    newUserButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔧 用户头像被点击');
        forceToggleUserDropdown();
    });
    
    console.log('✅ 用户菜单强制修复完成');
}

// 强制切换用户菜单
function forceToggleUserDropdown() {
    console.log('🔧 forceToggleUserDropdown 被调用');
    
    const dropdownContent = document.getElementById('userDropdownContent');
    const chevronIcon = document.querySelector('.top-ui-user .fa-chevron-down');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    // 检查当前显示状态
    const isVisible = dropdownContent.style.display === 'block' || 
                     dropdownContent.style.opacity === '1' ||
                     dropdownContent.classList.contains('show');
    
    console.log('当前菜单状态:', {
        display: dropdownContent.style.display,
        opacity: dropdownContent.style.opacity,
        isVisible: isVisible
    });
    
    if (isVisible) {
        // 隐藏菜单
        dropdownContent.style.display = 'none';
        dropdownContent.style.opacity = '0';
        dropdownContent.style.transform = 'scale(0.95) translateY(-10px)';
        dropdownContent.classList.remove('show');
        
        if (chevronIcon) {
            chevronIcon.style.transform = 'rotate(0deg)';
        }
        
        console.log('✅ 菜单已隐藏');
    } else {
        // 显示菜单
        dropdownContent.style.display = 'block';
        dropdownContent.style.opacity = '1';
        dropdownContent.style.transform = 'scale(1) translateY(0)';
        dropdownContent.classList.add('show');
        
        if (chevronIcon) {
            chevronIcon.style.transform = 'rotate(180deg)';
        }
        
        console.log('✅ 菜单已显示');
    }
}



// 导出函数到全局作用域
window.forceToggleUserDropdown = forceToggleUserDropdown;

console.log('✅ 强制修复脚本加载完成');
