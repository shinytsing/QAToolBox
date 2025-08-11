import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import ChatRoom, ChatMessage, UserOnlineStatus

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # 检查用户是否已登录
        if isinstance(self.scope['user'], AnonymousUser):
            logger.warning(f'Anonymous user attempted to connect to room {self.room_id}')
            await self.close()
            return
        
        # 检查聊天室是否存在且用户有权限访问
        if not await self.can_access_room():
            logger.warning(f'User {self.scope["user"].username} denied access to room {self.room_id}')
            await self.close()
            return
        
        # 加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # 更新在线状态
        await self.update_online_status('online')
        
        await self.accept()
        
        # 获取用户资料信息
        user_profile = await self.get_user_profile_data(self.scope['user'])
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat room',
            'room_id': self.room_id,
            'user': self.scope['user'].username,
            'user_profile': user_profile
        }))
        
        # 广播用户上线消息给房间内其他用户
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.scope['user'].username,
                'user_profile': user_profile
            }
        )
        
        logger.info(f'User {self.scope["user"].username} connected to room {self.room_id}')
    
    async def disconnect(self, close_code):
        # 广播用户离开消息
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.scope['user'].username
            }
        )
        
        # 更新在线状态
        await self.update_online_status('offline')
        
        # 离开房间组
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f'User {self.scope["user"].username} disconnected from room {self.room_id}')
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'read_status':
                await self.handle_read_status(data)
            elif message_type == 'online_status':
                await self.handle_online_status(data)
                
        except json.JSONDecodeError:
            logger.error('Invalid JSON received')
        except Exception as e:
            logger.error(f'Error processing message: {e}')
    
    async def handle_message(self, data):
        """处理聊天消息"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        file_url = data.get('file_url', '')
        
        if not content and message_type == 'text':
            return
        
        # 保存消息到数据库
        message = await self.save_message(content, message_type, file_url)
        
        if message:
            # 广播消息给房间内所有用户
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'sender': message.sender.username,
                        'content': message.content,
                        'message_type': message.message_type,
                        'file_url': message.file_url,
                        'created_at': message.created_at.isoformat(),
                        'is_own': False,
                        'is_read': message.is_read
                    }
                }
            )
    
    async def handle_typing(self, data):
        """处理打字状态"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_typing',
                'username': self.scope['user'].username,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_status(self, data):
        """处理已读状态"""
        message_ids = data.get('message_ids', [])
        
        if message_ids:
            # 标记消息为已读
            await self.mark_messages_read(message_ids)
            
            # 广播已读状态更新
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_status_update',
                    'message_ids': message_ids,
                    'username': self.scope['user'].username
                }
            )
    
    async def handle_online_status(self, data):
        """处理在线状态"""
        status = data.get('status', 'online')
        await self.update_online_status(status)
    
    async def chat_message(self, event):
        """发送聊天消息给WebSocket"""
        message = event['message']
        
        # 标记消息为发送者自己的
        if message['sender'] == self.scope['user'].username:
            message['is_own'] = True
        
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))
    
    async def user_typing(self, event):
        """发送打字状态给WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def read_status_update(self, event):
        """发送已读状态更新给WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read_status_update',
            'message_ids': event['message_ids'],
            'username': event['username']
        }))
    
    async def user_joined(self, event):
        """发送用户加入消息给WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'user_profile': event['user_profile']
        }))
    
    async def user_left(self, event):
        """发送用户离开消息给WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': event['username']
        }))
    
    @database_sync_to_async
    def can_access_room(self):
        """检查用户是否有权限访问聊天室"""
        try:
            # 如果是测试房间，允许所有已登录用户访问
            if self.room_id.startswith('test-room-'):
                return True
                
            room = ChatRoom.objects.get(room_id=self.room_id)
            participants = [room.user1]
            if room.user2:
                participants.append(room.user2)
            return self.scope['user'] in participants
        except ChatRoom.DoesNotExist:
            # 如果房间不存在，创建测试房间
            if self.room_id.startswith('test-room-'):
                from django.contrib.auth.models import User
                try:
                    # 获取第一个用户作为测试用户
                    test_user = User.objects.first()
                    if test_user:
                        room = ChatRoom.objects.create(
                            room_id=self.room_id,
                            user1=test_user,
                            status='active'
                        )
                        return True
                except Exception as e:
                    logger.error(f'Error creating test room: {e}')
            return False
    
    @database_sync_to_async
    def save_message(self, content, message_type, file_url):
        """保存消息到数据库"""
        try:
            room = ChatRoom.objects.get(room_id=self.room_id)
            message = ChatMessage.objects.create(
                room=room,
                sender=self.scope['user'],
                content=content,
                message_type=message_type,
                file_url=file_url
            )
            return message
        except Exception as e:
            logger.error(f'Error saving message: {e}')
            return None
    
    @database_sync_to_async
    def mark_messages_read(self, message_ids):
        """标记消息为已读"""
        try:
            # 标记其他用户发送的消息为已读
            messages = ChatMessage.objects.filter(
                id__in=message_ids
            ).exclude(
                sender=self.scope['user']
            )
            messages.update(is_read=True)
        except Exception as e:
            logger.error(f'Error marking messages as read: {e}')
    
    @database_sync_to_async
    def update_online_status(self, status):
        """更新用户在线状态"""
        try:
            UserOnlineStatus.objects.update_or_create(
                user=self.scope['user'],
                defaults={
                    'status': status,
                    'room_id': self.room_id
                }
            )
        except Exception as e:
            logger.error(f'Error updating online status: {e}')
    
    @database_sync_to_async
    def get_user_profile_data(self, user):
        """获取用户资料数据"""
        try:
            from apps.users.models import Profile, UserMembership, UserTheme
            from django.utils import timezone
            
            profile = Profile.objects.filter(user=user).first()
            membership = UserMembership.objects.filter(user=user).first()
            theme = UserTheme.objects.filter(user=user).first()
            
            # 获取用户标签
            tags = []
            
            if membership and membership.membership_type != 'free':
                tags.append(f'💎 {membership.get_membership_type_display()}')
            
            if theme:
                mode_emojis = {
                    'work': '💻',
                    'life': '🌱',
                    'training': '💪',
                    'emo': '🎭'
                }
                tags.append(f"{mode_emojis.get(theme.mode, '🎯')} {theme.get_mode_display()}")
            
            if user.is_staff:
                tags.append('👑 管理员')
            
            days_since_joined = (timezone.now() - user.date_joined).days
            if days_since_joined > 365:
                tags.append('🎂 老用户')
            elif days_since_joined > 30:
                tags.append('🌟 活跃用户')
            else:
                tags.append('🆕 新用户')
            
            return {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'display_name': f"{user.first_name} {user.last_name}".strip() or user.username,
                'avatar_url': profile.avatar.url if profile and profile.avatar else None,
                'bio': profile.bio if profile else '',
                'membership_type': membership.get_membership_type_display() if membership else '免费用户',
                'theme_mode': theme.get_mode_display() if theme else '默认模式',
                'tags': tags,
                'is_online': True,
            }
        except Exception as e:
            logger.error(f'Error getting user profile data: {e}')
            return {
                'id': user.id,
                'username': user.username,
                'display_name': user.username,
                'avatar_url': None,
                'bio': '',
                'membership_type': '免费用户',
                'theme_mode': '默认模式',
                'tags': ['🆕 新用户'],
                'is_online': True,
            }
