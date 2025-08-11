# Pixabay食物摄影图片智能推荐系统使用指南

## 🎯 系统概述

本系统包含两个主要组件，用于从Pixabay食物摄影页面获取高质量图片，并通过智能识别为"中午吃什么"功能推荐合适的食物图片：

1. **完整版爬虫** (`pixabay_food_photography_crawler.py`) - 使用OpenCV进行图像分析
2. **简化版爬虫** (`pixabay_food_photography_simple.py`) - 使用轻量级关键词匹配

## 🚀 快速开始

### 方法一：使用简化版（推荐）

简化版不需要安装OpenCV，依赖更少，运行更快：

```bash
# 安装依赖
pip install requests beautifulsoup4 pillow

# 运行简化版爬虫
python pixabay_food_photography_simple.py
```

### 方法二：使用完整版

完整版提供更精确的图像分析，但需要安装更多依赖：

```bash
# 安装依赖
pip install requests beautifulsoup4 pillow opencv-python numpy

# 运行完整版爬虫
python pixabay_food_photography_crawler.py
```

## 📋 功能特性

### 🔍 智能图片识别
- **多维度匹配**：基于标题、标签、URL特征进行综合分析
- **关键词权重**：完全匹配(5分) > 部分匹配(3分) > 相关匹配(1分)
- **置信度评分**：自动计算匹配质量，只保留高质量推荐

### 🍽️ 食物分类系统
- **中餐**：26种经典菜品（麻婆豆腐、宫保鸡丁、红烧肉等）
- **西餐**：15种经典菜品（意大利面、披萨、汉堡包等）
- **日料**：7种经典菜品（寿司、拉面、天妇罗等）
- **韩料**：7种经典菜品（韩式烤肉、泡菜汤等）
- **泰餐**：6种经典菜品（泰式咖喱、冬阴功等）

### 📊 自动更新机制
- **实时爬取**：直接从Pixabay食物摄影页面获取最新图片
- **智能筛选**：过滤低质量图片，只保留高质量食物摄影
- **自动映射**：自动更新`comprehensive_food_images.py`文件

## 🛠️ 详细使用说明

### 1. 系统配置

#### 环境要求
```python
# 基础依赖
requests>=2.25.1
beautifulsoup4>=4.9.3
pillow>=8.0.0

# 完整版额外依赖
opencv-python>=4.5.0
numpy>=1.19.0
```

#### 文件结构
```
QAToolBox/
├── pixabay_food_photography_simple.py      # 简化版爬虫
├── pixabay_food_photography_crawler.py     # 完整版爬虫
├── update_food_images_with_pixabay.py      # API版本更新器
├── apps/tools/services/
│   └── comprehensive_food_images.py        # 图片映射文件
└── 输出文件/
    ├── pixabay_food_simple_results.json    # 简化版结果
    ├── pixabay_food_analysis_results.json  # 完整版结果
    ├── PIXABAY_FOOD_SIMPLE_REPORT.md       # 简化版报告
    └── PIXABAY_FOOD_ANALYSIS_REPORT.md     # 完整版报告
```

### 2. 运行流程

#### 简化版运行流程
```python
# 1. 爬取Pixabay食物摄影页面
images = crawler.crawl_food_photography_page()

# 2. 分析图片特征（基于文本和URL）
analyzed_images = []
for image_info in images:
    result = crawler.analyze_image_simple(image_info)
    if result.get('success'):
        analyzed_images.append(result)

# 3. 生成食物推荐
recommendations = crawler.generate_food_recommendations(analyzed_images)

# 4. 创建图片映射
image_mapping = crawler.create_enhanced_image_mapping(recommendations)

# 5. 自动更新文件
update_comprehensive_food_images(image_mapping)
```

#### 完整版运行流程
```python
# 1. 爬取Pixabay食物摄影页面
images = crawler.crawl_food_photography_page()

# 2. 下载并分析图片（使用OpenCV）
analyzed_images = []
for image_info in images:
    result = crawler.download_and_analyze_image(image_info)
    if result.get('success'):
        analyzed_images.append(result)

# 3. 生成食物推荐（基于图像特征）
recommendations = crawler.generate_food_recommendations(analyzed_images)

# 4. 创建图片映射
image_mapping = crawler.create_enhanced_image_mapping(recommendations)
```

### 3. 配置选项

#### 爬虫配置
```python
class SimplePixabayFoodCrawler:
    def __init__(self):
        # 基础URL配置
        self.base_url = "https://pixabay.com"
        self.search_url = "https://pixabay.com/photos/search/food%20photography/"
        
        # 请求头配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # ... 其他配置
        }
        
        # 关键词权重配置
        self.keyword_weights = {
            'exact_match': 5,    # 完全匹配权重
            'partial_match': 3,  # 部分匹配权重
            'related_match': 1,  # 相关匹配权重
        }
```

#### 分析参数配置
```python
def run_complete_analysis(self, max_images: int = 30) -> Dict:
    """
    运行完整分析流程
    
    Args:
        max_images: 最大分析图片数量（默认30张）
    """
    
def match_food_types(self, analysis: Dict) -> List[Dict]:
    """
    匹配食物类型
    
    Args:
        analysis: 图片分析结果
        
    Returns:
        匹配的食物类型列表（返回前5个最佳匹配）
    """
```

### 4. 输出结果

#### JSON结果文件
```json
{
  "recommendations": {
    "chinese": [
      {
        "food_name": "麻婆豆腐",
        "image_url": "https://pixabay.com/get/...",
        "confidence": 0.85,
        "matched_keywords": ["tofu", "spicy"],
        "image_title": "Spicy Mapo Tofu",
        "score": 12
      }
    ]
  },
  "image_mapping": {
    "麻婆豆腐": "https://pixabay.com/get/...?w=500&h=400&fit=crop&crop=center"
  },
  "stats": {
    "total_images_crawled": 45,
    "total_images_analyzed": 30,
    "total_recommendations": 28,
    "image_mapping_count": 28
  }
}
```

#### 分析报告
```markdown
# Pixabay食物摄影智能分析报告

## 📊 分析统计
- **爬取图片数量**: 45
- **分析图片数量**: 30
- **推荐数量**: 28
- **图片映射数量**: 28

## 🍽️ 菜系推荐分布
### CHINESE (12个推荐)
- **麻婆豆腐** (置信度: 0.85, 分数: 12)
  - 匹配关键词: tofu, spicy
  - 图片标题: Spicy Mapo Tofu
```

## 🔧 高级配置

### 自定义食物关键词
```python
# 在爬虫类中修改food_keywords字典
self.food_keywords = {
    'chinese': {
        '新菜品': ['new dish', 'custom keyword', '中文关键词'],
        # ... 其他菜品
    }
}
```

### 调整匹配阈值
```python
# 修改置信度阈值
if match['confidence'] > 0.2:  # 默认0.2，可调整为0.1-0.5
    recommendations[match['cuisine']].append(...)
```

### 自定义图片优化参数
```python
# 修改图片URL优化参数
if '?' not in image_url:
    image_url += '?w=500&h=400&fit=crop&crop=center'  # 可调整尺寸和裁剪方式
```

## 🚨 注意事项

### 1. 网络请求限制
- 系统内置请求延迟，避免对Pixabay服务器造成压力
- 建议在非高峰时段运行，提高成功率

### 2. 图片质量控制
- 系统自动过滤低质量图片
- 只保留置信度较高的推荐
- 图片URL自动优化为500x400像素

### 3. 版权安全
- 所有图片均来自Pixabay免费图片库
- 图片均为免费商用图片
- 建议在使用时保留Pixabay版权信息

### 4. 错误处理
- 系统具备完善的错误处理机制
- 网络异常时自动重试
- 图片分析失败时跳过，不影响整体流程

## 📈 性能优化

### 1. 批量处理
```python
# 可以调整max_images参数控制处理数量
results = crawler.run_complete_analysis(max_images=50)  # 处理50张图片
```

### 2. 并发处理（高级）
```python
# 可以添加多线程支持提高处理速度
import concurrent.futures

def analyze_images_parallel(images, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawler.analyze_image_simple, img) for img in images]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    return results
```

### 3. 缓存机制
```python
# 可以添加结果缓存，避免重复分析
import pickle

def save_cache(results, filename='food_analysis_cache.pkl'):
    with open(filename, 'wb') as f:
        pickle.dump(results, f)

def load_cache(filename='food_analysis_cache.pkl'):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
```

## 🔄 定期更新

### 自动化脚本
```bash
#!/bin/bash
# 创建定时任务脚本

# 每天凌晨2点运行更新
0 2 * * * cd /path/to/QAToolBox && python pixabay_food_photography_simple.py

# 或者每周运行一次
0 2 * * 0 cd /path/to/QAToolBox && python pixabay_food_photography_simple.py
```

### 监控和日志
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('food_analysis.log'),
        logging.StreamHandler()
    ]
)

# 在爬虫中添加日志
logging.info(f"开始分析图片: {image_info.get('title', 'Unknown')}")
logging.warning(f"图片分析失败: {e}")
logging.info(f"分析完成，共处理 {len(results)} 张图片")
```

## 🎉 总结

通过使用Pixabay食物摄影图片智能推荐系统，您可以：

1. **自动获取高质量食物图片**：直接从Pixabay食物摄影页面爬取
2. **智能匹配食物类型**：使用多维度分析算法精确匹配
3. **自动更新图片库**：一键更新"中午吃什么"功能的图片映射
4. **保持图片质量**：只推荐高质量、高置信度的图片
5. **支持多种菜系**：涵盖中餐、西餐、日料、韩料、泰餐等

系统设计轻量级且易于使用，推荐使用简化版进行日常更新，完整版用于深度分析和优化。
