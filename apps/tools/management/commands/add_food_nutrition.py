from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = '为食物添加营养信息'

    def handle(self, *args, **options):
        # 食物营养信息数据
        nutrition_data = {
            '宫保鸡丁': {'calories': 320, 'protein': 25, 'fat': 18, 'carbohydrates': 15, 'fiber': 2, 'sugar': 8, 'sodium': 850},
            '麻婆豆腐': {'calories': 280, 'protein': 18, 'fat': 22, 'carbohydrates': 8, 'fiber': 3, 'sugar': 2, 'sodium': 1200},
            '红烧肉': {'calories': 450, 'protein': 28, 'fat': 35, 'carbohydrates': 5, 'fiber': 1, 'sugar': 3, 'sodium': 680},
            '糖醋里脊': {'calories': 380, 'protein': 22, 'fat': 20, 'carbohydrates': 25, 'fiber': 1, 'sugar': 15, 'sodium': 720},
            '意大利面': {'calories': 380, 'protein': 12, 'fat': 8, 'carbohydrates': 65, 'fiber': 4, 'sugar': 6, 'sodium': 680},
            '披萨': {'calories': 450, 'protein': 18, 'fat': 22, 'carbohydrates': 48, 'fiber': 3, 'sugar': 8, 'sodium': 1200},
            '汉堡包': {'calories': 520, 'protein': 25, 'fat': 28, 'carbohydrates': 42, 'fiber': 2, 'sugar': 8, 'sodium': 850},
            '牛排': {'calories': 380, 'protein': 45, 'fat': 22, 'carbohydrates': 0, 'fiber': 0, 'sugar': 0, 'sodium': 450},
            '寿司拼盘': {'calories': 280, 'protein': 25, 'fat': 8, 'carbohydrates': 35, 'fiber': 2, 'sugar': 8, 'sodium': 680},
            '拉面': {'calories': 420, 'protein': 18, 'fat': 15, 'carbohydrates': 55, 'fiber': 3, 'sugar': 8, 'sodium': 1200},
            '韩式烤肉': {'calories': 380, 'protein': 35, 'fat': 22, 'carbohydrates': 8, 'fiber': 2, 'sugar': 4, 'sodium': 680},
            '泰式咖喱': {'calories': 320, 'protein': 18, 'fat': 22, 'carbohydrates': 18, 'fiber': 4, 'sugar': 8, 'sodium': 850},
        }

        updated_count = 0
        not_found_count = 0

        for food_name, nutrition in nutrition_data.items():
            try:
                food = FoodItem.objects.get(name=food_name)
                food.calories = nutrition['calories']
                food.protein = nutrition['protein']
                food.fat = nutrition['fat']
                food.carbohydrates = nutrition['carbohydrates']
                food.fiber = nutrition['fiber']
                food.sugar = nutrition['sugar']
                food.sodium = nutrition['sodium']
                food.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 更新: {food_name} - 卡路里: {nutrition["calories"]}千卡')
                )
                updated_count += 1
                
            except FoodItem.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ 未找到: {food_name}')
                )
                not_found_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'\n📊 更新完成! 成功更新: {updated_count}个食物, 未找到: {not_found_count}个食物')
        )
