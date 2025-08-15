from django.core.management.base import BaseCommand
from apps.tools.services.deepseek_food_images import get_food_image_coverage, DEEPSEEK_FOOD_IMAGES
from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = '更新食物随机器使用DeepSeek图片数据，确保食物名和图片一致'

    def handle(self, *args, **options):
        self.stdout.write('🖼️ 开始更新食物图片数据...')
        
        # 获取图片覆盖率统计
        coverage_stats = get_food_image_coverage()
        
        self.stdout.write(f'📊 图片覆盖率统计:')
        self.stdout.write(f'   总食物数量: {coverage_stats["total_foods"]}')
        self.stdout.write(f'   有图片的食物: {coverage_stats["covered_foods"]}')
        self.stdout.write(f'   无图片的食物: {coverage_stats["uncovered_foods"]}')
        self.stdout.write(f'   图片覆盖率: {coverage_stats["coverage_rate"]:.1f}%')
        
        # 显示有图片的食物
        if coverage_stats["covered_foods"] > 0:
            self.stdout.write(f'\n✅ 有图片的食物 ({coverage_stats["covered_foods"]}个):')
            for food_name in coverage_stats["covered_food_names"]:
                image_path = DEEPSEEK_FOOD_IMAGES[food_name]
                self.stdout.write(f'   - {food_name} -> {image_path}')
        
        # 显示无图片的食物
        if coverage_stats["uncovered_foods"] > 0:
            self.stdout.write(f'\n⚠️ 无图片的食物 ({coverage_stats["uncovered_foods"]}个):')
            for food_name in coverage_stats["uncovered_food_names"]:
                self.stdout.write(f'   - {food_name}')
        
        # 更新数据库中的图片URL
        self.stdout.write(f'\n🔄 开始更新数据库中的图片URL...')
        
        updated_count = 0
        for food_name, image_path in DEEPSEEK_FOOD_IMAGES.items():
            try:
                food = FoodItem.objects.get(name=food_name)
                food.image_url = image_path
                food.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ 更新: {food_name} -> {image_path}')
                )
                updated_count += 1
            except FoodItem.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ 未找到食物: {food_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 更新完成! 成功更新: {updated_count}个食物的图片URL')
        )
        
        # 验证更新结果
        self.stdout.write(f'\n🔍 验证更新结果...')
        foods_with_images = FoodItem.objects.filter(is_active=True, image_url__isnull=False).exclude(image_url='')
        self.stdout.write(f'   有图片URL的食物: {foods_with_images.count()}')
        self.stdout.write(f'   图片URL覆盖率: {(foods_with_images.count() / coverage_stats["total_foods"]) * 100:.1f}%')
        
        # 显示一些示例
        self.stdout.write(f'\n📸 图片URL示例:')
        sample_foods = foods_with_images[:5]
        for food in sample_foods:
            self.stdout.write(f'   - {food.name}: {food.image_url}')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 DeepSeek图片数据更新完成!')
        )
