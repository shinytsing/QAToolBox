# 🤝 WanderAI 好心人攻略功能说明

## 功能概述

好心人攻略是WanderAI智能旅游攻略系统的一个重要功能，允许用户创建、分享、查看和使用其他用户分享的旅游攻略。这个功能体现了"好心人"精神，让旅行者可以互相帮助，分享宝贵的旅行经验。

## 主要功能

### 1. 创建攻略 📝
- **攻略标题**：为攻略起一个吸引人的标题
- **目的地**：指定攻略的目的地
- **旅行风格**：选择攻略的旅行风格（通用型、冒险型、休闲型、文化型、美食型、购物型、摄影型）
- **预算范围**：设置预算范围（经济型、舒适型、豪华型、奢华型）
- **旅行时长**：指定旅行天数
- **兴趣偏好**：选择感兴趣的标签（美食、文化、自然、购物、历史、艺术、运动、摄影、夜生活、温泉、海滩、登山）
- **攻略摘要**：简要描述攻略的亮点和特色
- **攻略内容**：详细的攻略内容，支持Markdown格式
- **附件上传**：可上传PDF、Word、TXT、Markdown格式的附件（最大10MB）

### 2. 查看攻略 👀
- **攻略列表**：浏览所有公开的好心人攻略
- **搜索功能**：按目的地和旅行风格搜索攻略
- **攻略详情**：查看攻略的完整内容
- **统计信息**：显示攻略的查看次数、下载次数、使用次数
- **作者信息**：显示攻略创建者的用户名

### 3. 下载攻略 📥
- 下载攻略的附件文件
- 支持PDF、Word、TXT、Markdown格式
- 自动记录下载次数

### 4. 使用攻略 🎯
- 将好心人攻略的内容加载到新建攻略表单中
- 自动填充目的地、旅行风格、预算范围、旅行时长、兴趣偏好等信息
- 记录使用次数

## 技术实现

### 数据模型
```python
class UserGeneratedTravelGuide(models.Model):
    """用户生成的旅游攻略模型 - 好心人的攻略"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建用户')
    title = models.CharField(max_length=200, verbose_name='攻略标题')
    destination = models.CharField(max_length=200, verbose_name='目的地')
    content = models.TextField(verbose_name='攻略内容')
    summary = models.TextField(blank=True, null=True, verbose_name='攻略摘要')
    
    # 攻略分类
    travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 文件附件
    attachment = models.FileField(upload_to='travel_guides/', blank=True, null=True, verbose_name='附件')
    attachment_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='附件名称')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 状态
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
```

### API接口

#### 1. 获取攻略列表
```
GET /tools/api/user_generated_travel_guide/
参数：
- destination: 目的地（可选）
- travel_style: 旅行风格（可选）
- page: 页码（可选，默认1）
- page_size: 每页数量（可选，默认10）
```

#### 2. 创建攻略
```
POST /tools/api/user_generated_travel_guide/
参数：
- title: 攻略标题（必填）
- destination: 目的地（必填）
- content: 攻略内容（必填）
- summary: 攻略摘要（可选）
- travel_style: 旅行风格（可选）
- budget_range: 预算范围（可选）
- travel_duration: 旅行时长（可选）
- interests: 兴趣标签JSON数组（可选）
- attachment: 附件文件（可选）
```

#### 3. 获取攻略详情
```
GET /tools/api/user_generated_travel_guide/{guide_id}/
```

#### 4. 下载攻略
```
POST /tools/api/user_generated_travel_guide/{guide_id}/download/
```

#### 5. 使用攻略
```
POST /tools/api/user_generated_travel_guide/{guide_id}/use/
```

### 前端功能

#### 1. 攻略列表页面
- 显示所有公开的攻略
- 支持搜索和筛选
- 显示攻略的基本信息和统计

#### 2. 创建攻略表单
- 完整的表单验证
- 支持Markdown格式的内容编辑
- 文件上传功能
- 兴趣标签选择

#### 3. 攻略详情页面
- 格式化显示攻略内容
- 支持Markdown渲染
- 显示统计信息和标签
- 提供下载和使用按钮

#### 4. 使用攻略功能
- 自动填充新建攻略表单
- 智能匹配预算范围
- 保持用户选择的兴趣标签

## 使用流程

### 创建攻略
1. 进入WanderAI旅游攻略页面
2. 点击"好心人攻略"标签
3. 点击"创建攻略"按钮
4. 填写攻略信息
5. 上传附件（可选）
6. 点击"发布攻略"

### 查看攻略
1. 进入"好心人攻略"页面
2. 浏览攻略列表
3. 使用搜索功能筛选攻略
4. 点击攻略卡片查看详情

### 使用攻略
1. 在攻略详情页面点击"使用此攻略"
2. 系统自动跳转到新建攻略页面
3. 攻略信息已自动填充
4. 可以修改参数后生成新的攻略

### 下载攻略
1. 在攻略详情页面点击"下载附件"
2. 系统自动下载攻略文件
3. 文件保存到本地

## 特色功能

### 1. Markdown支持
攻略内容支持Markdown格式，可以：
- 使用**粗体**和*斜体*
- 创建标题层级
- 添加[链接](url)
- 创建列表
- 格式化文本

### 2. 智能标签系统
- 自动分类攻略类型
- 支持多标签筛选
- 个性化推荐

### 3. 统计追踪
- 实时统计查看次数
- 记录下载和使用行为
- 帮助用户了解攻略受欢迎程度

### 4. 文件上传
- 支持多种文件格式
- 文件大小限制
- 安全验证

## 安全考虑

### 1. 用户权限
- 只有登录用户才能创建攻略
- 攻略创建者可以管理自己的攻略
- 管理员可以审核和管理所有攻略

### 2. 内容审核
- 攻略需要审核通过才能公开
- 支持举报不当内容
- 自动过滤敏感词汇

### 3. 文件安全
- 限制文件类型和大小
- 扫描上传文件的安全性
- 防止恶意文件上传

## 未来扩展

### 1. 攻略评分系统
- 用户可以对攻略进行评分
- 显示攻略的平均评分
- 基于评分进行推荐

### 2. 攻略评论功能
- 用户可以对攻略进行评论
- 支持回复和讨论
- 帮助改进攻略内容

### 3. 攻略版本管理
- 支持攻略的版本更新
- 记录修改历史
- 用户可以查看不同版本

### 4. 攻略收藏功能
- 用户可以收藏喜欢的攻略
- 个人收藏夹管理
- 快速访问收藏的攻略

### 5. 攻略分享功能
- 支持分享到社交媒体
- 生成分享链接
- 二维码分享

## 测试

使用提供的测试页面 `test_good_people_guide.html` 可以测试所有功能：

1. 获取攻略列表
2. 创建测试攻略
3. 获取攻略详情
4. 使用攻略
5. 搜索攻略

## 总结

好心人攻略功能体现了WanderAI系统的社区价值，让旅行者可以互相分享经验，共同创造更好的旅行体验。通过这个功能，用户可以：

- 分享自己的旅行经验
- 学习他人的旅行攻略
- 获得个性化的旅行建议
- 建立旅行者社区

这个功能不仅提升了WanderAI的实用性，也增强了用户之间的互动和分享精神。
