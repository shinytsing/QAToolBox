# 食物评分API修复总结

## 🐛 问题描述

用户反馈食物随机器的评分功能失败，curl请求显示：
```bash
curl 'http://127.0.0.1:8000/tools/api/food-randomizer/rate/' \
  -H 'Content-Type: application/json' \
  --data-raw '{"session_id":35,"rating":4,"feedback":"1"}'
```

## 🔍 问题分析

### 根本原因
前端和后端API之间的参数不匹配：

1. **前端发送**: `session_id`
2. **后端期望**: `history_id`

### 代码问题
在 `apps/tools/views.py` 的 `rate_food_api` 函数中：
```python
# 修复前 - 错误的参数名
history_id = data.get('history_id')
history = FoodHistory.objects.get(
    id=history_id,  # 使用history_id查找
    user=request.user
)
```

## 🔧 解决方案

### 修复方法
修改评分API，使其接受 `session_id` 参数并通过 `session_id` 查找对应的历史记录：

```python
# 修复后 - 正确的参数名
session_id = data.get('session_id')
history = FoodHistory.objects.get(
    session_id=session_id,  # 使用session_id查找
    user=request.user
)
```

### 修改的文件
- `apps/tools/views.py` - 修改 `rate_food_api` 函数

### 具体修改
```python
@csrf_exempt
@require_http_methods(["POST"])
@login_required
def rate_food_api(request):
    """评价食物API"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')  # 修改：使用session_id
        rating = data.get('rating')
        feedback = data.get('feedback', '')
        was_cooked = data.get('was_cooked', False)
        
        # 通过session_id查找对应的历史记录
        history = FoodHistory.objects.get(
            session_id=session_id,  # 修改：使用session_id查找
            user=request.user
        )
        
        # ... 其余代码保持不变
```

## ✅ 验证结果

### 测试命令
```bash
curl 'http://127.0.0.1:8000/tools/api/food-randomizer/rate/' \
  -H 'Content-Type: application/json' \
  --data-raw '{"session_id":35,"rating":4,"feedback":"1"}'
```

### 测试结果
```json
{"success": true, "message": "评价已保存"}
```

### 数据库验证
```python
# 验证评分是否保存成功
history = FoodHistory.objects.filter(session_id=35).first()
print(f'历史记录: {history}')  # shinytsing - 沙拉 - 2025-08-07 23:43
print(f'评分: {history.rating}')  # 4
print(f'反馈: {history.feedback}')  # 1
```

## 🎯 修复效果

### 修复前
- ❌ 评分提交失败
- ❌ 参数不匹配错误
- ❌ 用户体验差

### 修复后
- ✅ 评分提交成功
- ✅ 参数匹配正确
- ✅ 数据正确保存到数据库
- ✅ 用户体验良好

## 📋 技术细节

### 数据流程
1. 用户进行食物随机选择 → 创建 `FoodRandomizationSession`
2. 选择完成后 → 创建 `FoodHistory` 记录（关联到session）
3. 用户评分 → 通过 `session_id` 查找对应的 `FoodHistory`
4. 保存评分 → 更新 `FoodHistory` 和 `FoodItem` 的受欢迎度

### 关键关系
- `FoodRandomizationSession` (会话) ←→ `FoodHistory` (历史记录)
- 一个会话对应一个历史记录
- 通过 `session_id` 可以找到对应的历史记录

## 🚀 后续建议

1. **统一参数命名**: 确保前后端API参数命名一致
2. **API文档**: 为所有API编写清晰的文档
3. **错误处理**: 增强错误处理和用户提示
4. **测试覆盖**: 添加API测试用例

---

**修复完成时间**: 2025年8月8日  
**修复状态**: ✅ 已完成并验证通过  
**影响范围**: 食物随机器评分功能  
**用户体验**: 显著提升
