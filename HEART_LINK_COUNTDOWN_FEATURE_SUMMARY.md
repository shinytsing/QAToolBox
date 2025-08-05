# 心动链接倒计时功能实现总结

## 功能概述

为心动链接功能添加了倒计时显示，提升用户体验：

1. **用户主动取消**：点击"取消匹配"按钮立即停止倒计时
2. **自动过期**：5分钟后自动过期，显示"请求已过期"
3. **实时倒计时**：前端显示剩余时间，格式为 (分:秒)
4. **匹配成功停止**：匹配成功后立即停止倒计时

## 后端修改

### 1. 模型过期时间调整

**文件**: `apps/tools/models.py`

```python
@property
def is_expired(self):
    """检查请求是否过期（5分钟）"""
    from django.utils import timezone
    from datetime import timedelta
    return timezone.now() > self.created_at + timedelta(minutes=5)
```

### 2. 用户活跃状态检查调整

**文件**: `apps/tools/views.py`

```python
def is_user_active(user):
    """检查用户是否活跃"""
    # 如果最后活跃时间超过5分钟，认为不活跃
    if timezone.now() - online_status.last_seen > timedelta(minutes=5):
        return False
    
    # 如果最后登录时间超过10分钟，认为不活跃
    if timezone.now() - user.last_login > timedelta(minutes=10):
        return False
    
    return True
```

### 3. 清理过期请求时间调整

**文件**: `apps/tools/views.py`

```python
def cleanup_expired_heart_link_requests():
    """清理过期的心动链接请求"""
    # 清理超过5分钟的pending请求
    expired_requests = HeartLinkRequest.objects.filter(
        status='pending',
        created_at__lt=timezone.now() - timedelta(minutes=5)
    )
```

### 4. 匹配超时时间调整

**文件**: `apps/tools/views.py`

```python
# 匹配时间阈值改为5分钟
match_time_threshold = timedelta(minutes=5)
```

## 前端修改

### 1. 倒计时变量

**文件**: `templates/tools/heart_link.html`

```javascript
let countdownInterval = null;
let expireTimeout = null;
```

### 2. 倒计时启动函数

```javascript
function startCountdown() {
    // 清除之前的倒计时
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    if (expireTimeout) {
        clearTimeout(expireTimeout);
    }
    
    // 设置5分钟倒计时
    let timeLeft = 5 * 60; // 5分钟 = 300秒
    
    const updateCountdown = () => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const statusDescription = document.getElementById('status-description');
        
        if (timeLeft > 0) {
            statusDescription.textContent = `正在等待其他用户响应... (${minutes}:${seconds.toString().padStart(2, '0')})`;
            timeLeft--;
        } else {
            // 倒计时结束，自动过期
            showNotification('匹配请求已过期', 'warning');
            resetUI();
        }
    };
    
    // 立即更新一次
    updateCountdown();
    
    // 每秒更新倒计时
    countdownInterval = setInterval(updateCountdown, 1000);
    
    // 5分钟后自动过期
    expireTimeout = setTimeout(() => {
        showNotification('匹配请求已过期', 'warning');
        resetUI();
    }, 5 * 60 * 1000);
}
```

### 3. 倒计时清理

在以下情况下会清理倒计时：

- **匹配成功时**：`handleMatchSuccess()` 函数
- **用户取消时**：`resetUI()` 函数
- **页面重置时**：`resetUI()` 函数

### 4. 倒计时启动

在 `startHeartLink()` 函数中，匹配请求创建成功后启动倒计时：

```javascript
// 启动倒计时
startCountdown();
```

## 功能测试

### 测试结果

✅ **创建匹配请求**：成功创建，ID: 40  
✅ **过期状态检查**：正确显示未过期  
✅ **状态API检查**：返回pending状态  
✅ **取消匹配请求**：成功取消  
✅ **取消后状态**：正确显示cancelled状态  

### 测试覆盖

1. **后端API测试**：使用Django测试客户端
2. **前端倒计时测试**：手动验证倒计时显示
3. **过期逻辑测试**：验证5分钟过期机制
4. **取消功能测试**：验证用户主动取消

## 用户体验

### 倒计时显示

- **格式**：`正在等待其他用户响应... (分:秒)`
- **更新频率**：每秒更新
- **示例**：`正在等待其他用户响应... (4:59)`

### 过期处理

- **自动过期**：5分钟后自动显示"匹配请求已过期"
- **手动取消**：点击取消按钮立即停止
- **匹配成功**：匹配成功后立即停止倒计时

### 通知提示

- **过期通知**：`匹配请求已过期` (warning类型)
- **取消通知**：`已取消匹配请求` (info类型)
- **匹配成功**：`匹配成功！` (success类型)

## 技术细节

### 时间设置

- **后端过期时间**：5分钟
- **用户活跃检查**：5分钟
- **清理间隔**：5分钟
- **匹配超时**：5分钟

### 前端倒计时

- **倒计时时长**：300秒（5分钟）
- **更新间隔**：1秒
- **显示格式**：分:秒（补零显示）

### 清理机制

- **定时器清理**：`clearInterval()` 和 `clearTimeout()`
- **变量重置**：`countdownInterval = null` 和 `expireTimeout = null`
- **UI重置**：状态文本和描述重置

## 总结

倒计时功能已成功实现，提供了：

1. **实时反馈**：用户可以看到剩余等待时间
2. **自动过期**：避免无限等待
3. **主动控制**：用户可以随时取消
4. **状态同步**：前后端状态保持一致

该功能显著提升了心动链接的用户体验，让用户对匹配过程有更清晰的预期和控制。 