import json
import logging

from django.conf import settings
from django.core.cache import cache

import requests

logger = logging.getLogger(__name__)


class IPLocationService:
    """IP定位服务"""

    def __init__(self):
        self.cache_timeout = 3600 * 24  # 24小时缓存
        self.api_urls = [
            "http://ip-api.com/json/",
            "https://ipapi.co/json/",
            "https://api.ipify.org?format=json",
            "https://ipinfo.io/json",
            "https://api.myip.com",
        ]

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def get_location_by_ip(self, ip):
        """根据IP获取地理位置信息"""
        cache_key = f"ip_location_{ip}"

        # 检查缓存
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # 本地IP地址处理
        if ip in ["127.0.0.1", "localhost", "::1"]:
            location_data = {
                "city": "北京",
                "region": "北京市",
                "country": "中国",
                "lat": 39.9042,
                "lon": 116.4074,
                "timezone": "Asia/Shanghai",
            }
            cache.set(cache_key, location_data, self.cache_timeout)
            return location_data

        # 尝试多个API获取位置信息
        for api_url in self.api_urls:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()

                    if "ip-api.com" in api_url:
                        if data.get("status") == "success":
                            location_data = {
                                "city": data.get("city", "未知"),
                                "region": data.get("regionName", "未知"),
                                "country": data.get("country", "未知"),
                                "lat": data.get("lat", 0),
                                "lon": data.get("lon", 0),
                                "timezone": data.get("timezone", "Asia/Shanghai"),
                                "isp": data.get("isp", ""),
                            }
                        else:
                            continue
                    elif "ipapi.co" in api_url:
                        location_data = {
                            "city": data.get("city", "未知"),
                            "region": data.get("region", "未知"),
                            "country": data.get("country_name", "未知"),
                            "lat": data.get("latitude", 0),
                            "lon": data.get("longitude", 0),
                            "timezone": data.get("timezone", "Asia/Shanghai"),
                            "isp": data.get("org", ""),
                        }
                    elif "ipinfo.io" in api_url:
                        location_data = {
                            "city": data.get("city", "未知"),
                            "region": data.get("region", "未知"),
                            "country": data.get("country", "未知"),
                            "lat": float(data.get("loc", "0,0").split(",")[0]) if data.get("loc") else 0,
                            "lon": float(data.get("loc", "0,0").split(",")[1]) if data.get("loc") else 0,
                            "timezone": data.get("timezone", "Asia/Shanghai"),
                            "isp": data.get("org", ""),
                        }
                    elif "myip.com" in api_url:
                        location_data = {
                            "city": data.get("city", "未知"),
                            "region": data.get("region", "未知"),
                            "country": data.get("country", "未知"),
                            "lat": data.get("lat", 0),
                            "lon": data.get("lon", 0),
                            "timezone": data.get("timezone", "Asia/Shanghai"),
                            "isp": data.get("isp", ""),
                        }
                    else:
                        # 如果只获取到IP，使用默认位置
                        location_data = {
                            "city": "未知",
                            "region": "未知",
                            "country": "中国",
                            "lat": 39.9042,
                            "lon": 116.4074,
                            "timezone": "Asia/Shanghai",
                            "isp": "",
                        }

                    # 缓存结果
                    cache.set(cache_key, location_data, self.cache_timeout)
                    return location_data

            except Exception as e:
                logger.warning(f"IP定位API {api_url} 失败: {str(e)}")
                continue

        # 所有API都失败，返回默认位置
        default_location = {
            "city": "未知",
            "region": "未知",
            "country": "中国",
            "lat": 39.9042,
            "lon": 116.4074,
            "timezone": "Asia/Shanghai",
            "isp": "",
        }
        cache.set(cache_key, default_location, self.cache_timeout)
        return default_location

    def get_user_location(self, request):
        """获取用户位置信息"""
        ip = self.get_client_ip(request)
        return self.get_location_by_ip(ip)

    def get_nearby_items(self, request, items, radius_km=50):
        """获取附近的物品（基于IP定位）"""
        user_location = self.get_user_location(request)

        if not user_location or user_location["city"] == "未知":
            return items

        # 这里可以添加基于地理位置的筛选逻辑
        # 目前返回所有物品，但标记距离信息
        for item in items:
            # 计算距离（简化版本）
            if hasattr(item, "latitude") and hasattr(item, "longitude"):
                distance = self.calculate_distance(user_location["lat"], user_location["lon"], item.latitude, item.longitude)
                item.distance = f"{distance:.1f}km"
            else:
                item.distance = "距离未知"

        return items

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """计算两点间距离（公里）"""
        from math import asin, cos, radians, sin, sqrt

        # 将经纬度转换为弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球半径（公里）

        return c * r

    def get_location_by_city_name(self, city_name):
        """根据城市名称获取地理位置信息"""
        cache_key = f"city_location_{city_name}"

        # 检查缓存
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        # 城市坐标映射
        city_coordinates = {
            "北京": {"lat": 39.9042, "lon": 116.4074, "region": "北京市"},
            "上海": {"lat": 31.2304, "lon": 121.4737, "region": "上海市"},
            "广州": {"lat": 23.1291, "lon": 113.2644, "region": "广东省"},
            "深圳": {"lat": 22.3193, "lon": 114.1694, "region": "广东省"},
            "杭州": {"lat": 30.2741, "lon": 120.1551, "region": "浙江省"},
            "南京": {"lat": 32.0603, "lon": 118.7969, "region": "江苏省"},
            "武汉": {"lat": 30.5928, "lon": 114.3055, "region": "湖北省"},
            "成都": {"lat": 30.5728, "lon": 104.0668, "region": "四川省"},
            "西安": {"lat": 34.3416, "lon": 108.9398, "region": "陕西省"},
            "重庆": {"lat": 29.4316, "lon": 106.9123, "region": "重庆市"},
            "天津": {"lat": 39.0842, "lon": 117.2009, "region": "天津市"},
            "苏州": {"lat": 31.2990, "lon": 120.5853, "region": "江苏省"},
            "青岛": {"lat": 36.0671, "lon": 120.3826, "region": "山东省"},
            "大连": {"lat": 38.9140, "lon": 121.6147, "region": "辽宁省"},
            "厦门": {"lat": 24.4798, "lon": 118.0894, "region": "福建省"},
            "宁波": {"lat": 29.8683, "lon": 121.5440, "region": "浙江省"},
            "无锡": {"lat": 31.4900, "lon": 120.3119, "region": "江苏省"},
            "长沙": {"lat": 28.2278, "lon": 112.9388, "region": "湖南省"},
            "郑州": {"lat": 34.7472, "lon": 113.6254, "region": "河南省"},
            "济南": {"lat": 36.6510, "lon": 117.1201, "region": "山东省"},
            "哈尔滨": {"lat": 45.8038, "lon": 126.5350, "region": "黑龙江省"},
            "沈阳": {"lat": 41.8057, "lon": 123.4315, "region": "辽宁省"},
            "昆明": {"lat": 25.0389, "lon": 102.7183, "region": "云南省"},
            "合肥": {"lat": 31.8206, "lon": 117.2272, "region": "安徽省"},
            "福州": {"lat": 26.0745, "lon": 119.2965, "region": "福建省"},
            "南昌": {"lat": 28.6820, "lon": 115.8579, "region": "江西省"},
            "石家庄": {"lat": 38.0428, "lon": 114.5149, "region": "河北省"},
            "太原": {"lat": 37.8706, "lon": 112.5489, "region": "山西省"},
            "长春": {"lat": 43.8171, "lon": 125.3235, "region": "吉林省"},
            "贵阳": {"lat": 26.6470, "lon": 106.6302, "region": "贵州省"},
            "南宁": {"lat": 22.8170, "lon": 108.3665, "region": "广西壮族自治区"},
            "兰州": {"lat": 36.0611, "lon": 103.8343, "region": "甘肃省"},
            "银川": {"lat": 38.4872, "lon": 106.2309, "region": "宁夏回族自治区"},
            "西宁": {"lat": 36.6232, "lon": 101.7803, "region": "青海省"},
            "乌鲁木齐": {"lat": 43.8256, "lon": 87.6168, "region": "新疆维吾尔自治区"},
            "拉萨": {"lat": 29.6500, "lon": 91.1000, "region": "西藏自治区"},
            "呼和浩特": {"lat": 40.8429, "lon": 111.7492, "region": "内蒙古自治区"},
            "海口": {"lat": 20.0440, "lon": 110.1920, "region": "海南省"},
            "三亚": {"lat": 18.2528, "lon": 109.5119, "region": "海南省"},
            "珠海": {"lat": 22.2707, "lon": 113.5767, "region": "广东省"},
            "佛山": {"lat": 23.0218, "lon": 113.1214, "region": "广东省"},
            "东莞": {"lat": 23.0207, "lon": 113.7518, "region": "广东省"},
            "中山": {"lat": 22.5176, "lon": 113.3928, "region": "广东省"},
            "惠州": {"lat": 23.1115, "lon": 114.4162, "region": "广东省"},
            "江门": {"lat": 22.5787, "lon": 113.0819, "region": "广东省"},
            "肇庆": {"lat": 23.0472, "lon": 112.4651, "region": "广东省"},
            "清远": {"lat": 23.6820, "lon": 113.0560, "region": "广东省"},
            "韶关": {"lat": 24.8108, "lon": 113.5972, "region": "广东省"},
            "湛江": {"lat": 21.2707, "lon": 110.3594, "region": "广东省"},
            "茂名": {"lat": 21.6630, "lon": 110.9254, "region": "广东省"},
            "阳江": {"lat": 21.8579, "lon": 111.9822, "region": "广东省"},
            "云浮": {"lat": 22.9150, "lon": 112.0444, "region": "广东省"},
            "潮州": {"lat": 23.6571, "lon": 116.6226, "region": "广东省"},
            "揭阳": {"lat": 23.5498, "lon": 116.3728, "region": "广东省"},
            "汕尾": {"lat": 22.7787, "lon": 115.3753, "region": "广东省"},
            "河源": {"lat": 23.7435, "lon": 114.6978, "region": "广东省"},
            "梅州": {"lat": 24.2886, "lon": 116.1222, "region": "广东省"},
        }

        # 查找城市坐标
        for city, coords in city_coordinates.items():
            if city_name in city or city in city_name:
                location_data = {
                    "city": city,
                    "region": coords["region"],
                    "country": "中国",
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "timezone": "Asia/Shanghai",
                    "isp": "",
                }
                cache.set(cache_key, location_data, self.cache_timeout)
                return location_data

        # 如果没找到，返回默认位置
        default_location = {
            "city": city_name,
            "region": "用户设置",
            "country": "中国",
            "lat": 39.9042,
            "lon": 116.4074,
            "timezone": "Asia/Shanghai",
            "isp": "",
        }
        cache.set(cache_key, default_location, self.cache_timeout)
        return default_location
