// 简单的拖拽测试脚本
console.log('简单拖拽测试脚本加载');

function createTestDraggable() {
    console.log('创建测试拖拽元素...');
    
    // 移除可能存在的旧元素
    const existing = document.getElementById('test-drag-element');
    if (existing) {
        existing.remove();
    }
    
    // 创建测试元素
    const testElement = document.createElement('div');
    testElement.id = 'test-drag-element';
    testElement.innerHTML = `
        <div style="
            position: fixed;
            top: 100px;
            right: 100px;
            width: 60px;
            height: 60px;
            background: #ff6b6b;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: move;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
            font-size: 24px;
        ">
            🔥
        </div>
    `;
    
    document.body.appendChild(testElement);
    
    const dragHandle = testElement.firstElementChild;
    let isDragging = false;
    let startX, startY, currentX = 0, currentY = 0;
    
    // 加载保存的位置
    const savedPos = localStorage.getItem('testDragPosition');
    if (savedPos) {
        const pos = JSON.parse(savedPos);
        dragHandle.style.transform = `translate(${pos.x}px, ${pos.y}px)`;
        currentX = pos.x;
        currentY = pos.y;
    }
    
    dragHandle.addEventListener('mousedown', (e) => {
        console.log('🔥 测试元素鼠标按下');
        isDragging = true;
        startX = e.clientX - currentX;
        startY = e.clientY - currentY;
        
        dragHandle.style.cursor = 'grabbing';
        dragHandle.style.transform += ' scale(1.1)';
        
        e.preventDefault();
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        
        console.log('🔥 测试元素拖拽中...');
        e.preventDefault();
        
        currentX = e.clientX - startX;
        currentY = e.clientY - startY;
        
        dragHandle.style.transform = `translate(${currentX}px, ${currentY}px) scale(1.1)`;
    });
    
    document.addEventListener('mouseup', () => {
        if (isDragging) {
            console.log('🔥 测试元素拖拽结束');
            isDragging = false;
            dragHandle.style.cursor = 'move';
            dragHandle.style.transform = `translate(${currentX}px, ${currentY}px)`;
            
            // 保存位置
            localStorage.setItem('testDragPosition', JSON.stringify({
                x: currentX,
                y: currentY
            }));
        }
    });
    
    console.log('✅ 测试拖拽元素创建完成！尝试拖拽红色圆圈🔥');
}

// 立即创建测试元素
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createTestDraggable);
} else {
    createTestDraggable();
}
