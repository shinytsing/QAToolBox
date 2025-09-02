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
def api_photos(request):
    """获取照片列表API - 使用真实照片文件"""
    try:
        # 获取查询参数
        category = request.GET.get('category', 'all')
        limit = int(request.GET.get('limit', 200))
        offset = int(request.GET.get('offset', 0))
        
        # 使用真实的照片文件数据（从实际存在的文件中获取）
        real_photos = [
            'beef-4805622_1280.jpg', 'bibimbap-1738580_1280.jpg', 'braise-pork-1398308_1280.jpg',
            'bread-1836411_1280.jpg', 'bread-6725352_1280.jpg', 'chinese-3855829_1280.jpg',
            'chinese-5233490_1280.jpg', 'chinese-5233510_1280.jpg', 'chinese-841179_1280.jpg',
            'chinese-915325_1280.jpg', 'chinese-916623_1280.jpg', 'chinese-916629_1280.jpg',
            'chongqing-6764962_1280.jpg', 'crayfish-866400_1280.jpg', 'cross-bridge-tofu-4866594_1280.jpg',
            'duck-2097959_1280.jpg', 'duck-253846_1280.jpg', 'eat-235771_1280.jpg',
            'egg-roll-6353108_1280.jpg', 'food-3228058_1280.jpg', 'food-5983402_1280.jpg',
            'food-5983403_1280.jpg', 'food-835469_1280.jpg', 'food-and-drink-8076626_1280.jpg',
            'food-photography-2358899_1280.jpg', 'food-photography-2610863_1280.jpg', 'food-photography-2610864_1280.jpg',
            'food-shoot-675564_1280.jpg', 'green-dragon-vegetable-1707089_1280.jpg', 'korean-barbecue-8579177_1280.jpg',
            'lanzhou-6896276_1280.jpg', 'macarons-2179198_1280.jpg', 'mapo-tofu-2570173_1280.jpg',
            'pancakes-2139844_1280.jpg', 'pasta-7209002_1280.jpg', 'pizza-6478478_1280.jpg',
            'ramen-4647408_1280.jpg', 'ramen-4647411_1280.jpg', 'ramen-7382882_1280.jpg',
            'rice-6364832_1280.jpg', 'roast-3416333_1280.jpg', 'seafood-4265995_1280.jpg',
            'seafood-4265999_1280.jpg', 'shrimp-6902940_1280.jpg', 'steak-6278031_1280.jpg',
            'steak-6714964_1280.jpg', 'steamed-fish-3495930_1280.jpg', 'sushi-2009611_1280.jpg',
            'the-pork-fried-rice-made-908333_1280.jpg', 'tofu-7525311_1280.jpg', 'toppokki-1607479_1280.jpg',
            'udon-noodles-4065311_1280.jpg', 'vegetarian-1141242_1280.jpg'
        ]
        
        # 生成照片数据
        photos_data = []
        for i, photo_file in enumerate(real_photos):
            # 根据文件名推断菜系
            photo_category = 'chinese'  # 默认中餐
            if 'japanese' in photo_file or 'ramen' in photo_file:
                photo_category = 'japanese'
            elif 'korean' in photo_file or 'bibimbap' in photo_file or 'gimbap' in photo_file:
                photo_category = 'korean'
            elif 'pasta' in photo_file or 'pizza' in photo_file or 'salad' in photo_file or 'steak' in photo_file:
                photo_category = 'western'
            elif 'chinese' in photo_file:
                photo_category = 'chinese'
            
            # 生成显示名称
            display_name = photo_file.replace('_1280.jpg', '').replace('-', ' ').title()
            
            photos_data.append({
                'id': i + 1,
                'name': photo_file,
                'display_name': display_name,
                'url': f'/static/img/food/{photo_file}',
                'category': photo_category,
                'tags': [photo_category, '美食', '图片'],
                'uploaded_at': (datetime.now() - timedelta(days=i+1)).isoformat()
            })
        
        # 根据类别过滤
        if category != 'all':
            photos_data = [photo for photo in photos_data if photo['category'] == category]
        
        # 分页
        total_count = len(photos_data)
        photos_page = photos_data[offset:offset + limit]
        
        logger.info(f"获取照片列表: 用户 {request.user.id}, 类别 {category}, 返回 {len(photos_page)} 条记录")
        
        return JsonResponse(photos_page, safe=False)
        
    except Exception as e:
        logger.error(f"获取照片列表失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'获取照片失败: {str(e)}'
        }, status=500)