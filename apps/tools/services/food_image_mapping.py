"""
食品图片映射服务
提供准确的食品名称到图片路径的映射，支持图像识别功能
"""

# 基础图片路径
LOCAL_FOOD_IMAGE_BASE = '/static/img/food/'

# 准确的食品图片映射
ACCURATE_FOOD_IMAGES = {
    # 早餐类
    '豆浆油条': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '煎蛋三明治': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',
    '燕麦粥': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '包子豆浆': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '牛奶麦片': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '煎饼果子': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '小笼包': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '法式吐司': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',
    '蒸蛋羹': f'{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg',
    '煎饺': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '蒸饺': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '烧卖': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '肠粉': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '糯米鸡': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '粽子': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '油条': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '豆浆': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '豆腐脑': f'{LOCAL_FOOD_IMAGE_BASE}tofu-7525311_1280.jpg',
    '胡辣汤': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
    '包子': f'{LOCAL_FOOD_IMAGE_BASE}chinese-5233510_1280.jpg',
    '馒头': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '花卷': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '咸鸭蛋': f'{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg',
    '茶叶蛋': f'{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg',
    
    # 午餐类 - 中式
    '宫保鸡丁': f'{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg',
    '麻婆豆腐': f'{LOCAL_FOOD_IMAGE_BASE}mapo-tofu-2570173_1280.jpg',
    '番茄炒蛋': f'{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg',
    '青椒肉丝': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '鱼香肉丝': f'{LOCAL_FOOD_IMAGE_BASE}chinese-915325_1280.jpg',
    '回锅肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '白切鸡': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
    '叉烧肉': f'{LOCAL_FOOD_IMAGE_BASE}roast-3416333_1280.jpg',
    '炸酱面': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',
    '蛋炒饭': f'{LOCAL_FOOD_IMAGE_BASE}the-pork-fried-rice-made-908333_1280.jpg',
    '糖醋排骨': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '蒜蓉炒青菜': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '酸菜鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '红烧茄子': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '干煸豆角': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '糖醋里脊': f'{LOCAL_FOOD_IMAGE_BASE}chinese-916623_1280.jpg',
    '红烧狮子头': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '清炒时蔬': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '蒜蓉粉丝蒸扇贝': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',
    '白灼虾': f'{LOCAL_FOOD_IMAGE_BASE}shrimp-6902940_1280.jpg',
    '清蒸鲈鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '红烧带鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '糖醋鲤鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '清炒豆芽': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '蒜蓉西兰花': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '红烧牛腩': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '清炖羊肉': f'{LOCAL_FOOD_IMAGE_BASE}beef-4805622_1280.jpg',
    '烧鹅': f'{LOCAL_FOOD_IMAGE_BASE}duck-2097959_1280.jpg',
    '烤鸭': f'{LOCAL_FOOD_IMAGE_BASE}duck-253846_1280.jpg',
    '清蒸石斑鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '红烧海参': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',
    '蒜蓉蒸扇贝': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265995_1280.jpg',
    '白灼基围虾': f'{LOCAL_FOOD_IMAGE_BASE}shrimp-6902940_1280.jpg',
    '清蒸大闸蟹': f'{LOCAL_FOOD_IMAGE_BASE}seafood-4265999_1280.jpg',
    
    # 午餐类 - 西式
    '意大利面': f'{LOCAL_FOOD_IMAGE_BASE}pasta-7209002_1280.jpg',
    '三明治': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',
    '沙拉': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '汉堡包': f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',
    '披萨': f'{LOCAL_FOOD_IMAGE_BASE}pizza-6478478_1280.jpg',
    '鸡肉沙拉': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '意式烩饭': f'{LOCAL_FOOD_IMAGE_BASE}pasta-7209002_1280.jpg',
    '墨西哥卷饼': f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',
    '希腊沙拉': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '法式洋葱汤': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '牛排': f'{LOCAL_FOOD_IMAGE_BASE}steak-6714964_1280.jpg',
    '烤鸡': f'{LOCAL_FOOD_IMAGE_BASE}chicken-2097959_1280.jpg',
    '烤鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '烤虾': f'{LOCAL_FOOD_IMAGE_BASE}shrimp-6902940_1280.jpg',
    '烤蔬菜': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '土豆泥': f'{LOCAL_FOOD_IMAGE_BASE}steak-6278031_1280.jpg',
    '奶油汤': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '蔬菜汤': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    
    # 晚餐类
    '红烧肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '水煮鱼': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '北京烤鸭': f'{LOCAL_FOOD_IMAGE_BASE}duck-253846_1280.jpg',
    '东坡肉': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    '剁椒鱼头': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '咖喱鸡': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
    '红酒炖牛肉': f'{LOCAL_FOOD_IMAGE_BASE}steak-6714964_1280.jpg',
    '泰式冬阴功': f'{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg',
    '日式照烧鸡': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
    
    # 夜宵类
    '小龙虾': f'{LOCAL_FOOD_IMAGE_BASE}crayfish-866400_1280.jpg',
    '火锅': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',
    '烧烤': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg',
    '烤串': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg',
    '麻辣烫': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',
    '炸鸡翅': f'{LOCAL_FOOD_IMAGE_BASE}chicken-2097959_1280.jpg',
    '关东煮': f'{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg',
    '烤冷面': f'{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg',
    '烤红薯': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '糖炒栗子': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '爆米花': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '烤玉米': f'{LOCAL_FOOD_IMAGE_BASE}food-5983402_1280.jpg',
    '烤茄子': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '烤韭菜': f'{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg',
    '烤金针菇': f'{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg',
    '烤豆腐': f'{LOCAL_FOOD_IMAGE_BASE}tofu-7525311_1280.jpg',
    '烤馒头': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    '烤面包片': f'{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg',
}

# 备用图片映射（当找不到精确匹配时使用）
FALLBACK_IMAGES = {
    'chinese': f'{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg',
    'western': f'{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg',
    'asian': f'{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg',
    'breakfast': f'{LOCAL_FOOD_IMAGE_BASE}bread-1836411_1280.jpg',
    'lunch': f'{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg',
    'dinner': f'{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg',
    'snack': f'{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg',
    'default': f'{LOCAL_FOOD_IMAGE_BASE}default-food.svg',
}

# 图像识别关键词映射
IMAGE_RECOGNITION_KEYWORDS = {
    # 早餐关键词
    '豆浆': ['豆浆', '豆奶', 'soy milk', '豆浆油条'],
    '油条': ['油条', '油炸鬼', 'fried bread stick'],
    '包子': ['包子', 'baozi', 'steamed bun'],
    '馒头': ['馒头', 'mantou', 'steamed bread'],
    '面包': ['面包', 'bread', '吐司', 'toast'],
    '鸡蛋': ['鸡蛋', '蛋', 'egg', '煎蛋', '炒蛋'],
    '粥': ['粥', 'porridge', '燕麦粥', '白粥'],
    
    # 午餐关键词
    '米饭': ['米饭', 'rice', '炒饭', '蛋炒饭'],
    '面条': ['面条', 'noodles', '拉面', '炸酱面'],
    '鸡肉': ['鸡肉', 'chicken', '鸡胸肉', '鸡腿'],
    '猪肉': ['猪肉', 'pork', '五花肉', '里脊'],
    '牛肉': ['牛肉', 'beef', '牛排', '牛腩'],
    '鱼': ['鱼', 'fish', '鲈鱼', '带鱼', '鲤鱼'],
    '虾': ['虾', 'shrimp', '基围虾', '白灼虾'],
    '豆腐': ['豆腐', 'tofu', '麻婆豆腐'],
    '蔬菜': ['蔬菜', 'vegetables', '青菜', '西兰花'],
    
    # 晚餐关键词
    '火锅': ['火锅', 'hot pot', '麻辣烫'],
    '烧烤': ['烧烤', 'bbq', '烤串', '烤肉'],
    '小龙虾': ['小龙虾', 'crayfish', '龙虾'],
    '烤鸭': ['烤鸭', 'roast duck', '北京烤鸭'],
    '红烧肉': ['红烧肉', 'braised pork', '东坡肉'],
    
    # 西式关键词
    'pizza': ['pizza', '披萨', '意大利披萨'],
    'pasta': ['pasta', '意大利面', '意面'],
    'burger': ['burger', '汉堡', '汉堡包'],
    'salad': ['salad', '沙拉', '蔬菜沙拉'],
    'steak': ['steak', '牛排', '煎牛排'],
    
    # 日式关键词
    'sushi': ['sushi', '寿司', '日本寿司'],
    'ramen': ['ramen', '拉面', '日本拉面'],
    'tempura': ['tempura', '天妇罗'],
    
    # 韩式关键词
    'bibimbap': ['bibimbap', '石锅拌饭', '韩式拌饭'],
    'kimchi': ['kimchi', '泡菜', '韩国泡菜'],
    'bbq': ['bbq', '韩式烤肉', '烤肉'],
}

def get_food_image(food_name, cuisine=None, meal_type=None):
    """
    获取食品图片路径
    
    Args:
        food_name: 食品名称
        cuisine: 菜系
        meal_type: 餐点类型
    
    Returns:
        str: 图片路径
    """
    # 精确匹配
    if food_name in ACCURATE_FOOD_IMAGES:
        return ACCURATE_FOOD_IMAGES[food_name]
    
    # 模糊匹配
    for key, value in ACCURATE_FOOD_IMAGES.items():
        if food_name in key or key in food_name:
            return value
    
    # 按菜系匹配
    if cuisine and cuisine in FALLBACK_IMAGES:
        return FALLBACK_IMAGES[cuisine]
    
    # 按餐点类型匹配
    if meal_type and meal_type in FALLBACK_IMAGES:
        return FALLBACK_IMAGES[meal_type]
    
    # 默认图片
    return FALLBACK_IMAGES['default']

def recognize_food_from_image(image_path, confidence_threshold=0.7):
    """
    从图片识别食品（模拟图像识别功能）
    
    Args:
        image_path: 图片路径
        confidence_threshold: 置信度阈值
    
    Returns:
        dict: 识别结果 {'food_name': '食品名称', 'confidence': 0.8, 'alternatives': []}
    """
    # 这里可以集成真实的图像识别API，如Google Vision API、Azure Computer Vision等
    # 目前返回模拟结果
    
    import random
    import os
    
    # 基于文件名或路径进行简单的识别
    filename = os.path.basename(image_path).lower()
    
    # 根据文件名特征进行识别
    food_mapping = {
        'chicken': ('宫保鸡丁', 0.95),
        'pork': ('红烧肉', 0.92),
        'beef': ('牛排', 0.89),
        'fish': ('水煮鱼', 0.87),
        'noodle': ('炸酱面', 0.85),
        'rice': ('蛋炒饭', 0.83),
        'bread': ('三明治', 0.81),
        'pizza': ('披萨', 0.79),
        'pasta': ('意大利面', 0.77),
        'salad': ('沙拉', 0.75),
        'tofu': ('麻婆豆腐', 0.73),
        'duck': ('北京烤鸭', 0.71),
        'shrimp': ('小龙虾', 0.69),
        'hotpot': ('火锅', 0.67),
        'bbq': ('烧烤', 0.65),
    }
    
    # 尝试根据文件名匹配
    for key, (food_name, confidence) in food_mapping.items():
        if key in filename:
            # 生成替代选项
            alternatives = []
            all_foods = [
                ('宫保鸡丁', 0.95), ('麻婆豆腐', 0.92), ('红烧肉', 0.89),
                ('番茄炒蛋', 0.87), ('鱼香肉丝', 0.85), ('回锅肉', 0.83),
                ('白切鸡', 0.81), ('叉烧肉', 0.79), ('炸酱面', 0.77),
                ('蛋炒饭', 0.75), ('意大利面', 0.73), ('披萨', 0.71),
                ('汉堡包', 0.69), ('沙拉', 0.67), ('牛排', 0.65),
                ('小龙虾', 0.63), ('火锅', 0.61), ('烧烤', 0.59)
            ]
            
            for alt_food, alt_conf in all_foods:
                if alt_food != food_name and alt_conf >= confidence_threshold * 0.8:
                    alternatives.append({'name': alt_food, 'confidence': alt_conf})
            
            return {
                'food_name': food_name,
                'confidence': confidence,
                'alternatives': alternatives[:3]
            }
    
    # 如果没有匹配，随机选择一个结果
    possible_foods = [
        ('宫保鸡丁', 0.95), ('麻婆豆腐', 0.92), ('红烧肉', 0.89),
        ('番茄炒蛋', 0.87), ('鱼香肉丝', 0.85), ('回锅肉', 0.83),
        ('白切鸡', 0.81), ('叉烧肉', 0.79), ('炸酱面', 0.77),
        ('蛋炒饭', 0.75), ('意大利面', 0.73), ('披萨', 0.71),
        ('汉堡包', 0.69), ('沙拉', 0.67), ('牛排', 0.65),
        ('小龙虾', 0.63), ('火锅', 0.61), ('烧烤', 0.59)
    ]
    
    food_name, confidence = random.choice(possible_foods)
    
    if confidence >= confidence_threshold:
        # 生成替代选项
        alternatives = []
        for alt_food, alt_conf in possible_foods:
            if alt_food != food_name and alt_conf >= confidence_threshold * 0.8:
                alternatives.append({'name': alt_food, 'confidence': alt_conf})
        
        return {
            'food_name': food_name,
            'confidence': confidence,
            'alternatives': alternatives[:3]  # 最多3个替代选项
        }
    
    return {
        'food_name': '未知食品',
        'confidence': 0.0,
        'alternatives': []
    }

def get_food_suggestions_by_image(image_path):
    """
    根据图片获取食品建议
    
    Args:
        image_path: 图片路径
    
    Returns:
        list: 建议的食品列表
    """
    # 模拟图像识别
    recognition_result = recognize_food_from_image(image_path)
    
    if recognition_result['confidence'] > 0.7:
        # 基于识别结果推荐相似食品
        base_food = recognition_result['food_name']
        
        # 根据基础食品推荐相似食品
        similar_foods = {
            '宫保鸡丁': ['鱼香肉丝', '回锅肉', '青椒肉丝', '糖醋里脊'],
            '麻婆豆腐': ['红烧茄子', '干煸豆角', '蒜蓉炒青菜'],
            '红烧肉': ['东坡肉', '叉烧肉', '糖醋排骨', '红烧牛腩'],
            '番茄炒蛋': ['青椒肉丝', '蒜蓉炒青菜', '干煸豆角'],
            '鱼香肉丝': ['宫保鸡丁', '回锅肉', '青椒肉丝'],
            '回锅肉': ['宫保鸡丁', '鱼香肉丝', '红烧肉'],
            '白切鸡': ['叉烧肉', '烧鹅', '烤鸭'],
            '叉烧肉': ['白切鸡', '烧鹅', '烤鸭'],
            '炸酱面': ['蛋炒饭', '意大利面', '拉面'],
            '蛋炒饭': ['炸酱面', '意大利面', '炒饭'],
            '意大利面': ['炸酱面', '蛋炒饭', '披萨'],
            '披萨': ['意大利面', '汉堡包', '三明治'],
            '汉堡包': ['披萨', '三明治', '墨西哥卷饼'],
            '沙拉': ['希腊沙拉', '鸡肉沙拉', '蔬菜汤'],
            '牛排': ['烤鸡', '烤鱼', '红酒炖牛肉'],
            '小龙虾': ['火锅', '烧烤', '麻辣烫'],
            '火锅': ['小龙虾', '烧烤', '麻辣烫'],
            '烧烤': ['小龙虾', '火锅', '麻辣烫'],
            '三明治': ['汉堡包', '披萨', '意大利面'],
            '水煮鱼': ['清蒸鲈鱼', '红烧带鱼', '糖醋鲤鱼'],
            '北京烤鸭': ['白切鸡', '叉烧肉', '烧鹅'],
        }
        
        suggestions = similar_foods.get(base_food, [])
        
        # 如果建议为空，返回一些通用建议
        if not suggestions:
            suggestions = ['宫保鸡丁', '麻婆豆腐', '红烧肉', '番茄炒蛋']
        
        return suggestions
    
    # 如果置信度不够，返回一些通用建议
    return ['宫保鸡丁', '麻婆豆腐', '红烧肉', '番茄炒蛋', '鱼香肉丝', '回锅肉']

def update_food_images_in_database():
    """
    更新数据库中的食品图片路径
    """
    from apps.tools.models import FoodItem
    
    updated_count = 0
    not_found_count = 0
    
    for food in FoodItem.objects.all():
        new_image_url = get_food_image(food.name, food.cuisine, food.meal_types[0] if food.meal_types else None)
        
        if new_image_url != food.image_url:
            food.image_url = new_image_url
            food.save()
            updated_count += 1
        else:
            not_found_count += 1
    
    return {
        'updated': updated_count,
        'not_found': not_found_count,
        'total': FoodItem.objects.count()
    }

def get_image_coverage_stats():
    """
    获取图片覆盖率统计
    """
    from apps.tools.models import FoodItem
    
    total_foods = FoodItem.objects.count()
    foods_with_images = FoodItem.objects.exclude(image_url='').count()
    foods_with_accurate_images = 0
    
    for food in FoodItem.objects.all():
        if food.name in ACCURATE_FOOD_IMAGES:
            foods_with_accurate_images += 1
    
    return {
        'total_foods': total_foods,
        'foods_with_images': foods_with_images,
        'foods_with_accurate_images': foods_with_accurate_images,
        'image_coverage': round(foods_with_images / total_foods * 100, 2) if total_foods > 0 else 0,
        'accurate_coverage': round(foods_with_accurate_images / total_foods * 100, 2) if total_foods > 0 else 0
    }
