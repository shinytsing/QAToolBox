# QAToolBox API 端点文档

## 🔗 基础URL
```
开发环境: http://localhost:8000/api/v1/
生产环境: https://shenyiqing.xin/api/v1/
```

## 🔐 认证方式

### JWT Token 认证
```bash
# 请求头
Authorization: Bearer <your_access_token>
```

### 获取Token
```bash
# 登录获取Token
POST /api/v1/auth/login/
{
    "username": "your_username",
    "password": "your_password"
}

# 响应
{
    "success": true,
    "data": {
        "user": {...},
        "tokens": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
}
```

## 📱 认证模块 (`/api/v1/auth/`)

### 用户注册
```bash
POST /api/v1/auth/register/
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### 用户登录
```bash
POST /api/v1/auth/login/
{
    "username": "username",
    "password": "password"
}
```

### 用户登出
```bash
POST /api/v1/auth/logout/
Authorization: Bearer <token>
```

### 刷新Token
```bash
POST /api/v1/auth/refresh/
{
    "refresh_token": "your_refresh_token"
}
```

### 获取用户资料
```bash
GET /api/v1/auth/profile/
Authorization: Bearer <token>
```

### 更新用户资料
```bash
PUT /api/v1/auth/profile/
Authorization: Bearer <token>
{
    "first_name": "New Name",
    "bio": "Updated bio"
}
```

### 修改密码
```bash
POST /api/v1/auth/change-password/
Authorization: Bearer <token>
{
    "old_password": "old_password",
    "new_password": "new_password",
    "new_password_confirm": "new_password"
}
```

### 忘记密码
```bash
POST /api/v1/auth/forgot-password/
{
    "email": "user@example.com"
}
```

### 重置密码
```bash
POST /api/v1/auth/reset-password/
{
    "token": "reset_token",
    "new_password": "new_password",
    "new_password_confirm": "new_password"
}
```

## 🏋️ 健身模块 (`/api/v1/fitness/`)

### 训练计划管理

#### 获取训练计划列表
```bash
GET /api/v1/fitness/workouts/
Authorization: Bearer <token>

# 查询参数
?workout_type=strength&start_date=2024-01-01&end_date=2024-01-31
```

#### 创建训练计划
```bash
POST /api/v1/fitness/workouts/
Authorization: Bearer <token>
{
    "workout_name": "胸肌训练",
    "workout_type": "strength",
    "start_time": "2024-01-01T10:00:00Z",
    "end_time": "2024-01-01T11:00:00Z",
    "notes": "训练笔记"
}
```

#### 获取训练计划详情
```bash
GET /api/v1/fitness/workouts/{id}/
Authorization: Bearer <token>
```

#### 更新训练计划
```bash
PUT /api/v1/fitness/workouts/{id}/
Authorization: Bearer <token>
{
    "workout_name": "更新的训练名称",
    "notes": "更新的笔记"
}
```

#### 删除训练计划
```bash
DELETE /api/v1/fitness/workouts/{id}/
Authorization: Bearer <token>
```

#### 添加重量记录
```bash
POST /api/v1/fitness/workouts/{id}/add_weight_record/
Authorization: Bearer <token>
{
    "exercise_name": "卧推",
    "weight": 80,
    "reps": 10,
    "sets": 3,
    "notes": "感觉不错"
}
```

### 健身资料管理

#### 获取健身资料
```bash
GET /api/v1/fitness/profile/
Authorization: Bearer <token>
```

#### 更新健身资料
```bash
PUT /api/v1/fitness/profile/
Authorization: Bearer <token>
{
    "height": 175,
    "weight": 70,
    "fitness_goal": "增肌",
    "experience_level": "intermediate",
    "preferred_workout_types": ["strength", "cardio"],
    "available_days": ["monday", "wednesday", "friday"],
    "workout_duration": 60
}
```

### 健身社区

#### 获取社区动态列表
```bash
GET /api/v1/fitness/posts/
Authorization: Bearer <token>

# 查询参数
?search=关键词&post_type=workout&page=1&page_size=20
```

#### 发布社区动态
```bash
POST /api/v1/fitness/posts/
Authorization: Bearer <token>
{
    "title": "今日训练分享",
    "content": "完成了胸肌训练，感觉很好！",
    "post_type": "workout",
    "images": ["image1.jpg", "image2.jpg"]
}
```

#### 点赞动态
```bash
POST /api/v1/fitness/posts/{id}/like/
Authorization: Bearer <token>
```

#### 评论动态
```bash
POST /api/v1/fitness/posts/{id}/comment/
Authorization: Bearer <token>
{
    "content": "很棒的训练！"
}
```

#### 获取动态评论
```bash
GET /api/v1/fitness/posts/{id}/comments/
Authorization: Bearer <token>
```

## 📱 生活工具模块 (`/api/v1/life/`)

*待实现*

## 🛠️ 极客工具模块 (`/api/v1/tools/`)

*待实现*

## 🎭 社交娱乐模块 (`/api/v1/social/`)

*待实现*

## 📤 分享模块 (`/api/v1/share/`)

*待实现*

## 👨‍💼 管理模块 (`/api/v1/admin/`)

*待实现*

## 📊 响应格式

### 成功响应
```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {...},
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

### 分页响应
```json
{
    "success": true,
    "code": 200,
    "message": "获取成功",
    "data": [...],
    "pagination": {
        "count": 100,
        "total_pages": 5,
        "current_page": 1,
        "page_size": 20,
        "has_next": true,
        "has_previous": false
    },
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123456789"
}
```

## 🔒 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 1001 | 用户名或密码错误 |
| 1002 | Token已过期 |
| 1003 | Token无效 |
| 2001 | 权限不足 |
| 2002 | 功能未启用 |
| 3001 | 数据验证错误 |

## 🚀 使用示例

### Python 示例
```python
import requests

# 登录获取Token
response = requests.post('http://localhost:8000/api/v1/auth/login/', {
    'username': 'your_username',
    'password': 'your_password'
})
tokens = response.json()['data']['tokens']

# 使用Token访问API
headers = {
    'Authorization': f"Bearer {tokens['access_token']}"
}

# 获取训练计划
response = requests.get(
    'http://localhost:8000/api/v1/fitness/workouts/',
    headers=headers
)
workouts = response.json()['data']
```

### JavaScript 示例
```javascript
// 登录获取Token
const loginResponse = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});
const { data } = await loginResponse.json();
const token = data.tokens.access_token;

// 使用Token访问API
const workoutsResponse = await fetch('/api/v1/fitness/workouts/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const workouts = await workoutsResponse.json();
```
