# NutriCoach Pro - 健身营养定制系统

## 系统概述

NutriCoach Pro 是一个专为健身人群设计的个性化饮食计划定制系统，集成了智能营养计算、个性化餐食生成、进度追踪和智能提醒功能。

## 核心功能

### 1. 用户档案管理
- **基础信息收集**：年龄、性别、身高、体重
- **健身目标设置**：减脂、增肌、维持体重
- **活动水平评估**：久坐、轻度、中度、重度活动
- **饮食偏好配置**：素食、生酮、低脂、无麸质等
- **过敏食物管理**：坚果、海鲜、鸡蛋等常见过敏源

### 2. 智能饮食计划生成
- **基于科学算法**：使用 Mifflin-St Jeor 公式计算基础代谢率
- **个性化调整**：根据目标强度（保守型/均衡型/激进型）调整热量
- **宏量营养素优化**：根据健身目标分配蛋白质、碳水、脂肪比例
- **DeepSeek AI 集成**：调用 DeepSeek API 生成个性化餐食建议

### 3. 餐食追踪系统
- **每日餐食计划**：早餐、午餐、晚餐、加餐、训练前后餐食
- **营养成分分析**：每餐热量、蛋白质、碳水、脂肪含量
- **完成度记录**：记录实际食用情况，追踪计划执行情况

### 4. 智能提醒系统
- **用餐时间提醒**：固定时间推送餐食提醒
- **训练相关提醒**：训练前加餐、训练后补充提醒
- **水分补充提醒**：定时提醒补充水分
- **漏记餐食提醒**：检测未记录的餐食并提醒

### 5. 进度分析
- **体重追踪**：记录体重变化趋势
- **完成率统计**：分析餐食计划执行情况
- **营养目标达成度**：实时显示营养目标完成进度

## 技术架构

### 后端技术栈
- **Django 4.x**：Web框架
- **PostgreSQL**：数据库
- **Celery**：异步任务处理
- **DeepSeek API**：AI营养建议生成

### 前端技术栈
- **Bootstrap 5**：UI框架
- **JavaScript ES6+**：交互逻辑
- **Chart.js**：数据可视化
- **Font Awesome**：图标库

### 数据模型设计
```python
# 核心模型
- FitnessUserProfile: 用户档案
- DietPlan: 饮食计划
- Meal: 餐食详情
- MealLog: 餐食记录
- WeightTracking: 体重追踪
- NutritionReminder: 营养提醒
- FoodDatabase: 食物数据库
```

## 安装部署

### 1. 环境要求
- Python 3.9+
- Django 4.x
- PostgreSQL 12+
- Redis (用于Celery)

### 2. 安装步骤
```bash
# 克隆项目
git clone <repository_url>
cd QAToolBox

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 初始化数据
python manage.py init_nutrition_data

# 启动开发服务器
python manage.py runserver
```

### 3. 环境配置
在 `settings.py` 中配置以下变量：
```python
# DeepSeek API 配置
DEEPSEEK_API_KEY = 'your_deepseek_api_key'

# Celery 配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

## 使用指南

### 1. 首次使用
1. 访问 `/nutrition-profile-setup/` 设置用户档案
2. 填写基础信息、健身目标、饮食偏好
3. 系统自动计算个性化营养需求

### 2. 生成饮食计划
1. 访问 `/nutrition-generate-plan/` 
2. 选择目标强度和训练频率
3. 系统调用 DeepSeek API 生成7天饮食计划
4. 确认生成并保存计划

### 3. 日常使用
1. **仪表板**：`/nutrition-dashboard/` 查看今日计划
2. **餐食记录**：`/nutrition-meal-log/` 记录实际食用情况
3. **体重追踪**：`/nutrition-weight-tracking/` 记录体重变化
4. **进度分析**：`/nutrition-progress/` 查看健身进展
5. **提醒管理**：`/nutrition-reminders/` 设置和管理提醒

### 4. API 接口
```python
# 生成饮食计划 API
POST /api/nutrition/generate-plan/
Content-Type: application/json

{
    "age": 25,
    "gender": "male",
    "height": 175,
    "weight": 70,
    "goal": "lose_weight",
    "activity_level": "moderate",
    "dietary_preferences": ["vegetarian"],
    "allergies": ["nuts"],
    "intensity": "balanced",
    "training_days_per_week": 3
}
```

## 算法说明

### 1. 基础代谢率计算 (BMR)
使用 Mifflin-St Jeor 公式：
```python
# 男性
BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 + 5

# 女性  
BMR = 10 × 体重(kg) + 6.25 × 身高(cm) - 5 × 年龄 - 161
```

### 2. 每日总能量消耗 (TDEE)
```python
TDEE = BMR × 活动系数

活动系数：
- 久坐: 1.2
- 轻度活动: 1.375
- 中度活动: 1.55
- 重度活动: 1.725
```

### 3. 目标热量调整
```python
# 减脂
目标热量 = TDEE - (500 × 强度系数)

# 增肌
目标热量 = TDEE + (300 × 强度系数)

# 维持
目标热量 = TDEE

强度系数：
- 保守型: 0.8
- 均衡型: 1.0
- 激进型: 1.2
```

### 4. 宏量营养素分配
```python
# 增肌
蛋白质: 35%, 碳水: 45%, 脂肪: 20%

# 减脂
蛋白质: 40%, 碳水: 30%, 脂肪: 30%

# 维持
蛋白质: 30%, 碳水: 40%, 脂肪: 30%
```

## 定时任务

### 1. 营养提醒任务
```python
# 每小时执行一次
@shared_task
def send_nutrition_reminders():
    # 发送定时提醒
```

### 2. 餐食完成检查
```python
# 每天下午2点执行
@shared_task  
def check_meal_completion():
    # 检查未完成的餐食并创建提醒
```

## 扩展功能

### 1. 智能厨房设备集成
预留API接口用于未来对接智能厨房设备，实现自动食材推荐和烹饪指导。

### 2. 多平台提醒
支持短信、邮件、智能手表推送等多种提醒方式。

### 3. 社交功能
用户可以分享饮食计划、交流健身心得、参与营养挑战。

### 4. 专业营养师咨询
集成在线咨询功能，用户可与专业营养师进行一对一咨询。

## 安全与隐私

### 1. 数据加密
- 敏感健康数据端到端加密存储
- 用户密码使用 bcrypt 加密

### 2. 隐私保护
- 营养数据仅用于生成饮食计划
- 用户可随时导出或删除个人数据
- 严格遵守 GDPR 隐私保护规定

### 3. 访问控制
- 基于角色的权限管理
- API 接口访问频率限制
- 敏感操作需要二次验证

## 故障排除

### 1. 常见问题
**Q: DeepSeek API 调用失败**
A: 检查 API 密钥配置和网络连接

**Q: 提醒功能不工作**
A: 确认 Celery 服务正常运行

**Q: 数据库连接错误**
A: 检查数据库配置和连接状态

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/django.log

# 查看 Celery 日志
tail -f logs/celery.log
```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进系统功能。

### 开发环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements/dev.txt

# 运行测试
python manage.py test apps.tools.tests.test_nutrition
```

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: support@nutricoach.pro
- GitHub Issues: [项目地址]/issues
- 文档: [项目地址]/docs

---

**NutriCoach Pro** - 让科学营养为您的健身目标保驾护航！
