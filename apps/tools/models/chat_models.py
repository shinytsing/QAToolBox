from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Index, Q
import random
import json
from datetime import timedelta


class ChatRoom(models.Model):
    """聊天室模型"""
    ROOM_TYPE_CHOICES = [
        ('private', '私聊'),
        ('group', '群聊'),
        ('public', '公开'),
        ('system', '系统'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('inactive', '非活跃'),
        ('archived', '已归档'),
        ('deleted', '已删除'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='房间名称')
    description = models.TextField(blank=True, verbose_name='描述')
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='private', verbose_name='房间类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms', verbose_name='创建者')
    members = models.ManyToManyField(User, through='ChatRoomMember', related_name='joined_rooms', verbose_name='成员')
    max_members = models.IntegerField(default=100, verbose_name='最大成员数')
    is_encrypted = models.BooleanField(default=False, verbose_name='是否加密')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最后活动时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['room_type', 'status']),
            models.Index(fields=['creator', 'status']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def get_member_count(self):
        """获取成员数量"""
        return self.members.count()

    def is_user_member(self, user):
        """检查用户是否为成员"""
        return self.members.filter(id=user.id).exists()

    def add_member(self, user, role='member'):
        """添加成员"""
        ChatRoomMember.objects.get_or_create(
            room=self,
            user=user,
            defaults={'role': role}
        )

    def remove_member(self, user):
        """移除成员"""
        ChatRoomMember.objects.filter(room=self, user=user).delete()

    def get_online_members(self):
        """获取在线成员"""
        return self.members.filter(
            useronlinestatus__is_online=True,
            useronlinestatus__last_seen__gte=timezone.now() - timedelta(minutes=5)
        )


class ChatRoomMember(models.Model):
    """聊天室成员模型"""
    ROLE_CHOICES = [
        ('owner', '房主'),
        ('admin', '管理员'),
        ('member', '成员'),
        ('guest', '访客'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name='聊天室')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name='角色')
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    last_read = models.DateTimeField(auto_now_add=True, verbose_name='最后阅读时间')
    is_muted = models.BooleanField(default=False, verbose_name='是否禁言')
    is_banned = models.BooleanField(default=False, verbose_name='是否封禁')

    class Meta:
        verbose_name = '聊天室成员'
        verbose_name_plural = '聊天室成员'
        unique_together = ['room', 'user']
        indexes = [
            models.Index(fields=['room', 'role']),
            models.Index(fields=['user', 'joined_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.room.name} ({self.get_role_display()})"


class ChatMessage(models.Model):
    """聊天消息模型"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('voice', '语音'),
        ('video', '视频'),
        ('system', '系统消息'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name='聊天室')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='内容')
    file_url = models.URLField(blank=True, verbose_name='文件链接')
    file_size = models.IntegerField(default=0, verbose_name='文件大小')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='回复消息')
    is_edited = models.BooleanField(default=False, verbose_name='是否编辑')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    read_by = models.ManyToManyField(User, through='MessageRead', related_name='chat_read_messages', verbose_name='已读用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
            models.Index(fields=['message_type', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender.username} - {self.content[:50]}"

    def get_read_count(self):
        """获取已读数量"""
        return self.read_by.count()

    def mark_as_read(self, user):
        """标记为已读"""
        MessageRead.objects.get_or_create(
            message=self,
            user=user,
            defaults={'read_at': timezone.now()}
        )

    def is_read_by_user(self, user):
        """检查用户是否已读"""
        return self.read_by.filter(id=user.id).exists()


class MessageRead(models.Model):
    """消息已读记录模型"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name='消息')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    read_at = models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')

    class Meta:
        verbose_name = '消息已读记录'
        verbose_name_plural = '消息已读记录'
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message', 'read_at']),
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.username} 已读 {self.message.id}"


class UserOnlineStatus(models.Model):
    """用户在线状态模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    is_online = models.BooleanField(default=False, verbose_name='是否在线')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='最后在线时间')
    current_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='当前房间')
    device_info = models.JSONField(default=dict, verbose_name='设备信息')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')

    class Meta:
        verbose_name = '用户在线状态'
        verbose_name_plural = '用户在线状态'
        indexes = [
            models.Index(fields=['is_online', 'last_seen']),
            models.Index(fields=['current_room']),
        ]

    def __str__(self):
        status = "在线" if self.is_online else "离线"
        return f"{self.user.username} - {status}"

    def go_online(self, room=None):
        """用户上线"""
        self.is_online = True
        if room:
            self.current_room = room
        self.save()

    def go_offline(self):
        """用户下线"""
        self.is_online = False
        self.current_room = None
        self.save()

    def update_last_seen(self):
        """更新最后在线时间"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class HeartLinkRequest(models.Model):
    """心动链接请求模型"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('accepted', '已接受'),
        ('rejected', '已拒绝'),
        ('expired', '已过期'),
    ]
    
    REQUEST_TYPE_CHOICES = [
        ('friend', '好友'),
        ('dating', '约会'),
        ('relationship', '恋爱'),
        ('marriage', '结婚'),
    ]
    
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_heart_links', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_heart_links', verbose_name='接收者')
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, verbose_name='请求类型')
    message = models.TextField(blank=True, verbose_name='留言')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='接受时间')
    rejected_at = models.DateTimeField(null=True, blank=True, verbose_name='拒绝时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '心动链接请求'
        verbose_name_plural = '心动链接请求'
        unique_together = ['sender', 'receiver', 'request_type']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} ({self.get_request_type_display()})"

    def is_expired(self):
        """检查是否过期"""
        return timezone.now() > self.expires_at

    def accept(self):
        """接受请求"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()

    def reject(self):
        """拒绝请求"""
        self.status = 'rejected'
        self.rejected_at = timezone.now()
        self.save()

    def expire(self):
        """过期请求"""
        self.status = 'expired'
        self.save()

    def get_remaining_time(self):
        """获取剩余时间"""
        if self.is_expired():
            return timedelta(0)
        return self.expires_at - timezone.now()
