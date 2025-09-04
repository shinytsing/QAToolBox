from django.core.management.base import BaseCommand
from django.conf import settings
import os
from apps.tools.models import FoodItem
import random


class Command(BaseCommand):
    help = "智能映射食物图片 - 根据文件名进行精确匹配"

    def handle(self, *args, **options):
        self.stdout.write("🧠 开始智能映射食物图片...")

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

        # 创建详细的图片映射字典
        detailed_mapping = {
            # 中餐
            "mapo-tofu": ["麻婆豆腐"],
            "braise-pork": ["红烧肉", "叉烧肉"],
            "chinese-": ["白切鸡", "回锅肉", "小龙虾"],
            "steamed-fish": ["剁椒鱼头", "水煮鱼"],
            "cross-bridge-tofu": ["麻婆豆腐"],
            "the-pork-fried-rice": ["叉烧肉"],
            "egg-roll": ["番茄炒蛋"],
            "chongqing": ["水煮鱼", "回锅肉"],
            "green-dragon-vegetable": ["青椒肉丝"],
            "lanzhou": ["拉面"],
            # 西餐
            "steak-": ["牛排"],
            "beef-": ["牛排"],
            "bread-": ["意大利面", "三明治"],
            "pizza-": ["披萨"],
            "pasta-": ["意大利面"],
            "pancakes": ["华夫饼"],
            "macarons": ["甜点"],
            # 日料
            "sushi-": ["寿司"],
            "ramen-": ["拉面"],
            "udon-noodles": ["乌冬面"],
            "tofu-": ["麻婆豆腐"],
            # 韩料
            "bibimbap": ["石锅拌饭"],
            "korean-barbecue": ["韩式烤肉", "部队锅"],
            "toppokki": ["韩式炒年糕"],
            "rice-": ["石锅拌饭", "蛋炒饭"],
            # 海鲜
            "seafood-": ["小龙虾", "剁椒鱼头"],
            "crayfish": ["小龙虾"],
            "shrimp-": ["小龙虾"],
            # 禽类
            "duck-": ["北京烤鸭", "烧鹅"],
            "chicken": ["白切鸡", "宫保鸡丁"],
            # 其他
            "food-": ["通用食物"],
            "eat-": ["通用食物"],
            "roast-": ["烤制食物"],
            "vegetarian-": ["素食"],
            "food-photography-": ["通用食物"],
            "food-shoot-": ["通用食物"],
            "food-and-drink-": ["通用食物"],
        }

        # 创建图片映射字典
        image_mapping = {}
        used_foods = set()

        # 智能匹配
        for image_file in image_files:
            filename_lower = image_file.lower()
            name_without_ext = os.path.splitext(image_file)[0]

            matched_food = None

            # 1. 精确匹配
            for food in food_items:
                if food.name.lower() in name_without_ext or name_without_ext in food.name.lower():
                    if food.name not in used_foods:
                        matched_food = food
                        break

            # 2. 详细映射匹配
            if not matched_food:
                for pattern, food_names in detailed_mapping.items():
                    if pattern in filename_lower:
                        for food_name in food_names:
                            for food in food_items:
                                if food.name == food_name and food.name not in used_foods:
                                    matched_food = food
                                    break
                            if matched_food:
                                break
                        if matched_food:
                            break

            # 3. 关键词匹配
            if not matched_food:
                keywords = {
                    "beef": ["牛排"],
                    "pork": ["红烧肉", "叉烧肉"],
                    "chicken": ["白切鸡", "宫保鸡丁"],
                    "fish": ["剁椒鱼头", "水煮鱼"],
                    "rice": ["石锅拌饭", "蛋炒饭"],
                    "noodle": ["拉面", "乌冬面"],
                    "bread": ["意大利面", "三明治"],
                    "pizza": ["披萨"],
                    "sushi": ["寿司"],
                    "ramen": ["拉面"],
                    "bibimbap": ["石锅拌饭"],
                    "tofu": ["麻婆豆腐"],
                    "seafood": ["小龙虾"],
                    "steak": ["牛排"],
                    "pasta": ["意大利面"],
                    "soup": ["味增汤"],
                    "salad": ["沙拉"],
                    "cake": ["甜点"],
                    "coffee": ["咖啡"],
                    "tea": ["茶"],
                    "wine": ["红酒"],
                    "beer": ["啤酒"],
                    "juice": ["果汁"],
                    "milk": ["牛奶"],
                    "egg": ["番茄炒蛋"],
                    "vegetable": ["青椒肉丝"],
                    "fruit": ["水果"],
                    "dessert": ["甜点"],
                    "snack": ["小吃"],
                    "breakfast": ["早餐"],
                    "lunch": ["午餐"],
                    "dinner": ["晚餐"],
                }

                for keyword, food_names in keywords.items():
                    if keyword in filename_lower:
                        for food_name in food_names:
                            for food in food_items:
                                if food.name == food_name and food.name not in used_foods:
                                    matched_food = food
                                    break
                            if matched_food:
                                break
                        if matched_food:
                            break

            # 4. 菜系匹配
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
                        cuisine_foods = [f for f in food_items if f.cuisine == cuisine and f.name not in used_foods]
                        if cuisine_foods:
                            matched_food = random.choice(cuisine_foods)
                            break

            if matched_food:
                image_mapping[image_file] = matched_food
                used_foods.add(matched_food.name)
                self.stdout.write(f"✅ 智能匹配: {image_file} -> {matched_food.name}")
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

        # 为没有图片的食物分配剩余图片
        remaining_images = [img for img in image_files if img not in image_mapping]
        foods_without_images = [food for food in food_items if food.name not in used_foods]

        if remaining_images and foods_without_images:
            self.stdout.write(f"🔄 为 {len(foods_without_images)} 个食物分配剩余图片...")

            # 按菜系分配
            cuisine_groups = {}
            for food in foods_without_images:
                if food.cuisine not in cuisine_groups:
                    cuisine_groups[food.cuisine] = []
                cuisine_groups[food.cuisine].append(food)

            # 为每个菜系分配相关图片
            for cuisine, foods in cuisine_groups.items():
                cuisine_images = []
                for img in remaining_images:
                    img_lower = img.lower()
                    if cuisine in img_lower or any(
                        keyword in img_lower for keyword in ["chinese", "western", "japanese", "korean"]
                    ):
                        cuisine_images.append(img)

                if cuisine_images:
                    # 随机分配
                    random.shuffle(cuisine_images)
                    random.shuffle(foods)

                    for i, food in enumerate(foods):
                        if i < len(cuisine_images):
                            image_file = cuisine_images[i]
                            image_url = f"/static/img/food/{image_file}"
                            food.image_url = image_url
                            food.save()
                            updated_count += 1
                            remaining_images.remove(image_file)
                            self.stdout.write(f"🎲 菜系分配: {image_file} -> {food.name} ({cuisine})")

            # 为剩余食物分配图片
            remaining_foods = [
                food
                for food in foods_without_images
                if not food.image_url or not food.image_url.startswith("/static/img/food/")
            ]
            if remaining_foods and remaining_images:
                random.shuffle(remaining_images)
                random.shuffle(remaining_foods)

                for i, food in enumerate(remaining_foods):
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

        self.stdout.write(self.style.SUCCESS(f"\n🎉 智能图片映射完成！"))
        self.stdout.write(f"📊 统计结果:")
        self.stdout.write(f"  - 总食物数: {total_foods}")
        self.stdout.write(f"  - 有图片的食物: {foods_with_images}")
        self.stdout.write(f"  - 图片覆盖率: {foods_with_images/total_foods*100:.1f}%")
        self.stdout.write(f"  - 智能匹配数: {len(image_mapping)}")
        self.stdout.write(f"  - 总更新数量: {updated_count}")

        # 显示各菜系的图片覆盖率
        self.stdout.write(f"\n🍽️ 各菜系图片覆盖率:")
        for cuisine_code, cuisine_name in FoodItem.CUISINE_CHOICES:
            cuisine_foods = FoodItem.objects.filter(cuisine=cuisine_code, is_active=True)
            cuisine_total = cuisine_foods.count()
            cuisine_with_images = cuisine_foods.exclude(image_url="").count()
            if cuisine_total > 0:
                coverage = cuisine_with_images / cuisine_total * 100
                self.stdout.write(f"  - {cuisine_name}: {cuisine_with_images}/{cuisine_total} ({coverage:.1f}%)")

        # 显示匹配详情
        self.stdout.write(f"\n📋 智能匹配详情:")
        for image_file, food_item in image_mapping.items():
            self.stdout.write(f"  - {image_file} -> {food_item.name} ({food_item.cuisine})")
