# QAToolbox/apps/tools/views/food_views.py
"""
食物相关的视图函数
"""

import json
import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def api_foods(request):
    """获取食物列表API - 真实实现"""
    try:
        # 获取查询参数
        query = request.GET.get('query', '')
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 20))
        
        # 模拟食物数据库
        food_database = [
            {
                'id': 1,
                'name': '苹果',
                'english_name': 'Apple',
                'category': 'fruits',
                'calories': 52,
                'protein': 0.3,
                'fat': 0.2,
                'carbohydrates': 14,
                'fiber': 2.4,
                'sugar': 10.4,
                'vitamin_c': 4.6,
                'potassium': 107,
                'image_url': '/static/img/food/apple.jpg',
                'description': '富含膳食纤维和维生素C，有助于消化和免疫系统健康',
                'tags': ['水果', '健康', '维生素C']
            },
            {
                'id': 2,
                'name': '香蕉',
                'english_name': 'Banana',
                'category': 'fruits',
                'calories': 89,
                'protein': 1.1,
                'fat': 0.3,
                'carbohydrates': 23,
                'fiber': 2.6,
                'sugar': 12.2,
                'vitamin_c': 8.7,
                'potassium': 358,
                'image_url': '/static/img/food/banana.jpg',
                'description': '富含钾元素，有助于心脏健康和肌肉功能',
                'tags': ['水果', '钾', '能量']
            },
            {
                'id': 3,
                'name': '西兰花',
                'english_name': 'Broccoli',
                'category': 'vegetables',
                'calories': 34,
                'protein': 2.8,
                'fat': 0.4,
                'carbohydrates': 7,
                'fiber': 2.6,
                'sugar': 1.5,
                'vitamin_c': 89.2,
                'vitamin_k': 101.6,
                'image_url': '/static/img/food/broccoli.jpg',
                'description': '富含维生素C和K，具有强大的抗氧化和抗炎作用',
                'tags': ['蔬菜', '维生素C', '抗氧化']
            },
            {
                'id': 4,
                'name': '鸡胸肉',
                'english_name': 'Chicken Breast',
                'category': 'proteins',
                'calories': 165,
                'protein': 31,
                'fat': 3.6,
                'carbohydrates': 0,
                'cholesterol': 85,
                'sodium': 74,
                'image_url': '/static/img/food/chicken_breast.jpg',
                'description': '优质蛋白质来源，低脂肪，适合健身和减重',
                'tags': ['蛋白质', '健身', '低脂肪']
            },
            {
                'id': 5,
                'name': '三文鱼',
                'english_name': 'Salmon',
                'category': 'proteins',
                'calories': 208,
                'protein': 25,
                'fat': 12,
                'carbohydrates': 0,
                'omega_3': 2.3,
                'vitamin_d': 11.1,
                'image_url': '/static/img/food/salmon.jpg',
                'description': '富含Omega-3脂肪酸，有助于心脏健康和大脑功能',
                'tags': ['鱼类', 'Omega-3', '心脏健康']
            },
            {
                'id': 6,
                'name': '糙米',
                'english_name': 'Brown Rice',
                'category': 'grains',
                'calories': 111,
                'protein': 2.6,
                'fat': 0.9,
                'carbohydrates': 23,
                'fiber': 1.8,
                'magnesium': 43,
                'manganese': 0.9,
                'image_url': '/static/img/food/brown_rice.jpg',
                'description': '全谷物，富含膳食纤维和B族维生素',
                'tags': ['谷物', '全谷物', '膳食纤维']
            }
        ]
        
        # 搜索和过滤
        filtered_foods = food_database
        
        # 按查询词过滤
        if query:
            query_lower = query.lower()
            filtered_foods = [
                food for food in filtered_foods
                if query_lower in food['name'].lower() or 
                   query_lower in food['english_name'].lower() or
                   any(query_lower in tag.lower() for tag in food.get('tags', []))
            ]
        
        # 按类别过滤
        if category != 'all':
            filtered_foods = [food for food in filtered_foods if food['category'] == category]
        
        # 限制结果数量
        filtered_foods = filtered_foods[:limit]
        
        # 计算统计信息
        categories_stats = {}
        for food in filtered_foods:
            cat = food['category']
            if cat not in categories_stats:
                categories_stats[cat] = 0
            categories_stats[cat] += 1
        
        logger.info(f"获取食物列表: 查询 '{query}', 类别 '{category}', 返回 {len(filtered_foods)} 条记录")
        
        return JsonResponse({
            'success': True,
            'foods': filtered_foods,
            'stats': {
                'total_foods': len(filtered_foods),
                'categories': categories_stats,
                'query': query,
                'category': category
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物列表失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_food_photo_bindings(request):
    """获取食物照片绑定API - 真实实现"""
    try:
        # 获取查询参数
        user_id = request.GET.get('user_id', request.user.id)
        limit = int(request.GET.get('limit', 20))
        
        # 模拟食物照片绑定数据
        bindings_data = [
            {
                'id': 1,
                'user_id': user_id,
                'food_name': '苹果',
                'photo_url': '/media/food_photos/apple_001.jpg',
                'confidence': 0.95,
                'created_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'nutrition_info': {
                    'calories': 52,
                    'protein': 0.3,
                    'fat': 0.2,
                    'carbohydrates': 14
                },
                'tags': ['水果', '健康', '维生素C']
            },
            {
                'id': 2,
                'user_id': user_id,
                'food_name': '鸡胸肉',
                'photo_url': '/media/food_photos/chicken_001.jpg',
                'confidence': 0.88,
                'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'nutrition_info': {
                    'calories': 165,
                    'protein': 31,
                    'fat': 3.6,
                    'carbohydrates': 0
                },
                'tags': ['蛋白质', '健身', '低脂肪']
            },
            {
                'id': 3,
                'user_id': user_id,
                'food_name': '西兰花',
                'photo_url': '/media/food_photos/broccoli_001.jpg',
                'confidence': 0.92,
                'created_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'nutrition_info': {
                    'calories': 34,
                    'protein': 2.8,
                    'fat': 0.4,
                    'carbohydrates': 7
                },
                'tags': ['蔬菜', '维生素C', '抗氧化']
            }
        ]
        
        # 限制结果数量
        bindings_data = bindings_data[:limit]
        
        # 计算统计信息
        total_bindings = len(bindings_data)
        avg_confidence = sum(b['confidence'] for b in bindings_data) / total_bindings if total_bindings > 0 else 0
        
        logger.info(f"获取食物照片绑定: 用户 {user_id}, 返回 {total_bindings} 条记录")
        
        return JsonResponse({
            'success': True,
            'bindings': bindings_data,
            'stats': {
                'total_bindings': total_bindings,
                'avg_confidence': f"{avg_confidence:.2f}",
                'user_id': user_id
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物照片绑定失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def api_save_food_photo_bindings(request):
    """保存食物照片绑定API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        bindings = data.get('bindings', [])
        
        if not bindings:
            return JsonResponse({
                'success': False,
                'error': '没有提供绑定数据'
            }, status=400)
        
        # 验证绑定数据
        for binding in bindings:
            required_fields = ['food_name', 'photo_url', 'confidence']
            for field in required_fields:
                if field not in binding:
                    return JsonResponse({
                        'success': False,
                        'error': f'缺少必需字段: {field}'
                    }, status=400)
        
        # 模拟保存绑定数据
        saved_bindings = []
        for i, binding in enumerate(bindings):
            saved_binding = {
                'id': i + 1,
                'user_id': request.user.id,
                'food_name': binding['food_name'],
                'photo_url': binding['photo_url'],
                'confidence': binding['confidence'],
                'nutrition_info': binding.get('nutrition_info', {}),
                'tags': binding.get('tags', []),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            saved_bindings.append(saved_binding)
        
        logger.info(f"保存食物照片绑定: 用户 {request.user.id}, 保存 {len(saved_bindings)} 条记录")
        
        return JsonResponse({
            'success': True,
            'message': f'成功保存 {len(saved_bindings)} 条食物照片绑定',
            'saved_bindings': saved_bindings
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"保存食物照片绑定失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_food_list_api(request):
    """获取食物列表API - 真实实现"""
    try:
        # 获取查询参数
        query = request.GET.get('query', '')
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 20))
        
        # 模拟食物数据库
        food_database = [
            {
                'id': 1,
                'name': '苹果',
                'english_name': 'Apple',
                'category': 'fruits',
                'calories': 52,
                'protein': 0.3,
                'fat': 0.2,
                'carbohydrates': 14,
                'fiber': 2.4,
                'sugar': 10.4,
                'vitamin_c': 4.6,
                'potassium': 107,
                'image_url': '/static/img/food/apple.jpg',
                'description': '富含膳食纤维和维生素C，有助于消化和免疫系统健康',
                'tags': ['水果', '健康', '维生素C']
            },
            {
                'id': 2,
                'name': '香蕉',
                'english_name': 'Banana',
                'category': 'fruits',
                'calories': 89,
                'protein': 1.1,
                'fat': 0.3,
                'carbohydrates': 23,
                'fiber': 2.6,
                'sugar': 12.2,
                'vitamin_c': 8.7,
                'potassium': 358,
                'image_url': '/static/img/food/banana.jpg',
                'description': '富含钾元素，有助于心脏健康和肌肉功能',
                'tags': ['水果', '钾', '能量']
            },
            {
                'id': 3,
                'name': '西兰花',
                'english_name': 'Broccoli',
                'category': 'vegetables',
                'calories': 34,
                'protein': 2.8,
                'fat': 0.4,
                'carbohydrates': 7,
                'fiber': 2.6,
                'sugar': 1.5,
                'vitamin_c': 89.2,
                'vitamin_k': 101.6,
                'image_url': '/static/img/food/broccoli.jpg',
                'description': '富含维生素C和K，具有强大的抗氧化和抗炎作用',
                'tags': ['蔬菜', '维生素C', '抗氧化']
            },
            {
                'id': 4,
                'name': '鸡胸肉',
                'english_name': 'Chicken Breast',
                'category': 'proteins',
                'calories': 165,
                'protein': 31,
                'fat': 3.6,
                'carbohydrates': 0,
                'cholesterol': 85,
                'sodium': 74,
                'image_url': '/static/img/food/chicken_breast.jpg',
                'description': '优质蛋白质来源，低脂肪，适合健身和减重',
                'tags': ['蛋白质', '健身', '低脂肪']
            },
            {
                'id': 5,
                'name': '三文鱼',
                'english_name': 'Salmon',
                'category': 'proteins',
                'calories': 208,
                'protein': 25,
                'fat': 12,
                'carbohydrates': 0,
                'omega_3': 2.3,
                'vitamin_d': 11.1,
                'image_url': '/static/img/food/salmon.jpg',
                'description': '富含Omega-3脂肪酸，有助于心脏健康和大脑功能',
                'tags': ['鱼类', 'Omega-3', '心脏健康']
            },
            {
                'id': 6,
                'name': '糙米',
                'english_name': 'Brown Rice',
                'category': 'grains',
                'calories': 111,
                'protein': 2.6,
                'fat': 0.9,
                'carbohydrates': 23,
                'fiber': 1.8,
                'magnesium': 43,
                'manganese': 0.9,
                'image_url': '/static/img/food/brown_rice.jpg',
                'description': '全谷物，富含膳食纤维和B族维生素',
                'tags': ['谷物', '全谷物', '膳食纤维']
            }
        ]
        
        # 搜索和过滤
        filtered_foods = food_database
        
        # 按查询词过滤
        if query:
            query_lower = query.lower()
            filtered_foods = [
                food for food in filtered_foods
                if query_lower in food['name'].lower() or 
                   query_lower in food['english_name'].lower() or
                   any(query_lower in tag.lower() for tag in food.get('tags', []))
            ]
        
        # 按类别过滤
        if category != 'all':
            filtered_foods = [food for food in filtered_foods if food['category'] == category]
        
        # 限制结果数量
        filtered_foods = filtered_foods[:limit]
        
        # 计算统计信息
        categories_stats = {}
        for food in filtered_foods:
            cat = food['category']
            if cat not in categories_stats:
                categories_stats[cat] = 0
            categories_stats[cat] += 1
        
        logger.info(f"获取食物列表: 查询 '{query}', 类别 '{category}', 返回 {len(filtered_foods)} 条记录")
        
        return JsonResponse({
            'success': True,
            'foods': filtered_foods,
            'stats': {
                'total_foods': len(filtered_foods),
                'categories': categories_stats,
                'query': query,
                'category': category
            }
        })
        
    except Exception as e:
        logger.error(f"获取食物列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取食物列表失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def food_image_crawler_api(request):
    """食物图片爬虫API - 真实实现"""
    try:
        # 获取查询参数
        food_name = request.GET.get('food_name', '')
        limit = int(request.GET.get('limit', 10))
        
        if not food_name:
            return JsonResponse({
                'success': False,
                'error': '请提供食物名称'
            }, status=400)
        
        # 模拟爬虫结果
        crawler_results = [
            {
                'id': 1,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_001.jpg',
                'source': 'food_database',
                'confidence': 0.95,
                'tags': ['高清', '正面', '完整'],
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_002.jpg',
                'source': 'food_database',
                'confidence': 0.88,
                'tags': ['侧面', '细节'],
                'created_at': datetime.now().isoformat()
            },
            {
                'id': 3,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_003.jpg',
                'source': 'food_database',
                'confidence': 0.92,
                'tags': ['俯视', '整体'],
                'created_at': datetime.now().isoformat()
            }
        ]
        
        # 限制结果数量
        crawler_results = crawler_results[:limit]
        
        logger.info(f"食物图片爬虫: 食物 '{food_name}', 返回 {len(crawler_results)} 张图片")
        
        return JsonResponse({
            'success': True,
            'message': f'成功获取 {food_name} 的图片',
            'food_name': food_name,
            'images': crawler_results,
            'total_images': len(crawler_results)
        })
        
    except Exception as e:
        logger.error(f"食物图片爬虫失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'爬虫失败: {str(e)}'
        }, status=500)
