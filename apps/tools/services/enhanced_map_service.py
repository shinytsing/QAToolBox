"""
增强版地图服务 - 集成高德地图API，提供准确的地址定位和地图显示
"""

import requests
import json
import logging
from django.core.cache import cache
from django.conf import settings
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class EnhancedMapService:
    """增强版地图服务"""

    def __init__(self):
        # 高德地图API配置
        self.amap_key = getattr(settings, "AMAP_API_KEY", "a825cd9231f473717912d3203a62c53e")  # 更新后的有效key
        self.amap_base_url = "https://restapi.amap.com/v3"

        # 缓存配置
        self.cache_timeout = 3600  # 1小时缓存

        # 请求配置
        self.session = requests.Session()
        self.session.timeout = (5, 15)  # 连接超时5秒，读取超时15秒

    def search_address(self, query: str, city: str = None, limit: int = 10) -> List[Dict]:
        """
        搜索地址，返回准确的位置建议

        Args:
            query: 搜索关键词
            city: 限定城市（可选）
            limit: 返回结果数量限制

        Returns:
            包含地址信息的列表
        """
        cache_key = f"map_search_{query}_{city}_{limit}"

        # 检查缓存
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        results = []

        # 尝试高德地图API
        try:
            results = self._search_with_amap(query, city, limit)
            if results:
                cache.set(cache_key, results, self.cache_timeout)
                logger.info(f"高德地图搜索成功，返回{len(results)}个结果")
                return results
        except Exception as e:
            logger.warning(f"高德地图搜索失败: {e}")

        # 如果高德地图失败，返回模拟数据
        results = self._get_fallback_suggestions(query, city, limit)
        cache.set(cache_key, results, self.cache_timeout)
        return results

    def _search_with_amap(self, query: str, city: str = None, limit: int = 10) -> List[Dict]:
        """使用高德地图API搜索地址"""
        url = f"{self.amap_base_url}/place/text"
        params = {"key": self.amap_key, "keywords": query, "offset": limit, "page": 1, "extensions": "all", "output": "json"}

        if city:
            params["city"] = city

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            raise Exception(f"高德API错误: {data.get('info', 'Unknown error')}")

        results = []
        for place in data.get("pois", []):
            # 解析坐标
            location = place.get("location", "").split(",")
            if len(location) >= 2:
                try:
                    lon, lat = float(location[0]), float(location[1])
                except (ValueError, IndexError):
                    continue

                # 构建结果
                result = {
                    "name": place.get("name", ""),
                    "address": place.get("address", ""),
                    "full_address": f"{place.get('address', '')} {place.get('name', '')}".strip(),
                    "city": place.get("cityname", city or ""),
                    "district": place.get("adname", ""),
                    "province": place.get("pname", ""),
                    "lat": lat,
                    "lon": lon,
                    "type": place.get("type", ""),
                    "source": "amap",
                }
                results.append(result)

        return results

    def _get_fallback_suggestions(self, query: str, city: str = None, limit: int = 10) -> List[Dict]:
        """获取备用地址建议（当API不可用时）"""
        # 导入IP位置服务用于获取基础坐标
        from .ip_location_service import IPLocationService

        ip_service = IPLocationService()

        # 获取城市基础坐标
        base_location = ip_service.get_location_by_city_name(city or query)
        base_lat = base_location.get("lat", 39.9042)
        base_lon = base_location.get("lon", 116.4074)

        suggestions = []

        # 生成常见地址模式
        patterns = [
            f"{query}",
            f"{query}市中心",
            f"{query}火车站",
            f"{query}机场",
            f"{query}汽车站",
            f"{query}大学",
            f"{query}购物中心",
            f"{query}医院",
            f"{query}政府",
            f"{query}体育馆",
        ]

        for i, pattern in enumerate(patterns[:limit]):
            # 为每个建议生成稍微不同的坐标
            offset = i * 0.01
            suggestion = {
                "name": pattern,
                "address": f'{city or ""}市{pattern}',
                "full_address": f'{city or ""}市{pattern}',
                "city": city or query,
                "district": "市中心",
                "province": "",
                "lat": base_lat + offset,
                "lon": base_lon + offset,
                "type": "地址",
                "source": "fallback",
            }
            suggestions.append(suggestion)

        return suggestions

    def geocode(self, address: str) -> Optional[Dict]:
        """
        地址转坐标（地理编码）

        Args:
            address: 地址字符串

        Returns:
            包含坐标的字典，或None
        """
        cache_key = f"geocode_{address}"

        # 检查缓存
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # 尝试高德地图API
        try:
            result = self._geocode_with_amap(address)
            if result:
                cache.set(cache_key, result, self.cache_timeout)
                return result
        except Exception as e:
            logger.warning(f"高德地理编码失败: {e}")

        return None

    def _geocode_with_amap(self, address: str) -> Optional[Dict]:
        """使用高德地图进行地理编码"""
        url = f"{self.amap_base_url}/geocode/geo"
        params = {"key": self.amap_key, "address": address, "output": "json"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            raise Exception(f"高德API错误: {data.get('info', 'Unknown error')}")

        geocodes = data.get("geocodes", [])
        if not geocodes:
            return None

        geocode = geocodes[0]
        location = geocode.get("location", "").split(",")

        if len(location) >= 2:
            try:
                lon, lat = float(location[0]), float(location[1])
                return {
                    "lat": lat,
                    "lon": lon,
                    "formatted_address": geocode.get("formatted_address", address),
                    "province": geocode.get("province", ""),
                    "city": geocode.get("city", ""),
                    "district": geocode.get("district", ""),
                    "level": geocode.get("level", ""),
                    "source": "amap",
                }
            except (ValueError, IndexError):
                pass

        return None

    def reverse_geocode(self, lat: float, lon: float) -> Optional[Dict]:
        """
        坐标转地址（逆地理编码）

        Args:
            lat: 纬度
            lon: 经度

        Returns:
            包含地址信息的字典，或None
        """
        cache_key = f"reverse_geocode_{lat}_{lon}"

        # 检查缓存
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # 尝试高德地图API
        try:
            result = self._reverse_geocode_with_amap(lat, lon)
            if result:
                cache.set(cache_key, result, self.cache_timeout)
                return result
        except Exception as e:
            logger.warning(f"高德逆地理编码失败: {e}")

        return None

    def _reverse_geocode_with_amap(self, lat: float, lon: float) -> Optional[Dict]:
        """使用高德地图进行逆地理编码"""
        url = f"{self.amap_base_url}/geocode/regeo"
        params = {"key": self.amap_key, "location": f"{lon},{lat}", "output": "json", "extensions": "all"}

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            raise Exception(f"高德API错误: {data.get('info', 'Unknown error')}")

        regeocode = data.get("regeocode")
        if not regeocode:
            return None

        addressComponent = regeocode.get("addressComponent", {})

        return {
            "formatted_address": regeocode.get("formatted_address", ""),
            "province": addressComponent.get("province", ""),
            "city": addressComponent.get("city", ""),
            "district": addressComponent.get("district", ""),
            "township": addressComponent.get("township", ""),
            "neighborhood": addressComponent.get("neighborhood", {}).get("name", ""),
            "building": addressComponent.get("building", {}).get("name", ""),
            "lat": lat,
            "lon": lon,
            "source": "amap",
        }

    def get_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        计算两点间距离（公里）

        Args:
            lat1, lon1: 第一个点的坐标
            lat2, lon2: 第二个点的坐标

        Returns:
            距离（公里）
        """
        from math import radians, cos, sin, asin, sqrt

        # 将经纬度转换为弧度
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球半径（公里）

        return c * r

    def get_poi_nearby(self, lat: float, lon: float, keyword: str = "", radius: int = 1000) -> List[Dict]:
        """
        获取附近的兴趣点

        Args:
            lat: 纬度
            lon: 经度
            keyword: 搜索关键词
            radius: 搜索半径（米）

        Returns:
            附近兴趣点列表
        """
        cache_key = f"poi_nearby_{lat}_{lon}_{keyword}_{radius}"

        # 检查缓存
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        # 尝试高德地图API
        try:
            results = self._get_poi_with_amap(lat, lon, keyword, radius)
            if results:
                cache.set(cache_key, results, self.cache_timeout)
                return results
        except Exception as e:
            logger.warning(f"高德POI搜索失败: {e}")

        return []

    def _get_poi_with_amap(self, lat: float, lon: float, keyword: str = "", radius: int = 1000) -> List[Dict]:
        """使用高德地图API获取附近POI"""
        url = f"{self.amap_base_url}/place/around"
        params = {
            "key": self.amap_key,
            "location": f"{lon},{lat}",
            "radius": radius,
            "offset": 20,
            "page": 1,
            "extensions": "all",
            "output": "json",
        }

        if keyword:
            params["keywords"] = keyword

        response = self.session.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data.get("status") != "1":
            raise Exception(f"高德API错误: {data.get('info', 'Unknown error')}")

        results = []
        for place in data.get("pois", []):
            # 解析坐标
            location = place.get("location", "").split(",")
            if len(location) >= 2:
                try:
                    poi_lon, poi_lat = float(location[0]), float(location[1])
                except (ValueError, IndexError):
                    continue

                # 计算距离
                distance = self.get_distance(lat, lon, poi_lat, poi_lon) * 1000  # 转换为米

                # 构建结果
                result = {
                    "name": place.get("name", ""),
                    "address": place.get("address", ""),
                    "type": place.get("type", ""),
                    "lat": poi_lat,
                    "lon": poi_lon,
                    "distance": distance,
                    "tel": place.get("tel", ""),
                    "business_area": place.get("business_area", ""),
                    "source": "amap",
                }
                results.append(result)

        return results


# 全局实例
enhanced_map_service = EnhancedMapService()


# 便利函数
def search_location_suggestions(query: str, city: str = None, limit: int = 10) -> List[Dict]:
    """搜索地址建议"""
    return enhanced_map_service.search_address(query, city, limit)


def get_location_by_coordinates(lat: float, lon: float) -> Optional[Dict]:
    """根据坐标获取地址信息"""
    return enhanced_map_service.reverse_geocode(lat, lon)


def geocode_address(address: str) -> Optional[Dict]:
    """地址转坐标"""
    return enhanced_map_service.geocode(address)


def get_ip_location(request):
    """获取用户IP位置"""
    from .ip_location_service import IPLocationService

    ip_service = IPLocationService()
    return ip_service.get_user_location(request)
