"""
聊天通知相关视图
"""

import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count

from ..models.chat_models import ChatNotification, ChatRoom, ChatMessage


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_unread_notifications_api(request):
    """获取未读通知API"""
    try:
        # 获取用户的未读通知
        unread_notifications = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).select_related('room', 'message', 'message__sender').order_by('-created_at')
        
        # 按聊天室分组统计未读消息
        unread_rooms = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).values('room__room_id', 'room__name').annotate(
            unread_count=Count('id')
        ).order_by('-unread_count')
        
        # 构建响应数据
        notifications_data = []
        for notification in unread_notifications[:10]:  # 最近10条
            notifications_data.append({
                'id': notification.id,
                'room_id': notification.room.room_id,
                'room_name': notification.room.name,
                'sender_username': notification.message.sender.username,
                'message_preview': notification.message.content[:50] + ('...' if len(notification.message.content) > 50 else ''),
                'message_type': notification.message.message_type,
                'created_at': notification.created_at.isoformat()
            })
        
        rooms_data = []
        for room in unread_rooms:
            rooms_data.append({
                'room_id': room['room__room_id'],
                'room_name': room['room__name'],
                'unread_count': room['unread_count']
            })
        
        total_unread = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'success': True,
            'total_unread': total_unread,
            'notifications': notifications_data,
            'unread_rooms': rooms_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取通知失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def mark_notifications_read_api(request):
    """标记通知为已读API"""
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        notification_ids = data.get('notification_ids', [])
        
        if room_id:
            # 标记整个聊天室的通知为已读
            try:
                room = ChatRoom.objects.get(room_id=room_id)
                notifications = ChatNotification.objects.filter(
                    user=request.user,
                    room=room,
                    is_read=False
                )
                
                for notification in notifications:
                    notification.mark_as_read()
                
                return JsonResponse({
                    'success': True,
                    'message': f'已标记 {notifications.count()} 条通知为已读'
                })
                
            except ChatRoom.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': '聊天室不存在'
                })
        
        elif notification_ids:
            # 标记指定的通知为已读
            notifications = ChatNotification.objects.filter(
                id__in=notification_ids,
                user=request.user,
                is_read=False
            )
            
            for notification in notifications:
                notification.mark_as_read()
            
            return JsonResponse({
                'success': True,
                'message': f'已标记 {notifications.count()} 条通知为已读'
            })
        
        else:
            return JsonResponse({
                'success': False,
                'error': '请提供room_id或notification_ids'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'标记通知失败: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required  
def clear_all_notifications_api(request):
    """清除所有通知API"""
    try:
        # 标记所有未读通知为已读
        notifications = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        )
        
        count = notifications.count()
        for notification in notifications:
            notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'message': f'已清除 {count} 条通知'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'清除通知失败: {str(e)}'
        }, status=500)


def create_chat_notification(message, exclude_sender=True):
    """
    创建聊天通知
    当有新消息时调用此函数
    """
    try:
        room = message.room
        
        # 获取聊天室的所有用户
        room_users = []
        if room.user1:
            room_users.append(room.user1)
        if room.user2:
            room_users.append(room.user2)
        
        # 为除发送者外的用户创建通知
        for user in room_users:
            if exclude_sender and user == message.sender:
                continue
            
            # 检查是否已存在相同的通知（避免重复）
            existing_notification = ChatNotification.objects.filter(
                user=user,
                room=room,
                message=message
            ).first()
            
            if not existing_notification:
                ChatNotification.objects.create(
                    user=user,
                    room=room,
                    message=message
                )
                
    except Exception as e:
        # 记录错误但不影响消息发送
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"创建聊天通知失败: {e}")


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_notification_summary_api(request):
    """获取通知摘要API - 用于右上角显示"""
    try:
        total_unread = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        # 获取最近的一条未读通知
        latest_notification = ChatNotification.objects.filter(
            user=request.user,
            is_read=False
        ).select_related('room', 'message', 'message__sender').first()
        
        latest_data = None
        if latest_notification:
            latest_data = {
                'room_id': latest_notification.room.room_id,
                'room_name': latest_notification.room.name,
                'sender_username': latest_notification.message.sender.username,
                'message_preview': latest_notification.message.content[:30] + ('...' if len(latest_notification.message.content) > 30 else ''),
                'created_at': latest_notification.created_at.isoformat()
            }
        
        return JsonResponse({
            'success': True,
            'total_unread': total_unread,
            'latest_notification': latest_data,
            'has_unread': total_unread > 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'获取通知摘要失败: {str(e)}'
        }, status=500)
