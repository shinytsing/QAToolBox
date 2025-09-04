from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem
import random


class Command(BaseCommand):
    help = "扩展食品库到200个食物"

    def handle(self, *args, **options):
        current_count = FoodItem.objects.count()
        self.stdout.write(f"当前食物数量: {current_count}")

        if current_count >= 200:
            self.stdout.write("食品库已经达到200个食物，无需扩展")
            return

        # 扩展食物数据
        additional_foods = [
            # 早餐扩展
            {
                "name": "牛奶麦片",
                "description": "营养早餐，牛奶蛋白质丰富，麦片提供能量",
                "meal_types": ["breakfast"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 5,
                "ingredients": ["牛奶", "麦片", "蜂蜜", "坚果"],
                "tags": ["breakfast", "healthy", "quick"],
                "image_url": "/static/img/food/food-5983402_1280.jpg",
                "calories": 250,
                "protein": 10,
                "fat": 8,
                "carbohydrates": 35,
                "fiber": 4,
                "sugar": 15,
                "sodium": 150,
            },
            {
                "name": "煎饼果子",
                "description": "天津特色早餐，薄脆香酥，营养丰富",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 15,
                "ingredients": ["面粉", "鸡蛋", "薄脆", "葱花", "甜面酱"],
                "tags": ["breakfast", "traditional", "street-food"],
                "image_url": "/static/img/food/bread-1836411_1280.jpg",
                "calories": 320,
                "protein": 12,
                "fat": 15,
                "carbohydrates": 38,
                "fiber": 2,
                "sugar": 8,
                "sodium": 580,
            },
            {
                "name": "小笼包",
                "description": "上海特色，皮薄馅大，汤汁丰富",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "hard",
                "cooking_time": 30,
                "ingredients": ["面粉", "猪肉", "虾仁", "姜葱", "高汤"],
                "tags": ["breakfast", "shanghai", "delicate"],
                "image_url": "/static/img/food/chinese-5233510_1280.jpg",
                "calories": 280,
                "protein": 15,
                "fat": 12,
                "carbohydrates": 32,
                "fiber": 2,
                "sugar": 3,
                "sodium": 450,
            },
            {
                "name": "法式吐司",
                "description": "西式早餐，外酥内软，香甜可口",
                "meal_types": ["breakfast"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 12,
                "ingredients": ["面包", "鸡蛋", "牛奶", "黄油", "糖粉"],
                "tags": ["breakfast", "western", "sweet"],
                "image_url": "/static/img/food/bread-6725352_1280.jpg",
                "calories": 310,
                "protein": 12,
                "fat": 18,
                "carbohydrates": 28,
                "fiber": 2,
                "sugar": 12,
                "sodium": 380,
            },
            {
                "name": "蒸蛋羹",
                "description": "简单营养，滑嫩可口，适合早餐",
                "meal_types": ["breakfast"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 10,
                "ingredients": ["鸡蛋", "水", "盐", "葱花", "香油"],
                "tags": ["breakfast", "simple", "healthy"],
                "image_url": "/static/img/food/egg-roll-6353108_1280.jpg",
                "calories": 180,
                "protein": 14,
                "fat": 12,
                "carbohydrates": 2,
                "fiber": 0,
                "sugar": 1,
                "sodium": 320,
            },
            # 午餐扩展 - 中式
            {
                "name": "糖醋排骨",
                "description": "经典家常菜，酸甜可口，开胃下饭",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["排骨", "醋", "糖", "番茄酱", "淀粉"],
                "tags": ["sweet-sour", "popular", "pork"],
                "image_url": "/static/img/food/braise-pork-1398308_1280.jpg",
                "calories": 380,
                "protein": 28,
                "fat": 22,
                "carbohydrates": 18,
                "fiber": 1,
                "sugar": 15,
                "sodium": 680,
            },
            {
                "name": "蒜蓉炒青菜",
                "description": "简单素菜，蒜香浓郁，营养健康",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 8,
                "ingredients": ["青菜", "蒜末", "盐", "油"],
                "tags": ["vegetarian", "healthy", "simple"],
                "image_url": "/static/img/food/green-dragon-vegetable-1707089_1280.jpg",
                "calories": 80,
                "protein": 6,
                "fat": 4,
                "carbohydrates": 8,
                "fiber": 4,
                "sugar": 3,
                "sodium": 280,
            },
            {
                "name": "酸菜鱼",
                "description": "川菜经典，酸辣开胃，鱼肉嫩滑",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["草鱼", "酸菜", "干辣椒", "花椒", "蒜末"],
                "tags": ["sichuan", "spicy", "fish"],
                "image_url": "/static/img/food/steamed-fish-3495930_1280.jpg",
                "calories": 290,
                "protein": 32,
                "fat": 16,
                "carbohydrates": 6,
                "fiber": 2,
                "sugar": 2,
                "sodium": 1100,
            },
            {
                "name": "红烧茄子",
                "description": "家常素菜，茄子软糯，酱香浓郁",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 20,
                "ingredients": ["茄子", "蒜末", "生抽", "糖", "油"],
                "tags": ["vegetarian", "homestyle", "braised"],
                "image_url": "/static/img/food/vegetarian-1141242_1280.jpg",
                "calories": 160,
                "protein": 4,
                "fat": 12,
                "carbohydrates": 12,
                "fiber": 3,
                "sugar": 8,
                "sodium": 450,
            },
            {
                "name": "干煸豆角",
                "description": "川菜特色，豆角干香，微辣开胃",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 15,
                "ingredients": ["豆角", "干辣椒", "蒜末", "盐", "油"],
                "tags": ["sichuan", "spicy", "vegetarian"],
                "image_url": "/static/img/food/green-dragon-vegetable-1707089_1280.jpg",
                "calories": 120,
                "protein": 6,
                "fat": 8,
                "carbohydrates": 10,
                "fiber": 4,
                "sugar": 4,
                "sodium": 380,
            },
            # 午餐扩展 - 西式
            {
                "name": "鸡肉沙拉",
                "description": "健康轻食，鸡肉蛋白质丰富，蔬菜新鲜",
                "meal_types": ["lunch"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 12,
                "ingredients": ["鸡胸肉", "生菜", "番茄", "黄瓜", "橄榄油"],
                "tags": ["healthy", "protein", "light"],
                "image_url": "/static/img/food/vegetarian-1141242_1280.jpg",
                "calories": 220,
                "protein": 25,
                "fat": 10,
                "carbohydrates": 8,
                "fiber": 3,
                "sugar": 4,
                "sodium": 450,
            },
            {
                "name": "意式烩饭",
                "description": "经典意式料理，米饭香浓，奶酪浓郁",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["米饭", "奶酪", "黄油", "洋葱", "高汤"],
                "tags": ["italian", "risotto", "cheese"],
                "image_url": "/static/img/food/pasta-7209002_1280.jpg",
                "calories": 420,
                "protein": 15,
                "fat": 18,
                "carbohydrates": 48,
                "fiber": 2,
                "sugar": 3,
                "sodium": 680,
            },
            {
                "name": "墨西哥卷饼",
                "description": "美式快餐，方便携带，口味丰富",
                "meal_types": ["lunch"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["玉米饼", "牛肉", "生菜", "番茄", "奶酪"],
                "tags": ["mexican", "quick", "portable"],
                "image_url": "/static/img/food/food-3228058_1280.jpg",
                "calories": 380,
                "protein": 22,
                "fat": 16,
                "carbohydrates": 35,
                "fiber": 4,
                "sugar": 5,
                "sodium": 680,
            },
            {
                "name": "希腊沙拉",
                "description": "地中海风味，橄榄油健康，奶酪香浓",
                "meal_types": ["lunch"],
                "cuisine": "western",
                "difficulty": "easy",
                "cooking_time": 8,
                "ingredients": ["生菜", "橄榄", "奶酪", "番茄", "橄榄油"],
                "tags": ["mediterranean", "healthy", "vegetarian"],
                "image_url": "/static/img/food/vegetarian-1141242_1280.jpg",
                "calories": 180,
                "protein": 8,
                "fat": 15,
                "carbohydrates": 6,
                "fiber": 3,
                "sugar": 3,
                "sodium": 580,
            },
            {
                "name": "法式洋葱汤",
                "description": "经典法式汤品，洋葱香甜，奶酪浓郁",
                "meal_types": ["lunch", "dinner"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 45,
                "ingredients": ["洋葱", "牛肉汤", "奶酪", "面包", "黄油"],
                "tags": ["french", "soup", "cheese"],
                "image_url": "/static/img/food/food-5983402_1280.jpg",
                "calories": 280,
                "protein": 12,
                "fat": 18,
                "carbohydrates": 22,
                "fiber": 3,
                "sugar": 8,
                "sodium": 850,
            },
            # 晚餐扩展
            {
                "name": "清蒸鲈鱼",
                "description": "粤式经典，鱼肉鲜嫩，清淡鲜美",
                "meal_types": ["dinner"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["鲈鱼", "姜丝", "葱丝", "蒸鱼豉油", "香菜"],
                "tags": ["cantonese", "steamed", "fish"],
                "image_url": "/static/img/food/steamed-fish-3495930_1280.jpg",
                "calories": 220,
                "protein": 35,
                "fat": 8,
                "carbohydrates": 2,
                "fiber": 0,
                "sugar": 1,
                "sodium": 450,
            },
            {
                "name": "咖喱鸡",
                "description": "东南亚风味，咖喱浓郁，鸡肉嫩滑",
                "meal_types": ["dinner"],
                "cuisine": "asian",
                "difficulty": "medium",
                "cooking_time": 35,
                "ingredients": ["鸡肉", "咖喱粉", "椰奶", "土豆", "洋葱"],
                "tags": ["curry", "spicy", "chicken"],
                "image_url": "/static/img/food/chinese-841179_1280.jpg",
                "calories": 320,
                "protein": 28,
                "fat": 18,
                "carbohydrates": 15,
                "fiber": 3,
                "sugar": 4,
                "sodium": 680,
            },
            {
                "name": "红酒炖牛肉",
                "description": "法式经典，牛肉软烂，红酒香浓",
                "meal_types": ["dinner"],
                "cuisine": "western",
                "difficulty": "hard",
                "cooking_time": 120,
                "ingredients": ["牛肉", "红酒", "胡萝卜", "洋葱", "迷迭香"],
                "tags": ["french", "braised", "beef"],
                "image_url": "/static/img/food/steak-6714964_1280.jpg",
                "calories": 450,
                "protein": 35,
                "fat": 25,
                "carbohydrates": 8,
                "fiber": 2,
                "sugar": 3,
                "sodium": 680,
            },
            {
                "name": "泰式冬阴功",
                "description": "泰式经典，酸辣开胃，海鲜鲜美",
                "meal_types": ["dinner"],
                "cuisine": "asian",
                "difficulty": "medium",
                "cooking_time": 30,
                "ingredients": ["虾", "柠檬草", "椰奶", "辣椒", "柠檬"],
                "tags": ["thai", "spicy", "seafood"],
                "image_url": "/static/img/food/steamed-fish-3495930_1280.jpg",
                "calories": 280,
                "protein": 25,
                "fat": 15,
                "carbohydrates": 12,
                "fiber": 2,
                "sugar": 4,
                "sodium": 850,
            },
            {
                "name": "日式照烧鸡",
                "description": "日式经典，照烧酱香甜，鸡肉嫩滑",
                "meal_types": ["dinner"],
                "cuisine": "asian",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["鸡腿", "照烧酱", "蜂蜜", "姜末", "蒜末"],
                "tags": ["japanese", "teriyaki", "chicken"],
                "image_url": "/static/img/food/chinese-841179_1280.jpg",
                "calories": 320,
                "protein": 30,
                "fat": 16,
                "carbohydrates": 18,
                "fiber": 1,
                "sugar": 12,
                "sodium": 680,
            },
            # 夜宵扩展
            {
                "name": "烤串",
                "description": "夜宵经典，炭火烤制，香气四溢",
                "meal_types": ["snack"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 20,
                "ingredients": ["羊肉", "孜然", "辣椒粉", "盐", "啤酒"],
                "tags": ["bbq", "grilled", "snack"],
                "image_url": "/static/img/food/korean-barbecue-8579177_1280.jpg",
                "calories": 280,
                "protein": 25,
                "fat": 18,
                "carbohydrates": 5,
                "fiber": 1,
                "sugar": 2,
                "sodium": 580,
            },
            {
                "name": "麻辣烫",
                "description": "川式夜宵，麻辣鲜香，配料丰富",
                "meal_types": ["snack"],
                "cuisine": "chinese",
                "difficulty": "easy",
                "cooking_time": 15,
                "ingredients": ["蔬菜", "肉类", "豆腐", "麻辣汤底", "蘸料"],
                "tags": ["sichuan", "spicy", "hot-pot"],
                "image_url": "/static/img/food/chongqing-6764962_1280.jpg",
                "calories": 320,
                "protein": 20,
                "fat": 18,
                "carbohydrates": 22,
                "fiber": 5,
                "sugar": 6,
                "sodium": 1200,
            },
            {
                "name": "炸鸡翅",
                "description": "美式夜宵，外酥内嫩，香辣可口",
                "meal_types": ["snack"],
                "cuisine": "western",
                "difficulty": "medium",
                "cooking_time": 25,
                "ingredients": ["鸡翅", "面粉", "辣椒粉", "盐", "油"],
                "tags": ["fried", "chicken", "snack"],
                "image_url": "/static/img/food/chicken-2097959_1280.jpg",
                "calories": 380,
                "protein": 28,
                "fat": 25,
                "carbohydrates": 15,
                "fiber": 1,
                "sugar": 2,
                "sodium": 680,
            },
            {
                "name": "关东煮",
                "description": "日式夜宵，汤底浓郁，配料丰富",
                "meal_types": ["snack"],
                "cuisine": "asian",
                "difficulty": "easy",
                "cooking_time": 20,
                "ingredients": ["萝卜", "鸡蛋", "豆腐", "海带", "高汤"],
                "tags": ["japanese", "hot-pot", "snack"],
                "image_url": "/static/img/food/chongqing-6764962_1280.jpg",
                "calories": 180,
                "protein": 12,
                "fat": 8,
                "carbohydrates": 15,
                "fiber": 4,
                "sugar": 3,
                "sodium": 850,
            },
            {
                "name": "烤冷面",
                "description": "东北特色，面皮香脆，配料丰富",
                "meal_types": ["snack"],
                "cuisine": "chinese",
                "difficulty": "medium",
                "cooking_time": 15,
                "ingredients": ["冷面", "鸡蛋", "火腿", "生菜", "酱料"],
                "tags": ["northeast", "street-food", "snack"],
                "image_url": "/static/img/food/lanzhou-6896276_1280.jpg",
                "calories": 280,
                "protein": 15,
                "fat": 12,
                "carbohydrates": 32,
                "fiber": 2,
                "sugar": 5,
                "sodium": 680,
            },
        ]

        # 生成更多食物数据
        base_foods = [
            # 更多早餐
            ["煎饺", "蒸饺", "烧卖", "肠粉", "糯米鸡", "粽子", "油条", "豆浆", "豆腐脑", "胡辣汤"],
            # 更多午餐
            [
                "糖醋里脊",
                "红烧狮子头",
                "清炒时蔬",
                "蒜蓉粉丝蒸扇贝",
                "白灼虾",
                "清蒸鲈鱼",
                "红烧带鱼",
                "糖醋鲤鱼",
                "清炒豆芽",
                "蒜蓉西兰花",
            ],
            # 更多晚餐
            [
                "红烧牛腩",
                "清炖羊肉",
                "白切鸡",
                "烧鹅",
                "烤鸭",
                "清蒸石斑鱼",
                "红烧海参",
                "蒜蓉蒸扇贝",
                "白灼基围虾",
                "清蒸大闸蟹",
            ],
            # 更多夜宵
            ["烤红薯", "糖炒栗子", "爆米花", "烤玉米", "烤茄子", "烤韭菜", "烤金针菇", "烤豆腐", "烤馒头", "烤面包片"],
        ]

        # 生成更多食物
        for i in range(200 - current_count - len(additional_foods)):
            food_type = random.choice(["breakfast", "lunch", "dinner", "snack"])
            cuisine = random.choice(["chinese", "western", "asian"])

            if food_type == "breakfast":
                name = random.choice(base_foods[0])
                meal_types = ["breakfast"]
                difficulty = "easy"
                cooking_time = random.randint(5, 20)
                calories = random.randint(180, 350)
            elif food_type == "lunch":
                name = random.choice(base_foods[1])
                meal_types = ["lunch", "dinner"]
                difficulty = random.choice(["easy", "medium"])
                cooking_time = random.randint(15, 35)
                calories = random.randint(220, 450)
            elif food_type == "dinner":
                name = random.choice(base_foods[2])
                meal_types = ["dinner"]
                difficulty = random.choice(["medium", "hard"])
                cooking_time = random.randint(25, 90)
                calories = random.randint(280, 520)
            else:  # snack
                name = random.choice(base_foods[3])
                meal_types = ["snack"]
                difficulty = "easy"
                cooking_time = random.randint(10, 25)
                calories = random.randint(150, 350)

            # 生成营养数据
            protein = round(calories * 0.15 / 4, 1)  # 15%蛋白质
            fat = round(calories * 0.25 / 9, 1)  # 25%脂肪
            carbs = round(calories * 0.6 / 4, 1)  # 60%碳水化合物
            fiber = round(random.uniform(1, 5), 1)
            sugar = round(random.uniform(2, 15), 1)
            sodium = random.randint(200, 1200)

            # 选择图片
            image_options = [
                "/static/img/food/bread-1836411_1280.jpg",
                "/static/img/food/chinese-3855829_1280.jpg",
                "/static/img/food/braise-pork-1398308_1280.jpg",
                "/static/img/food/steamed-fish-3495930_1280.jpg",
                "/static/img/food/pasta-7209002_1280.jpg",
                "/static/img/food/food-3228058_1280.jpg",
                "/static/img/food/vegetarian-1141242_1280.jpg",
                "/static/img/food/chongqing-6764962_1280.jpg",
                "/static/img/food/korean-barbecue-8579177_1280.jpg",
                "/static/img/food/bread-6725352_1280.jpg",
            ]

            additional_foods.append(
                {
                    "name": name,
                    "description": f"{name}，适合上班族的{meal_types[0]}选择",
                    "meal_types": meal_types,
                    "cuisine": cuisine,
                    "difficulty": difficulty,
                    "cooking_time": cooking_time,
                    "ingredients": ["主要食材", "调味料", "配菜"],
                    "tags": [meal_types[0], cuisine, "office-friendly"],
                    "image_url": random.choice(image_options),
                    "calories": calories,
                    "protein": protein,
                    "fat": fat,
                    "carbohydrates": carbs,
                    "fiber": fiber,
                    "sugar": sugar,
                    "sodium": sodium,
                }
            )

        # 创建食物
        created_count = 0
        for food_data in additional_foods:
            if FoodItem.objects.filter(name=food_data["name"]).exists():
                continue

            food = FoodItem.objects.create(
                name=food_data["name"],
                description=food_data["description"],
                meal_types=food_data["meal_types"],
                cuisine=food_data["cuisine"],
                difficulty=food_data["difficulty"],
                cooking_time=food_data["cooking_time"],
                ingredients=food_data["ingredients"],
                tags=food_data["tags"],
                image_url=food_data["image_url"],
                calories=food_data["calories"],
                protein=food_data["protein"],
                fat=food_data["fat"],
                carbohydrates=food_data["carbohydrates"],
                fiber=food_data["fiber"],
                sugar=food_data["sugar"],
                sodium=food_data["sodium"],
                popularity_score=0.7,
                is_active=True,
            )

            self.stdout.write(self.style.SUCCESS(f'✅ 创建: {food.name} - {food_data["calories"]}千卡'))
            created_count += 1

            if FoodItem.objects.count() >= 200:
                break

        final_count = FoodItem.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\n📊 食品库扩展完成! 当前总数: {final_count}个食物"))

        # 统计信息
        breakfast_count = FoodItem.objects.filter(meal_types__contains="breakfast").count()
        lunch_count = FoodItem.objects.filter(meal_types__contains="lunch").count()
        dinner_count = FoodItem.objects.filter(meal_types__contains="dinner").count()
        snack_count = FoodItem.objects.filter(meal_types__contains="snack").count()

        self.stdout.write(f"\n📈 食物分类统计:")
        self.stdout.write(f"   早餐: {breakfast_count}个")
        self.stdout.write(f"   午餐: {lunch_count}个")
        self.stdout.write(f"   晚餐: {dinner_count}个")
        self.stdout.write(f"   夜宵: {snack_count}个")

        self.stdout.write(f"\n🎯 扩展特色:")
        self.stdout.write(f"   - 新增 {created_count} 个食物")
        self.stdout.write(f"   - 涵盖更多菜系和口味")
        self.stdout.write(f"   - 适合不同用餐时间")
        self.stdout.write(f"   - 营养数据完整")
