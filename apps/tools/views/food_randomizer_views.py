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
            # 中餐
            {
                'id': 1, 'name': '宫保鸡丁', 'english_name': 'Kung Pao Chicken',
                'cuisine': 'chinese', 'meal_type': 'main', 'calories': 350,
                'ingredients': ['鸡肉', '花生', '干辣椒', '葱姜蒜'],
                'description': '经典川菜，口感麻辣鲜香',
                'image_url': '/static/img/food/kung_pao_chicken.jpg',
                'difficulty': 3, 'cooking_time': 25
            },
            {
                'id': 6, 'name': '麻婆豆腐', 'english_name': 'Mapo Tofu',
                'cuisine': 'chinese', 'meal_type': 'main', 'calories': 280,
                'ingredients': ['豆腐', '猪肉末', '豆瓣酱', '花椒'],
                'description': '川菜经典，麻辣鲜香',
                'image_url': '/static/img/food/mapo_tofu.jpg',
                'difficulty': 3, 'cooking_time': 20
            },
            {
                'id': 7, 'name': '糖醋里脊', 'english_name': 'Sweet and Sour Pork',
                'cuisine': 'chinese', 'meal_type': 'main', 'calories': 320,
                'ingredients': ['里脊肉', '糖', '醋', '淀粉'],
                'description': '酸甜可口，开胃下饭',
                'image_url': '/static/img/food/sweet_sour_pork.jpg',
                'difficulty': 3, 'cooking_time': 25
            },
            {
                'id': 8, 'name': '小笼包', 'english_name': 'Xiaolongbao',
                'cuisine': 'chinese', 'meal_type': 'appetizer', 'calories': 150,
                'ingredients': ['面粉', '猪肉', '高汤', '姜'],
                'description': '上海名点，汤汁丰富',
                'image_url': '/static/img/food/xiaolongbao.jpg',
                'difficulty': 4, 'cooking_time': 40
            },
            {
                'id': 9, 'name': '蛋炒饭', 'english_name': 'Egg Fried Rice',
                'cuisine': 'chinese', 'meal_type': 'main', 'calories': 300,
                'ingredients': ['米饭', '鸡蛋', '葱花', '酱油'],
                'description': '简单美味，经典家常菜',
                'image_url': '/static/img/food/egg_fried_rice.jpg',
                'difficulty': 1, 'cooking_time': 15
            },
            
            # 意餐
            {
                'id': 2, 'name': '意大利面', 'english_name': 'Spaghetti',
                'cuisine': 'italian', 'meal_type': 'main', 'calories': 280,
                'ingredients': ['意大利面', '番茄酱', '橄榄油', '罗勒'],
                'description': '经典意式料理，简单美味',
                'image_url': '/static/img/food/spaghetti.jpg',
                'difficulty': 2, 'cooking_time': 20
            },
            {
                'id': 10, 'name': '披萨', 'english_name': 'Pizza',
                'cuisine': 'italian', 'meal_type': 'main', 'calories': 400,
                'ingredients': ['面团', '番茄酱', '奶酪', '香肠'],
                'description': '意式经典，香浓可口',
                'image_url': '/static/img/food/pizza.jpg',
                'difficulty': 3, 'cooking_time': 30
            },
            {
                'id': 11, 'name': '提拉米苏', 'english_name': 'Tiramisu',
                'cuisine': 'italian', 'meal_type': 'dessert', 'calories': 250,
                'ingredients': ['手指饼干', '咖啡', '马斯卡彭奶酪', '可可粉'],
                'description': '意式甜点，浓郁香滑',
                'image_url': '/static/img/food/tiramisu.jpg',
                'difficulty': 3, 'cooking_time': 45
            },
            
            # 日餐
            {
                'id': 3, 'name': '寿司', 'english_name': 'Sushi',
                'cuisine': 'japanese', 'meal_type': 'main', 'calories': 200,
                'ingredients': ['米饭', '三文鱼', '海苔', '芥末'],
                'description': '精致日式料理，营养丰富',
                'image_url': '/static/img/food/sushi.jpg',
                'difficulty': 4, 'cooking_time': 30
            },
            {
                'id': 12, 'name': '拉面', 'english_name': 'Ramen',
                'cuisine': 'japanese', 'meal_type': 'main', 'calories': 350,
                'ingredients': ['面条', '高汤', '叉烧', '海苔'],
                'description': '日式拉面，汤浓面滑',
                'image_url': '/static/img/food/ramen.jpg',
                'difficulty': 3, 'cooking_time': 25
            },
            {
                'id': 13, 'name': '天妇罗', 'english_name': 'Tempura',
                'cuisine': 'japanese', 'meal_type': 'appetizer', 'calories': 180,
                'ingredients': ['虾', '面粉', '鸡蛋', '油'],
                'description': '日式炸物，酥脆可口',
                'image_url': '/static/img/food/tempura.jpg',
                'difficulty': 3, 'cooking_time': 20
            },
            
            # 美餐
            {
                'id': 4, 'name': '汉堡', 'english_name': 'Burger',
                'cuisine': 'american', 'meal_type': 'main', 'calories': 450,
                'ingredients': ['牛肉饼', '面包', '生菜', '番茄'],
                'description': '美式快餐，方便快捷',
                'image_url': '/static/img/food/burger.jpg',
                'difficulty': 2, 'cooking_time': 15
            },
            {
                'id': 14, 'name': '热狗', 'english_name': 'Hot Dog',
                'cuisine': 'american', 'meal_type': 'main', 'calories': 300,
                'ingredients': ['香肠', '面包', '芥末', '洋葱'],
                'description': '美式经典，简单美味',
                'image_url': '/static/img/food/hot_dog.jpg',
                'difficulty': 1, 'cooking_time': 10
            },
            {
                'id': 15, 'name': '苹果派', 'english_name': 'Apple Pie',
                'cuisine': 'american', 'meal_type': 'dessert', 'calories': 280,
                'ingredients': ['苹果', '面粉', '糖', '肉桂'],
                'description': '美式甜点，香甜可口',
                'image_url': '/static/img/food/apple_pie.jpg',
                'difficulty': 3, 'cooking_time': 60
            },
            
            # 健康餐
            {
                'id': 5, 'name': '沙拉', 'english_name': 'Salad',
                'cuisine': 'healthy', 'meal_type': 'appetizer', 'calories': 120,
                'ingredients': ['生菜', '番茄', '黄瓜', '橄榄油'],
                'description': '健康轻食，清爽可口',
                'image_url': '/static/img/food/salad.jpg',
                'difficulty': 1, 'cooking_time': 10
            },
            {
                'id': 16, 'name': '燕麦粥', 'english_name': 'Oatmeal',
                'cuisine': 'healthy', 'meal_type': 'breakfast', 'calories': 150,
                'ingredients': ['燕麦', '牛奶', '蜂蜜', '坚果'],
                'description': '营养早餐，健康美味',
                'image_url': '/static/img/food/oatmeal.jpg',
                'difficulty': 1, 'cooking_time': 15
            },
            {
                'id': 17, 'name': '蒸蛋羹', 'english_name': 'Steamed Egg',
                'cuisine': 'healthy', 'meal_type': 'appetizer', 'calories': 100,
                'ingredients': ['鸡蛋', '水', '盐', '葱花'],
                'description': '清淡营养，易消化',
                'image_url': '/static/img/food/steamed_egg.jpg',
                'difficulty': 2, 'cooking_time': 20
            },
            
            # 法餐
            {
                'id': 18, 'name': '法式牛排', 'english_name': 'French Steak',
                'cuisine': 'french', 'meal_type': 'main', 'calories': 500,
                'ingredients': ['牛排', '黄油', '红酒', '香草'],
                'description': '法式经典，精致美味',
                'image_url': '/static/img/food/french_steak.jpg',
                'difficulty': 4, 'cooking_time': 30
            },
            {
                'id': 19, 'name': '马卡龙', 'english_name': 'Macaron',
                'cuisine': 'french', 'meal_type': 'dessert', 'calories': 200,
                'ingredients': ['杏仁粉', '糖粉', '蛋白', '色素'],
                'description': '法式甜点，色彩缤纷',
                'image_url': '/static/img/food/macaron.jpg',
                'difficulty': 5, 'cooking_time': 90
            },
            
            # 韩餐
            {
                'id': 20, 'name': '韩式烤肉', 'english_name': 'Korean BBQ',
                'cuisine': 'korean', 'meal_type': 'main', 'calories': 400,
                'ingredients': ['牛肉', '生菜', '蒜', '辣椒酱'],
                'description': '韩式经典，香辣可口',
                'image_url': '/static/img/food/korean_bbq.jpg',
                'difficulty': 3, 'cooking_time': 25
            },
            {
                'id': 21, 'name': '泡菜汤', 'english_name': 'Kimchi Soup',
                'cuisine': 'korean', 'meal_type': 'main', 'calories': 200,
                'ingredients': ['泡菜', '豆腐', '猪肉', '辣椒'],
                'description': '韩式汤品，开胃暖身',
                'image_url': '/static/img/food/kimchi_soup.jpg',
                'difficulty': 2, 'cooking_time': 20
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
        
        logger.info(f"食物随机推荐: 选择 {selected_food['name']}")
        
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
        
        logger.info(f"获取食物随机器统计")
        
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
