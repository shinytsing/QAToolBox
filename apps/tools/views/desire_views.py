"""
Desire相关视图
包含欲望仪表盘、欲望管理、欲望满足等功能
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 导入相关模型和服务
try:
    from apps.tools.services.desire_dashboard_service import DesireDashboardService
except ImportError:
    # 如果服务不存在，使用空类
    class DesireDashboardService:
        pass


@login_required
def desire_dashboard(request):
    """欲望仪表盘页面"""
    return render(request, "tools/desire_dashboard.html")


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_dashboard_api(request):
    """获取欲望仪表盘数据API"""
    try:
        service = DesireDashboardService()
        dashboard_data = service.get_dashboard_data(request.user)

        return JsonResponse({"success": True, "data": dashboard_data})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取数据失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_desire_api(request):
    """添加欲望API"""
    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description", "")
        category = data.get("category", "general")
        priority = data.get("priority", 1)

        if not title:
            return JsonResponse({"success": False, "message": "欲望标题不能为空"})

        service = DesireDashboardService()
        desire = service.add_desire(request.user, title, description, category, priority)

        return JsonResponse({"success": True, "desire_id": desire.id, "message": "欲望添加成功！"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"添加失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def check_desire_fulfillment_api(request):
    """检查欲望满足API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_type = data.get("task_type")
            task_details = data.get("task_details")

            if not task_type or not task_details:
                return JsonResponse({"success": False, "message": "缺少任务类型或详情"})

            service = DesireDashboardService()
            fulfilled_desires = service.check_desire_fulfillment(request.user, task_type, task_details)

            if fulfilled_desires:
                return JsonResponse(
                    {
                        "success": True,
                        "fulfilled_desires": [
                            {
                                "desire_title": item["desire"].title,
                                "fulfillment_id": item["fulfillment"].id,
                                "ai_prompt": item["fulfillment"].ai_prompt,
                            }
                            for item in fulfilled_desires
                        ],
                        "message": f"恭喜！满足了 {len(fulfilled_desires)} 个欲望！",
                    }
                )
            else:
                return JsonResponse({"success": True, "message": "继续努力，还没有满足的欲望"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"检查失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "只支持POST请求"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def generate_ai_image_api(request):
    """生成AI图片API"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            fulfillment_id = data.get("fulfillment_id")

            if not fulfillment_id:
                return JsonResponse({"success": False, "message": "缺少兑现记录ID"})

            service = DesireDashboardService()
            image_url = service.generate_ai_image(fulfillment_id)

            return JsonResponse({"success": True, "image_url": image_url, "message": "AI图片生成成功！"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"生成失败: {str(e)}"})

    return JsonResponse({"success": False, "message": "只支持POST请求"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_progress_api(request):
    """获取欲望进度API"""
    try:
        service = DesireDashboardService()
        progress = service.get_desire_progress(request.user)

        return JsonResponse({"success": True, "data": progress})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取进度失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_fulfillment_history_api(request):
    """获取兑现历史API"""
    try:
        service = DesireDashboardService()
        history = service.get_fulfillment_history(request.user)

        return JsonResponse({"success": True, "data": history})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取历史失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_todos_api(request):
    """获取欲望待办API"""
    try:
        service = DesireDashboardService()
        todos = service.get_desire_todos(request.user)

        return JsonResponse({"success": True, "data": todos})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取待办失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_desire_todo_api(request):
    """添加欲望待办API"""
    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description", "")
        due_date = data.get("due_date")

        if not title:
            return JsonResponse({"success": False, "message": "待办标题不能为空"})

        service = DesireDashboardService()
        todo = service.add_desire_todo(request.user, title, description, due_date)

        return JsonResponse({"success": True, "todo_id": todo.id, "message": "待办添加成功！"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"添加失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def complete_desire_todo_api(request):
    """完成欲望待办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get("todo_id")

        if not todo_id:
            return JsonResponse({"success": False, "message": "待办ID不能为空"})

        service = DesireDashboardService()
        result = service.complete_desire_todo(request.user, todo_id)

        return JsonResponse(
            {"success": True, "message": "待办完成！", "fulfilled_desires": result.get("fulfilled_desires", [])}
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"完成失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def delete_desire_todo_api(request):
    """删除欲望待办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get("todo_id")

        if not todo_id:
            return JsonResponse({"success": False, "message": "待办ID不能为空"})

        service = DesireDashboardService()
        service.delete_desire_todo(request.user, todo_id)

        return JsonResponse({"success": True, "message": "待办删除成功！"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"删除失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def edit_desire_todo_api(request):
    """编辑欲望待办API"""
    try:
        data = json.loads(request.body)
        todo_id = data.get("todo_id")
        title = data.get("title")
        description = data.get("description", "")
        due_date = data.get("due_date")

        if not todo_id or not title:
            return JsonResponse({"success": False, "message": "待办ID和标题不能为空"})

        service = DesireDashboardService()
        service.edit_desire_todo(request.user, todo_id, title, description, due_date)

        return JsonResponse({"success": True, "message": "待办编辑成功！"})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"编辑失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_desire_todo_stats_api(request):
    """获取欲望待办统计API"""
    try:
        service = DesireDashboardService()
        stats = service.get_desire_todo_stats(request.user)

        return JsonResponse({"success": True, "data": stats})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"获取统计失败: {str(e)}"})
