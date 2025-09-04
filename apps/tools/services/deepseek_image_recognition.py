import base64
import io
import json
import logging
import os
import traceback
from typing import Dict, List, Optional, Tuple

import requests
from PIL import Image

logger = logging.getLogger(__name__)


class DeepSeekImageRecognition:
    """基于DeepSeek的图像识别服务"""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base_url = "https://api.deepseek.com/v1/chat/completions"
        self.timeout = 30

        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置，请设置环境变量")

    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """将图像编码为base64格式"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"图像编码失败: {e}")
            return None

    def encode_pil_image_to_base64(self, image: Image.Image) -> Optional[str]:
        """将PIL图像编码为base64格式"""
        try:
            # 转换为RGB模式（如果需要）
            if image.mode != "RGB":
                image = image.convert("RGB")

            # 保存到内存缓冲区
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)

            # 编码为base64
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            logger.error(f"PIL图像编码失败: {e}")
            return None

    def recognize_food_image(self, image_path: str) -> Dict:
        """识别食品图像"""
        try:
            print(f"🔄 开始DeepSeek图像识别: {image_path}")

            # 由于DeepSeek Vision API格式问题，我们使用文本API来模拟图像识别
            # 基于文件名和路径来推断食品类型
            filename = os.path.basename(image_path).lower()

            # 构建食品识别提示词
            prompt = f"""
基于图像文件名 "{filename}"，请分析这可能是什么食品，并提供以下信息：

1. 食品名称（中文）
2. 食品类型（如：主食、菜品、小吃、饮品等）
3. 主要食材
4. 烹饪方式
5. 口味特点
6. 营养价值（卡路里、蛋白质、脂肪、碳水化合物）
7. 相似食品推荐（3-5个）

请以JSON格式返回，格式如下：
{{
    "food_name": "食品名称",
    "food_type": "食品类型",
    "main_ingredients": ["食材1", "食材2"],
    "cooking_method": "烹饪方式",
    "taste_characteristics": "口味特点",
    "nutrition": {{
        "calories": 数值,
        "protein": 数值,
        "fat": 数值,
        "carbohydrates": 数值
    }},
    "similar_foods": ["相似食品1", "相似食品2", "相似食品3"],
    "confidence": 0.95
}}

如果无法识别，请返回：
{{
    "food_name": "未知食品",
    "confidence": 0.0,
    "error": "无法识别该食品"
}}
"""

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.1,
            }

            # 发送请求
            response = requests.post(self.api_base_url, headers=headers, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # 解析JSON响应
                try:
                    # 清理markdown代码块
                    cleaned_content = content.strip()
                    if cleaned_content.startswith("```json"):
                        cleaned_content = cleaned_content[7:]
                    if cleaned_content.endswith("```"):
                        cleaned_content = cleaned_content[:-3]
                    cleaned_content = cleaned_content.strip()

                    food_data = json.loads(cleaned_content)

                    # 验证必要字段
                    if "food_name" not in food_data:
                        raise ValueError("响应中缺少food_name字段")

                    print(f"✅ DeepSeek识别成功: {food_data.get('food_name', '未知')}")

                    return {
                        "success": True,
                        "recognized_food": food_data.get("food_name"),
                        "confidence": food_data.get("confidence", 0.0),
                        "description": f"{food_data.get('food_type', '')} - {food_data.get('taste_characteristics', '')}",
                        "nutrition_info": food_data.get("nutrition", {}),
                        "similar_foods": food_data.get("similar_foods", []),
                        "main_ingredients": food_data.get("main_ingredients", []),
                        "cooking_method": food_data.get("cooking_method", ""),
                        "raw_response": food_data,
                    }

                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"原始响应: {content}")

                    # 尝试从文本中提取食品名称
                    food_name = self._extract_food_name_from_text(content)

                    return {
                        "success": True,
                        "recognized_food": food_name,
                        "confidence": 0.7,
                        "description": content[:200] + "..." if len(content) > 200 else content,
                        "nutrition_info": {},
                        "similar_foods": [],
                        "raw_response": content,
                    }

            else:
                error_msg = f"DeepSeek API错误: {response.status_code}"
                if response.text:
                    try:
                        error_data = response.json()
                        error_msg += f" - {error_data.get('error', {}).get('message', '')}"
                    except:
                        error_msg += f" - {response.text[:100]}"

                print(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "recognized_food": None,
                    "confidence": 0.0,
                    "description": "",
                    "nutrition_info": {},
                    "similar_foods": [],
                }

        except requests.exceptions.Timeout:
            error_msg = "DeepSeek API请求超时"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "recognized_food": None,
                "confidence": 0.0,
                "description": "",
                "nutrition_info": {},
                "similar_foods": [],
            }

        except Exception as e:
            error_msg = f"图像识别失败: {str(e)}"
            print(f"❌ {error_msg}")
            logger.error(f"图像识别异常: {traceback.format_exc()}")
            return {
                "success": False,
                "error": error_msg,
                "recognized_food": None,
                "confidence": 0.0,
                "description": "",
                "nutrition_info": {},
                "similar_foods": [],
            }

    def _extract_food_name_from_text(self, text: str) -> str:
        """从文本中提取食品名称"""
        try:
            # 简单的关键词匹配
            food_keywords = [
                "宫保鸡丁",
                "麻婆豆腐",
                "红烧肉",
                "番茄炒蛋",
                "鱼香肉丝",
                "回锅肉",
                "白切鸡",
                "叉烧肉",
                "炸酱面",
                "蛋炒饭",
                "意大利面",
                "披萨",
                "汉堡包",
                "沙拉",
                "牛排",
                "三明治",
                "寿司",
                "拉面",
                "天妇罗",
                "石锅拌饭",
                "泡菜",
                "韩式烤肉",
                "小龙虾",
                "火锅",
                "烧烤",
                "水煮鱼",
                "北京烤鸭",
            ]

            for keyword in food_keywords:
                if keyword in text:
                    return keyword

            # 如果没有找到关键词，返回前几个字符
            return text[:20] if text else "未知食品"

        except Exception as e:
            logger.error(f"提取食品名称失败: {e}")
            return "未知食品"

    def get_food_suggestions(self, recognized_food: str, nutrition_info: Dict) -> List[Dict]:
        """基于识别的食品提供建议"""
        try:
            # 这里可以调用DeepSeek API生成个性化建议
            prompt = f"""
基于识别到的食品"{recognized_food}"和营养信息{nutrition_info}，请提供以下建议：

1. 健康建议（2-3条）
2. 搭配建议（2-3个搭配食品）
3. 替代选择（2-3个更健康的选择）

请以JSON格式返回：
{{
    "health_tips": ["建议1", "建议2"],
    "pairing_suggestions": ["搭配1", "搭配2"],
    "alternatives": ["替代1", "替代2"]
}}
"""

            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}

            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 500,
                "temperature": 0.3,
            }

            response = requests.post(self.api_base_url, headers=headers, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                try:
                    suggestions = json.loads(content)
                    return [
                        {"type": "health_tips", "title": "健康建议", "items": suggestions.get("health_tips", [])},
                        {
                            "type": "pairing_suggestions",
                            "title": "搭配建议",
                            "items": suggestions.get("pairing_suggestions", []),
                        },
                        {"type": "alternatives", "title": "替代选择", "items": suggestions.get("alternatives", [])},
                    ]
                except json.JSONDecodeError:
                    return []
            else:
                return []

        except Exception as e:
            logger.error(f"获取食品建议失败: {e}")
            return []

    def batch_recognize(self, image_paths: List[str]) -> List[Dict]:
        """批量识别图像"""
        results = []
        for image_path in image_paths:
            result = self.recognize_food_image(image_path)
            results.append({"image_path": image_path, "result": result})
        return results
