# 聊天室回收机制使用指南

## 🎯 功能概述

已成功实现聊天室回收机制，用户断开连接10分钟后，聊天室自动消失。同时提供了活跃聊天室查看功能。

## ✨ 主要功能

### 1. 🔄 自动聊天室清理
- **清理时间**: 用户断开连接10分钟后自动清理
- **清理条件**: 聊天室中所有用户都离线超过10分钟
- **保护机制**: 新创建的聊天室（5分钟内）不会被清理
- **执行频率**: 每5分钟检查一次

### 2. 📊 活跃聊天室查看
- **页面路径**: `/tools/chat/active_rooms/`
- **功能特性**:
  - 显示用户参与的活跃聊天室
  - 实时显示在线用户数量
  - 显示心动链接请求状态
  - 支持手动刷新
  - 自动每30秒刷新一次

### 3. 🛠️ 管理命令
- **命令**: `python manage.py cleanup_chat_rooms`
- **参数**:
  - `--dry-run`: 仅显示将要清理的聊天室，不实际执行
  - `--force`: 强制执行清理，忽略时间限制
  - `--minutes`: 设置清理时间（默认10分钟）

## 🚀 使用方法

### 1. 启动自动清理服务

#### 方法一：使用定时任务脚本
```bash
# 启动聊天室清理定时任务
python start_chat_cleanup.py
```

#### 方法二：手动执行清理
```bash
# 查看将要清理的聊天室（不实际执行）
python manage.py cleanup_chat_rooms --dry-run

# 执行清理
python manage.py cleanup_chat_rooms

# 强制执行清理
python manage.py cleanup_chat_rooms --force

# 设置5分钟清理时间
python manage.py cleanup_chat_rooms --minutes 5
```

### 2. 查看活跃聊天室

#### 访问页面
1. 登录系统
2. 访问: `http://localhost:8000/tools/chat/active_rooms/`
3. 查看您的活跃聊天室和在线用户

#### API接口
```bash
# 获取活跃聊天室信息
curl -X GET http://localhost:8000/tools/api/chat/active_rooms/ \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -H "Content-Type: application/json"
```

## 🔧 技术实现

### 1. 后端架构

#### 管理命令
- **文件**: `apps/tools/management/commands/cleanup_chat_rooms.py`
- **功能**: 清理不活跃的聊天室和用户状态

#### WebSocket消费者增强
- **文件**: `apps/tools/consumers.py`
- **新增方法**: `record_disconnect_time()`
- **功能**: 记录用户断开连接时间

#### API接口
- **文件**: `apps/tools/views.py`
- **新增API**: `get_active_chat_rooms_api()`
- **功能**: 获取用户活跃聊天室信息

### 2. 前端实现

#### 活跃聊天室页面
- **文件**: `templates/tools/active_chat_rooms.html`
- **功能**: 显示活跃聊天室和用户状态
- **特性**: 响应式设计，实时更新

### 3. 数据库模型

#### 聊天室状态跟踪
```python
class ChatRoom(models.Model):
    status = models.CharField(max_length=20, choices=[
        ('waiting', '等待匹配'),
        ('active', '活跃'),
        ('ended', '已结束'),
    ])
    ended_at = models.DateTimeField(null=True, blank=True)
```

#### 用户在线状态
```python
class UserOnlineStatus(models.Model):
    status = models.CharField(max_length=20, choices=[
        ('online', '在线'),
        ('busy', '忙碌'),
        ('away', '离开'),
        ('offline', '离线'),
    ])
    last_seen = models.DateTimeField(auto_now=True)
    is_online = models.BooleanField(default=False)
```

## 📋 清理逻辑

### 1. 清理条件
- 聊天室状态为 `active`
- 聊天室创建时间超过5分钟
- 聊天室中所有用户都离线超过指定时间（默认10分钟）

### 2. 清理操作
- 将聊天室状态更新为 `ended`
- 记录结束时间 `ended_at`
- 更新相关心动链接请求状态为 `expired`
- 更新用户在线状态为 `offline`

### 3. 保护机制
- 新创建的聊天室（5分钟内）不会被清理
- 只有所有用户都离线才会清理
- 支持强制清理模式

## 🔍 监控和日志

### 1. 日志文件
- **文件**: `chat_cleanup.log`
- **内容**: 清理任务执行记录和错误信息

### 2. 统计信息
清理完成后会显示：
- 本次清理的聊天室数量
- 当前活跃聊天室数量
- 已结束聊天室数量
- 等待匹配的聊天室数量

## 🎯 使用场景

### 1. 开发环境
```bash
# 启动清理服务
python start_chat_cleanup.py

# 在另一个终端启动Django服务器
python manage.py runserver
```

### 2. 生产环境
```bash
# 使用cron定时任务
# 编辑crontab
crontab -e

# 添加定时任务（每5分钟执行一次）
*/5 * * * * cd /path/to/QAToolBox && python manage.py cleanup_chat_rooms
```

### 3. 测试清理功能
```bash
# 查看当前聊天室状态
python manage.py cleanup_chat_rooms --dry-run

# 测试清理（设置较短时间）
python manage.py cleanup_chat_rooms --minutes 1
```

## 🚨 注意事项

1. **数据安全**: 清理操作会永久删除聊天室，请谨慎使用
2. **性能考虑**: 大量聊天室时建议调整清理频率
3. **日志监控**: 定期检查日志文件，确保清理任务正常运行
4. **备份建议**: 重要聊天室数据建议定期备份

## 🔄 故障排除

### 1. 清理任务不执行
- 检查Django环境是否正确设置
- 确认数据库连接正常
- 查看日志文件中的错误信息

### 2. 聊天室未按预期清理
- 检查用户在线状态是否正确更新
- 确认清理时间设置是否合理
- 使用 `--dry-run` 参数检查清理条件

### 3. API接口错误
- 确认用户已登录
- 检查CSRF令牌是否正确
- 查看Django错误日志

## 📈 性能优化建议

1. **数据库索引**: 为 `last_seen` 和 `status` 字段添加索引
2. **批量操作**: 大量清理时使用批量更新
3. **缓存机制**: 考虑使用Redis缓存用户在线状态
4. **异步处理**: 使用Celery处理清理任务

---

**总结**: 聊天室回收机制已完全实现，支持自动清理和手动管理，确保系统资源得到有效利用。
