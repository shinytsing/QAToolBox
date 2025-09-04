from django.core.management.base import BaseCommand
from django.conf import settings
import os
from apps.tools.models import FoodItem, FoodNutrition
import re


class Command(BaseCommand):
    help = "智能匹配食物图片 - 使用更精确的匹配算法"

    def handle(self, *args, **options):
        self.stdout.write("🚀 开始智能匹配食物图片...")

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

        # 创建精确匹配字典
        precise_mapping = {
            # 中餐精确匹配
            "麻婆豆腐": ["mapo-tofu", "tofu"],
            "宫保鸡丁": ["chicken", "kung-pao"],
            "红烧肉": ["braise-pork", "pork"],
            "糖醋里脊": ["sweet-sour", "pork"],
            "鱼香肉丝": ["fish-fragrant", "pork"],
            "青椒肉丝": ["green-pepper", "pork"],
            "番茄炒蛋": ["tomato-egg", "egg"],
            "白切鸡": ["white-cut-chicken", "chicken"],
            "北京烤鸭": ["peking-duck", "duck"],
            "东坡肉": ["dongpo-pork", "pork"],
            "炸酱面": ["zhajiang-noodle", "noodle"],
            "蛋炒饭": ["fried-rice", "rice"],
            "叉烧肉": ["char-siu", "pork"],
            "烧鹅": ["roast-goose", "goose"],
            "水煮鱼": ["boiled-fish", "fish"],
            "火锅": ["hot-pot", "chinese"],
            "小龙虾": ["crayfish", "lobster"],
            "剁椒鱼头": ["fish-head", "fish"],
            "回锅肉": ["twice-cooked-pork", "pork"],
            "麻辣香锅": ["spicy-pot", "chinese"],
            # 西餐精确匹配
            "意大利面": ["pasta", "spaghetti"],
            "披萨": ["pizza"],
            "汉堡包": ["burger", "hamburger"],
            "牛排": ["steak", "beef"],
            "沙拉": ["salad"],
            "土豆泥": ["mashed-potato", "potato"],
            "炸鸡": ["fried-chicken", "chicken"],
            "三明治": ["sandwich", "bread"],
            # 日料精确匹配
            "寿司": ["sushi"],
            "拉面": ["ramen"],
            "天妇罗": ["tempura"],
            "刺身": ["sashimi"],
            "乌冬面": ["udon", "noodle"],
            "章鱼小丸子": ["takoyaki"],
            "日式烤肉": ["japanese-bbq", "yakiniku"],
            # 韩料精确匹配
            "韩式烤肉": ["korean-bbq", "barbecue"],
            "泡菜": ["kimchi"],
            "石锅拌饭": ["bibimbap", "rice"],
            "年糕": ["rice-cake", "tteok"],
            "韩式炸鸡": ["korean-fried-chicken"],
            "部队锅": ["budae-jjigae"],
            "冷面": ["cold-noodle"],
        }

        # 为FoodItem匹配图片
        self.stdout.write("\n🍽️ 开始为FoodItem匹配图片...")
        food_items = FoodItem.objects.filter(is_active=True)
        updated_count = 0

        for food_item in food_items:
            best_match = None
            best_score = 0

            # 尝试精确匹配
            if food_item.name in precise_mapping:
                keywords = precise_mapping[food_item.name]
                for image_file in image_files:
                    filename_lower = image_file.lower()
                    for keyword in keywords:
                        if keyword in filename_lower:
                            best_match = image_file
                            best_score = 100
                            break
                    if best_match:
                        break

            # 如果没有精确匹配，尝试模糊匹配
            if not best_match:
                food_name_lower = food_item.name.lower()
                for image_file in image_files:
                    filename_lower = image_file.lower()
                    score = 0

                    # 检查文件名中是否包含食物名称的关键词
                    food_keywords = re.findall(r"[\u4e00-\u9fff]+", food_name_lower)  # 中文字符
                    for keyword in food_keywords:
                        if keyword in filename_lower:
                            score += 50

                    # 检查英文关键词
                    english_keywords = {
                        "鸡": ["chicken"],
                        "牛": ["beef", "steak"],
                        "猪": ["pork"],
                        "鱼": ["fish"],
                        "虾": ["shrimp", "prawn"],
                        "面": ["noodle", "pasta"],
                        "饭": ["rice"],
                        "汤": ["soup"],
                        "烤": ["roast", "grill"],
                        "炸": ["fried"],
                        "炒": ["stir-fry"],
                    }

                    for chinese, english_list in english_keywords.items():
                        if chinese in food_name_lower:
                            for english in english_list:
                                if english in filename_lower:
                                    score += 30

                    if score > best_score:
                        best_score = score
                        best_match = image_file

            # 更新图片
            if best_match and best_score > 20:  # 只更新匹配度较高的
                image_url = f"/static/img/food/{best_match}"
                food_item.image_url = image_url
                food_item.save()
                updated_count += 1
                self.stdout.write(f"✅ {food_item.name} -> {best_match} (匹配度: {best_score})")
            else:
                self.stdout.write(f"❓ {food_item.name} - 未找到合适匹配")

        # 为FoodNutrition匹配图片
        self.stdout.write("\n🥗 开始为FoodNutrition匹配图片...")
        food_nutrition_items = FoodNutrition.objects.filter(is_active=True)
        nutrition_updated_count = 0

        for food_item in food_nutrition_items:
            best_match = None
            best_score = 0

            # 尝试精确匹配
            if food_item.name in precise_mapping:
                keywords = precise_mapping[food_item.name]
                for image_file in image_files:
                    filename_lower = image_file.lower()
                    for keyword in keywords:
                        if keyword in filename_lower:
                            best_match = image_file
                            best_score = 100
                            break
                    if best_match:
                        break

            # 模糊匹配
            if not best_match:
                food_name_lower = food_item.name.lower()
                for image_file in image_files:
                    filename_lower = image_file.lower()
                    score = 0

                    # 检查中文字符匹配
                    food_keywords = re.findall(r"[\u4e00-\u9fff]+", food_name_lower)
                    for keyword in food_keywords:
                        if keyword in filename_lower:
                            score += 50

                    # 检查英文关键词
                    english_keywords = {
                        "鸡": ["chicken"],
                        "牛": ["beef", "steak"],
                        "猪": ["pork"],
                        "鱼": ["fish"],
                        "虾": ["shrimp", "prawn"],
                        "面": ["noodle", "pasta"],
                        "饭": ["rice"],
                        "汤": ["soup"],
                        "烤": ["roast", "grill"],
                        "炸": ["fried"],
                        "炒": ["stir-fry"],
                    }

                    for chinese, english_list in english_keywords.items():
                        if chinese in food_name_lower:
                            for english in english_list:
                                if english in filename_lower:
                                    score += 30

                    if score > best_score:
                        best_score = score
                        best_match = image_file

            # 更新图片
            if best_match and best_score > 20:
                image_url = f"/static/img/food/{best_match}"
                food_item.image_url = image_url
                food_item.save()
                nutrition_updated_count += 1
                self.stdout.write(f"✅ {food_item.name} -> {best_match} (匹配度: {best_score})")
            else:
                self.stdout.write(f"❓ {food_item.name} - 未找到合适匹配")

        # 统计结果
        self.stdout.write(self.style.SUCCESS(f"\n🎉 智能匹配完成！"))
        self.stdout.write(f"📊 统计结果:")
        self.stdout.write(f"  - FoodItem更新: {updated_count}/{food_items.count()}")
        self.stdout.write(f"  - FoodNutrition更新: {nutrition_updated_count}/{food_nutrition_items.count()}")
        self.stdout.write(f"  - 总更新数量: {updated_count + nutrition_updated_count}")

        self.stdout.write(f"\n💡 提示:")
        self.stdout.write(f"  - 访问 /tools/food_photo_binding/ 进行手动精确调整")
        self.stdout.write(f"  - 使用拖拽方式可以快速重新匹配图片")
