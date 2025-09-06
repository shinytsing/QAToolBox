from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    max_members = models.PositiveIntegerField(default=100)
    
    class Meta:
        db_table = 'chat_rooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ChatMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('system', '系统消息'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    content = models.TextField()
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class UserConnection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections')
    room_name = models.CharField(max_length=100)
    is_connected = models.BooleanField(default=False)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_connections'
        unique_together = ['user', 'room_name']
    
    def __str__(self):
        return f"{self.user.username} - {self.room_name}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('info', '信息'),
        ('success', '成功'),
        ('warning', '警告'),
        ('error', '错误'),
        ('system', '系统'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.title}"

class RealTimeData(models.Model):
    DATA_TYPES = [
        ('fitness', '健身数据'),
        ('life', '生活数据'),
        ('social', '社交数据'),
        ('system', '系统数据'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='realtime_data')
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    data_key = models.CharField(max_length=100)
    data_value = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'realtime_data'
        unique_together = ['user', 'data_type', 'data_key']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.data_type}: {self.data_key}"
