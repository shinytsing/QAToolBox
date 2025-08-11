# Selenium社交媒体爬虫使用指南

## 概述

本项目已将社交媒体订阅功能升级为使用Selenium进行真实的网页爬取，特别针对B站等反爬机制严格的平台。Selenium可以模拟真实浏览器行为，有效绕过反爬限制。

## 主要特性

### 🔧 技术特性
- **真实浏览器模拟**: 使用Chrome浏览器进行网页爬取
- **反爬绕过**: 模拟真实用户行为，有效绕过反爬机制
- **智能等待**: 自动等待页面元素加载完成
- **错误处理**: 完善的异常处理和重试机制
- **资源优化**: 支持无头模式，减少资源消耗

### 📊 支持平台
- **B站 (bilibili)**: 完整支持，包括粉丝数、视频、关注数、资料变化
- **小红书 (xiaohongshu)**: 支持粉丝数、笔记更新
- **抖音 (douyin)**: 备用方案（模拟数据）
- **微博 (weibo)**: 备用方案（模拟数据）
- **网易云音乐 (netease)**: 备用方案（模拟数据）
- **知乎 (zhihu)**: 备用方案（模拟数据）

## 安装配置

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements/base.txt

# 或者单独安装selenium相关包
pip install selenium==4.20.0 webdriver-manager==4.0.1
```

### 2. 安装Chrome浏览器

确保系统已安装Chrome浏览器（推荐版本120+）

**macOS:**
```bash
# 使用Homebrew安装
brew install --cask google-chrome
```

**Ubuntu/Debian:**
```bash
# 下载并安装Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

**CentOS/RHEL:**
```bash
# 下载并安装Chrome
sudo yum install wget
wget https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
sudo yum localinstall google-chrome-stable_current_x86_64.rpm
```

### 3. ChromeDriver管理

项目使用`webdriver-manager`自动管理ChromeDriver，无需手动下载：

```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# 自动下载和管理ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

## 使用方法

### 1. 基本使用

```python
from apps.tools.services.social_media_crawler import SocialMediaCrawler

# 创建爬虫实例
crawler = SocialMediaCrawler()

# 爬取用户更新
updates = crawler.crawl_user_updates(subscription)
```

### 2. 直接使用Selenium爬虫

```python
from apps.tools.services.social_media_crawler import SeleniumSocialMediaCrawler

# 创建Selenium爬虫实例
selenium_crawler = SeleniumSocialMediaCrawler(headless=True)

# 爬取B站用户
updates = selenium_crawler.crawl_bilibili_user(subscription)

# 爬取小红书用户
updates = selenium_crawler.crawl_xiaohongshu_user(subscription)
```

### 3. 配置选项

```python
# 创建带配置的爬虫实例
selenium_crawler = SeleniumSocialMediaCrawler(
    headless=True,  # 无头模式，不显示浏览器窗口
    proxy="http://proxy.example.com:8080"  # 可选代理
)
```

## 平台特定配置

### B站 (bilibili)

**支持的监控类型:**
- `newPosts`: 新视频发布
- `newFollowers`: 粉丝数变化
- `newFollowing`: 关注数变化
- `profileChanges`: 个人资料变化

**CSS选择器配置:**
```python
'bilibili': {
    'base_url': 'https://space.bilibili.com',
    'user_info_selectors': {
        'follower_count': '.n-fans',
        'following_count': '.n-attention', 
        'video_count': '.n-video',
        'user_name': '.h-name',
        'user_sign': '.h-sign',
        'user_level': '.h-level'
    },
    'video_selectors': {
        'video_list': '.video-list .small-item',
        'video_title': '.title',
        'video_cover': '.cover img',
        'video_play_count': '.play',
        'video_danmaku': '.danmu',
        'video_upload_time': '.time'
    }
}
```

### 小红书 (xiaohongshu)

**支持的监控类型:**
- `newPosts`: 新笔记发布
- `newFollowers`: 粉丝数变化

**CSS选择器配置:**
```python
'xiaohongshu': {
    'base_url': 'https://www.xiaohongshu.com',
    'user_info_selectors': {
        'follower_count': '.follow-count',
        'following_count': '.following-count',
        'note_count': '.note-count',
        'user_name': '.user-name',
        'user_desc': '.user-desc'
    }
}
```

## 测试验证

### 运行测试脚本

```bash
# 测试selenium爬虫功能
python test_selenium_crawler.py
```

### 测试内容

1. **WebDriver Manager测试**: 验证ChromeDriver自动管理
2. **B站爬虫测试**: 使用真实B站用户ID进行测试
3. **小红书爬虫测试**: 测试小红书用户数据爬取
4. **主爬虫服务测试**: 验证完整的爬虫服务流程

## 性能优化

### 1. 浏览器配置优化

```python
chrome_options = Options()

# 无头模式
chrome_options.add_argument('--headless')

# 性能优化
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片加载

# 内存优化
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-logging')
```

### 2. 请求频率控制

```python
# 在爬取过程中添加延迟
import time
import random

# 随机延迟1-3秒
time.sleep(random.uniform(1, 3))

# 在检查多个订阅时添加延迟
for subscription in subscriptions:
    updates = crawler.crawl_user_updates(subscription)
    time.sleep(random.uniform(1, 2))  # 避免请求过于频繁
```

### 3. 资源管理

```python
# 确保正确关闭WebDriver
try:
    # 爬取操作
    updates = crawler.crawl_user_updates(subscription)
finally:
    # 清理资源
    crawler._close_driver()
```

## 错误处理

### 常见错误及解决方案

1. **ChromeDriver版本不匹配**
   ```
   解决方案: 使用webdriver-manager自动管理版本
   ```

2. **页面元素未找到**
   ```
   解决方案: 增加等待时间，检查CSS选择器是否正确
   ```

3. **反爬限制**
   ```
   解决方案: 增加延迟，使用代理，模拟真实用户行为
   ```

4. **内存不足**
   ```
   解决方案: 启用无头模式，禁用图片加载，及时关闭浏览器
   ```

### 日志配置

```python
import logging

# 配置日志级别
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 查看详细日志
logger.info("开始爬取用户数据...")
logger.error(f"爬取失败: {str(e)}")
```

## 部署注意事项

### 1. 服务器环境

- 确保服务器安装了Chrome浏览器
- 配置适当的用户权限
- 考虑使用Docker容器化部署

### 2. 资源监控

- 监控内存使用情况
- 定期清理临时文件
- 设置合理的并发限制

### 3. 安全考虑

- 使用代理池轮换IP
- 定期更新Chrome和ChromeDriver
- 监控异常访问模式

## 扩展开发

### 添加新平台支持

1. **在platform_configs中添加配置**
```python
'new_platform': {
    'base_url': 'https://example.com',
    'user_info_selectors': {
        'follower_count': '.follower-selector',
        # 其他选择器...
    }
}
```

2. **实现爬取方法**
```python
def crawl_new_platform_user(self, subscription: SocialMediaSubscription) -> List[Dict]:
    """爬取新平台用户数据"""
    # 实现爬取逻辑
    pass
```

3. **在主爬虫中添加支持**
```python
elif subscription.platform == 'new_platform':
    updates = self.selenium_crawler.crawl_new_platform_user(subscription)
```

## 故障排除

### 1. 检查Chrome安装

```bash
# 检查Chrome版本
google-chrome --version

# 检查ChromeDriver
chromedriver --version
```

### 2. 检查依赖安装

```bash
# 检查Python包
pip list | grep selenium
pip list | grep webdriver-manager
```

### 3. 测试基本功能

```python
# 简单测试
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get("https://www.bilibili.com")
print(driver.title)
driver.quit()
```

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持B站和小红书爬取
- 集成WebDriver Manager
- 完善的错误处理和日志记录

---

如有问题或建议，请提交Issue或联系开发团队。 