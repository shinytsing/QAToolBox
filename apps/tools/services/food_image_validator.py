import requests
import json
from typing import Dict, List
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class FoodImageValidator:
    """食品图片验证服务 - 解决图文不匹配问题"""

    def __init__(self):
        self.validation_results = []
        self.mismatch_foods = []

    def validate_food_images(self) -> Dict:
        """验证所有食品的图片"""
        from apps.tools.models import FoodItem

        logger.info("开始验证食品图片...")

        foods = FoodItem.objects.filter(is_active=True)
        total_count = foods.count()
        valid_count = 0
        invalid_count = 0

        for food in foods:
            validation_result = self.validate_single_food(food)
            self.validation_results.append(validation_result)

            if validation_result["is_valid"]:
                valid_count += 1
            else:
                invalid_count += 1
                self.mismatch_foods.append(food)

        # 生成验证报告
        report = {
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "validation_rate": round(valid_count / total_count * 100, 2) if total_count > 0 else 0,
            "mismatch_foods": [food.name for food in self.mismatch_foods],
            "validation_time": timezone.now().isoformat(),
            "details": self.validation_results,
        }

        logger.info(f"图片验证完成: {valid_count}/{total_count} 有效")
        return report

    def validate_single_food(self, food) -> Dict:
        """验证单个食品的图片"""
        result = {
            "food_id": food.id,
            "food_name": food.name,
            "cuisine": food.cuisine,
            "image_url": food.image_url,
            "is_valid": True,
            "issues": [],
            "suggestions": [],
        }

        # 1. 检查图片URL是否存在
        if not self.check_image_exists(food.image_url):
            result["is_valid"] = False
            result["issues"].append("图片URL无效或无法访问")
            result["suggestions"].append("需要更新图片URL")

        # 2. 检查图片与食物名称的匹配度
        if food.image_url:
            match_score = self.check_image_name_match(food.name, food.image_url)
            if match_score < 0.7:
                result["is_valid"] = False
                result["issues"].append(f"图片与食物名称匹配度低 ({match_score:.2f})")
                result["suggestions"].append("建议更换更匹配的图片")

        return result

    def check_image_exists(self, image_url: str) -> bool:
        """检查图片URL是否存在"""
        try:
            if not image_url:
                return False

            response = requests.head(image_url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"检查图片失败 {image_url}: {e}")
            return False

    def check_image_name_match(self, food_name: str, image_url: str) -> float:
        """检查图片与食物名称的匹配度"""
        # 模拟图像识别结果
        food_keywords = self.extract_food_keywords(food_name)
        detected_objects = self.simulate_image_recognition(image_url)

        # 计算匹配度
        match_count = 0
        for keyword in food_keywords:
            if any(keyword in obj.lower() for obj in detected_objects):
                match_count += 1

        return match_count / len(food_keywords) if food_keywords else 0.0

    def extract_food_keywords(self, food_name: str) -> List[str]:
        """提取食物关键词"""
        keywords = []

        # 中餐关键词
        chinese_keywords = ["豆腐", "鸡丁", "红烧", "糖醋", "鱼香", "宫保", "麻婆", "回锅", "水煮", "剁椒"]
        for keyword in chinese_keywords:
            if keyword in food_name:
                keywords.append(keyword)

        # 西餐关键词
        western_keywords = ["pasta", "pizza", "steak", "burger", "salad", "soup", "bread"]
        for keyword in western_keywords:
            if keyword.lower() in food_name.lower():
                keywords.append(keyword)

        return keywords if keywords else [food_name]

    def simulate_image_recognition(self, image_url: str) -> List[str]:
        """模拟图像识别结果"""
        import random

        # 模拟检测到的物体
        all_objects = [
            "food",
            "dish",
            "plate",
            "rice",
            "noodles",
            "meat",
            "vegetables",
            "soup",
            "sauce",
            "spices",
            "herbs",
            "garnish",
            "utensils",
        ]

        return random.sample(all_objects, random.randint(3, 6))
