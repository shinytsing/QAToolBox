"""
旅行攻略相关视图
按照产品文档重构的好心人攻略功能
"""

import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 导入相关模型
from ..models import TravelCity, TravelPost, TravelPostComment, TravelPostFavorite, TravelPostLike


def travel_post_home(request):
    """旅行攻略首页"""
    return render(request, "tools/travel_post_home.html")


@csrf_exempt
@require_http_methods(["GET"])
def travel_post_list_api(request):
    """获取旅行攻略列表API"""
    try:
        # 获取查询参数
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        sort_by = request.GET.get("sort", "latest")  # latest, popular, favorite
        search = request.GET.get("search", "").strip()

        # 筛选参数
        travel_styles = request.GET.getlist("travel_styles", [])
        cities = request.GET.getlist("cities", [])
        budget_min = request.GET.get("budget_min")
        budget_max = request.GET.get("budget_max")
        duration_min = request.GET.get("duration_min")
        duration_max = request.GET.get("duration_max")
        transportation_methods = request.GET.getlist("transportation_methods", [])

        # 地区筛选参数
        location_city = request.GET.get("location_city", "").strip()
        location_region = request.GET.get("location_region", "").strip()
        user_lat = request.GET.get("user_lat")
        user_lon = request.GET.get("user_lon")
        max_distance = request.GET.get("max_distance", 50)  # 最大距离（公里）

        # 构建查询
        queryset = (
            TravelPost.objects.filter(is_public=True, is_approved=True).select_related("user").prefetch_related("cities")
        )

        # 搜索筛选
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(cities__name__icontains=search) | Q(cities__country__icontains=search)
            ).distinct()

        # 旅行风格筛选
        if travel_styles:
            queryset = queryset.filter(travel_styles__overlap=travel_styles)

        # 城市筛选
        if cities:
            queryset = queryset.filter(cities__name__in=cities)

        # 预算筛选
        if budget_min:
            queryset = queryset.filter(budget_amount__gte=float(budget_min))
        if budget_max:
            queryset = queryset.filter(budget_amount__lte=float(budget_max))

        # 旅行时长筛选
        if duration_min or duration_max:
            # 这里需要根据实际的时长格式进行解析
            pass

        # 交通方式筛选
        if transportation_methods:
            queryset = queryset.filter(transportation_methods__overlap=transportation_methods)

        # 地区筛选
        if location_city:
            queryset = queryset.filter(location_city__icontains=location_city)
        if location_region:
            queryset = queryset.filter(location_region__icontains=location_region)

        # 排序
        if sort_by == "popular":
            queryset = queryset.order_by("-like_count", "-view_count", "-created_at")
        elif sort_by == "favorite":
            queryset = queryset.order_by("-favorite_count", "-view_count", "-created_at")
        else:  # latest
            queryset = queryset.order_by("-created_at")

        # 分页
        paginator = Paginator(queryset, page_size)
        posts = paginator.get_page(page)

        # 格式化数据
        posts_data = []
        for post in posts:
            # 检查用户是否已点赞/收藏
            is_liked = False
            is_favorited = False
            if request.user.is_authenticated:
                is_liked = TravelPostLike.objects.filter(user=request.user, post=post).exists()
                is_favorited = TravelPostFavorite.objects.filter(user=request.user, post=post).exists()

            # 计算距离（如果用户提供了位置信息）
            distance = None
            if user_lat and user_lon and post.location_latitude and post.location_longitude:
                try:
                    distance = post.calculate_distance_to(float(user_lat), float(user_lon))
                except (ValueError, TypeError):
                    distance = None

            posts_data.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "cover_image": post.cover_image.url if post.cover_image else None,
                    "travel_styles": post.get_travel_styles_display(),
                    "cities": [{"name": city.name, "country": city.country} for city in post.cities.all()],
                    "travel_duration": post.travel_duration,
                    "travel_date": post.travel_date.strftime("%Y-%m") if post.travel_date else None,
                    "budget_amount": float(post.budget_amount),
                    "budget_currency": post.budget_currency,
                    "budget_type": post.get_budget_type_display(),
                    "transportation_methods": post.get_transportation_methods_display(),
                    "custom_tags": post.custom_tags,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "favorite_count": post.favorite_count,
                    "comment_count": post.comment_count,
                    "is_liked": is_liked,
                    "is_favorited": is_favorited,
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
                    "user": {
                        "id": post.user.id,
                        "username": post.user.username,
                        "avatar": getattr(post.user.profile, "avatar", None),
                    },
                    # 位置信息
                    "location": {
                        "city": post.location_city,
                        "region": post.location_region,
                        "address": post.location_address,
                        "lat": post.location_latitude,
                        "lon": post.location_longitude,
                        "radius": post.location_radius,
                        "display": post.get_location_display(),
                    },
                    "distance": distance,
                }
            )

        return JsonResponse(
            {
                "success": True,
                "posts": posts_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "has_next": posts.has_next(),
                "has_previous": posts.has_previous(),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取攻略列表失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def travel_post_create_api(request):
    """创建旅行攻略API"""
    try:
        # 处理表单数据
        title = request.POST.get("title", "").strip()
        travel_styles = json.loads(request.POST.get("travel_styles", "[]"))
        city_ids = json.loads(request.POST.get("city_ids", "[]"))
        travel_duration = request.POST.get("travel_duration", "").strip()
        travel_date_str = request.POST.get("travel_date", "").strip()
        budget_amount = request.POST.get("budget_amount", "").strip()
        budget_currency = request.POST.get("budget_currency", "CNY")
        budget_type = request.POST.get("budget_type", "total")
        itinerary_details = json.loads(request.POST.get("itinerary_details", "[]"))
        transportation_methods = json.loads(request.POST.get("transportation_methods", "[]"))
        food_recommendations = json.loads(request.POST.get("food_recommendations", "[]"))
        accommodation_recommendations = request.POST.get("accommodation_recommendations", "").strip()
        travel_tips = request.POST.get("travel_tips", "").strip()
        custom_tags = json.loads(request.POST.get("custom_tags", "[]"))

        # 验证必填字段
        if not title:
            return JsonResponse({"success": False, "error": "请填写攻略标题"}, status=400)

        if not travel_styles:
            return JsonResponse({"success": False, "error": "请选择旅行风格"}, status=400)

        if not city_ids:
            return JsonResponse({"success": False, "error": "请选择关联城市"}, status=400)

        if not travel_duration:
            return JsonResponse({"success": False, "error": "请填写旅行时长"}, status=400)

        if not budget_amount:
            return JsonResponse({"success": False, "error": "请填写人均预算"}, status=400)

        if not itinerary_details:
            return JsonResponse({"success": False, "error": "请填写行程明细"}, status=400)

        # 处理封面图
        cover_image = request.FILES.get("cover_image")
        if not cover_image:
            return JsonResponse({"success": False, "error": "请上传封面图"}, status=400)

        # 验证文件类型和大小
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if cover_image.content_type not in allowed_types:
            return JsonResponse({"success": False, "error": "封面图格式不支持，请上传JPG、PNG或WebP格式"}, status=400)

        if cover_image.size > 10 * 1024 * 1024:  # 10MB
            return JsonResponse({"success": False, "error": "封面图大小不能超过10MB"}, status=400)

        # 处理出行时间
        travel_date = None
        if travel_date_str:
            try:
                travel_date = datetime.strptime(travel_date_str, "%Y-%m").date()
            except ValueError:
                pass

        # 创建攻略
        post = TravelPost.objects.create(
            user=request.user,
            title=title,
            cover_image=cover_image,
            travel_styles=travel_styles,
            travel_duration=travel_duration,
            travel_date=travel_date,
            budget_amount=budget_amount,
            budget_currency=budget_currency,
            budget_type=budget_type,
            itinerary_details=itinerary_details,
            transportation_methods=transportation_methods,
            food_recommendations=food_recommendations,
            accommodation_recommendations=accommodation_recommendations,
            travel_tips=travel_tips,
            custom_tags=custom_tags,
        )

        # 关联城市
        cities = TravelCity.objects.filter(id__in=city_ids)
        post.cities.set(cities)

        return JsonResponse({"success": True, "message": "攻略创建成功！", "post_id": post.id})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"创建攻略失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def travel_post_detail_api(request, post_id):
    """获取旅行攻略详情API"""
    try:
        post = get_object_or_404(TravelPost, id=post_id, is_public=True, is_approved=True)

        # 增加查看次数
        post.increment_view_count()

        # 检查用户是否已点赞/收藏
        is_liked = False
        is_favorited = False
        if request.user.is_authenticated:
            is_liked = TravelPostLike.objects.filter(user=request.user, post=post).exists()
            is_favorited = TravelPostFavorite.objects.filter(user=request.user, post=post).exists()

        # 提取自动聚合的清单
        food_list = post.extract_food_list()
        attractions_list = post.extract_attractions_list()

        # 格式化数据
        post_data = {
            "id": post.id,
            "title": post.title,
            "cover_image": post.cover_image.url if post.cover_image else None,
            "travel_styles": post.get_travel_styles_display(),
            "cities": [{"name": city.name, "country": city.country} for city in post.cities.all()],
            "travel_duration": post.travel_duration,
            "travel_date": post.travel_date.strftime("%Y-%m") if post.travel_date else None,
            "budget_amount": float(post.budget_amount),
            "budget_currency": post.budget_currency,
            "budget_type": post.get_budget_type_display(),
            "itinerary_details": post.itinerary_details,
            "transportation_methods": post.get_transportation_methods_display(),
            "food_recommendations": post.food_recommendations,
            "accommodation_recommendations": post.accommodation_recommendations,
            "travel_tips": post.travel_tips,
            "custom_tags": post.custom_tags,
            "view_count": post.view_count,
            "like_count": post.like_count,
            "favorite_count": post.favorite_count,
            "comment_count": post.comment_count,
            "is_liked": is_liked,
            "is_favorited": is_favorited,
            "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
            "user": {"id": post.user.id, "username": post.user.username, "avatar": getattr(post.user.profile, "avatar", None)},
            # 自动聚合的清单
            "food_list": food_list,
            "attractions_list": attractions_list,
        }

        return JsonResponse({"success": True, "post": post_data})

    except TravelPost.DoesNotExist:
        return JsonResponse({"success": False, "error": "攻略不存在或已被删除"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取攻略详情失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def travel_post_like_api(request, post_id):
    """点赞/取消点赞攻略API"""
    try:
        post = get_object_or_404(TravelPost, id=post_id, is_public=True, is_approved=True)

        like, created = TravelPostLike.objects.get_or_create(user=request.user, post=post)

        if created:
            # 新增点赞
            post.increment_like_count()
            message = "点赞成功"
        else:
            # 取消点赞
            like.delete()
            post.like_count = max(0, post.like_count - 1)
            post.save(update_fields=["like_count"])
            message = "取消点赞成功"

        return JsonResponse({"success": True, "message": message, "is_liked": created, "like_count": post.like_count})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def travel_post_favorite_api(request, post_id):
    """收藏/取消收藏攻略API"""
    try:
        post = get_object_or_404(TravelPost, id=post_id, is_public=True, is_approved=True)

        favorite, created = TravelPostFavorite.objects.get_or_create(user=request.user, post=post)

        if created:
            # 新增收藏
            post.increment_favorite_count()
            message = "收藏成功"
        else:
            # 取消收藏
            favorite.delete()
            post.favorite_count = max(0, post.favorite_count - 1)
            post.save(update_fields=["favorite_count"])
            message = "取消收藏成功"

        return JsonResponse(
            {"success": True, "message": message, "is_favorited": created, "favorite_count": post.favorite_count}
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET", "POST"])
def travel_post_comment_api(request, post_id):
    """攻略评论API"""
    try:
        post = get_object_or_404(TravelPost, id=post_id, is_public=True, is_approved=True)

        if request.method == "GET":
            # 获取评论列表
            comments = (
                TravelPostComment.objects.filter(post=post, parent=None)  # 只获取顶级评论
                .select_related("user")
                .prefetch_related("travelpostcomment_set")
                .order_by("-created_at")
            )

            comments_data = []
            for comment in comments:
                # 获取回复
                replies = []
                for reply in comment.travelpostcomment_set.all():
                    replies.append(
                        {
                            "id": reply.id,
                            "content": reply.content,
                            "created_at": reply.created_at.strftime("%Y-%m-%d %H:%M"),
                            "user": {
                                "id": reply.user.id,
                                "username": reply.user.username,
                                "avatar": getattr(reply.user.profile, "avatar", None),
                            },
                        }
                    )

                comments_data.append(
                    {
                        "id": comment.id,
                        "content": comment.content,
                        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
                        "user": {
                            "id": comment.user.id,
                            "username": comment.user.username,
                            "avatar": getattr(comment.user.profile, "avatar", None),
                        },
                        "replies": replies,
                    }
                )

            return JsonResponse({"success": True, "comments": comments_data})

        elif request.method == "POST":
            # 发表评论
            if not request.user.is_authenticated:
                return JsonResponse({"success": False, "error": "请先登录后再发表评论"}, status=401)

            data = json.loads(request.body)
            content = data.get("content", "").strip()
            parent_id = data.get("parent_id")

            if not content:
                return JsonResponse({"success": False, "error": "请填写评论内容"}, status=400)

            # 创建评论
            parent = None
            if parent_id:
                try:
                    parent = TravelPostComment.objects.get(id=parent_id, post=post)
                except TravelPostComment.DoesNotExist:
                    pass

            comment = TravelPostComment.objects.create(user=request.user, post=post, parent=parent, content=content)

            # 增加评论数
            post.increment_comment_count()

            return JsonResponse(
                {
                    "success": True,
                    "message": "评论发表成功",
                    "comment": {
                        "id": comment.id,
                        "content": comment.content,
                        "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M"),
                        "user": {
                            "id": comment.user.id,
                            "username": comment.user.username,
                            "avatar": getattr(comment.user.profile, "avatar", None),
                        },
                    },
                }
            )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def travel_city_list_api(request):
    """获取城市列表API"""
    try:
        search = request.GET.get("search", "").strip()

        queryset = TravelCity.objects.filter(is_active=True)

        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(country__icontains=search))

        cities_data = []
        for city in queryset[:50]:  # 限制返回数量
            cities_data.append(
                {
                    "id": city.id,
                    "name": city.name,
                    "country": city.country,
                    "region": city.region,
                    "display_name": f"{city.name}, {city.country}",
                }
            )

        return JsonResponse({"success": True, "cities": cities_data})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取城市列表失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def user_favorites_api(request):
    """获取用户收藏的攻略API"""
    try:
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        favorites = (
            TravelPostFavorite.objects.filter(user=request.user)
            .select_related("post", "post__user")
            .prefetch_related("post__cities")
            .order_by("-created_at")
        )

        paginator = Paginator(favorites, page_size)
        favorites_page = paginator.get_page(page)

        favorites_data = []
        for favorite in favorites_page:
            post = favorite.post
            favorites_data.append(
                {
                    "id": post.id,
                    "title": post.title,
                    "cover_image": post.cover_image.url if post.cover_image else None,
                    "travel_styles": post.get_travel_styles_display(),
                    "cities": [{"name": city.name, "country": city.country} for city in post.cities.all()],
                    "travel_duration": post.travel_duration,
                    "budget_amount": float(post.budget_amount),
                    "budget_currency": post.budget_currency,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "favorite_count": post.favorite_count,
                    "created_at": post.created_at.strftime("%Y-%m-%d %H:%M"),
                    "user": {
                        "id": post.user.id,
                        "username": post.user.username,
                        "avatar": getattr(post.user.profile, "avatar", None),
                    },
                    "favorited_at": favorite.created_at.strftime("%Y-%m-%d %H:%M"),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "favorites": favorites_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取收藏列表失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def map_picker_api(request):
    """地图选择器API - 获取位置建议"""
    try:
        query = request.GET.get("query", "").strip()
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        if not query and not (lat and lon):
            return JsonResponse({"success": False, "error": "请提供搜索关键词或坐标"}, status=400)

        # 如果提供了坐标，进行反向地理编码
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                # 这里可以集成实际的地图API进行反向地理编码
                # 目前使用模拟数据
                location_data = {
                    "address": f"坐标位置 ({lat:.4f}, {lon:.4f})",
                    "city": "未知城市",
                    "region": "未知地区",
                    "country": "中国",
                    "lat": lat,
                    "lon": lon,
                }
            except ValueError:
                return JsonResponse({"success": False, "error": "无效的坐标格式"}, status=400)
        else:
            # 搜索位置建议
            suggestions = search_location_suggestions(query)
            return JsonResponse({"success": True, "suggestions": suggestions})

        return JsonResponse({"success": True, "location": location_data})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"地图选择器API失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_post_location_api(request):
    """更新攻略位置信息API"""
    try:
        data = json.loads(request.body)
        post_id = data.get("post_id")
        location_data = data.get("location", {})

        if not post_id:
            return JsonResponse({"success": False, "error": "请提供攻略ID"}, status=400)

        try:
            post = TravelPost.objects.get(id=post_id, user=request.user)
        except TravelPost.DoesNotExist:
            return JsonResponse({"success": False, "error": "攻略不存在或无权限修改"}, status=404)

        # 更新位置信息
        post.location_city = location_data.get("city", "")
        post.location_region = location_data.get("region", "")
        post.location_address = location_data.get("address", "")
        post.location_latitude = location_data.get("lat")
        post.location_longitude = location_data.get("lon")
        post.location_radius = location_data.get("radius", 50)

        post.save()

        return JsonResponse(
            {
                "success": True,
                "message": "位置信息更新成功",
                "location": {
                    "city": post.location_city,
                    "region": post.location_region,
                    "address": post.location_address,
                    "lat": post.location_latitude,
                    "lon": post.location_longitude,
                    "radius": post.location_radius,
                    "display": post.get_location_display(),
                },
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": f"更新位置信息失败: {str(e)}"}, status=500)


def search_location_suggestions(query):
    """搜索位置建议"""
    # 模拟位置搜索建议
    # 实际项目中可以集成高德地图、百度地图等API
    common_cities = [
        "北京",
        "上海",
        "广州",
        "深圳",
        "杭州",
        "南京",
        "武汉",
        "成都",
        "西安",
        "重庆",
        "天津",
        "苏州",
        "青岛",
        "大连",
        "厦门",
        "宁波",
        "无锡",
        "长沙",
        "郑州",
        "济南",
    ]

    suggestions = []

    # 精确匹配城市名
    for city in common_cities:
        if query in city or city in query:
            suggestions.append(
                {"name": city, "type": "city", "address": f"{city}市", "city": city, "region": f"{city}市", "country": "中国"}
            )

    # 添加一些常见的地址模式
    address_patterns = [
        f"{query}市中心",
        f"{query}火车站",
        f"{query}机场",
        f"{query}大学",
        f"{query}购物中心",
        f"{query}地铁站",
    ]

    for pattern in address_patterns:
        suggestions.append(
            {"name": pattern, "type": "address", "address": pattern, "city": query, "region": "用户选择", "country": "中国"}
        )

    return suggestions[:10]  # 限制返回数量
