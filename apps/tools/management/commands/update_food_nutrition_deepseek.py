from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = '使用DeepSeek数据为所有食物添加完整的营养信息'

    def handle(self, *args, **options):
        # 基于DeepSeek数据的完整食物营养信息
        nutrition_data = {
            # 中餐
            '宫保鸡丁': {'calories': 320, 'protein': 25, 'fat': 18, 'carbohydrates': 15, 'fiber': 2, 'sugar': 8, 'sodium': 850},
            '麻婆豆腐': {'calories': 280, 'protein': 18, 'fat': 22, 'carbohydrates': 8, 'fiber': 3, 'sugar': 2, 'sodium': 1200},
            '红烧肉': {'calories': 450, 'protein': 28, 'fat': 35, 'carbohydrates': 5, 'fiber': 1, 'sugar': 3, 'sodium': 680},
            '糖醋里脊': {'calories': 380, 'protein': 22, 'fat': 20, 'carbohydrates': 25, 'fiber': 1, 'sugar': 15, 'sodium': 720},
            '鱼香肉丝': {'calories': 290, 'protein': 20, 'fat': 16, 'carbohydrates': 18, 'fiber': 2, 'sugar': 10, 'sodium': 890},
            '回锅肉': {'calories': 420, 'protein': 25, 'fat': 32, 'carbohydrates': 8, 'fiber': 2, 'sugar': 4, 'sodium': 950},
            '水煮鱼': {'calories': 310, 'protein': 35, 'fat': 18, 'carbohydrates': 5, 'fiber': 2, 'sugar': 2, 'sodium': 1100},
            '白切鸡': {'calories': 280, 'protein': 35, 'fat': 15, 'carbohydrates': 2, 'fiber': 0, 'sugar': 1, 'sodium': 450},
            '叉烧肉': {'calories': 380, 'protein': 25, 'fat': 28, 'carbohydrates': 12, 'fiber': 1, 'sugar': 8, 'sodium': 1200},
            '北京烤鸭': {'calories': 450, 'protein': 35, 'fat': 30, 'carbohydrates': 8, 'fiber': 1, 'sugar': 2, 'sodium': 680},
            '炸酱面': {'calories': 420, 'protein': 18, 'fat': 15, 'carbohydrates': 55, 'fiber': 4, 'sugar': 8, 'sodium': 1200},
            '东坡肉': {'calories': 520, 'protein': 30, 'fat': 42, 'carbohydrates': 6, 'fiber': 1, 'sugar': 4, 'sodium': 850},
            '剁椒鱼头': {'calories': 280, 'protein': 32, 'fat': 16, 'carbohydrates': 5, 'fiber': 2, 'sugar': 2, 'sodium': 1100},
            '青椒肉丝': {'calories': 260, 'protein': 22, 'fat': 18, 'carbohydrates': 8, 'fiber': 2, 'sugar': 3, 'sodium': 680},
            '番茄炒蛋': {'calories': 220, 'protein': 15, 'fat': 16, 'carbohydrates': 8, 'fiber': 2, 'sugar': 5, 'sodium': 450},
            '蛋炒饭': {'calories': 380, 'protein': 12, 'fat': 15, 'carbohydrates': 55, 'fiber': 2, 'sugar': 3, 'sodium': 680},
            '小龙虾': {'calories': 180, 'protein': 28, 'fat': 8, 'carbohydrates': 2, 'fiber': 0, 'sugar': 1, 'sodium': 450},
            '火锅': {'calories': 350, 'protein': 25, 'fat': 22, 'carbohydrates': 15, 'fiber': 4, 'sugar': 5, 'sodium': 1200},
            '烧鹅': {'calories': 380, 'protein': 32, 'fat': 28, 'carbohydrates': 2, 'fiber': 0, 'sugar': 1, 'sodium': 680},
            '石锅拌饭': {'calories': 420, 'protein': 18, 'fat': 22, 'carbohydrates': 45, 'fiber': 4, 'sugar': 8, 'sodium': 850},
            '麻辣香锅': {'calories': 380, 'protein': 25, 'fat': 28, 'carbohydrates': 15, 'fiber': 3, 'sugar': 6, 'sodium': 1200},
            
            # 西餐
            '意大利面': {'calories': 380, 'protein': 12, 'fat': 8, 'carbohydrates': 65, 'fiber': 4, 'sugar': 6, 'sodium': 680},
            '披萨': {'calories': 450, 'protein': 18, 'fat': 22, 'carbohydrates': 48, 'fiber': 3, 'sugar': 8, 'sodium': 1200},
            '汉堡包': {'calories': 520, 'protein': 25, 'fat': 28, 'carbohydrates': 42, 'fiber': 2, 'sugar': 8, 'sodium': 850},
            '牛排': {'calories': 380, 'protein': 45, 'fat': 22, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 450},
            '三明治': {'calories': 280, 'protein': 15, 'fat': 12, 'carbohydrates': 32, 'fiber': 3, 'sugar': 5, 'sodium': 680},
            '沙拉': {'calories': 120, 'protein': 8, 'fat': 8, 'carbohydrates': 12, 'fiber': 4, 'sugar': 6, 'sodium': 450},
            '土豆泥': {'calories': 180, 'protein': 4, 'fat': 8, 'carbohydrates': 28, 'fiber': 2, 'sugar': 2, 'sodium': 450},
            
            # 日料
            '寿司': {'calories': 280, 'protein': 25, 'fat': 8, 'carbohydrates': 35, 'fiber': 2, 'sugar': 8, 'sodium': 680},
            '拉面': {'calories': 420, 'protein': 18, 'fat': 15, 'carbohydrates': 55, 'fiber': 3, 'sugar': 8, 'sodium': 1200},
            '天妇罗': {'calories': 380, 'protein': 12, 'fat': 25, 'carbohydrates': 32, 'fiber': 2, 'sugar': 4, 'sodium': 850},
            '刺身': {'calories': 120, 'protein': 25, 'fat': 2, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 450},
            '乌冬面': {'calories': 380, 'protein': 12, 'fat': 8, 'carbohydrates': 65, 'fiber': 3, 'sugar': 6, 'sodium': 1200},
            '日式烤肉': {'calories': 320, 'protein': 35, 'fat': 18, 'carbohydrates': 8, 'fiber': 2, 'sugar': 4, 'sodium': 680},
            '章鱼小丸子': {'calories': 280, 'protein': 15, 'fat': 18, 'carbohydrates': 22, 'fiber': 2, 'sugar': 6, 'sodium': 850},
            
            # 韩料
            '韩式烤肉': {'calories': 380, 'protein': 35, 'fat': 22, 'carbohydrates': 8, 'fiber': 2, 'sugar': 4, 'sodium': 680},
            '韩式炸鸡': {'calories': 420, 'protein': 25, 'fat': 28, 'carbohydrates': 22, 'fiber': 2, 'sugar': 8, 'sodium': 850},
            '泡菜': {'calories': 80, 'protein': 4, 'fat': 2, 'carbohydrates': 12, 'fiber': 3, 'sugar': 4, 'sodium': 1200},
            '部队锅': {'calories': 380, 'protein': 22, 'fat': 25, 'carbohydrates': 18, 'fiber': 3, 'sugar': 6, 'sodium': 1200},
            
            # 其他
            '冷面': {'calories': 280, 'protein': 8, 'fat': 4, 'carbohydrates': 52, 'fiber': 2, 'sugar': 8, 'sodium': 680},
            '年糕': {'calories': 220, 'protein': 4, 'fat': 2, 'carbohydrates': 45, 'fiber': 1, 'sugar': 12, 'sodium': 450},
            '炸鸡': {'calories': 380, 'protein': 25, 'fat': 28, 'carbohydrates': 15, 'fiber': 1, 'sugar': 4, 'sodium': 850},
        }

        updated_count = 0
        not_found_count = 0
        not_found_foods = []

        # 获取所有活跃的食物
        all_foods = FoodItem.objects.filter(is_active=True)
        
        self.stdout.write(f'📊 开始更新营养信息，共找到 {all_foods.count()} 个活跃食物')
        
        for food in all_foods:
            if food.name in nutrition_data:
                nutrition = nutrition_data[food.name]
                food.calories = nutrition['calories']
                food.protein = nutrition['protein']
                food.fat = nutrition['fat']
                food.carbohydrates = nutrition['carbohydrates']
                food.fiber = nutrition['fiber']
                food.sugar = nutrition['sugar']
                food.sodium = nutrition['sodium']
                food.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 更新: {food.name} - {nutrition["calories"]}千卡')
                )
                updated_count += 1
            else:
                not_found_foods.append(food.name)
                not_found_count += 1

        # 显示未找到营养信息的食物
        if not_found_foods:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️ 以下 {len(not_found_foods)} 个食物未找到营养信息:')
            )
            for food_name in not_found_foods:
                self.stdout.write(f'   - {food_name}')

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 更新完成! 成功更新: {updated_count}个食物, 未找到: {not_found_count}个食物')
        )
        
        # 统计营养信息覆盖率
        coverage_rate = (updated_count / all_foods.count()) * 100
        self.stdout.write(
            self.style.SUCCESS(f'📈 营养信息覆盖率: {coverage_rate:.1f}%')
        )
