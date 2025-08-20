# 灵境塔罗功能使用指南

## 功能概述

灵境塔罗是一个完整的塔罗牌占卜系统，提供专业的塔罗牌解读服务。系统包含完整的78张塔罗牌数据、多种牌阵选择、AI智能解读、用户反馈系统等功能。

## 主要功能

### 1. 塔罗牌数据
- **大阿卡纳（22张）**：包含愚者、魔术师、女祭司等经典大阿卡纳牌
- **小阿卡纳（56张）**：权杖、圣杯、宝剑、钱币四个花色
- **完整牌义**：每张牌包含正位和逆位含义、关键词、详细描述

### 2. 牌阵系统
- **单张牌阵**：简单直接的问题解答
- **三张牌阵**：过去、现在、未来的时间线
- **凯尔特十字**：深度分析复杂情况
- **爱情十字**：专门用于爱情关系分析
- **事业阶梯**：分析事业发展路径
- **心灵花园**：探索内心世界和灵性成长

### 3. AI智能解读
- 基于DeepSeek AI的专业解读
- 结合牌阵位置和牌面含义
- 提供整体解读、各位置解读、建议指导
- 支持多种占卜类型（爱情、事业、健康等）

### 4. 用户功能
- 占卜历史记录
- 用户反馈系统
- 心情变化追踪
- 每日能量提示

## 安装和配置

### 1. 初始化数据
```bash
# 运行初始化命令
python manage.py init_tarot_data
```

### 2. 配置AI API（可选）
在 `settings.py` 中添加：
```python
DEEPSEEK_API_KEY = 'your_api_key_here'
```

### 3. 运行测试
```bash
# 测试塔罗牌功能
python test_tarot_functionality.py
```

## API接口

### 1. 初始化数据
```
POST /tools/api/tarot/initialize-data/
```

### 2. 获取牌阵
```
GET /tools/api/tarot/spreads/
```

### 3. 创建占卜
```
POST /tools/api/tarot/create-reading/
Content-Type: application/json

{
    "spread_id": 1,
    "reading_type": "love",
    "question": "我的感情发展如何？",
    "mood_before": "期待"
}
```

### 4. 获取占卜历史
```
GET /tools/api/tarot/readings/
```

### 5. 获取占卜详情
```
GET /tools/api/tarot/reading/{reading_id}/
```

### 6. 提交反馈
```
POST /tools/api/tarot/reading/{reading_id}/feedback/
Content-Type: application/json

{
    "feedback": "解读很准确",
    "rating": 5,
    "mood_after": "满意"
}
```

### 7. 获取每日能量
```
GET /tools/api/tarot/daily-energy/
```

## 使用流程

### 1. 选择牌阵
用户可以从多种牌阵中选择：
- **单张牌阵**：适合快速占卜
- **三张牌阵**：了解事情发展脉络
- **凯尔特十字**：深度分析复杂情况
- **专业牌阵**：针对特定问题（爱情、事业等）

### 2. 提出问题
- 选择占卜类型（爱情、事业、健康、灵性等）
- 详细描述问题
- 选择当前心情

### 3. 获得解读
- 系统随机抽取塔罗牌
- AI生成专业解读
- 显示各位置含义
- 提供建议指导

### 4. 反馈评价
- 对解读准确性评分
- 记录占卜后心情
- 分享感受和建议

## 技术架构

### 1. 数据模型
- `TarotCard`：塔罗牌数据
- `TarotSpread`：牌阵定义
- `TarotReading`：占卜记录
- `TarotEnergyCalendar`：每日能量

### 2. 服务层
- `TarotService`：核心业务逻辑
- AI解读生成
- 数据缓存管理
- 统计分析

### 3. 视图层
- RESTful API接口
- 用户认证和权限
- 错误处理和日志

### 4. 前端界面
- 响应式设计
- 动画效果
- 用户交互优化

## 自定义配置

### 1. 添加新牌阵
在 `TarotSpread` 模型中添加新的牌阵数据：
```python
{
    'name': '新牌阵名称',
    'spread_type': 'custom',
    'description': '牌阵描述',
    'card_count': 5,
    'positions': ['位置1', '位置2', '位置3', '位置4', '位置5']
}
```

### 2. 自定义AI解读
修改 `TarotService.generate_ai_interpretation()` 方法：
- 调整提示词模板
- 更换AI服务提供商
- 自定义解读风格

### 3. 扩展功能
- 添加更多牌阵类型
- 实现用户收藏功能
- 增加社交分享功能
- 添加占卜统计图表

## 注意事项

### 1. 数据安全
- 用户占卜记录隐私保护
- API访问权限控制
- 敏感信息加密存储

### 2. 性能优化
- 数据库查询优化
- 缓存策略实施
- 异步任务处理

### 3. 用户体验
- 响应时间优化
- 错误提示友好
- 界面交互流畅

## 故障排除

### 1. 数据初始化失败
```bash
# 检查数据库连接
python manage.py check

# 重新运行迁移
python manage.py migrate

# 重新初始化数据
python manage.py init_tarot_data
```

### 2. AI解读失败
- 检查API密钥配置
- 验证网络连接
- 查看错误日志

### 3. 前端显示问题
- 检查静态文件收集
- 验证CSS/JS加载
- 清除浏览器缓存

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 完整的塔罗牌数据
- 基础牌阵系统
- AI智能解读
- 用户反馈功能

## 贡献指南

欢迎提交Issue和Pull Request来改进这个功能：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。
