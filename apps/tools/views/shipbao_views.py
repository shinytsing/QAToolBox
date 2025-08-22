"""
船宝相关视图
包含二手交易、收藏、位置筛选等功能
"""

import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

# 导入相关模型
from ..models import ShipBaoItem, ShipBaoTransaction, ShipBaoUserProfile
# 暂时注释掉不存在的模型
# from ..models import ShipBaoFavorite, ShipBaoInquiry


def shipbao_home(request):
    """船宝首页"""
    return render(request, 'tools/shipbao_home.html')


def shipbao_detail(request, item_id):
    """船宝商品详情页"""
    try:
        item = ShipBaoItem.objects.get(id=item_id, is_active=True)
        # 增加浏览次数
        item.increment_view_count()
        
        # 暂时禁用收藏功能
        is_favorited = False
        
    except ShipBaoItem.DoesNotExist:
        item = None
        is_favorited = False
    
    context = {
        'item': item,
        'item_id': item_id,
        'is_favorited': is_favorited
    }
    return render(request, 'tools/shipbao_detail.html', context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_favorites_api(request):
    """船宝收藏API - 暂时不可用"""
    return JsonResponse({
        'success': False,
        'error': '收藏功能暂时不可用，正在维护中'
    }, status=503)


@csrf_exempt
@require_http_methods(["GET"])
def shipbao_items_api(request):
    """获取船宝商品列表API"""
    try:
        # 获取查询参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        search = request.GET.get('search', '').strip()
        
        # 筛选参数
        category = request.GET.get('category', '')
        price_min = request.GET.get('price_min')
        price_max = request.GET.get('price_max')
        delivery_option = request.GET.get('delivery_option', '')
        
        # 地区筛选参数
        location_city = request.GET.get('location_city', '').strip()
        user_lat = request.GET.get('user_lat')
        user_lon = request.GET.get('user_lon')
        max_distance = request.GET.get('max_distance', 50)
        
        # 构建查询
        queryset = ShipBaoItem.objects.filter(
            is_active=True
        ).select_related('seller')
        
        # 搜索筛选
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location_city__icontains=search)
            ).distinct()
        
        # 分类筛选
        if category:
            queryset = queryset.filter(category=category)
        
        # 地区筛选
        if location_city:
            queryset = queryset.filter(location_city__icontains=location_city)
        
        # 价格筛选
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))
        
        # 交易方式筛选
        if delivery_option:
            queryset = queryset.filter(delivery_option=delivery_option)
        
        # 排序
        queryset = queryset.order_by('-created_at')
        
        # 分页
        paginator = Paginator(queryset, page_size)
        items = paginator.get_page(page)
        
        # 格式化数据
        items_data = []
        for item in items:
            # 计算距离
            distance = None
            if user_lat and user_lon and item.location_latitude and item.location_longitude:
                try:
                    distance = item.calculate_distance_to(float(user_lat), float(user_lon))
                except (ValueError, TypeError):
                    distance = None
            
            # 检查用户是否已收藏
            is_favorited = False
            if request.user.is_authenticated:
                is_favorited = ShipBaoFavorite.objects.filter(
                    user=request.user, 
                    item=item
                ).exists()
            
            items_data.append({
                'id': item.id,
                'title': item.title,
                'description': item.description[:100] + '...' if len(item.description) > 100 else item.description,
                'category': item.category,
                'category_display': item.get_category_display_name(),
                'condition': item.condition,
                'condition_stars': item.get_condition_stars(),
                'price': float(item.price),
                'original_price': float(item.original_price) if item.original_price else None,
                'can_bargain': item.can_bargain,
                'main_image': item.main_image.url if item.main_image else None,
                'delivery_option': item.delivery_option,
                'location': {
                    'city': item.location_city,
                    'region': item.location_region,
                    'address': item.location_address,
                    'display': item.get_location_display()
                },
                'distance': distance,
                'view_count': item.view_count,
                'favorite_count': item.favorite_count,
                'inquiry_count': item.inquiry_count,
                'is_favorited': is_favorited,
                'is_sold': item.is_sold,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M'),
                'seller': {
                    'id': item.seller.id,
                    'username': item.seller.username
                }
            })
        
        return JsonResponse({
            'success': True,
            'items': items_data,
            'total': paginator.count,
            'page': page,
            'page_size': page_size,
            'total_pages': paginator.num_pages,
            'has_next': items.has_next(),
            'has_previous': items.has_previous()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取商品列表失败: {str(e)}'
        }, status=500)
