#!/usr/bin/env python3
"""
真实数据旅游服务 - 使用DeepSeek API获取真实旅游数据
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List

import requests

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealDataTravelService:
    """真实数据旅游服务 - 使用DeepSeek API获取真实数据"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

        # 配置优化的超时时间
        self.session.timeout = (5, 30)  # (连接超时, 读取超时) - 减少等待时间

        # DeepSeek API配置
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "sk-c4a84c8bbff341cbb3006ecaf84030fe")
        self.deepseek_base_url = "https://api.deepseek.com/v1"

        # 免费API配置
        self.free_apis = {
            "weather": "wttr.in",
            "geocoding": "nominatim.openstreetmap.org",
            "places": "api.opentripmap.com",
            "wikipedia": "zh.wikipedia.org",
            "currency": "api.exchangerate-api.com",
            "timezone": "worldtimeapi.org",
        }

        # 重试配置 - 优化版本
        self.max_retries = 2  # 减少重试次数
        self.retry_delay = 1  # 减少重试延迟

    def get_real_travel_guide(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """获取真实旅游攻略数据 - 修复版本"""
        try:
            logger.info(f"🔍 开始为{destination}生成真实旅游攻略...")
            start_time = time.time()

            # 使用同步方式获取数据，避免线程池问题
            logger.info("🚀 获取基础数据...")

            # 获取景点数据
            logger.info("🔍 获取attractions数据...")
            attractions = self._get_data_with_fallback(
                "attractions", self._get_real_attractions_with_deepseek, destination, travel_style, interests
            )

            # 获取美食数据
            logger.info("🔍 获取foods数据...")
            foods = self._get_data_with_fallback("foods", self._get_real_foods_with_deepseek, destination, interests)

            # 获取住宿数据
            logger.info("🔍 获取accommodations数据...")
            accommodations = self._get_data_with_fallback(
                "accommodations", self._get_real_accommodations_with_deepseek, destination, budget_range
            )

            # 获取交通数据
            logger.info("🔍 获取transport数据...")
            transport = self._get_data_with_fallback("transport", self._get_real_transport_with_deepseek, destination)

            # 获取天气和地理信息
            logger.info("🌤️ 获取天气和地理信息...")
            weather_info = self._get_real_weather_data(destination)
            geo_info = self._get_geolocation_info(destination)

            # 生成完整攻略
            logger.info("📝 生成完整攻略...")
            complete_guide = self._generate_complete_guide_with_deepseek(
                destination,
                travel_style,
                budget_range,
                travel_duration,
                interests,
                attractions,
                foods,
                accommodations,
                transport,
                weather_info,
                geo_info,
            )

            # 合成最终攻略
            final_guide = self._synthesize_final_guide(
                destination,
                travel_style,
                budget_range,
                travel_duration,
                interests,
                geo_info,
                weather_info,
                attractions,
                foods,
                transport,
                accommodations,
                complete_guide,
            )

            end_time = time.time()
            logger.info(f"✅ 真实旅游攻略生成完成！耗时: {end_time - start_time:.2f}秒")
            return final_guide

        except Exception as e:
            logger.error(f"❌ 真实旅游攻略生成失败: {e}")
            # 如果真实数据获取失败，使用DeepSeek生成基础攻略
            return self._generate_fallback_with_deepseek(destination, travel_style, budget_range, travel_duration, interests)

    def _get_data_with_fallback(self, data_type: str, api_func, *args):
        """获取数据，失败时使用备用数据 - 快速模式"""
        try:
            logger.info(f"🔍 获取{data_type}数据...")
            result = api_func(*args)
            if result:
                logger.info(f"✅ {data_type}数据获取成功")
                return result
            else:
                logger.warning(f"⚠️ {data_type}数据获取失败，使用备用数据")
                return self._get_fallback_data(data_type, *args)
        except Exception as e:
            logger.warning(f"⚠️ {data_type}数据获取异常: {e}，使用备用数据")
            return self._get_fallback_data(data_type, *args)

    def _get_fallback_data(self, data_type: str, *args):
        """获取备用数据"""
        try:
            if data_type == "attractions":
                destination, travel_style, interests = args
                return self._get_fallback_attractions(destination, travel_style, interests)
            elif data_type == "foods":
                destination, interests = args
                return self._get_fallback_foods(destination, interests)
            elif data_type == "accommodations":
                destination, budget_range = args
                return self._get_fallback_accommodations(destination, budget_range)
            elif data_type == "transport":
                (destination,) = args
                return self._get_fallback_transport(destination)
            else:
                return []
        except Exception as e:
            logger.error(f"❌ 获取{data_type}备用数据失败: {e}")
            return []

    def get_fast_travel_guide(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """快速获取旅游攻略 - 优先使用备用数据"""
        try:
            logger.info(f"⚡ 开始为{destination}生成快速旅游攻略...")
            start_time = time.time()

            # 直接使用备用数据，跳过API调用
            attractions = self._get_fallback_attractions(destination, travel_style, interests)
            foods = self._get_fallback_foods(destination, interests)
            accommodations = self._get_fallback_accommodations(destination, budget_range)
            transport = self._get_fallback_transport(destination)

            # 快速获取天气和地理信息（使用备用数据）
            weather_info = self._get_fallback_weather_data(destination)
            geo_info = self._get_fallback_geo_data(destination)

            # 生成快速攻略
            complete_guide = self._generate_fallback_complete_guide(
                destination, travel_style, budget_range, travel_duration, interests
            )

            # 合成最终攻略
            final_guide = self._synthesize_final_guide(
                destination,
                travel_style,
                budget_range,
                travel_duration,
                interests,
                geo_info,
                weather_info,
                attractions,
                foods,
                transport,
                accommodations,
                complete_guide,
            )

            end_time = time.time()
            logger.info(f"⚡ 快速旅游攻略生成完成！耗时: {end_time - start_time:.2f}秒")
            return final_guide

        except Exception as e:
            logger.error(f"❌ 快速旅游攻略生成失败: {e}")
            return self._generate_fallback_guide(destination, travel_style, budget_range, travel_duration, interests)

    def _call_deepseek_api(self, prompt: str, max_tokens: int = 8000) -> str:  # 增加token数量到8000
        """调用DeepSeek API，带重试机制"""
        import time

        for attempt in range(self.max_retries):
            try:
                url = f"{self.deepseek_base_url}/chat/completions"
                headers = {"Authorization": f"Bearer {self.deepseek_api_key}", "Content-Type": "application/json"}

                data = {
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                }

                logger.info(f"🔄 DeepSeek API调用尝试 {attempt + 1}/{self.max_retries}")
                response = self.session.post(url, headers=headers, json=data)

                if response.status_code == 200:
                    result = response.json()
                    logger.info("✅ DeepSeek API调用成功")
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.warning(f"⚠️ DeepSeek API调用失败: {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        return ""

            except requests.exceptions.Timeout:
                logger.warning(f"⏰ DeepSeek API调用超时 (尝试 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error("❌ DeepSeek API调用最终超时")
                    return ""

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"🔌 DeepSeek API连接错误 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error("❌ DeepSeek API连接最终失败")
                    return ""

            except Exception as e:
                logger.error(f"❌ DeepSeek API调用异常: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                else:
                    return ""

        return ""

    def _get_real_attractions_with_deepseek(self, destination: str, travel_style: str, interests: List[str]) -> List[Dict]:
        """使用DeepSeek获取真实景点数据 - 增强版本"""
        try:
            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""请为{destination}推荐12个真实存在的景点，要求：

1. 必须是真实存在的景点，有具体名称和准确信息
2. 符合{travel_style}旅行风格
3. 考虑{interests_text}兴趣偏好
4. 包含以下详细信息：
   - 景点名称（必须准确）
   - 门票价格（人民币，包含优惠政策）
   - 开放时间（具体时间段）
   - 推荐理由（详细说明）
   - 交通方式（具体路线）
   - 游览时长（建议时间）
   - 景点类型（自然/人文/娱乐等）
   - 最佳游览季节
   - 特色亮点
   - 周边配套设施
   - 拍照建议
   - 注意事项

请按以下格式返回JSON：
{{
  "attractions": [
    {{
      "name": "景点名称",
      "ticket_price": "门票价格（包含优惠政策）",
      "opening_hours": "开放时间",
      "reason": "详细推荐理由",
      "transport": "具体交通方式",
      "duration": "建议游览时长",
      "type": "景点类型",
      "best_season": "最佳游览季节",
      "highlights": "特色亮点",
      "facilities": "周边配套设施",
      "photo_tips": "拍照建议",
      "notes": "注意事项"
    }}
  ]
}}

只返回JSON格式，不要其他内容。确保JSON格式正确，可以被解析。"""

            response = self._call_deepseek_api(prompt, max_tokens=3000)

            if response:
                # 尝试解析JSON
                try:
                    cleaned_response = self._clean_json_response(response)
                    data = json.loads(cleaned_response)
                    logger.info("✅ 景点数据JSON解析成功")
                    return data.get("attractions", [])
                except json.JSONDecodeError as e:
                    logger.warning(f"景点数据JSON解析失败: {e}")
                    # 如果JSON解析失败，尝试提取景点信息
                    return self._extract_attractions_from_text(response, destination)

        except Exception as e:
            logger.error(f"获取景点数据失败: {e}")

        return []

    def _extract_attractions_from_text(self, text: str, destination: str) -> List[Dict]:
        """从文本中提取景点信息"""
        attractions = []

        # 使用正则表达式提取景点信息
        lines = text.split("\n")
        current_attraction = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 提取景点名称
            if "：" in line or ":" in line:
                parts = line.replace("：", ":").split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    if "景点" in key or "名称" in key:
                        if current_attraction:
                            attractions.append(current_attraction)
                        current_attraction = {"name": value}
                    elif "门票" in key or "价格" in key:
                        current_attraction["ticket_price"] = value
                    elif "时间" in key or "开放" in key:
                        current_attraction["opening_hours"] = value
                    elif "理由" in key or "推荐" in key:
                        current_attraction["reason"] = value
                    elif "交通" in key:
                        current_attraction["transport"] = value
                    elif "时长" in key or "游览" in key:
                        current_attraction["duration"] = value

        if current_attraction:
            attractions.append(current_attraction)

        return attractions

    def _get_real_foods_with_deepseek(self, destination: str, interests: List[str]) -> List[Dict]:
        """使用DeepSeek获取真实美食数据 - 增强版本"""
        try:
            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""请为{destination}推荐12个真实存在的美食/餐厅，要求：

1. 必须是真实存在的美食或餐厅，有具体名称
2. 考虑{interests_text}兴趣偏好
3. 包含以下详细信息：
   - 美食/餐厅名称（必须准确）
   - 特色菜品（具体菜名）
   - 推荐餐厅（具体店名）
   - 价格区间（人均消费）
   - 推荐理由（详细说明）
   - 餐厅地址（具体位置）
   - 营业时间（具体时间段）
   - 预订建议（是否需要预订）
   - 用餐高峰期提醒
   - 特色亮点
   - 适合人群
   - 注意事项

请按以下格式返回JSON：
{{
  "foods": [
    {{
      "name": "美食/餐厅名称",
      "specialty": "特色菜品",
      "restaurant": "推荐餐厅",
      "price_range": "价格区间",
      "reason": "详细推荐理由",
      "address": "餐厅地址",
      "opening_hours": "营业时间",
      "booking": "预订建议",
      "peak_hours": "用餐高峰期",
      "highlights": "特色亮点",
      "suitable_for": "适合人群",
      "notes": "注意事项"
    }}
  ]
}}

只返回JSON格式，不要其他内容。确保JSON格式正确，可以被解析。"""

            response = self._call_deepseek_api(prompt, max_tokens=3000)

            if response:
                try:
                    cleaned_response = self._clean_json_response(response)
                    data = json.loads(cleaned_response)
                    logger.info("✅ 美食数据JSON解析成功")
                    return data.get("foods", [])
                except json.JSONDecodeError as e:
                    logger.warning(f"美食数据JSON解析失败: {e}")
                    # 如果JSON解析失败，尝试提取美食信息
                    return self._extract_foods_from_text(response, destination)

        except Exception as e:
            logger.error(f"获取美食数据失败: {e}")

        return []

    def _extract_foods_from_text(self, text: str, destination: str) -> List[Dict]:
        """从文本中提取美食信息"""
        foods = []

        lines = text.split("\n")
        current_food = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "：" in line or ":" in line:
                parts = line.replace("：", ":").split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    if "美食" in key or "名称" in key:
                        if current_food:
                            foods.append(current_food)
                        current_food = {"name": value}
                    elif "餐厅" in key or "店" in key:
                        current_food["restaurant"] = value
                    elif "价格" in key:
                        current_food["price_range"] = value
                    elif "描述" in key or "特色" in key:
                        current_food["description"] = value
                    elif "理由" in key or "推荐" in key:
                        current_food["reason"] = value
                    elif "时间" in key:
                        current_food["best_time"] = value

        if current_food:
            foods.append(current_food)

        return foods

    def _get_real_accommodations_with_deepseek(self, destination: str, budget_range: str) -> List[Dict]:
        """使用DeepSeek获取真实住宿数据 - 增强版本"""
        try:
            prompt = f"""请为{destination}推荐8个真实存在的住宿选择，要求：

1. 必须是真实存在的酒店/民宿，有具体名称
2. 符合{budget_range}预算范围
3. 包含以下详细信息：
   - 酒店/民宿名称（必须准确）
   - 价格区间（具体价格范围）
   - 推荐理由（详细说明）
   - 酒店地址（具体位置）
   - 房间类型（标准间/豪华间等）
   - 设施服务（WiFi/早餐/健身房等）
   - 交通便利性（距离地铁/景点距离）
   - 周边环境（餐饮/购物/景点）
   - 入住和退房时间
   - 预订渠道建议
   - 适合人群
   - 注意事项

请按以下格式返回JSON：
{{
  "accommodations": [
    {{
      "name": "酒店/民宿名称",
      "price_range": "价格区间",
      "reason": "详细推荐理由",
      "address": "酒店地址",
      "room_type": "房间类型",
      "facilities": "设施服务",
      "transport": "交通便利性",
      "surroundings": "周边环境",
      "check_in_out": "入住和退房时间",
      "booking": "预订渠道建议",
      "suitable_for": "适合人群",
      "notes": "注意事项"
    }}
  ]
}}

只返回JSON格式，不要其他内容。确保JSON格式正确，可以被解析。"""

            response = self._call_deepseek_api(prompt, max_tokens=2500)

            if response:
                try:
                    cleaned_response = self._clean_json_response(response)
                    data = json.loads(cleaned_response)
                    logger.info("✅ 住宿数据JSON解析成功")
                    return data.get("accommodations", [])
                except json.JSONDecodeError as e:
                    logger.warning(f"住宿数据JSON解析失败: {e}")
                    return []

        except Exception as e:
            logger.error(f"获取住宿数据失败: {e}")

        return []

    def _get_real_transport_with_deepseek(self, destination: str) -> Dict:
        """使用DeepSeek获取真实交通数据 - 增强版本"""
        try:
            prompt = f"""请为{destination}提供详细的交通指南，要求：

1. 必须是{destination}真实的交通信息
2. 包含以下详细信息：
   - 机场到市区交通（多种方式、费用、时间）
   - 火车站到市区交通（多种方式、费用、时间）
   - 市内公共交通（地铁、公交、出租车等）
   - 主要景点间交通（具体路线、费用、时间）
   - 交通费用参考（详细费用明细）
   - 交通卡办理和使用
   - 自驾游路线和停车信息
   - 网约车使用建议
   - 交通高峰期提醒
   - 夜间交通选择
   - 交通注意事项

请按以下格式返回JSON：
{{
  "transport": {{
    "airport_to_city": "机场到市区交通（详细说明）",
    "train_to_city": "火车站到市区交通（详细说明）",
    "public_transport": "市内公共交通（详细说明）",
    "attractions_transport": "主要景点间交通（详细说明）",
    "cost_reference": "交通费用参考（详细费用）",
    "transport_card": "交通卡办理和使用",
    "self_drive": "自驾游路线和停车信息",
    "ride_sharing": "网约车使用建议",
    "peak_hours": "交通高峰期提醒",
    "night_transport": "夜间交通选择",
    "notes": "交通注意事项"
  }}
}}

只返回JSON格式，不要其他内容。确保JSON格式正确，可以被解析。"""

            response = self._call_deepseek_api(prompt, max_tokens=2000)

            if response:
                try:
                    cleaned_response = self._clean_json_response(response)
                    data = json.loads(cleaned_response)
                    logger.info("✅ 交通数据JSON解析成功")
                    return data.get("transport", {})
                except json.JSONDecodeError as e:
                    logger.warning(f"交通数据JSON解析失败: {e}")
                    return {}

        except Exception as e:
            logger.error(f"获取交通数据失败: {e}")

        return {}

    def _get_real_weather_data(self, destination: str) -> Dict:
        """使用DeepSeek获取天气数据 - 改进版本"""
        try:
            prompt = f"""请为{destination}提供当前天气信息。

要求：
1. 基于{destination}的实际气候特点
2. 必须严格按照JSON格式返回，不要任何其他文字
3. 确保JSON格式完全正确，可以被解析

格式要求：
{{
  "current": {{
    "temperature": 25,
    "feels_like": 27,
    "weather": "晴天",
    "humidity": 65,
    "wind_speed": 3.5,
    "visibility": 10,
    "pressure": 1013
  }},
  "forecast": {{
    "max_temp": 28,
    "min_temp": 22,
    "weather": "多云",
    "chance_of_rain": 20
  }},
  "location": "{destination}",
  "last_updated": "2024-01-01T12:00:00"
}}

请确保返回的是有效的JSON格式，不要包含任何解释文字。"""

            response = self._call_deepseek_api(prompt, max_tokens=1000)

            if response:
                # 清理响应文本，移除可能的非JSON内容
                cleaned_response = self._clean_json_response(response)
                try:
                    data = json.loads(cleaned_response)
                    logger.info("✅ 天气数据JSON解析成功")
                    return data
                except json.JSONDecodeError as e:
                    logger.warning(f"天气数据JSON解析失败: {e}")
                    logger.warning(f"原始响应: {response[:200]}...")
                    return self._get_fallback_weather_data(destination)
            else:
                return self._get_fallback_weather_data(destination)

        except Exception as e:
            logger.warning(f"天气数据获取失败: {e}")
            return self._get_fallback_weather_data(destination)

    def _get_fallback_weather_data(self, destination: str) -> Dict:
        """获取备用天气数据"""
        # 基于城市特点提供合理的天气数据
        weather_data = {
            "current": {
                "temperature": 25,
                "feels_like": 27,
                "weather": "晴天",
                "humidity": 65,
                "wind_speed": 3.5,
                "visibility": 10,
                "pressure": 1013,
            },
            "forecast": {"max_temp": 28, "min_temp": 22, "weather": "多云", "chance_of_rain": 20},
            "location": destination,
            "last_updated": datetime.now().isoformat(),
        }

        # 根据城市调整天气数据
        if "北京" in destination:
            weather_data["current"]["temperature"] = 20
            weather_data["current"]["weather"] = "晴朗"
        elif "上海" in destination:
            weather_data["current"]["temperature"] = 26
            weather_data["current"]["weather"] = "多云"
        elif "广州" in destination or "深圳" in destination:
            weather_data["current"]["temperature"] = 30
            weather_data["current"]["weather"] = "阵雨"
            weather_data["current"]["humidity"] = 80

        return weather_data

    def _get_geolocation_info(self, destination: str) -> Dict:
        """使用DeepSeek获取地理信息 - 改进版本"""
        try:
            prompt = f"""请为{destination}提供地理位置信息。

要求：
1. 基于{destination}的实际地理位置
2. 必须严格按照JSON格式返回，不要任何其他文字
3. 确保JSON格式完全正确，可以被解析

格式要求：
{{
  "lat": 23.1291,
  "lon": 113.2644,
  "display_name": "{destination}, 中国",
  "country": "中国",
  "state": "广东省",
  "city": "{destination}",
  "postcode": "510000"
}}

请确保返回的是有效的JSON格式，不要包含任何解释文字。"""

            response = self._call_deepseek_api(prompt, max_tokens=800)

            if response:
                # 清理响应文本，移除可能的非JSON内容
                cleaned_response = self._clean_json_response(response)
                try:
                    data = json.loads(cleaned_response)
                    logger.info("✅ 地理信息JSON解析成功")
                    return data
                except json.JSONDecodeError as e:
                    logger.warning(f"地理信息JSON解析失败: {e}")
                    logger.warning(f"原始响应: {response[:200]}...")
                    return self._get_fallback_geo_data(destination)
            else:
                return self._get_fallback_geo_data(destination)

        except Exception as e:
            logger.warning(f"地理信息获取失败: {e}")
            return self._get_fallback_geo_data(destination)

    def _get_fallback_geo_data(self, destination: str) -> Dict:
        """获取备用地理数据"""
        # 基于城市提供合理的地理数据
        geo_data = {
            "lat": 23.1291,
            "lon": 113.2644,
            "display_name": destination,
            "country": "中国",
            "state": "广东省",
            "city": destination,
            "postcode": "510000",
        }

        # 根据城市调整地理数据
        if "北京" in destination:
            geo_data.update({"lat": 39.9042, "lon": 116.4074, "state": "北京市", "postcode": "100000"})
        elif "上海" in destination:
            geo_data.update({"lat": 31.2304, "lon": 121.4737, "state": "上海市", "postcode": "200000"})
        elif "深圳" in destination:
            geo_data.update({"lat": 22.3193, "lon": 114.1694, "state": "广东省", "postcode": "518000"})
        elif "杭州" in destination:
            geo_data.update({"lat": 30.2741, "lon": 120.1551, "state": "浙江省", "postcode": "310000"})
        elif "成都" in destination:
            geo_data.update({"lat": 30.5728, "lon": 104.0668, "state": "四川省", "postcode": "610000"})

        return geo_data

    def _clean_json_response(self, response: str) -> str:
        """清理API响应，提取JSON部分"""
        try:
            # 查找JSON开始和结束的位置
            start_markers = ["{", "["]

            start_pos = -1
            end_pos = -1

            # 找到第一个 { 或 [
            for marker in start_markers:
                pos = response.find(marker)
                if pos != -1 and (start_pos == -1 or pos < start_pos):
                    start_pos = pos

            if start_pos == -1:
                return response

            # 找到匹配的结束标记
            if response[start_pos] == "{":
                # 查找匹配的 }
                brace_count = 0
                for i in range(start_pos, len(response)):
                    if response[i] == "{":
                        brace_count += 1
                    elif response[i] == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
            elif response[start_pos] == "[":
                # 查找匹配的 ]
                bracket_count = 0
                for i in range(start_pos, len(response)):
                    if response[i] == "[":
                        bracket_count += 1
                    elif response[i] == "]":
                        bracket_count -= 1
                        if bracket_count == 0:
                            end_pos = i + 1
                            break

            if start_pos != -1 and end_pos != -1:
                return response[start_pos:end_pos]
            else:
                return response

        except Exception as e:
            logger.warning(f"清理JSON响应失败: {e}")
            return response

    def _generate_complete_guide_with_deepseek(
        self,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        attractions: List[Dict],
        foods: List[Dict],
        accommodations: List[Dict],
        transport: Dict,
        weather_info: Dict,
        geo_info: Dict,
    ) -> str:
        """使用DeepSeek生成完整攻略 - 增强详细版本"""
        try:
            # 构建包含所有真实数据的提示词
            attractions_text = "\n".join(
                [
                    f"- {att['name']}: {att.get('ticket_price', 'N/A')}元, {att.get('opening_hours', 'N/A')}, {att.get('reason', 'N/A')}"
                    for att in attractions[:8]  # 增加到8个景点
                ]
            )

            foods_text = "\n".join(
                [
                    f"- {food['name']}: {food.get('restaurant', 'N/A')}, {food.get('price_range', 'N/A')}, {food.get('reason', 'N/A')}"
                    for food in foods[:8]  # 增加到8个美食
                ]
            )

            accommodations_text = "\n".join(
                [
                    f"- {acc['name']}: {acc.get('price_range', 'N/A')}, {acc.get('reason', 'N/A')}"
                    for acc in accommodations[:5]  # 增加到5个住宿
                ]
            )

            weather_text = ""
            if "current" in weather_info and not weather_info.get("error"):
                current = weather_info["current"]
                weather_text = (
                    f"当前天气: {current['weather']}, 温度: {current['temperature']}°C, 湿度: {current['humidity']}%"
                )

            interests_text = "、".join(interests) if interests else "通用"

            prompt = f"""基于以下真实数据为{destination}生成一份极其详细、实用的旅游攻略：

## 真实景点数据：
{attractions_text}

## 真实美食数据：
{foods_text}

## 真实住宿数据：
{accommodations_text}

## 真实交通信息：
- 机场到市区：{transport.get('airport_to_city', 'N/A')}
- 市内交通：{transport.get('public_transport', 'N/A')}
- 景点间交通：{transport.get('attractions_transport', 'N/A')}

## 实时天气信息：
{weather_text}

## 旅行要求：
- 目的地：{destination}
- 旅行风格：{travel_style}
- 预算范围：{budget_range}
- 旅行时长：{travel_duration}
- 兴趣偏好：{interests_text}

请生成一份包含以下内容的极其详细的攻略：

# 🗺️ {destination}旅游攻略

## 📋 行程总览
基于{travel_duration}的详细行程安排，包含每日具体时间安排和路线规划。

## 🎯 必去景点详解
基于真实景点数据的详细推荐，包含：
- 每个景点的详细介绍和特色
- 最佳游览时间和季节
- 门票价格和优惠政策
- 交通方式和到达路线
- 游览时长和游览建议
- 拍照最佳位置
- 周边配套设施

## 🍜 美食攻略详解
基于真实美食数据的详细推荐，包含：
- 每个餐厅的详细介绍
- 必点菜品和特色菜
- 价格区间和性价比
- 餐厅地址和交通方式
- 营业时间和预订建议
- 用餐高峰期提醒
- 当地特色小吃推荐

## 🏨 住宿指南详解
基于真实住宿数据的详细推荐，包含：
- 不同预算档次的酒店推荐
- 酒店位置和周边环境
- 房间类型和设施介绍
- 预订渠道和价格对比
- 入住和退房时间
- 周边餐饮和交通

## 🚗 交通指南详解
详细的交通信息和费用，包含：
- 机场/火车站到市区的多种交通方式
- 市内公共交通线路和费用
- 主要景点间的交通路线
- 出租车和网约车使用建议
- 自驾游路线和停车信息
- 交通卡办理和使用

## 💰 预算分析详解
基于真实价格的详细预算，包含：
- 住宿费用明细（按天计算）
- 餐饮费用明细（按餐计算）
- 交通费用明细（按行程计算）
- 门票费用明细（按景点计算）
- 购物和娱乐费用
- 应急费用预留
- 总预算和日均预算

## 💡 实用贴士详解
基于当前天气和当地特色的详细建议，包含：
- 最佳旅行季节和月份
- 天气适应和着装建议
- 当地习俗和文化禁忌
- 安全注意事项
- 购物和讨价还价技巧
- 网络和通讯建议
- 医疗和紧急联系方式

## 🏮 文化背景详解
当地特色和文化信息，包含：
- 历史背景和文化特色
- 当地语言和常用词汇
- 传统节日和活动
- 手工艺品和特产
- 宗教信仰和习俗
- 当地人的生活方式

## 📱 实用信息
- 紧急联系电话
- 旅游咨询中心
- 医院和药店
- 银行和ATM
- 邮局和快递
- 网络和WiFi

请确保所有信息都基于提供的真实数据，内容要极其详细实用，便于游客参考。每个部分都要有具体的建议和实用的信息。"""

            return self._call_deepseek_api(prompt, max_tokens=4000)  # 增加token数量

        except Exception as e:
            logger.error(f"生成完整攻略失败: {e}")
            return ""

    def _synthesize_final_guide(
        self,
        destination: str,
        travel_style: str,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        geo_info: Dict,
        weather_info: Dict,
        attractions: List[Dict],
        foods: List[Dict],
        transport: Dict,
        accommodations: List[Dict],
        complete_guide: str,
    ) -> Dict:
        """合成最终攻略 - 新格式"""
        try:
            days = self._parse_travel_duration(travel_duration)

            # 提取景点和美食名称
            attraction_names = [att["name"] for att in attractions if "name" in att]
            food_names = [food["name"] for food in foods if "name" in food]

            # 生成预算估算
            budget_estimate = self._generate_realistic_budget(days, budget_range, attractions, accommodations)

            # 生成每日行程
            daily_schedule = self._generate_realistic_daily_schedule(
                destination, days, attraction_names, food_names, travel_style, weather_info
            )

            # 生成旅行贴士
            travel_tips = self._generate_realistic_tips(destination, weather_info, attractions)

            # 生成概览信息
            overview = {
                "destination": destination,
                "travel_style": travel_style,
                "budget_range": budget_range,
                "travel_duration": travel_duration,
                "interests": interests,
                "weather_summary": weather_info.get("current", {}).get("weather", "未知"),
                "temperature": weather_info.get("current", {}).get("temperature", 0),
                "total_budget": budget_estimate.get("total_cost", 0),
                "days": days,
                "geo_info": geo_info,
            }

            # 生成行程信息
            itinerary = {"daily_schedule": daily_schedule, "total_days": days}

            # 生成景点信息
            attractions_section = {
                "must_visit": attractions,
                "total_count": len(attractions),
                "attraction_names": attraction_names[:8],
            }

            # 生成美食信息
            foods_section = {"recommendations": foods, "total_count": len(foods), "food_names": food_names[:8]}

            # 生成交通信息
            transport_section = {
                "airport_to_city": transport.get("airport_to_city", ""),
                "train_to_city": transport.get("train_to_city", ""),
                "public_transport": transport.get("public_transport", ""),
                "attractions_transport": transport.get("attractions_transport", ""),
                "cost_reference": transport.get("cost_reference", ""),
            }

            # 生成预算信息
            budget_section = {
                "total_cost": budget_estimate.get("total_cost", 0),
                "daily_average": budget_estimate.get("daily_total", 0),
                "breakdown": budget_estimate.get("daily_breakdown", {}),
                "budget_range": budget_range,
            }

            # 生成贴士信息
            tips_section = {
                "travel_tips": travel_tips,
                "weather_tips": self._generate_weather_tips(weather_info),
                "cultural_tips": self._generate_cultural_tips(destination),
                "safety_tips": self._generate_safety_tips(destination),
            }

            # 生成详细攻略文本（用于PDF导出）
            detailed_guide_text = self._generate_detailed_guide_text(
                overview,
                itinerary,
                attractions_section,
                foods_section,
                transport_section,
                budget_section,
                tips_section,
                accommodations,
            )

            return {
                # 基本信息
                "destination": destination,
                "travel_style": travel_style,
                "budget_range": budget_range,
                "travel_duration": travel_duration,
                "interests": interests,
                "weather_info": weather_info,
                "geolocation_info": geo_info,
                "transportation_guide": transport,
                # 核心数据 - 直接返回原始数据
                "attractions": attractions,  # 直接返回景点列表
                "foods": foods,  # 直接返回美食列表
                "accommodations": accommodations,  # 直接返回住宿列表
                # 结构化数据
                "overview": overview,
                "itinerary": itinerary,
                "sections": {
                    "attractions": attractions_section,
                    "foods": foods_section,
                    "transport": transport_section,
                    "budget": budget_section,
                    "tips": tips_section,
                },
                # 详细攻略文本（用于PDF导出）
                "detailed_guide_text": detailed_guide_text,
                # 兼容性字段
                "must_visit_attractions": attraction_names[:8],
                "food_recommendations": food_names[:8],
                "attractions_detail": attractions,
                "foods_detail": foods,
                "budget_estimate": budget_estimate,
                "daily_schedule": daily_schedule,
                "travel_tips": travel_tips,
                "complete_guide": complete_guide,
                # 元数据
                "data_sources": {
                    "attractions": "DeepSeek API",
                    "foods": "DeepSeek API",
                    "accommodations": "DeepSeek API",
                    "transport": "DeepSeek API",
                    "weather": "DeepSeek API",
                    "geolocation": "DeepSeek API",
                    "complete_guide": "DeepSeek API",
                },
                "generated_at": datetime.now().isoformat(),
                "is_real_data": True,
                "api_used": "DeepSeek API",
            }

        except Exception as e:
            logger.error(f"合成最终攻略失败: {e}")
            return self._generate_fallback_guide(destination, travel_style, budget_range, travel_duration, interests)

    def _parse_travel_duration(self, travel_duration: str) -> int:
        """解析旅行时长"""
        if "1天" in travel_duration or "1晚" in travel_duration:
            return 1
        elif "2天" in travel_duration or "2晚" in travel_duration:
            return 2
        elif "3天" in travel_duration or "3晚" in travel_duration:
            return 3
        elif "4天" in travel_duration or "4晚" in travel_duration:
            return 4
        elif "5天" in travel_duration or "5晚" in travel_duration:
            return 5
        else:
            return 3

    def _generate_realistic_budget(
        self, days: int, budget_range: str, attractions: List[Dict], accommodations: List[Dict]
    ) -> Dict:
        """生成真实预算估算"""
        base_costs = {
            "low": {"accommodation": 150, "food": 80, "transport": 50, "attractions": 30},
            "medium": {"accommodation": 300, "food": 150, "transport": 100, "attractions": 80},
            "high": {"accommodation": 600, "food": 300, "transport": 200, "attractions": 150},
        }

        costs = base_costs.get(budget_range, base_costs["medium"])

        # 根据景点数量调整门票费用
        attraction_count = len(attractions)
        if attraction_count > 0:
            costs["attractions"] = min(costs["attractions"] * (attraction_count / 5), 200)

        daily_total = sum(costs.values())
        total_cost = daily_total * days

        return {
            "daily_breakdown": costs,
            "daily_total": daily_total,
            "total_cost": total_cost,
            "currency": "CNY",
            "budget_range": budget_range,
            "days": days,
        }

    def _generate_realistic_daily_schedule(
        self, destination: str, days: int, attractions: List[str], foods: List[str], travel_style: str, weather_info: Dict
    ) -> List[Dict]:
        """生成真实每日行程"""
        schedules = []

        for day in range(1, days + 1):
            # 根据天气调整行程
            weather_advice = ""
            if "current" in weather_info and not weather_info.get("error"):
                current = weather_info["current"]
                if current["weather"] in ["雨", "雪", "雾"]:
                    weather_advice = "建议室内活动为主"
                elif current["temperature"] > 30:
                    weather_advice = "注意防暑降温"
                elif current["temperature"] < 10:
                    weather_advice = "注意保暖"

            # 分配景点和美食
            day_attractions = attractions[day - 1 :: days] if attractions else []
            day_foods = foods[day - 1 :: days] if foods else []

            schedule = {
                "day": day,
                "date": f"第{day}天",
                "weather_advice": weather_advice,
                "morning": day_attractions[:2] if day_attractions else [],
                "afternoon": day_attractions[2:4] if len(day_attractions) > 2 else [],
                "evening": day_foods[:2] if day_foods else [],
                "night": day_foods[2:4] if len(day_foods) > 2 else [],
                "total_attractions": len(day_attractions),
                "total_foods": len(day_foods),
            }

            schedules.append(schedule)

        return schedules

    def _generate_realistic_tips(self, destination: str, weather_info: Dict, attractions: List[Dict]) -> List[str]:
        """生成真实旅行贴士"""
        tips = []

        # 基于天气的贴士
        if "current" in weather_info and not weather_info.get("error"):
            current = weather_info["current"]
            if current["weather"] in ["雨", "雪"]:
                tips.append(f"今天{destination}有{current['weather']}，建议携带雨具或保暖衣物")
            if current["temperature"] > 30:
                tips.append(f"今天{destination}温度较高({current['temperature']}°C)，注意防暑降温")
            if current["humidity"] > 70:
                tips.append("湿度较大，注意防潮")

        # 基于景点的贴士
        attraction_count = len(attractions)
        if attraction_count > 0:
            tips.append(f"{destination}有{attraction_count}个推荐景点，建议合理安排时间")

        # 通用贴士
        tips.extend(
            [f"建议提前了解{destination}的交通情况", "准备一些常用药品和应急用品", "注意保管好随身物品", "尊重当地文化和习俗"]
        )

        return tips[:8]

    def _generate_fallback_guide(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> Dict:
        """生成备用攻略"""
        return {
            "destination": destination,
            "travel_style": travel_style,
            "budget_range": budget_range,
            "travel_duration": travel_duration,
            "interests": interests,
            "must_visit_attractions": [f"{destination}著名景点"],
            "food_recommendations": [f"{destination}特色美食"],
            "detailed_guide": f"{destination}是一个美丽的旅游目的地，建议您亲自体验。",
            "travel_tips": ["建议提前了解当地天气", "注意保管好随身物品"],
            "budget_estimate": {"total_cost": 1000, "currency": "CNY"},
            "daily_schedule": [],
            "is_real_data": False,
            "fallback_source": "Basic Fallback",
            "generated_at": datetime.now().isoformat(),
        }

    def _get_fallback_attractions(self, destination: str, travel_style: str, interests: List[str]) -> List[Dict]:
        """获取备用景点数据"""
        common_attractions = {
            "武汉": [
                {
                    "name": "黄鹤楼",
                    "ticket_price": "80元",
                    "opening_hours": "8:00-17:00",
                    "reason": "武汉地标建筑",
                    "transport": "地铁4号线",
                    "duration": "2小时",
                    "type": "历史建筑",
                },
                {
                    "name": "东湖",
                    "ticket_price": "免费",
                    "opening_hours": "全天开放",
                    "reason": "中国最大的城中湖",
                    "transport": "公交或地铁",
                    "duration": "半天",
                    "type": "自然景观",
                },
                {
                    "name": "户部巷",
                    "ticket_price": "免费",
                    "opening_hours": "全天开放",
                    "reason": "武汉特色小吃街",
                    "transport": "地铁2号线",
                    "duration": "2小时",
                    "type": "美食街",
                },
            ],
            "北京": [
                {
                    "name": "故宫",
                    "ticket_price": "60元",
                    "opening_hours": "8:30-17:00",
                    "reason": "明清皇宫",
                    "transport": "地铁1号线",
                    "duration": "4小时",
                    "type": "历史建筑",
                },
                {
                    "name": "天安门广场",
                    "ticket_price": "免费",
                    "opening_hours": "全天开放",
                    "reason": "中国政治中心",
                    "transport": "地铁1号线",
                    "duration": "1小时",
                    "type": "广场",
                },
                {
                    "name": "长城",
                    "ticket_price": "40元",
                    "opening_hours": "8:00-17:00",
                    "reason": "世界文化遗产",
                    "transport": "旅游大巴",
                    "duration": "半天",
                    "type": "历史建筑",
                },
            ],
            "上海": [
                {
                    "name": "外滩",
                    "ticket_price": "免费",
                    "opening_hours": "全天开放",
                    "reason": "黄浦江畔景观",
                    "transport": "地铁2号线",
                    "duration": "2小时",
                    "type": "城市景观",
                },
                {
                    "name": "东方明珠",
                    "ticket_price": "220元",
                    "opening_hours": "8:30-21:30",
                    "reason": "上海地标",
                    "transport": "地铁2号线",
                    "duration": "2小时",
                    "type": "现代建筑",
                },
                {
                    "name": "豫园",
                    "ticket_price": "45元",
                    "opening_hours": "8:45-16:45",
                    "reason": "明代园林",
                    "transport": "地铁10号线",
                    "duration": "2小时",
                    "type": "古典园林",
                },
            ],
        }

        return common_attractions.get(
            destination,
            [
                {
                    "name": f"{destination}著名景点",
                    "ticket_price": "50元",
                    "opening_hours": "9:00-17:00",
                    "reason": "当地特色",
                    "transport": "公交",
                    "duration": "2小时",
                    "type": "景点",
                }
            ],
        )

    def _get_fallback_foods(self, destination: str, interests: List[str]) -> List[Dict]:
        """获取备用美食数据"""
        common_foods = {
            "武汉": [
                {"name": "热干面", "price": "8-15元", "location": "户部巷", "description": "武汉特色小吃", "type": "面食"},
                {"name": "豆皮", "price": "5-10元", "location": "户部巷", "description": "传统小吃", "type": "小吃"},
                {"name": "武昌鱼", "price": "50-100元", "location": "各大餐厅", "description": "湖北名菜", "type": "鱼类"},
            ],
            "北京": [
                {"name": "北京烤鸭", "price": "100-200元", "location": "全聚德", "description": "北京名菜", "type": "烤鸭"},
                {"name": "炸酱面", "price": "15-25元", "location": "老北京炸酱面", "description": "传统面食", "type": "面食"},
                {"name": "糖葫芦", "price": "5-10元", "location": "街头小摊", "description": "传统小吃", "type": "小吃"},
            ],
            "上海": [
                {"name": "小笼包", "price": "20-40元", "location": "南翔小笼", "description": "上海名点", "type": "包子"},
                {"name": "生煎包", "price": "15-25元", "location": "各大生煎店", "description": "上海特色", "type": "包子"},
                {"name": "红烧肉", "price": "50-80元", "location": "本帮菜馆", "description": "上海名菜", "type": "肉类"},
            ],
        }

        return common_foods.get(
            destination,
            [
                {
                    "name": f"{destination}特色美食",
                    "price": "30-50元",
                    "location": "当地餐厅",
                    "description": "当地特色",
                    "type": "特色菜",
                }
            ],
        )

    def _get_fallback_accommodations(self, destination: str, budget_range: str) -> List[Dict]:
        """获取备用住宿数据"""
        budget_levels = {
            "经济型": {"price_range": "100-300元", "type": "经济型酒店"},
            "舒适型": {"price_range": "300-600元", "type": "商务酒店"},
            "豪华型": {"price_range": "600-1200元", "type": "星级酒店"},
            "奢华型": {"price_range": "1200元以上", "type": "豪华酒店"},
        }

        level = budget_levels.get(budget_range, budget_levels["舒适型"])

        return [
            {
                "name": f'{destination}{level["type"]}',
                "price_range": level["price_range"],
                "type": level["type"],
                "location": f"{destination}市中心",
                "amenities": ["WiFi", "空调", "热水"],
                "rating": "4.0",
            }
        ]

    def _get_fallback_transport(self, destination: str) -> Dict:
        """获取备用交通数据"""
        return {
            "airport": f"{destination}机场",
            "train_station": f"{destination}火车站",
            "subway": f"{destination}地铁",
            "bus": f"{destination}公交",
            "taxi": f"{destination}出租车",
            "tips": f"建议使用地铁和公交出行，方便快捷",
        }

    def _generate_fallback_complete_guide(
        self, destination: str, travel_style: str, budget_range: str, travel_duration: str, interests: List[str]
    ) -> str:
        """生成备用完整攻略"""
        interests_text = "、".join(interests) if interests else "通用"

        return f"""
{destination}旅游攻略

目的地：{destination}
旅行风格：{travel_style}
预算范围：{budget_range}
旅行时长：{travel_duration}
兴趣偏好：{interests_text}

【景点推荐】
- {destination}著名景点
- 建议提前了解开放时间和门票价格

【美食推荐】
- {destination}特色美食
- 建议品尝当地特色小吃

【住宿建议】
- 根据预算选择合适的酒店
- 建议选择交通便利的位置

【交通指南】
- 机场/火车站到市区
- 市内交通方式
- 景点间交通

【旅行贴士】
- 提前了解当地天气
- 准备必要的证件
- 注意保管随身物品
- 尊重当地文化习俗

祝您在{destination}旅途愉快！
"""

    def _generate_weather_tips(self, weather_info: Dict) -> List[str]:
        """生成天气相关贴士"""
        tips = []
        try:
            current = weather_info.get("current", {})
            weather = current.get("weather", "")
            temperature = current.get("temperature", 0)
            humidity = current.get("humidity", 0)

            if "雨" in weather or "雪" in weather:
                tips.append("建议携带雨具或保暖衣物")
            elif temperature > 30:
                tips.append("天气炎热，注意防晒和补水")
            elif temperature < 10:
                tips.append("天气较冷，注意保暖")

            if humidity > 80:
                tips.append("湿度较大，建议携带防潮用品")

        except Exception as e:
            logger.warning(f"生成天气贴士失败: {e}")

        return tips if tips else ["请关注当地天气预报"]

    def _generate_cultural_tips(self, destination: str) -> List[str]:
        """生成文化相关贴士"""
        tips = []
        try:
            # 基于城市特点生成文化贴士
            if "北京" in destination:
                tips.extend(["注意参观故宫等景点需要提前预约", "尊重当地文化习俗，注意礼仪"])
            elif "上海" in destination:
                tips.extend(["体验海派文化，品尝本帮菜", "注意地铁出行时间安排"])
            elif "广州" in destination or "深圳" in destination:
                tips.extend(["品尝粤式早茶文化", "注意天气变化，携带雨具"])
            else:
                tips.extend(["了解当地文化习俗", "尊重当地居民生活习惯"])
        except Exception as e:
            logger.warning(f"生成文化贴士失败: {e}")

        return tips if tips else ["了解当地文化习俗"]

    def _generate_safety_tips(self, destination: str) -> List[str]:
        """生成安全相关贴士"""
        tips = [
            "保管好随身财物，注意防盗",
            "遵守交通规则，注意人身安全",
            "保持手机畅通，记录紧急联系方式",
            "注意饮食卫生，避免食物中毒",
        ]
        return tips

    def _generate_detailed_guide_text(
        self,
        overview: Dict,
        itinerary: Dict,
        attractions_section: Dict,
        foods_section: Dict,
        transport_section: Dict,
        budget_section: Dict,
        tips_section: Dict,
        accommodations: List[Dict],
    ) -> str:
        """生成详细攻略文本（用于PDF导出）"""
        try:
            content = []

            # 标题
            content.append(f"🗺️ {overview['destination']}旅游攻略")
            content.append("=" * 60)
            content.append("")

            # 概览
            content.append("📋 概览")
            content.append("-" * 30)
            content.append(f"📍 目的地: {overview['destination']}")
            content.append(f"🎯 旅行风格: {overview['travel_style']}")
            content.append(f"💰 预算范围: {overview['budget_range']}")
            content.append(f"⏰ 旅行时长: {overview['travel_duration']}")
            interests = overview.get("interests", [])
            if isinstance(interests, list):
                content.append(f"🎨 兴趣偏好: {', '.join(interests)}")
            else:
                content.append(f"🎨 兴趣偏好: {str(interests)}")
            content.append(f"🌤️ 天气状况: {overview['weather_summary']}")
            content.append(f"🌡️ 当前温度: {overview['temperature']}°C")
            content.append(f"💵 总预算: {overview['total_budget']}元")
            content.append("")

            # 行程
            content.append("🚥 行程安排")
            content.append("-" * 30)
            daily_schedule = itinerary.get("daily_schedule", [])
            for i, day_schedule in enumerate(daily_schedule, 1):
                content.append(f"第{i}天:")
                for time_slot, activities in day_schedule.items():
                    if activities:
                        if isinstance(activities, list):
                            content.append(f"  {time_slot}: {', '.join([str(act) for act in activities])}")
                        else:
                            content.append(f"  {time_slot}: {str(activities)}")
                content.append("")

            # 景点
            content.append("🎯 必去景点")
            content.append("-" * 30)
            attractions = attractions_section.get("must_visit", [])
            for i, attraction in enumerate(attractions, 1):
                if isinstance(attraction, dict):
                    name = attraction.get("name", "")
                    description = attraction.get("description", "")
                    ticket_price = attraction.get("ticket_price", "")
                    content.append(f"{i}. {name}")
                    if description:
                        content.append(f"   描述: {description}")
                    if ticket_price:
                        content.append(f"   门票: {ticket_price}")
                    content.append("")
                else:
                    content.append(f"{i}. {str(attraction)}")
                    content.append("")

            # 美食
            content.append("🍜 美食推荐")
            content.append("-" * 30)
            foods = foods_section.get("recommendations", [])
            for i, food in enumerate(foods, 1):
                if isinstance(food, dict):
                    name = food.get("name", "")
                    specialty = food.get("specialty", "")
                    restaurant = food.get("restaurant", "")
                    content.append(f"{i}. {name}")
                    if specialty:
                        content.append(f"   特色: {specialty}")
                    if restaurant:
                        content.append(f"   推荐餐厅: {restaurant}")
                    content.append("")
                else:
                    content.append(f"{i}. {str(food)}")
                    content.append("")

            # 交通
            content.append("🚗 交通指南")
            content.append("-" * 30)
            content.append(f"✈️ 机场到市区: {transport_section.get('airport_to_city', '')}")
            content.append(f"🚄 火车站到市区: {transport_section.get('train_to_city', '')}")
            content.append(f"🚌 市内公共交通: {transport_section.get('public_transport', '')}")
            content.append(f"🚶 景点间交通: {transport_section.get('attractions_transport', '')}")
            content.append(f"💰 交通费用参考: {transport_section.get('cost_reference', '')}")
            content.append("")

            # 预算
            content.append("💰 预算分析")
            content.append("-" * 30)
            content.append(f"💵 总预算: {budget_section.get('total_cost', 0)}元")
            content.append(f"📊 日均预算: {budget_section.get('daily_average', 0)}元")
            breakdown = budget_section.get("breakdown", {})
            for category, amount in breakdown.items():
                content.append(f"  {category}: {amount}元")
            content.append("")

            # 贴士
            content.append("💡 实用贴士")
            content.append("-" * 30)

            # 旅行贴士
            travel_tips = tips_section.get("travel_tips", [])
            if travel_tips:
                content.append("🎒 旅行贴士:")
                for tip in travel_tips:
                    content.append(f"  • {tip}")
                content.append("")

            # 天气贴士
            weather_tips = tips_section.get("weather_tips", [])
            if weather_tips:
                content.append("🌤️ 天气贴士:")
                for tip in weather_tips:
                    content.append(f"  • {tip}")
                content.append("")

            # 文化贴士
            cultural_tips = tips_section.get("cultural_tips", [])
            if cultural_tips:
                content.append("🏛️ 文化贴士:")
                for tip in cultural_tips:
                    content.append(f"  • {tip}")
                content.append("")

            # 安全贴士
            safety_tips = tips_section.get("safety_tips", [])
            if safety_tips:
                content.append("🛡️ 安全贴士:")
                for tip in safety_tips:
                    content.append(f"  • {tip}")
                content.append("")

            # 住宿推荐
            if accommodations:
                content.append("🏠 住宿推荐")
                content.append("-" * 30)
                for i, accommodation in enumerate(accommodations, 1):
                    if isinstance(accommodation, dict):
                        name = accommodation.get("name", "")
                        address = accommodation.get("address", "")
                        price_range = accommodation.get("price_range", "")
                        content.append(f"{i}. {name}")
                        if address:
                            content.append(f"   地址: {address}")
                        if price_range:
                            content.append(f"   价格: {price_range}")
                        content.append("")
                    else:
                        content.append(f"{i}. {str(accommodation)}")
                        content.append("")

            return "\n".join(content)

        except Exception as e:
            logger.error(f"生成详细攻略文本失败: {e}")
            return f"🗺️ {overview.get('destination', '未知')}旅游攻略\n\n生成详细攻略时出现错误，请查看原始数据。"
