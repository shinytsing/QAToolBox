from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = '创建完整的上班族食品库'

    def handle(self, *args, **options):
        # 完整的上班族食品库数据 - 基于DeepSeek数据
        complete_office_foods = [
            # 早餐类
            {
                'name': '豆浆油条',
                'description': '经典中式早餐，豆浆营养丰富，油条香脆可口',
                'meal_types': ['breakfast'],
                'cuisine': 'chinese',
                'difficulty': 'easy',
                'cooking_time': 10,
                'ingredients': ['豆浆', '油条', '白糖'],
                'tags': ['breakfast', 'traditional', 'quick'],
                'image_url': '/static/img/food/soy-milk-1280.jpg',
                'calories': 320, 'protein': 12, 'fat': 18, 'carbohydrates': 35, 'fiber': 3, 'sugar': 8, 'sodium': 680
            },
            {
                'name': '煎蛋三明治',
                'description': '简单营养的早餐选择，鸡蛋蛋白质丰富',
                'meal_types': ['breakfast'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 8,
                'ingredients': ['面包', '鸡蛋', '生菜', '番茄'],
                'tags': ['breakfast', 'protein', 'quick'],
                'image_url': '/static/img/food/egg-sandwich-1280.jpg',
                'calories': 280, 'protein': 15, 'fat': 12, 'carbohydrates': 32, 'fiber': 2, 'sugar': 5, 'sodium': 450
            },
            {
                'name': '燕麦粥',
                'description': '健康营养的早餐，富含膳食纤维',
                'meal_types': ['breakfast'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 15,
                'ingredients': ['燕麦', '牛奶', '蜂蜜', '坚果'],
                'tags': ['breakfast', 'healthy', 'fiber'],
                'image_url': '/static/img/food/oatmeal-1280.jpg',
                'calories': 220, 'protein': 8, 'fat': 6, 'carbohydrates': 35, 'fiber': 5, 'sugar': 12, 'sodium': 120
            },
            {
                'name': '包子豆浆',
                'description': '传统中式早餐，包子馅料丰富，豆浆营养',
                'meal_types': ['breakfast'],
                'cuisine': 'chinese',
                'difficulty': 'easy',
                'cooking_time': 5,
                'ingredients': ['包子', '豆浆', '咸菜'],
                'tags': ['breakfast', 'traditional', 'quick'],
                'image_url': '/static/img/food/baozi-1280.jpg',
                'calories': 280, 'protein': 10, 'fat': 8, 'carbohydrates': 45, 'fiber': 2, 'sugar': 6, 'sodium': 450
            },
            {
                'name': '牛奶麦片',
                'description': '西式早餐，简单快捷，营养均衡',
                'meal_types': ['breakfast'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 3,
                'ingredients': ['牛奶', '麦片', '香蕉', '蜂蜜'],
                'tags': ['breakfast', 'quick', 'healthy'],
                'image_url': '/static/img/food/cereal-1280.jpg',
                'calories': 250, 'protein': 8, 'fat': 5, 'carbohydrates': 45, 'fiber': 4, 'sugar': 15, 'sodium': 200
            },
            
            # 午餐类 - 中式
            {
                'name': '宫保鸡丁',
                'description': '经典川菜，鸡肉嫩滑，花生香脆，微辣开胃',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 25,
                'ingredients': ['鸡胸肉', '花生', '干辣椒', '黄瓜', '葱姜蒜'],
                'tags': ['sichuan', 'spicy', 'popular'],
                'image_url': '/static/img/food/kungpao-chicken-1280.jpg',
                'calories': 320, 'protein': 25, 'fat': 18, 'carbohydrates': 15, 'fiber': 2, 'sugar': 8, 'sodium': 850
            },
            {
                'name': '麻婆豆腐',
                'description': '川菜经典，豆腐嫩滑，麻辣鲜香',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 20,
                'ingredients': ['嫩豆腐', '猪肉末', '豆瓣酱', '花椒', '葱花'],
                'tags': ['sichuan', 'spicy', 'tofu'],
                'image_url': '/static/img/food/mapo-tofu-1280.jpg',
                'calories': 280, 'protein': 18, 'fat': 22, 'carbohydrates': 8, 'fiber': 3, 'sugar': 2, 'sodium': 1200
            },
            {
                'name': '番茄炒蛋',
                'description': '家常菜，简单易做，营养丰富',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'easy',
                'cooking_time': 12,
                'ingredients': ['番茄', '鸡蛋', '葱花', '盐'],
                'tags': ['homestyle', 'easy', 'healthy'],
                'image_url': '/static/img/food/tomato-egg-1280.jpg',
                'calories': 220, 'protein': 15, 'fat': 16, 'carbohydrates': 8, 'fiber': 2, 'sugar': 5, 'sodium': 450
            },
            {
                'name': '青椒肉丝',
                'description': '经典家常菜，青椒爽脆，肉丝嫩滑',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 18,
                'ingredients': ['青椒', '猪肉丝', '蒜末', '生抽'],
                'tags': ['homestyle', 'green', 'protein'],
                'image_url': '/static/img/food/pepper-pork-1280.jpg',
                'calories': 260, 'protein': 22, 'fat': 18, 'carbohydrates': 8, 'fiber': 2, 'sugar': 3, 'sodium': 680
            },
            {
                'name': '鱼香肉丝',
                'description': '川菜经典，肉丝嫩滑，鱼香味浓郁',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 20,
                'ingredients': ['猪肉丝', '木耳', '胡萝卜', '豆瓣酱', '醋'],
                'tags': ['sichuan', 'sweet-sour', 'popular'],
                'image_url': '/static/img/food/yuxiang-pork-1280.jpg',
                'calories': 290, 'protein': 20, 'fat': 16, 'carbohydrates': 18, 'fiber': 2, 'sugar': 10, 'sodium': 890
            },
            {
                'name': '回锅肉',
                'description': '川菜经典，肥而不腻，香辣可口',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 30,
                'ingredients': ['五花肉', '青椒', '豆瓣酱', '蒜苗', '干辣椒'],
                'tags': ['sichuan', 'spicy', 'pork'],
                'image_url': '/static/img/food/twice-cooked-pork-1280.jpg',
                'calories': 420, 'protein': 25, 'fat': 32, 'carbohydrates': 8, 'fiber': 2, 'sugar': 4, 'sodium': 950
            },
            {
                'name': '白切鸡',
                'description': '粤菜经典，鸡肉嫩滑，清淡鲜美',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 45,
                'ingredients': ['整鸡', '姜葱', '料酒', '盐', '蘸料'],
                'tags': ['cantonese', 'light', 'protein'],
                'image_url': '/static/img/food/white-cut-chicken-1280.jpg',
                'calories': 280, 'protein': 35, 'fat': 15, 'carbohydrates': 2, 'fiber': 0, 'sugar': 1, 'sodium': 450
            },
            {
                'name': '叉烧肉',
                'description': '粤式烧腊，甜咸适中，肉质鲜嫩',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'hard',
                'cooking_time': 60,
                'ingredients': ['五花肉', '叉烧酱', '蜂蜜', '五香粉', '料酒'],
                'tags': ['cantonese', 'bbq', 'sweet'],
                'image_url': '/static/img/food/char-siu-1280.jpg',
                'calories': 380, 'protein': 25, 'fat': 28, 'carbohydrates': 12, 'fiber': 1, 'sugar': 8, 'sodium': 1200
            },
            {
                'name': '炸酱面',
                'description': '北京特色，面条劲道，酱料浓郁',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 25,
                'ingredients': ['面条', '甜面酱', '猪肉末', '黄瓜丝', '豆芽'],
                'tags': ['beijing', 'noodles', 'sauce'],
                'image_url': '/static/img/food/zhajiang-noodles-1280.jpg',
                'calories': 420, 'protein': 18, 'fat': 15, 'carbohydrates': 55, 'fiber': 4, 'sugar': 8, 'sodium': 1200
            },
            {
                'name': '蛋炒饭',
                'description': '经典炒饭，简单美味，饱腹感强',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'chinese',
                'difficulty': 'easy',
                'cooking_time': 15,
                'ingredients': ['米饭', '鸡蛋', '葱花', '胡萝卜', '火腿'],
                'tags': ['fried-rice', 'quick', 'popular'],
                'image_url': '/static/img/food/egg-fried-rice-1280.jpg',
                'calories': 380, 'protein': 12, 'fat': 15, 'carbohydrates': 55, 'fiber': 2, 'sugar': 3, 'sodium': 680
            },
            
            # 午餐类 - 西式
            {
                'name': '意大利面',
                'description': '经典意式料理，面条劲道，酱汁浓郁',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'western',
                'difficulty': 'medium',
                'cooking_time': 20,
                'ingredients': ['意大利面', '番茄酱', '肉末', '洋葱', '奶酪'],
                'tags': ['italian', 'pasta', 'popular'],
                'image_url': '/static/img/food/spaghetti-1280.jpg',
                'calories': 380, 'protein': 12, 'fat': 8, 'carbohydrates': 65, 'fiber': 4, 'sugar': 6, 'sodium': 680
            },
            {
                'name': '三明治',
                'description': '简单营养的午餐选择，方便携带',
                'meal_types': ['lunch'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 10,
                'ingredients': ['面包', '火腿', '生菜', '番茄', '奶酪'],
                'tags': ['quick', 'portable', 'lunch'],
                'image_url': '/static/img/food/sandwich-1280.jpg',
                'calories': 280, 'protein': 15, 'fat': 12, 'carbohydrates': 32, 'fiber': 3, 'sugar': 5, 'sodium': 680
            },
            {
                'name': '沙拉',
                'description': '健康轻食，新鲜蔬菜，低卡路里',
                'meal_types': ['lunch'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 8,
                'ingredients': ['生菜', '番茄', '黄瓜', '胡萝卜', '橄榄油'],
                'tags': ['healthy', 'light', 'vegetarian'],
                'image_url': '/static/img/food/salad-1280.jpg',
                'calories': 120, 'protein': 8, 'fat': 8, 'carbohydrates': 12, 'fiber': 4, 'sugar': 6, 'sodium': 450
            },
            {
                'name': '汉堡包',
                'description': '美式快餐，方便快捷，饱腹感强',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'western',
                'difficulty': 'easy',
                'cooking_time': 12,
                'ingredients': ['汉堡面包', '牛肉饼', '生菜', '番茄', '奶酪'],
                'tags': ['fast-food', 'quick', 'popular'],
                'image_url': '/static/img/food/burger-1280.jpg',
                'calories': 520, 'protein': 25, 'fat': 28, 'carbohydrates': 42, 'fiber': 2, 'sugar': 8, 'sodium': 850
            },
            {
                'name': '披萨',
                'description': '意式快餐，奶酪浓郁，配料丰富',
                'meal_types': ['lunch', 'dinner'],
                'cuisine': 'western',
                'difficulty': 'medium',
                'cooking_time': 25,
                'ingredients': ['披萨饼底', '番茄酱', '奶酪', '火腿', '蘑菇'],
                'tags': ['italian', 'cheese', 'popular'],
                'image_url': '/static/img/food/pizza-1280.jpg',
                'calories': 450, 'protein': 18, 'fat': 22, 'carbohydrates': 48, 'fiber': 3, 'sugar': 8, 'sodium': 1200
            },
            
            # 晚餐类
            {
                'name': '红烧肉',
                'description': '经典家常菜，肥而不腻，入口即化',
                'meal_types': ['dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 60,
                'ingredients': ['五花肉', '生抽', '老抽', '冰糖', '葱姜'],
                'tags': ['homestyle', 'braised', 'popular'],
                'image_url': '/static/img/food/braised-pork-1280.jpg',
                'calories': 450, 'protein': 28, 'fat': 35, 'carbohydrates': 5, 'fiber': 1, 'sugar': 3, 'sodium': 680
            },
            {
                'name': '牛排',
                'description': '西式经典，肉质鲜嫩，营养丰富',
                'meal_types': ['dinner'],
                'cuisine': 'western',
                'difficulty': 'medium',
                'cooking_time': 15,
                'ingredients': ['牛排', '黑胡椒', '盐', '黄油', '迷迭香'],
                'tags': ['western', 'protein', 'premium'],
                'image_url': '/static/img/food/steak-1280.jpg',
                'calories': 380, 'protein': 45, 'fat': 22, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 450
            },
            {
                'name': '水煮鱼',
                'description': '川菜经典，鱼肉嫩滑，麻辣鲜香',
                'meal_types': ['dinner'],
                'cuisine': 'chinese',
                'difficulty': 'hard',
                'cooking_time': 30,
                'ingredients': ['草鱼', '豆芽', '干辣椒', '花椒', '蒜末'],
                'tags': ['sichuan', 'spicy', 'fish'],
                'image_url': '/static/img/food/boiled-fish-1280.jpg',
                'calories': 310, 'protein': 35, 'fat': 18, 'carbohydrates': 5, 'fiber': 2, 'sugar': 2, 'sodium': 1100
            },
            {
                'name': '北京烤鸭',
                'description': '北京名菜，皮酥肉嫩，配饼卷食',
                'meal_types': ['dinner'],
                'cuisine': 'chinese',
                'difficulty': 'hard',
                'cooking_time': 120,
                'ingredients': ['整鸭', '甜面酱', '葱丝', '黄瓜丝', '薄饼'],
                'tags': ['beijing', 'roasted', 'premium'],
                'image_url': '/static/img/food/beijing-duck-1280.jpg',
                'calories': 450, 'protein': 35, 'fat': 30, 'carbohydrates': 8, 'fiber': 1, 'sugar': 2, 'sodium': 680
            },
            {
                'name': '东坡肉',
                'description': '江浙名菜，肥而不腻，入口即化',
                'meal_types': ['dinner'],
                'cuisine': 'chinese',
                'difficulty': 'hard',
                'cooking_time': 90,
                'ingredients': ['五花肉', '黄酒', '酱油', '冰糖', '葱姜'],
                'tags': ['jiangsu', 'braised', 'premium'],
                'image_url': '/static/img/food/dongpo-pork-1280.jpg',
                'calories': 520, 'protein': 30, 'fat': 42, 'carbohydrates': 6, 'fiber': 1, 'sugar': 4, 'sodium': 850
            },
            {
                'name': '剁椒鱼头',
                'description': '湘菜经典，鱼头鲜美，剁椒香辣',
                'meal_types': ['dinner'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 25,
                'ingredients': ['鱼头', '剁椒', '蒜末', '姜丝', '葱花'],
                'tags': ['hunan', 'spicy', 'fish'],
                'image_url': '/static/img/food/chopped-fish-head-1280.jpg',
                'calories': 280, 'protein': 32, 'fat': 16, 'carbohydrates': 5, 'fiber': 2, 'sugar': 2, 'sodium': 1100
            },
            
            # 夜宵类
            {
                'name': '小龙虾',
                'description': '夜宵首选，麻辣鲜香，肉质鲜美',
                'meal_types': ['snack'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 20,
                'ingredients': ['小龙虾', '干辣椒', '花椒', '蒜末', '啤酒'],
                'tags': ['spicy', 'seafood', 'snack'],
                'image_url': '/static/img/food/crayfish-1280.jpg',
                'calories': 180, 'protein': 28, 'fat': 8, 'carbohydrates': 2, 'fiber': 0, 'sugar': 1, 'sodium': 450
            },
            {
                'name': '火锅',
                'description': '社交美食，汤底浓郁，配料丰富',
                'meal_types': ['dinner', 'snack'],
                'cuisine': 'chinese',
                'difficulty': 'easy',
                'cooking_time': 15,
                'ingredients': ['火锅底料', '牛肉片', '蔬菜', '豆腐', '粉丝'],
                'tags': ['social', 'hot-pot', 'popular'],
                'image_url': '/static/img/food/hotpot-1280.jpg',
                'calories': 350, 'protein': 25, 'fat': 22, 'carbohydrates': 15, 'fiber': 4, 'sugar': 5, 'sodium': 1200
            },
            {
                'name': '烧烤',
                'description': '夜宵经典，炭火烤制，香气四溢',
                'meal_types': ['snack'],
                'cuisine': 'chinese',
                'difficulty': 'medium',
                'cooking_time': 30,
                'ingredients': ['羊肉串', '鸡翅', '蔬菜', '孜然', '辣椒粉'],
                'tags': ['bbq', 'grilled', 'snack'],
                'image_url': '/static/img/food/bbq-1280.jpg',
                'calories': 400, 'protein': 30, 'fat': 25, 'carbohydrates': 10, 'fiber': 2, 'sugar': 3, 'sodium': 800
            }
        ]
        
        # 清除现有数据
        FoodItem.objects.all().delete()
        self.stdout.write('🗑️ 已清除现有食物数据')
        
        created_count = 0
        
        for food_data in complete_office_foods:
            food = FoodItem.objects.create(
                name=food_data['name'],
                description=food_data['description'],
                meal_types=food_data['meal_types'],
                cuisine=food_data['cuisine'],
                difficulty=food_data['difficulty'],
                cooking_time=food_data['cooking_time'],
                ingredients=food_data['ingredients'],
                tags=food_data['tags'],
                image_url=food_data['image_url'],
                calories=food_data['calories'],
                protein=food_data['protein'],
                fat=food_data['fat'],
                carbohydrates=food_data['carbohydrates'],
                fiber=food_data['fiber'],
                sugar=food_data['sugar'],
                sodium=food_data['sodium'],
                popularity_score=0.8,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ 创建: {food.name} - {food_data["calories"]}千卡')
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 完整上班族食品库创建完成! 共创建: {created_count}个食物')
        )
        
        # 统计信息
        breakfast_count = FoodItem.objects.filter(meal_types__contains=['breakfast']).count()
        lunch_count = FoodItem.objects.filter(meal_types__contains=['lunch']).count()
        dinner_count = FoodItem.objects.filter(meal_types__contains=['dinner']).count()
        snack_count = FoodItem.objects.filter(meal_types__contains=['snack']).count()
        
        self.stdout.write(f'\n📈 食物分类统计:')
        self.stdout.write(f'   早餐: {breakfast_count}个')
        self.stdout.write(f'   午餐: {lunch_count}个')
        self.stdout.write(f'   晚餐: {dinner_count}个')
        self.stdout.write(f'   夜宵: {snack_count}个')
