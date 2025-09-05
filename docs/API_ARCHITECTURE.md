# QAToolBox API 架构设计

## 🎯 设计目标

将现有Django项目重构为统一的RESTful API服务，支持多端开发（Web、小程序、移动App）。

## 📋 API 版本策略

- **v1**: 现有功能API化（向后兼容）
- **v2**: 优化后的API设计（未来版本）

## 🏗️ 整体架构

```
QAToolBox API Server
├── 认证授权层 (JWT + OAuth2)
├── 权限控制层 (RBAC)
├── API路由层 (DRF)
├── 业务逻辑层 (Services)
├── 数据访问层 (Models)
└── 数据存储层 (PostgreSQL + Redis)
```

## 🔐 认证授权

### JWT Token 认证
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 权限级别
- `public`: 公开访问
- `authenticated`: 需要登录
- `vip`: VIP用户
- `admin`: 管理员

## 📡 API 响应格式

### 统一响应结构
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456789"
}
```

### 错误响应
```json
{
  "success": false,
  "code": 400,
  "message": "参数错误",
  "errors": {
    "field_name": ["错误详情"]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "req_123456789"
}
```

## 🗂️ API 模块划分

### 1. 用户认证模块 (`/api/v1/auth/`)
```
POST   /api/v1/auth/login/          # 用户登录
POST   /api/v1/auth/register/       # 用户注册
POST   /api/v1/auth/logout/         # 用户登出
POST   /api/v1/auth/refresh/        # 刷新Token
POST   /api/v1/auth/forgot-password/ # 忘记密码
POST   /api/v1/auth/reset-password/  # 重置密码
GET    /api/v1/auth/profile/        # 获取用户信息
PUT    /api/v1/auth/profile/        # 更新用户信息
```

### 2. 健身模块 (`/api/v1/fitness/`)
```
# 训练计划
GET    /api/v1/fitness/workouts/           # 获取训练计划列表
POST   /api/v1/fitness/workouts/           # 创建训练计划
GET    /api/v1/fitness/workouts/{id}/      # 获取训练计划详情
PUT    /api/v1/fitness/workouts/{id}/      # 更新训练计划
DELETE /api/v1/fitness/workouts/{id}/      # 删除训练计划

# 健身记录
GET    /api/v1/fitness/records/            # 获取健身记录
POST   /api/v1/fitness/records/            # 添加健身记录
PUT    /api/v1/fitness/records/{id}/       # 更新健身记录
DELETE /api/v1/fitness/records/{id}/       # 删除健身记录

# 健身社区
GET    /api/v1/fitness/posts/              # 获取社区动态
POST   /api/v1/fitness/posts/              # 发布动态
GET    /api/v1/fitness/posts/{id}/         # 获取动态详情
POST   /api/v1/fitness/posts/{id}/like/    # 点赞
POST   /api/v1/fitness/posts/{id}/comment/ # 评论
```

### 3. 生活工具模块 (`/api/v1/life/`)
```
# 生活日记
GET    /api/v1/life/diary/                 # 获取日记列表
POST   /api/v1/life/diary/                 # 创建日记
GET    /api/v1/life/diary/{id}/            # 获取日记详情
PUT    /api/v1/life/diary/{id}/            # 更新日记
DELETE /api/v1/life/diary/{id}/            # 删除日记

# 冥想指导
GET    /api/v1/life/meditation/            # 获取冥想列表
POST   /api/v1/life/meditation/session/    # 开始冥想
GET    /api/v1/life/meditation/session/{id}/ # 获取冥想会话

# 食物随机
GET    /api/v1/life/food/random/           # 随机食物推荐
POST   /api/v1/life/food/rate/             # 评价食物
GET    /api/v1/life/food/history/          # 食物历史记录
```

### 4. 极客工具模块 (`/api/v1/tools/`)
```
# PDF转换
POST   /api/v1/tools/pdf/convert/          # PDF转换
GET    /api/v1/tools/pdf/status/{id}/      # 转换状态
GET    /api/v1/tools/pdf/download/{id}/    # 下载转换结果

# 数据爬虫
POST   /api/v1/tools/crawler/start/        # 开始爬虫任务
GET    /api/v1/tools/crawler/status/{id}/  # 爬虫状态
GET    /api/v1/tools/crawler/result/{id}/  # 爬虫结果

# 测试用例生成
POST   /api/v1/tools/testcase/generate/    # 生成测试用例
GET    /api/v1/tools/testcase/templates/   # 获取模板列表
```

### 5. 社交娱乐模块 (`/api/v1/social/`)
```
# 聊天室
GET    /api/v1/social/chat/rooms/          # 获取聊天室列表
POST   /api/v1/social/chat/rooms/          # 创建聊天室
GET    /api/v1/social/chat/rooms/{id}/     # 获取聊天室详情
POST   /api/v1/social/chat/rooms/{id}/join/ # 加入聊天室
POST   /api/v1/social/chat/rooms/{id}/leave/ # 离开聊天室

# 心链功能
GET    /api/v1/social/heart-link/          # 获取心链列表
POST   /api/v1/social/heart-link/          # 创建心链请求
PUT    /api/v1/social/heart-link/{id}/     # 更新心链状态

# 塔罗占卜
GET    /api/v1/social/tarot/cards/         # 获取塔罗牌
POST   /api/v1/social/tarot/reading/       # 塔罗占卜
GET    /api/v1/social/tarot/history/       # 占卜历史
```

### 6. 分享模块 (`/api/v1/share/`)
```
POST   /api/v1/share/create/               # 创建分享链接
GET    /api/v1/share/{short_code}/         # 获取分享内容
POST   /api/v1/share/record/               # 记录分享行为
GET    /api/v1/share/analytics/            # 分享数据统计
```

### 7. 管理模块 (`/api/v1/admin/`)
```
# 用户管理
GET    /api/v1/admin/users/                # 获取用户列表
PUT    /api/v1/admin/users/{id}/           # 更新用户信息
DELETE /api/v1/admin/users/{id}/           # 删除用户

# 功能管理
GET    /api/v1/admin/features/             # 获取功能列表
PUT    /api/v1/admin/features/{id}/        # 更新功能状态
GET    /api/v1/admin/analytics/            # 系统数据统计
```

## 🔄 实时通信

### WebSocket 连接
```
ws://api.qatoolbox.com/ws/
├── /ws/chat/{room_id}/     # 聊天室
├── /ws/notifications/      # 通知推送
└── /ws/heart-link/         # 心链实时状态
```

## 📊 数据模型设计

### 核心实体关系
```
User (用户)
├── Profile (用户资料)
├── UserRole (用户角色)
├── UserMembership (会员信息)
└── UserActivity (用户活动)

FitnessWorkout (训练计划)
├── Exercise (运动项目)
├── WorkoutRecord (训练记录)
└── FitnessPost (健身动态)

LifeDiary (生活日记)
├── DiaryEntry (日记条目)
├── MeditationSession (冥想会话)
└── FoodHistory (食物历史)

ToolUsage (工具使用)
├── PDFConversion (PDF转换)
├── CrawlerTask (爬虫任务)
└── TestCaseGeneration (测试用例生成)

SocialInteraction (社交互动)
├── ChatRoom (聊天室)
├── HeartLink (心链)
└── TarotReading (塔罗占卜)
```

## 🚀 性能优化

### 缓存策略
- **Redis缓存**: 用户会话、API响应、热点数据
- **数据库缓存**: 查询结果缓存
- **CDN缓存**: 静态资源、图片、文件

### 数据库优化
- **读写分离**: 主从数据库
- **分库分表**: 按功能模块分库
- **索引优化**: 关键字段索引

### API优化
- **分页**: 所有列表API支持分页
- **过滤**: 支持多条件过滤
- **排序**: 支持多字段排序
- **限流**: API访问频率限制

## 🔒 安全策略

### 认证安全
- JWT Token过期时间控制
- Refresh Token轮换机制
- 多设备登录管理

### 数据安全
- 敏感数据加密存储
- API请求签名验证
- SQL注入防护
- XSS攻击防护

### 访问控制
- IP白名单
- 用户权限验证
- API访问频率限制
- 异常访问监控

## 📱 多端适配

### 响应格式适配
- Web端: 完整数据 + 分页信息
- 小程序: 精简数据 + 必要字段
- 移动端: 优化数据 + 缓存策略

### 功能权限控制
- 根据客户端类型返回不同功能
- 小程序功能限制
- 移动端功能增强

## 🔧 开发规范

### API命名规范
- 使用RESTful风格
- 动词使用POST，名词使用GET
- 资源使用复数形式
- 版本号在URL中体现

### 错误处理
- 统一错误码定义
- 详细错误信息
- 错误日志记录
- 用户友好提示

### 文档规范
- Swagger/OpenAPI文档
- 接口使用示例
- 错误码说明
- 更新日志记录
