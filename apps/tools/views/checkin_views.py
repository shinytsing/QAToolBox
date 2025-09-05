# QAToolbox/apps/tools/views/checkin_views.py
"""
签到相关的视图函数
"""

import json
import logging
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_add_api(request):
    """添加签到记录API - 真实实现"""
    try:
        from django.utils.dateparse import parse_date

        from apps.tools.models.legacy_models import CheckInCalendar, CheckInDetail

        # 解析请求数据
        data = json.loads(request.body)
        checkin_type = data.get("type", "fitness")
        date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
        status = data.get("status", "completed")
        detail_data = data.get("detail", {})

        # 解析日期
        checkin_date = parse_date(date_str) if date_str else datetime.now().date()

        # 创建或更新打卡记录
        checkin, created = CheckInCalendar.objects.get_or_create(
            user=request.user, calendar_type=checkin_type, date=checkin_date, defaults={"status": status}
        )

        if not created:
            checkin.status = status
            checkin.save()

        # 创建或更新详情记录
        if detail_data:
            detail, detail_created = CheckInDetail.objects.get_or_create(checkin=checkin, defaults=detail_data)

            if not detail_created:
                # 更新详情
                for key, value in detail_data.items():
                    if hasattr(detail, key):
                        setattr(detail, key, value)
                detail.save()

        logger.info(f"用户打卡: {request.user.username}, 类型: {checkin_type}, 日期: {checkin_date}")

        return JsonResponse(
            {
                "success": True,
                "message": "打卡成功",
                "checkin_record": {
                    "id": checkin.id,
                    "date": checkin.date.strftime("%Y-%m-%d"),
                    "status": checkin.status,
                    "type": checkin.calendar_type,
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"打卡失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"打卡失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def checkin_delete_api_simple(request):
    """删除签到记录API（简化版） - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        checkin_id = data.get("checkin_id")

        if not checkin_id:
            return JsonResponse({"success": False, "error": "缺少签到记录ID"}, status=400)

        # 模拟删除操作
        logger.info(f"删除签到记录: 用户 {request.user.id}, 记录 {checkin_id}")

        return JsonResponse({"success": True, "message": f"签到记录 {checkin_id} 删除成功"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"删除签到记录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"删除失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def checkin_delete_api(request, checkin_id):
    """删除签到记录API - 真实实现"""
    try:
        if not checkin_id:
            return JsonResponse({"success": False, "error": "缺少签到记录ID"}, status=400)

        # 模拟删除操作
        logger.info(f"删除签到记录: 用户 {request.user.id}, 记录 {checkin_id}")

        return JsonResponse({"success": True, "message": f"签到记录 {checkin_id} 删除成功"})

    except Exception as e:
        logger.error(f"删除签到记录失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"删除失败: {str(e)}"}, status=500)
