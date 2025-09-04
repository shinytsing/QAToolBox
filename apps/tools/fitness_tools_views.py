import json
import logging
import math

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@login_required
def fitness_tools_dashboard(request):
    """健身工具主页面"""
    return render(request, "tools/fitness_tools_dashboard.html")


@login_required
def bmi_calculator(request):
    """BMI计算器页面"""
    return render(request, "tools/bmi_calculator.html")


@login_required
def workout_timer(request):
    """训练计时器页面"""
    return render(request, "tools/workout_timer.html")


@login_required
def nutrition_calculator(request):
    """营养计算器页面"""
    return render(request, "tools/nutrition_calculator.html")


@login_required
def workout_tracker(request):
    """训练追踪器页面"""
    return render(request, "tools/workout_tracker.html")


@login_required
def body_analyzer(request):
    """身体成分分析页面"""
    return render(request, "tools/body_analyzer.html")


@login_required
def workout_planner(request):
    """训练计划器页面"""
    return render(request, "tools/workout_planner.html")


@login_required
def one_rm_calculator(request):
    """1RM计算器页面"""
    return render(request, "tools/one_rm_calculator.html")


# API视图函数
@csrf_exempt
@require_http_methods(["POST"])
def calculate_bmi_api(request):
    """BMI计算API"""
    try:
        data = json.loads(request.body)
        height = float(data.get("height", 0))  # 厘米
        weight = float(data.get("weight", 0))  # 公斤

        if height <= 0 or weight <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的身高和体重"})

        # 计算BMI
        height_m = height / 100
        bmi = weight / (height_m * height_m)

        # BMI分类
        if bmi < 18.5:
            category = "体重过轻"
            health_risk = "低"
            suggestion = "建议适当增加营养摄入，进行力量训练增肌"
        elif bmi < 24:
            category = "正常体重"
            health_risk = "正常"
            suggestion = "保持健康的生活方式，定期运动"
        elif bmi < 28:
            category = "超重"
            health_risk = "中等"
            suggestion = "建议控制饮食，增加有氧运动"
        else:
            category = "肥胖"
            health_risk = "高"
            suggestion = "建议咨询医生，制定减重计划"

        # 计算理想体重范围
        min_weight = 18.5 * height_m * height_m
        max_weight = 24 * height_m * height_m

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "bmi": round(bmi, 1),
                    "category": category,
                    "health_risk": health_risk,
                    "suggestion": suggestion,
                    "ideal_weight_range": {"min": round(min_weight, 1), "max": round(max_weight, 1)},
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"BMI计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_heart_rate_api(request):
    """心率计算API"""
    try:
        data = json.loads(request.body)
        age = int(data.get("age", 0))
        resting_hr = int(data.get("resting_hr", 0))  # 静息心率
        activity_level = data.get("activity_level", "moderate")  # 活动强度

        if age <= 0 or resting_hr <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的年龄和静息心率"})

        # 计算最大心率 (220 - 年龄)
        max_hr = 220 - age

        # 计算目标心率区间
        target_hr_ranges = {
            "light": {"min": int(max_hr * 0.5), "max": int(max_hr * 0.6), "description": "轻度活动，适合热身和恢复"},
            "moderate": {"min": int(max_hr * 0.6), "max": int(max_hr * 0.7), "description": "中等强度，适合有氧训练"},
            "vigorous": {"min": int(max_hr * 0.7), "max": int(max_hr * 0.85), "description": "高强度，适合心肺训练"},
            "maximum": {"min": int(max_hr * 0.85), "max": int(max_hr), "description": "最大强度，适合间歇训练"},
        }

        # 使用Karvonen公式计算更精确的目标心率
        hr_reserve = max_hr - resting_hr
        karvonen_ranges = {
            "light": {"min": int(resting_hr + hr_reserve * 0.5), "max": int(resting_hr + hr_reserve * 0.6)},
            "moderate": {"min": int(resting_hr + hr_reserve * 0.6), "max": int(resting_hr + hr_reserve * 0.7)},
            "vigorous": {"min": int(resting_hr + hr_reserve * 0.7), "max": int(resting_hr + hr_reserve * 0.85)},
            "maximum": {"min": int(resting_hr + hr_reserve * 0.85), "max": int(resting_hr + hr_reserve * 0.95)},
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "max_heart_rate": max_hr,
                    "resting_heart_rate": resting_hr,
                    "heart_rate_reserve": hr_reserve,
                    "target_ranges": target_hr_ranges,
                    "karvonen_ranges": karvonen_ranges,
                    "recommended_range": karvonen_ranges.get(activity_level, karvonen_ranges["moderate"]),
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"心率计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_calories_api(request):
    """卡路里计算API"""
    try:
        data = json.loads(request.body)
        weight = float(data.get("weight", 0))  # 公斤
        duration = float(data.get("duration", 0))  # 分钟
        activity_type = data.get("activity_type", "walking")

        if weight <= 0 or duration <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的体重和运动时长"})

        # 不同运动类型的MET值 (代谢当量)
        met_values = {
            "walking": 3.5,
            "jogging": 7.0,
            "running": 11.5,
            "cycling": 8.0,
            "swimming": 8.0,
            "weightlifting": 6.0,
            "yoga": 2.5,
            "dancing": 4.5,
            "basketball": 8.0,
            "tennis": 7.0,
            "soccer": 8.0,
            "volleyball": 4.0,
            "hiking": 6.0,
            "rowing": 7.0,
            "elliptical": 5.0,
            "stair_climbing": 8.0,
        }

        met = met_values.get(activity_type, 3.5)

        # 计算消耗的卡路里
        # 公式: 卡路里 = MET × 体重(kg) × 时间(小时)
        calories_burned = met * weight * (duration / 60)

        # 计算不同强度下的卡路里消耗
        intensity_calories = {
            "light": round(calories_burned * 0.7, 1),
            "moderate": round(calories_burned, 1),
            "vigorous": round(calories_burned * 1.3, 1),
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "activity_type": activity_type,
                    "duration_minutes": duration,
                    "weight_kg": weight,
                    "met_value": met,
                    "calories_burned": round(calories_burned, 1),
                    "intensity_calories": intensity_calories,
                    "calories_per_hour": round(calories_burned * 60 / duration, 1),
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"卡路里计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_protein_api(request):
    """蛋白质需求计算API"""
    try:
        data = json.loads(request.body)
        weight = float(data.get("weight", 0))  # 公斤
        activity_level = data.get("activity_level", "moderate")
        goal = data.get("goal", "maintain")  # maintain, lose, gain

        if weight <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的体重"})

        # 基础蛋白质需求 (每公斤体重)
        base_protein = 0.8  # 克/公斤体重

        # 根据活动水平调整
        activity_multipliers = {"sedentary": 1.0, "light": 1.1, "moderate": 1.2, "active": 1.3, "very_active": 1.4}

        # 根据目标调整
        goal_multipliers = {"maintain": 1.0, "lose": 1.2, "gain": 1.5}  # 减重时增加蛋白质摄入  # 增肌时大幅增加蛋白质摄入

        multiplier = activity_multipliers.get(activity_level, 1.2) * goal_multipliers.get(goal, 1.0)
        daily_protein = weight * base_protein * multiplier

        # 计算不同来源的蛋白质建议
        protein_sources = {
            "lean_meat": round(daily_protein * 0.3, 1),  # 瘦肉
            "fish": round(daily_protein * 0.2, 1),  # 鱼类
            "eggs": round(daily_protein * 0.15, 1),  # 鸡蛋
            "dairy": round(daily_protein * 0.2, 1),  # 乳制品
            "legumes": round(daily_protein * 0.1, 1),  # 豆类
            "nuts": round(daily_protein * 0.05, 1),  # 坚果
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "weight_kg": weight,
                    "activity_level": activity_level,
                    "goal": goal,
                    "daily_protein_grams": round(daily_protein, 1),
                    "protein_sources": protein_sources,
                    "recommendations": {
                        "maintain": "保持当前蛋白质摄入水平",
                        "lose": "增加蛋白质摄入有助于保持肌肉质量",
                        "gain": "大幅增加蛋白质摄入以支持肌肉生长",
                    }.get(goal, ""),
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"蛋白质计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_water_api(request):
    """水分需求计算API"""
    try:
        data = json.loads(request.body)
        weight = float(data.get("weight", 0))  # 公斤
        activity_level = data.get("activity_level", "moderate")
        climate = data.get("climate", "temperate")  # temperate, hot, cold
        exercise_duration = float(data.get("exercise_duration", 0))  # 运动时长(小时)

        if weight <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的体重"})

        # 基础水分需求 (每公斤体重30-35ml)
        base_water = weight * 33  # ml

        # 根据活动水平调整
        activity_multipliers = {"sedentary": 1.0, "light": 1.1, "moderate": 1.2, "active": 1.3, "very_active": 1.4}

        # 根据气候调整
        climate_multipliers = {"temperate": 1.0, "hot": 1.2, "cold": 0.9}

        # 运动补充水分 (每小时500-1000ml)
        exercise_water = exercise_duration * 750  # ml

        multiplier = activity_multipliers.get(activity_level, 1.2) * climate_multipliers.get(climate, 1.0)
        daily_water = base_water * multiplier + exercise_water

        # 转换为升
        daily_water_liters = daily_water / 1000

        # 分时段饮水建议
        water_schedule = {
            "morning": round(daily_water * 0.3, 1),  # 早晨30%
            "afternoon": round(daily_water * 0.4, 1),  # 下午40%
            "evening": round(daily_water * 0.3, 1),  # 晚上30%
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "weight_kg": weight,
                    "activity_level": activity_level,
                    "climate": climate,
                    "exercise_duration_hours": exercise_duration,
                    "daily_water_ml": round(daily_water, 0),
                    "daily_water_liters": round(daily_water_liters, 1),
                    "water_schedule": water_schedule,
                    "recommendations": [
                        "早晨起床后立即喝一杯水",
                        "运动前2小时开始补充水分",
                        "运动期间每15-20分钟补充一次水分",
                        "避免一次性大量饮水",
                    ],
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"水分计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_rm_api(request):
    """RM (最大重复次数) 计算API"""
    try:
        data = json.loads(request.body)
        weight = float(data.get("weight", 0))  # 公斤
        reps = int(data.get("reps", 0))  # 重复次数
        rpe = int(data.get("rpe", 0))  # 主观疲劳度 (1-10)

        if weight <= 0 or reps <= 0 or rpe < 1 or rpe > 10:
            return JsonResponse({"success": False, "message": "请输入有效的重量、重复次数和疲劳度"})

        # 使用Brzycki公式计算1RM
        # 1RM = 重量 / (1.0278 - 0.0278 × 重复次数)
        one_rm = weight / (1.0278 - 0.0278 * reps)

        # 使用Epley公式 (另一种常用公式)
        # 1RM = 重量 × (1 + 重复次数 / 30)
        one_rm_epley = weight * (1 + reps / 30)

        # 根据RPE调整
        rpe_adjustments = {
            10: 1.0,  # 最大努力
            9: 0.95,  # 接近最大
            8: 0.9,  # 困难但可完成
            7: 0.85,  # 中等困难
            6: 0.8,  # 中等
            5: 0.75,  # 轻松
            4: 0.7,  # 很轻松
            3: 0.65,  # 非常轻松
            2: 0.6,  # 极其轻松
            1: 0.55,  # 几乎无感觉
        }

        rpe_adjustment = rpe_adjustments.get(rpe, 1.0)
        adjusted_one_rm = one_rm * rpe_adjustment

        # 计算不同重复次数的重量
        rep_percentages = {1: 100, 2: 95, 3: 90, 5: 85, 8: 80, 10: 75, 12: 70, 15: 65, 20: 60}

        rep_weights = {}
        for rep, percentage in rep_percentages.items():
            rep_weights[rep] = round(adjusted_one_rm * percentage / 100, 1)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "input_weight": weight,
                    "input_reps": reps,
                    "input_rpe": rpe,
                    "one_rm_brzycki": round(one_rm, 1),
                    "one_rm_epley": round(one_rm_epley, 1),
                    "adjusted_one_rm": round(adjusted_one_rm, 1),
                    "rep_weights": rep_weights,
                    "recommendations": {
                        "strength": f"力量训练建议重量: {rep_weights.get(5, 0)}kg (5次)",
                        "hypertrophy": f"增肌训练建议重量: {rep_weights.get(8, 0)}kg (8次)",
                        "endurance": f"耐力训练建议重量: {rep_weights.get(15, 0)}kg (15次)",
                    },
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"RM计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_pace_api(request):
    """配速计算API"""
    try:
        data = json.loads(request.body)
        distance = float(data.get("distance", 0))  # 公里
        time_minutes = float(data.get("time_minutes", 0))  # 分钟

        if distance <= 0 or time_minutes <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的距离和时间"})

        # 计算配速 (分钟/公里)
        pace_per_km = time_minutes / distance

        # 转换为分钟:秒格式
        pace_minutes = int(pace_per_km)
        pace_seconds = int((pace_per_km - pace_minutes) * 60)
        pace_formatted = f"{pace_minutes}:{pace_seconds:02d}"

        # 计算速度 (公里/小时)
        speed_kmh = distance / (time_minutes / 60)

        # 计算不同距离的预估时间
        common_distances = [5, 10, 21.0975, 42.195]  # 5K, 10K, 半马, 全马
        estimated_times = {}

        for dist in common_distances:
            estimated_minutes = dist * pace_per_km
            hours = int(estimated_minutes // 60)
            minutes = int(estimated_minutes % 60)
            seconds = int((estimated_minutes % 1) * 60)

            if hours > 0:
                estimated_times[dist] = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                estimated_times[dist] = f"{minutes}:{seconds:02d}"

        # 训练配速建议
        training_paces = {
            "easy": round(pace_per_km * 1.2, 1),  # 轻松跑
            "tempo": round(pace_per_km * 0.9, 1),  # 节奏跑
            "threshold": round(pace_per_km * 0.85, 1),  # 阈值跑
            "interval": round(pace_per_km * 0.8, 1),  # 间歇跑
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "distance_km": distance,
                    "time_minutes": time_minutes,
                    "pace_per_km": round(pace_per_km, 2),
                    "pace_formatted": pace_formatted,
                    "speed_kmh": round(speed_kmh, 2),
                    "estimated_times": estimated_times,
                    "training_paces": training_paces,
                    "pace_analysis": {
                        "very_fast": pace_per_km < 4.0,
                        "fast": 4.0 <= pace_per_km < 5.0,
                        "moderate": 5.0 <= pace_per_km < 6.0,
                        "slow": 6.0 <= pace_per_km < 7.0,
                        "very_slow": pace_per_km >= 7.0,
                    },
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"配速计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def save_workout_record_api(request):
    """保存训练记录API"""
    try:
        data = json.loads(request.body)
        workout_type = data.get("workout_type", "")
        duration = int(data.get("duration", 0))  # 分钟
        calories = int(data.get("calories", 0))
        notes = data.get("notes", "")
        exercises = data.get("exercises", [])

        if not workout_type or duration <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的训练类型和时长"})

        # 这里可以保存到数据库，暂时返回成功
        workout_record = {
            "id": int(timezone.now().timestamp()),
            "user_id": request.user.id,
            "workout_type": workout_type,
            "duration": duration,
            "calories": calories,
            "notes": notes,
            "exercises": exercises,
            "created_at": timezone.now().isoformat(),
        }

        # 缓存用户最近的训练记录
        cache_key = f"user_workout_records_{request.user.id}"
        recent_records = cache.get(cache_key, [])
        recent_records.insert(0, workout_record)
        recent_records = recent_records[:10]  # 只保留最近10条
        cache.set(cache_key, recent_records, 3600 * 24)  # 缓存24小时

        return JsonResponse({"success": True, "message": "训练记录保存成功", "data": workout_record})

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"保存训练记录错误: {str(e)}")
        return JsonResponse({"success": False, "message": "保存过程中出现错误"})


@csrf_exempt
@require_http_methods(["GET"])
def get_workout_records_api(request):
    """获取训练记录API"""
    try:
        # 从缓存获取用户最近的训练记录
        cache_key = f"user_workout_records_{request.user.id}"
        recent_records = cache.get(cache_key, [])

        return JsonResponse({"success": True, "data": recent_records})

    except Exception as e:
        logger.error(f"获取训练记录错误: {str(e)}")
        return JsonResponse({"success": False, "message": "获取记录过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_body_composition_api(request):
    """身体成分分析API"""
    try:
        data = json.loads(request.body)
        age = int(data.get("age", 0))
        gender = data.get("gender", "male")
        height = float(data.get("height", 0))  # 厘米
        weight = float(data.get("weight", 0))  # 公斤
        waist = float(data.get("waist", 0))  # 腰围(厘米)
        hip = float(data.get("hip", 0))  # 臀围(厘米)
        neck = float(data.get("neck", 0))  # 颈围(厘米)

        if age <= 0 or height <= 0 or weight <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的基本信息"})

        # 计算BMI
        height_m = height / 100
        bmi = weight / (height_m * height_m)

        # 计算体脂率 (使用美国海军公式)
        if gender == "male":
            body_fat_percentage = 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(height)) - 450
        else:
            body_fat_percentage = (
                495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(height)) - 450
            )

        body_fat_percentage = max(0, min(100, body_fat_percentage))  # 限制在0-100%范围内

        # 计算瘦体重
        lean_body_mass = weight * (1 - body_fat_percentage / 100)

        # 计算脂肪重量
        fat_mass = weight - lean_body_mass

        # 体脂率分类
        if gender == "male":
            if body_fat_percentage < 6:
                fat_category = "必需脂肪"
            elif body_fat_percentage < 14:
                fat_category = "运动员水平"
            elif body_fat_percentage < 18:
                fat_category = "健康水平"
            elif body_fat_percentage < 25:
                fat_category = "可接受水平"
            else:
                fat_category = "肥胖"
        else:
            if body_fat_percentage < 14:
                fat_category = "必需脂肪"
            elif body_fat_percentage < 21:
                fat_category = "运动员水平"
            elif body_fat_percentage < 25:
                fat_category = "健康水平"
            elif body_fat_percentage < 32:
                fat_category = "可接受水平"
            else:
                fat_category = "肥胖"

        # 计算腰臀比
        whr = waist / hip if hip > 0 else 0

        # 腰臀比分类
        if gender == "male":
            if whr < 0.9:
                whr_category = "低风险"
            elif whr < 1.0:
                whr_category = "中等风险"
            else:
                whr_category = "高风险"
        else:
            if whr < 0.8:
                whr_category = "低风险"
            elif whr < 0.85:
                whr_category = "中等风险"
            else:
                whr_category = "高风险"

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "bmi": round(bmi, 1),
                    "body_fat_percentage": round(body_fat_percentage, 1),
                    "lean_body_mass": round(lean_body_mass, 1),
                    "fat_mass": round(fat_mass, 1),
                    "fat_category": fat_category,
                    "waist_hip_ratio": round(whr, 2),
                    "whr_category": whr_category,
                    "recommendations": {
                        "body_fat": f"当前体脂率: {body_fat_percentage:.1f}% ({fat_category})",
                        "whr": f"腰臀比: {whr:.2f} ({whr_category})",
                        "general": "建议结合有氧运动和力量训练，注意饮食控制",
                    },
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"身体成分分析错误: {str(e)}")
        return JsonResponse({"success": False, "message": "分析过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def calculate_one_rm_api(request):
    """1RM计算API"""
    try:
        data = json.loads(request.body)
        weight = float(data.get("weight", 0))  # 公斤
        reps = int(data.get("reps", 0))  # 重复次数
        formula = data.get("formula", "epley")  # 计算公式

        if weight <= 0 or reps <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的重量和重复次数"})

        # 不同公式的1RM计算
        formulas = {
            "epley": {"name": "埃普勒公式", "description": "最常用、最通用的公式", "formula": lambda w, r: w * (1 + r / 30)},
            "brzycki": {
                "name": "布日奇克公式",
                "description": "在次数较高时（>10次）可能更准确",
                "formula": lambda w, r: w * (36 / (37 - r)),
            },
            "lombardi": {"name": "隆巴迪公式", "description": "适用于各种重复次数", "formula": lambda w, r: w * (r**0.1)},
            "oconner": {"name": "奥康纳公式", "description": "简单易用的公式", "formula": lambda w, r: w * (1 + r * 0.025)},
        }

        selected_formula = formulas.get(formula, formulas["epley"])
        one_rm = selected_formula["formula"](weight, reps)

        # 计算不同重复次数的重量
        rep_percentages = {1: 100, 2: 95, 3: 90, 5: 85, 8: 80, 10: 75, 12: 70, 15: 65, 20: 60}

        rep_weights = {}
        for rep, percentage in rep_percentages.items():
            rep_weights[rep] = round(one_rm * percentage / 100, 1)

        # 训练建议
        training_recommendations = {
            "strength": {"reps": "1-5次", "weight": f"{rep_weights.get(5, 0)}kg", "description": "力量训练，提高最大力量"},
            "hypertrophy": {
                "reps": "8-12次",
                "weight": f"{rep_weights.get(10, 0)}kg",
                "description": "增肌训练，促进肌肉生长",
            },
            "endurance": {"reps": "15-20次", "weight": f"{rep_weights.get(15, 0)}kg", "description": "耐力训练，提高肌肉耐力"},
        }

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "input_weight": weight,
                    "input_reps": reps,
                    "formula_used": selected_formula["name"],
                    "formula_description": selected_formula["description"],
                    "one_rep_max": round(one_rm, 1),
                    "rep_weights": rep_weights,
                    "training_recommendations": training_recommendations,
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"1RM计算错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})


@csrf_exempt
@require_http_methods(["POST"])
def predict_reps_api(request):
    """预测重复次数API"""
    try:
        data = json.loads(request.body)
        target_weight = float(data.get("target_weight", 0))  # 目标重量
        one_rep_max = data.get("one_rep_max", None)  # 已知1RM
        known_weight = data.get("known_weight", None)  # 已知重量
        known_reps = data.get("known_reps", None)  # 已知重复次数
        formula = data.get("formula", "epley")  # 计算公式

        if target_weight <= 0:
            return JsonResponse({"success": False, "message": "请输入有效的目标重量"})

        # 如果没有提供1RM，但有已知重量和重复次数，先计算1RM
        if one_rep_max is None and known_weight and known_reps:
            formulas = {
                "epley": lambda w, r: w * (1 + r / 30),
                "brzycki": lambda w, r: w * (36 / (37 - r)),
                "lombardi": lambda w, r: w * (r**0.1),
                "oconner": lambda w, r: w * (1 + r * 0.025),
            }
            selected_formula = formulas.get(formula, formulas["epley"])
            one_rep_max = selected_formula(known_weight, known_reps)

        if one_rep_max is None or one_rep_max <= 0:
            return JsonResponse({"success": False, "message": "请提供有效的1RM或已知重量和重复次数"})

        # 根据公式反推重复次数
        formulas_reverse = {
            "epley": lambda w, rm: (rm / w - 1) * 30,
            "brzycki": lambda w, rm: 37 - (36 * w / rm),
            "lombardi": lambda w, rm: (rm / w) ** 10,
            "oconner": lambda w, rm: (rm / w - 1) / 0.025,
        }

        selected_formula_reverse = formulas_reverse.get(formula, formulas_reverse["epley"])
        predicted_reps = selected_formula_reverse(target_weight, one_rep_max)

        # 确保重复次数为正数
        predicted_reps = max(0, predicted_reps)

        return JsonResponse(
            {
                "success": True,
                "data": {
                    "target_weight": target_weight,
                    "one_rep_max": round(one_rep_max, 1),
                    "predicted_reps": round(predicted_reps, 1),
                    "formula_used": {
                        "epley": "埃普勒公式",
                        "brzycki": "布日奇克公式",
                        "lombardi": "隆巴迪公式",
                        "oconner": "奥康纳公式",
                    }.get(formula, "埃普勒公式"),
                },
            }
        )

    except (ValueError, TypeError) as e:
        return JsonResponse({"success": False, "message": "输入数据格式错误"})
    except Exception as e:
        logger.error(f"重复次数预测错误: {str(e)}")
        return JsonResponse({"success": False, "message": "计算过程中出现错误"})
