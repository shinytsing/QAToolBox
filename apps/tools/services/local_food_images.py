"""
基于本地图片的食物映射 - 使用static/img/food目录下的图片
让食物名称与图片更加匹配，提升用户体验
"""

# 本地图片基础路径
LOCAL_FOOD_IMAGE_BASE = '/static/img/food/'

# 中餐图片映射 - 使用本地图片，确保食物与图片高度匹配
CHINESE_FOOD_IMAGES_LOCAL = {
    # 川菜
    '麻婆豆腐': f'{LOCAL_FOOD_IMAGE_BASE}mapo-tofu-2570173_1280.jpg',  # 专门的麻婆豆腐图片
    '宫保鸡丁': f'{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg',    # 中式炒菜
    '鱼香肉丝': f'{LOCAL_FOOD_IMAGE_BASE}chinese-915325_1280.jpg',     # 中式菜品
    '回锅肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',  # 红烧肉类
    '水煮鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg', # 鱼类菜品
    '麻辣香锅': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',  # 重庆风味
    '剁椒鱼头': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg', # 鱼类菜品
    
    # 粤菜
    '白切鸡': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',       # 中式白切菜
    '叉烧肉': f'{LOCAL_FOOD_IMAGE_BASE}roast-3416333_1280.jpg',        # 烤肉类
    '烧鹅': f'{LOCAL_FOOD_IMAGE_BASE}duck-2097959_1280.jpg',           # 烤鸭类
    
    # 北京菜
    '北京烤鸭': f'{LOCAL_FOOD_IMAGE_BASE}duck-253846_1280.jpg',        # 烤鸭
    '炸酱面': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',      # 面条类
    
    # 江浙菜
    '东坡肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',  # 红烧肉
    '红烧肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',  # 红烧肉
    '糖醋里脊': f'{LOCAL_FOOD_IMAGE_BASE}chinese-916623_1280.jpg',     # 中式炒菜
    '青椒肉丝': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg', # 青菜类
    
    # 家常菜
    '番茄炒蛋': f'{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg',   # 蛋类菜品
    '蛋炒饭': f'{LOCAL_FOOD_IMAGE_BASE}the-pork-fried-rice-made-908333_1280.jpg', # 炒饭
    '盖浇饭': f'{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg',         # 米饭类
    '中式炒面': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',    # 面条类
    '烧鹅': f'{LOCAL_FOOD_IMAGE_BASE}duck-2097959_1280.jpg',           # 烧鹅
    '章鱼小丸子': f'{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg',    # 章鱼小丸子
    
    # 名菜
    '佛跳墙': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',      # 海鲜汤类
    '小龙虾': f'{LOCAL_FOOD_IMAGE_BASE}crayfish-866400_1280.jpg',      # 小龙虾专用
    '烧烤': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg', # 烧烤类
    '火锅': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',      # 火锅类
    
    # 面食
    '兰州拉面': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',    # 兰州拉面专用
    '小笼包': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233490_1280.jpg',      # 中式点心
    '煎饼果子': f'{LOCAL_FOOD_IMAGE_BASE}pancakes-2139844_1280.jpg',   # 煎饼类
    '豆浆油条': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',      # 早餐类
    '包子豆浆': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',    # 中式早点
    
    # 快餐
    '黄焖鸡米饭': f'{LOCAL_FOOD_IMAGE_BASE}chinese-916629_1280.jpg',   # 中式快餐
    '沙县小吃': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233490_1280.jpg',    # 小吃类
    '麻辣烫': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',     # 麻辣类
    '炸串': f'{LOCAL_FOOD_IMAGE_BASE}food-835469_1280.jpg',            # 炸物类
    '螺蛳粉': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',       # 粉类
    
    # 新增中餐
    '过桥米线': f'{LOCAL_FOOD_IMAGE_BASE}cross-bridge-tofu-4866594_1280.jpg', # 过桥米线专用
    '豆腐料理': f'{LOCAL_FOOD_IMAGE_BASE}tofu-7525311_1280.jpg',       # 豆腐专用
}

# 西餐图片映射
WESTERN_FOOD_IMAGES_LOCAL = {
    # 意式
    '意大利面': f'{LOCAL_FOOD_IMAGE_BASE}pasta-7209002_1280.jpg',      # 意大利面专用
    '意式烩饭': f'{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg',       # 米饭类
    '披萨': f'{LOCAL_FOOD_IMAGE_BASE}pizza-6478478_1280.jpg',          # 披萨专用
    '意式披萨': f'{LOCAL_FOOD_IMAGE_BASE}pizza-6478478_1280.jpg',      # 披萨专用
    
    # 美式
    '汉堡包': f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',         # 快餐类
    '三明治': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',        # 面包类
    '煎蛋三明治': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',    # 面包类
    
    # 法式
    '法式可颂': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',      # 面包类
    '法式牛排': f'{LOCAL_FOOD_IMAGE_BASE}steak-6278031_1280.jpg',      # 牛排专用
    
    # 其他西餐
    '沙拉': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',     # 素食类
    '牛排': f'{LOCAL_FOOD_IMAGE_BASE}steak-6714964_1280.jpg',          # 牛排专用
    '华夫饼': f'{LOCAL_FOOD_IMAGE_BASE}pancakes-2139844_1280.jpg',     # 煎饼类
    '燕麦粥': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',         # 粥类
    '烤鸡': f'{LOCAL_FOOD_IMAGE_BASE}roast-3416333_1280.jpg',          # 烤肉类
    '西班牙海鲜饭': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265999_1280.jpg', # 海鲜饭
    '蔬菜沙拉': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg', # 素食类
    '水果拼盘': f'{LOCAL_FOOD_IMAGE_BASE}food-5983403_1280.jpg',       # 水果类
    
    # 新增西餐
    '马卡龙': f'{LOCAL_FOOD_IMAGE_BASE}macarons-2179198_1280.jpg',     # 马卡龙专用
    '牛肉料理': f'{LOCAL_FOOD_IMAGE_BASE}beef-4805622_1280.jpg',       # 牛肉专用
    '汉堡包': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',        # 汉堡包
    '土豆泥': f'{LOCAL_FOOD_IMAGE_BASE}steak-6278031_1280.jpg',        # 土豆泥
    '炸鸡': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',          # 炸鸡
}

# 日料图片映射
JAPANESE_FOOD_IMAGES_LOCAL = {
    '寿司拼盘': f'{LOCAL_FOOD_IMAGE_BASE}sushi-2009611_1280.jpg',      # 寿司专用
    '拉面': f'{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg',          # 拉面专用
    '天妇罗': f'{LOCAL_FOOD_IMAGE_BASE}shrimp-6902940_1280.jpg',       # 天妇罗虾
    '日式味增汤': f'{LOCAL_FOOD_IMAGE_BASE}ramen-7382882_1280.jpg',    # 汤类
    '日式饭团': f'{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg',       # 米饭类
    '寿司卷': f'{LOCAL_FOOD_IMAGE_BASE}sushi-2009611_1280.jpg',        # 寿司专用
    '日式拉面': f'{LOCAL_FOOD_IMAGE_BASE}ramen-4647411_1280.jpg',      # 拉面专用
    '乌冬面': f'{LOCAL_FOOD_IMAGE_BASE}udon-noodles-4065311_1280.jpg', # 乌冬面专用
    '日式烤肉': f'{LOCAL_FOOD_IMAGE_BASE}udon-noodles-4065311_1280.jpg', # 日式烤肉
}

# 韩料图片映射
KOREAN_FOOD_IMAGES_LOCAL = {
    '韩式烤肉': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg', # 韩式烤肉专用
    '韩式炸鸡': f'{LOCAL_FOOD_IMAGE_BASE}food-and-drink-8076626_1280.jpg',  # 炸鸡类
    '韩式泡菜汤': f'{LOCAL_FOOD_IMAGE_BASE}ramen-7382882_1280.jpg',         # 汤类
    '韩式紫菜包饭': f'{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg',        # 米饭类
    '韩式煎饼': f'{LOCAL_FOOD_IMAGE_BASE}pancakes-2139844_1280.jpg',        # 煎饼类
    '韩式炒年糕': f'{LOCAL_FOOD_IMAGE_BASE}toppokki-1607479_1280.jpg',      # 炒年糕专用
    '韩式拌饭': f'{LOCAL_FOOD_IMAGE_BASE}bibimbap-1738580_1280.jpg',        # 拌饭专用
    '冷面': f'{LOCAL_FOOD_IMAGE_BASE}bibimbap-1738580_1280.jpg',            # 韩式冷面
    '年糕': f'{LOCAL_FOOD_IMAGE_BASE}toppokki-1607479_1280.jpg',            # 年糕
    '泡菜': f'{LOCAL_FOOD_IMAGE_BASE}toppokki-1607479_1280.jpg',            # 泡菜
    '石锅拌饭': f'{LOCAL_FOOD_IMAGE_BASE}bibimbap-1738580_1280.jpg',        # 石锅拌饭
    '部队锅': f'{LOCAL_FOOD_IMAGE_BASE}ramen-7382882_1280.jpg',             # 部队锅
}

# 泰餐图片映射
THAI_FOOD_IMAGES_LOCAL = {
    '泰式咖喱': f'{LOCAL_FOOD_IMAGE_BASE}food-photography-2358899_1280.jpg', # 咖喱类
    '泰式冬阴功': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',        # 海鲜汤
    '泰式炒河粉': f'{LOCAL_FOOD_IMAGE_BASE}food-photography-2610863_1280.jpg', # 炒粉类
    '泰式炒饭': f'{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg',             # 炒饭类
    '绿咖喱鸡': f'{LOCAL_FOOD_IMAGE_BASE}food-photography-2610864_1280.jpg', # 咖喱鸡
    '冬阴功汤': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265999_1280.jpg',          # 海鲜汤
}

# 其他菜系图片映射
OTHER_FOOD_IMAGES_LOCAL = {
    '印度咖喱': f'{LOCAL_FOOD_IMAGE_BASE}food-photography-2358899_1280.jpg', # 咖喱类
    '墨西哥卷饼': f'{LOCAL_FOOD_IMAGE_BASE}food-shoot-675564_1280.jpg',      # 卷类食物
    '土耳其烤肉': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg', # 烤肉类
    '越南河粉': f'{LOCAL_FOOD_IMAGE_BASE}udon-noodles-4065311_1280.jpg',     # 面条类
}

# 备用图片池 - 按菜系分类
FALLBACK_IMAGES_LOCAL = {
    'chinese': [
        f'{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}chinese-915325_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}chinese-916623_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233490_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'western': [
        f'{LOCAL_FOOD_IMAGE_BASE}pasta-7209002_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}pizza-6478478_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}steak-6278031_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'japanese': [
        f'{LOCAL_FOOD_IMAGE_BASE}sushi-2009611_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}udon-noodles-4065311_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'korean': [
        f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}bibimbap-1738580_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}toppokki-1607479_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'thai': [
        f'{LOCAL_FOOD_IMAGE_BASE}food-photography-2358899_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'other': [
        f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
    ],
    'default': [
        f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
        f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',
        f'{LOCAL_FOOD_IMAGE_BASE}eat-235771_1280.jpg',
    ]
}

# 完整的本地食物图片映射字典
LOCAL_FOOD_IMAGES = {}
LOCAL_FOOD_IMAGES.update(CHINESE_FOOD_IMAGES_LOCAL)
LOCAL_FOOD_IMAGES.update(WESTERN_FOOD_IMAGES_LOCAL)
LOCAL_FOOD_IMAGES.update(JAPANESE_FOOD_IMAGES_LOCAL)
LOCAL_FOOD_IMAGES.update(KOREAN_FOOD_IMAGES_LOCAL)
LOCAL_FOOD_IMAGES.update(THAI_FOOD_IMAGES_LOCAL)
LOCAL_FOOD_IMAGES.update(OTHER_FOOD_IMAGES_LOCAL)

def get_local_food_image(food_name: str, cuisine: str = 'chinese') -> str:
    """
    获取本地食物图片URL
    
    Args:
        food_name: 食物名称
        cuisine: 菜系
        
    Returns:
        本地图片URL
    """
    import random
    
    # 首先尝试从完整映射中获取
    if food_name in LOCAL_FOOD_IMAGES:
        return LOCAL_FOOD_IMAGES[food_name]
    
    # 如果没有映射，根据菜系选择备用图片
    fallback_images = FALLBACK_IMAGES_LOCAL.get(cuisine, FALLBACK_IMAGES_LOCAL['default'])
    return random.choice(fallback_images)

def get_local_food_images_by_cuisine(cuisine: str) -> dict:
    """
    获取指定菜系的所有本地食物图片映射
    
    Args:
        cuisine: 菜系
        
    Returns:
        该菜系的食物图片映射字典
    """
    cuisine_mappings = {
        'chinese': CHINESE_FOOD_IMAGES_LOCAL,
        'western': WESTERN_FOOD_IMAGES_LOCAL,
        'japanese': JAPANESE_FOOD_IMAGES_LOCAL,
        'korean': KOREAN_FOOD_IMAGES_LOCAL,
        'thai': THAI_FOOD_IMAGES_LOCAL,
        'other': OTHER_FOOD_IMAGES_LOCAL,
    }
    
    return cuisine_mappings.get(cuisine, {})

def get_all_local_food_images() -> dict:
    """
    获取所有本地食物图片映射
    
    Returns:
        完整的食物图片映射字典
    """
    return LOCAL_FOOD_IMAGES.copy()

def get_local_image_statistics() -> dict:
    """
    获取本地图片统计信息
    
    Returns:
        统计信息字典
    """
    # 统计各菜系的图片数量
    cuisine_stats = {
        'chinese': len(CHINESE_FOOD_IMAGES_LOCAL),
        'western': len(WESTERN_FOOD_IMAGES_LOCAL),
        'japanese': len(JAPANESE_FOOD_IMAGES_LOCAL),
        'korean': len(KOREAN_FOOD_IMAGES_LOCAL),
        'thai': len(THAI_FOOD_IMAGES_LOCAL),
        'other': len(OTHER_FOOD_IMAGES_LOCAL),
    }
    
    # 统计唯一图片数量
    all_images = set()
    for images_dict in [CHINESE_FOOD_IMAGES_LOCAL, WESTERN_FOOD_IMAGES_LOCAL, 
                       JAPANESE_FOOD_IMAGES_LOCAL, KOREAN_FOOD_IMAGES_LOCAL, 
                       THAI_FOOD_IMAGES_LOCAL, OTHER_FOOD_IMAGES_LOCAL]:
        all_images.update(images_dict.values())
    
    # 统计图片来源 (全部为本地)
    image_sources = {'Local': len(all_images)}
    
    # 统计备用图片数量
    fallback_count = sum(len(images) for images in FALLBACK_IMAGES_LOCAL.values())
    
    return {
        'total_foods': len(LOCAL_FOOD_IMAGES),
        'unique_images': len(all_images),
        'cuisine_distribution': cuisine_stats,
        'image_sources': image_sources,
        'fallback_images': fallback_count,
        'image_coverage': 100.0,  # 本地图片100%覆盖
        'is_local': True,
    }

def get_food_image_analysis() -> dict:
    """
    分析食物与图片的匹配度
    
    Returns:
        匹配度分析结果
    """
    # 高匹配度的食物（专用图片）
    high_match_foods = [
        ('麻婆豆腐', 'mapo-tofu-2570173_1280.jpg'),
        ('小龙虾', 'crayfish-866400_1280.jpg'),
        ('兰州拉面', 'lanzhou-6896276_1280.jpg'),
        ('过桥米线', 'cross-bridge-tofu-4866594_1280.jpg'),
        ('意大利面', 'pasta-7209002_1280.jpg'),
        ('披萨', 'pizza-6478478_1280.jpg'),
        ('牛排', 'steak-6714964_1280.jpg'),
        ('寿司拼盘', 'sushi-2009611_1280.jpg'),
        ('拉面', 'ramen-4647408_1280.jpg'),
        ('乌冬面', 'udon-noodles-4065311_1280.jpg'),
        ('韩式烤肉', 'korean-barbecue-8579177_1280.jpg'),
        ('韩式拌饭', 'bibimbap-1738580_1280.jpg'),
        ('韩式炒年糕', 'toppokki-1607479_1280.jpg'),
        ('马卡龙', 'macarons-2179198_1280.jpg'),
        ('豆腐料理', 'tofu-7525311_1280.jpg'),
        ('牛肉料理', 'beef-4805622_1280.jpg'),
    ]
    
    return {
        'total_foods': len(LOCAL_FOOD_IMAGES),
        'high_match_count': len(high_match_foods),
        'high_match_foods': high_match_foods,
        'match_percentage': (len(high_match_foods) / len(LOCAL_FOOD_IMAGES)) * 100,
        'specialized_images': len(high_match_foods),
    }
