# 社交媒体爬虫改进说明

## 🚀 改进内容

### 1. 自动运行优化
- **智能调度**: 爬虫现在会根据每个订阅的检查频率自动调度
- **精确时间控制**: 严格按照订阅设置的检查频率运行
- **智能等待**: 根据最短频率计算下次检查时间
- **优雅退出**: 支持Ctrl+C优雅停止

### 2. 数据获取改进
- **区分粉丝和关注**: 明确区分新增粉丝数和新增关注数
- **更真实的数据**: 为每个平台生成更真实和丰富的内容
- **详细字段**: 添加了更多详细字段如头像、ID、数量等
- **平台特色**: 每个平台都有特色的内容类型和标签

### 3. 日志和监控
- **详细日志**: 添加了完整的日志记录系统
- **实时监控**: 可以实时查看爬虫运行状态
- **错误处理**: 完善的错误处理和恢复机制

## 📋 使用方法

### 启动自动爬虫
```bash
# 基本启动
python start_auto_crawler.py

# 指定日志文件
python start_auto_crawler.py --log /path/to/crawler.log

# 守护进程模式
python start_auto_crawler.py --daemon

# 仅检查订阅状态
python start_auto_crawler.py --check-only
```

### 使用Django管理命令
```bash
# 持续运行
python manage.py run_social_crawler --continuous

# 单次运行
python manage.py run_social_crawler

# 检查指定订阅
python manage.py run_social_crawler --subscription-id 1
```

### 测试爬虫功能
```bash
# 运行测试脚本
python test_crawler.py
```

## 🔧 配置说明

### 订阅检查频率
- 每个订阅可以设置不同的检查频率（分钟）
- 爬虫会根据最短频率进行调度
- 支持1-1440分钟（24小时）的频率设置

### 订阅类型
支持以下订阅类型：
- `newPosts`: 新发布内容
- `newFollowers`: 新增粉丝
- `newFollowing`: 新增关注
- `profileChanges`: 资料变化

### 支持的平台
- 小红书 (xiaohongshu)
- 抖音 (douyin)
- 微博 (weibo)
- B站 (bilibili)
- 知乎 (zhihu)
- 网易云音乐 (netease)

## 📊 数据字段说明

### 新发布内容 (newPosts)
```json
{
    "type": "newPosts",
    "title": "用户发布了新内容",
    "content": "内容描述",
    "post_content": "详细内容",
    "post_images": ["图片URL"],
    "post_tags": ["标签"],
    "post_likes": 点赞数,
    "post_comments": 评论数,
    "post_shares": 分享数,
    "external_url": "外部链接",
    "timestamp": "时间戳"
}
```

### 新增粉丝 (newFollowers)
```json
{
    "type": "newFollowers",
    "title": "用户获得了新粉丝",
    "content": "粉丝变化描述",
    "follower_name": "粉丝名称",
    "follower_avatar": "粉丝头像",
    "follower_id": "粉丝ID",
    "follower_count": "当前粉丝总数",
    "new_followers_count": "新增粉丝数",
    "timestamp": "时间戳"
}
```

### 新增关注 (newFollowing)
```json
{
    "type": "newFollowing",
    "title": "用户关注了新用户",
    "content": "关注变化描述",
    "following_name": "关注用户名称",
    "following_avatar": "关注用户头像",
    "following_id": "关注用户ID",
    "following_count": "当前关注总数",
    "new_following_count": "新增关注数",
    "timestamp": "时间戳"
}
```

## 🛠️ 故障排除

### 常见问题

1. **爬虫不运行**
   - 检查是否有活跃订阅
   - 确认订阅状态为 'active'
   - 检查数据库连接

2. **数据不准确**
   - 当前使用模拟数据
   - 实际项目中需要集成真实API
   - 检查订阅配置是否正确

3. **频率不准确**
   - 检查订阅的check_frequency设置
   - 确认last_check时间是否正确
   - 查看日志中的时间计算

### 日志查看
```bash
# 查看爬虫日志
tail -f crawler.log

# 查看Django日志
tail -f logs/django.log
```

## 🔄 更新日志

### v2.0.0 (当前版本)
- ✅ 修复自动运行逻辑
- ✅ 改进数据获取准确性
- ✅ 区分粉丝和关注数据
- ✅ 添加详细日志系统
- ✅ 优化错误处理
- ✅ 改进平台特色内容

### v1.0.0 (之前版本)
- 基础爬虫功能
- 简单的数据模拟
- 基本的调度逻辑

## 📝 注意事项

1. **数据模拟**: 当前版本使用模拟数据，实际部署时需要集成真实API
2. **频率限制**: 请合理设置检查频率，避免过于频繁的请求
3. **资源消耗**: 长时间运行会消耗系统资源，建议监控系统状态
4. **数据存储**: 确保数据库有足够空间存储通知数据

## 🤝 贡献

欢迎提交Issue和Pull Request来改进爬虫功能！ 