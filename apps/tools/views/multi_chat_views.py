# 多人聊天室视图
import logging
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.tools.models.chat_models import ChatMessage, ChatRoom

logger = logging.getLogger(__name__)


@login_required
def multi_chat_room(request, room_id):
    """多人聊天室页面 - 自动创建或加入聊天室"""
    try:
        # 尝试获取现有聊天室
        try:
            chat_room = ChatRoom.objects.get(room_id=room_id)
            # 防止访问心动链接聊天室
            if chat_room.is_heart_link_room():
                return JsonResponse(
                    {
                        "success": False,
                        "error": "此房间是心动链接私密聊天室，请使用心动链接功能访问",
                        "redirect": "/tools/heart_link/",
                    },
                    status=400,
                )
        except ChatRoom.DoesNotExist:
            # 如果聊天室不存在，创建新的多人聊天室
            chat_room = ChatRoom.objects.create(
                room_id=room_id,
                user1=request.user,
                status="active",  # 多人聊天室直接设为活跃状态
                room_type="group",  # 明确标记为群聊
            )

        # 检查聊天室状态
        if chat_room.status != "active":
            # 重新激活聊天室
            chat_room.status = "active"
            chat_room.save()

        # 对于多人聊天室，允许任何用户加入
        participants = [chat_room.user1]
        if chat_room.user2:
            participants.append(chat_room.user2)

        # 如果用户不在参与者列表中且没有第二个用户，将其设为第二个用户
        if request.user not in participants and not chat_room.user2:
            chat_room.user2 = request.user
            chat_room.save()
            participants.append(request.user)

        # 获取其他参与者（如果有的话）
        other_users = []
        for participant in participants:
            if participant != request.user and participant:
                other_users.append(participant)

        # 获取聊天室最近的消息
        recent_messages = ChatMessage.objects.filter(room=chat_room).select_related("sender").order_by("-created_at")[:50]

        context = {
            "room_id": room_id,
            "chat_room": chat_room,
            "other_user": other_users[0] if other_users else None,  # 为了兼容现有模板
            "other_users": other_users,  # 所有其他用户
            "is_multi_user_room": True,
            "participants": participants,
            "recent_messages": recent_messages[::-1],  # 反转顺序显示最旧的在前
            "room_name": room_id.replace("-", " ").title(),  # 格式化房间名称
        }

        return render(request, "tools/multi_chat_room.html", context)

    except Exception as e:
        logger.error(f"访问多人聊天室失败: {str(e)}")
        return JsonResponse({"success": False, "error": f"访问聊天室失败: {str(e)}"}, status=500)


@login_required
def create_chat_room(request):
    """创建新的聊天室"""
    if request.method == "POST":
        room_name = request.POST.get("room_name", "").strip()

        if not room_name:
            return JsonResponse({"success": False, "error": "房间名称不能为空"}, status=400)

        # 生成房间ID（使用房间名称，替换空格为连字符）
        room_id = room_name.lower().replace(" ", "-").replace("_", "-")

        # 如果房间已存在，直接跳转
        if ChatRoom.objects.filter(room_id=room_id).exists():
            return JsonResponse({"success": True, "room_id": room_id, "message": "加入现有聊天室"})

        # 创建新聊天室
        chat_room = ChatRoom.objects.create(room_id=room_id, user1=request.user, status="active")

        return JsonResponse({"success": True, "room_id": room_id, "message": "聊天室创建成功"})

    return JsonResponse({"success": False, "error": "只支持POST请求"}, status=405)


@login_required
def list_active_rooms(request):
    """获取活跃的聊天室列表"""
    active_rooms = ChatRoom.objects.filter(status="active").select_related("user1", "user2").order_by("-updated_at")[:20]

    rooms_data = []
    for room in active_rooms:
        # 获取最后一条消息
        last_message = ChatMessage.objects.filter(room=room).order_by("-created_at").first()

        # 获取参与者数量
        participants_count = 1  # user1
        if room.user2:
            participants_count += 1

        rooms_data.append(
            {
                "room_id": room.room_id,
                "room_name": room.room_id.replace("-", " ").title(),
                "participants_count": participants_count,
                "last_message": {
                    "content": last_message.content[:50] if last_message else "",
                    "created_at": last_message.created_at.isoformat() if last_message else None,
                    "sender": last_message.sender.username if last_message else None,
                },
                "created_at": room.created_at.isoformat(),
                "updated_at": room.updated_at.isoformat(),
            }
        )

    return JsonResponse({"success": True, "rooms": rooms_data})
