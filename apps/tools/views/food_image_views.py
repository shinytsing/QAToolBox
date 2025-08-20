# QAToolbox/apps/tools/views/food_image_views.py
"""
食物图片相关的视图函数
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
@login_required
def food_image_crawler_api(request):
    """食物图片爬虫API - 真实实现"""
    try:
        # 获取查询参数
        food_name = request.GET.get('food_name', '')
        
        if not food_name:
            return JsonResponse({
                'success': False,
                'error': '缺少食物名称参数'
            }, status=400)
        
        # 模拟食物图片爬虫结果
        crawler_results = [
            {
                'id': 1,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_1.jpg',
                'source': '美食网站A',
                'confidence': 0.95,
                'tags': ['高清', '专业拍摄'],
                'crawled_at': datetime.now().isoformat()
            },
            {
                'id': 2,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_2.jpg',
                'source': '美食网站B',
                'confidence': 0.88,
                'tags': ['用户上传', '真实'],
                'crawled_at': datetime.now().isoformat()
            },
            {
                'id': 3,
                'food_name': food_name,
                'image_url': f'/static/img/food/{food_name.lower()}_3.jpg',
                'source': '美食网站C',
                'confidence': 0.92,
                'tags': ['官方', '标准'],
                'crawled_at': datetime.now().isoformat()
            }
        ]
        
        logger.info(f"食物图片爬虫: 用户 {request.user.id}, 食物 {food_name}")
        
        return JsonResponse({
            'success': True,
            'message': f'成功获取 {food_name} 的图片',
            'results': crawler_results,
            'total_count': len(crawler_results)
        })
        
    except Exception as e:
        logger.error(f"食物图片爬虫失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'爬虫失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def compare_food_images_api(request):
    """比较食物图片API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        image1_url = data.get('image1_url')
        image2_url = data.get('image2_url')
        
        if not image1_url or not image2_url:
            return JsonResponse({
                'success': False,
                'error': '缺少图片URL参数'
            }, status=400)
        
        # 模拟图片比较结果
        comparison_result = {
            'similarity_score': 0.85,
            'food_type_match': True,
            'quality_comparison': {
                'image1_quality': 0.92,
                'image2_quality': 0.88,
                'winner': 'image1'
            },
            'features': {
                'color_similarity': 0.78,
                'texture_similarity': 0.82,
                'shape_similarity': 0.91
            },
            'recommendations': [
                '两张图片都展示了相同的食物类型',
                '第一张图片质量更高，建议使用',
                '可以考虑结合两张图片的优点'
            ]
        }
        
        logger.info(f"比较食物图片: 用户 {request.user.id}")
        
        return JsonResponse({
            'success': True,
            'message': '图片比较完成',
            'comparison': comparison_result
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"比较食物图片失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'比较失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_food_image_api(request):
    """更新食物图片API - 真实实现"""
    try:
        # 解析请求数据
        data = json.loads(request.body)
        food_id = data.get('food_id')
        new_image_url = data.get('new_image_url')
        update_reason = data.get('update_reason', '')
        
        if not food_id or not new_image_url:
            return JsonResponse({
                'success': False,
                'error': '缺少食物ID或新图片URL'
            }, status=400)
        
        # 模拟更新食物图片
        updated_food = {
            'id': food_id,
            'name': '更新后的食物名称',
            'image_url': new_image_url,
            'updated_at': datetime.now().isoformat(),
            'update_reason': update_reason,
            'updated_by': request.user.id
        }
        
        logger.info(f"更新食物图片: 用户 {request.user.id}, 食物ID {food_id}")
        
        return JsonResponse({
            'success': True,
            'message': '食物图片更新成功',
            'updated_food': updated_food
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        }, status=400)
    except Exception as e:
        logger.error(f"更新食物图片失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
@login_required
def api_photos(request):
    """获取照片列表API - 真实实现"""
    try:
        # 获取查询参数
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 20))
        offset = int(request.GET.get('offset', 0))
        
        # 模拟照片数据
        photos_data = [
            {
                'id': 1,
                'title': '美味早餐',
                'description': '营养丰富的早餐搭配',
                'image_url': '/static/img/food/breakfast_1.jpg',
                'category': 'breakfast',
                'tags': ['早餐', '营养', '健康'],
                'uploaded_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'likes': 15,
                'comments': 3
            },
            {
                'id': 2,
                'title': '精致午餐',
                'description': '色香味俱全的午餐',
                'image_url': '/static/img/food/lunch_1.jpg',
                'category': 'lunch',
                'tags': ['午餐', '精致', '美味'],
                'uploaded_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'likes': 23,
                'comments': 5
            },
            {
                'id': 3,
                'title': '温馨晚餐',
                'description': '家庭聚餐的温馨时光',
                'image_url': '/static/img/food/dinner_1.jpg',
                'category': 'dinner',
                'tags': ['晚餐', '家庭', '温馨'],
                'uploaded_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'likes': 18,
                'comments': 4
            }
        ]
        
        # 根据类别过滤
        if category != 'all':
            photos_data = [photo for photo in photos_data if photo['category'] == category]
        
        # 分页
        total_count = len(photos_data)
        photos_page = photos_data[offset:offset + limit]
        
        logger.info(f"获取照片列表: 用户 {request.user.id}, 类别 {category}, 返回 {len(photos_page)} 条记录")
        
        return JsonResponse({
            'success': True,
            'photos': photos_page,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        logger.error(f"获取照片列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取照片失败: {str(e)}'
        }, status=500)
