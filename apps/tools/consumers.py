import json
import logging
import gzip
import time
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from .models.legacy_models import ChatRoom, ChatMessage, UserOnlineStatus
from .services.reconnection_manager import (
    ReconnectionManager, ConnectionConfig, MessageCompressor,
    get_reconnection_manager, remove_reconnection_manager
)

logger = logging.getLogger(__name__)

# 连接池管理
connection_pool = {}

def compress_message(data):
    """压缩消息数据"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        if len(json_str) > 1024:  # 只压缩大于1KB的消息
            compressed = gzip.compress(json_str.encode('utf-8'))
            return {
                'compressed': True,
                'data': compressed.hex()
            }
        return {'compressed': False, 'data': data}
    except Exception as e:
        logger.error(f'消息压缩失败: {e}')
        return {'compressed': False, 'data': data}

def decompress_message(data):
    """解压消息数据"""
    try:
        if data.get('compressed'):
            compressed_data = bytes.fromhex(data['data'])
            decompressed = gzip.decompress(compressed_data)
            return json.loads(decompressed.decode('utf-8'))
        return data.get('data', data)
    except Exception as e:
        logger.error(f'消息解压失败: {e}')
        return data.get('data', data)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # 获取查询参数中的令牌
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        import urllib.parse
        query_params = urllib.parse.parse_qs(query_string)
        self.token = query_params.get('token', [None])[0]
        
        # 检查用户是否已登录
        if isinstance(self.scope['user'], AnonymousUser):
            # 对于测试房间，允许匿名用户连接
            if self.room_id.startswith('test-room-'):
                logger.info(f'Anonymous user connecting to test room {self.room_id}')
            else:
                logger.warning(f'Anonymous user attempted to connect to room {self.room_id}')
                await self.close()
                return
        
        # 验证令牌和权限
        if not await self.verify_token_and_access():
            logger.warning(f'User {self.scope["user"].username} denied access to room {self.room_id} (token verification failed)')
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
        
        # 添加到连接池
        user_id = self.scope['user'].id
        if user_id not in connection_pool:
            connection_pool[user_id] = {}
        connection_pool[user_id][self.room_id] = self
        
        # 获取用户资料信息
        user_profile = await self.get_user_profile_data(self.scope['user'])
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to chat room',
            'room_id': self.room_id,
            'user': self.scope['user'].username,
            'user_profile': user_profile,
            'heartbeat_interval': 30  # 30秒心跳间隔
        }))
        
        # 启动心跳任务
        asyncio.create_task(self.heartbeat_task())
        
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
        try:
            # 从连接池中移除
            user_id = self.scope['user'].id
            if user_id in connection_pool and self.room_id in connection_pool[user_id]:
                del connection_pool[user_id][self.room_id]
                if not connection_pool[user_id]:
                    del connection_pool[user_id]
            
            # 广播用户离开消息
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'username': self.scope['user'].username
                }
            )
            
            # 更新在线状态为离线
            await self.update_online_status('offline')
            
            # 记录断开连接时间
            await self.record_disconnect_time()
            
            # 离开房间组
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info(f'User {self.scope["user"].username} disconnected from room {self.room_id} (code: {close_code})')
            
        except Exception as e:
            logger.error(f'Error during disconnect: {e}')
    
    async def heartbeat_task(self):
        """心跳任务"""
        try:
            while True:
                await asyncio.sleep(30)  # 30秒发送一次心跳
                if hasattr(self, 'scope') and self.scope.get('user'):
                    await self.send(text_data=json.dumps({
                        'type': 'heartbeat',
                        'timestamp': int(time.time())
                    }))
        except Exception as e:
            logger.error(f'心跳任务异常: {e}')
    
    async def receive(self, text_data):
        try:
            # 解压消息
            raw_data = json.loads(text_data)
            data = decompress_message(raw_data)
            message_type = data.get('type', 'message')
            
            # 处理心跳响应
            if message_type == 'heartbeat_ack':
                await self.send(text_data=json.dumps({
                    'type': 'heartbeat_ack',
                    'timestamp': int(time.time())
                }))
                return
            
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
            # 获取用户资料信息
            user_profile = await self.get_user_profile_data(self.scope['user'])
            
            # 构建消息数据
            message_data = {
                'id': message.id,
                'sender': message.sender.username,
                'sender_id': message.sender.id,
                'sender_avatar': user_profile.get('avatar', ''),
                'content': message.content,
                'message_type': message.message_type,
                'file_url': message.file_url,
                'created_at': message.created_at.isoformat(),
                'is_own': False,
                'is_read': message.is_read
            }
            
            # 压缩消息数据
            compressed_data = compress_message(message_data)
            
            # 广播消息给房间内所有用户
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': compressed_data
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
            
            # 同时通过API标记已读（确保数据库状态同步）
            await self.mark_messages_read_via_api(message_ids)
            
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
        compressed_message = event['message']
        
        # 解压消息数据
        message = decompress_message(compressed_message)
        
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
    def verify_token_and_access(self):
        """验证令牌和用户访问权限"""
        try:
            # 如果是测试房间，允许所有已登录用户访问
            if self.room_id.startswith('test-room-'):
                # 检查测试房间是否存在，如果不存在则创建
                room, created = ChatRoom.objects.get_or_create(
                    room_id=self.room_id,
                    defaults={
                        'user1': self.scope['user'],
                        'status': 'active'
                    }
                )
                return True
                
            room = ChatRoom.objects.get(room_id=self.room_id)
            
            # 检查聊天室状态
            if room.status != 'active':
                return False
            
            # 检查用户是否是聊天室的参与者
            participants = [room.user1]
            if room.user2:
                participants.append(room.user2)
            
            if self.scope['user'] not in participants:
                return False
            
            # 验证令牌（简化验证，主要依赖用户权限检查）
            # 在实际应用中，可以存储令牌到数据库进行更严格的验证
            if hasattr(self, 'token') and self.token:
                # 这里可以添加更复杂的令牌验证逻辑
                return True
            else:
                # 如果没有令牌，仍然允许访问（向后兼容）
                return True
                
        except ChatRoom.DoesNotExist:
            logger.warning(f'Room {self.room_id} does not exist')
            return False
        except Exception as e:
            logger.error(f'Error checking room access: {e}')
            return False
    
    @database_sync_to_async
    def can_access_room(self):
        """检查用户是否有权限访问聊天室（向后兼容）"""
        return self.verify_token_and_access()
    
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
    
    async def mark_messages_read_via_api(self, message_ids):
        """通过API标记消息为已读"""
        try:
            import aiohttp
            import asyncio
            
            # 构建API请求
            url = f'http://localhost:8001/tools/api/chat/{self.room_id}/mark_read/'
            headers = {
                'Content-Type': 'application/json',
                'X-CSRFToken': getattr(self.scope, 'csrf_token', ''),
            }
            data = {
                'message_ids': message_ids
            }
            
            # 异步发送API请求
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f'API标记已读成功: {result}')
                    else:
                        logger.warning(f'API标记已读失败: {response.status}')
        except Exception as e:
            logger.error(f'Error marking messages as read via API: {e}')
    
    @database_sync_to_async
    def update_online_status(self, status):
        """更新用户在线状态"""
        try:
            # 获取聊天室对象
            room = ChatRoom.objects.get(room_id=self.room_id)
            
            UserOnlineStatus.objects.update_or_create(
                user=self.scope['user'],
                defaults={
                    'status': status,
                    'current_room': room,
                    'is_online': status == 'online'
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
    
    @database_sync_to_async
    def record_disconnect_time(self):
        """记录用户断开连接时间"""
        try:
            from django.utils import timezone
            
            # 更新用户在线状态，记录断开时间
            online_status, created = UserOnlineStatus.objects.get_or_create(
                user=self.scope['user'],
                defaults={
                    'status': 'offline',
                    'is_online': False,
                    'last_seen': timezone.now()
                }
            )
            
            if not created:
                online_status.status = 'offline'
                online_status.is_online = False
                online_status.last_seen = timezone.now()
                online_status.save()
            
            # 检查聊天室是否需要结束
            try:
                room = ChatRoom.objects.get(room_id=self.room_id)
                if room.status == 'active':
                    # 检查房间中的其他用户是否也离线
                    participants = room.participants
                    all_offline = True
                    
                    for participant in participants:
                        if participant != self.scope['user']:
                            participant_status = UserOnlineStatus.objects.filter(user=participant).first()
                            if participant_status and participant_status.is_online:
                                all_offline = False
                                break
                    
                    # 如果所有用户都离线，标记房间为需要清理
                    if all_offline:
                        logger.info(f'聊天室 {self.room_id} 所有用户已离线，标记为需要清理')
                        
            except ChatRoom.DoesNotExist:
                pass
                
        except Exception as e:
            logger.error(f'Error recording disconnect time: {e}')
