# 社交媒体订阅功能

## 功能概述

社交媒体订阅功能允许用户订阅主流社交媒体平台的用户动态，实时获取最新更新和变化提醒。

## 支持的平台

- **小红书** - 时尚、生活方式内容
- **抖音** - 短视频内容
- **网易云音乐** - 音乐动态
- **微博** - 社交动态
- **B站** - 视频内容
- **知乎** - 问答和文章

## 订阅类型

1. **新动态** - 用户发布的新内容
2. **新关注** - 用户新增的关注者
3. **资料变化** - 用户资料更新

## 功能特性

### 1. 订阅管理
- 添加新订阅
- 暂停/启用订阅
- 取消订阅
- 设置检查频率（5分钟、15分钟、30分钟、1小时）

### 2. 实时通知
- 站内通知系统
- 通知分类过滤
- 标记已读功能
- 通知统计

### 3. 数据统计
- 总订阅数
- 活跃订阅数
- 新通知数量

## 技术架构

### 后端模型

#### SocialMediaSubscription（订阅模型）
```python
- user: 订阅用户
- platform: 平台类型
- target_user_id: 目标用户ID
- target_user_name: 目标用户名
- subscription_types: 订阅类型列表
- check_frequency: 检查频率
- status: 状态（活跃/暂停/错误）
- last_check: 最后检查时间
- avatar_url: 头像URL
```

#### SocialMediaNotification（通知模型）
```python
- subscription: 关联订阅
- notification_type: 通知类型
- title: 通知标题
- content: 通知内容
- is_read: 是否已读
- created_at: 创建时间
```

### API接口

#### 订阅管理
- `POST /tools/api/social-subscription/add/` - 添加订阅
- `GET /tools/api/social-subscription/list/` - 获取订阅列表
- `POST /tools/api/social-subscription/update/` - 更新订阅状态

#### 通知管理
- `GET /tools/api/social-subscription/notifications/` - 获取通知列表
- `POST /tools/api/social-subscription/mark-read/` - 标记通知已读
- `GET /tools/api/social-subscription/stats/` - 获取统计信息

### 爬虫服务

#### SocialMediaCrawler
- 支持多平台数据爬取
- 模拟真实API调用
- 智能频率控制
- 错误处理和重试机制

#### NotificationService
- 通知创建和管理
- 重复通知检测
- 未读通知统计

## 使用方法

### 1. 初始化数据
```bash
python manage.py init_social_subscriptions
```

### 2. 运行爬虫任务
```bash
# 单次运行
python manage.py run_social_crawler

# 持续运行（每5分钟检查一次）
python manage.py run_social_crawler --continuous --interval 300
```

### 3. 访问功能页面
访问 `/tools/web-crawler/` 页面使用社交媒体订阅功能。

## 前端界面

### 主要组件
1. **添加订阅表单** - 选择平台、输入用户ID、设置订阅类型和频率
2. **订阅列表** - 显示所有订阅，支持暂停/删除操作
3. **通知中心** - 显示所有通知，支持过滤和标记已读
4. **统计面板** - 显示订阅和通知统计信息

### 交互功能
- 实时数据加载
- 异步API调用
- 通知toast提示
- 响应式设计

## 配置说明

### 平台配置
在 `SocialMediaPlatformConfig` 模型中配置各平台的API端点和密钥：

```python
- platform: 平台标识
- api_endpoint: API端点URL
- api_key: API密钥（可选）
- is_active: 是否启用
- rate_limit: 速率限制
```

### 检查频率
- 5分钟：高频检查，适合重要用户
- 15分钟：标准检查，平衡性能和实时性
- 30分钟：低频检查，减少服务器负载
- 1小时：最低频率，适合不活跃用户

## 扩展功能

### 1. 真实API集成
- 替换模拟数据为真实API调用
- 添加各平台的API认证
- 实现更精确的数据解析

### 2. 推送通知
- 邮件通知
- 短信通知
- 浏览器推送
- 移动端推送

### 3. 数据分析
- 用户活跃度分析
- 内容趋势分析
- 订阅效果统计

### 4. 智能推荐
- 基于用户兴趣推荐订阅
- 相似用户推荐
- 热门内容推荐

## 注意事项

1. **API限制** - 注意各平台的API调用频率限制
2. **数据隐私** - 遵守各平台的数据使用政策
3. **错误处理** - 完善的错误处理和重试机制
4. **性能优化** - 合理设置检查频率，避免过度请求
5. **数据备份** - 定期备份订阅和通知数据

## 开发计划

- [x] 基础订阅功能
- [x] 通知系统
- [x] 爬虫服务
- [x] 前端界面
- [ ] 真实API集成
- [ ] 推送通知
- [ ] 数据分析
- [ ] 移动端适配 