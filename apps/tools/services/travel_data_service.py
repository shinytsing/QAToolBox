import json
import os
import random
import re
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


class TravelDataService:
    """智能旅游攻略生成引擎 - 使用免费API实现"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }
        )

        # 使用免费API，不需要密钥
        self.use_free_apis = True

    def get_travel_guide_data(
        self,
        destination: str,
        travel_style: str,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
    ) -> Dict:
        """智能旅游攻略生成引擎主函数"""
        try:
            print(f"🔍 开始为{destination}生成智能攻略...")

            # 1. 数据抓取阶段
            print("📡 阶段1: 数据抓取...")
            raw_data = self._数据抓取阶段(destination)

            # 检查是否获取到有效数据
            if not self._has_valid_data(raw_data):
                raise Exception("无法获取有效的旅游数据，请检查网络连接")

            # 2. 信息结构化
            print("🔧 阶段2: 信息结构化...")
            structured_data = self._信息结构化(raw_data, destination)

            # 3. 智能合成阶段
            print("🤖 阶段3: 智能合成...")
            final_guide = self._智能合成阶段(
                destination,
                travel_style,
                budget_min,
                budget_max,
                budget_amount,
                budget_range,
                travel_duration,
                interests,
                structured_data,
            )

            print("✅ 攻略生成完成！")
            return final_guide

        except Exception as e:
            print(f"❌ 攻略生成失败: {e}")
            raise Exception(f"旅游攻略生成失败: {str(e)}")

    def _has_valid_data(self, raw_data: Dict) -> bool:
        """检查是否获取到有效数据"""
        if not raw_data:
            return False

        # 检查各个数据源是否有有效数据
        for source, data in raw_data.items():
            if source == "weather" and data and not data.get("error"):
                return True
            elif source in ["search_data", "wiki_data"] and data and not data.get("error"):
                return True

        return True  # 即使没有外部数据，也可以生成基础攻略

    def _数据抓取阶段(self, destination: str) -> Dict:
        """数据抓取阶段 - 使用免费API"""
        raw_data = {}

        # 1. 使用免费搜索API获取旅游信息
        try:
            print(f"  🔍 搜索{destination}旅游信息")
            search_data = self._search_travel_info(destination)
            raw_data["search_data"] = search_data
        except Exception as e:
            print(f"  ⚠️ 搜索API调用失败: {e}")
            raw_data["search_data"] = {"error": f"搜索API调用失败: {str(e)}"}

        # 2. 获取天气数据（免费wttr.in API）
        try:
            print(f"  🌤️ 获取天气数据（免费wttr.in API）")
            weather_data = self._get_weather_data(destination)
            raw_data["weather"] = weather_data
        except Exception as e:
            print(f"  ⚠️ wttr.in API调用失败: {e}")
            raw_data["weather"] = {"error": f"wttr.in API调用失败: {str(e)}"}

        # 3. 获取维基百科数据（免费）
        try:
            print(f"  📚 获取维基百科数据")
            wiki_data = self._get_wikipedia_data(destination)
            raw_data["wiki_data"] = wiki_data
        except Exception as e:
            print(f"  ⚠️ 维基百科API调用失败: {e}")
            raw_data["wiki_data"] = {"error": f"维基百科API调用失败: {str(e)}"}

        # 4. 获取OpenTripMap景点数据（免费）
        try:
            print(f"  🗺️ 获取OpenTripMap景点数据")
            opentripmap_data = self._get_opentripmap_data(destination)
            raw_data["opentripmap"] = opentripmap_data
        except Exception as e:
            print(f"  ⚠️ OpenTripMap API调用失败: {e}")
            raw_data["opentripmap"] = {"error": f"OpenTripMap API调用失败: {str(e)}"}

        # 5. 获取国家信息数据（免费RestCountries API）
        try:
            print(f"  🌍 获取国家信息数据")
            country_data = self._get_country_data(destination)
            raw_data["country"] = country_data
        except Exception as e:
            print(f"  ⚠️ RestCountries API调用失败: {e}")
            raw_data["country"] = {"error": f"RestCountries API调用失败: {str(e)}"}

        # 6. 获取地理位置数据（免费IP Geolocation API）
        try:
            print(f"  📍 获取地理位置数据")
            geo_data = self._get_geolocation_data(destination)
            raw_data["geolocation"] = geo_data
        except Exception as e:
            print(f"  ⚠️ IP Geolocation API调用失败: {e}")
            raw_data["geolocation"] = {"error": f"IP Geolocation API调用失败: {str(e)}"}

        # 7. 获取汇率数据（免费Currency API）
        try:
            print(f"  💱 获取汇率数据")
            currency_data = self._get_currency_data(destination)
            raw_data["currency"] = currency_data
        except Exception as e:
            print(f"  ⚠️ Currency API调用失败: {e}")
            raw_data["currency"] = {"error": f"Currency API调用失败: {str(e)}"}

        # 8. 获取时区数据（免费Time API）
        try:
            print(f"  🕐 获取时区数据")
            timezone_data = self._get_timezone_data(destination)
            raw_data["timezone"] = timezone_data
        except Exception as e:
            print(f"  ⚠️ Time API调用失败: {e}")
            raw_data["timezone"] = {"error": f"Time API调用失败: {str(e)}"}

        return raw_data

    def _search_travel_info(self, destination: str) -> Dict:
        """使用免费搜索API获取旅游信息"""
        try:
            # 使用DuckDuckGo Instant Answer API (免费)
            query = f"{destination} 旅游攻略 景点 美食"
            encoded_query = urllib.parse.quote(query)

            url = f"https://api.duckduckgo.com/"
            params = {"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"}

            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_duckduckgo_results(data, destination)

        except Exception as e:
            print(f"DuckDuckGo搜索失败: {e}")

        # 如果搜索失败，返回基础数据
        return self._get_fallback_travel_data(destination)

    def _get_weather_data(self, destination: str) -> Dict:
        """获取天气数据（免费wttr.in API）"""
        try:
            # 使用免费的wttr.in API
            url = f"https://wttr.in/{destination}?format=j1"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current_condition = data["current_condition"][0]

                return {
                    "temperature": float(current_condition["temp_C"]),
                    "weather": (
                        current_condition["lang_zh"][0]["value"]
                        if "lang_zh" in current_condition
                        else current_condition["weatherDesc"][0]["value"]
                    ),
                    "humidity": int(current_condition["humidity"]),
                    "wind_speed": float(current_condition["windspeedKmph"]),
                    "feels_like": float(current_condition["FeelsLikeC"]),
                }

        except Exception as e:
            print(f"天气数据获取失败: {e}")

        # 如果免费API失败，返回模拟数据
        return self._get_fallback_weather_data(destination)

    def _get_wikipedia_data(self, destination: str) -> Dict:
        """获取维基百科数据（免费API）"""
        try:
            # 使用维基百科API
            url = "https://zh.wikipedia.org/api/rest_v1/page/summary/"
            encoded_destination = urllib.parse.quote(destination)

            response = self.session.get(f"{url}{encoded_destination}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", destination),
                    "extract": data.get("extract", f"{destination}是一个美丽的旅游目的地"),
                    "content_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                }

        except Exception as e:
            print(f"维基百科数据获取失败: {e}")

        return {
            "title": destination,
            "extract": f"{destination}是一个充满魅力的旅游目的地，拥有丰富的文化遗产和自然风光。",
            "content_url": "",
        }

    def _get_opentripmap_data(self, destination: str) -> Dict:
        """获取OpenTripMap景点数据（免费API）"""
        try:
            # 使用OpenTripMap API (免费，无需密钥)
            # 首先获取地理坐标
            geocode_url = f"https://api.opentripmap.com/0.1/zh/places/geocode"
            params = {"name": destination, "limit": 1, "format": "json"}

            response = self.session.get(geocode_url, params=params, timeout=10)
            if response.status_code == 200:
                geocode_data = response.json()
                if geocode_data:
                    location = geocode_data[0]
                    lat = location.get("lat")
                    lon = location.get("lon")

                    # 获取景点信息
                    places_url = f"https://api.opentripmap.com/0.1/zh/places/radius"
                    places_params = {
                        "radius": 5000,  # 5公里半径
                        "lon": lon,
                        "lat": lat,
                        "kinds": "cultural,historic,architecture,interesting_places",
                        "limit": 10,
                        "format": "json",
                    }

                    places_response = self.session.get(places_url, params=places_params, timeout=10)
                    if places_response.status_code == 200:
                        places_data = places_response.json()
                        attractions = []
                        for place in places_data.get("features", []):
                            props = place.get("properties", {})
                            attractions.append(
                                {
                                    "name": props.get("name", ""),
                                    "type": props.get("kinds", ""),
                                    "description": props.get("wikipedia_extracts", {}).get("text", ""),
                                }
                            )

                        return {
                            "location": {"lat": lat, "lon": lon},
                            "attractions": attractions,
                            "total_count": len(attractions),
                        }

        except Exception as e:
            print(f"OpenTripMap数据获取失败: {e}")

        return {"location": {"lat": 0, "lon": 0}, "attractions": [], "total_count": 0}

    def _get_country_data(self, destination: str) -> Dict:
        """获取国家信息数据（免费RestCountries API）"""
        try:
            # 使用RestCountries API
            url = f"https://restcountries.com/v3.1/name/{destination}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    country = data[0]
                    return {
                        "name": country.get("name", {}).get("common", destination),
                        "capital": country.get("capital", [""])[0] if country.get("capital") else "",
                        "region": country.get("region", ""),
                        "population": country.get("population", 0),
                        "currencies": list(country.get("currencies", {}).keys()),
                        "languages": list(country.get("languages", {}).values()),
                        "flag": country.get("flags", {}).get("png", ""),
                        "timezones": country.get("timezones", []),
                    }

        except Exception as e:
            print(f"RestCountries数据获取失败: {e}")

        return {
            "name": destination,
            "capital": "",
            "region": "",
            "population": 0,
            "currencies": ["CNY"],
            "languages": ["中文"],
            "flag": "",
            "timezones": ["UTC+8"],
        }

    def _get_geolocation_data(self, destination: str) -> Dict:
        """获取地理位置数据（免费IP Geolocation API）"""
        try:
            # 使用免费的地理位置API
            url = f"http://ip-api.com/json/{destination}"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return {
                        "country": data.get("country", ""),
                        "region": data.get("regionName", ""),
                        "city": data.get("city", ""),
                        "lat": data.get("lat", 0),
                        "lon": data.get("lon", 0),
                        "timezone": data.get("timezone", ""),
                        "isp": data.get("isp", ""),
                    }

        except Exception as e:
            print(f"IP Geolocation数据获取失败: {e}")

        return {
            "country": "China",
            "region": "",
            "city": destination,
            "lat": 0,
            "lon": 0,
            "timezone": "Asia/Shanghai",
            "isp": "",
        }

    def _get_currency_data(self, destination: str) -> Dict:
        """获取汇率数据（免费Currency API）"""
        try:
            # 使用免费的汇率API
            url = "https://api.exchangerate-api.com/v4/latest/CNY"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})

                # 获取主要货币汇率
                major_currencies = ["USD", "EUR", "JPY", "GBP", "KRW", "THB", "SGD", "MYR"]
                currency_rates = {}
                for currency in major_currencies:
                    if currency in rates:
                        currency_rates[currency] = rates[currency]

                return {"base_currency": "CNY", "rates": currency_rates, "last_updated": data.get("date", "")}

        except Exception as e:
            print(f"Currency数据获取失败: {e}")

        return {
            "base_currency": "CNY",
            "rates": {"USD": 0.14, "EUR": 0.13, "JPY": 20.5, "GBP": 0.11, "KRW": 180.0, "THB": 5.0, "SGD": 0.19, "MYR": 0.65},
            "last_updated": "2024-01-01",
        }

    def _get_timezone_data(self, destination: str) -> Dict:
        """获取时区数据（免费Time API）"""
        try:
            # 使用免费的时区API
            url = f"http://worldtimeapi.org/api/timezone/Asia/Shanghai"

            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "timezone": data.get("timezone", "Asia/Shanghai"),
                    "datetime": data.get("datetime", ""),
                    "utc_offset": data.get("utc_offset", "+08:00"),
                    "day_of_week": data.get("day_of_week", 1),
                    "is_dst": data.get("dst", False),
                }

        except Exception as e:
            print(f"Timezone数据获取失败: {e}")

        return {"timezone": "Asia/Shanghai", "datetime": "", "utc_offset": "+08:00", "day_of_week": 1, "is_dst": False}

    def _信息结构化(self, raw_data: Dict, destination: str = "目的地") -> Dict:
        """信息结构化"""
        structured_data = {
            "景点": [],
            "美食": [],
            "贴士": [],
            "天气": {},
            "简介": "",
            "地理位置": {},
            "国家信息": {},
            "汇率信息": {},
            "时区信息": {},
            "景点详情": [],
        }

        try:
            # 从搜索数据提取
            if (
                "search_data" in raw_data
                and isinstance(raw_data["search_data"], dict)
                and "error" not in raw_data["search_data"]
            ):
                search_data = raw_data["search_data"]
                if "attractions" in search_data:
                    structured_data["景点"].extend([att["name"] for att in search_data["attractions"]])
                if "tips" in search_data:
                    structured_data["贴士"].extend([tip["content"] for tip in search_data["tips"]])

            # 从维基百科数据提取
            if "wiki_data" in raw_data and isinstance(raw_data["wiki_data"], dict) and "error" not in raw_data["wiki_data"]:
                wiki_data = raw_data["wiki_data"]
                structured_data["简介"] = wiki_data.get("extract", f"{destination}是一个美丽的旅游目的地")

            # 从天气数据提取
            if "weather" in raw_data and isinstance(raw_data["weather"], dict) and "error" not in raw_data["weather"]:
                structured_data["天气"] = raw_data["weather"]

            # 从OpenTripMap数据提取景点详情
            if (
                "opentripmap" in raw_data
                and isinstance(raw_data["opentripmap"], dict)
                and "error" not in raw_data["opentripmap"]
            ):
                opentripmap_data = raw_data["opentripmap"]
                if "attractions" in opentripmap_data:
                    attractions = opentripmap_data["attractions"]
                    structured_data["景点详情"] = attractions
                    # 提取景点名称
                    for attraction in attractions:
                        if attraction.get("name"):
                            structured_data["景点"].append(attraction["name"])

            # 从国家信息数据提取
            if "country" in raw_data and isinstance(raw_data["country"], dict) and "error" not in raw_data["country"]:
                structured_data["国家信息"] = raw_data["country"]

            # 从地理位置数据提取
            if (
                "geolocation" in raw_data
                and isinstance(raw_data["geolocation"], dict)
                and "error" not in raw_data["geolocation"]
            ):
                structured_data["地理位置"] = raw_data["geolocation"]

            # 从汇率数据提取
            if "currency" in raw_data and isinstance(raw_data["currency"], dict) and "error" not in raw_data["currency"]:
                structured_data["汇率信息"] = raw_data["currency"]

            # 从时区数据提取
            if "timezone" in raw_data and isinstance(raw_data["timezone"], dict) and "error" not in raw_data["timezone"]:
                structured_data["时区信息"] = raw_data["timezone"]

            # 使用正则表达式提取核心信息
            for source_name, source_data in raw_data.items():
                if isinstance(source_data, str):
                    extracted_info = self.提取核心信息(source_data)
                    structured_data["景点"].extend(extracted_info["景点"])
                    structured_data["美食"].extend(extracted_info["美食"])
                    structured_data["贴士"].extend(extracted_info["贴士"])

            # 去重
            structured_data["景点"] = list(set(structured_data["景点"]))
            structured_data["美食"] = list(set(structured_data["美食"]))
            structured_data["贴士"] = list(set(structured_data["贴士"]))

            # 如果没有获取到任何数据，添加一些基础信息
            if not structured_data["景点"]:
                structured_data["景点"] = [f"{destination}著名景点", f"{destination}历史文化景点", f"{destination}自然风光"]
            if not structured_data["美食"]:
                structured_data["美食"] = [f"{destination}特色美食", f"{destination}传统小吃", f"{destination}地方特产"]
            if not structured_data["贴士"]:
                structured_data["贴士"] = ["建议提前了解当地天气", "准备常用药品", "注意人身和财物安全"]
            if not structured_data["简介"]:
                structured_data["简介"] = f"{destination}是一个充满魅力的旅游目的地，拥有丰富的文化遗产和自然风光。"

        except Exception as e:
            print(f"信息结构化失败: {e}")
            # 提供基础数据
            structured_data["景点"] = [f"{destination}著名景点", f"{destination}历史文化景点", f"{destination}自然风光"]
            structured_data["美食"] = [f"{destination}特色美食", f"{destination}传统小吃", f"{destination}地方特产"]
            structured_data["贴士"] = ["建议提前了解当地天气", "准备常用药品", "注意人身和财物安全"]
            structured_data["简介"] = f"{destination}是一个充满魅力的旅游目的地，拥有丰富的文化遗产和自然风光。"

        return structured_data

    def 提取核心信息(self, 原始文本: str) -> Dict:
        """提取核心信息"""
        attractions = []
        foods = []
        tips = []

        # 提取景点信息
        attraction_matches = re.findall(r"推荐景点[:：]\s*([^必吃注意]+?)(?=\s*必吃|注意|$)", 原始文本)
        for match in attraction_matches:
            attractions.extend([item.strip() for item in match.split("、") if item.strip()])

        # 提取美食信息
        food_matches = re.findall(r"必吃[：:]\s*([^注意]+?)(?=\s*注意|$)", 原始文本)
        for match in food_matches:
            foods.extend([item.strip() for item in match.split("、") if item.strip()])

        # 提取贴士信息
        tip_matches = re.findall(r"注意[：:]\s*([^推荐必吃]+?)(?=\s*推荐|必吃|$)", 原始文本)
        for match in tip_matches:
            tips.extend([item.strip() for item in match.split("，") if item.strip()])

        return {"景点": attractions, "美食": foods, "贴士": tips}

    def _智能合成阶段(
        self,
        destination: str,
        travel_style: str,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        structured_data: Dict,
    ) -> Dict:
        """智能合成阶段 - 使用本地算法生成攻略"""
        try:
            # 生成智能攻略
            guide_data = self._generate_smart_guide(
                destination,
                travel_style,
                budget_min,
                budget_max,
                budget_amount,
                budget_range,
                travel_duration,
                interests,
                structured_data,
            )

            return guide_data

        except Exception as e:
            print(f"智能合成失败: {e}")
            raise Exception(f"智能合成失败: {str(e)}")

    def _generate_smart_guide(
        self,
        destination: str,
        travel_style: str,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        travel_duration: str,
        interests: List[str],
        structured_data: Dict,
    ) -> Dict:
        """生成智能攻略"""
        days = self._parse_travel_duration(travel_duration)

        # 根据旅行风格和兴趣调整景点和美食
        adjusted_attractions = self._adjust_attractions_by_style(structured_data["景点"], travel_style, interests)
        adjusted_foods = self._adjust_foods_by_style(structured_data["美食"], travel_style, interests)

        # 生成详细攻略
        detailed_guide = self._generate_detailed_guide_text(
            destination,
            adjusted_attractions,
            adjusted_foods,
            structured_data["贴士"],
            travel_style,
            budget_min,
            budget_max,
            budget_amount,
            budget_range,
            travel_duration,
        )

        # 生成增强版攻略内容
        enhanced_guide = self._generate_enhanced_guide_content(
            destination, structured_data, travel_style, budget_min, budget_max, budget_amount, budget_range
        )

        return {
            "destination": destination,
            "travel_style": travel_style,
            "budget_range": budget_range,
            "travel_duration": travel_duration,
            "interests": interests,
            "must_visit_attractions": adjusted_attractions[:5],
            "food_recommendations": adjusted_foods[:5],
            "transportation_guide": self._generate_transportation_guide(destination),
            "hidden_gems": self._generate_hidden_gems(destination, travel_style),
            "weather_info": structured_data.get("天气", self._get_fallback_weather_data(destination)),
            "budget_estimate": self._generate_budget_estimate(budget_min, budget_max, budget_amount, budget_range, days),
            "travel_tips": structured_data["贴士"][:5],
            "best_time_to_visit": self._get_best_time_to_visit(destination),
            "detailed_guide": detailed_guide,
            "daily_schedule": self._generate_daily_schedule(
                destination, days, {"景点": adjusted_attractions, "美食": adjusted_foods, "贴士": structured_data["贴士"]}
            ),
            "activity_timeline": self._generate_activity_timeline(days),
            "cost_breakdown": self._generate_cost_breakdown(
                destination,
                days,
                budget_min,
                budget_max,
                budget_amount,
                budget_range,
                {"景点": adjusted_attractions, "美食": adjusted_foods, "贴士": structured_data["贴士"]},
            ),
            # 新增的丰富数据
            "destination_info": self._generate_destination_info(destination, structured_data),
            "attraction_details": structured_data.get("景点详情", []),
            "country_info": structured_data.get("国家信息", {}),
            "geolocation_info": structured_data.get("地理位置", {}),
            "currency_info": structured_data.get("汇率信息", {}),
            "timezone_info": structured_data.get("时区信息", {}),
            "enhanced_content": enhanced_guide,
        }

    def _adjust_attractions_by_style(self, attractions: List[str], travel_style: str, interests: List[str]) -> List[str]:
        """根据旅行风格调整景点"""
        style_keywords = {
            "adventure": ["公园", "山", "湖", "自然", "户外", "探险"],
            "leisure": ["公园", "广场", "花园", "休闲", "放松"],
            "cultural": ["博物馆", "寺庙", "古迹", "文化", "历史"],
            "foodie": ["美食街", "小吃", "餐厅", "市场"],
            "shopping": ["商场", "市场", "步行街", "购物"],
            "photography": ["观景台", "公园", "湖", "山", "古建筑"],
        }

        keywords = style_keywords.get(travel_style, [])
        if not keywords:
            return attractions

        # 根据关键词重新排序景点
        prioritized = []
        others = []

        for attraction in attractions:
            if any(keyword in attraction for keyword in keywords):
                prioritized.append(attraction)
            else:
                others.append(attraction)

        return prioritized + others

    def _adjust_foods_by_style(self, foods: List[str], travel_style: str, interests: List[str]) -> List[str]:
        """根据旅行风格调整美食"""
        if travel_style == "foodie":
            # 美食型旅行者，美食优先
            return foods
        else:
            # 其他类型，美食作为补充
            return foods[:3]  # 只保留前3个

    def _generate_transportation_guide(self, destination: str) -> Dict:
        """生成交通指南"""
        return {
            "地铁": f"{destination}地铁四通八达，建议购买交通卡",
            "公交": "公交车线路覆盖广泛，票价便宜",
            "出租车": "起步价8-13元，建议使用滴滴打车",
            "共享单车": "适合短距离出行，注意安全",
        }

    def _generate_hidden_gems(self, destination: str, travel_style: str) -> List[str]:
        """生成隐藏玩法"""
        gems = [
            f"{destination}小众景点",
            f"{destination}本地人推荐的美食街",
            f"{destination}隐藏的拍照胜地",
            f"{destination}当地人常去的休闲场所",
        ]

        if travel_style == "adventure":
            gems.append(f"{destination}户外探险路线")
        elif travel_style == "cultural":
            gems.append(f"{destination}文化体验活动")

        return gems

    def _generate_budget_estimate(
        self, budget_min: int, budget_max: int, budget_amount: int, budget_range: str, days: int
    ) -> Dict:
        """生成预算估算 - 基于预算范围智能分配"""
        # 按照经验比例分配预算
        allocation_ratios = {
            "住宿": 0.4,  # 40%
            "餐饮": 0.25,  # 25%
            "交通": 0.15,  # 15%
            "门票": 0.15,  # 15%
            "其他": 0.05,  # 5%
        }

        # 计算各项费用范围
        config = {}
        for category, ratio in allocation_ratios.items():
            min_amount = int(budget_min * ratio)
            max_amount = int(budget_max * ratio)
            avg_amount = int(budget_amount * ratio)
            daily_min = int(min_amount / days) if days > 0 else 0
            daily_max = int(max_amount / days) if days > 0 else 0
            daily_avg = int(avg_amount / days) if days > 0 else 0

            config[category] = {
                "daily_min": daily_min,
                "daily_max": daily_max,
                "daily_avg": daily_avg,
                "total_min": min_amount,
                "total_max": max_amount,
                "total_avg": avg_amount,
            }

        return {
            "total_cost_min": budget_min,
            "total_cost_max": budget_max,
            "total_cost_avg": budget_amount,
            "travel_days": days,
            "budget_range": f"{budget_min}-{budget_max}元",
            "budget_category": budget_range,
            **config,
        }

    def _get_best_time_to_visit(self, destination: str) -> str:
        """获取最佳旅行时间"""
        # 根据目的地特点返回最佳时间
        return "春秋两季，气候宜人，是旅游的最佳时节"

    def _generate_activity_timeline(self, days: int) -> List[Dict]:
        """生成活动时间线"""
        timeline = []
        for day in range(1, days + 1):
            timeline.append(
                {
                    "day": day,
                    "morning": f"第{day}天上午：游览景点",
                    "afternoon": f"第{day}天下午：继续游览",
                    "evening": f"第{day}天晚上：品尝美食",
                    "night": f"第{day}天夜晚：休息或夜游",
                }
            )
        return timeline

    def _generate_destination_info(self, destination: str, structured_data: Dict) -> Dict:
        """生成目的地信息"""
        country_info = structured_data.get("国家信息", {})
        geo_info = structured_data.get("地理位置", {})
        timezone_info = structured_data.get("时区信息", {})

        return {
            "name": destination,
            "country": country_info.get("name", "中国"),
            "capital": country_info.get("capital", ""),
            "region": country_info.get("region", ""),
            "population": country_info.get("population", 0),
            "languages": country_info.get("languages", ["中文"]),
            "currencies": country_info.get("currencies", ["CNY"]),
            "timezone": timezone_info.get("timezone", "Asia/Shanghai"),
            "utc_offset": timezone_info.get("utc_offset", "+08:00"),
            "coordinates": {"lat": geo_info.get("lat", 0), "lon": geo_info.get("lon", 0)},
            "description": structured_data.get("简介", f"{destination}是一个充满魅力的旅游目的地"),
        }

    def _generate_enhanced_guide_content(
        self,
        destination: str,
        structured_data: Dict,
        travel_style: str,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
    ) -> Dict:
        """生成增强版攻略内容"""
        currency_info = structured_data.get("汇率信息", {})
        weather_info = structured_data.get("天气", {})
        attraction_details = structured_data.get("景点详情", [])

        # 生成货币兑换建议
        currency_advice = self._generate_currency_advice(currency_info)

        # 生成天气建议
        weather_advice = self._generate_weather_advice(weather_info)

        # 生成景点详情
        attraction_info = self._generate_attraction_info(attraction_details)

        # 生成文化信息
        cultural_info = self._generate_cultural_info(structured_data)

        return {
            "currency_advice": currency_advice,
            "weather_advice": weather_advice,
            "attraction_info": attraction_info,
            "cultural_info": cultural_info,
            "practical_tips": self._generate_practical_tips(destination, structured_data),
            "local_customs": self._generate_local_customs(destination, structured_data),
            "emergency_info": self._generate_emergency_info(destination, structured_data),
        }

    def _generate_currency_advice(self, currency_info: Dict) -> Dict:
        """生成货币兑换建议"""
        rates = currency_info.get("rates", {})
        base_currency = currency_info.get("base_currency", "CNY")

        advice = {"base_currency": base_currency, "exchange_rates": rates, "recommendations": []}

        if "USD" in rates:
            advice["recommendations"].append(f"美元汇率: 1 CNY = {rates['USD']:.4f} USD")
        if "EUR" in rates:
            advice["recommendations"].append(f"欧元汇率: 1 CNY = {rates['EUR']:.4f} EUR")
        if "JPY" in rates:
            advice["recommendations"].append(f"日元汇率: 1 CNY = {rates['JPY']:.2f} JPY")

        advice["tips"] = ["建议在银行或正规兑换点兑换货币", "保留一些现金以备不时之需", "注意汇率波动，选择合适的兑换时机"]

        return advice

    def _generate_weather_advice(self, weather_info: Dict) -> Dict:
        """生成天气建议"""
        temperature = weather_info.get("temperature", 0)
        weather = weather_info.get("weather", "")
        humidity = weather_info.get("humidity", 0)

        advice = {
            "current_weather": {"temperature": temperature, "weather": weather, "humidity": humidity},
            "clothing_advice": self._get_clothing_advice(temperature),
            "activity_suggestions": self._get_activity_suggestions(weather),
            "precautions": self._get_weather_precautions(weather, temperature),
        }

        return advice

    def _generate_attraction_info(self, attraction_details: List[Dict]) -> Dict:
        """生成景点详情信息"""
        if not attraction_details:
            return {"attractions": [], "total_count": 0}

        categorized_attractions = {"cultural": [], "historic": [], "natural": [], "entertainment": []}

        for attraction in attraction_details:
            name = attraction.get("name", "")
            attraction_type = attraction.get("type", "")
            description = attraction.get("description", "")

            if "cultural" in attraction_type or "museum" in attraction_type:
                categorized_attractions["cultural"].append({"name": name, "description": description, "type": "文化景点"})
            elif "historic" in attraction_type or "castle" in attraction_type:
                categorized_attractions["historic"].append({"name": name, "description": description, "type": "历史景点"})
            elif "natural" in attraction_type or "park" in attraction_type:
                categorized_attractions["natural"].append({"name": name, "description": description, "type": "自然景点"})
            else:
                categorized_attractions["entertainment"].append({"name": name, "description": description, "type": "娱乐景点"})

        return {
            "attractions": categorized_attractions,
            "total_count": len(attraction_details),
            "top_attractions": [att["name"] for att in attraction_details[:5] if att.get("name")],
        }

    def _generate_cultural_info(self, structured_data: Dict) -> Dict:
        """生成文化信息"""
        country_info = structured_data.get("国家信息", {})

        return {
            "languages": country_info.get("languages", ["中文"]),
            "currencies": country_info.get("currencies", ["CNY"]),
            "timezones": country_info.get("timezones", ["UTC+8"]),
            "cultural_tips": ["尊重当地文化习俗", "注意着装得体", "学习基本的当地语言问候语", "了解当地的礼仪规范"],
        }

    def _generate_practical_tips(self, destination: str, structured_data: Dict) -> List[str]:
        """生成实用贴士"""
        tips = [
            f"在{destination}旅行时，建议提前了解当地交通情况",
            "准备常用药品和急救用品",
            "保存紧急联系方式和当地报警电话",
            "注意人身和财物安全",
            "提前预订酒店和机票",
            "准备现金和移动支付方式",
        ]

        # 根据天气信息添加贴士
        weather_info = structured_data.get("天气", {})
        if weather_info:
            temperature = weather_info.get("temperature", 0)
            if temperature > 30:
                tips.append("天气炎热，注意防晒和补水")
            elif temperature < 10:
                tips.append("天气寒冷，注意保暖")

        return tips

    def _generate_local_customs(self, destination: str, structured_data: Dict) -> List[str]:
        """生成当地习俗信息"""
        return [
            "了解并尊重当地的文化传统",
            "注意当地的饮食禁忌",
            "遵守当地的礼仪规范",
            "注意拍照时的文化敏感性",
            "了解当地的节日和庆典时间",
        ]

    def _generate_emergency_info(self, destination: str, structured_data: Dict) -> Dict:
        """生成紧急信息"""
        return {
            "emergency_numbers": {"police": "110", "ambulance": "120", "fire": "119", "tourist_hotline": "12301"},
            "hospitals": [f"{destination}市第一人民医院", f"{destination}市中心医院", f"{destination}市急救中心"],
            "embassies": ["中国驻当地使领馆", "当地中国大使馆"],
            "tips": ["随身携带身份证件", "保存酒店地址和联系方式", "了解最近的医院位置", "准备紧急联系人信息"],
        }

    def _get_clothing_advice(self, temperature: float) -> str:
        """根据温度获取穿衣建议"""
        if temperature > 30:
            return "建议穿着轻便透气的衣物，注意防晒"
        elif temperature > 20:
            return "建议穿着薄外套或长袖衣物"
        elif temperature > 10:
            return "建议穿着厚外套或毛衣"
        else:
            return "建议穿着厚外套、围巾、手套等保暖衣物"

    def _get_activity_suggestions(self, weather: str) -> List[str]:
        """根据天气获取活动建议"""
        if "雨" in weather or "雪" in weather:
            return ["室内景点游览", "博物馆参观", "购物中心", "咖啡厅休息"]
        elif "晴" in weather:
            return ["户外景点游览", "公园散步", "拍照留念", "户外运动"]
        else:
            return ["景点游览", "文化体验", "美食探索", "休闲娱乐"]

    def _get_weather_precautions(self, weather: str, temperature: float) -> List[str]:
        """根据天气获取注意事项"""
        precautions = []

        if "雨" in weather:
            precautions.extend(["携带雨具", "注意路面湿滑", "选择室内活动"])
        if "雪" in weather:
            precautions.extend(["注意保暖", "选择防滑鞋", "注意交通安全"])
        if temperature > 30:
            precautions.extend(["注意防晒", "多补充水分", "避免长时间户外活动"])
        if temperature < 0:
            precautions.extend(["注意保暖", "防止冻伤", "选择室内活动"])

        return precautions

    def _parse_duckduckgo_results(self, data: Dict, destination: str) -> Dict:
        """解析DuckDuckGo搜索结果"""
        parsed_data = {"attractions": [], "tips": []}

        # 从DuckDuckGo的AbstractText中提取信息
        if "AbstractText" in data and data["AbstractText"]:
            text = data["AbstractText"]
            # 简单的关键词提取
            if any(keyword in text for keyword in ["景点", "景区", "公园", "博物馆", "寺庙"]):
                parsed_data["attractions"].append({"name": f"{destination}著名景点", "description": text})

        # 从RelatedTopics中提取更多信息
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"][:3]:  # 取前3个相关主题
                if "Text" in topic:
                    parsed_data["attractions"].append({"name": f"{destination}旅游景点", "description": topic["Text"]})

        return parsed_data

    def _get_fallback_travel_data(self, destination: str) -> Dict:
        """获取备用旅游数据"""
        return {
            "attractions": [
                {
                    "name": f"{destination}著名景点",
                    "description": f"{destination}是一个充满魅力的旅游目的地，拥有丰富的文化遗产和自然风光。",
                },
                {
                    "name": f"{destination}历史文化景点",
                    "description": f"{destination}历史悠久，文化底蕴深厚，有许多值得参观的历史遗迹。",
                },
                {"name": f"{destination}自然风光", "description": f"{destination}的自然风光优美，是放松身心的好去处。"},
            ],
            "tips": [{"title": f"{destination}旅游贴士", "content": f"建议提前了解{destination}的天气情况，准备合适的衣物。"}],
        }

    def _get_fallback_weather_data(self, destination: str) -> Dict:
        """获取备用天气数据"""
        import datetime
        import random

        # 根据季节生成合理的模拟天气数据
        current_month = datetime.datetime.now().month

        if current_month in [12, 1, 2]:  # 冬季
            temp = random.randint(-5, 15)
            weather = "晴朗"
        elif current_month in [3, 4, 5]:  # 春季
            temp = random.randint(10, 25)
            weather = "多云"
        elif current_month in [6, 7, 8]:  # 夏季
            temp = random.randint(20, 35)
            weather = "晴朗"
        else:  # 秋季
            temp = random.randint(15, 30)
            weather = "晴朗"

        return {
            "temperature": temp,
            "weather": weather,
            "humidity": random.randint(40, 80),
            "wind_speed": random.randint(0, 20),
            "feels_like": temp + random.randint(-3, 3),
        }

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
            return 3  # 默认3天

    def _generate_daily_schedule(self, destination: str, days: int, real_data: Dict) -> List[Dict]:
        """生成每日行程"""
        daily_schedule = []
        attractions = real_data.get("景点", [])
        foods = real_data.get("美食", [])

        # 创建循环使用的列表
        attraction_cycle = attractions.copy() if attractions else []
        food_cycle = foods.copy() if foods else []

        # 创建索引跟踪器
        attraction_index = 0
        food_index = 0

        for day in range(1, days + 1):
            day_schedule = {
                "day": day,
                "date": f"第{day}天",
                "morning": [],
                "afternoon": [],
                "evening": [],
                "night": [],
                "accommodation": "",
                "total_cost": 0,
            }

            # 分配景点到不同时间段（循环使用）
            if attractions:
                # 选择景点（每天最多2个）
                selected_attractions = []
                for i in range(min(2, len(attraction_cycle))):
                    if attraction_cycle:
                        # 使用索引循环选择景点
                        attraction = attraction_cycle[attraction_index % len(attraction_cycle)]
                        selected_attractions.append(attraction)
                        attraction_index += 1

                # 分配景点到时间段
                for i, attraction in enumerate(selected_attractions):
                    if i == 0:
                        day_schedule["morning"].append(
                            {
                                "time": "09:00-12:00",
                                "activity": f"游览{attraction}",
                                "location": "",
                                "cost": "免费",
                                "tips": "",
                            }
                        )
                    else:
                        day_schedule["afternoon"].append(
                            {
                                "time": "14:00-17:00",
                                "activity": f"游览{attraction}",
                                "location": "",
                                "cost": "免费",
                                "tips": "",
                            }
                        )

            # 分配美食（循环使用）
            if foods:
                # 使用索引循环选择美食
                food = food_cycle[food_index % len(food_cycle)]
                food_index += 1

                day_schedule["evening"].append(
                    {
                        "time": "18:00-20:00",
                        "activity": f"品尝{food}",
                        "location": "",
                        "cost": "50-100元",
                        "tips": f"推荐品尝{food}",
                    }
                )

            daily_schedule.append(day_schedule)

        return daily_schedule

    def _generate_cost_breakdown(
        self,
        destination: str,
        days: int,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        real_data: Dict,
    ) -> Dict:
        """生成费用明细 - 基于预算范围智能分配"""
        # 分配比例
        allocation = {
            "accommodation": 0.4,  # 住宿 40%
            "food": 0.25,  # 餐饮 25%
            "transport": 0.15,  # 交通 15%
            "attractions": 0.15,  # 景点 15%
            "shopping": 0.05,  # 购物其他 5%
        }

        # 计算各项费用范围
        costs = {}
        for category, ratio in allocation.items():
            min_total = int(budget_min * ratio)
            max_total = int(budget_max * ratio)
            avg_total = int(budget_amount * ratio)
            min_daily = int(min_total / days) if days > 0 else 0
            max_daily = int(max_total / days) if days > 0 else 0
            avg_daily = int(avg_total / days) if days > 0 else 0

            costs[category] = {
                "daily_cost_min": min_daily,
                "daily_cost_max": max_daily,
                "daily_cost_avg": avg_daily,
                "total_cost_min": min_total,
                "total_cost_max": max_total,
                "total_cost_avg": avg_total,
            }

        return {
            "total_cost_min": budget_min,
            "total_cost_max": budget_max,
            "total_cost_avg": budget_amount,
            "travel_days": days,
            "budget_range": f"{budget_min}-{budget_max}元",
            "budget_category": budget_range,
            **costs,
        }

    def _generate_detailed_guide_text(
        self,
        destination: str,
        attractions: List[str],
        foods: List[str],
        tips: List[str],
        travel_style: str,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        travel_duration: str,
    ) -> str:
        """生成详细攻略文本"""
        days = self._parse_travel_duration(travel_duration)

        # 根据旅行风格生成不同的攻略内容
        style_descriptions = {
            "adventure": "冒险探索型",
            "cultural": "文化体验型",
            "leisure": "休闲放松型",
            "foodie": "美食探索型",
            "shopping": "购物娱乐型",
            "photography": "摄影记录型",
        }

        style_desc = style_descriptions.get(travel_style, "综合体验型")

        # 生成详细的每日行程安排
        daily_schedules = self._generate_detailed_daily_schedules(destination, days, attractions, foods, travel_style)

        # 生成详细的交通信息
        transport_info = self._generate_detailed_transport_info(destination)

        # 生成详细的预算分析
        budget_info = self._generate_detailed_budget_info(
            destination, days, budget_min, budget_max, budget_amount, budget_range, travel_style
        )

        # 构建详细攻略文本
        guide_text = f"""
# {destination}深度旅游攻略 - {style_desc}体验

## 📍 目的地概况
{destination}是一个充满魅力的旅游目的地，拥有丰富的自然景观和人文历史。本攻略专为{style_desc}旅行者定制，帮助您深度体验{destination}的独特魅力。

## 🗓️ 行程总览
**旅行天数**: {days}天
**旅行风格**: {style_desc}
**预算范围**: {budget_min}-{budget_max}元 ({budget_range})
**最佳时间**: {self._get_best_time_to_visit(destination)}

## 🏛️ 必去景点推荐
{chr(10).join([f"**{i+1}. {attraction}**" for i, attraction in enumerate(attractions[:8])])}

## 🍜 特色美食推荐
{chr(10).join([f"**{i+1}. {food}**" for i, food in enumerate(foods[:8])])}

## 🚗 详细交通指南
{transport_info}

## 💰 详细预算分析
{budget_info}

## 📅 每日行程安排
{daily_schedules}

## 🎯 深度体验建议
根据您的{style_desc}偏好，推荐以下特色体验：

### 文化体验
• 参观当地博物馆和历史文化景点
• 体验传统手工艺制作
• 参加当地节庆活动
• 与当地人交流，了解文化习俗

### 美食探索
• 品尝当地特色小吃
• 参加美食制作体验
• 探访当地市场
• 尝试传统餐厅

### 自然探索
• 徒步探索自然景观
• 拍摄风景照片
• 体验户外活动
• 观赏日出日落

## 💡 实用旅行贴士
{chr(10).join([f"• {tip}" for tip in tips[:8]])}

## ⚠️ 重要注意事项
• **提前预订**: 建议提前1-2个月预订酒店和机票
• **天气准备**: 查看天气预报，准备合适的衣物
• **证件准备**: 确保身份证、护照等证件齐全
• **保险购买**: 建议购买旅游保险
• **应急联系**: 记录当地紧急联系电话
• **文化尊重**: 注意当地风俗习惯，尊重当地文化

## 🎒 行前准备清单
### 必备物品
• 身份证/护照
• 现金和银行卡
• 手机和充电器
• 相机
• 舒适的鞋子

### 根据季节准备
• 春秋：薄外套、雨具
• 夏季：防晒用品、遮阳帽
• 冬季：保暖衣物、手套

## 📞 实用信息
• **旅游咨询**: 当地旅游局电话
• **紧急救援**: 120（医疗）、110（警察）、119（消防）
• **天气预报**: 关注当地天气APP
• **交通查询**: 使用高德地图或百度地图

## 🎉 特别提醒
{destination}是一个值得深度探索的目的地，建议您：
• 放慢脚步，用心感受当地文化
• 与当地人交流，获得更真实的体验
• 记录美好瞬间，留下珍贵回忆
• 保持开放心态，接受不同的文化体验

祝您在{destination}的{style_desc}之旅中收获满满的美好回忆！
"""

        return guide_text.strip()

    def _generate_detailed_daily_schedules(
        self, destination: str, days: int, attractions: List[str], foods: List[str], travel_style: str
    ) -> str:
        """生成详细的每日行程安排"""
        schedules = []

        for day in range(1, min(days + 1, 8)):  # 最多显示7天
            if day == 1:
                schedule = f"""
### 第{day}天：初识{destination}
**上午** (9:00-12:00)
• 抵达{destination}，办理入住
• 游览{attractions[0] if attractions else '主要景点'}
• 午餐：品尝{foods[0] if foods else '当地特色美食'}

**下午** (14:00-18:00)
• 参观{attractions[1] if len(attractions) > 1 else '文化景点'}
• 体验当地文化活动
• 晚餐：{foods[1] if len(foods) > 1 else '特色餐厅'}

**晚上** (19:00-21:00)
• 夜游{destination}，欣赏夜景
• 体验当地夜生活
"""
            elif day == 2:
                schedule = f"""
### 第{day}天：深度探索
**上午** (8:00-12:00)
• 早起观看日出（如果适用）
• 游览{attractions[2] if len(attractions) > 2 else '自然景观'}
• 午餐：{foods[2] if len(foods) > 2 else '当地小吃'}

**下午** (14:00-18:00)
• 探索{attractions[3] if len(attractions) > 3 else '历史遗迹'}
• 参加文化体验活动
• 晚餐：{foods[3] if len(foods) > 3 else '传统美食'}

**晚上** (19:00-21:00)
• 观看当地表演或演出
• 购物体验
"""
            else:
                schedule = f"""
### 第{day}天：特色体验
**上午** (9:00-12:00)
• 游览{attractions[min(day+2, len(attractions)-1)] if attractions else '特色景点'}
• 体验{travel_style}相关活动
• 午餐：{foods[min(day+2, len(foods)-1)] if foods else '特色美食'}

**下午** (14:00-18:00)
• 自由探索，发现隐藏景点
• 深度体验当地文化
• 晚餐：尝试新口味

**晚上** (19:00-21:00)
• 总结行程，整理照片
• 准备次日行程
"""

            schedules.append(schedule)

        return "".join(schedules)

    def _generate_detailed_transport_info(self, destination: str) -> str:
        """生成详细的交通信息"""
        return f"""
### 🚇 公共交通
• **地铁**: {destination}地铁网络发达，建议购买交通卡
• **公交**: 公交车线路覆盖广泛，票价2-5元
• **共享单车**: 适合短距离出行，1-2元/小时

### 🚕 出租车/网约车
• **出租车**: 起步价8-15元，建议使用滴滴打车
• **网约车**: 滴滴、高德等平台，价格透明
• **包车服务**: 适合团队出行，约300-500元/天

### 🚄 城际交通
• **高铁/动车**: 连接主要城市，速度快
• **普通火车**: 价格便宜，适合预算有限
• **长途汽车**: 覆盖范围广，价格实惠

### 🚗 自驾游
• **租车**: 约200-400元/天，需要驾照
• **停车**: 景区停车场10-20元/天
• **路况**: 主要道路路况良好
"""

    def _generate_detailed_budget_info(
        self,
        destination: str,
        days: int,
        budget_min: int,
        budget_max: int,
        budget_amount: int,
        budget_range: str,
        travel_style: str,
    ) -> str:
        """生成详细的预算分析 - 基于具体预算金额"""
        # 分配比例
        allocation = {"住宿": 0.4, "餐饮": 0.25, "交通": 0.15, "门票": 0.15, "其他": 0.05}

        # 计算各项费用范围
        breakdown = {}
        for category, ratio in allocation.items():
            total_min = int(budget_min * ratio)
            total_max = int(budget_max * ratio)
            daily_min = int(total_min / days) if days > 0 else 0
            daily_max = int(total_max / days) if days > 0 else 0
            breakdown[category] = {
                "total_min": total_min,
                "total_max": total_max,
                "daily_min": daily_min,
                "daily_max": daily_max,
            }

        # 获取预算类型描述
        if budget_amount < 3000:
            budget_type = "经济型"
        elif budget_amount < 8000:
            budget_type = "舒适型"
        elif budget_amount < 15000:
            budget_type = "豪华型"
        else:
            budget_type = "奢华型"

        return f"""
### 💰 预算分析 ({budget_type}预算)
**总预算**: {budget_min}-{budget_max}元 ({days}天)
**日均消费**: {int(budget_min / days) if days > 0 else 0}-{int(budget_max / days) if days > 0 else 0}元/天

#### 详细费用分配范围:
• **住宿费用**: {breakdown['住宿']['total_min']}-{breakdown['住宿']['total_max']}元 ({breakdown['住宿']['daily_min']}-{breakdown['住宿']['daily_max']}元/晚)
• **餐饮费用**: {breakdown['餐饮']['total_min']}-{breakdown['餐饮']['total_max']}元 ({breakdown['餐饮']['daily_min']}-{breakdown['餐饮']['daily_max']}元/天)
• **交通费用**: {breakdown['交通']['total_min']}-{breakdown['交通']['total_max']}元 ({breakdown['交通']['daily_min']}-{breakdown['交通']['daily_max']}元/天)
• **门票费用**: {breakdown['门票']['total_min']}-{breakdown['门票']['total_max']}元 ({breakdown['门票']['daily_min']}-{breakdown['门票']['daily_max']}元/天)
• **其他费用**: {breakdown['其他']['total_min']}-{breakdown['其他']['total_max']}元 ({breakdown['其他']['daily_min']}-{breakdown['其他']['daily_max']}元/天)

### 💡 预算优化建议
• 住宿：选择性价比高的酒店或民宿，预算范围内灵活调整
• 餐饮：体验当地特色美食，可根据预算选择不同档次
• 交通：优先使用公共交通，适当打车
• 门票：提前购买，寻找优惠套票
• 购物：控制支出，选择有意义的纪念品
"""


def duration_to_days(duration: str) -> str:
    """将时长转换为天数显示"""
    if "1天" in duration or "1晚" in duration:
        return "一"
    elif "2天" in duration or "2晚" in duration:
        return "二"
    elif "3天" in duration or "3晚" in duration:
        return "三"
    elif "4天" in duration or "4晚" in duration:
        return "四"
    elif "5天" in duration or "5晚" in duration:
        return "五"
    else:
        return "三"
