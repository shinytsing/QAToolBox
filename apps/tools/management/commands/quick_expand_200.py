from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem
import random


class Command(BaseCommand):
    help = '快速扩展食品库到200个食物'

    def handle(self, *args, **options):
        current_count = FoodItem.objects.count()
        self.stdout.write(f'当前食物数量: {current_count}')
        
        if current_count >= 200:
            self.stdout.write('食品库已经达到200个食物，无需扩展')
            return
        
        # 预定义的食物名称列表
        food_names = [
            # 早餐类
            '牛奶麦片', '煎饼果子', '小笼包', '法式吐司', '蒸蛋羹', '煎饺', '蒸饺', '烧卖', '肠粉', '糯米鸡',
            '粽子', '油条', '豆浆', '豆腐脑', '胡辣汤', '包子', '馒头', '花卷', '咸鸭蛋', '茶叶蛋',
            
            # 午餐类 - 中式
            '糖醋排骨', '蒜蓉炒青菜', '酸菜鱼', '红烧茄子', '干煸豆角', '糖醋里脊', '红烧狮子头', '清炒时蔬',
            '蒜蓉粉丝蒸扇贝', '白灼虾', '清蒸鲈鱼', '红烧带鱼', '糖醋鲤鱼', '清炒豆芽', '蒜蓉西兰花',
            '红烧牛腩', '清炖羊肉', '白切鸡', '烧鹅', '烤鸭', '清蒸石斑鱼', '红烧海参', '蒜蓉蒸扇贝',
            '白灼基围虾', '清蒸大闸蟹', '清炒时蔬', '红烧肉', '回锅肉', '鱼香肉丝', '宫保鸡丁',
            
            # 午餐类 - 西式
            '鸡肉沙拉', '意式烩饭', '墨西哥卷饼', '希腊沙拉', '法式洋葱汤', '意大利面', '披萨', '汉堡包',
            '三明治', '沙拉', '牛排', '烤鸡', '烤鱼', '烤虾', '烤蔬菜', '土豆泥', '奶油汤', '蔬菜汤',
            
            # 晚餐类
            '清蒸鲈鱼', '咖喱鸡', '红酒炖牛肉', '泰式冬阴功', '日式照烧鸡', '红烧肉', '牛排', '水煮鱼',
            '北京烤鸭', '东坡肉', '剁椒鱼头', '清蒸鲈鱼', '红烧牛腩', '清炖羊肉', '白切鸡', '烧鹅',
            '烤鸭', '清蒸石斑鱼', '红烧海参', '蒜蓉蒸扇贝', '白灼基围虾', '清蒸大闸蟹',
            
            # 夜宵类
            '烤串', '麻辣烫', '炸鸡翅', '关东煮', '烤冷面', '烤红薯', '糖炒栗子', '爆米花', '烤玉米',
            '烤茄子', '烤韭菜', '烤金针菇', '烤豆腐', '烤馒头', '烤面包片', '小龙虾', '火锅', '烧烤',
            
            # 更多食物
            '麻婆豆腐', '番茄炒蛋', '青椒肉丝', '叉烧肉', '炸酱面', '蛋炒饭', '燕麦粥', '煎蛋三明治',
            '包子豆浆', '白切鸡', '叉烧肉', '炸酱面', '蛋炒饭', '意大利面', '三明治', '沙拉', '汉堡包',
            '披萨', '红烧肉', '牛排', '水煮鱼', '北京烤鸭', '东坡肉', '剁椒鱼头', '小龙虾', '火锅', '烧烤',
            
            # 继续添加更多食物名称
            '糖醋里脊', '红烧狮子头', '清炒时蔬', '蒜蓉粉丝蒸扇贝', '白灼虾', '清蒸鲈鱼', '红烧带鱼',
            '糖醋鲤鱼', '清炒豆芽', '蒜蓉西兰花', '红烧牛腩', '清炖羊肉', '白切鸡', '烧鹅', '烤鸭',
            '清蒸石斑鱼', '红烧海参', '蒜蓉蒸扇贝', '白灼基围虾', '清蒸大闸蟹', '清炒时蔬', '红烧肉',
            '回锅肉', '鱼香肉丝', '宫保鸡丁', '麻婆豆腐', '番茄炒蛋', '青椒肉丝', '叉烧肉', '炸酱面',
            '蛋炒饭', '意大利面', '三明治', '沙拉', '汉堡包', '披萨', '牛排', '水煮鱼', '北京烤鸭',
            '东坡肉', '剁椒鱼头', '小龙虾', '火锅', '烧烤', '烤串', '麻辣烫', '炸鸡翅', '关东煮',
            '烤冷面', '烤红薯', '糖炒栗子', '爆米花', '烤玉米', '烤茄子', '烤韭菜', '烤金针菇',
            '烤豆腐', '烤馒头', '烤面包片', '牛奶麦片', '煎饼果子', '小笼包', '法式吐司', '蒸蛋羹',
            '煎饺', '蒸饺', '烧卖', '肠粉', '糯米鸡', '粽子', '油条', '豆浆', '豆腐脑', '胡辣汤',
            '包子', '馒头', '花卷', '咸鸭蛋', '茶叶蛋', '鸡肉沙拉', '意式烩饭', '墨西哥卷饼', '希腊沙拉',
            '法式洋葱汤', '烤鸡', '烤鱼', '烤虾', '烤蔬菜', '土豆泥', '奶油汤', '蔬菜汤', '咖喱鸡',
            '红酒炖牛肉', '泰式冬阴功', '日式照烧鸡', '清蒸鲈鱼', '红烧牛腩', '清炖羊肉', '白切鸡',
            '烧鹅', '烤鸭', '清蒸石斑鱼', '红烧海参', '蒜蓉蒸扇贝', '白灼基围虾', '清蒸大闸蟹'
        ]
        
        # 图片选项
        image_options = [
            '/static/img/food/bread-1836411_1280.jpg',
            '/static/img/food/chinese-3855829_1280.jpg',
            '/static/img/food/braise-pork-1398308_1280.jpg',
            '/static/img/food/steamed-fish-3495930_1280.jpg',
            '/static/img/food/pasta-7209002_1280.jpg',
            '/static/img/food/food-3228058_1280.jpg',
            '/static/img/food/vegetarian-1141242_1280.jpg',
            '/static/img/food/chongqing-6764962_1280.jpg',
            '/static/img/food/korean-barbecue-8579177_1280.jpg',
            '/static/img/food/bread-6725352_1280.jpg',
            '/static/img/food/egg-roll-6353108_1280.jpg',
            '/static/img/food/green-dragon-vegetable-1707089_1280.jpg',
            '/static/img/food/chinese-915325_1280.jpg',
            '/static/img/food/chinese-841179_1280.jpg',
            '/static/img/food/roast-3416333_1280.jpg',
            '/static/img/food/lanzhou-6896276_1280.jpg',
            '/static/img/food/the-pork-fried-rice-made-908333_1280.jpg',
            '/static/img/food/pizza-6478478_1280.jpg',
            '/static/img/food/steak-6714964_1280.jpg',
            '/static/img/food/duck-253846_1280.jpg',
            '/static/img/food/crayfish-866400_1280.jpg',
            '/static/img/food/chicken-2097959_1280.jpg',
            '/static/img/food/chinese-5233510_1280.jpg',
            '/static/img/food/food-5983402_1280.jpg'
        ]
        
        created_count = 0
        target_count = 200
        
        while FoodItem.objects.count() < target_count:
            # 随机选择食物名称
            name = random.choice(food_names)
            
            # 检查是否已存在
            if FoodItem.objects.filter(name=name).exists():
                continue
            
            # 随机生成食物属性
            food_type = random.choice(['breakfast', 'lunch', 'dinner', 'snack'])
            cuisine = random.choice(['chinese', 'western', 'asian'])
            
            if food_type == 'breakfast':
                meal_types = ['breakfast']
                difficulty = 'easy'
                cooking_time = random.randint(5, 20)
                calories = random.randint(180, 350)
            elif food_type == 'lunch':
                meal_types = ['lunch', 'dinner']
                difficulty = random.choice(['easy', 'medium'])
                cooking_time = random.randint(15, 35)
                calories = random.randint(220, 450)
            elif food_type == 'dinner':
                meal_types = ['dinner']
                difficulty = random.choice(['medium', 'hard'])
                cooking_time = random.randint(25, 90)
                calories = random.randint(280, 520)
            else:  # snack
                meal_types = ['snack']
                difficulty = 'easy'
                cooking_time = random.randint(10, 25)
                calories = random.randint(150, 350)
            
            # 生成营养数据
            protein = round(calories * 0.15 / 4, 1)
            fat = round(calories * 0.25 / 9, 1)
            carbs = round(calories * 0.6 / 4, 1)
            fiber = round(random.uniform(1, 5), 1)
            sugar = round(random.uniform(2, 15), 1)
            sodium = random.randint(200, 1200)
            
            # 创建食物
            food = FoodItem.objects.create(
                name=name,
                description=f'{name}，适合上班族的{meal_types[0]}选择',
                meal_types=meal_types,
                cuisine=cuisine,
                difficulty=difficulty,
                cooking_time=cooking_time,
                ingredients=['主要食材', '调味料', '配菜'],
                tags=[meal_types[0], cuisine, 'office-friendly'],
                image_url=random.choice(image_options),
                calories=calories,
                protein=protein,
                fat=fat,
                carbohydrates=carbs,
                fiber=fiber,
                sugar=sugar,
                sodium=sodium,
                popularity_score=0.7,
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ 创建: {food.name} - {calories}千卡')
            )
            created_count += 1
            
            # 每创建10个食物显示一次进度
            if created_count % 10 == 0:
                current_total = FoodItem.objects.count()
                self.stdout.write(f'📊 进度: {current_total}/200')
        
        final_count = FoodItem.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 食品库扩展完成! 最终总数: {final_count}个食物')
        )
        
        self.stdout.write(f'\n📈 扩展统计:')
        self.stdout.write(f'   - 新增: {created_count} 个食物')
        self.stdout.write(f'   - 总计: {final_count} 个食物')
        self.stdout.write(f'   - 目标: 200 个食物')
        self.stdout.write(f'   - 完成度: {final_count/200*100:.1f}%')
