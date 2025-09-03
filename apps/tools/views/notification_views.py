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
        # 确保ChatNotification表存在
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tools_chatnotification')")
            table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return JsonResponse({
                'success': True,
                'total_unread': 0,
                'notifications': [],
                'unread_rooms': []
            })
        
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
        # 确保ChatNotification表存在
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tools_chatnotification')")
            table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            return JsonResponse({
                'success': True,
                'message': '已清除 0 条通知'
            })
        
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
        # 添加调试信息
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"获取通知摘要 - 用户: {request.user.username}")
        
        # 获取聊天通知
        try:
            unread_notifications = ChatNotification.objects.filter(
                user=request.user,
                is_read=False
            ).select_related('room', 'message', 'message__sender').order_by('-created_at')
            
            total_unread = unread_notifications.count()
            latest_notification = None
            
            if unread_notifications.exists():
                latest = unread_notifications.first()
                latest_notification = {
                    'id': latest.id,
                    'room_id': latest.room.room_id,
                    'room_name': latest.room.name,
                    'sender_username': latest.message.sender.username,
                    'message_preview': latest.message.content[:50] + ('...' if len(latest.message.content) > 50 else ''),
                    'created_at': latest.created_at.isoformat()
                }
            
            response_data = {
                'success': True,
                'total_unread': total_unread,
                'latest_notification': latest_notification,
                'has_unread': total_unread > 0,
                'user': request.user.username,
                'timestamp': str(timezone.now())
            }
        except Exception as db_error:
            # 如果数据库查询失败，返回空通知
            logger.warning(f"数据库查询失败，返回空通知: {db_error}")
            response_data = {
                'success': True,
                'total_unread': 0,
                'latest_notification': None,
                'has_unread': False,
                'user': request.user.username,
                'timestamp': str(timezone.now()),
                'note': 'Database query failed, returning empty notifications'
            }
        
        logger.info(f"通知摘要响应: {response_data}")
        return JsonResponse(response_data)
        
    except Exception as e:
        import traceback
        error_msg = f'获取通知摘要失败: {str(e)}'
        print(f"通知摘要API错误: {error_msg}")
        print(traceback.format_exc())
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_system_notification_api(request):
    """创建系统通知API"""
    try:
        data = json.loads(request.body)
        title = data.get('title', '系统通知')
        message = data.get('message', '')
        notification_type = data.get('type', 'system')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': '通知消息不能为空'
            })
        
        # 创建系统聊天室（如果不存在）
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(username='admin').first()
        if not admin_user:
            admin_user = request.user
        
        system_room, created = ChatRoom.objects.get_or_create(
            name='系统通知',
            defaults={
                'description': '系统任务完成通知',
                'is_public': False,
                'created_by': admin_user
            }
        )
        
        # 创建系统消息
        system_message = ChatMessage.objects.create(
            room=system_room,
            sender=admin_user,
            content=f"**{title}**\n\n{message}",
            message_type='system'
        )
        
        # 为当前用户创建通知
        ChatNotification.objects.create(
            user=request.user,
            room=system_room,
            message=system_message
        )
        
        return JsonResponse({
            'success': True,
            'message': '系统通知已创建',
            'notification_id': system_message.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '无效的JSON数据'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'创建系统通知失败: {str(e)}'
        }, status=500)
