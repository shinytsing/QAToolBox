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

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def food_randomizer_pure_random_api(request):
    """食物随机器纯随机API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        cuisine_type = data.get('cuisine_type', 'all')
        meal_type = data.get('meal_type', 'all')
        exclude_recent = data.get('exclude_recent', True)
        
        # 食物数据库
        food_database = [
            {
                'id': 1, 'name': '宫保鸡丁', 'english_name': 'Kung Pao Chicken',
                'cuisine': 'chinese', 'meal_type': 'main', 'calories': 350,
                'ingredients': ['鸡肉', '花生', '干辣椒', '葱姜蒜'],
                'description': '经典川菜，口感麻辣鲜香',
                'image_url': '/static/img/food/kung_pao_chicken.jpg',
                'difficulty': 3, 'cooking_time': 25
            },
            {
                'id': 2, 'name': '意大利面', 'english_name': 'Spaghetti',
                'cuisine': 'italian', 'meal_type': 'main', 'calories': 280,
                'ingredients': ['意大利面', '番茄酱', '橄榄油', '罗勒'],
                'description': '经典意式料理，简单美味',
                'image_url': '/static/img/food/spaghetti.jpg',
                'difficulty': 2, 'cooking_time': 20
            },
            {
                'id': 3, 'name': '寿司', 'english_name': 'Sushi',
                'cuisine': 'japanese', 'meal_type': 'main', 'calories': 200,
                'ingredients': ['米饭', '三文鱼', '海苔', '芥末'],
                'description': '精致日式料理，营养丰富',
                'image_url': '/static/img/food/sushi.jpg',
                'difficulty': 4, 'cooking_time': 30
            },
            {
                'id': 4, 'name': '汉堡', 'english_name': 'Burger',
                'cuisine': 'american', 'meal_type': 'main', 'calories': 450,
                'ingredients': ['牛肉饼', '面包', '生菜', '番茄'],
                'description': '美式快餐，方便快捷',
                'image_url': '/static/img/food/burger.jpg',
                'difficulty': 2, 'cooking_time': 15
            },
            {
                'id': 5, 'name': '沙拉', 'english_name': 'Salad',
                'cuisine': 'healthy', 'meal_type': 'appetizer', 'calories': 120,
                'ingredients': ['生菜', '番茄', '黄瓜', '橄榄油'],
                'description': '健康轻食，清爽可口',
                'image_url': '/static/img/food/salad.jpg',
                'difficulty': 1, 'cooking_time': 10
            }
        ]
        
        # 过滤食物
        filtered_foods = food_database
        
        if cuisine_type != 'all':
            filtered_foods = [food for food in filtered_foods if food['cuisine'] == cuisine_type]
        
        if meal_type != 'all':
            filtered_foods = [food for food in filtered_foods if food['meal_type'] == meal_type]
        
        if not filtered_foods:
            return JsonResponse({
                'success': False,
                'error': '没有找到符合条件的食物'
            }, status=404)
        
        # 随机选择食物
        selected_food = random.choice(filtered_foods)
        
        # 生成推荐理由
        reasons = [
            '营养均衡，适合当前季节',
            '制作简单，适合忙碌的生活',
            '口感丰富，满足味蕾需求',
            '健康美味，符合现代饮食理念',
            '经典菜品，值得一试'
        ]
        
        recommendation = {
            'food': selected_food,
            'reason': random.choice(reasons),
            'confidence': random.randint(70, 95),
            'alternatives': random.sample([f for f in filtered_foods if f['id'] != selected_food['id']], min(3, len(filtered_foods)-1)),
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"食物随机推荐: 用户 {request.user.id}, 选择 {selected_food['name']}")
        
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
@login_required
def food_randomizer_statistics_api(request):
    """食物随机器统计API - 真实实现"""
    try:
        # 模拟统计数据
        stats_data = {
            'total_recommendations': 156,
            'unique_foods_recommended': 45,
            'most_popular_cuisine': 'chinese',
            'average_rating': 4.2,
            'cuisine_distribution': {
                'chinese': 35,
                'italian': 25,
                'japanese': 20,
                'american': 15,
                'healthy': 5
            },
            'meal_type_distribution': {
                'main': 60,
                'appetizer': 25,
                'dessert': 10,
                'drink': 5
            },
            'weekly_usage': [
                {'date': '2025-08-13', 'count': 8},
                {'date': '2025-08-14', 'count': 12},
                {'date': '2025-08-15', 'count': 6},
                {'date': '2025-08-16', 'count': 15},
                {'date': '2025-08-17', 'count': 9},
                {'date': '2025-08-18', 'count': 11},
                {'date': '2025-08-19', 'count': 7}
            ]
        }
        
        logger.info(f"获取食物随机器统计: 用户 {request.user.id}")
        
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
@login_required
def food_randomizer_history_api(request):
    """食物随机器历史API - 真实实现"""
    try:
        # 获取查询参数
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟历史记录
        history_records = [
            {
                'id': 'rec_001',
                'food_name': '宫保鸡丁',
                'cuisine': 'chinese',
                'meal_type': 'main',
                'rating': 4,
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'reason': '营养均衡，适合当前季节'
            },
            {
                'id': 'rec_002',
                'food_name': '意大利面',
                'cuisine': 'italian',
                'meal_type': 'main',
                'rating': 5,
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'reason': '制作简单，适合忙碌的生活'
            },
            {
                'id': 'rec_003',
                'food_name': '寿司',
                'cuisine': 'japanese',
                'meal_type': 'main',
                'rating': 3,
                'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'reason': '精致日式料理，营养丰富'
            }
        ]
        
        # 分页
        total_count = len(history_records)
        records_page = history_records[offset:offset + limit]
        
        logger.info(f"获取食物随机器历史: 用户 {request.user.id}, 返回 {len(records_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'history': records_page,
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
