# 主题管理器使用文档

## 概述

主题管理器是一个独立的JavaScript模块，可以在您的项目中轻松实现主题切换功能。它提供了4种预设主题：极客模式、生活模式、狂暴模式和Emo模式。

## 快速开始

### 1. 引入文件

在您的HTML页面中引入主题管理器：

```html
<!-- 引入主题管理器 -->
<script src="/static/js/theme_manager.js"></script>
```

### 2. 基本使用

```javascript
// 切换到极客模式
ThemeManager.switchTheme('work');

// 切换到生活模式
ThemeManager.switchTheme('life');

// 切换到狂暴模式
ThemeManager.switchTheme('training');

// 切换到Emo模式
ThemeManager.switchTheme('emo');

// 获取当前主题
const currentTheme = ThemeManager.getCurrentTheme();
console.log('当前主题:', currentTheme);
```

### 3. 创建主题切换按钮

```html
<!-- 在您的页面中添加容器 -->
<div id="theme-buttons"></div>

<script>
// 创建主题切换按钮
ThemeManager.createThemeButtons('#theme-buttons');
</script>
```

## 可用主题

### 极客模式 (work)
- **背景**: 深蓝色渐变
- **颜色**: 浅灰色文字
- **适用场景**: 编程、技术工作

### 生活模式 (life)
- **背景**: 紫色渐变
- **颜色**: 白色文字
- **适用场景**: 日常使用、休闲

### 狂暴模式 (training)
- **背景**: 红色渐变
- **颜色**: 白色文字
- **适用场景**: 运动、激情活动

### Emo模式 (emo)
- **背景**: 灰色渐变
- **颜色**: 浅灰色文字
- **适用场景**: 情感表达、文艺

## API 参考

### 方法

#### `switchTheme(theme, saveToServer = true)`
切换主题
- `theme`: 主题名称 ('work', 'life', 'training', 'emo')
- `saveToServer`: 是否保存到服务器 (默认: true)
- 返回: Promise<boolean>

#### `getCurrentTheme()`
获取当前主题
- 返回: string

#### `getThemeConfig(theme)`
获取主题配置
- `theme`: 主题名称
- 返回: object | null

#### `getAvailableThemes()`
获取所有可用主题
- 返回: string[]

#### `createThemeButtons(containerSelector)`
创建主题切换按钮
- `containerSelector`: CSS选择器

### 事件

#### `themeChange`
主题切换时触发
```javascript
document.addEventListener('themeChange', (event) => {
    console.log('主题已切换:', event.detail.theme);
    console.log('主题配置:', event.detail.config);
});
```

## 键盘快捷键

- `Ctrl + 1`: 切换到极客模式
- `Ctrl + 2`: 切换到生活模式
- `Ctrl + 3`: 切换到狂暴模式
- `Ctrl + 4`: 切换到Emo模式

## 自定义主题

您可以通过修改 `ThemeManager.themes` 对象来添加自定义主题：

```javascript
// 添加自定义主题
ThemeManager.themes.custom = {
    name: '自定义主题',
    background: 'linear-gradient(135deg, #your-color-1, #your-color-2)',
    color: '#your-text-color',
    buttonColors: {
        primary: 'your-primary-color',
        secondary: 'your-secondary-color',
        success: 'your-success-color',
        danger: 'your-danger-color'
    }
};

// 切换到自定义主题
ThemeManager.switchTheme('custom');
```

## 服务器集成

主题管理器会自动保存主题偏好到服务器（如果API可用）：

### API 端点

- `POST /tools/api/theme/save/`: 保存主题偏好
- `GET /tools/api/theme/get/`: 获取主题偏好

### 请求格式

```javascript
// 保存主题
{
    "theme": "work"
}

// 响应格式
{
    "success": true,
    "theme": "work",
    "message": "主题偏好已保存: work"
}
```

## 样式变量

主题管理器会自动设置CSS变量，您可以在CSS中使用：

```css
.my-button {
    background: var(--theme-primary);
    color: white;
}

.my-secondary-button {
    background: var(--theme-secondary);
    color: white;
}
```

## 完整示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主题管理器示例</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            transition: all 0.3s ease;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .theme-section {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        
        .demo-button {
            padding: 10px 20px;
            margin: 5px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .demo-button:hover {
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>主题管理器示例</h1>
        
        <div class="theme-section">
            <h2>主题切换</h2>
            <div id="theme-buttons"></div>
        </div>
        
        <div class="theme-section">
            <h2>演示按钮</h2>
            <button class="demo-button" style="background: var(--theme-primary); color: white;">
                主要按钮
            </button>
            <button class="demo-button" style="background: var(--theme-secondary); color: white;">
                次要按钮
            </button>
            <button class="demo-button" style="background: var(--theme-success); color: black;">
                成功按钮
            </button>
            <button class="demo-button" style="background: var(--theme-danger); color: white;">
                危险按钮
            </button>
        </div>
        
        <div class="theme-section">
            <h2>当前主题信息</h2>
            <p>当前主题: <span id="current-theme-display"></span></p>
            <button onclick="showThemeInfo()" class="demo-button" style="background: var(--theme-primary); color: white;">
                显示主题信息
            </button>
        </div>
    </div>
    
    <!-- 引入主题管理器 -->
    <script src="/static/js/theme_manager.js"></script>
    
    <script>
        // 创建主题切换按钮
        ThemeManager.createThemeButtons('#theme-buttons');
        
        // 更新当前主题显示
        function updateCurrentThemeDisplay() {
            const display = document.getElementById('current-theme-display');
            const currentTheme = ThemeManager.getCurrentTheme();
            const config = ThemeManager.getThemeConfig(currentTheme);
            display.textContent = `${config.name} (${currentTheme})`;
        }
        
        // 显示主题信息
        function showThemeInfo() {
            const currentTheme = ThemeManager.getCurrentTheme();
            const config = ThemeManager.getThemeConfig(currentTheme);
            alert(`当前主题: ${config.name}\n主题代码: ${currentTheme}\n背景: ${config.background}`);
        }
        
        // 监听主题切换事件
        document.addEventListener('themeChange', (event) => {
            console.log('主题已切换:', event.detail.theme);
            updateCurrentThemeDisplay();
        });
        
        // 初始化显示
        updateCurrentThemeDisplay();
    </script>
</body>
</html>
```

## 注意事项

1. 主题管理器会自动保存主题偏好到localStorage
2. 如果服务器API不可用，主题切换仍然可以正常工作
3. 主题切换是即时的，无需刷新页面
4. 所有主题都支持响应式设计
5. 主题管理器兼容所有现代浏览器

## 故障排除

### 主题不生效
- 检查是否正确引入了 `theme_manager.js`
- 确认主题名称拼写正确
- 查看浏览器控制台是否有错误信息

### 按钮不显示
- 确认容器选择器正确
- 检查CSS样式是否被覆盖

### 服务器保存失败
- 检查网络连接
- 确认API端点正确
- 查看服务器日志
