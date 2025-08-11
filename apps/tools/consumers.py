import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import ChatRoom, ChatMessage, UserOnlineStatus

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket消费者，处理实时聊天功能"""
    
    async def connect(self):
        """建立WebSocket连接"""
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']
        
        # 检查用户是否已登录
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # 检查用户是否有权限访问此聊天室
        if not await self.can_access_room():
            await self.close()
            return
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 更新用户在线状态
        await self.update_online_status('online')
        
        # 接受WebSocket连接
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': '连接成功'
        }))
        
        # 通知其他用户有新用户上线
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_online',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        # 更新用户在线状态为离线
        await self.update_online_status('offline')
        
        # 通知其他用户有用户下线
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_offline',
                'user_id': self.user.id,
                'username': self.user.username
            }
        )
        
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_messages':
                await self.handle_read_messages(data)
            elif message_type == 'ping':
                await self.handle_ping()
            else:
                logger.warning(f"未知的消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("无效的JSON格式")
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
    
    async def handle_chat_message(self, data):
        """处理聊天消息"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        
        if not content:
            return
        
        # 保存消息到数据库
        message = await self.save_message(content, message_type)
        
        # 广播消息给房间内所有用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'message_type': message.message_type,
                    'sender': message.sender.username,
                    'sender_id': message.sender.id,
                    'created_at': message.created_at.isoformat(),
                    'is_own': False
                }
            }
        )
    
    async def handle_typing(self, data):
        """处理用户输入状态"""
        is_typing = data.get('is_typing', False)
        
        # 更新用户输入状态
        await self.update_typing_status(is_typing)
        
        # 通知其他用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_messages(self, data):
        """处理消息已读状态"""
        message_ids = data.get('message_ids', [])
        
        if message_ids:
            # 标记消息为已读
            marked_count = await self.mark_messages_as_read(message_ids)
            
            # 通知其他用户消息已读
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'message_ids': message_ids,
                    'marked_count': marked_count
                }
            )
    
    async def handle_ping(self):
        """处理ping消息"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    # WebSocket消息处理器
    async def chat_message(self, event):
        """发送聊天消息给WebSocket客户端"""
        message = event['message']
        # 标记消息是否为自己发送的
        message['is_own'] = message['sender_id'] == self.user.id
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    async def user_typing(self, event):
        """发送用户输入状态给WebSocket客户端"""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def user_online(self, event):
        """发送用户上线通知给WebSocket客户端"""
        await self.send(text_data=json.dumps({
            'type': 'user_online',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def user_offline(self, event):
        """发送用户下线通知给WebSocket客户端"""
        await self.send(text_data=json.dumps({
            'type': 'user_offline',
            'user_id': event['user_id'],
            'username': event['username']
        }))
    
    async def messages_read(self, event):
        """发送消息已读通知给WebSocket客户端"""
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'user_id': event['user_id'],
            'username': event['username'],
            'message_ids': event['message_ids'],
            'marked_count': event['marked_count']
        }))
    
    # 数据库操作
    @database_sync_to_async
    def can_access_room(self):
        """检查用户是否有权限访问聊天室"""
        try:
            chat_room = ChatRoom.objects.get(room_id=self.room_id)
            participants = [chat_room.user1]
            if chat_room.user2:
                participants.append(chat_room.user2)
            return self.user in participants
        except ChatRoom.DoesNotExist:
            return False
    
    @database_sync_to_async
    def save_message(self, content, message_type):
        """保存消息到数据库"""
        chat_room = ChatRoom.objects.get(room_id=self.room_id)
        return ChatMessage.objects.create(
            room=chat_room,
            sender=self.user,
            content=content,
            message_type=message_type
        )
    
    @database_sync_to_async
    def update_online_status(self, status):
        """更新用户在线状态"""
        UserOnlineStatus.objects.update_or_create(
            user=self.user,
            defaults={
                'status': status,
                'last_seen': timezone.now()
            }
        )
    
    @database_sync_to_async
    def update_typing_status(self, is_typing):
        """更新用户输入状态"""
        UserOnlineStatus.objects.update_or_create(
            user=self.user,
            defaults={
                'is_typing': is_typing,
                'last_seen': timezone.now()
            }
        )
    
    @database_sync_to_async
    def mark_messages_as_read(self, message_ids):
        """标记消息为已读"""
        if not message_ids:
            return 0
        
        # 只标记其他用户发送的消息
        marked_count = ChatMessage.objects.filter(
            id__in=message_ids,
            sender__id__ne=self.user.id,
            is_read=False
        ).update(is_read=True)
        
        return marked_count
