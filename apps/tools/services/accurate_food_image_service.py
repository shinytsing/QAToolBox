import json
import random
import time
from typing import Dict, List, Optional

from django.conf import settings

import requests


class AccurateFoodImageService:
    """准确食物图片服务 - 使用多个免费API确保图片与食物一一对应"""

    def __init__(self):
        # 免费图片API配置
        self.pexels_api_key = getattr(settings, "PEXELS_API_KEY", None)
        self.pixabay_api_key = getattr(settings, "PIXABAY_API_KEY", None)
        self.unsplash_access_key = getattr(settings, "UNSPLASH_ACCESS_KEY", None)

        # 导入全面的食物图片映射
        from .comprehensive_food_images import get_food_image, get_food_images_by_cuisine, get_image_statistics

        # 精确的食物图片映射 - 使用全面的图片映射
        self.accurate_food_images = {}
        self.comprehensive_images = get_food_images_by_cuisine("chinese")
        self.accurate_food_images.update(self.comprehensive_images)

        # 保存导入的函数引用
        self.get_food_image = get_food_image

        # 备用图片池 - 按菜系分类
        self.fallback_images_by_cuisine = {
            "chinese": [
                "https://images.pexels.com/photos/699953/pexels-photo-699953.jpeg?w=500",
                "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg?w=500",
                "https://images.pexels.com/photos/884596/pexels-photo-884596.jpeg?w=500",
            ],
            "western": [
                "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg?w=500",
                "https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=500",
                "https://images.pexels.com/photos/3535383/pexels-photo-3535383.jpeg?w=500",
            ],
            "japanese": [
                "https://images.pexels.com/photos/2097090/pexels-photo-2097090.jpeg?w=500",
                "https://images.pexels.com/photos/884596/pexels-photo-884596.jpeg?w=500",
            ],
            "korean": [
                "https://images.pexels.com/photos/3535383/pexels-photo-3535383.jpeg?w=500",
                "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg?w=500",
            ],
            "thai": [
                "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg?w=500",
                "https://images.pexels.com/photos/884596/pexels-photo-884596.jpeg?w=500",
            ],
            "default": [
                "https://images.pexels.com/photos/699953/pexels-photo-699953.jpeg?w=500",
                "https://images.pexels.com/photos/1624487/pexels-photo-1624487.jpeg?w=500",
                "https://images.pexels.com/photos/1639557/pexels-photo-1639557.jpeg?w=500",
            ],
        }

    def get_accurate_food_image(self, food_name: str, cuisine: str = "chinese") -> str:
        """获取准确的食物图片URL"""
        # 使用全面的图片映射服务
        return self.get_food_image(food_name, cuisine)

    def search_pexels_image(self, query: str) -> Optional[str]:
        """使用Pexels API搜索食物图片"""
        try:
            if not self.pexels_api_key:
                return None

            url = "https://api.pexels.com/v1/search"
            params = {"query": f"{query} food dish", "per_page": 1, "orientation": "landscape"}
            headers = {"Authorization": self.pexels_api_key}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["photos"]:
                    return data["photos"][0]["src"]["medium"]

            return None
        except Exception as e:
            print(f"Pexels API error: {e}")
            return None

    def search_pixabay_image(self, query: str) -> Optional[str]:
        """使用Pixabay API搜索食物图片"""
        try:
            if not self.pixabay_api_key:
                return None

            url = "https://pixabay.com/api/"
            params = {"key": self.pixabay_api_key, "q": f"{query} food dish", "per_page": 1, "orientation": "horizontal"}

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["hits"]:
                    return data["hits"][0]["webformatURL"]

            return None
        except Exception as e:
            print(f"Pixabay API error: {e}")
            return None

    def search_unsplash_image(self, query: str) -> Optional[str]:
        """使用Unsplash API搜索食物图片"""
        try:
            if not self.unsplash_access_key:
                return None

            url = "https://api.unsplash.com/search/photos"
            params = {"query": f"{query} food dish", "per_page": 1, "orientation": "landscape"}
            headers = {"Authorization": f"Client-ID {self.unsplash_access_key}"}

            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data["results"]:
                    return data["results"][0]["urls"]["regular"]

            return None
        except Exception as e:
            print(f"Unsplash API error: {e}")
            return None

    def get_deepseek_food_description(self, food_name: str, cuisine: str) -> str:
        """使用DeepSeek生成食物描述"""
        # 这里可以集成DeepSeek API
        # 暂时返回基于菜系的模板描述
        descriptions = {
            "chinese": f"{food_name}，经典中餐，口感丰富，营养美味，深受欢迎的传统美食",
            "western": f"{food_name}，西式美食，精致可口，营养均衡，现代烹饪艺术的体现",
            "japanese": f"{food_name}，日式料理，精致美味，健康营养，体现日本饮食文化的精髓",
            "korean": f"{food_name}，韩式美食，口味独特，营养丰富，展现韩国传统与现代的完美结合",
            "thai": f"{food_name}，泰式料理，酸辣开胃，风味独特，充满东南亚热带风情",
            "italian": f"{food_name}，意式美食，传统经典，口感丰富，地中海饮食文化的代表",
            "french": f"{food_name}，法式料理，精致优雅，味道醇厚，体现法国烹饪艺术的精髓",
            "indian": f"{food_name}，印度美食，香料丰富，口味浓郁，展现印度多元文化的魅力",
            "mexican": f"{food_name}，墨西哥美食，色彩丰富，味道独特，充满拉丁美洲的热情",
        }

        return descriptions.get(cuisine, f"{food_name}，美味佳肴，营养丰富，值得品尝的美食")

    def expand_food_variants(self, base_foods: List[Dict]) -> List[Dict]:
        """扩展食物变体，确保每个变体都有独特的图片"""
        expanded_foods = []

        for food in base_foods:
            # 添加原始食物
            expanded_foods.append(food)

            # 根据菜系添加变体
            if food["cuisine"] == "chinese":
                # 中餐变体
                variants = [
                    {"name": f"{food['name']}（微辣）", "tags": food["tags"] + ["mild_spicy"], "difficulty": "easy"},
                    {"name": f"{food['name']}（特辣）", "tags": food["tags"] + ["extra_spicy"], "difficulty": "hard"},
                    {"name": f"{food['name']}（清淡）", "tags": food["tags"] + ["light"], "difficulty": "easy"},
                    {"name": f"{food['name']}（经典）", "tags": food["tags"] + ["classic"], "difficulty": "medium"},
                ]

                for variant in variants:
                    variant_food = food.copy()
                    variant_food["name"] = variant["name"]
                    variant_food["tags"] = variant["tags"]
                    variant_food["difficulty"] = variant["difficulty"]
                    variant_food["image_url"] = self.get_accurate_food_image(variant["name"], food["cuisine"])
                    variant_food["description"] = self.get_deepseek_food_description(variant["name"], food["cuisine"])
                    expanded_foods.append(variant_food)

            elif food["cuisine"] == "western":
                # 西餐变体
                variants = [
                    {"name": f"{food['name']}（经典）", "tags": food["tags"] + ["classic"], "difficulty": "medium"},
                    {"name": f"{food['name']}（创新）", "tags": food["tags"] + ["innovative"], "difficulty": "hard"},
                    {"name": f"{food['name']}（健康）", "tags": food["tags"] + ["healthy"], "difficulty": "easy"},
                    {"name": f"{food['name']}（豪华）", "tags": food["tags"] + ["premium"], "difficulty": "hard"},
                ]

                for variant in variants:
                    variant_food = food.copy()
                    variant_food["name"] = variant["name"]
                    variant_food["tags"] = variant["tags"]
                    variant_food["difficulty"] = variant["difficulty"]
                    variant_food["image_url"] = self.get_accurate_food_image(variant["name"], food["cuisine"])
                    variant_food["description"] = self.get_deepseek_food_description(variant["name"], food["cuisine"])
                    expanded_foods.append(variant_food)

            elif food["cuisine"] in ["japanese", "korean", "thai"]:
                # 亚洲菜系变体
                variants = [
                    {"name": f"{food['name']}（传统）", "tags": food["tags"] + ["traditional"], "difficulty": "medium"},
                    {"name": f"{food['name']}（现代）", "tags": food["tags"] + ["modern"], "difficulty": "medium"},
                    {"name": f"{food['name']}（精致）", "tags": food["tags"] + ["elegant"], "difficulty": "hard"},
                ]

                for variant in variants:
                    variant_food = food.copy()
                    variant_food["name"] = variant["name"]
                    variant_food["tags"] = variant["tags"]
                    variant_food["difficulty"] = variant["difficulty"]
                    variant_food["image_url"] = self.get_accurate_food_image(variant["name"], food["cuisine"])
                    variant_food["description"] = self.get_deepseek_food_description(variant["name"], food["cuisine"])
                    expanded_foods.append(variant_food)

        return expanded_foods

    def validate_image_url(self, image_url: str) -> bool:
        """验证图片URL是否有效"""
        try:
            response = requests.head(image_url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_food_statistics(self, foods: List[Dict]) -> Dict:
        """获取食物数据统计"""
        stats = {
            "total_foods": len(foods),
            "cuisine_distribution": {},
            "meal_type_distribution": {},
            "difficulty_distribution": {},
            "foods_with_images": 0,
            "unique_images": set(),
        }

        for food in foods:
            # 菜系分布
            cuisine = food.get("cuisine", "unknown")
            stats["cuisine_distribution"][cuisine] = stats["cuisine_distribution"].get(cuisine, 0) + 1

            # 餐种分布
            meal_types = food.get("meal_types", [])
            for meal_type in meal_types:
                stats["meal_type_distribution"][meal_type] = stats["meal_type_distribution"].get(meal_type, 0) + 1

            # 难度分布
            difficulty = food.get("difficulty", "medium")
            stats["difficulty_distribution"][difficulty] = stats["difficulty_distribution"].get(difficulty, 0) + 1

            # 图片统计
            if food.get("image_url"):
                stats["foods_with_images"] += 1
                stats["unique_images"].add(food["image_url"])

        stats["unique_images"] = len(stats["unique_images"])
        stats["image_coverage"] = (stats["foods_with_images"] / stats["total_foods"]) * 100 if stats["total_foods"] > 0 else 0

        return stats
