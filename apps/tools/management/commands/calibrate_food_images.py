from django.core.management.base import BaseCommand
from apps.tools.services.food_image_mapping import (
    update_food_images_in_database,
    get_image_coverage_stats,
    get_food_image,
    ACCURATE_FOOD_IMAGES,
)


class Command(BaseCommand):
    help = "校准食品图片路径，确保所有食品都有正确的图片"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="强制更新所有图片路径",
        )
        parser.add_argument(
            "--show-stats",
            action="store_true",
            help="显示图片覆盖率统计",
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 开始校准食品图片路径...")

        # 显示校准前的统计
        if options["show_stats"]:
            self.show_image_stats("校准前")

        # 更新数据库中的图片路径
        result = update_food_images_in_database()

        self.stdout.write(f"✅ 图片校准完成!")
        self.stdout.write(f'   - 更新了 {result["updated"]} 个食品的图片')
        self.stdout.write(f'   - 未找到匹配的: {result["not_found"]} 个')
        self.stdout.write(f'   - 总计: {result["total"]} 个食品')

        # 显示校准后的统计
        if options["show_stats"]:
            self.show_image_stats("校准后")

        # 显示精确匹配的食品
        self.stdout.write(f"\n📋 精确匹配的食品 ({len(ACCURATE_FOOD_IMAGES)}个):")
        for i, food_name in enumerate(sorted(ACCURATE_FOOD_IMAGES.keys()), 1):
            self.stdout.write(f"   {i:2d}. {food_name}")
            if i % 10 == 0:
                self.stdout.write("")  # 每10个换行

        self.stdout.write(f"\n🎯 校准特色:")
        self.stdout.write(f"   - 使用准确的图片映射")
        self.stdout.write(f"   - 支持模糊匹配")
        self.stdout.write(f"   - 提供备用图片")
        self.stdout.write(f"   - 为图像识别功能做准备")

    def show_image_stats(self, prefix):
        """显示图片统计信息"""
        stats = get_image_coverage_stats()

        self.stdout.write(f"\n📊 {prefix}图片覆盖率统计:")
        self.stdout.write(f'   - 总食品数: {stats["total_foods"]}')
        self.stdout.write(f'   - 有图片的: {stats["foods_with_images"]}')
        self.stdout.write(f'   - 精确匹配的: {stats["foods_with_accurate_images"]}')
        self.stdout.write(f'   - 图片覆盖率: {stats["image_coverage"]}%')
        self.stdout.write(f'   - 精确覆盖率: {stats["accurate_coverage"]}%')
