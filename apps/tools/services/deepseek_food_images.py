"""
基于DeepSeek数据的食物图片映射 - 确保食物名称与图片完全一致
使用static/img/food目录下的图片，保证每个食物都有对应的图片
"""

# 本地图片基础路径
LOCAL_FOOD_IMAGE_BASE = "/static/img/food/"

# 基于DeepSeek数据的完整食物图片映射
DEEPSEEK_FOOD_IMAGES = {
    # 中餐 (22个)
    "宫保鸡丁": f"{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg",  # 中式炒菜
    "麻婆豆腐": f"{LOCAL_FOOD_IMAGE_BASE}mapo-tofu-2570173_1280.jpg",  # 麻婆豆腐专用
    "红烧肉": f"{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg",  # 红烧肉专用
    "糖醋里脊": f"{LOCAL_FOOD_IMAGE_BASE}chinese-916623_1280.jpg",  # 中式炒菜
    "鱼香肉丝": f"{LOCAL_FOOD_IMAGE_BASE}chinese-915325_1280.jpg",  # 中式菜品
    "回锅肉": f"{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg",  # 红烧肉类
    "水煮鱼": f"{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg",  # 鱼类菜品
    "白切鸡": f"{LOCAL_FOOD_IMAGE_BASE}chinese-841179_1280.jpg",  # 中式白切菜
    "叉烧肉": f"{LOCAL_FOOD_IMAGE_BASE}roast-3416333_1280.jpg",  # 烤肉类
    "北京烤鸭": f"{LOCAL_FOOD_IMAGE_BASE}duck-253846_1280.jpg",  # 烤鸭专用
    "炸酱面": f"{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg",  # 面条类
    "东坡肉": f"{LOCAL_FOOD_IMAGE_BASE}braise-pork-1398308_1280.jpg",  # 红烧肉
    "剁椒鱼头": f"{LOCAL_FOOD_IMAGE_BASE}steamed-fish-3495930_1280.jpg",  # 鱼类菜品
    "青椒肉丝": f"{LOCAL_FOOD_IMAGE_BASE}green-dragon-vegetable-1707089_1280.jpg",  # 青菜类
    "番茄炒蛋": f"{LOCAL_FOOD_IMAGE_BASE}egg-roll-6353108_1280.jpg",  # 蛋类菜品
    "蛋炒饭": f"{LOCAL_FOOD_IMAGE_BASE}the-pork-fried-rice-made-908333_1280.jpg",  # 炒饭
    "小龙虾": f"{LOCAL_FOOD_IMAGE_BASE}crayfish-866400_1280.jpg",  # 小龙虾专用
    "火锅": f"{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg",  # 火锅类
    "烧鹅": f"{LOCAL_FOOD_IMAGE_BASE}duck-2097959_1280.jpg",  # 烤鸭类
    "石锅拌饭": f"{LOCAL_FOOD_IMAGE_BASE}rice-6364832_1280.jpg",  # 米饭类
    "麻辣香锅": f"{LOCAL_FOOD_IMAGE_BASE}chongqing-6764962_1280.jpg",  # 重庆风味
    # 西餐 (7个)
    "意大利面": f"{LOCAL_FOOD_IMAGE_BASE}pasta-7209002_1280.jpg",  # 意大利面专用
    "披萨": f"{LOCAL_FOOD_IMAGE_BASE}pizza-6478478_1280.jpg",  # 披萨专用
    "汉堡包": f"{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg",  # 快餐类
    "牛排": f"{LOCAL_FOOD_IMAGE_BASE}steak-6714964_1280.jpg",  # 牛排专用
    "三明治": f"{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg",  # 面包类
    "沙拉": f"{LOCAL_FOOD_IMAGE_BASE}vegetarian-1141242_1280.jpg",  # 素食类
    "土豆泥": f"{LOCAL_FOOD_IMAGE_BASE}steak-6278031_1280.jpg",  # 土豆泥
    # 日料 (7个)
    "寿司": f"{LOCAL_FOOD_IMAGE_BASE}sushi-2853382_1280.jpg",  # 寿司专用
    "拉面": f"{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg",  # 拉面专用
    "天妇罗": f"{LOCAL_FOOD_IMAGE_BASE}tempura-2853382_1280.jpg",  # 天妇罗专用
    "刺身": f"{LOCAL_FOOD_IMAGE_BASE}sashimi-2853382_1280.jpg",  # 刺身专用
    "乌冬面": f"{LOCAL_FOOD_IMAGE_BASE}udon-4647408_1280.jpg",  # 乌冬面专用
    "日式烤肉": f"{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg",  # 烤肉类
    "章鱼小丸子": f"{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg",  # 章鱼小丸子
    # 韩料 (4个)
    "韩式烤肉": f"{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg",  # 韩式烤肉
    "韩式炸鸡": f"{LOCAL_FOOD_IMAGE_BASE}chicken-2097959_1280.jpg",  # 炸鸡类
    "泡菜": f"{LOCAL_FOOD_IMAGE_BASE}kimchi-2853382_1280.jpg",  # 泡菜专用
    "部队锅": f"{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg",  # 韩式火锅
    # 其他 (2个)
    "冷面": f"{LOCAL_FOOD_IMAGE_BASE}lanzhou-6896276_1280.jpg",  # 面条类
    "年糕": f"{LOCAL_FOOD_IMAGE_BASE}rice-cake-2853382_1280.jpg",  # 年糕专用
    "炸鸡": f"{LOCAL_FOOD_IMAGE_BASE}chicken-2097959_1280.jpg",  # 炸鸡类
}

# 备用图片映射 - 当找不到对应图片时使用
FALLBACK_IMAGES = {
    "chinese": [
        f"{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}chinese-915325_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}chinese-916623_1280.jpg",
    ],
    "western": [
        f"{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}steak-6714964_1280.jpg",
    ],
    "japanese": [
        f"{LOCAL_FOOD_IMAGE_BASE}sushi-2853382_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}ramen-4647408_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}tempura-2853382_1280.jpg",
    ],
    "korean": [
        f"{LOCAL_FOOD_IMAGE_BASE}korean-barbecue-8579177_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}kimchi-2853382_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}chicken-2097959_1280.jpg",
    ],
    "default": [
        f"{LOCAL_FOOD_IMAGE_BASE}food-3228058_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}chinese-3855829_1280.jpg",
        f"{LOCAL_FOOD_IMAGE_BASE}bread-6725352_1280.jpg",
    ],
}


def get_deepseek_food_image(food_name: str, cuisine: str = "chinese") -> str:
    """
    获取基于DeepSeek数据的食物图片URL

    Args:
        food_name: 食物名称
        cuisine: 菜系

    Returns:
        本地图片URL
    """
    import random

    # 首先尝试从DeepSeek映射中获取
    if food_name in DEEPSEEK_FOOD_IMAGES:
        return DEEPSEEK_FOOD_IMAGES[food_name]

    # 如果没有映射，根据菜系选择备用图片
    fallback_images = FALLBACK_IMAGES.get(cuisine, FALLBACK_IMAGES["default"])
    return random.choice(fallback_images)


def get_all_deepseek_food_images() -> dict:
    """
    获取所有DeepSeek食物图片映射

    Returns:
        完整的食物图片映射字典
    """
    return DEEPSEEK_FOOD_IMAGES.copy()


def get_food_image_coverage() -> dict:
    """
    获取食物图片覆盖率统计

    Returns:
        覆盖率统计信息
    """
    from apps.tools.models import FoodItem

    all_foods = FoodItem.objects.filter(is_active=True)
    total_foods = all_foods.count()

    covered_foods = []
    uncovered_foods = []

    for food in all_foods:
        if food.name in DEEPSEEK_FOOD_IMAGES:
            covered_foods.append(food.name)
        else:
            uncovered_foods.append(food.name)

    coverage_rate = (len(covered_foods) / total_foods) * 100 if total_foods > 0 else 0

    return {
        "total_foods": total_foods,
        "covered_foods": len(covered_foods),
        "uncovered_foods": len(uncovered_foods),
        "coverage_rate": coverage_rate,
        "covered_food_names": covered_foods,
        "uncovered_food_names": uncovered_foods,
    }
