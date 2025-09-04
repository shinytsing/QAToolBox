import os
import random

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.tools.models import FoodItem


class Command(BaseCommand):
    help = "将static/img/food目录下的图片与食物数据一一对应"

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始映射食物图片...")

        # 获取static/img/food目录下的所有图片文件
        food_images_dir = os.path.join(settings.STATIC_ROOT, "img", "food")
        if not os.path.exists(food_images_dir):
            food_images_dir = os.path.join(settings.BASE_DIR, "static", "img", "food")

        if not os.path.exists(food_images_dir):
            self.stdout.write(self.style.ERROR(f"❌ 食物图片目录不存在: {food_images_dir}"))
            return

        # 获取所有图片文件
        image_files = []
        for filename in os.listdir(food_images_dir):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                image_files.append(filename)

        self.stdout.write(f"📸 找到 {len(image_files)} 个图片文件")

        # 获取所有食物数据
        food_items = list(FoodItem.objects.filter(is_active=True))
        self.stdout.write(f"🍽️ 找到 {len(food_items)} 个活跃食物")

        if len(food_items) == 0:
            self.stdout.write(self.style.WARNING("⚠️ 没有找到食物数据，请先运行食物数据初始化命令"))
            return

        # 创建图片映射字典
        image_mapping = {}

        # 根据文件名智能匹配食物
        for image_file in image_files:
            filename_lower = image_file.lower()

            # 移除文件扩展名
            name_without_ext = os.path.splitext(image_file)[0]

            # 尝试匹配食物名称
            matched_food = None

            # 1. 精确匹配
            for food in food_items:
                if food.name.lower() in name_without_ext or name_without_ext in food.name.lower():
                    matched_food = food
                    break

            # 2. 关键词匹配
            if not matched_food:
                keywords = {
                    "beef": ["牛肉", "牛排", "牛肉面"],
                    "pork": ["猪肉", "红烧肉", "叉烧"],
                    "chicken": ["鸡肉", "鸡丁", "白切鸡"],
                    "fish": ["鱼", "鱼头", "水煮鱼"],
                    "rice": ["米饭", "炒饭", "拌饭"],
                    "noodle": ["面条", "拉面", "乌冬面"],
                    "bread": ["面包", "吐司", "华夫饼"],
                    "pizza": ["披萨"],
                    "sushi": ["寿司"],
                    "ramen": ["拉面"],
                    "bibimbap": ["拌饭", "石锅拌饭"],
                    "tofu": ["豆腐", "麻婆豆腐"],
                    "seafood": ["海鲜", "虾", "蟹"],
                    "steak": ["牛排"],
                    "pasta": ["意大利面", "意面"],
                    "soup": ["汤", "味增汤"],
                    "salad": ["沙拉"],
                    "cake": ["蛋糕", "甜点"],
                    "coffee": ["咖啡"],
                    "tea": ["茶"],
                    "wine": ["酒", "红酒"],
                    "beer": ["啤酒"],
                    "juice": ["果汁"],
                    "milk": ["牛奶"],
                    "egg": ["鸡蛋", "蛋"],
                    "vegetable": ["蔬菜", "青菜"],
                    "fruit": ["水果"],
                    "dessert": ["甜点", "蛋糕"],
                    "snack": ["零食", "小吃"],
                    "breakfast": ["早餐"],
                    "lunch": ["午餐"],
                    "dinner": ["晚餐"],
                    "chinese": ["中餐", "中国菜"],
                    "western": ["西餐", "西式"],
                    "japanese": ["日料", "日本菜"],
                    "korean": ["韩料", "韩国菜"],
                    "thai": ["泰餐", "泰国菜"],
                    "italian": ["意式", "意大利"],
                    "french": ["法式", "法国"],
                    "mexican": ["墨西哥"],
                    "indian": ["印度"],
                }

                for keyword, food_names in keywords.items():
                    if keyword in filename_lower:
                        for food in food_items:
                            if any(name in food.name for name in food_names):
                                matched_food = food
                                break
                        if matched_food:
                            break

            # 3. 菜系匹配
            if not matched_food:
                cuisine_keywords = {
                    "chinese": ["chinese", "china"],
                    "western": ["western", "bread", "steak", "pizza"],
                    "japanese": ["japanese", "japan", "sushi", "ramen"],
                    "korean": ["korean", "korea", "bibimbap"],
                    "thai": ["thai", "thailand"],
                    "italian": ["italian", "italy", "pasta"],
                    "french": ["french", "france"],
                    "mexican": ["mexican", "mexico"],
                }

                for cuisine, keywords in cuisine_keywords.items():
                    if any(keyword in filename_lower for keyword in keywords):
                        cuisine_foods = [f for f in food_items if f.cuisine == cuisine]
                        if cuisine_foods:
                            matched_food = random.choice(cuisine_foods)
                            break

            if matched_food:
                image_mapping[image_file] = matched_food
                self.stdout.write(f"✅ 匹配: {image_file} -> {matched_food.name}")
            else:
                self.stdout.write(f"❓ 未匹配: {image_file}")

        # 更新食物数据的图片URL
        updated_count = 0
        for image_file, food_item in image_mapping.items():
            # 构建图片URL
            image_url = f"/static/img/food/{image_file}"

            # 更新食物数据
            food_item.image_url = image_url
            food_item.save()
            updated_count += 1

        # 为没有图片的食物随机分配剩余图片
        remaining_images = [img for img in image_files if img not in image_mapping]
        foods_without_images = [
            food for food in food_items if not food.image_url or not food.image_url.startswith("/static/img/food/")
        ]

        if remaining_images and foods_without_images:
            self.stdout.write(f"🔄 为 {len(foods_without_images)} 个食物分配剩余图片...")

            # 随机分配
            random.shuffle(remaining_images)
            random.shuffle(foods_without_images)

            for i, food in enumerate(foods_without_images):
                if i < len(remaining_images):
                    image_file = remaining_images[i]
                    image_url = f"/static/img/food/{image_file}"
                    food.image_url = image_url
                    food.save()
                    updated_count += 1
                    self.stdout.write(f"🎲 随机分配: {image_file} -> {food.name}")

        # 统计结果
        total_foods = FoodItem.objects.filter(is_active=True).count()
        foods_with_images = FoodItem.objects.filter(is_active=True).exclude(image_url="").count()

        self.stdout.write(self.style.SUCCESS(f"\n🎉 图片映射完成！"))
        self.stdout.write(f"📊 统计结果:")
        self.stdout.write(f"  - 总食物数: {total_foods}")
        self.stdout.write(f"  - 有图片的食物: {foods_with_images}")
        self.stdout.write(f"  - 图片覆盖率: {foods_with_images/total_foods*100:.1f}%")
        self.stdout.write(f"  - 更新数量: {updated_count}")

        # 显示各菜系的图片覆盖率
        self.stdout.write(f"\n🍽️ 各菜系图片覆盖率:")
        for cuisine_code, cuisine_name in FoodItem.CUISINE_CHOICES:
            cuisine_foods = FoodItem.objects.filter(cuisine=cuisine_code, is_active=True)
            cuisine_total = cuisine_foods.count()
            cuisine_with_images = cuisine_foods.exclude(image_url="").count()
            if cuisine_total > 0:
                coverage = cuisine_with_images / cuisine_total * 100
                self.stdout.write(f"  - {cuisine_name}: {cuisine_with_images}/{cuisine_total} ({coverage:.1f}%)")
