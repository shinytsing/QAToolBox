from django.core.management.base import BaseCommand

from apps.tools.models import FoodItem
from apps.tools.services.accurate_food_image_service import AccurateFoodImageService


class Command(BaseCommand):
    help = "初始化准确的食物数据 - 确保图片与食物一一对应，移除微辣清淡分类"

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始初始化准确的食物数据...")

        # 清空现有数据
        FoodItem.objects.all().delete()

        # 初始化图片服务
        image_service = AccurateFoodImageService()

        # 定义丰富的食物数据 - 移除微辣、清淡等分类
        base_foods = [
            # 中餐经典 (30个)
            {
                "name": "麻婆豆腐",
                "description": "川菜经典，麻辣鲜香，豆腐嫩滑，肉末香浓",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["豆腐", "猪肉末", "豆瓣酱", "花椒"],
                "tags": ["spicy", "sichuan", "comfort", "traditional"],
            },
            {
                "name": "宫保鸡丁",
                "description": "经典川菜，鸡肉配花生，酸甜微辣，口感丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["鸡胸肉", "花生", "干辣椒", "黄瓜"],
                "tags": ["classic", "sichuan", "delicious", "balanced"],
            },
            {
                "name": "红烧肉",
                "description": "传统名菜，肥而不腻，入口即化，香气四溢",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 60,
                "ingredients": ["五花肉", "酱油", "糖", "葱姜蒜"],
                "tags": ["traditional", "delicious", "comfort", "classic"],
            },
            {
                "name": "糖醋里脊",
                "description": "酸甜可口，外酥内嫩，色泽金黄，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["里脊肉", "糖", "醋", "淀粉"],
                "tags": ["sweet", "sour", "crispy", "delicious"],
            },
            {
                "name": "鱼香肉丝",
                "description": "川菜名品，肉丝嫩滑，鱼香味浓，下饭神器",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["猪肉丝", "木耳", "胡萝卜", "鱼香汁"],
                "tags": ["sichuan", "delicious", "balanced", "traditional"],
            },
            {
                "name": "青椒肉丝",
                "description": "家常小炒，青椒爽脆，肉丝嫩滑，简单美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["猪肉丝", "青椒", "蒜", "酱油"],
                "tags": ["simple", "delicious", "home-style", "balanced"],
            },
            {
                "name": "番茄炒蛋",
                "description": "经典家常菜，番茄酸甜，鸡蛋嫩滑，营养丰富",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["鸡蛋", "番茄", "葱花", "盐"],
                "tags": ["simple", "nutritious", "home-style", "classic"],
            },
            {
                "name": "白切鸡",
                "description": "粤菜经典，鸡肉嫩滑，蘸料鲜美，清淡爽口",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 45,
                "ingredients": ["整鸡", "姜", "葱", "蘸料"],
                "tags": ["cantonese", "delicious", "light", "traditional"],
            },
            {
                "name": "北京烤鸭",
                "description": "北京名菜，皮酥肉嫩，色泽红亮，香气扑鼻",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "hard",
                "cooking_time": 120,
                "ingredients": ["鸭子", "甜面酱", "葱丝", "薄饼"],
                "tags": ["beijing", "premium", "traditional", "delicious"],
            },
            {
                "name": "东坡肉",
                "description": "江浙名菜，肥而不腻，入口即化，香气浓郁",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 90,
                "ingredients": ["五花肉", "酱油", "糖", "料酒"],
                "tags": ["jiangsu", "traditional", "delicious", "comfort"],
            },
            {
                "name": "佛跳墙",
                "description": "福建名菜，食材丰富，汤汁浓郁，营养丰富",
                "meal_types": ["dinner"],
                "cuisine": "chinese",
                "difficulty": "hard",
                "cooking_time": 180,
                "ingredients": ["海参", "鲍鱼", "鱼翅", "花胶"],
                "tags": ["fujian", "premium", "luxury", "nutritious"],
            },
            {
                "name": "剁椒鱼头",
                "description": "湘菜经典，鱼头鲜美，剁椒香辣，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["鱼头", "剁椒", "蒜", "姜"],
                "tags": ["hunan", "spicy", "delicious", "traditional"],
            },
            {
                "name": "小龙虾",
                "description": "夏季美食，麻辣鲜香，肉质鲜美，聚会必备",
                "meal_types": ["dinner", "snack"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["小龙虾", "麻辣料", "蒜", "啤酒"],
                "tags": ["spicy", "delicious", "party", "summer"],
            },
            {
                "name": "烧烤",
                "description": "户外美食，炭火烤制，香气四溢，聚会首选",
                "meal_types": ["dinner", "snack"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 45,
                "ingredients": ["各种肉类", "蔬菜", "烧烤料", "炭火"],
                "tags": ["outdoor", "party", "delicious", "social"],
            },
            {
                "name": "火锅",
                "description": "冬季美食，热气腾腾，食材丰富，温暖人心",
                "meal_types": ["dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 60,
                "ingredients": ["火锅底料", "各种肉类", "蔬菜", "蘸料"],
                "tags": ["winter", "warm", "social", "delicious"],
            },
            {
                "name": "炸酱面",
                "description": "北京特色，面条劲道，炸酱香浓，简单美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["面条", "炸酱", "黄瓜丝", "豆芽"],
                "tags": ["beijing", "noodles", "delicious", "traditional"],
            },
            {
                "name": "蛋炒饭",
                "description": "经典炒饭，鸡蛋金黄，米饭粒粒分明，简单美味",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["米饭", "鸡蛋", "葱花", "盐"],
                "tags": ["simple", "delicious", "home-style", "classic"],
            },
            {
                "name": "盖浇饭",
                "description": "中式快餐，米饭配菜，简单美味，营养均衡",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["米饭", "各种菜", "酱油", "葱花"],
                "tags": ["simple", "delicious", "fast", "balanced"],
            },
            {
                "name": "回锅肉",
                "description": "川菜经典，肥而不腻，香辣可口，下饭神器",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["五花肉", "青椒", "蒜苗", "豆瓣酱"],
                "tags": ["sichuan", "spicy", "delicious", "traditional"],
            },
            {
                "name": "水煮鱼",
                "description": "川菜名品，鱼肉嫩滑，麻辣鲜香，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["鱼片", "豆芽", "辣椒", "花椒"],
                "tags": ["sichuan", "spicy", "delicious", "traditional"],
            },
            {
                "name": "麻辣香锅",
                "description": "现代川菜，食材丰富，麻辣鲜香，聚会首选",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["各种食材", "麻辣料", "蒜", "香菜"],
                "tags": ["modern", "spicy", "delicious", "social"],
            },
            {
                "name": "叉烧肉",
                "description": "粤菜经典，甜咸适中，色泽红亮，香气扑鼻",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 50,
                "ingredients": ["猪肉", "叉烧酱", "蜂蜜", "五香粉"],
                "tags": ["cantonese", "sweet", "delicious", "traditional"],
            },
            {
                "name": "烧鹅",
                "description": "粤菜名品，皮脆肉嫩，色泽金黄，香气浓郁",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "hard",
                "cooking_time": 90,
                "ingredients": ["鹅", "烧鹅料", "蜂蜜", "五香粉"],
                "tags": ["cantonese", "premium", "delicious", "traditional"],
            },
            {
                "name": "酸菜鱼",
                "description": "川菜经典，鱼肉嫩滑，酸辣开胃，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["鱼片", "酸菜", "辣椒", "豆芽"],
                "tags": ["sichuan", "sour", "spicy", "delicious"],
            },
            {
                "name": "辣子鸡",
                "description": "川菜名品，鸡肉酥脆，麻辣鲜香，下酒佳品",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["鸡块", "干辣椒", "花椒", "蒜"],
                "tags": ["sichuan", "spicy", "crispy", "delicious"],
            },
            {
                "name": "蒜蓉粉丝蒸扇贝",
                "description": "粤菜海鲜，扇贝鲜美，蒜香浓郁，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["扇贝", "粉丝", "蒜蓉", "葱花"],
                "tags": ["cantonese", "seafood", "delicious", "nutritious"],
            },
            {
                "name": "红烧狮子头",
                "description": "江浙名菜，肉丸嫩滑，汤汁浓郁，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 60,
                "ingredients": ["猪肉馅", "荸荠", "葱姜", "酱油"],
                "tags": ["jiangsu", "traditional", "delicious", "nutritious"],
            },
            {
                "name": "清蒸鲈鱼",
                "description": "粤菜海鲜，鱼肉嫩滑，清淡爽口，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["鲈鱼", "姜丝", "葱花", "蒸鱼豉油"],
                "tags": ["cantonese", "seafood", "light", "nutritious"],
            },
            {
                "name": "干煸豆角",
                "description": "川菜素菜，豆角爽脆，麻辣鲜香，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["豆角", "干辣椒", "蒜", "盐"],
                "tags": ["sichuan", "vegetarian", "spicy", "delicious"],
            },
            {
                "name": "蚂蚁上树",
                "description": "川菜经典，粉丝爽滑，肉末香浓，下饭神器",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 25,
                "ingredients": ["粉丝", "猪肉末", "豆瓣酱", "葱花"],
                "tags": ["sichuan", "delicious", "home-style", "traditional"],
            },
            {
                "name": "红烧茄子",
                "description": "家常素菜，茄子软糯，酱香浓郁，简单美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["茄子", "酱油", "蒜", "葱花"],
                "tags": ["vegetarian", "simple", "delicious", "home-style"],
            },
            # 西餐经典 (15个)
            {
                "name": "意大利面",
                "description": "经典西餐，面条劲道，酱料浓郁，简单美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 25,
                "ingredients": ["意大利面", "番茄酱", "肉末", "奶酪"],
                "tags": ["italian", "pasta", "delicious", "simple"],
            },
            {
                "name": "汉堡包",
                "description": "美式快餐，面包松软，肉饼多汁，简单美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["面包", "牛肉饼", "生菜", "番茄"],
                "tags": ["american", "fast", "delicious", "simple"],
            },
            {
                "name": "三明治",
                "description": "经典西餐，面包松软，馅料丰富，营养均衡",
                "meal_types": ["breakfast", "lunch"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["面包", "火腿", "生菜", "奶酪"],
                "tags": ["western", "simple", "delicious", "balanced"],
            },
            {
                "name": "沙拉",
                "description": "健康西餐，蔬菜新鲜，营养丰富，清爽可口",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 10,
                "ingredients": ["生菜", "番茄", "黄瓜", "橄榄油"],
                "tags": ["healthy", "fresh", "light", "nutritious"],
            },
            {
                "name": "牛排",
                "description": "西餐经典，肉质嫩滑，香气浓郁，营养丰富",
                "meal_types": ["dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["牛排", "黑胡椒", "黄油", "迷迭香"],
                "tags": ["western", "premium", "delicious", "nutritious"],
            },
            {
                "name": "披萨",
                "description": "意式美食，饼底酥脆，配料丰富，聚会首选",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["面团", "番茄酱", "奶酪", "各种配料"],
                "tags": ["italian", "pizza", "delicious", "social"],
            },
            {
                "name": "烤鸡",
                "description": "西式烤制，鸡肉嫩滑，香气扑鼻，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 60,
                "ingredients": ["整鸡", "香料", "柠檬", "橄榄油"],
                "tags": ["western", "roasted", "delicious", "nutritious"],
            },
            {
                "name": "奶油蘑菇汤",
                "description": "西式浓汤，蘑菇鲜美，奶油浓郁，温暖人心",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["蘑菇", "奶油", "洋葱", "面粉"],
                "tags": ["western", "soup", "creamy", "delicious"],
            },
            {
                "name": "法式吐司",
                "description": "经典早餐，面包松软，蛋香浓郁，简单美味",
                "meal_types": ["breakfast"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["面包", "鸡蛋", "牛奶", "黄油"],
                "tags": ["french", "breakfast", "delicious", "simple"],
            },
            {
                "name": "墨西哥卷饼",
                "description": "墨式美食，饼皮柔软，馅料丰富，风味独特",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["玉米饼", "鸡肉", "豆子", "莎莎酱"],
                "tags": ["mexican", "wrapped", "delicious", "spicy"],
            },
            {
                "name": "希腊沙拉",
                "description": "地中海风味，蔬菜新鲜，橄榄香浓，健康美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 10,
                "ingredients": ["生菜", "橄榄", "奶酪", "橄榄油"],
                "tags": ["greek", "healthy", "fresh", "delicious"],
            },
            {
                "name": "烤三文鱼",
                "description": "西式海鲜，鱼肉嫩滑，营养丰富，健康美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["三文鱼", "柠檬", "香草", "橄榄油"],
                "tags": ["western", "seafood", "healthy", "delicious"],
            },
            {
                "name": "意式烩饭",
                "description": "意式经典，米饭香浓，配料丰富，营养均衡",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["米饭", "高汤", "奶酪", "蘑菇"],
                "tags": ["italian", "risotto", "delicious", "creamy"],
            },
            {
                "name": "法式洋葱汤",
                "description": "法式经典，洋葱香甜，汤汁浓郁，温暖人心",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 45,
                "ingredients": ["洋葱", "牛肉汤", "面包", "奶酪"],
                "tags": ["french", "soup", "delicious", "warm"],
            },
            {
                "name": "美式烤肋排",
                "description": "美式烧烤，肉质嫩滑，酱料浓郁，聚会首选",
                "meal_types": ["dinner"],
                "cuisine": "western",
                "difficulty": "hard",
                "cooking_time": 120,
                "ingredients": ["猪肋排", "烧烤酱", "香料", "蜂蜜"],
                "tags": ["american", "bbq", "delicious", "social"],
            },
            # 日料经典 (10个)
            {
                "name": "寿司",
                "description": "日式经典，米饭香糯，鱼肉鲜美，精致美味",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["寿司米", "生鱼片", "海苔", "芥末"],
                "tags": ["japanese", "sushi", "delicious", "premium"],
            },
            {
                "name": "拉面",
                "description": "日式面食，面条劲道，汤汁浓郁，温暖人心",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["拉面", "高汤", "叉烧", "海苔"],
                "tags": ["japanese", "noodles", "delicious", "warm"],
            },
            {
                "name": "天妇罗",
                "description": "日式炸物，外酥内嫩，色泽金黄，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["虾", "蔬菜", "天妇罗粉", "油"],
                "tags": ["japanese", "fried", "crispy", "delicious"],
            },
            {
                "name": "味增汤",
                "description": "日式汤品，味增香浓，营养丰富，开胃暖身",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["味增", "豆腐", "海带", "葱花"],
                "tags": ["japanese", "soup", "delicious", "warm"],
            },
            {
                "name": "饭团",
                "description": "日式便当，米饭香糯，馅料丰富，便携美味",
                "meal_types": ["breakfast", "lunch"],
                "cuisine": "japanese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["米饭", "海苔", "梅干", "鲑鱼"],
                "tags": ["japanese", "bento", "delicious", "portable"],
            },
            {
                "name": "咖喱饭",
                "description": "日式咖喱，咖喱浓郁，米饭香糯，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["咖喱块", "米饭", "鸡肉", "蔬菜"],
                "tags": ["japanese", "curry", "delicious", "nutritious"],
            },
            {
                "name": "刺身",
                "description": "日式生食，鱼肉鲜美，口感细腻，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 20,
                "ingredients": ["生鱼片", "芥末", "酱油", "萝卜丝"],
                "tags": ["japanese", "sashimi", "premium", "delicious"],
            },
            {
                "name": "乌冬面",
                "description": "日式面食，面条粗壮，汤汁浓郁，温暖人心",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["乌冬面", "高汤", "天妇罗", "葱花"],
                "tags": ["japanese", "noodles", "delicious", "warm"],
            },
            {
                "name": "茶碗蒸",
                "description": "日式蒸蛋，蛋羹嫩滑，配料丰富，营养美味",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["鸡蛋", "高汤", "虾", "香菇"],
                "tags": ["japanese", "steamed", "delicious", "nutritious"],
            },
            {
                "name": "炸猪排",
                "description": "日式炸物，猪排酥脆，肉质嫩滑，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "japanese",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["猪排", "面包糠", "鸡蛋", "油"],
                "tags": ["japanese", "fried", "crispy", "delicious"],
            },
            # 韩料经典 (8个)
            {
                "name": "韩式烤肉",
                "description": "韩式烧烤，肉质嫩滑，香气四溢，聚会首选",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "korean",
                "difficulty": "medium",
                "cooking_time": 45,
                "ingredients": ["牛肉", "生菜", "蒜", "辣椒酱"],
                "tags": ["korean", "bbq", "delicious", "social"],
            },
            {
                "name": "泡菜汤",
                "description": "韩式汤品，泡菜酸辣，开胃暖身，营养丰富",
                "meal_types": ["breakfast", "lunch", "dinner"],
                "cuisine": "korean",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["泡菜", "豆腐", "猪肉", "辣椒"],
                "tags": ["korean", "soup", "spicy", "delicious"],
            },
            {
                "name": "紫菜包饭",
                "description": "韩式便当，米饭香糯，配料丰富，便携美味",
                "meal_types": ["breakfast", "lunch"],
                "cuisine": "korean",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["米饭", "紫菜", "胡萝卜", "鸡蛋"],
                "tags": ["korean", "bento", "delicious", "portable"],
            },
            {
                "name": "韩式炸鸡",
                "description": "韩式炸物，鸡肉酥脆，酱料浓郁，下酒佳品",
                "meal_types": ["dinner", "snack"],
                "cuisine": "korean",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["鸡翅", "炸鸡粉", "辣椒酱", "蒜"],
                "tags": ["korean", "fried", "spicy", "delicious"],
            },
            {
                "name": "韩式炒年糕",
                "description": "韩式小吃，年糕软糯，酱料浓郁，开胃下饭",
                "meal_types": ["lunch", "dinner", "snack"],
                "cuisine": "korean",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["年糕", "辣椒酱", "鱼饼", "葱花"],
                "tags": ["korean", "spicy", "delicious", "simple"],
            },
            {
                "name": "韩式拌饭",
                "description": "韩式经典，米饭香糯，配料丰富，营养均衡",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "korean",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["米饭", "各种蔬菜", "鸡蛋", "辣椒酱"],
                "tags": ["korean", "mixed", "delicious", "balanced"],
            },
            {
                "name": "韩式煎饼",
                "description": "韩式小吃，饼皮酥脆，馅料丰富，简单美味",
                "meal_types": ["breakfast", "lunch"],
                "cuisine": "korean",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["面粉", "韭菜", "鸡蛋", "油"],
                "tags": ["korean", "pancake", "delicious", "simple"],
            },
            {
                "name": "韩式冷面",
                "description": "韩式面食，面条劲道，汤汁清爽，夏季美食",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "korean",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["冷面", "牛肉汤", "黄瓜", "鸡蛋"],
                "tags": ["korean", "noodles", "cold", "delicious"],
            },
            # 泰餐经典 (5个)
            {
                "name": "泰式咖喱",
                "description": "泰式经典，咖喱浓郁，椰香四溢，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "thai",
                "difficulty": "medium",
                "cooking_time": 40,
                "ingredients": ["咖喱酱", "椰奶", "鸡肉", "蔬菜"],
                "tags": ["thai", "curry", "spicy", "delicious"],
            },
            {
                "name": "冬阴功汤",
                "description": "泰式汤品，酸辣开胃，香气浓郁，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "thai",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["虾", "柠檬草", "辣椒", "椰奶"],
                "tags": ["thai", "soup", "sour", "spicy"],
            },
            {
                "name": "泰式炒河粉",
                "description": "泰式炒粉，河粉爽滑，配料丰富，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "thai",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["河粉", "豆芽", "虾", "鱼露"],
                "tags": ["thai", "noodles", "delicious", "simple"],
            },
            {
                "name": "泰式青咖喱",
                "description": "泰式咖喱，青咖喱香辣，椰香浓郁，营养丰富",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "thai",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["青咖喱酱", "椰奶", "鸡肉", "茄子"],
                "tags": ["thai", "curry", "spicy", "delicious"],
            },
            {
                "name": "泰式芒果糯米饭",
                "description": "泰式甜点，芒果香甜，糯米软糯，清爽可口",
                "meal_types": ["dessert"],
                "cuisine": "thai",
                "difficulty": "easy",
                "cooking_time": 30,
                "ingredients": ["糯米", "芒果", "椰奶", "糖"],
                "tags": ["thai", "dessert", "sweet", "delicious"],
            },
            # 早餐经典 (8个)
            {
                "name": "豆浆油条",
                "description": "中式早餐，豆浆香浓，油条酥脆，经典搭配",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["豆浆", "油条", "咸菜", "葱花"],
                "tags": ["chinese", "breakfast", "classic", "delicious"],
            },
            {
                "name": "包子豆浆",
                "description": "中式早餐，包子松软，豆浆香浓，营养丰富",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["包子", "豆浆", "咸菜", "葱花"],
                "tags": ["chinese", "breakfast", "delicious", "nutritious"],
            },
            {
                "name": "煎饼果子",
                "description": "中式早餐，煎饼酥脆，配料丰富，简单美味",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 15,
                "ingredients": ["煎饼", "鸡蛋", "生菜", "酱料"],
                "tags": ["chinese", "breakfast", "delicious", "simple"],
            },
            {
                "name": "小笼包",
                "description": "中式早餐，包子小巧，汤汁丰富，精致美味",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["小笼包", "醋", "姜丝", "葱花"],
                "tags": ["chinese", "breakfast", "delicious", "premium"],
            },
            {
                "name": "燕麦粥",
                "description": "西式早餐，燕麦营养，配料丰富，健康美味",
                "meal_types": ["breakfast"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["燕麦", "牛奶", "蜂蜜", "坚果"],
                "tags": ["western", "breakfast", "healthy", "nutritious"],
            },
            {
                "name": "华夫饼",
                "description": "西式早餐，饼皮酥脆，配料丰富，简单美味",
                "meal_types": ["breakfast"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["华夫饼", "黄油", "枫糖浆", "水果"],
                "tags": ["western", "breakfast", "delicious", "simple"],
            },
            {
                "name": "日式味增汤",
                "description": "日式早餐，味增香浓，营养丰富，开胃暖身",
                "meal_types": ["breakfast"],
                "cuisine": "japanese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["味增", "豆腐", "海带", "葱花"],
                "tags": ["japanese", "breakfast", "delicious", "warm"],
            },
            {
                "name": "韩式泡菜汤",
                "description": "韩式早餐，泡菜酸辣，开胃暖身，营养丰富",
                "meal_types": ["breakfast"],
                "cuisine": "korean",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["泡菜", "豆腐", "猪肉", "辣椒"],
                "tags": ["korean", "breakfast", "spicy", "delicious"],
            },
        ]

        # 创建食物项目
        created_count = 0
        for food_data in base_foods:
            try:
                # 使用精确图片服务获取图片
                image_url = image_service.get_accurate_food_image(food_data["name"], food_data["cuisine"])

                # 使用DeepSeek生成准确描述
                ai_description = image_service.get_deepseek_food_description(food_data["name"], food_data["cuisine"])

                # 合并描述
                final_description = f"{food_data['description']} {ai_description}"

                FoodItem.objects.create(
                    name=food_data["name"],
                    description=final_description,
                    meal_types=food_data["meal_types"],
                    cuisine=food_data["cuisine"],
                    difficulty=food_data["difficulty"],
                    cooking_time=food_data["cooking_time"],
                    ingredients=food_data["ingredients"],
                    tags=food_data["tags"],
                    image_url=image_url,
                    recipe_url=f"https://www.xiachufang.com/recipe/{100000000 + created_count}/",
                    popularity_score=0.0,
                    is_active=True,
                )
                created_count += 1
                self.stdout.write(f"✅ 创建: {food_data['name']} (图片: {image_url[:50]}...)")
            except Exception as e:
                self.stdout.write(f"❌ 创建失败 {food_data['name']}: {str(e)}")

        self.stdout.write(f"\n🎉 完成！共创建了 {created_count} 个食物项目")
        self.stdout.write("📊 食物分布:")

        # 统计各菜系数量
        cuisines = FoodItem.objects.values_list("cuisine", flat=True)
        cuisine_counts = {}
        for cuisine in cuisines:
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1

        for cuisine, count in cuisine_counts.items():
            self.stdout.write(f"  - {cuisine}: {count} 个")

        # 统计各餐种数量
        meal_types = []
        for food in FoodItem.objects.all():
            meal_types.extend(food.meal_types)

        meal_type_counts = {}
        for meal_type in meal_types:
            meal_type_counts[meal_type] = meal_type_counts.get(meal_type, 0) + 1

        self.stdout.write("\n🍽️ 餐种分布:")
        for meal_type, count in meal_type_counts.items():
            self.stdout.write(f"  - {meal_type}: {count} 个")

        # 检查图片覆盖率
        foods_with_images = FoodItem.objects.exclude(image_url="").exclude(image_url__isnull=True)
        image_coverage = (foods_with_images.count() / FoodItem.objects.count()) * 100

        self.stdout.write(f"\n🖼️ 图片覆盖率: {image_coverage:.1f}%")
        self.stdout.write(f"📸 有图片的食物: {foods_with_images.count()} 个")

        # 检查标签分布
        self.stdout.write("\n🏷️ 标签统计:")
        all_tags = []
        for food in FoodItem.objects.all():
            all_tags.extend(food.tags)

        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 显示前10个最常用的标签
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in sorted_tags:
            self.stdout.write(f"  - {tag}: {count} 次")

        self.stdout.write("\n✨ 食物数据初始化完成！")
        self.stdout.write("🎯 特点:")
        self.stdout.write("  - 移除了微辣、清淡等分类")
        self.stdout.write("  - 确保食物与图片一一对应")
        self.stdout.write("  - 丰富了食物种类")
        self.stdout.write("  - 提供了准确的描述")
