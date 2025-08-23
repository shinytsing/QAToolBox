# 社交媒体订阅通知API修复总结

## 问题描述
用户报告了以下错误：
```
web_crawler/:3710  GET http://localhost:8000/tools/api/social_subscription/notifications/ 500 (Internal Server Error)
```

## 根本原因分析
经过调查发现，500错误主要由以下几个问题导致：

### 1. 模型字段不匹配
- 数据库迁移 `0014_socialmedianotification_external_url_and_more.py` 添加了多个新字段
- 但 `SocialMediaNotification` 模型定义中缺少这些字段
- 导致视图访问不存在的字段时出错

### 2. 服务层字段引用错误
- `notification_service.py` 中引用了不存在的字段：
  - `user` 字段（应该通过 `subscription__user` 访问）
  - `metadata` 字段（应该使用 `data` 字段）
  - `read_at` 字段（模型中不存在）

### 3. 视图层方法缺失
- `SocialMediaSubscription` 模型缺少 `get_user_subscription_stats` 方法
- `SocialMediaNotification` 模型缺少 `get_user_notification_stats` 方法

### 4. 视图字段引用错误
- `add_social_subscription_api` 中引用了不存在的字段
- `update_subscription_api` 中引用了不存在的字段

## 修复内容

### 1. 更新 SocialMediaNotification 模型
```python
# 添加了迁移0014中定义的所有字段
external_url = models.URLField(blank=True, null=True, verbose_name='外部链接')
follower_avatar = models.URLField(blank=True, null=True, verbose_name='粉丝头像')
follower_count = models.IntegerField(blank=True, default=0, null=True, verbose_name='当前粉丝总数')
# ... 其他字段
```

### 2. 修复 notification_service.py
```python
# 修复字段引用
# 之前: user=subscription.user
# 修复后: 移除user字段引用

# 之前: metadata=update
# 修复后: data=update

# 之前: notification.read_at = timezone.now()
# 修复后: 移除read_at字段引用
```

### 3. 添加缺失的模型方法
```python
# SocialMediaSubscription 模型
@classmethod
def get_user_subscription_stats(cls, user):
    """获取用户订阅统计信息"""
    # 实现统计逻辑

# SocialMediaNotification 模型  
@classmethod
def get_user_notification_stats(cls, user):
    """获取用户通知统计信息"""
    # 实现统计逻辑
```

### 4. 修复视图字段引用
```python
# add_social_subscription_api
# 移除了不存在的字段引用，只保留模型中存在的字段

# update_subscription_api
# 更新字段列表，只包含模型中存在的字段
```

## 修复后的状态
- ✅ 模型字段完整，与数据库迁移一致
- ✅ 服务层字段引用正确
- ✅ 视图层方法完整
- ✅ 字段引用正确

## 测试建议
1. 确保用户已登录（API需要 `@login_required` 装饰器）
2. 测试通知列表API：`GET /tools/api/social_subscription/notifications/`
3. 测试订阅统计API：`GET /tools/api/social_subscription/stats/`
4. 检查返回的JSON格式是否正确

## 注意事项
- 所有社交媒体订阅相关的API都需要用户登录
- 如果仍然遇到问题，请检查Django日志获取详细错误信息
- 确保数据库迁移已正确应用
