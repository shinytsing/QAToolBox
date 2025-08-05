# 智能旅游攻略生成引擎

## 🎯 项目概述

这是一个基于AI的智能旅游攻略生成引擎，能够自动抓取多平台数据，结合AI分析，为用户生成个性化的旅游攻略。

## ✨ 核心功能

### 1. 数据抓取阶段
- **DeepSeek API搜索**：`{地点} 小红书最新攻略 site:xiaohongshu.com`
- **Google Custom Search API**：`{地点} 马蜂窝2024旅行指南`
- **OpenWeatherMap API**：获取实时天气数据

### 2. 信息结构化
```python
def 提取核心信息(原始文本):
    return {
        "景点": re.findall(r"推荐景点[:：]\s*(.+)", 原始文本),
        "美食": re.findall(r"必吃[：:]\s*(.+)", 原始文本),
        "贴士": re.findall(r"注意[：:]\s*(.+)", 原始文本)
    }
```

### 3. AI合成阶段
- 结合用户偏好（旅行风格、预算、时长、兴趣）
- 生成个性化行程安排
- 提供费用预算和实用贴士

## 🚀 快速开始

### 1. 环境准备

确保已安装Python 3.8+和所需依赖：

```bash
pip install -r requirements/base.txt
```

### 2. API配置

运行配置脚本设置API密钥：

```bash
python setup_travel_apis.py
```

需要配置的API：
- **DeepSeek API**：用于AI内容生成
- **Google Custom Search API**：用于搜索马蜂窝攻略
- **OpenWeatherMap API**：用于获取天气数据

### 3. 测试配置

验证API配置是否正确：

```bash
python test_travel_apis.py
```

### 4. 运行演示

查看完整功能演示：

```bash
python demo_travel_guide.py
```

## 📋 API获取指南

### DeepSeek API
1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册账户并获取API密钥
3. API密钥格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Google Custom Search API
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用Custom Search API
3. 获取API密钥
4. 访问 [Google Custom Search](https://cse.google.com/)
5. 创建自定义搜索引擎，包含马蜂窝网站
6. 获取搜索引擎ID

### OpenWeatherMap API
1. 访问 [OpenWeatherMap](https://openweathermap.org/api)
2. 注册免费账户
3. 获取API密钥

## 🔧 使用方法

### 基本使用

```python
from apps.tools.services.travel_data_service import TravelDataService

# 创建服务实例
service = TravelDataService()

# 生成攻略
guide = service.get_travel_guide_data(
    destination="北京",
    travel_style="文化探索",
    budget_range="中等预算",
    travel_duration="3天",
    interests=["历史古迹", "美食", "文化体验"]
)

# 查看结果
print(guide['title'])
print(guide['daily_schedule'])
print(guide['top_attractions'])
```

### 信息提取

```python
# 从文本中提取核心信息
text = "推荐景点：故宫博物院、天安门广场 必吃：北京烤鸭、炸酱面 注意：避开节假日高峰"
result = service.提取核心信息(text)

print(result['景点'])  # ['故宫博物院、天安门广场']
print(result['美食'])  # ['北京烤鸭、炸酱面']
print(result['贴士'])  # ['避开节假日高峰']
```

## 📊 输出格式

生成的攻略包含以下信息：

```json
{
    "title": "北京深度攻略（AI优化版）",
    "daily_schedule": [
        {
            "title": "Day 1: 故宫博物院 + 天安门广场",
            "activities": ["参观故宫博物院", "游览天安门广场", "品尝北京烤鸭"]
        }
    ],
    "top_attractions": ["故宫博物院", "天安门广场", "颐和园"],
    "must_eat_foods": ["北京烤鸭", "炸酱面", "豆汁"],
    "travel_tips": ["避开节假日高峰", "提前预约门票"],
    "cost_breakdown": {
        "accommodation": 800,
        "food": 300,
        "transportation": 100,
        "tickets": 200,
        "others": 100,
        "total": 1500
    },
    "weather_info": {
        "temperature": 25,
        "weather": "晴天",
        "humidity": 60
    }
}
```

## 🛠️ 项目结构

```
QAToolBox/
├── apps/tools/services/
│   └── travel_data_service.py    # 核心服务类
├── setup_travel_apis.py          # API配置脚本
├── test_travel_apis.py           # API测试脚本
├── demo_travel_guide.py          # 功能演示脚本
├── env.example                   # 环境变量示例
└── TRAVEL_GUIDE_ENGINE_README.md # 本文档
```

## 🔍 核心类说明

### TravelDataService

主要的服务类，包含以下核心方法：

- `get_travel_guide_data()`: 生成完整攻略
- `_数据抓取阶段()`: 抓取多平台数据
- `_信息结构化()`: 结构化处理数据
- `_AI合成阶段()`: AI生成最终攻略
- `提取核心信息()`: 从文本提取关键信息

## 🎨 自定义配置

### 修改搜索查询

在 `travel_data_service.py` 中可以自定义搜索查询：

```python
# 小红书搜索
search_query = f"{destination} 小红书最新攻略 site:xiaohongshu.com"

# 马蜂窝搜索
query = f"{destination} 马蜂窝2024旅行指南"
```

### 调整信息提取规则

修改正则表达式来适应不同的文本格式：

```python
def 提取核心信息(self, 原始文本: str) -> Dict:
    return {
        "景点": re.findall(r"推荐景点[:：]\s*(.+)", 原始文本),
        "美食": re.findall(r"必吃[：:]\s*(.+)", 原始文本),
        "贴士": re.findall(r"注意[：:]\s*(.+)", 原始文本)
    }
```

## 🚨 注意事项

1. **API限制**：各API都有调用频率限制，请合理使用
2. **数据准确性**：AI生成的内容仅供参考，建议结合实际情况
3. **网络连接**：需要稳定的网络连接来调用外部API
4. **费用控制**：API调用可能产生费用，请注意控制使用量

## 🐛 故障排除

### 常见问题

1. **API密钥错误**
   - 检查密钥格式是否正确
   - 确认密钥是否有效且未过期

2. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

3. **依赖包缺失**
   - 运行 `pip install -r requirements/base.txt`
   - 检查Python版本是否兼容

### 调试模式

启用详细日志输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 性能优化

1. **缓存机制**：对重复查询进行缓存
2. **并发请求**：并行调用多个API
3. **错误重试**：实现指数退避重试机制
4. **数据压缩**：压缩传输数据减少带宽

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件
- 参与讨论

---

**享受智能旅游攻略生成引擎带来的便利！** 🎉 