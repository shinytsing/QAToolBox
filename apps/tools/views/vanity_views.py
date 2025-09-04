"""
VanityOS相关视图
包含虚拟财富、罪恶积分、赞助者、欲望任务等功能
"""

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models

# 导入相关模型
try:
    from apps.tools.models import VanityWealth, SinPoints, Sponsor, VanityTask, BasedDevAvatar
except ImportError:
    # 如果模型不存在，使用空类
    class VanityWealth:
        pass

    class SinPoints:
        pass

    class Sponsor:
        pass

    class VanityTask:
        pass

    class BasedDevAvatar:
        pass


def vanity_os_dashboard(request):
    """VanityOS 主仪表盘页面 - 里世界入口（公开访问）"""
    return render(request, "tools/vanity_os_dashboard.html")


@login_required
def vanity_rewards(request):
    """罪恶积分系统页面"""
    return render(request, "tools/vanity_rewards.html")


@login_required
def sponsor_hall_of_fame(request):
    """金主荣耀墙页面"""
    return render(request, "tools/sponsor_hall_of_fame.html")


@login_required
def based_dev_avatar(request):
    """反程序员形象生成器页面"""
    return render(request, "tools/based_dev_avatar.html")


@login_required
def vanity_todo_list(request):
    """欲望驱动待办清单页面"""
    return render(request, "tools/vanity_todo_list.html")


@csrf_exempt
@require_http_methods(["GET"])
def get_vanity_wealth_api(request):
    """获取虚拟财富API（公开访问）"""
    try:
        # 如果没有登录用户，返回演示数据
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": True,
                    "virtual_wealth": 1250.50,
                    "code_lines": 125050,
                    "page_views": 50000,
                    "donations": 100.00,
                    "car_progress": 0.25,  # 玛莎拉蒂进度
                    "last_updated": timezone.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

        user = request.user
        wealth, created = VanityWealth.objects.get_or_create(user=user)

        # 计算虚拟财富
        wealth.calculate_wealth()
        wealth.save()

        return JsonResponse(
            {
                "success": True,
                "virtual_wealth": float(wealth.virtual_wealth),
                "code_lines": wealth.code_lines,
                "page_views": wealth.page_views,
                "donations": float(wealth.donations),
                "car_progress": min((float(wealth.virtual_wealth) / 500000) * 100, 100),  # 玛莎拉蒂进度
                "last_updated": wealth.last_updated.strftime("%Y-%m-%d %H:%M"),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def add_sin_points_api(request):
    """添加罪恶积分API（公开访问）"""
    try:
        data = json.loads(request.body)
        action_type = data.get("action_type")
        points = data.get("points", 0)
        metadata = data.get("metadata", {})

        if not action_type:
            return JsonResponse({"success": False, "error": "行为类型不能为空"})

        # 如果没有登录用户，返回演示响应
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": True,
                    "points_earned": points,
                    "total_points": 150,
                    "virtual_wealth": 1350.50,
                    "message": "演示模式：积分已记录",
                }
            )

        user = request.user

        # 创建罪恶积分记录
        sin_points = SinPoints.objects.create(user=user, action_type=action_type, points_earned=points, metadata=metadata)

        # 更新虚拟财富
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        if action_type == "code_line":
            wealth.code_lines += metadata.get("lines", 1)
        elif action_type == "donation":
            wealth.donations += metadata.get("amount", 0)

        wealth.calculate_wealth()
        wealth.save()

        return JsonResponse(
            {
                "success": True,
                "points_earned": points,
                "total_points": SinPoints.objects.filter(user=user).aggregate(total=models.Sum("points_earned"))["total"] or 0,
                "virtual_wealth": float(wealth.virtual_wealth),
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_sponsors_api(request):
    """获取赞助者列表API"""
    try:
        sponsors = Sponsor.objects.all().order_by("-amount", "-created_at")[:20]

        sponsors_data = []
        for sponsor in sponsors:
            sponsors_data.append(
                {
                    "id": sponsor.id,
                    "name": "匿名土豪" if sponsor.is_anonymous else sponsor.name,
                    "amount": float(sponsor.amount),
                    "message": sponsor.message,
                    "effect": sponsor.effect,
                    "created_at": sponsor.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse({"success": True, "sponsors": sponsors_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_sponsor_api(request):
    """添加赞助者API"""
    try:
        data = json.loads(request.body)
        name = data.get("name", "匿名土豪")
        amount = data.get("amount", 0)
        message = data.get("message", "")
        is_anonymous = data.get("is_anonymous", False)

        if amount <= 0:
            return JsonResponse({"success": False, "error": "赞助金额必须大于0"})

        # 根据金额确定特效类型
        if amount >= 1000:
            effect = "diamond-sparkle"
        elif amount >= 500:
            effect = "platinum-glow"
        elif amount >= 100:
            effect = "golden-bling"
        else:
            effect = "silver-shine"

        sponsor = Sponsor.objects.create(name=name, amount=amount, message=message, effect=effect, is_anonymous=is_anonymous)

        # 更新用户虚拟财富
        user = request.user
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        wealth.donations += amount
        wealth.calculate_wealth()
        wealth.save()

        return JsonResponse({"success": True, "sponsor_id": sponsor.id, "effect": effect})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_vanity_tasks_api(request):
    """获取欲望任务列表API"""
    try:
        user = request.user
        tasks = VanityTask.objects.filter(user=user, is_completed=False).order_by("-created_at")

        tasks_data = []
        for task in tasks:
            tasks_data.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.get_task_type_display(),
                    "difficulty": task.difficulty,
                    "reward_value": task.reward_value,
                    "reward_description": task.reward_description,
                    "created_at": task.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse({"success": True, "tasks": tasks_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def add_vanity_task_api(request):
    """添加欲望任务API"""
    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description", "")
        task_type = data.get("task_type")
        difficulty = data.get("difficulty", 1)

        if not title or not task_type:
            return JsonResponse({"success": False, "error": "任务标题和类型不能为空"})

        user = request.user

        # 根据难度生成奖励描述
        reward_descriptions = {
            1: "虚拟咖啡券",
            2: "星巴克虚拟券",
            3: "虚拟劳力士+3%豪车进度",
            4: "米其林虚拟体验",
            5: "虚拟游艇体验",
            6: "虚拟私人飞机",
            7: "虚拟岛屿",
            8: "虚拟太空旅行",
            9: "虚拟时间机器",
            10: "虚拟平行宇宙",
        }

        task = VanityTask.objects.create(
            user=user,
            title=title,
            description=description,
            task_type=task_type,
            difficulty=difficulty,
            reward_description=reward_descriptions.get(difficulty, "神秘奖励"),
        )

        # 计算奖励价值
        task.calculate_reward()
        task.save()

        return JsonResponse({"success": True, "task_id": task.id, "reward_value": task.reward_value})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def complete_vanity_task_api(request):
    """完成欲望任务API"""
    try:
        data = json.loads(request.body)
        task_id = data.get("task_id")

        if not task_id:
            return JsonResponse({"success": False, "error": "任务ID不能为空"})

        user = request.user
        task = VanityTask.objects.get(id=task_id, user=user, is_completed=False)

        # 标记任务完成
        task.is_completed = True
        task.completed_at = timezone.now()
        task.save()

        # 添加罪恶积分
        sin_points = SinPoints.objects.create(
            user=user,
            action_type="deep_work",
            points_earned=task.reward_value,
            metadata={"task_id": task_id, "task_title": task.title},
        )

        # 更新虚拟财富
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        wealth.code_lines += task.difficulty * 10  # 根据难度增加代码行数
        wealth.calculate_wealth()
        wealth.save()

        return JsonResponse(
            {
                "success": True,
                "points_earned": task.reward_value,
                "reward_description": task.reward_description,
                "virtual_wealth": float(wealth.virtual_wealth),
            }
        )
    except VanityTask.DoesNotExist:
        return JsonResponse({"success": False, "error": "任务不存在或已完成"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_based_dev_avatar_api(request):
    """创建反程序员形象API"""
    try:
        data = json.loads(request.body)
        code_snippet = data.get("code_snippet")
        caption = data.get("caption")

        if not code_snippet or not caption:
            return JsonResponse({"success": False, "error": "代码片段和配文不能为空"})

        user = request.user

        # 这里应该处理图片上传，暂时使用默认图片
        avatar = BasedDevAvatar.objects.create(user=user, code_snippet=code_snippet, caption=caption)

        return JsonResponse({"success": True, "avatar_id": avatar.id, "caption": caption})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_based_dev_avatar_api(request):
    """获取反程序员形象API"""
    try:
        user = request.user
        avatars = BasedDevAvatar.objects.filter(user=user).order_by("-created_at")[:10]

        avatars_data = []
        for avatar in avatars:
            avatars_data.append(
                {
                    "id": avatar.id,
                    "code_snippet": avatar.code_snippet,
                    "caption": avatar.caption,
                    "image_url": avatar.image.url if avatar.image else None,
                    "likes": avatar.likes,
                    "created_at": avatar.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse({"success": True, "avatars": avatars_data})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_based_dev_stats_api(request):
    """更新反程序员统计API"""
    try:
        data = json.loads(request.body)
        stats_type = data.get("stats_type")
        value = data.get("value", 0)

        if not stats_type:
            return JsonResponse({"success": False, "error": "统计类型不能为空"})

        user = request.user

        # 更新用户统计
        if stats_type == "code_lines":
            wealth, created = VanityWealth.objects.get_or_create(user=user)
            wealth.code_lines += value
            wealth.calculate_wealth()
            wealth.save()

        return JsonResponse({"success": True, "message": "统计更新成功"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def like_based_dev_avatar_api(request):
    """点赞反程序员形象API"""
    try:
        data = json.loads(request.body)
        avatar_id = data.get("avatar_id")

        if not avatar_id:
            return JsonResponse({"success": False, "error": "形象ID不能为空"})

        avatar = BasedDevAvatar.objects.get(id=avatar_id)
        avatar.likes += 1
        avatar.save()

        return JsonResponse({"success": True, "likes": avatar.likes})
    except BasedDevAvatar.DoesNotExist:
        return JsonResponse({"success": False, "error": "形象不存在"})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_based_dev_achievements_api(request):
    """获取反程序员成就API"""
    try:
        user = request.user

        # 计算成就
        achievements = []

        # 代码行数成就
        wealth, created = VanityWealth.objects.get_or_create(user=user)
        if wealth.code_lines >= 100000:
            achievements.append(
                {
                    "id": "code_master",
                    "title": "代码大师",
                    "description": "累计代码行数超过10万行",
                    "icon": "💻",
                    "unlocked_at": timezone.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

        # 虚拟财富成就
        if wealth.virtual_wealth >= 100000:
            achievements.append(
                {
                    "id": "wealth_master",
                    "title": "财富大师",
                    "description": "虚拟财富超过10万",
                    "icon": "💰",
                    "unlocked_at": timezone.now().strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse({"success": True, "achievements": achievements, "total_count": len(achievements)})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})
