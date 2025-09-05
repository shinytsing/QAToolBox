#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控仪表板视图
"""


from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.tools.services.cache_service import CacheManager
from apps.tools.services.monitoring_service import monitoring_service


def is_admin(user):
    """检查用户是否为管理员"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def monitoring_dashboard(request):
    """监控仪表板页面"""
    return render(request, "tools/monitoring_dashboard.html")


@login_required
@user_passes_test(is_admin)
def get_monitoring_data(request):
    """获取监控数据API"""
    try:
        dashboard_data = monitoring_service.get_dashboard_data()
        return JsonResponse({"success": True, "data": dashboard_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_system_metrics(request):
    """获取系统指标"""
    try:
        metrics = monitoring_service.collect_all_metrics()
        return JsonResponse({"success": True, "data": metrics})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_alerts(request):
    """获取告警信息"""
    try:
        alerts = monitoring_service.check_all_alerts()
        return JsonResponse({"success": True, "data": alerts})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def get_cache_stats(request):
    """获取缓存统计"""
    try:
        cache_stats = CacheManager.get_cache_stats()
        return JsonResponse({"success": True, "data": cache_stats})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def clear_cache(request):
    """清除缓存"""
    try:
        results = CacheManager.clear_all_cache()
        return JsonResponse({"success": True, "data": results})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
@user_passes_test(is_admin)
def warm_up_cache(request):
    """预热缓存"""
    try:
        results = CacheManager.warm_up_cache()
        return JsonResponse({"success": True, "data": results})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class MonitoringAPIView(View):
    """监控API视图"""

    def get(self, request, *args, **kwargs):
        """获取监控数据"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "权限不足"}, status=403)

        data_type = kwargs.get("type", "dashboard")

        try:
            if data_type == "dashboard":
                data = monitoring_service.get_dashboard_data()
            elif data_type == "metrics":
                data = monitoring_service.collect_all_metrics()
            elif data_type == "alerts":
                data = monitoring_service.check_all_alerts()
            elif data_type == "cache":
                data = CacheManager.get_cache_stats()
            else:
                return JsonResponse({"error": "未知的数据类型"}, status=400)

            return JsonResponse({"success": True, "data": data})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def post(self, request, *args, **kwargs):
        """执行监控操作"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return JsonResponse({"error": "权限不足"}, status=403)

        action = kwargs.get("action")

        try:
            if action == "clear_cache":
                results = CacheManager.clear_all_cache()
            elif action == "warm_cache":
                results = CacheManager.warm_up_cache()
            else:
                return JsonResponse({"error": "未知的操作"}, status=400)

            return JsonResponse({"success": True, "data": results})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
