from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
@require_http_methods(["GET", "POST"])
def test_theme_api(request):
    """测试主题API - 不需要登录"""
    try:
        if request.method == "GET":
            return JsonResponse({"success": True, "theme": "work", "message": "测试获取主题成功"})
        elif request.method == "POST":
            data = json.loads(request.body)
            theme = data.get("theme") or data.get("mode", "work")

            # 验证主题是否有效
            valid_themes = ["work", "life", "training", "emo"]
            if theme not in valid_themes:
                return JsonResponse({"success": False, "error": f"无效的主题: {theme}"})

            return JsonResponse({"success": True, "theme": theme, "mode": theme, "message": f"测试主题切换成功: {theme}"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"服务器错误: {str(e)}"})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def switch_theme_api(request):
    """主题切换API"""
    try:
        data = json.loads(request.body)
        theme = data.get("theme")

        if not theme:
            return JsonResponse({"success": False, "error": "主题参数不能为空"})

        # 验证主题是否有效
        valid_themes = ["work", "life", "training", "emo"]
        if theme not in valid_themes:
            return JsonResponse({"success": False, "error": f"无效的主题: {theme}"})

        # 保存用户主题偏好到数据库（如果需要）
        # 这里可以扩展为保存到用户配置中

        # 返回成功响应
        return JsonResponse({"success": True, "theme": theme, "message": f"主题已切换到: {theme}"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"服务器错误: {str(e)}"})


@login_required
def get_user_theme_api(request):
    """获取用户当前主题API"""
    try:
        # 这里可以从数据库获取用户主题偏好
        # 暂时返回默认主题
        theme = request.session.get("user_theme", "work")

        return JsonResponse({"success": True, "theme": theme})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"服务器错误: {str(e)}"})


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def save_user_theme_api(request):
    """保存用户主题偏好API"""
    try:
        data = json.loads(request.body)
        theme = data.get("theme")

        if not theme:
            return JsonResponse({"success": False, "error": "主题参数不能为空"})

        # 验证主题是否有效
        valid_themes = ["work", "life", "training", "emo"]
        if theme not in valid_themes:
            return JsonResponse({"success": False, "error": f"无效的主题: {theme}"})

        # 保存到session
        request.session["user_theme"] = theme

        return JsonResponse({"success": True, "theme": theme, "message": f"主题偏好已保存: {theme}"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"服务器错误: {str(e)}"})
