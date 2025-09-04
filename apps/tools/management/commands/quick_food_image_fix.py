from django.core.management.base import BaseCommand
from apps.tools.models import FoodItem, FoodNutrition
import os


class Command(BaseCommand):
    help = "快速修复食物图片匹配 - 手动指定精确匹配"

    def add_arguments(self, parser):
        parser.add_argument("--food", type=str, help="食物名称")
        parser.add_argument("--image", type=str, help="图片文件名")
        parser.add_argument("--list-unmatched", action="store_true", help="列出未匹配的食物")
        parser.add_argument("--list-images", action="store_true", help="列出所有可用图片")

    def handle(self, *args, **options):
        if options["list_unmatched"]:
            self.list_unmatched_foods()
        elif options["list_images"]:
            self.list_available_images()
        elif options["food"] and options["image"]:
            self.fix_single_mapping(options["food"], options["image"])
        else:
            self.show_help()

    def list_unmatched_foods(self):
        """列出未匹配或匹配度低的食物"""
        self.stdout.write("🔍 查找匹配度低的食物...")

        # 检查FoodItem
        food_items = FoodItem.objects.filter(is_active=True)
        unmatched_foods = []

        for food in food_items:
            if not food.image_url or food.image_url == "/static/img/food/default-food.svg":
                unmatched_foods.append(("FoodItem", food.name, food.cuisine))

        # 检查FoodNutrition
        food_nutrition_items = FoodNutrition.objects.filter(is_active=True)
        for food in food_nutrition_items:
            if not food.image_url or food.image_url == "/static/img/food/default-food.svg":
                unmatched_foods.append(("FoodNutrition", food.name, food.cuisine))

        if unmatched_foods:
            self.stdout.write(f"\n❌ 找到 {len(unmatched_foods)} 个未匹配的食物:")
            for model_type, name, cuisine in unmatched_foods:
                self.stdout.write(f"  - {model_type}: {name} ({cuisine})")
        else:
            self.stdout.write("✅ 所有食物都已匹配图片！")

    def list_available_images(self):
        """列出所有可用的图片文件"""
        food_images_dir = "static/img/food"
        if not os.path.exists(food_images_dir):
            self.stdout.write(self.style.ERROR("❌ 图片目录不存在"))
            return

        image_files = []
        for filename in os.listdir(food_images_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                image_files.append(filename)

        self.stdout.write(f"📸 可用图片文件 ({len(image_files)}个):")
        for i, filename in enumerate(image_files, 1):
            self.stdout.write(f"  {i:2d}. {filename}")

    def fix_single_mapping(self, food_name, image_name):
        """修复单个食物的图片匹配"""
        # 检查图片文件是否存在
        image_path = f"static/img/food/{image_name}"
        if not os.path.exists(image_path):
            self.stdout.write(self.style.ERROR(f"❌ 图片文件不存在: {image_path}"))
            return

        # 查找食物
        food_item = FoodItem.objects.filter(name=food_name, is_active=True).first()
        food_nutrition = FoodNutrition.objects.filter(name=food_name, is_active=True).first()

        if not food_item and not food_nutrition:
            self.stdout.write(self.style.ERROR(f"❌ 未找到食物: {food_name}"))
            return

        # 更新图片
        image_url = f"/static/img/food/{image_name}"

        if food_item:
            food_item.image_url = image_url
            food_item.save()
            self.stdout.write(f"✅ FoodItem: {food_name} -> {image_name}")

        if food_nutrition:
            food_nutrition.image_url = image_url
            food_nutrition.save()
            self.stdout.write(f"✅ FoodNutrition: {food_name} -> {image_name}")

    def show_help(self):
        """显示帮助信息"""
        self.stdout.write("🔧 快速食物图片修复工具")
        self.stdout.write("")
        self.stdout.write("使用方法:")
        self.stdout.write("  python manage.py quick_food_image_fix --list-unmatched    # 列出未匹配的食物")
        self.stdout.write("  python manage.py quick_food_image_fix --list-images       # 列出可用图片")
        self.stdout.write(
            '  python manage.py quick_food_image_fix --food "麻婆豆腐" --image "mapo-tofu-2570173_1280.jpg"  # 修复单个匹配'
        )
        self.stdout.write("")
        self.stdout.write("示例:")
        self.stdout.write('  python manage.py quick_food_image_fix --food "宫保鸡丁" --image "chinese-841179_1280.jpg"')
        self.stdout.write('  python manage.py quick_food_image_fix --food "白切鸡" --image "duck-2097959_1280.jpg"')
