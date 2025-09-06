import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import ChatRoom, ChatMessage, UserConnection
from .serializers import ChatMessageSerializer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # 验证用户身份
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            await self.close()
            return
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 记录用户连接
        await self.save_user_connection(user, True)
        
        await self.accept()
        
        # 发送在线用户列表
        await self.send_online_users()

    async def disconnect(self, close_code):
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # 记录用户断开连接
        user = await self.get_user_from_token()
        if user and not user.is_anonymous:
            await self.save_user_connection(user, False)
            await self.send_online_users()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
            elif message_type == 'user_join':
                await self.handle_user_join(text_data_json)
            elif message_type == 'user_leave':
                await self.handle_user_leave(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def handle_chat_message(self, data):
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            return
        
        message_text = data.get('message', '').strip()
        if not message_text:
            return
        
        # 保存消息到数据库
        message = await self.save_message(user, message_text)
        
        # 发送消息到房间组
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'avatar': user.avatar.url if user.avatar else None
                    },
                    'message': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'message_type': message.message_type
                }
            }
        )

    async def handle_typing(self, data):
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            return
        
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing',
                'user': {
                    'id': user.id,
                    'username': user.username
                },
                'is_typing': is_typing
            }
        )

    async def handle_user_join(self, data):
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'avatar': user.avatar.url if user.avatar else None
                }
            }
        )

    async def handle_user_leave(self, data):
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            return
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'data': event['message']
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'data': event
        }))

    async def user_join(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_join',
            'data': event['user']
        }))

    async def user_leave(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'data': event['user']
        }))

    async def send_online_users(self):
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'data': online_users
        }))

    @database_sync_to_async
    def get_user_from_token(self):
        try:
            # 从查询参数或头部获取token
            token = self.scope.get('query_string', b'').decode().split('token=')[-1]
            if not token:
                return AnonymousUser()
            
            # 验证token
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, KeyError, Exception):
            return AnonymousUser()

    @database_sync_to_async
    def save_message(self, user, content):
        room = ChatRoom.objects.get(name=self.room_name)
        message = ChatMessage.objects.create(
            room=room,
            user=user,
            content=content,
            message_type='text'
        )
        return message

    @database_sync_to_async
    def save_user_connection(self, user, is_connected):
        UserConnection.objects.update_or_create(
            user=user,
            room_name=self.room_name,
            defaults={'is_connected': is_connected}
        )

    @database_sync_to_async
    def get_online_users(self):
        connections = UserConnection.objects.filter(
            room_name=self.room_name,
            is_connected=True
        ).select_related('user')
        
        return [
            {
                'id': conn.user.id,
                'username': conn.user.username,
                'avatar': conn.user.avatar.url if conn.user.avatar else None
            }
            for conn in connections
        ]


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = await self.get_user_from_token()
        if not user or user.is_anonymous:
            await self.close()
            return
        
        self.user_id = user.id
        self.notification_group_name = f'notifications_{self.user_id}'
        
        # 加入用户通知组
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_read':
                await self.handle_mark_read(text_data_json)
            elif message_type == 'get_notifications':
                await self.handle_get_notifications(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def handle_mark_read(self, data):
        notification_id = data.get('notification_id')
        if notification_id:
            await self.mark_notification_read(notification_id)

    async def handle_get_notifications(self, data):
        notifications = await self.get_user_notifications()
        await self.send(text_data=json.dumps({
            'type': 'notifications',
            'data': notifications
        }))

    async def notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_user_from_token(self):
        try:
            token = self.scope.get('query_string', b'').decode().split('token=')[-1]
            if not token:
                return AnonymousUser()
            
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            from django.contrib.auth import get_user_model
            User = get_user_model()
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, KeyError, Exception):
            return AnonymousUser()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        from .models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.is_read = True
            notification.save()
        except Notification.DoesNotExist:
            pass

    @database_sync_to_async
    def get_user_notifications(self):
        from .models import Notification
        notifications = Notification.objects.filter(
            user_id=self.user_id
        ).order_by('-created_at')[:50]
        
        return [
            {
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'is_read': notif.is_read,
                'created_at': notif.created_at.isoformat()
            }
            for notif in notifications
        ]
