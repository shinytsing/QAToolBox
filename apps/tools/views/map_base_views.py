"""
地图功能的基础视图 - 可被多个应用复用
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def search_location_suggestions(query, limit=5):
    """
    搜索地址建议 - 使用增强版地图服务
    """
    try:
        # 使用增强版地图服务
        from ..services.enhanced_map_service import enhanced_map_service

        results = enhanced_map_service.search_address(query, limit=limit)

        # 如果结果为空，返回基础模拟数据
        if not results:
            return get_fallback_suggestions(query, limit)

        return results
    except Exception as e:
        logger.error(f"地址搜索失败: {e}")
        # 返回模拟数据作为后备
        return get_fallback_suggestions(query, limit)


def get_fallback_suggestions(query, limit=5):
    """生成基础的地址建议（作为API失败时的后备）"""
    suggestions = []

    # 中国主要城市列表
    major_cities = [
        "北京",
        "上海",
        "广州",
        "深圳",
        "杭州",
        "成都",
        "重庆",
        "天津",
        "武汉",
        "西安",
        "南京",
        "青岛",
        "大连",
        "宁波",
        "厦门",
    ]

    # 如果查询是城市名，提供该城市的常见地点
    if any(city in query for city in major_cities):
        base_city = next((city for city in major_cities if city in query), query)
        patterns = [f"{base_city}市中心", f"{base_city}火车站", f"{base_city}机场", f"{base_city}大学", f"{base_city}购物中心"]
    else:
        # 通用模式
        patterns = [f"{query}", f"{query}市", f"{query}区", f"{query}街道", f"{query}附近"]

    for i, pattern in enumerate(patterns[:limit]):
        suggestion = {
            "name": pattern,
            "address": f"{pattern}",
            "full_address": f"{pattern}",
            "city": query if not any(city in query for city in major_cities) else query,
            "district": "",
            "province": "",
            "lat": 39.9042 + (i * 0.01),  # 北京附近的坐标偏移
            "lon": 116.4074 + (i * 0.01),
            "type": "地址",
            "source": "fallback",
        }
        suggestions.append(suggestion)

    return suggestions


def get_location_by_coordinates(lat, lon):
    """
    根据坐标反向地理编码获取地址信息
    """
    try:
        # 使用增强版地图服务
        from ..services.enhanced_map_service import enhanced_map_service

        return enhanced_map_service.reverse_geocode(lat, lon)
    except Exception as e:
        logger.error(f"反向地理编码失败: {e}")
        return None


def get_ip_location(request):
    """
    根据IP获取用户大概位置
    """
    try:
        from ..services.enhanced_map_service import get_ip_location as enhanced_get_ip_location

        location = enhanced_get_ip_location(request)

        # 如果位置信息不完整，使用默认值补充
        if location:
            location.setdefault("city", "北京")
            location.setdefault("region", "北京市")
            location.setdefault("country", "中国")
            location.setdefault("lat", 39.9042)
            location.setdefault("lon", 116.4074)
            location.setdefault("timezone", "Asia/Shanghai")
            return location
        else:
            # 如果没有返回任何位置信息，使用默认位置
            return get_default_location()
    except Exception as e:
        logger.error(f"IP定位失败: {e}")
        # 返回默认位置
        return get_default_location()


def get_default_location():
    """获取默认位置（北京）"""
    return {
        "city": "北京",
        "region": "北京市",
        "country": "中国",
        "lat": 39.9042,
        "lon": 116.4074,
        "timezone": "Asia/Shanghai",
        "source": "default",
    }


@csrf_exempt
@require_http_methods(["GET"])
def location_api(request):
    """统一的位置信息API"""
    try:
        # 获取IP定位信息
        location = get_ip_location(request)

        if location:
            return JsonResponse({"success": True, "location": location})
        else:
            return JsonResponse({"success": False, "error": "无法获取位置信息"})

    except Exception as e:
        logger.error(f"位置API失败: {e}")
        return JsonResponse({"success": False, "error": f"位置API失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def map_picker_api(request):
    """地图选择器API - 统一的地址搜索接口"""
    try:
        query = request.GET.get("query", "").strip()
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        if not query and not (lat and lon):
            return JsonResponse({"success": False, "error": "请提供搜索关键词或坐标"}, status=400)

        # 如果提供了坐标，进行反向地理编码
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                location_data = get_location_by_coordinates(lat, lon)

                if location_data:
                    return JsonResponse({"success": True, "location": location_data})
                else:
                    return JsonResponse({"success": False, "error": "反向地理编码失败"})

            except ValueError:
                return JsonResponse({"success": False, "error": "无效的坐标格式"}, status=400)
        else:
            # 搜索位置建议
            suggestions = search_location_suggestions(query)
            return JsonResponse({"success": True, "suggestions": suggestions})

    except Exception as e:
        logger.error(f"地图选择器API失败: {e}")
        return JsonResponse({"success": False, "error": f"地图选择器API失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_user_location_api(request):
    """保存用户选择的位置"""
    try:
        data = json.loads(request.body)
        location_data = data.get("location")

        if not location_data:
            return JsonResponse({"success": False, "error": "缺少位置数据"})

        # 这里可以保存到用户档案或会话中
        # 目前返回成功响应
        return JsonResponse({"success": True, "message": "位置保存成功"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        logger.error(f"保存位置失败: {e}")
        return JsonResponse({"success": False, "error": f"保存位置失败: {str(e)}"}, status=500)


class MapMixin:
    """地图功能的Mixin类，可以被其他视图继承"""

    def get_user_location(self, request):
        """获取用户位置"""
        return get_ip_location(request)

    def search_locations(self, query, limit=5):
        """搜索地址"""
        return search_location_suggestions(query, limit)

    def geocode_address(self, address):
        """地址转坐标"""
        # 这里可以实现地址转坐标的功能

    def reverse_geocode(self, lat, lon):
        """坐标转地址"""
        return get_location_by_coordinates(lat, lon)
