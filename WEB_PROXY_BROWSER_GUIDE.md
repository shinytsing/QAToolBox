# Web代理浏览器使用指南

## 🌐 功能概述

Web代理浏览器是一个**无需安装任何软件**的在线代理服务，让用户直接在浏览器中访问外网，特别适合：

- 没有安装Clash的用户
- 临时需要访问外网的用户
- 不想配置复杂代理的用户
- 移动端用户

## 🚀 核心特性

### 1. 零安装使用
- **无需下载**：直接在浏览器中使用
- **无需配置**：自动检测和配置代理
- **即开即用**：输入网址即可访问

### 2. 智能代理
- **自动识别**：智能识别外网网站
- **自动代理**：外网自动使用代理，国内直连
- **故障转移**：代理失败时自动直连

### 3. 完整功能
- **全站访问**：支持所有网站类型
- **资源修复**：自动修复页面中的链接和资源
- **响应式设计**：支持各种设备

## 📱 使用方法

### 方法一：通过代理仪表板
1. 访问：`https://shenyiqing.xin/tools/proxy-dashboard/`
2. 找到"Web代理浏览器"卡片
3. 点击"打开Web浏览器"按钮

### 方法二：直接访问
1. 直接访问：`https://shenyiqing.xin/tools/web-proxy-browser/`
2. 在地址栏输入要访问的网址
3. 点击"访问"按钮

## 🎯 支持的外网网站

### 视频平台
- **YouTube** - 视频分享平台
- **Netflix** - 流媒体服务
- **Twitch** - 游戏直播

### 社交网络
- **Facebook** - 社交网络
- **Twitter** - 微博平台
- **Instagram** - 图片分享
- **Reddit** - 社区论坛

### 开发工具
- **GitHub** - 代码托管
- **Stack Overflow** - 技术问答

### 搜索引擎
- **Google** - 搜索引擎
- **Google Scholar** - 学术搜索

### 其他服务
- **Medium** - 文章平台
- **Telegram** - 即时通讯
- **Discord** - 游戏聊天
- **Spotify** - 音乐服务
- **Pinterest** - 图片收藏

## 🔧 技术原理

### 1. 代理检测
```python
def should_use_proxy(self, url):
    """判断是否需要使用代理"""
    proxy_domains = [
        'youtube.com', 'google.com', 'facebook.com', 
        'twitter.com', 'instagram.com', 'github.com'
    ]
    domain = urlparse(url).netloc.lower()
    return any(proxy_domain in domain for proxy_domain in proxy_domains)
```

### 2. 内容处理
- **链接修复**：将所有链接重写为代理链接
- **资源修复**：修复CSS、JS、图片等资源链接
- **相对路径**：处理相对路径和绝对路径

### 3. 代理配置
```python
proxy_config = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
```

## 📊 状态监控

### 代理状态检查
- **实时监控**：每30秒检查一次代理状态
- **状态显示**：显示代理IP和连接状态
- **故障提示**：代理不可用时显示提示

### 访问统计
- **成功率**：显示访问成功率
- **响应时间**：显示页面加载时间
- **代理使用**：显示是否使用了代理

## 🛠️ 故障排除

### 常见问题

#### 1. 页面无法加载
**原因**：代理服务未启动
**解决**：
- 检查ClashX Pro是否运行
- 访问Clash控制台启动服务
- 或使用直连模式

#### 2. 部分资源无法显示
**原因**：资源链接未正确修复
**解决**：
- 刷新页面重试
- 检查网络连接
- 尝试其他网站

#### 3. 访问速度慢
**原因**：代理节点速度慢
**解决**：
- 切换到其他代理节点
- 使用直连模式
- 检查网络状况

### 调试工具

#### 1. 代理测试
```javascript
// 测试代理连接
async function testProxy() {
    const response = await fetch('/tools/api/web-proxy-browser/test/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: 'https://www.youtube.com' })
    });
    const data = await response.json();
    console.log('测试结果:', data);
}
```

#### 2. 状态检查
```javascript
// 检查代理状态
async function checkStatus() {
    const response = await fetch('/tools/api/web-proxy-browser/status/');
    const data = await response.json();
    console.log('代理状态:', data);
}
```

## 💡 使用技巧

### 1. 快速访问
- 使用预设的快速链接
- 收藏常用网站
- 使用书签功能

### 2. 性能优化
- 关闭不必要的标签页
- 使用轻量级网站
- 避免同时访问多个视频网站

### 3. 安全建议
- 不要在代理浏览器中输入敏感信息
- 定期清理浏览器缓存
- 使用HTTPS网站

## 🔄 更新日志

### v1.0.0 (2025-09-03)
- ✅ 基础Web代理浏览器功能
- ✅ 智能代理检测
- ✅ 内容链接修复
- ✅ 响应式界面设计
- ✅ 实时状态监控
- ✅ 快速链接预设

## 📞 技术支持

如果遇到问题，可以：

1. **查看日志**：检查浏览器控制台错误信息
2. **测试连接**：使用内置的测试功能
3. **联系支持**：通过QAToolBox反馈问题

## 🎉 总结

Web代理浏览器为用户提供了**最简单、最便捷**的外网访问方式：

- **零门槛**：无需任何技术知识
- **零安装**：无需下载任何软件
- **零配置**：自动处理所有设置
- **零限制**：支持所有网站类型

无论是临时访问外网，还是长期使用，Web代理浏览器都是最佳选择！
