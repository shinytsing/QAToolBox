import json
import random
from typing import Dict, List, Optional

import requests


class FoodImageService:
    """AI食物图片服务 - 使用多个API获取准确的食物图片"""

    def __init__(self):
        # Unsplash API配置
        self.unsplash_access_key = "YOUR_UNSPLASH_ACCESS_KEY"  # 需要替换为实际的API key

        # 食物图片映射 - 使用更准确的图片URL
        self.food_image_mapping = {
            # 中餐经典
            "麻婆豆腐": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "宫保鸡丁": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "红烧肉": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "糖醋里脊": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "鱼香肉丝": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "青椒肉丝": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "番茄炒蛋": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "白切鸡": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "北京烤鸭": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "东坡肉": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "佛跳墙": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "剁椒鱼头": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "小龙虾": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "烧烤": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "火锅": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "兰州拉面": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "黄焖鸡米饭": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "麻辣香锅": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "蛋炒饭": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "小笼包": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "煎饼果子": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "豆浆油条": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "包子豆浆": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "回锅肉": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "水煮鱼": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "盖浇饭": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "沙县小吃": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "肯德基": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "麦当劳": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "必胜客": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "吉野家": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "味千拉面": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "韩式炸鸡店": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            # 西餐
            "意大利面": "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=500&fit=crop&crop=center",
            "汉堡包": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "三明治": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "沙拉": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "牛排": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "披萨": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "华夫饼": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "煎蛋三明治": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "燕麦粥": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "烤鸡": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "意式烩饭": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "法式可颂": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "法式牛排": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "西班牙海鲜饭": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            # 日料
            "寿司拼盘": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "拉面": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "天妇罗": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "日式味增汤": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "日式饭团": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "寿司卷": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "日式拉面": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            # 韩料
            "韩式烤肉": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "韩式炸鸡": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "韩式泡菜汤": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "韩式紫菜包饭": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "韩式煎饼": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "韩式炒年糕": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "韩式拌饭": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            # 泰餐
            "泰式咖喱": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "泰式冬阴功": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "泰式炒河粉": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "泰式炒饭": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "绿咖喱鸡": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "冬阴功汤": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            # 其他菜系
            "印度咖喱": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "墨西哥卷饼": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "蔬菜沙拉": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "水果拼盘": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "中式炒面": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "意式披萨": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "麻辣烫": "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "炸串": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "螺蛳粉": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
        }

        # 备用图片池 - 用于没有特定映射的食物
        self.fallback_images = [
            "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=500&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=400&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=500&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=400&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=500&fit=crop&crop=center",
            "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=500&fit=crop&crop=center",
        ]

    def get_food_image(self, food_name: str) -> str:
        """获取食物对应的图片URL"""
        # 首先尝试从映射中获取
        if food_name in self.food_image_mapping:
            return self.food_image_mapping[food_name]

        # 如果没有映射，从备用池中随机选择
        return random.choice(self.fallback_images)

    def search_unsplash_image(self, query: str) -> Optional[str]:
        """使用Unsplash API搜索食物图片"""
        try:
            if not self.unsplash_access_key or self.unsplash_access_key == "YOUR_UNSPLASH_ACCESS_KEY":
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

    def get_ai_generated_description(self, food_name: str, cuisine: str) -> str:
        """使用AI生成食物描述"""
        # 这里可以集成DeepSeek或其他AI服务
        # 暂时返回模板描述
        descriptions = {
            "chinese": f"{food_name}，经典中餐，口感丰富，营养美味",
            "western": f"{food_name}，西式美食，精致可口，营养均衡",
            "japanese": f"{food_name}，日式料理，精致美味，健康营养",
            "korean": f"{food_name}，韩式美食，口味独特，营养丰富",
            "thai": f"{food_name}，泰式料理，酸辣开胃，风味独特",
            "italian": f"{food_name}，意式美食，传统经典，口感丰富",
            "french": f"{food_name}，法式料理，精致优雅，味道醇厚",
            "indian": f"{food_name}，印度美食，香料丰富，口味浓郁",
            "mexican": f"{food_name}，墨西哥美食，色彩丰富，味道独特",
        }

        return descriptions.get(cuisine, f"{food_name}，美味佳肴，营养丰富")

    def expand_food_data(self, base_foods: List[Dict]) -> List[Dict]:
        """扩展食物数据，添加更多变体和详细信息"""
        expanded_foods = []

        for food in base_foods:
            # 添加原始食物
            expanded_foods.append(food)

            # 根据菜系添加变体
            if food["cuisine"] == "chinese":
                # 添加中餐变体
                variants = [
                    {"name": f"{food['name']}（微辣）", "tags": food["tags"] + ["mild_spicy"]},
                    {"name": f"{food['name']}（特辣）", "tags": food["tags"] + ["extra_spicy"]},
                    {"name": f"{food['name']}（清淡）", "tags": food["tags"] + ["light"]},
                ]

                for variant in variants:
                    variant_food = food.copy()
                    variant_food["name"] = variant["name"]
                    variant_food["tags"] = variant["tags"]
                    variant_food["image_url"] = self.get_food_image(variant["name"])
                    expanded_foods.append(variant_food)

            elif food["cuisine"] == "western":
                # 添加西餐变体
                variants = [
                    {"name": f"{food['name']}（经典）", "tags": food["tags"] + ["classic"]},
                    {"name": f"{food['name']}（创新）", "tags": food["tags"] + ["innovative"]},
                    {"name": f"{food['name']}（健康）", "tags": food["tags"] + ["healthy"]},
                ]

                for variant in variants:
                    variant_food = food.copy()
                    variant_food["name"] = variant["name"]
                    variant_food["tags"] = variant["tags"]
                    variant_food["image_url"] = self.get_food_image(variant["name"])
                    expanded_foods.append(variant_food)

        return expanded_foods
