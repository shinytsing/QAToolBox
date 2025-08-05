# QAToolBox 数据库设计文档

## 项目概述
QAToolBox 是一个多功能工具集合平台，包含生活模式、极客模式、狂暴模式和Emo模式四大主题模块。

## 数据库架构

### 1. 用户系统 (apps.users)

#### 核心用户模型
- **User** (Django内置) - 基础用户信息
- **UserRole** - 用户角色管理 (普通用户/管理员)
- **UserStatus** - 用户状态管理 (正常/暂停/封禁/删除)
- **UserMembership** - 会员系统 (免费/基础/高级/VIP)
- **Profile** - 用户资料扩展 (头像、手机号、个人简介)

#### 用户行为追踪
- **UserActionLog** - 管理员操作日志
- **UserActivityLog** - 用户活动日志
- **UserSessionStats** - 用户会话统计
- **APIUsageStats** - API使用统计

#### 用户偏好设置
- **UserTheme** - 用户主题设置 (生活/极客/狂暴/Emo模式)

### 2. 工具系统 (apps.tools)

#### 工具使用记录
- **ToolUsageLog** - 工具使用日志
  - 支持的工具类型：测试用例生成器、代码质量检查、性能模拟器、小红书生成器
  - 记录输入输出、预览图片、原始响应

#### 社交媒体监控
- **SocialMediaSubscription** - 社交媒体订阅
  - 支持平台：小红书、抖音、网易云音乐、微博、B站、知乎
  - 订阅类型：新动态、新关注、资料变化
- **SocialMediaNotification** - 社交媒体通知
- **SocialMediaPlatformConfig** - 平台配置管理

#### 生活管理功能
- **LifeDiaryEntry** - 生活日记
  - 心情记录：开心、平静、兴奋、难过、生气、一般
  - 支持标签和心情备注
- **LifeGoal** - 生活目标
  - 目标类别：健康、事业、学习、人际关系、财务、兴趣爱好、其他
  - 状态：进行中、已完成、暂停、已取消
- **LifeGoalProgress** - 目标进度记录
- **LifeStatistics** - 生活统计数据

### 3. 内容系统 (apps.content)

#### 内容管理
- **Article** - 文章管理
- **Comment** - 评论系统

#### 用户反馈
- **Suggestion** - 用户建议
  - 建议类型：功能建议、界面改进、Bug报告、其他
  - 状态：待处理、审核中、已实现、已拒绝
  - 支持图片和视频附件
- **Feedback** - 用户反馈
  - 反馈类型：Bug报告、功能建议、界面改进、其他
  - 状态：待处理、处理中、已解决、已关闭

#### 系统管理
- **Announcement** - 公告管理
  - 优先级：普通、重要、紧急
  - 状态：草稿、已发布、已归档
  - 支持弹窗显示和时间控制
- **AILink** - AI友情链接
  - 分类：视觉、音乐、编程、图片、其他
  - 支持图标和排序

## 数据库关系图

```
User (Django内置)
├── UserRole (1:1)
├── UserStatus (1:1)
├── UserMembership (1:1)
├── Profile (1:1)
├── UserTheme (1:1)
├── UserActionLog (1:N)
├── UserActivityLog (1:N)
├── UserSessionStats (1:N)
├── APIUsageStats (1:N)
├── ToolUsageLog (1:N)
├── SocialMediaSubscription (1:N)
├── LifeDiaryEntry (1:N)
├── LifeGoal (1:N)
├── LifeStatistics (1:N)
├── Article (1:N)
├── Comment (1:N)
├── Suggestion (1:N)
├── Feedback (1:N)
└── Announcement (1:N)

SocialMediaSubscription (1:N)
└── SocialMediaNotification

LifeGoal (1:N)
└── LifeGoalProgress

Article (1:N)
└── Comment
```

## 数据库配置

### 开发环境
- 数据库：SQLite3
- 位置：db.sqlite3
- 字符集：UTF-8

### 生产环境建议
- 数据库：PostgreSQL/MySQL
- 字符集：UTF-8
- 时区：Asia/Shanghai

## 索引优化

### 用户系统索引
- UserActivityLog: (user, created_at)
- UserSessionStats: (user, session_start)
- APIUsageStats: (user, created_at)

### 工具系统索引
- ToolUsageLog: (user, tool_type, created_at)
- SocialMediaSubscription: (user, platform, target_user_id)
- LifeDiaryEntry: (user, date)
- LifeGoal: (user, status, priority)

### 内容系统索引
- Suggestion: (status, created_at)
- Feedback: (status, created_at)
- Announcement: (status, priority, start_time)

## 数据迁移策略

### 初始迁移
1. 创建所有模型的基础表结构
2. 设置默认数据（管理员用户、基础配置）
3. 创建必要的索引

### 版本升级
1. 增量迁移文件
2. 数据备份策略
3. 回滚机制

## 性能优化建议

### 查询优化
- 使用select_related()和prefetch_related()减少查询
- 合理使用数据库索引
- 分页查询大数据集

### 缓存策略
- 用户会话缓存
- 静态内容缓存
- API响应缓存

### 监控指标
- 数据库连接数
- 查询响应时间
- 慢查询日志
- 存储空间使用

## 安全考虑

### 数据保护
- 敏感信息加密存储
- 用户密码哈希处理
- API密钥安全存储

### 访问控制
- 基于角色的权限控制
- API访问频率限制
- 用户操作日志记录

### 数据备份
- 定期自动备份
- 增量备份策略
- 备份数据加密

## 扩展性设计

### 水平扩展
- 读写分离
- 分库分表策略
- 缓存层设计

### 功能扩展
- 插件化架构
- 微服务拆分
- API版本管理 