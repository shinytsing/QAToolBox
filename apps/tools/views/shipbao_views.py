"""
船宝相关视图
包含二手交易、收藏、位置筛选等功能
"""

import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 导入相关模型
from ..models.legacy_models import ShipBaoFavorite, ShipBaoItem, ShipBaoTransaction, ShipBaoUserProfile, ShipBaoWantItem


def shipbao_home(request):
    """船宝首页"""
    return render(request, "tools/shipbao_home.html")


def shipbao_detail(request, item_id):
    """船宝商品详情页"""
    try:
        item = ShipBaoItem.objects.get(id=item_id, status="pending")

        # 增加浏览次数
        item.view_count += 1
        item.save()

        # 检查用户是否已收藏
        is_favorited = False
        if request.user.is_authenticated:
            is_favorited = ShipBaoFavorite.objects.filter(user=request.user, item=item).exists()

        # 获取想要此商品的人数
        want_count = item.want_count

        # 如果是卖家，获取想要此商品的用户列表
        interested_users = []
        if request.user.is_authenticated and request.user == item.seller:
            want_list = ShipBaoWantItem.objects.filter(item=item).select_related("user").order_by("-created_at")

            interested_users = []
            for want in want_list:
                interested_users.append(
                    {
                        "user_id": want.user.id,
                        "username": want.user.username,
                        "message": want.message,
                        "created_at": want.created_at.isoformat(),
                    }
                )

        context = {
            "item": item,
            "item_id": item_id,
            "is_favorited": is_favorited,
            "want_count": want_count,
            "interested_users": interested_users,
            "is_seller": request.user.is_authenticated and request.user == item.seller,
        }

    except ShipBaoItem.DoesNotExist:
        context = {
            "item": None,
            "item_id": item_id,
            "is_favorited": False,
            "want_count": 0,
            "interested_users": [],
            "is_seller": False,
        }

    return render(request, "tools/shipbao_detail.html", context)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_favorites_api(request):
    """船宝收藏API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        action = data.get("action", "add")  # add 或 remove

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id, status="pending")
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否已经收藏
        existing_favorite = ShipBaoFavorite.objects.filter(user=request.user, item=item).first()

        if action == "add":
            if existing_favorite:
                return JsonResponse({"success": False, "error": "已经收藏过此商品"})

            # 创建收藏记录
            ShipBaoFavorite.objects.create(user=request.user, item=item)

            # 更新商品收藏数
            item.favorite_count += 1
            item.save()

            return JsonResponse({"success": True, "message": "收藏成功", "is_favorited": True})

        elif action == "remove":
            if not existing_favorite:
                return JsonResponse({"success": False, "error": "未收藏此商品"})

            # 删除收藏记录
            existing_favorite.delete()

            # 更新商品收藏数
            item.favorite_count = max(0, item.favorite_count - 1)
            item.save()

            return JsonResponse({"success": True, "message": "取消收藏成功", "is_favorited": False})

        else:
            return JsonResponse({"success": False, "error": "无效的操作"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def shipbao_items_api(request):
    """获取船宝商品列表API"""
    try:
        # 获取查询参数
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        search = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sort_by", "created_at")

        # 筛选参数
        category = request.GET.get("category", "")
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")
        delivery_option = request.GET.get("delivery_option", "")

        # 地区筛选参数
        location_city = request.GET.get("location_city", "").strip()
        user_city = request.GET.get("city", "").strip()  # 用户位置城市
        user_lat = request.GET.get("user_lat")
        user_lon = request.GET.get("user_lon")
        max_distance_str = request.GET.get("max_distance", "")
        max_distance = float(max_distance_str) if max_distance_str else None

        # 构建查询
        queryset = ShipBaoItem.objects.filter(status="pending").select_related("seller")

        # 搜索筛选
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search) | Q(location_city__icontains=search)
            ).distinct()

        # 分类筛选
        if category:
            queryset = queryset.filter(category=category)

        # 地区筛选
        if location_city:
            if location_city == "nearby":
                # 附近筛选 - 需要用户位置信息
                if user_lat and user_lon:
                    # 这里先不过滤，在后续处理中根据距离筛选
                    pass
                else:
                    # 没有位置信息时，显示同城商品
                    queryset = queryset.filter(location_city__isnull=False)
            elif location_city == "same-city":
                # 同城筛选 - 需要用户位置信息
                if user_lat and user_lon:
                    # 这里先不过滤，在后续处理中根据距离筛选
                    pass
                else:
                    # 没有位置信息时，显示所有有城市信息的商品
                    queryset = queryset.filter(location_city__isnull=False)
            elif location_city == "same-region":
                # 同省筛选 - 需要用户位置信息
                if user_lat and user_lon:
                    # 这里先不过滤，在后续处理中根据距离筛选
                    pass
                else:
                    # 没有位置信息时，显示所有有城市信息的商品
                    queryset = queryset.filter(location_city__isnull=False)
            else:
                # 具体城市筛选
                queryset = queryset.filter(location_city__icontains=location_city)
        else:
            # 没有设置地区筛选条件，但有用户位置信息时，显示所有商品让距离筛选处理
            # 如果没有用户位置信息，也显示所有商品
            pass

        # 价格筛选
        if price_min:
            queryset = queryset.filter(price__gte=float(price_min))
        if price_max:
            queryset = queryset.filter(price__lte=float(price_max))

        # 交易方式筛选
        if delivery_option:
            queryset = queryset.filter(delivery_option=delivery_option)

        # 排序
        if sort_by == "price":
            queryset = queryset.order_by("price")
        elif sort_by == "price_desc":
            queryset = queryset.order_by("-price")
        elif sort_by == "favorite_count":
            queryset = queryset.order_by("-favorite_count")
        elif sort_by == "distance" and user_lat and user_lon:
            # 距离排序需要特殊处理，这里先用创建时间排序
            # 距离排序将在后续处理中实现
            queryset = queryset.order_by("-created_at")
        else:  # created_at or default
            queryset = queryset.order_by("-created_at")

        # 分页
        paginator = Paginator(queryset, page_size)
        items = paginator.get_page(page)

        # 格式化数据
        items_data = []
        for item in items:
            # 计算距离
            distance = None
            if user_lat and user_lon and item.latitude and item.longitude:
                try:
                    distance = item.calculate_distance_to(float(user_lat), float(user_lon))
                except (ValueError, TypeError):
                    distance = None

            # 根据距离范围筛选
            if user_lat and user_lon and distance is not None and max_distance is not None:
                # 距离范围筛选
                if distance > max_distance:
                    continue

                # 地区筛选逻辑
                if location_city == "nearby":
                    # 附近筛选 - 20公里内
                    if distance > 20:
                        continue
                elif location_city == "same-city":
                    # 同城筛选 - 50公里内
                    if distance > 50:
                        continue
                elif location_city == "same-region":
                    # 同省筛选 - 200公里内
                    if distance > 200:
                        continue

            # 检查用户是否已收藏
            is_favorited = False
            # if request.user.is_authenticated:
            #     is_favorited = ShipBaoFavorite.objects.filter(
            #         user=request.user,
            #         item=item
            #     ).exists()

            items_data.append(
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description[:100] + "..." if len(item.description) > 100 else item.description,
                    "category": item.category,
                    "category_display": item.get_category_display(),
                    "condition": item.condition,
                    "condition_stars": item.get_condition_stars(),
                    "price": float(item.price),
                    "can_bargain": item.can_bargain,
                    "main_image": item.get_main_image(),
                    "delivery_option": item.delivery_option,
                    "location": {
                        "city": item.location_city,
                        "region": item.location_region,
                        "address": item.location_address,
                        "display": item.get_location_display(),
                    },
                    "distance": round(distance, 2) if distance is not None else None,
                    "view_count": item.view_count,
                    "favorite_count": item.favorite_count,
                    "is_favorited": is_favorited,
                    "status": item.status,
                    "created_at": item.created_at.strftime("%Y-%m-%d %H:%M"),
                    "seller": {"id": item.seller.id, "username": item.seller.username},
                }
            )

        # 如果按距离排序，需要重新排序
        if sort_by == "distance" and user_lat and user_lon:
            items_data.sort(key=lambda x: x["distance"] if x["distance"] is not None else float("inf"))

        return JsonResponse(
            {
                "success": True,
                "items": items_data,
                "total": paginator.count,
                "page": page,
                "page_size": page_size,
                "total_pages": paginator.num_pages,
                "has_next": items.has_next(),
                "has_previous": items.has_previous(),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取商品列表失败: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_initiate_transaction_api(request):
    """发起船宝交易API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        message = data.get("message", "")

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id, status="pending")
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否是自己的商品
        if request.user == item.seller:
            return JsonResponse({"success": False, "error": "不能购买自己的商品"})

        # 检查是否已经发起过交易
        from ..models.legacy_models import ShipBaoTransaction

        existing_transaction = ShipBaoTransaction.objects.filter(
            item=item, buyer=request.user, status__in=["initiated", "negotiating"]
        ).first()

        if existing_transaction:
            return JsonResponse({"success": False, "error": "您已经发起过交易请求"})

        # 创建交易记录
        transaction = ShipBaoTransaction.objects.create(item=item, buyer=request.user, seller=item.seller, status="initiated")

        # 如果有消息，创建聊天记录
        if message:
            from ..models.legacy_models import ShipBaoMessage

            ShipBaoMessage.objects.create(transaction=transaction, sender=request.user, content=message)

        # 自动创建想要记录（如果不存在）
        want_record, want_created = ShipBaoWantItem.objects.get_or_create(
            user=request.user, item=item, defaults={"message": "发起交易"}
        )

        # 如果是新创建的想要记录，增加想要人数
        if want_created:
            item.increment_want_count()

        return JsonResponse(
            {"success": True, "message": "交易请求已发送", "transaction_id": transaction.id, "want_count": item.want_count}
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"发起交易失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_contact_seller_api(request):
    """联系卖家API - 集成心动链接聊天系统"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        message = data.get("message", "")

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id, status="pending")
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否是自己的商品
        if request.user == item.seller:
            return JsonResponse({"success": False, "error": "不能联系自己"})

        # 使用心动链接聊天系统
        import uuid

        from django.db import IntegrityError, transaction

        from ..models.chat_models import ChatMessage, ChatRoom

        # 使用咨询队列系统来管理并发
        from ..models.legacy_models import ShipBaoInquiry

        # 首先检查是否已经有咨询记录
        existing_inquiry = ShipBaoInquiry.objects.filter(item=item, buyer=request.user).first()

        # 记录是否需要重用现有咨询记录
        reuse_inquiry = None

        if existing_inquiry:
            if existing_inquiry.status == "pending" and not existing_inquiry.chat_room:
                # 如果有待处理的咨询且没有聊天室，检查队列位置
                queue_position = (
                    ShipBaoInquiry.objects.filter(
                        item=item, status="pending", created_at__lt=existing_inquiry.created_at
                    ).count()
                    + 1
                )

                return JsonResponse(
                    {
                        "success": False,
                        "error": f"您已在咨询队列中，当前排队位置: {queue_position}",
                        "queue_info": {
                            "position": queue_position,
                            "estimated_wait": f"预计等待时间: {queue_position * 10}分钟",
                            "inquiry_id": existing_inquiry.id,
                        },
                    }
                )
            elif existing_inquiry.chat_room:
                # 检查聊天室是否仍然有效
                chat_room = existing_inquiry.chat_room
                if chat_room.status == "active":
                    # 聊天室仍然有效，直接返回
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "继续之前的对话",
                            "room_id": chat_room.room_id,
                            "chat_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
                            "redirect_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
                        }
                    )
                else:
                    # 聊天室已过期，标记需要重用这个咨询记录
                    reuse_inquiry = existing_inquiry

        # 创建或重用咨询记录
        try:
            with transaction.atomic():
                # 如果需要重用现有咨询记录（聊天室过期的情况）
                if reuse_inquiry:
                    inquiry = reuse_inquiry
                    inquiry.initial_message = message
                    inquiry.chat_room = None
                    inquiry.status = "pending"
                    inquiry.responded_at = None
                    inquiry.calculate_priority_score()
                    inquiry.save()
                else:
                    # 创建新的咨询记录
                    inquiry = ShipBaoInquiry.objects.create(
                        item=item, buyer=request.user, seller=item.seller, initial_message=message, status="pending"
                    )
                    inquiry.calculate_priority_score()
                    inquiry.save()

                # 获取当前队列位置
                queue_position = (
                    ShipBaoInquiry.objects.filter(item=item, status="pending", created_at__lt=inquiry.created_at).count() + 1
                )

                # 如果队列较短或者是高优先级用户或聊天室过期，立即创建聊天室
                pending_count = ShipBaoInquiry.objects.filter(item=item, status="pending").count()

                should_create_immediately = (
                    reuse_inquiry is not None  # 聊天室过期，直接创建新的
                    or pending_count <= 3  # 队列较短
                    or inquiry.priority_score > 100  # 高优先级用户
                )

                if should_create_immediately:
                    # 查找是否已有活跃的聊天室
                    chat_room = (
                        ChatRoom.objects.filter(
                            Q(user1=request.user, user2=item.seller) | Q(user1=item.seller, user2=request.user)
                        )
                        .filter(room_type="private", status="active")  # 只查找活跃的聊天室
                        .first()
                    )

                    # 如果没有活跃的聊天室，创建一个新的
                    if not chat_room:
                        chat_room = ChatRoom.objects.create(
                            room_id=str(uuid.uuid4()),
                            user1=request.user,
                            user2=item.seller,
                            room_type="private",
                            status="active",
                            name=f"关于商品: {item.title}",
                        )

                    # 更新咨询记录
                    inquiry.chat_room = chat_room
                    inquiry.status = "responded"
                    from django.utils import timezone

                    inquiry.responded_at = timezone.now()
                    inquiry.save()

                    # 确保聊天室状态是活跃的
                    if chat_room.status != "active":
                        chat_room.status = "active"
                        chat_room.save()

                    # 发送初始消息
                    if message:
                        chat_message = ChatMessage.objects.create(
                            room=chat_room, sender=request.user, content=message, message_type="text"
                        )

                        # 创建聊天通知
                        from ..views.notification_views import create_chat_notification

                        create_chat_notification(chat_message)

                    # 增加商品咨询次数
                    item.increment_inquiry_count()

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "已进入聊天室",
                            "room_id": chat_room.room_id,
                            "chat_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
                            "redirect_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
                        }
                    )
                else:
                    # 加入队列，返回队列信息
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "已加入咨询队列",
                            "queue_info": {
                                "position": queue_position,
                                "estimated_wait": f"预计等待时间: {queue_position * 10}分钟",
                                "total_pending": pending_count,
                                "inquiry_id": inquiry.id,
                                "priority_score": inquiry.priority_score,
                            },
                        }
                    )

        except IntegrityError:
            # 并发创建时的重复数据处理
            return JsonResponse({"success": False, "error": "您已经发送过咨询请求，请勿重复提交"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"联系卖家失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
def shipbao_inquiry_queue_api(request, item_id):
    """获取商品咨询队列状态API"""
    try:
        try:
            item = ShipBaoItem.objects.get(id=item_id)
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        from ..models.legacy_models import ShipBaoInquiry

        # 获取用户的咨询状态（仅当用户已登录时）
        user_inquiry = None
        if request.user.is_authenticated:
            user_inquiry = ShipBaoInquiry.objects.filter(item=item, buyer=request.user).first()

        # 获取队列统计
        total_pending = ShipBaoInquiry.objects.filter(item=item, status="pending").count()

        total_responded = ShipBaoInquiry.objects.filter(item=item, status="responded").count()

        queue_info = {"total_pending": total_pending, "total_responded": total_responded, "user_inquiry": None}

        if user_inquiry:
            position = None
            if user_inquiry.status == "pending":
                position = (
                    ShipBaoInquiry.objects.filter(item=item, status="pending", created_at__lt=user_inquiry.created_at).count()
                    + 1
                )

            queue_info["user_inquiry"] = {
                "id": user_inquiry.id,
                "status": user_inquiry.status,
                "created_at": user_inquiry.created_at.isoformat(),
                "position": position,
                "priority_score": user_inquiry.priority_score,
                "estimated_wait": f"{position * 10}分钟" if position else None,
                "chat_room_id": user_inquiry.chat_room.room_id if user_inquiry.chat_room else None,
            }

        return JsonResponse({"success": True, "queue_info": queue_info})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取队列状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_want_item_api(request):
    """想要商品API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        action = data.get("action", "add")  # add 或 remove
        message = data.get("message", "")

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id, status="pending")
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否是自己的商品
        if request.user == item.seller:
            return JsonResponse({"success": False, "error": "不能对自己的商品表示想要"})

        # 检查是否已经想要过
        existing_want = ShipBaoWantItem.objects.filter(user=request.user, item=item).first()

        if action == "add":
            if existing_want:
                return JsonResponse({"success": False, "error": "您已经表示想要此商品"})

            # 创建想要记录
            ShipBaoWantItem.objects.create(user=request.user, item=item, message=message)

            # 更新商品想要数
            item.increment_want_count()

            return JsonResponse({"success": True, "message": "已表示想要", "want_count": item.want_count})

        elif action == "remove":
            if not existing_want:
                return JsonResponse({"success": False, "error": "您尚未表示想要此商品"})

            # 删除想要记录
            existing_want.delete()

            # 更新商品想要数
            item.decrement_want_count()

            return JsonResponse({"success": True, "message": "已取消想要", "want_count": item.want_count})

        else:
            return JsonResponse({"success": False, "error": "无效的操作"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"操作失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def shipbao_want_list_api(request, item_id):
    """获取想要商品的用户列表API - 仅供商品发布者查看"""
    try:
        item = get_object_or_404(ShipBaoItem, id=item_id)

        # 只有商品发布者可以查看
        if request.user != item.seller:
            return JsonResponse({"success": False, "error": "权限不足"})

        want_list = ShipBaoWantItem.objects.filter(item=item).select_related("user").order_by("-created_at")

        users_data = []
        for want in want_list:
            users_data.append(
                {
                    "user_id": want.user.id,
                    "username": want.user.username,
                    "message": want.message,
                    "created_at": want.created_at.isoformat(),
                }
            )

        return JsonResponse({"success": True, "want_list": users_data, "total_count": len(users_data)})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"获取列表失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_contact_wanter_api(request):
    """商家联系想要商品的用户API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        user_id = data.get("user_id")
        message = data.get("message", "")

        if not item_id or not user_id:
            return JsonResponse({"success": False, "error": "缺少必要参数"})

        try:
            item = ShipBaoItem.objects.get(id=item_id)
            from django.contrib.auth.models import User

            target_user = User.objects.get(id=user_id)
        except (ShipBaoItem.DoesNotExist, User.DoesNotExist):
            return JsonResponse({"success": False, "error": "商品或用户不存在"})

        # 检查是否是商品发布者
        if request.user != item.seller:
            return JsonResponse({"success": False, "error": "权限不足"})

        # 使用心动链接聊天系统创建聊天室
        import uuid

        from ..models.chat_models import ChatMessage, ChatRoom

        # 查找是否已有聊天室
        chat_room = (
            ChatRoom.objects.filter(Q(user1=request.user, user2=target_user) | Q(user1=target_user, user2=request.user))
            .filter(room_type="private")
            .first()
        )

        # 如果没有聊天室，创建一个新的
        if not chat_room:
            chat_room = ChatRoom.objects.create(
                room_id=str(uuid.uuid4()),
                user1=request.user,
                user2=target_user,
                room_type="private",
                status="active",
                name=f"关于商品: {item.title}",
            )

        # 发送初始消息
        if message:
            chat_message = ChatMessage.objects.create(
                room=chat_room, sender=request.user, content=message, message_type="text"
            )

            # 创建聊天通知
            from ..views.notification_views import create_chat_notification

            create_chat_notification(chat_message)

        return JsonResponse(
            {
                "success": True,
                "message": "已进入聊天室",
                "room_id": chat_room.room_id,
                "chat_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
                "redirect_url": f"/tools/heart_link/chat/{chat_room.room_id}/",
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"联系用户失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_remove_item_api(request):
    """下架商品API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")
        action = data.get("action", "remove")

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id)
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否是商品发布者
        if request.user != item.seller:
            return JsonResponse({"success": False, "error": "只有商品发布者可以执行此操作"})

        # 检查商品当前状态
        if item.status in ["completed", "cancelled"]:
            return JsonResponse({"success": False, "error": "商品已经处于完成或已取消状态，无法下架"})

        if action == "remove":
            # 下架商品
            item.status = "cancelled"
            item.save()

            return JsonResponse({"success": True, "message": "商品已成功下架", "new_status": "cancelled"})
        else:
            return JsonResponse({"success": False, "error": "无效的操作"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"下架商品失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def shipbao_mark_sold_api(request):
    """标记商品为已售API"""
    try:
        data = json.loads(request.body)
        item_id = data.get("item_id")

        if not item_id:
            return JsonResponse({"success": False, "error": "缺少商品ID"})

        try:
            item = ShipBaoItem.objects.get(id=item_id)
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否是商品发布者
        if request.user != item.seller:
            return JsonResponse({"success": False, "error": "只有商品发布者可以标记为已售"})

        # 检查商品当前状态
        if item.status == "completed":
            return JsonResponse({"success": False, "error": "商品已经标记为已售"})

        if item.status == "cancelled":
            return JsonResponse({"success": False, "error": "已下架的商品无法标记为已售"})

        # 标记为已售
        item.status = "completed"
        item.save()

        return JsonResponse({"success": True, "message": "商品已成功标记为已售", "new_status": "completed"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"标记为已售失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def shipbao_transaction_status_api(request, item_id):
    """检查用户对指定商品的交易状态API"""
    try:
        try:
            item = ShipBaoItem.objects.get(id=item_id)
        except ShipBaoItem.DoesNotExist:
            return JsonResponse({"success": False, "error": "商品不存在"})

        # 检查是否已经发起过交易
        from ..models.legacy_models import ShipBaoTransaction

        existing_transaction = ShipBaoTransaction.objects.filter(
            item=item, buyer=request.user, status__in=["initiated", "negotiating", "confirmed", "completed"]
        ).first()

        if existing_transaction:
            return JsonResponse(
                {
                    "success": True,
                    "has_transaction": True,
                    "transaction_status": existing_transaction.status,
                    "transaction_id": existing_transaction.id,
                }
            )
        else:
            return JsonResponse({"success": True, "has_transaction": False})

    except Exception as e:
        return JsonResponse({"success": False, "error": f"检查交易状态失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def save_user_location_api(request):
    """保存用户位置API"""
    try:
        data = json.loads(request.body)

        # 这里可以选择将位置信息保存到用户模型或单独的位置表中
        # 暂时只返回成功，位置主要保存在localStorage中

        return JsonResponse({"success": True, "message": "位置信息已保存"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"保存位置失败: {str(e)}"})


# ==================== 地图API函数 ====================


@csrf_exempt
@require_http_methods(["POST"])
def map_search_location_api(request):
    """地图位置搜索API"""
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()

        if not query:
            return JsonResponse({"success": False, "error": "请提供搜索关键词"})

        # 使用增强版地图服务搜索
        from ..services.enhanced_map_service import enhanced_map_service

        suggestions = enhanced_map_service.search_address(query, limit=8)

        return JsonResponse({"success": True, "suggestions": suggestions})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"位置搜索失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def map_reverse_geocode_api(request):
    """地图反向地理编码API"""
    try:
        data = json.loads(request.body)
        lat = data.get("lat")
        lon = data.get("lon")

        if lat is None or lon is None:
            return JsonResponse({"success": False, "error": "请提供经纬度坐标"})

        try:
            lat = float(lat)
            lon = float(lon)
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "无效的坐标格式"})

        # 使用增强版地图服务进行反向地理编码
        from ..services.enhanced_map_service import enhanced_map_service

        location_data = enhanced_map_service.reverse_geocode(lat, lon)

        if location_data:
            return JsonResponse(
                {
                    "success": True,
                    "location": {
                        "address": location_data.get("formatted_address", ""),
                        "city": location_data.get("city", ""),
                        "region": location_data.get("district", ""),
                        "province": location_data.get("province", ""),
                        "country": "中国",
                        "lat": lat,
                        "lon": lon,
                    },
                }
            )
        else:
            return JsonResponse({"success": False, "error": "反向地理编码失败"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"反向地理编码失败: {str(e)}"})


@csrf_exempt
@require_http_methods(["POST"])
def map_geocode_api(request):
    """地图地理编码API"""
    try:
        data = json.loads(request.body)
        address = data.get("address", "").strip()

        if not address:
            return JsonResponse({"success": False, "error": "请提供地址信息"})

        # 使用增强版地图服务进行地理编码
        from ..services.enhanced_map_service import enhanced_map_service

        location_data = enhanced_map_service.geocode(address)

        if location_data:
            return JsonResponse(
                {
                    "success": True,
                    "location": {
                        "address": location_data.get("formatted_address", address),
                        "city": location_data.get("city", ""),
                        "region": location_data.get("district", ""),
                        "province": location_data.get("province", ""),
                        "lat": location_data.get("lat"),
                        "lon": location_data.get("lon"),
                    },
                }
            )
        else:
            return JsonResponse({"success": False, "error": "地理编码失败"})

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "无效的JSON数据"})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"地理编码失败: {str(e)}"})
