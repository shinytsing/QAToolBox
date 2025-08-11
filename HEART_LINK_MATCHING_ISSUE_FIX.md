# Heart Link 匹配问题修复

## 问题描述

用户 A 发送 Heart Link 请求后，当用户 B 发起请求时，A 的请求会失败（状态变为 expired）。

## 问题原因分析

### 1. 清理逻辑过于频繁

在 `create_heart_link_request_api` 函数中，每次有新用户创建请求时都会执行清理：

```python
# 清理过期的请求
cleanup_expired_heart_link_requests()
```

### 2. 时间线分析

1. **A 发送请求** → 创建 `pending` 状态的 HeartLinkRequest
2. **等待时间** → A 的请求在等待匹配（可能等待超过 10 分钟）
3. **B 发起请求** → 触发 `cleanup_expired_heart_link_requests()` 函数
4. **A 的请求被清理** → 如果 A 的请求已经超过 10 分钟，会被标记为 `expired`
5. **A 检查状态** → 发现自己的请求已经过期

### 3. 根本原因

- 清理函数在每次创建新请求时都会执行
- 清理函数会将所有超过 10 分钟的 pending 请求标记为 expired
- 这导致正在等待匹配的用户请求被意外清理

## 解决方案

### 1. 减少清理频率

修改 `create_heart_link_request_api` 函数，使用概率控制清理频率：

```python
# 减少清理频率，只在必要时清理（10%的概率）
import random
if random.random() < 0.1:
    cleanup_expired_heart_link_requests()
```

### 2. 优化状态检查

修改 `check_heart_link_status_api` 函数，进一步减少清理频率：

```python
# 只有5%的概率执行清理，进一步减少数据库压力和避免影响等待用户
if random.random() < 0.05:
    # 清理逻辑
```

### 3. 创建独立的清理任务

创建 `cleanup_heart_links` 管理命令，用于定期清理：

```bash
# 定期执行清理
python manage.py cleanup_heart_links

# 强制执行清理
python manage.py cleanup_heart_links --force
```

### 4. 改进匹配逻辑

在匹配服务中也减少清理频率：

```python
# 清理过期请求（减少频率）
if random.random() < 0.1:
    matcher.cleanup_expired_requests()
```

## 修改的文件

1. **apps/tools/views.py**
   - `create_heart_link_request_api` - 减少清理频率
   - `check_heart_link_status_api` - 进一步减少清理频率

2. **apps/tools/management/commands/cleanup_heart_links.py**
   - 创建独立的清理命令
   - 支持概率控制和强制执行

## 预期效果

### 1. 减少误清理
- 清理频率从 100% 降低到 5-10%
- 大大减少正在等待匹配的用户请求被意外清理

### 2. 提高匹配成功率
- 用户请求有更多时间等待匹配
- 减少因清理导致的匹配失败

### 3. 更好的用户体验
- 用户不会因为其他用户的操作而失去匹配机会
- 系统更加稳定和可预测

## 监控建议

### 1. 定期检查清理效果
```bash
# 查看当前状态
python manage.py cleanup_heart_links --force
```

### 2. 监控匹配成功率
- 跟踪 pending → matched 的转换率
- 监控因过期导致的失败率

### 3. 调整清理参数
- 根据实际使用情况调整清理概率
- 考虑延长过期时间（从 10 分钟改为 15-20 分钟）

## 已实现的优化

### 1. 智能清理机制
- 根据系统负载动态调整清理频率
- 请求较多时（>50）清理概率 50%
- 请求中等时（>20）清理概率 30%
- 请求较少时（≤20）清理概率 10%

### 2. 用户通知机制
- 创建了 `HeartLinkNotificationService` 通知服务
- 在请求即将过期时（8-10分钟）显示警告
- 提供剩余时间提示

### 3. 自动续期机制
- 为活跃用户（5分钟内在线）自动延长请求有效期
- 将过期时间从 10 分钟延长到 15 分钟
- 自动更新请求的创建时间

### 4. 匹配优先级机制
- 优先匹配等待时间最长的用户
- 按 `created_at` 排序，确保公平性
- 使用乐观锁避免竞态条件

## 修改的文件

1. **apps/tools/views.py**
   - `create_heart_link_request_api` - 减少清理频率
   - `check_heart_link_status_api` - 添加自动续期和通知

2. **apps/tools/services/heart_link_matcher.py**
   - `find_best_match` - 实现匹配优先级

3. **apps/tools/services/heart_link_notification.py**
   - 新增通知服务

4. **apps/tools/management/commands/cleanup_heart_links.py**
   - 实现智能清理机制

## 预期效果

### 1. 大幅提高匹配成功率
- 减少误清理导致的匹配失败
- 自动续期延长等待时间
- 优先级匹配提高公平性

### 2. 更好的用户体验
- 实时警告避免意外过期
- 活跃用户自动续期
- 更稳定的匹配系统

### 3. 系统性能优化
- 智能清理减少数据库压力
- 概率控制避免频繁操作
- 动态调整适应负载变化

## 监控指标

### 1. 匹配成功率
```bash
python manage.py cleanup_heart_links --force
```

### 2. 关键指标
- 总请求数
- 等待中请求数
- 已过期请求数
- 已匹配请求数
- 匹配成功率

## 后续优化建议

1. **实时通知**：集成 WebSocket 实现实时通知
2. **用户偏好**：根据用户历史匹配偏好优化算法
3. **负载均衡**：在多个服务器间分配匹配负载
4. **数据分析**：收集匹配数据用于算法优化
