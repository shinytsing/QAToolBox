# QAToolbox/apps/tools/views/food_randomizer_views.py
"""
食物随机器相关的视图函数
"""

import json
import logging
import random
from datetime import datetime, timedelta

from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.tools.models import FoodRandomizationLog
from apps.tools.models.legacy_models import FoodHistory, FoodItem, FoodPhotoBinding, FoodRandomizationSession

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def food_randomizer_pure_random_api(request):
    """食物随机器纯随机API - 使用数据库数据"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        cuisine_type = data.get("cuisine_type", "all")
        meal_type = data.get("meal_type", "all")
        exclude_recent = data.get("exclude_recent", True)

        # 从数据库获取活跃的食物数据 - 使用FoodItem模型
        queryset = FoodItem.objects.all()

        # 处理cuisine_type过滤
        if cuisine_type != "all" and cuisine_type != "mixed":
            queryset = queryset.filter(cuisine=cuisine_type)
        # 如果是'mixed'，则不过滤cuisine类型，显示所有菜系

        # 处理meal_type过滤
        if meal_type != "all":
            # 将'lunch'映射到'main'，因为午餐通常是主食
            if meal_type == "lunch":
                meal_type = "main"
            # FoodItem模型使用meal_types JSON字段，需要特殊处理
            if meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                queryset = queryset.filter(meal_types__contains=[meal_type])

        # 排除最近食用的食物（如果需要的话）
        if exclude_recent and request.user.is_authenticated:
            # 获取用户最近3天内食用过的食物
            recent_cutoff = datetime.now() - timedelta(days=3)
            recent_food_ids = FoodRandomizationLog.objects.filter(
                user=request.user, created_at__gte=recent_cutoff, selected=True
            ).values_list("food_id", flat=True)
            queryset = queryset.exclude(id__in=recent_food_ids)

        # 转换为列表
        available_foods = list(queryset)

        if not available_foods:
            return JsonResponse({"success": False, "error": "没有找到符合条件的食物"}, status=404)

        # 随机选择食物
        selected_food = random.choice(available_foods)

        # 生成推荐理由
        reasons = [
            "营养均衡，适合当前季节",
            "制作简单，适合忙碌的生活",
            "口感丰富，满足味蕾需求",
            "健康美味，符合现代饮食理念",
            "经典菜品，值得一试",
            "富含蛋白质，有助于肌肉健康",
            "低脂健康，适合减肥期间",
            "高纤维食物，促进消化",
            "维生素丰富，增强免疫力",
        ]

        # 获取备选食物（除了选中的食物）
        alternative_foods = [f for f in available_foods if f.id != selected_food.id]
        alternatives = random.sample(alternative_foods, min(3, len(alternative_foods)))

        # 将选中的食物转换为字典格式 - 适配FoodItem模型
        def food_to_dict(food):
            # 获取绑定的图片
            binding = FoodPhotoBinding.objects.filter(food_item=food).first()
            image_url = f"/static/img/food/{binding.photo_name}" if binding else "/static/img/food/default-food.svg"

            return {
                "id": food.id,
                "name": food.name,
                "english_name": "",  # FoodItem模型没有这个字段
                "cuisine": food.cuisine,
                "meal_type": food.meal_types[0] if food.meal_types else "main",  # 取第一个餐型
                "calories": int(food.calories),
                "ingredients": food.ingredients,
                "description": food.description,
                "image_url": image_url,
                "difficulty": food.difficulty,
                "cooking_time": food.cooking_time,
                "health_score": 75,  # 默认健康评分
                "nutrition": {
                    "protein": food.protein,
                    "fat": food.fat,
                    "carbohydrates": food.carbohydrates,
                    "dietary_fiber": food.fiber,
                    "sugar": food.sugar,
                    "sodium": 0,  # FoodItem模型没有这个字段
                    "calcium": 0,  # FoodItem模型没有这个字段
                    "iron": 0,  # FoodItem模型没有这个字段
                    "vitamin_c": 0,  # FoodItem模型没有这个字段
                },
                "tags": food.tags,
                "is_vegetarian": "素食" in food.tags if food.tags else False,
                "is_high_protein": "高蛋白" in food.tags if food.tags else False,
                "is_low_carb": "低碳水" in food.tags if food.tags else False,
            }

        # 构建推荐结果
        recommendation = {
            "food": food_to_dict(selected_food),
            "reason": random.choice(reasons),
            "confidence": random.randint(70, 95),
            "alternatives": [food_to_dict(f) for f in alternatives],
            "generated_at": datetime.now().isoformat(),
            "nutrition_summary": {
                "macronutrients": {
                    "protein": (
                        round((selected_food.protein * 4 / selected_food.calories) * 100, 1)
                        if selected_food.calories > 0
                        else 0
                    ),
                    "fat": (
                        round((selected_food.fat * 9 / selected_food.calories) * 100, 1) if selected_food.calories > 0 else 0
                    ),
                    "carbs": (
                        round((selected_food.carbohydrates * 4 / selected_food.calories) * 100, 1)
                        if selected_food.calories > 0
                        else 0
                    ),
                },
                "health_score": 75,  # 默认健康评分
                "is_healthy": True,  # 默认认为是健康的
            },
        }

        # 记录推荐日志 - 使用FoodHistory模型
        recommendation["generated_at"]
        if request.user.is_authenticated:
            # 创建随机会话记录
            session = FoodRandomizationSession.objects.create(
                user=request.user,
                meal_type=meal_type if meal_type != "all" else "main",
                cuisine_preference=cuisine_type if cuisine_type != "all" else "mixed",
                status="completed",
                selected_food=selected_food,
                alternative_foods=[alt_food.id for alt_food in alternatives],
                completed_at=datetime.now(),
            )

            # 创建主推荐记录
            FoodHistory.objects.create(
                user=request.user,
                session=session,
                food_item=selected_food,
                meal_type=meal_type if meal_type != "all" else "main",
                rating=None,  # 初始没有评分
                feedback="",
                was_cooked=False,
            )

            # 为备选食物也创建日志记录
            for alt_food in alternatives:
                FoodHistory.objects.create(
                    user=request.user,
                    session=session,
                    food_item=alt_food,
                    meal_type=meal_type if meal_type != "all" else "main",
                    rating=None,
                    feedback="",
                    was_cooked=False,
                )

        logger.info(f"食物随机推荐: 选择 {selected_food.name} (ID: {selected_food.id})")

        return JsonResponse({"success": True, "recommendation": recommendation})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        logger.error(f"食物随机推荐失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"推荐失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def food_randomizer_statistics_api(request):
    """食物随机器统计API - 使用数据库数据"""
    try:
        # 获取总体统计 - 使用FoodItem模型
        total_foods = FoodItem.objects.count()
        total_recommendations = FoodHistory.objects.count()

        # 按菜系统计
        cuisine_stats = {}
        for cuisine, display_name in FoodItem.CUISINE_CHOICES:
            count = FoodItem.objects.filter(cuisine=cuisine).count()
            if count > 0:
                cuisine_stats[cuisine] = count

        # 按餐型统计
        meal_type_stats = {}
        for meal_type, display_name in FoodItem.MEAL_TYPE_CHOICES:
            count = FoodItem.objects.filter(meal_types__contains=[meal_type]).count()
            if count > 0:
                meal_type_stats[meal_type] = count

        # 最受欢迎的食物
        popular_food = FoodItem.objects.order_by("-popularity_score").first()

        # 用户特定统计（如果用户已登录）
        user_stats = {}
        if request.user.is_authenticated:
            user_recommendations = FoodHistory.objects.filter(user=request.user).count()
            user_stats = {"total_recommendations": user_recommendations, "favorite_cuisine": None, "healthy_choices": 0}

            # 用户最喜欢的菜系
            if user_recommendations > 0:
                user_cuisine_stats = (
                    FoodHistory.objects.filter(user=request.user)
                    .values("food_item__cuisine")
                    .annotate(count=models.Count("food_item__cuisine"))
                    .order_by("-count")
                    .first()
                )

                if user_cuisine_stats:
                    user_stats["favorite_cuisine"] = user_cuisine_stats["food_item__cuisine"]

            # 健康选择统计（所有食物都认为是健康的）
            user_stats["healthy_choices"] = user_recommendations

        # 周使用统计（最近7天）
        weekly_usage = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            count = FoodHistory.objects.filter(created_at__date=date).count()
            weekly_usage.append({"date": date.isoformat(), "count": count})
        weekly_usage.reverse()  # 按时间顺序排列

        stats_data = {
            "total_foods": total_foods,
            "total_recommendations": total_recommendations,
            "most_popular_food": popular_food.name if popular_food else None,
            "cuisine_distribution": cuisine_stats,
            "meal_type_distribution": meal_type_stats,
            "weekly_usage": weekly_usage,
            "user_stats": user_stats,
            "health_metrics": {
                "healthy_foods_count": FoodItem.objects.count(),  # 所有食物都认为是健康的
                "vegetarian_foods_count": FoodItem.objects.filter(tags__contains=["素食"]).count(),
                "high_protein_foods_count": FoodItem.objects.filter(tags__contains=["高蛋白"]).count(),
            },
        }

        logger.info(f"获取食物随机器统计: 用户 {request.user.username if request.user.is_authenticated else 'Anonymous'}")

        return JsonResponse({"success": True, "stats": stats_data})

    except Exception as e:
        logger.error(f"获取食物随机器统计失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取统计数据失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def food_randomizer_history_api(request):
    """食物随机器历史API - 使用数据库数据"""
    try:
        # 获取查询参数
        limit = int(request.GET.get("limit", 20))
        offset = int(request.GET.get("offset", 0))

        if request.user.is_authenticated:
            # 获取用户的推荐历史
            queryset = FoodHistory.objects.filter(user=request.user).select_related("food_item").order_by("-created_at")

            total_count = queryset.count()
            records = queryset[offset : offset + limit]

            history_records = []
            for record in records:
                # 获取绑定的图片
                binding = FoodPhotoBinding.objects.filter(food_item=record.food_item).first()
                image_url = f"/static/img/food/{binding.photo_name}" if binding else "/static/img/food/default-food.svg"

                history_records.append(
                    {
                        "id": record.id,
                        "food_name": record.food_item.name,
                        "cuisine": record.food_item.cuisine,
                        "meal_type": record.meal_type,
                        "calories": int(record.food_item.calories),
                        "health_score": 75,  # 默认健康评分
                        "rating": record.rating,
                        "selected": True,  # FoodHistory记录的都是被选择的
                        "created_at": record.created_at.isoformat(),
                        "session_id": record.created_at.isoformat(),  # 使用创建时间作为session_id
                        "image_url": image_url,
                        "nutrition_summary": {
                            "calories": record.food_item.calories,
                            "protein": record.food_item.protein,
                            "fat": record.food_item.fat,
                            "carbohydrates": record.food_item.carbohydrates,
                            "fiber": record.food_item.fiber,
                            "sodium": 0,
                        },
                    }
                )
        else:
            # 如果用户未登录，返回空历史
            total_count = 0
            history_records = []

        logger.info(
            f"获取食物随机器历史: 用户 {request.user.username if request.user.is_authenticated else 'Anonymous'}, 返回 {len(history_records)} 条记录"
        )

        return JsonResponse(
            {
                "success": True,
                "history": history_records,
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total_count,
                },
            }
        )

    except Exception as e:
        logger.error(f"获取食物随机器历史失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"获取历史失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def food_randomizer_rate_api(request):
    """食物随机器评分API"""
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")
        rating = data.get("rating")
        feedback = data.get("feedback", "")

        # 验证评分范围
        if rating is None or rating < 1 or rating > 5:
            return JsonResponse({"success": False, "error": "评分必须在1-5之间"}, status=400)

        # 查找对应的推荐记录
        if session_id:
            # 通过session_id查找记录（session_id通常是ISO格式的时间戳）
            try:
                from datetime import datetime, timedelta

                from django.utils import timezone

                # 解析session_id为datetime对象
                session_datetime = datetime.fromisoformat(session_id.replace("Z", "+00:00"))
                if session_datetime.tzinfo is None:
                    session_datetime = timezone.make_aware(session_datetime)

                # 查找在session时间前后1分钟内的记录（允许时间误差）
                time_range = timedelta(minutes=1)
                log_record = (
                    FoodHistory.objects.filter(
                        user=request.user, created_at__range=[session_datetime - time_range, session_datetime + time_range]
                    )
                    .order_by("-created_at")
                    .first()
                )

                # 如果没找到，尝试查找用户最新的记录
                if not log_record:
                    log_record = FoodHistory.objects.filter(user=request.user).order_by("-created_at").first()

            except (ValueError, TypeError):
                # 如果session_id不是有效的时间格式，查找用户最新的记录
                log_record = FoodHistory.objects.filter(user=request.user).order_by("-created_at").first()
        else:
            # 查找用户最新的推荐记录
            log_record = FoodHistory.objects.filter(user=request.user).order_by("-created_at").first()

        if not log_record:
            return JsonResponse({"success": False, "error": "未找到对应的推荐记录"}, status=404)

        # 更新评分和反馈
        log_record.rating = rating
        log_record.feedback = feedback
        log_record.save()

        # 更新食物的受欢迎度评分
        if log_record.food_item:
            # 计算该食物的平均评分
            all_ratings = FoodHistory.objects.filter(food_item=log_record.food_item, rating__isnull=False).values_list(
                "rating", flat=True
            )

            if all_ratings:
                avg_rating = sum(all_ratings) / len(all_ratings)
                # 将评分转换为0-1范围并更新popularity_score
                log_record.food_item.popularity_score = avg_rating / 5.0
                log_record.food_item.save()

        return JsonResponse(
            {
                "success": True,
                "message": "评分提交成功",
                "data": {
                    "session_id": session_id,
                    "rating": rating,
                    "feedback": feedback,
                    "food_name": log_record.food_item.name if log_record.food_item else None,
                },
            }
        )

    except Exception as e:
        logger.error(f"食物随机器评分失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"评分提交失败: {str(e)}"}, status=500)
