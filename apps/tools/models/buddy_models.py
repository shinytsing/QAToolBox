from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class BuddyEvent(models.Model):
    """搭子活动模型"""
    EVENT_TYPE_CHOICES = [
        ('meal', '饭搭'),
        ('sports', '球搭'),
        ('travel', '旅行搭'),
        ('study', '学习搭'),
        ('game', '游戏搭'),
        ('movie', '电影搭'),
        ('shopping', '购物搭'),
        ('coffee', '咖啡搭'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('active', '招募中'),
        ('full', '人数已满'),
        ('in_progress', '进行中'),
        ('completed', '已结束'),
        ('cancelled', '已取消'),
    ]
    
    COST_TYPE_CHOICES = [
        ('free', '免费'),
        ('aa', 'AA制'),
    ]
    
    GENDER_RESTRICTION_CHOICES = [
        ('none', '不限'),
        ('male', '仅限男性'),
        ('female', '仅限女性'),
    ]
    
    # 基础信息
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发起人')
    title = models.CharField(max_length=200, verbose_name='活动标题')
    description = models.TextField(verbose_name='活动描述')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, verbose_name='活动类型')
    
    # 时间地点
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='结束时间')
    location = models.CharField(max_length=200, verbose_name='活动地点')
    latitude = models.FloatField(blank=True, null=True, verbose_name='纬度')
    longitude = models.FloatField(blank=True, null=True, verbose_name='经度')
    
    # 人数和费用
    max_members = models.IntegerField(default=4, verbose_name='人数上限')
    cost_type = models.CharField(max_length=20, choices=COST_TYPE_CHOICES, default='aa', verbose_name='费用类型')
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='预估费用')
    
    # 限制条件
    gender_restriction = models.CharField(max_length=20, choices=GENDER_RESTRICTION_CHOICES, default='none', verbose_name='性别限制')
    age_min = models.IntegerField(blank=True, null=True, verbose_name='最小年龄')
    age_max = models.IntegerField(blank=True, null=True, verbose_name='最大年龄')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='活动状态')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    application_count = models.IntegerField(default=0, verbose_name='申请次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '搭子活动'
        verbose_name_plural = '搭子活动'
        indexes = [
            models.Index(fields=['event_type', 'status']),
            models.Index(fields=['creator', 'status']),
            models.Index(fields=['start_time']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.creator.username} - {self.title}"
    
    def get_current_member_count(self):
        """获取当前成员数"""
        return self.members.filter(status='joined').count()
    
    def is_full(self):
        """检查是否已满员"""
        return self.get_current_member_count() >= self.max_members
    
    def get_time_until_start(self):
        """获取距离开始时间"""
        from django.utils import timezone
        now = timezone.now()
        if self.start_time > now:
            delta = self.start_time - now
            days = delta.days
            hours = delta.seconds // 3600
            if days > 0:
                return f"{days}天{hours}小时"
            else:
                return f"{hours}小时"
        return "已开始"


class BuddyEventMember(models.Model):
    """搭子活动成员模型"""
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('joined', '已加入'),
        ('rejected', '已拒绝'),
        ('left', '已退出'),
    ]
    
    event = models.ForeignKey(BuddyEvent, on_delete=models.CASCADE, related_name='members', verbose_name='活动')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 申请信息
    application_message = models.TextField(blank=True, null=True, verbose_name='申请留言')
    
    # 时间戳
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    joined_at = models.DateTimeField(blank=True, null=True, verbose_name='加入时间')
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['applied_at']
        verbose_name = '搭子活动成员'
        verbose_name_plural = '搭子活动成员'
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"


class BuddyEventChat(models.Model):
    """搭子活动群聊模型"""
    event = models.OneToOneField(BuddyEvent, on_delete=models.CASCADE, related_name='chat', verbose_name='活动')
    is_active = models.BooleanField(default=False, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '搭子活动群聊'
        verbose_name_plural = '搭子活动群聊'
    
    def __str__(self):
        return f"{self.event.title} - 群聊"


class BuddyEventMessage(models.Model):
    """搭子活动群聊消息模型"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('system', '系统消息'),
    ]
    
    chat = models.ForeignKey(BuddyEventChat, on_delete=models.CASCADE, related_name='messages', verbose_name='群聊')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    
    # 消息状态
    is_read_by = models.ManyToManyField(User, related_name='buddy_read_messages', blank=True, verbose_name='已读用户')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '搭子活动消息'
        verbose_name_plural = '搭子活动消息'
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class BuddyUserProfile(models.Model):
    """搭子用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 兴趣标签
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 位置信息
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在城市')
    district = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在区域')
    
    # 活动统计
    created_events = models.IntegerField(default=0, verbose_name='发起活动数')
    joined_events = models.IntegerField(default=0, verbose_name='参与活动数')
    total_events = models.IntegerField(default=0, verbose_name='总活动数')
    
    # 信用评分
    credit_score = models.IntegerField(default=100, verbose_name='信用评分')
    no_show_count = models.IntegerField(default=0, verbose_name='爽约次数')
    
    # 偏好设置
    notification_enabled = models.BooleanField(default=True, verbose_name='启用通知')
    auto_join_enabled = models.BooleanField(default=False, verbose_name='自动加入')
    
    # 黑名单
    blacklisted_users = models.ManyToManyField(User, related_name='blacklisted_by', blank=True, verbose_name='黑名单用户')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '搭子用户资料'
        verbose_name_plural = '搭子用户资料'
    
    def __str__(self):
        return f"{self.user.username} - 搭子资料"
    
    def get_activity_rate(self):
        """获取活动参与率"""
        if self.total_events == 0:
            return 0
        return round((self.joined_events / self.total_events) * 100, 1)
    
    def get_credit_level(self):
        """获取信用等级"""
        if self.credit_score >= 90:
            return '优秀'
        elif self.credit_score >= 80:
            return '良好'
        elif self.credit_score >= 70:
            return '一般'
        else:
            return '较差'


class BuddyEventReview(models.Model):
    """搭子活动评价模型"""
    event = models.ForeignKey(BuddyEvent, on_delete=models.CASCADE, related_name='reviews', verbose_name='活动')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评价者')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_reviews_received', verbose_name='被评价者')
    
    # 评价内容
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
    comment = models.TextField(blank=True, null=True, verbose_name='评价内容')
    
    # 评价维度
    punctuality = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='守时程度')
    friendliness = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='友好程度')
    participation = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='参与度')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评价时间')
    
    class Meta:
        unique_together = ['event', 'reviewer', 'reviewed_user']
        ordering = ['-created_at']
        verbose_name = '搭子活动评价'
        verbose_name_plural = '搭子活动评价'
    
    def __str__(self):
        return f"{self.reviewer.username} 评价 {self.reviewed_user.username}"


class BuddyEventReport(models.Model):
    """搭子活动举报模型"""
    REPORT_TYPE_CHOICES = [
        ('no_show', '爽约'),
        ('inappropriate', '不当行为'),
        ('harassment', '骚扰'),
        ('fake_info', '虚假信息'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('investigating', '调查中'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_reports', verbose_name='举报者')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buddy_reported', verbose_name='被举报者')
    reported_event = models.ForeignKey(BuddyEvent, on_delete=models.CASCADE, blank=True, null=True, verbose_name='相关活动')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='举报类型')
    description = models.TextField(verbose_name='举报描述')
    evidence = models.JSONField(default=list, verbose_name='证据材料')
    
    # 处理状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='管理员备注')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='举报时间')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '搭子活动举报'
        verbose_name_plural = '搭子活动举报'
    
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username}"
