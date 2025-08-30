# QAToolbox/apps/tools/views/food_randomizer_views.py
"""
食物随机器相关的视图函数
"""

import json
import logging
import random
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db import models
from apps.tools.models import FoodNutrition, FoodRandomizationLog

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def food_randomizer_pure_random_api(request):
    """食物随机器纯随机API - 使用数据库数据"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        cuisine_type = data.get('cuisine_type', 'all')
        meal_type = data.get('meal_type', 'all')
        exclude_recent = data.get('exclude_recent', True)
        
        # 从数据库获取活跃的食物数据
        queryset = FoodNutrition.objects.filter(is_active=True)
        
        # 处理cuisine_type过滤
        if cuisine_type != 'all' and cuisine_type != 'mixed':
            queryset = queryset.filter(cuisine=cuisine_type)
        # 如果是'mixed'，则不过滤cuisine类型，显示所有菜系
        
        # 处理meal_type过滤
        if meal_type != 'all':
            # 将'lunch'映射到'main'，因为午餐通常是主食
            if meal_type == 'lunch':
                meal_type = 'main'
            queryset = queryset.filter(meal_type=meal_type)
        
        # 排除最近食用的食物（如果需要的话）
        if exclude_recent and request.user.is_authenticated:
            # 获取用户最近3天内食用过的食物
            recent_cutoff = datetime.now() - timedelta(days=3)
            recent_food_ids = FoodRandomizationLog.objects.filter(
                user=request.user,
                created_at__gte=recent_cutoff,
                selected=True
            ).values_list('food_id', flat=True)
            queryset = queryset.exclude(id__in=recent_food_ids)
        
        # 转换为列表
        available_foods = list(queryset)
        
        if not available_foods:
            return JsonResponse({
                'success': False,
                'error': '没有找到符合条件的食物'
            }, status=404)
        
        # 随机选择食物
        selected_food = random.choice(available_foods)
        
        # 生成推荐理由
        reasons = [
            '营养均衡，适合当前季节',
            '制作简单，适合忙碌的生活',
            '口感丰富，满足味蕾需求',
            '健康美味，符合现代饮食理念',
            '经典菜品，值得一试',
            '富含蛋白质，有助于肌肉健康',
            '低脂健康，适合减肥期间',
            '高纤维食物，促进消化',
            '维生素丰富，增强免疫力'
        ]
        
        # 获取备选食物（除了选中的食物）
        alternative_foods = [f for f in available_foods if f.id != selected_food.id]
        alternatives = random.sample(alternative_foods, min(3, len(alternative_foods)))
        
        # 将选中的食物转换为字典格式
        def food_to_dict(food):
            return {
                'id': food.id,
                'name': food.name,
                'english_name': food.english_name,
                'cuisine': food.cuisine,
                'meal_type': food.meal_type,
                'calories': int(food.calories),
                'ingredients': food.ingredients,
                'description': food.description,
                'image_url': food.image_url or '/static/img/food/default-food.svg',
                'difficulty': food.difficulty,
                'cooking_time': food.cooking_time,
                'health_score': food.health_score,
                'nutrition': {
                    'protein': food.protein,
                    'fat': food.fat,
                    'carbohydrates': food.carbohydrates,
                    'dietary_fiber': food.dietary_fiber,
                    'sugar': food.sugar,
                    'sodium': food.sodium,
                    'calcium': food.calcium,
                    'iron': food.iron,
                    'vitamin_c': food.vitamin_c
                },
                'tags': food.tags,
                'is_vegetarian': food.is_vegetarian,
                'is_high_protein': food.is_high_protein,
                'is_low_carb': food.is_low_carb
            }
        
        # 构建推荐结果
        recommendation = {
            'food': food_to_dict(selected_food),
            'reason': random.choice(reasons),
            'confidence': random.randint(70, 95),
            'alternatives': [food_to_dict(f) for f in alternatives],
            'generated_at': datetime.now().isoformat(),
            'nutrition_summary': {
                'macronutrients': selected_food.get_macronutrients_ratio(),
                'health_score': selected_food.health_score,
                'is_healthy': selected_food.is_healthy()
            }
        }
        
        # 记录推荐日志
        session_id = recommendation['generated_at']
        if request.user.is_authenticated:
            FoodRandomizationLog.objects.create(
                user=request.user,
                food=selected_food,
                session_id=session_id,
                cuisine_filter=cuisine_type if cuisine_type != 'all' else None,
                meal_type_filter=meal_type if meal_type != 'all' else None
            )
            
            # 为备选食物也创建日志记录
            for alt_food in alternatives:
                FoodRandomizationLog.objects.create(
                    user=request.user,
                    food=alt_food,
                    session_id=session_id,
                    cuisine_filter=cuisine_type if cuisine_type != 'all' else None,
                    meal_type_filter=meal_type if meal_type != 'all' else None,
                    selected=False
                )
        
        logger.info(f"食物随机推荐: 选择 {selected_food.name} (ID: {selected_food.id})")
        
        return JsonResponse({
            'success': True,
            'recommendation': recommendation
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"食物随机推荐失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'推荐失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def food_randomizer_statistics_api(request):
    """食物随机器统计API - 使用数据库数据"""
    try:
        # 获取总体统计
        total_foods = FoodNutrition.objects.filter(is_active=True).count()
        total_recommendations = FoodRandomizationLog.objects.count()
        
        # 按菜系统计
        cuisine_stats = {}
        for cuisine, display_name in FoodNutrition.CUISINE_CHOICES:
            count = FoodRandomizationLog.objects.filter(food__cuisine=cuisine).count()
            if count > 0:
                cuisine_stats[cuisine] = count
        
        # 按餐型统计
        meal_type_stats = {}
        for meal_type, display_name in FoodNutrition.MEAL_TYPE_CHOICES:
            count = FoodRandomizationLog.objects.filter(food__meal_type=meal_type).count()
            if count > 0:
                meal_type_stats[meal_type] = count
        
        # 最受欢迎的食物
        popular_food = FoodNutrition.objects.filter(is_active=True).order_by('-popularity_score').first()
        
        # 用户特定统计（如果用户已登录）
        user_stats = {}
        if request.user.is_authenticated:
            user_recommendations = FoodRandomizationLog.objects.filter(user=request.user).count()
            user_stats = {
                'total_recommendations': user_recommendations,
                'favorite_cuisine': None,
                'healthy_choices': 0
            }
            
            # 用户最喜欢的菜系
            if user_recommendations > 0:
                user_cuisine_stats = FoodRandomizationLog.objects.filter(
                    user=request.user
                ).values('food__cuisine').annotate(
                    count=models.Count('food__cuisine')
                ).order_by('-count').first()
                
                if user_cuisine_stats:
                    user_stats['favorite_cuisine'] = user_cuisine_stats['food__cuisine']
            
            # 健康选择统计
            user_stats['healthy_choices'] = FoodRandomizationLog.objects.filter(
                user=request.user,
                food__health_score__gte=70
            ).count()
        
        # 周使用统计（最近7天）
        weekly_usage = []
        for i in range(7):
            date = datetime.now().date() - timedelta(days=i)
            count = FoodRandomizationLog.objects.filter(
                created_at__date=date
            ).count()
            weekly_usage.append({
                'date': date.isoformat(),
                'count': count
            })
        weekly_usage.reverse()  # 按时间顺序排列
        
        stats_data = {
            'total_foods': total_foods,
            'total_recommendations': total_recommendations,
            'most_popular_food': popular_food.name if popular_food else None,
            'cuisine_distribution': cuisine_stats,
            'meal_type_distribution': meal_type_stats,
            'weekly_usage': weekly_usage,
            'user_stats': user_stats,
            'health_metrics': {
                'healthy_foods_count': FoodNutrition.objects.filter(
                    is_active=True, 
                    health_score__gte=70
                ).count(),
                'vegetarian_foods_count': FoodNutrition.objects.filter(
                    is_active=True,
                    is_vegetarian=True
                ).count(),
                'high_protein_foods_count': FoodNutrition.objects.filter(
                    is_active=True,
                    is_high_protein=True
                ).count()
            }
        }
        
        logger.info(f"获取食物随机器统计: 用户 {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        
        return JsonResponse({
            'success': True,
            'stats': stats_data
        })
        
    except Exception as e:
        logger.error(f"获取食物随机器统计失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取统计数据失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def food_randomizer_history_api(request):
    """食物随机器历史API - 使用数据库数据"""
    try:
        # 获取查询参数
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        if request.user.is_authenticated:
            # 获取用户的推荐历史
            queryset = FoodRandomizationLog.objects.filter(
                user=request.user
            ).select_related('food').order_by('-created_at')
            
            total_count = queryset.count()
            records = queryset[offset:offset + limit]
            
            history_records = []
            for record in records:
                history_records.append({
                    'id': record.id,
                    'food_name': record.food.name,
                    'cuisine': record.food.cuisine,
                    'meal_type': record.food.meal_type,
                    'calories': int(record.food.calories),
                    'health_score': record.food.health_score,
                    'rating': record.rating,
                    'selected': record.selected,
                    'created_at': record.created_at.isoformat(),
                    'session_id': record.session_id,
                    'nutrition_summary': record.food.get_nutrition_summary()
                })
        else:
            # 如果用户未登录，返回空历史
            total_count = 0
            history_records = []
        
        logger.info(f"获取食物随机器历史: 用户 {request.user.username if request.user.is_authenticated else 'Anonymous'}, 返回 {len(history_records)} 条记录")
        
        return JsonResponse({
            'success': True,
            'history': history_records,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物随机器历史失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取历史失败: {str(e)}'
        }, status=500)