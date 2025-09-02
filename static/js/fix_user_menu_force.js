// 强制修复用户菜单问题

// 等待页面完全加载
window.addEventListener('load', function() {

    // 强制修复用户菜单
    forceFixUserMenu();
    

});

// 强制修复用户菜单
function forceFixUserMenu() {

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

        forceToggleUserDropdown();
    });

}

// 强制切换用户菜单
function forceToggleUserDropdown() {

    const dropdownContent = document.getElementById('userDropdownContent');
    const chevronIcon = document.querySelector('.top-ui-user .fa-chevron-down');
    
    if (!dropdownContent) {
        console.error('❌ 用户下拉菜单元素未找到');
        return;
    }
    
    // 检查当前显示状态
    const isVisible = dropdownContent.style.display === 'block' && 
                     dropdownContent.style.opacity !== '0' &&
                     !dropdownContent.classList.contains('hidden');

    if (isVisible) {
        // 隐藏菜单
        dropdownContent.style.display = 'none';
        dropdownContent.style.opacity = '0';
        dropdownContent.style.transform = 'scale(0.95) translateY(-10px)';
        dropdownContent.classList.remove('show');
        
        if (chevronIcon) {
            chevronIcon.style.transform = 'rotate(0deg)';
        }

    } else {
        // 显示菜单
        dropdownContent.style.display = 'block';
        dropdownContent.style.opacity = '1';
        dropdownContent.style.transform = 'scale(1) translateY(0)';
        dropdownContent.classList.add('show');
        
        if (chevronIcon) {
            chevronIcon.style.transform = 'rotate(180deg)';
        }

    }
}



// 导出函数到全局作用域
window.forceToggleUserDropdown = forceToggleUserDropdown;
