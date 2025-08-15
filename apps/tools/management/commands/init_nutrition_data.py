from django.core.management.base import BaseCommand
from apps.tools.models import FoodDatabase


class Command(BaseCommand):
    help = '初始化健身营养系统的食物数据库'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化食物数据库...')
        
        # 基础食物数据
        foods_data = [
            # 蛋白质类
            {
                'name': '鸡胸肉',
                'category': '蛋白质',
                'calories_per_100g': 165,
                'protein_per_100g': 31,
                'carbs_per_100g': 0,
                'fat_per_100g': 3.6,
                'fiber_per_100g': 0,
                'is_vegetarian': False,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '三文鱼',
                'category': '蛋白质',
                'calories_per_100g': 208,
                'protein_per_100g': 25,
                'carbs_per_100g': 0,
                'fat_per_100g': 12,
                'fiber_per_100g': 0,
                'is_vegetarian': False,
                'is_gluten_free': True,
                'allergens': ['seafood']
            },
            {
                'name': '鸡蛋',
                'category': '蛋白质',
                'calories_per_100g': 155,
                'protein_per_100g': 13,
                'carbs_per_100g': 1.1,
                'fat_per_100g': 11,
                'fiber_per_100g': 0,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['eggs']
            },
            {
                'name': '希腊酸奶',
                'category': '蛋白质',
                'calories_per_100g': 59,
                'protein_per_100g': 10,
                'carbs_per_100g': 3.6,
                'fat_per_100g': 0.4,
                'fiber_per_100g': 0,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['milk']
            },
            {
                'name': '豆腐',
                'category': '蛋白质',
                'calories_per_100g': 76,
                'protein_per_100g': 8,
                'carbs_per_100g': 1.9,
                'fat_per_100g': 4.8,
                'fiber_per_100g': 0.3,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['soy']
            },
            
            # 碳水类
            {
                'name': '燕麦',
                'category': '碳水',
                'calories_per_100g': 389,
                'protein_per_100g': 17,
                'carbs_per_100g': 66,
                'fat_per_100g': 6.9,
                'fiber_per_100g': 10.6,
                'is_vegetarian': True,
                'is_gluten_free': False,
                'allergens': ['wheat']
            },
            {
                'name': '红薯',
                'category': '碳水',
                'calories_per_100g': 86,
                'protein_per_100g': 1.6,
                'carbs_per_100g': 20,
                'fat_per_100g': 0.1,
                'fiber_per_100g': 3,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '糙米',
                'category': '碳水',
                'calories_per_100g': 111,
                'protein_per_100g': 2.6,
                'carbs_per_100g': 23,
                'fat_per_100g': 0.9,
                'fiber_per_100g': 1.8,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '香蕉',
                'category': '碳水',
                'calories_per_100g': 89,
                'protein_per_100g': 1.1,
                'carbs_per_100g': 23,
                'fat_per_100g': 0.3,
                'fiber_per_100g': 2.6,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '蓝莓',
                'category': '碳水',
                'calories_per_100g': 57,
                'protein_per_100g': 0.7,
                'carbs_per_100g': 14,
                'fat_per_100g': 0.3,
                'fiber_per_100g': 2.4,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            
            # 脂肪类
            {
                'name': '牛油果',
                'category': '脂肪',
                'calories_per_100g': 160,
                'protein_per_100g': 2,
                'carbs_per_100g': 9,
                'fat_per_100g': 15,
                'fiber_per_100g': 6.7,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '坚果（杏仁）',
                'category': '脂肪',
                'calories_per_100g': 579,
                'protein_per_100g': 21,
                'carbs_per_100g': 22,
                'fat_per_100g': 50,
                'fiber_per_100g': 12.5,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['nuts']
            },
            {
                'name': '橄榄油',
                'category': '脂肪',
                'calories_per_100g': 884,
                'protein_per_100g': 0,
                'carbs_per_100g': 0,
                'fat_per_100g': 100,
                'fiber_per_100g': 0,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '奇亚籽',
                'category': '脂肪',
                'calories_per_100g': 486,
                'protein_per_100g': 17,
                'carbs_per_100g': 42,
                'fat_per_100g': 31,
                'fiber_per_100g': 34.4,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            
            # 蔬菜类
            {
                'name': '西兰花',
                'category': '蔬菜',
                'calories_per_100g': 34,
                'protein_per_100g': 2.8,
                'carbs_per_100g': 7,
                'fat_per_100g': 0.4,
                'fiber_per_100g': 2.6,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '菠菜',
                'category': '蔬菜',
                'calories_per_100g': 23,
                'protein_per_100g': 2.9,
                'carbs_per_100g': 3.6,
                'fat_per_100g': 0.4,
                'fiber_per_100g': 2.2,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            {
                'name': '胡萝卜',
                'category': '蔬菜',
                'calories_per_100g': 41,
                'protein_per_100g': 0.9,
                'carbs_per_100g': 10,
                'fat_per_100g': 0.2,
                'fiber_per_100g': 2.8,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': []
            },
            
            # 补充剂
            {
                'name': '蛋白粉（乳清）',
                'category': '补充剂',
                'calories_per_100g': 352,
                'protein_per_100g': 80,
                'carbs_per_100g': 7,
                'fat_per_100g': 3,
                'fiber_per_100g': 0,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['milk']
            },
            {
                'name': '蛋白粉（植物）',
                'category': '补充剂',
                'calories_per_100g': 370,
                'protein_per_100g': 75,
                'carbs_per_100g': 8,
                'fat_per_100g': 4,
                'fiber_per_100g': 2,
                'is_vegetarian': True,
                'is_gluten_free': True,
                'allergens': ['soy']
            }
        ]
        
        # 创建食物记录
        created_count = 0
        for food_data in foods_data:
            food, created = FoodDatabase.objects.get_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'创建食物: {food.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'食物数据库初始化完成！共创建 {created_count} 个新食物记录。'
            )
        )
