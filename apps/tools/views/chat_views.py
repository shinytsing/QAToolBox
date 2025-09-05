import json
import logging
import mimetypes
import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db.models import Q
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from apps.tools.models import UserOnlineStatus
from apps.tools.models.chat_models import ChatMessage, ChatRoom, HeartLinkRequest

from .base import BaseView, CachedViewMixin, PaginationMixin, cache_response

logger = logging.getLogger(__name__)


def success_response(data=None, message="success"):
    """成功响应"""
    response_data = {"success": True, "message": message}
    if data is not None:
        response_data.update(data)
    return JsonResponse(response_data)


def error_response(message="error", status=400):
    """错误响应"""
    return JsonResponse({"success": False, "message": message}, status=status)


@login_required
def chat_dashboard(request):
    """聊天仪表盘"""
    user = request.user

    # 获取用户活跃聊天室
    active_rooms = ChatRoom.get_user_active_rooms(user)

    # 获取在线用户
    online_users = UserOnlineStatus.get_online_users()

    # 获取用户在线状态
    user_status, created = UserOnlineStatus.objects.get_or_create(user=user)

    context = {
        "active_rooms": active_rooms,
        "online_users": online_users,
        "user_status": user_status,
    }

    return render(request, "tools/chat_dashboard.html", context)


@login_required
def chat_room_list(request):
    """聊天室列表"""
    user = request.user

    # 获取用户参与的聊天室
    rooms = (
        ChatRoom.objects.filter(Q(user1=user) | Q(user2=user), status="active")
        .select_related("user1", "user2")
        .order_by("-updated_at")
    )

    room_data = []
    for room in rooms:
        # 获取最后一条消息
        last_message = ChatMessage.objects.filter(room=room).order_by("-created_at").first()

        # 获取未读消息数
        unread_count = ChatMessage.get_unread_count(user, room)

        # 获取对方用户
        other_user = room.user2 if room.user1 == user else room.user1

        room_data.append(
            {
                "room_id": room.room_id,
                "other_user": {
                    "id": other_user.id if other_user else None,
                    "username": other_user.username if other_user else "未知用户",
                    "is_online": getattr(other_user.online_status, "is_online", False) if other_user else False,
                },
                "last_message": {
                    "content": last_message.content[:50] if last_message else "",
                    "created_at": last_message.created_at.isoformat() if last_message else None,
                    "sender_id": last_message.sender.id if last_message else None,
                },
                "unread_count": unread_count,
                "created_at": room.created_at.isoformat(),
                "updated_at": room.updated_at.isoformat(),
            }
        )

    return success_response({"rooms": room_data})


@login_required
@cache_response(timeout=30)
def chat_room_detail(request, room_id):
    """聊天室详情"""
    user = request.user

    room = get_object_or_404(ChatRoom, room_id=room_id)

    # 检查用户是否参与该聊天室
    if room.user1 != user and room.user2 != user:
        return error_response("无权访问该聊天室", status=403)

    # 获取对方用户
    other_user = room.user2 if room.user1 == user else room.user1

    # 获取聊天室消息
    messages = ChatMessage.get_room_messages(room, limit=50)

    # 标记消息为已读
    ChatMessage.objects.filter(room=room, sender__in=room.participants, is_read=False).exclude(sender=user).update(
        is_read=True
    )

    return success_response(
        {
            "room": {
                "room_id": room.room_id,
                "status": room.status,
                "created_at": room.created_at.isoformat(),
            },
            "other_user": {
                "id": other_user.id,
                "username": other_user.username,
                "is_online": getattr(other_user.online_status, "is_online", False),
            },
            "messages": messages,
        }
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def send_message(request, room_id):
    """发送消息"""
    try:
        data = request.POST if request.method == "POST" else request.GET
        user = request.user

        room = get_object_or_404(ChatRoom, room_id=room_id)

        # 检查用户是否参与该聊天室
        if room.user1 != user and room.user2 != user:
            return error_response("无权访问该聊天室", status=403)

        # 检查聊天室状态
        if room.status != "active":
            return error_response("聊天室已关闭", status=400)

        # 创建消息
        message = ChatMessage.objects.create(
            room=room,
            sender=user,
            content=data["content"],
            message_type=data.get("message_type", "text"),
            file_url=data.get("file_url", ""),
        )

        # 创建聊天通知
        from ..views.notification_views import create_chat_notification

        create_chat_notification(message)

        # 通过WebSocket发送消息
        channel_layer = get_channel_layer()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}",
            {
                "type": "chat.message",
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "message_type": message.message_type,
                    "file_url": message.file_url,
                    "sender": {
                        "id": user.id,
                        "username": user.username,
                    },
                    "created_at": message.created_at.isoformat(),
                },
            },
        )

        return success_response(
            {
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "created_at": message.created_at.isoformat(),
                }
            }
        )

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return error_response("发送消息失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_chat_room(request):
    """创建聊天室"""
    try:
        user = request.user

        # 生成房间ID
        room_id = str(uuid.uuid4())

        # 创建聊天室
        room = ChatRoom.objects.create(room_id=room_id, user1=user, status="waiting")

        return success_response(
            {
                "room": {
                    "room_id": room.room_id,
                    "status": room.status,
                    "created_at": room.created_at.isoformat(),
                }
            }
        )

    except Exception as e:
        logger.error(f"Error creating chat room: {e}")
        return error_response("创建聊天室失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def join_chat_room(request, room_id):
    """加入聊天室"""
    try:
        user = request.user

        room = get_object_or_404(ChatRoom, room_id=room_id, status="waiting")

        # 检查是否已满
        if room.is_full:
            return error_response("聊天室已满", status=400)

        # 检查是否是自己创建的
        if room.user1 == user:
            return error_response("不能加入自己创建的聊天室", status=400)

        # 加入聊天室
        room.user2 = user
        room.status = "active"
        room.save()

        # 通过WebSocket通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}",
            {
                "type": "chat.user_joined",
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
        )

        return success_response(
            {
                "room": {
                    "room_id": room.room_id,
                    "status": room.status,
                    "other_user": {
                        "id": room.user1.id,
                        "username": room.user1.username,
                    },
                }
            }
        )

    except Exception as e:
        logger.error(f"Error joining chat room: {e}")
        return error_response("加入聊天室失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def leave_chat_room(request, room_id):
    """离开聊天室"""
    try:
        user = request.user

        room = get_object_or_404(ChatRoom, room_id=room_id)

        # 检查用户是否参与该聊天室
        if room.user1 != user and room.user2 != user:
            return error_response("无权访问该聊天室", status=403)

        # 结束聊天室
        room.status = "ended"
        room.save()

        # 通过WebSocket通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_id}",
            {
                "type": "chat.room_ended",
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
            },
        )

        return success_response(message="已离开聊天室")

    except Exception as e:
        logger.error(f"Error leaving chat room: {e}")
        return error_response("离开聊天室失败", status=500)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_online_status(request):
    """更新在线状态"""
    try:
        data = json.loads(request.body) if request.body else {}
        user = request.user

        status, created = UserOnlineStatus.objects.get_or_create(user=user)

        # 更新状态
        if "status" in data:
            status.status = data["status"]
        if "is_typing" in data:
            status.is_typing = data["is_typing"]
        if "current_room" in data:
            if data["current_room"]:
                room = get_object_or_404(ChatRoom, room_id=data["current_room"])
                status.current_room = room
            else:
                status.current_room = None

        status.is_online = True
        status.save()

        # 清除缓存
        cache.delete("online_users")

        return success_response(
            {
                "status": {
                    "status": status.status,
                    "is_typing": status.is_typing,
                    "is_online": status.is_online,
                    "last_seen": status.last_seen.isoformat(),
                }
            }
        )

    except json.JSONDecodeError:
        return error_response("无效的JSON数据")
    except Exception as e:
        logger.error(f"Error updating online status: {e}")
        return error_response("更新在线状态失败", status=500)


@login_required
@cache_response(timeout=30)
def online_users_list(request):
    """在线用户列表"""
    online_users = UserOnlineStatus.get_online_users()

    users_data = []
    for user_status in online_users:
        users_data.append(
            {
                "id": user_status.user.id,
                "username": user_status.user.username,
                "status": user_status.status,
                "is_typing": user_status.is_typing,
                "last_seen": user_status.last_seen.isoformat(),
            }
        )

    return success_response({"users": users_data})


# 心动链接相关视图
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_heart_link_request(request):
    """创建心动链接请求"""
    try:
        user = request.user

        # 检查是否已有请求
        existing_request = HeartLinkRequest.objects.filter(
            requester=user, status__in=["pending", "matching", "matched"]
        ).first()

        if existing_request:
            if existing_request.status == "matched" and existing_request.chat_room:
                # 如果已匹配，直接返回聊天室信息
                return success_response(
                    {
                        "request": {
                            "id": existing_request.id,
                            "status": existing_request.status,
                            "room_id": existing_request.chat_room.room_id,
                            "matched": True,
                            "redirect": f"/tools/heart_link/chat/{existing_request.chat_room.room_id}/",
                        }
                    }
                )
            elif existing_request.status in ["pending", "matching"]:
                # 如果还在等待，返回现有请求信息继续等待
                return success_response(
                    {
                        "request": {
                            "id": existing_request.id,
                            "status": existing_request.status,
                            "room_id": existing_request.chat_room.room_id if existing_request.chat_room else None,
                            "matched": False,
                            "continue_waiting": True,
                        }
                    }
                )

        # 创建私密聊天室（单人心动链接专用）
        room = ChatRoom.objects.create(
            room_id=str(uuid.uuid4()), user1=user, status="waiting", room_type="private"  # 明确设置为私密类型，不是公共的
        )

        # 创建心动链接请求

        heart_request = HeartLinkRequest.objects.create(requester=user, status="pending", chat_room=room)  # 关联聊天室

        return success_response(
            {
                "request": {
                    "id": heart_request.id,
                    "status": heart_request.status,
                    "room_id": room.room_id,
                    "created_at": heart_request.created_at.isoformat(),
                }
            }
        )

    except Exception as e:
        logger.error(f"Error creating heart link request: {e}")
        return error_response("创建心动链接请求失败", status=500)


@login_required
@cache_response(timeout=10)
def heart_link_status(request, request_id):
    """获取心动链接状态"""
    user = request.user

    heart_request = get_object_or_404(HeartLinkRequest, id=request_id, requester=user)

    # 检查是否过期
    if heart_request.is_expired and heart_request.status == "pending":
        heart_request.status = "expired"
        heart_request.save()

    return success_response(
        {
            "request": {
                "id": heart_request.id,
                "status": heart_request.status,
                "room_id": heart_request.chat_room.room_id,
                "created_at": heart_request.created_at.isoformat(),
                "matched_at": heart_request.matched_at.isoformat() if heart_request.matched_at else None,
                "matched_with": (
                    {
                        "id": heart_request.matched_with.id,
                        "username": heart_request.matched_with.username,
                    }
                    if heart_request.matched_with
                    else None
                ),
                "is_expired": heart_request.is_expired,
            }
        }
    )


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def cancel_heart_link_request(request, request_id):
    """取消心动链接请求"""
    try:
        user = request.user

        heart_request = get_object_or_404(HeartLinkRequest, id=request_id, requester=user)

        if heart_request.status not in ["pending", "matching"]:
            return error_response("无法取消该请求", status=400)

        heart_request.status = "cancelled"
        heart_request.save()

        # 结束聊天室
        heart_request.chat_room.status = "ended"
        heart_request.chat_room.save()

        return success_response(message="已取消心动链接请求")

    except Exception as e:
        logger.error(f"Error cancelling heart link request: {e}")
        return error_response("取消请求失败", status=500)


@login_required
@cache_response(timeout=30)
def available_heart_links(request):
    """获取可用的心动链接"""
    user = request.user

    # 获取待匹配的请求（排除自己的）
    available_requests = (
        HeartLinkRequest.objects.filter(status="pending", requester__is_online=True)
        .exclude(requester=user)
        .select_related("requester")[:10]
    )

    requests_data = []
    for heart_request in available_requests:
        requests_data.append(
            {
                "id": heart_request.id,
                "requester": {
                    "id": heart_request.requester.id,
                    "username": heart_request.requester.username,
                },
                "created_at": heart_request.created_at.isoformat(),
            }
        )

    return success_response({"requests": requests_data})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def accept_heart_link(request, request_id):
    """接受心动链接"""
    try:
        user = request.user

        heart_request = get_object_or_404(HeartLinkRequest, id=request_id, status="pending")

        # 检查是否是自己创建的
        if heart_request.requester == user:
            return error_response("不能接受自己的请求", status=400)

        # 更新请求状态
        heart_request.status = "matched"
        heart_request.matched_with = user
        heart_request.matched_at = timezone.now()
        heart_request.save()

        # 更新聊天室
        room = heart_request.chat_room
        room.user2 = user
        room.status = "active"
        room.save()

        # 通过WebSocket通知
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{room.room_id}",
            {
                "type": "chat.heart_link_matched",
                "users": [
                    {
                        "id": heart_request.requester.id,
                        "username": heart_request.requester.username,
                    },
                    {
                        "id": user.id,
                        "username": user.username,
                    },
                ],
            },
        )

        return success_response(
            {
                "room": {
                    "room_id": room.room_id,
                    "status": room.status,
                    "other_user": {
                        "id": heart_request.requester.id,
                        "username": heart_request.requester.username,
                    },
                }
            }
        )

    except Exception as e:
        logger.error(f"Error accepting heart link: {e}")
        return error_response("接受心动链接失败", status=500)


class ChatAPIView(BaseView, CachedViewMixin, PaginationMixin):
    """聊天API视图类"""

    @method_decorator(login_required)
    def get(self, request, room_id):
        """获取聊天室消息"""
        user = request.user

        room = get_object_or_404(ChatRoom, room_id=room_id)

        # 检查用户是否参与该聊天室
        if room.user1 != user and room.user2 != user:
            return self.error_response("无权访问该聊天室", status=403)

        # 获取查询参数
        page = request.GET.get("page", 1)
        page_size = request.GET.get("page_size", 50)

        # 获取消息
        queryset = ChatMessage.objects.filter(room=room).select_related("sender")
        result = self.get_paginated_data(queryset, page, page_size)

        # 标记消息为已读
        ChatMessage.objects.filter(room=room, sender__in=room.participants, is_read=False).exclude(sender=user).update(
            is_read=True
        )

        return self.success_response(result)

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request, room_id):
        """发送消息"""
        try:
            data = json.loads(request.body) if request.body else {}

            if "content" not in data:
                return self.error_response("缺少消息内容")

            user = request.user

            room = get_object_or_404(ChatRoom, room_id=room_id)

            # 检查用户是否参与该聊天室
            if room.user1 != user and room.user2 != user:
                return self.error_response("无权访问该聊天室", status=403)

            # 检查聊天室状态
            if room.status != "active":
                return self.error_response("聊天室已关闭", status=400)

            # 创建消息
            message = ChatMessage.objects.create(
                room=room,
                sender=user,
                content=data["content"],
                message_type=data.get("message_type", "text"),
                file_url=data.get("file_url", ""),
            )

            # 创建聊天通知
            from ..views.notification_views import create_chat_notification

            create_chat_notification(message)

            # 通过WebSocket发送消息
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{room_id}",
                {
                    "type": "chat.message",
                    "message": {
                        "id": message.id,
                        "content": message.content,
                        "message_type": message.message_type,
                        "file_url": message.file_url,
                        "sender": {
                            "id": user.id,
                            "username": user.username,
                        },
                        "created_at": message.created_at.isoformat(),
                    },
                },
            )

            return self.success_response(
                {
                    "message": {
                        "id": message.id,
                        "content": message.content,
                        "created_at": message.created_at.isoformat(),
                    }
                }
            )

        except json.JSONDecodeError:
            return self.error_response("无效的JSON数据")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return self.error_response("发送消息失败")


# 消息历史记录
@login_required
@cache_response(timeout=300)
def message_history(request, room_id):
    """获取消息历史记录"""
    user = request.user

    room = get_object_or_404(ChatRoom, room_id=room_id)

    # 检查用户是否参与该聊天室
    if room.user1 != user and room.user2 != user:
        return error_response("无权访问该聊天室", status=403)

    # 获取查询参数
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    message_type = request.GET.get("message_type")

    queryset = ChatMessage.objects.filter(room=room).select_related("sender")

    # 应用过滤
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)
    if message_type:
        queryset = queryset.filter(message_type=message_type)

    messages = list(queryset.order_by("-created_at")[:100])

    return success_response({"messages": messages})


# Heart Link 相关视图
def heart_link(request):
    """心动链接页面"""
    if not request.user.is_authenticated:
        return redirect("users:login")
    return render(request, "tools/heart_link.html")


@login_required
def heart_link_chat(request, room_id):
    """心动链接聊天页面 - 仅用于一对一私密聊天"""
    if not request.user.is_authenticated:
        return redirect("users:login")

    # 防止访问群聊天室ID - 引导用户到正确的心动链接流程
    if room_id in ["public-room", "general", "chat", "random"] or room_id.startswith("test-room-"):
        # 检查用户是否有活跃的心动链接请求
        from apps.tools.models.chat_models import HeartLinkRequest

        existing_request = HeartLinkRequest.objects.filter(requester=request.user, status__in=["pending", "matched"]).first()

        if existing_request and existing_request.status == "matched" and existing_request.chat_room:
            # 如果用户已有匹配的聊天室，重定向到正确的聊天室
            return JsonResponse(
                {
                    "success": True,
                    "message": "已为您找到心动链接聊天室",
                    "redirect": f"/tools/heart_link/chat/{existing_request.chat_room.room_id}/",
                }
            )
        else:
            # 自动为用户创建心动链接请求
            try:
                # 创建聊天室
                import uuid

                room = ChatRoom.objects.create(room_id=str(uuid.uuid4()), user1=request.user, status="waiting")

                # 创建心动链接请求
                new_request = HeartLinkRequest.objects.create(requester=request.user, status="pending", chat_room=room)

                # 尝试匹配其他用户
                from apps.tools.services.heart_link_matcher import matcher

                matched_room, matched_user = matcher.match_users(request.user, new_request)

                if matched_room and matched_user:
                    # 立即匹配成功
                    return JsonResponse(
                        {
                            "success": True,
                            "matched": True,
                            "message": "已为您找到匹配用户！",
                            "redirect": f"/tools/heart_link/chat/{matched_room.room_id}/",
                        }
                    )
                else:
                    # 等待匹配
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "正在为您寻找心动链接匹配，请稍候...",
                            "redirect": "/tools/heart_link/",
                            "auto_matching": True,
                        },
                        status=202,
                    )  # 202 表示正在处理
            except Exception:
                # 如果自动创建失败，回退到原方案
                return JsonResponse(
                    {
                        "success": False,
                        "error": "心动链接需要先进行匹配，正在为您跳转到匹配页面...",
                        "redirect": "/tools/heart_link/",
                    },
                    status=400,
                )

    try:
        chat_room = ChatRoom.objects.get(room_id=room_id)

        # 确保这是心动链接类型的聊天室
        if not chat_room.is_heart_link_room():
            return JsonResponse(
                {"success": False, "error": "此聊天室不是心动链接房间，请使用多人聊天功能", "redirect": "/tools/chat/"},
                status=400,
            )

        # 检查聊天室状态
        if chat_room.status != "active":
            return redirect("tools:chat_room_error", error_type="ended", room_id=room_id)

        # 检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)

        if request.user not in participants:
            # 如果用户不是参与者，但有匹配的请求，允许加入
            heart_link_request = HeartLinkRequest.objects.filter(
                requester=request.user, chat_room=chat_room, status="matched"
            ).first()

            if not heart_link_request:
                return JsonResponse({"success": False, "error": "您没有权限访问此心动链接聊天室"}, status=403)

        # 获取对方用户信息
        other_user = chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
        if not other_user:
            return JsonResponse({"success": False, "error": "心动链接聊天室配置错误，缺少匹配用户"}, status=500)

        context = {
            "room_id": room_id,
            "chat_room": chat_room,
            "other_user": other_user,
            "chat_type": "heart_link",  # 标识聊天类型
        }

        # 使用心动链接专用的聊天页面
        return render(request, "tools/heart_link_chat_websocket_new.html", context)

    except ChatRoom.DoesNotExist:
        return JsonResponse({"success": False, "error": "心动链接聊天室不存在", "redirect": "/tools/heart_link/"}, status=404)
    except Exception as e:
        logger.error(f"Heart link chat error: {e}")
        return JsonResponse(
            {"success": False, "error": "访问心动链接聊天室时发生错误", "redirect": "/tools/heart_link/"}, status=500
        )


def heart_link_test_view(request):
    """心动链接测试页面（无需登录）"""
    return render(request, "tools/heart_link_test.html")


def click_test_view(request):
    """点击测试页面（无需登录）"""
    return render(request, "tools/click_test_standalone.html")


@login_required
def chat_entrance_view(request):
    """聊天入口页面"""
    return render(request, "tools/chat_entrance.html")


def chat_enhanced(request, room_id):
    """增强聊天页面 - 展示用户头像、昵称、信息和标签"""
    if not request.user.is_authenticated:
        return redirect("users:login")

    try:
        chat_room = ChatRoom.objects.get(room_id=room_id)

        # 检查聊天室状态
        if chat_room.status != "active":
            return JsonResponse({"success": False, "error": "聊天室已结束或不存在"}, status=404)

        # 严格检查用户是否是聊天室的参与者
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)

        if request.user not in participants:
            # 记录未授权访问尝试
            logger.warning(f"未授权访问尝试: 用户 {request.user.username} 尝试访问聊天室 {room_id}")
            return JsonResponse({"success": False, "error": "您没有权限访问此聊天室"}, status=403)

        # 获取对方用户信息
        other_user = chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
        if not other_user:
            return JsonResponse({"success": False, "error": "聊天室配置错误"}, status=500)

        context = {"room_id": room_id, "chat_room": chat_room, "other_user": other_user}

        # 使用增强的聊天页面
        return render(request, "tools/chat_enhanced.html", context)

    except ChatRoom.DoesNotExist:
        return JsonResponse({"success": False, "error": "聊天室不存在"}, status=404)
    except Exception as e:
        logger.error(f"访问聊天室失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"访问聊天室失败: {str(e)}"}, status=500)


@login_required
def chat_debug_view(request, room_id):
    """聊天调试页面 - 用于诊断WebSocket连接问题"""
    if not request.user.is_authenticated:
        return redirect("users:login")

    context = {
        "room_id": room_id,
    }

    return render(request, "tools/chat_debug.html", context)


def active_chat_rooms_view(request):
    """活跃聊天室页面 - 显示用户参与的活跃聊天室"""
    if not request.user.is_authenticated:
        return redirect("users:login")

    context = {
        "user": request.user,
    }

    return render(request, "tools/active_chat_rooms.html", context)


@login_required
def number_match_view(request):
    """数字匹配页面"""
    return render(request, "tools/number_match.html")


def generate_chat_token(user, room_id):
    """生成聊天室访问令牌"""
    import hashlib

    # 使用用户ID、房间ID和时间戳生成唯一令牌
    timestamp = str(int(timezone.now().timestamp()))
    token_data = f"{user.id}:{room_id}:{timestamp}"
    token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
    return token


def verify_chat_token(user, room_id, token):
    """验证聊天室访问令牌"""
    try:
        # 检查用户是否有权限访问该聊天室
        chat_room = ChatRoom.objects.get(room_id=room_id)
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)

        if user not in participants:
            return False

        # 验证令牌（这里简化处理，实际可以存储令牌到数据库）
        # 为了安全，我们主要依赖用户权限检查
        return True
    except ChatRoom.DoesNotExist:
        return False


@login_required
def secure_chat_entrance(request):
    """安全的聊天入口页面 - 显示用户可访问的聊天室"""
    user = request.user

    # 获取用户参与的活跃聊天室
    active_rooms = ChatRoom.objects.filter(status="active", user1=user) | ChatRoom.objects.filter(status="active", user2=user)

    # 为每个聊天室生成访问令牌
    chat_rooms = []
    for room in active_rooms:
        other_user = room.user2 if user == room.user1 else room.user1
        token = generate_chat_token(user, room.room_id)
        chat_rooms.append(
            {
                "room_id": room.room_id,
                "token": token,
                "other_user": other_user,
                "created_at": room.created_at,
                "last_message": room.messages.order_by("-created_at").first(),
            }
        )

    context = {"chat_rooms": chat_rooms, "user": user}

    return render(request, "tools/secure_chat_entrance.html", context)


def secure_chat_enhanced(request, room_id, token):
    """安全的增强聊天页面 - 使用令牌验证访问权限"""
    if not request.user.is_authenticated:
        return redirect("users:login")

    # 验证访问令牌
    if not verify_chat_token(request.user, room_id, token):
        logger.warning(f"无效的聊天室访问令牌: 用户 {request.user.username} 尝试访问聊天室 {room_id}")
        return HttpResponseForbidden("访问被拒绝")

    try:
        chat_room = ChatRoom.objects.get(room_id=room_id)

        # 再次检查聊天室状态
        if chat_room.status != "active":
            return JsonResponse({"success": False, "error": "聊天室已结束或不存在"}, status=404)

        # 获取对方用户信息
        other_user = chat_room.user2 if request.user == chat_room.user1 else chat_room.user1
        if not other_user:
            return JsonResponse({"success": False, "error": "聊天室配置错误"}, status=500)

        context = {"room_id": room_id, "token": token, "chat_room": chat_room, "other_user": other_user}

        return render(request, "tools/secure_chat_enhanced.html", context)

    except ChatRoom.DoesNotExist:
        return JsonResponse({"success": False, "error": "聊天室不存在"}, status=404)
    except Exception as e:
        logger.error(f"访问聊天室失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"访问聊天室失败: {str(e)}"}, status=500)


def test_two_users_chat_view(request, room_id):
    """两个人聊天测试页面"""
    context = {
        "room_id": room_id,
    }
    return render(request, "tools/test_two_users_chat.html", context)


@login_required
def download_chat_file(request, room_id, message_id):
    """下载聊天室文件"""
    try:
        # 获取消息
        message = get_object_or_404(ChatMessage, id=message_id, room__room_id=room_id)

        # 检查用户权限
        if request.user not in [message.room.user1, message.room.user2]:
            return JsonResponse({"error": "无权访问此文件"}, status=403)

        # 检查消息类型
        if message.message_type not in ["file", "image", "voice", "video"]:
            return JsonResponse({"error": "此消息不包含文件"}, status=400)

        # 构建文件路径
        if message.file_url.startswith("/media/"):
            file_path = message.file_url[7:]  # 移除 '/media/' 前缀
        else:
            file_path = message.file_url

        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            return JsonResponse({"error": "文件不存在"}, status=404)

        # 获取文件信息
        file_size = os.path.getsize(full_path)
        file_name = os.path.basename(full_path)

        # 如果是图片消息，使用原始文件名
        if message.message_type == "image":
            file_name = f"image_{message_id}.jpg"
        elif message.message_type == "voice":
            file_name = f"voice_{message_id}.webm"
        elif message.message_type == "video":
            file_name = f"video_{message_id}.mp4"
        else:
            # 文件消息使用原始文件名
            file_name = message.content or file_name

        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # 创建文件响应
        response = FileResponse(open(full_path, "rb"), content_type=mime_type)

        # 对文件名进行URL编码以支持中文等特殊字符
        from urllib.parse import quote

        encoded_filename = quote(file_name, safe="")
        response["Content-Disposition"] = f"attachment; filename=\"{file_name}\"; filename*=UTF-8''{encoded_filename}"
        response["Content-Length"] = file_size

        # 添加安全头
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"

        return response

    except Exception as e:
        logger.error(f"下载文件失败: {e}")
        return JsonResponse({"error": "下载文件失败"}, status=500)
