from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ChatRoom(models.Model):
    """聊天室模型"""

    ROOM_TYPE_CHOICES = [
        ("private", "私聊"),
        ("group", "群聊"),
        ("public", "公开"),
        ("system", "系统"),
    ]

    STATUS_CHOICES = [
        ("waiting", "等待匹配"),
        ("active", "活跃"),
        ("ended", "已结束"),
        ("inactive", "非活跃"),
        ("archived", "已归档"),
        ("deleted", "已删除"),
    ]

    room_id = models.CharField(max_length=100, unique=True, verbose_name="房间ID", blank=True)
    name = models.CharField(max_length=200, verbose_name="房间名称", blank=True, null=True)
    description = models.TextField(blank=True, verbose_name="描述")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default="private", verbose_name="房间类型")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="状态")

    # 为了兼容数据库结构，只使用数据库中存在的字段
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_rooms_as_user1", verbose_name="用户1")
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_rooms_as_user2", verbose_name="用户2", null=True, blank=True
    )

    # 数据库中存在的字段
    max_members = models.IntegerField(default=100, verbose_name="最大成员数")
    is_encrypted = models.BooleanField(default=False, verbose_name="是否加密")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="最后活动时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")

    class Meta:
        verbose_name = "聊天室"
        verbose_name_plural = "聊天室"
        ordering = ["-last_activity"]
        indexes = [
            models.Index(fields=["room_type", "status"]),
            models.Index(fields=["user1", "status"]),
            models.Index(fields=["last_activity"]),
        ]

    def save(self, *args, **kwargs):
        if not self.room_id:
            import uuid

            self.room_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"

    def get_member_count(self):
        """获取成员数量"""
        count = 1 if self.user1 else 0
        if self.user2:
            count += 1
        return count

    def is_user_member(self, user):
        """检查用户是否为成员"""
        return user == self.user1 or user == self.user2

    def is_heart_link_room(self):
        """检查是否是心动链接聊天室"""
        try:
            # 检查是否有心动链接请求
            if hasattr(self, "heart_link_requests") and self.heart_link_requests.exists():
                return True

            # 检查是否是ShipBao商品咨询聊天室（一对一私密聊天）
            if (
                self.room_type == "private"
                and self.user1
                and self.user2
                and hasattr(self, "shipbao_inquiries")
                and self.shipbao_inquiries.exists()
            ):
                return True

            return False
        except Exception:
            return False

    def is_multi_chat_room(self):
        """检查是否是多人聊天室"""
        multi_chat_rooms = ["public-room", "general", "chat", "random"]
        return (
            self.room_id in multi_chat_rooms or self.room_id.startswith("test-room-") or self.room_type in ["group", "public"]
        )

    def get_room_category(self):
        """获取聊天室类别"""
        if self.is_heart_link_room():
            return "heart_link"
        elif self.is_multi_chat_room():
            return "multi_chat"
        else:
            return "private"

    def get_other_user(self, current_user):
        """获取对方用户"""
        if current_user == self.user1:
            return self.user2
        elif current_user == self.user2:
            return self.user1
        return None


class ChatRoomMember(models.Model):
    """聊天室成员模型"""

    ROLE_CHOICES = [
        ("owner", "房主"),
        ("admin", "管理员"),
        ("member", "成员"),
        ("guest", "访客"),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="聊天室")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member", verbose_name="角色")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    last_read = models.DateTimeField(auto_now_add=True, verbose_name="最后阅读时间")
    is_muted = models.BooleanField(default=False, verbose_name="是否禁言")
    is_banned = models.BooleanField(default=False, verbose_name="是否封禁")

    class Meta:
        verbose_name = "聊天室成员"
        verbose_name_plural = "聊天室成员"
        unique_together = ["room", "user"]
        indexes = [
            models.Index(fields=["room", "role"]),
            models.Index(fields=["user", "joined_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.room.name} ({self.get_role_display()})"


class ChatMessage(models.Model):
    """聊天消息模型"""

    MESSAGE_TYPE_CHOICES = [
        ("text", "文本"),
        ("image", "图片"),
        ("file", "文件"),
        ("voice", "语音"),
        ("video", "视频"),
        ("system", "系统消息"),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="聊天室")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发送者")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default="text", verbose_name="消息类型")
    content = models.TextField(verbose_name="内容")
    file_url = models.URLField(blank=True, verbose_name="文件链接")
    file_size = models.IntegerField(default=0, verbose_name="文件大小")
    reply_to = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="回复消息")
    is_edited = models.BooleanField(default=False, verbose_name="是否编辑")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    read_by = models.ManyToManyField(User, through="MessageRead", related_name="chat_read_messages", verbose_name="已读用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发送时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "聊天消息"
        verbose_name_plural = "聊天消息"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
            models.Index(fields=["message_type", "created_at"]),
        ]

    def __str__(self):
        return f"{self.sender.username} - {self.content[:50]}"

    def get_read_count(self):
        """获取已读数量"""
        return self.read_by.count()

    def mark_as_read(self, user):
        """标记为已读"""
        MessageRead.objects.get_or_create(message=self, user=user, defaults={"read_at": timezone.now()})

    def is_read_by_user(self, user):
        """检查用户是否已读"""
        return self.read_by.filter(id=user.id).exists()


class MessageRead(models.Model):
    """消息已读记录模型"""

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name="消息")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    read_at = models.DateTimeField(auto_now_add=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "消息已读记录"
        verbose_name_plural = "消息已读记录"
        unique_together = ["message", "user"]
        indexes = [
            models.Index(fields=["message", "read_at"]),
            models.Index(fields=["user", "read_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} 已读 {self.message.id}"


class UserOnlineStatus(models.Model):
    """用户在线状态模型"""

    STATUS_CHOICES = [
        ("online", "在线"),
        ("busy", "忙碌"),
        ("away", "离开"),
        ("offline", "离线"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="offline", verbose_name="在线状态", db_index=True)
    last_seen = models.DateTimeField(auto_now=True, verbose_name="最后在线时间")
    is_typing = models.BooleanField(default=False, verbose_name="是否正在输入")
    current_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="当前房间")
    is_online = models.BooleanField(default=False, verbose_name="是否在线")
    match_number = models.CharField(max_length=4, null=True, blank=True, verbose_name="匹配数字", db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")

    class Meta:
        verbose_name = "用户在线状态"
        verbose_name_plural = "用户在线状态"
        indexes = [
            models.Index(fields=["status", "last_seen"]),
            models.Index(fields=["is_online", "last_seen"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    def go_online(self, room=None):
        """用户上线"""
        self.status = "online"
        self.is_online = True
        if room:
            self.current_room = room
        self.save()

    def go_offline(self):
        """用户下线"""
        self.status = "offline"
        self.is_online = False
        self.current_room = None
        self.save()

    def update_last_seen(self):
        """更新最后在线时间"""
        self.last_seen = timezone.now()
        self.save(update_fields=["last_seen"])

    @classmethod
    def get_online_users(cls):
        """获取在线用户列表"""
        return cls.objects.filter(is_online=True, status="online")


class HeartLinkRequest(models.Model):
    """心动链接请求模型"""

    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("matched", "已匹配"),
        ("expired", "已过期"),
        ("cancelled", "已取消"),
    ]

    REQUEST_TYPE_CHOICES = [
        ("friend", "好友"),
        ("dating", "约会"),
        ("relationship", "恋爱"),
        ("marriage", "结婚"),
    ]

    # 匹配数据库schema
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="heart_link_requests", verbose_name="请求者")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    matched_at = models.DateTimeField(null=True, blank=True, verbose_name="匹配时间")
    matched_with = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="matched_heart_links", verbose_name="匹配用户"
    )
    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name="heart_link_requests", verbose_name="聊天室"
    )

    class Meta:
        verbose_name = "心动链接请求"
        verbose_name_plural = "心动链接请求"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["requester", "status"]),
            models.Index(fields=["matched_with", "status"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.requester.username} 的心动链接请求"

    def is_expired(self):
        """检查是否过期（10分钟）"""
        from datetime import timedelta

        from django.utils import timezone

        return timezone.now() > self.created_at + timedelta(minutes=10)

    def expire(self):
        """过期请求"""
        self.status = "expired"
        self.save()

    @property
    def get_remaining_time(self):
        """获取剩余时间"""
        from datetime import timedelta

        if self.is_expired():
            return timedelta(0)
        expiry_time = self.created_at + timedelta(minutes=10)
        return expiry_time - timezone.now()


class ChatNotification(models.Model):
    """聊天通知模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, verbose_name="聊天室")
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, verbose_name="消息")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间")

    class Meta:
        verbose_name = "聊天通知"
        verbose_name_plural = "聊天通知"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["room", "is_read"]),
        ]

    def __str__(self):
        status = "已读" if self.is_read else "未读"
        return f"{self.user.username} - {self.room.name} - {status}"

    def mark_as_read(self):
        """标记为已读"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
