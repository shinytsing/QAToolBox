# VanityOS —— 欲望驱动的开发者激励系统

## 🚀 系统概述

VanityOS 是一个完全符合您提供的AI指令精神的欲望驱动开发者激励系统。它将代码输出直接映射到欲望满足进度，为开发者提供即时多巴胺反馈。

## 🎯 核心功能实现

### 1. 点击四次进入里世界
- **位置**: 主页 `templates/home.html`
- **触发方式**: 连续点击左上角 "QATOOLBOX" 标题四次
- **效果**: 标题闪烁变红，1秒后跳转到 `/vanity-os/`
- **实现**: JavaScript 点击计数器 + 动画效果

### 2. 欲望仪表盘 (Vanity Dashboard)
- **位置**: `/tools/vanity-os/`
- **功能**: 实时可视化虚拟财富与欲望兑现进度
- **数据源**: 代码提交、网站访问量、赞助收入
- **UI组件**:
  - 虚拟财富计数器 (¥0.00)
  - 玛莎拉蒂进度条 (0% - 100%)
  - 罪恶积分显示
  - 欲望兑换建议

### 3. 罪恶积分系统 (Sin Points)
- **位置**: `/tools/vanity-rewards/`
- **积分规则**:
  - 提交1行原生代码: +1积分
  - 拒绝AI补全: +5积分
  - 完成1小时深度工作: +10积分
  - 收到1元赞助: +100积分
- **API端点**: `/tools/api/sin-points/add/`

### 4. 金主荣耀墙 (Sponsor Hall of Fame)
- **位置**: `/tools/sponsor-hall-of-fame/`
- **功能**: 展示赞助者名单及对应的浮夸特效
- **动态特效**:
  - 金色闪耀 (golden-bling)
  - 钻石闪烁 (diamond-sparkle)
  - 白金光芒 (platinum-glow)
  - 银色光辉 (silver-shine)
- **API端点**: `/tools/api/sponsors/`

### 5. 欲望驱动待办清单 (Lust Todo List)
- **位置**: `/tools/vanity-todo-list/`
- **功能**: 每个任务绑定欲望兑现值
- **奖励示例**:
  - 难度1: 虚拟咖啡券
  - 难度3: 虚拟劳力士+3%豪车进度
  - 难度5: 虚拟游艇体验
  - 难度10: 虚拟平行宇宙
- **API端点**: `/tools/api/vanity-tasks/`

## 🗄️ 数据模型

### VanityWealth (虚拟财富)
```python
- virtual_wealth: DecimalField (虚拟财富总额)
- code_lines: IntegerField (代码行数)
- page_views: IntegerField (网站访问量)
- donations: DecimalField (赞助金额)
```

### SinPoints (罪恶积分)
```python
- action_type: CharField (行为类型)
- points_earned: IntegerField (获得积分)
- metadata: JSONField (元数据)
```

### Sponsor (赞助者)
```python
- name: CharField (赞助者姓名)
- amount: DecimalField (赞助金额)
- message: TextField (赞助留言)
- effect: CharField (特效类型)
- is_anonymous: BooleanField (是否匿名)
```

### VanityTask (欲望任务)
```python
- title: CharField (任务标题)
- task_type: CharField (任务类型)
- difficulty: IntegerField (难度等级1-10)
- reward_value: IntegerField (奖励价值)
- reward_description: CharField (奖励描述)
```

## 🎨 视觉设计特色

### 浮夸的UI设计
- **金色渐变**: 主色调使用金色 (#ffd700)
- **动态背景**: 金钱雨效果 + 奢侈品形状浮动
- **特效动画**: 根据赞助金额显示不同级别的闪耀效果
- **响应式设计**: 完美适配各种设备

### 多巴胺反馈机制
- **即时反馈**: 每次操作都有视觉和数值反馈
- **进度可视化**: 玛莎拉蒂进度条实时更新
- **成就系统**: 积分获得时的浮动动画
- **欲望映射**: 代码行数直接转换为虚拟财富

## 🔧 技术实现

### 后端架构
- **Django**: 主框架
- **SQLite**: 数据库 (可升级到PostgreSQL)
- **RESTful API**: 前后端分离
- **CSRF保护**: 安全认证

### 前端技术
- **原生JavaScript**: 无框架依赖
- **CSS3动画**: 流畅的视觉效果
- **响应式设计**: 移动端友好
- **实时更新**: 30秒自动刷新数据

### API接口
```javascript
// 虚拟财富
GET /tools/api/vanity-wealth/

// 罪恶积分
POST /tools/api/sin-points/add/

// 赞助者
GET /tools/api/sponsors/
POST /tools/api/sponsors/add/

// 欲望任务
GET /tools/api/vanity-tasks/
POST /tools/api/vanity-tasks/add/
POST /tools/api/vanity-tasks/complete/
```

## 🎮 使用方法

### 1. 进入里世界
1. 访问主页
2. 连续点击左上角 "QATOOLBOX" 四次
3. 等待闪烁动画完成
4. 自动跳转到VanityOS仪表盘

### 2. 赚取罪恶积分
- 点击 "写1行代码" 按钮 (+1积分)
- 点击 "拒绝AI" 按钮 (+5积分)
- 点击 "深度工作" 按钮 (+10积分)
- 在赞助页面添加赞助 (+100积分)

### 3. 查看虚拟财富
- 虚拟财富 = 代码行数 × 0.01 + 访问量 × 0.001 + 赞助金额 × 1
- 玛莎拉蒂进度 = (虚拟财富 / 500,000) × 100%

### 4. 管理欲望任务
- 添加新任务并设置难度
- 完成任务获得积分奖励
- 查看任务完成历史

## 🚀 部署说明

### 1. 数据库迁移
```bash
python manage.py makemigrations tools
python manage.py migrate
```

### 2. 启动服务器
```bash
python manage.py runserver
```

### 3. 访问地址
- 主页: `http://localhost:8000/`
- VanityOS: `http://localhost:8000/tools/vanity-os/`
- 测试页面: `http://localhost:8000/test_vanity_os.html`

## 🎯 符合AI指令的设计理念

### 1. 欲望优先原则
- ✅ 所有代码直接贡献于增加虚拟财富
- ✅ 强化「反程序员」人设
- ✅ 提供即时多巴胺反馈

### 2. 禁止行为规避
- ✅ 不过度优化可读性 (保持浮夸风格)
- ✅ 不使用无聊的企业级技术栈 (原生JS + Django)
- ✅ 不写没有视觉回报的后端逻辑 (所有API都有UI反馈)

### 3. 浮夸元素
- ✅ 金色渐变 + 钻石装饰动画
- ✅ 实时计算代码行数 × 0.01 + 赞助金额
- ✅ 到达100%时显示引擎轰鸣效果
- ✅ 控制台输出 "🚗 Vroom! 代码已变现"

## 🔮 未来扩展

### 1. 反程序员形象生成器
- 用户上传健身/奢侈品照片
- 结合代码片段生成「物质主义极客」形象
- 配文：「我测的不是代码，是你们的财富上限」

### 2. CEO控制台快捷键
- 按下Shift+$开启「欲望狂暴模式」
- 所有UI变成镀金
- 播放《金钱之歌》MIDI音效

### 3. 更多欲望映射
- 代码提交频率 → 虚拟股票收益
- Bug修复数量 → 虚拟房产增值
- 技术博客发布 → 虚拟粉丝增长

## 🎉 总结

VanityOS 完全实现了您提供的AI指令精神，将开发者的代码输出直接映射到欲望满足进度。系统通过浮夸的视觉效果、即时的多巴胺反馈和虚拟财富激励机制，成功地将「厌恶传统努力」的开发者转化为「渴望物质回报」的编码机器。

**核心价值**: 将代码输出直接映射到欲望满足进度 ✅

**目标用户**: 渴望物质回报但厌恶传统努力的开发者 ✅

**系统特色**: 浮夸、即时、欲望驱动 ✅

现在，您的代码每一行都在为玛莎拉蒂添砖加瓦！🚗💎 