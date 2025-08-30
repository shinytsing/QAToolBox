from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Index, Q
import random
import json

# 导入聊天模型以避免循环导入
from .chat_models import ChatRoom, ChatMessage


# ToolUsageLog 已移至 base_models.py，这里不再重复定义
# LifeDiaryEntry已移到diary_models.py，避免重复定义


class LifeGoal(models.Model):
    """生活目标模型"""
    GOAL_STATUS_CHOICES = [
        ('active', '进行中'),
        ('completed', '已完成'),
        ('paused', '暂停'),
        ('cancelled', '已取消'),
    ]
    
    GOAL_CATEGORY_CHOICES = [
        ('health', '健康'),
        ('career', '事业'),
        ('learning', '学习'),
        ('relationship', '人际关系'),
        ('finance', '财务'),
        ('hobby', '兴趣爱好'),
        ('spiritual', '精神成长'),
        ('travel', '旅行'),
        ('other', '其他'),
    ]
    
    GOAL_TYPE_CHOICES = [
        ('daily', '每日目标'),
        ('weekly', '每周目标'),
        ('monthly', '每月目标'),
        ('quarterly', '季度目标'),
        ('yearly', '年度目标'),
        ('lifetime', '人生目标'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
        ('expert', '专家级'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', db_index=True)
    title = models.CharField(max_length=200, verbose_name='目标标题')
    description = models.TextField(blank=True, null=True, verbose_name='目标描述')
    category = models.CharField(max_length=20, choices=GOAL_CATEGORY_CHOICES, verbose_name='目标类别', db_index=True)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='daily', verbose_name='目标类型', db_index=True)
    status = models.CharField(max_length=20, choices=GOAL_STATUS_CHOICES, default='active', verbose_name='状态', db_index=True)
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    target_date = models.DateField(null=True, blank=True, verbose_name='目标日期', db_index=True)
    progress = models.IntegerField(default=0, verbose_name='进度百分比')
    priority = models.IntegerField(default=5, verbose_name='优先级(1-10)', db_index=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='难度等级')
    milestones = models.JSONField(default=list, verbose_name='里程碑')
    tags = models.JSONField(default=list, verbose_name='标签')
    reminder_enabled = models.BooleanField(default=True, verbose_name='启用提醒')
    reminder_frequency = models.CharField(max_length=20, default='daily', verbose_name='提醒频率')
    reminder_time = models.TimeField(default='09:00', verbose_name='提醒时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = '生活目标'
        verbose_name_plural = '生活目标'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['status', 'target_date']),
            models.Index(fields=['user', 'priority']),
            models.Index(fields=['user', 'goal_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_days_remaining(self):
        """获取剩余天数"""
        if not self.target_date:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        remaining = (self.target_date - today).days
        return max(0, remaining)
    
    def is_overdue(self):
        """检查是否逾期"""
        if not self.target_date:
            return False
        from django.utils import timezone
        today = timezone.now().date()
        return self.target_date < today and self.status == 'active'
    
    def get_priority_color(self):
        """获取优先级对应的颜色"""
        if self.priority >= 8:
            return '#ff4444'  # 红色 - 紧急
        elif self.priority >= 6:
            return '#ff8800'  # 橙色 - 重要
        else:
            return '#4CAF50'  # 绿色 - 普通
    
    def get_milestones_display(self):
        """获取里程碑显示文本"""
        if not self.milestones:
            return '无里程碑'
        return f"{len(self.milestones)} 个里程碑"
    
    def get_tags_display(self):
        """获取标签显示文本"""
        return ', '.join(self.tags) if self.tags else '无标签'

    @classmethod
    def get_user_goals_summary(cls, user):
        """获取用户目标摘要，带缓存"""
        cache_key = f"goals_summary_{user.id}"
        summary = cache.get(cache_key)
        
        if summary is None:
            goals = cls.objects.filter(user=user)
            
            summary = {
                'total_goals': goals.count(),
                'active_goals': goals.filter(status='active').count(),
                'completed_goals': goals.filter(status='completed').count(),
                'overdue_goals': goals.filter(status='active', target_date__lt=timezone.now().date()).count(),
                'category_breakdown': list(goals.values('category').annotate(count=models.Count('id'))),
                'priority_breakdown': list(goals.values('priority').annotate(count=models.Count('id'))),
            }
            cache.set(cache_key, summary, 300)  # 缓存5分钟
        
        return summary


class LifeGoalProgress(models.Model):
    """生活目标进度记录模型"""
    goal = models.ForeignKey(LifeGoal, on_delete=models.CASCADE, verbose_name='目标', db_index=True)
    date = models.DateField(auto_now_add=True, verbose_name='日期', db_index=True)
    progress_value = models.IntegerField(verbose_name='进度值')
    notes = models.TextField(blank=True, null=True, verbose_name='进度备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_index=True)
    
    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['-date']
        verbose_name = '目标进度'
        verbose_name_plural = '目标进度'
        indexes = [
            models.Index(fields=['goal', 'date']),
            models.Index(fields=['date', 'progress_value']),
        ]
    
    def __str__(self):
        return f"{self.goal.title} - {self.date} - {self.progress_value}%"


class LifeStatistics(models.Model):
    """生活统计数据模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', db_index=True)
    date = models.DateField(auto_now_add=True, verbose_name='日期', db_index=True)
    total_diary_days = models.IntegerField(default=0, verbose_name='日记总天数')
    total_diary_count = models.IntegerField(default=0, verbose_name='日记总次数')
    happy_days = models.IntegerField(default=0, verbose_name='开心天数')
    total_goals = models.IntegerField(default=0, verbose_name='目标总数')
    completed_goals = models.IntegerField(default=0, verbose_name='已完成目标数')
    mood_distribution = models.JSONField(default=dict, verbose_name='心情分布')
    goal_completion_rate = models.FloatField(default=0.0, verbose_name='目标完成率')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '生活统计'
        verbose_name_plural = '生活统计'
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date', 'goal_completion_rate']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - 统计"


class ShipBaoInquiry(models.Model):
    """船宝商品咨询队列模型"""
    STATUS_CHOICES = [
        ('pending', '待响应'),
        ('responded', '已响应'),
        ('ignored', '已忽略'),
        ('cancelled', '已取消'),
    ]
    
    item = models.ForeignKey('ShipBaoItem', on_delete=models.CASCADE, verbose_name='商品', related_name='inquiries')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='买家', related_name='shipbao_inquiries')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='卖家', related_name='received_inquiries')
    chat_room = models.ForeignKey('tools.ChatRoom', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='聊天室')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    initial_message = models.TextField(blank=True, verbose_name='初始消息')
    priority_score = models.IntegerField(default=0, verbose_name='优先级分数')  # 基于买家信誉等计算
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='响应时间')
    
    class Meta:
        unique_together = ['item', 'buyer']  # 每个买家对每个商品只能咨询一次
        ordering = ['-priority_score', 'created_at']
        verbose_name = '商品咨询'
        verbose_name_plural = '商品咨询'
        indexes = [
            models.Index(fields=['item', 'status']),
            models.Index(fields=['seller', 'status', 'created_at']),
            models.Index(fields=['buyer', 'status']),
        ]
    
    def __str__(self):
        return f"{self.buyer.username} 咨询 {self.item.title}"
    
    def calculate_priority_score(self):
        """计算优先级分数"""
        score = 0
        
        # 基于买家信誉
        if hasattr(self.buyer, 'profile'):
            profile = self.buyer.profile
            # 假设有信誉分数字段
            if hasattr(profile, 'reputation_score'):
                score += profile.reputation_score * 10
        
        # 基于消息长度（更详细的咨询给更高优先级）
        if self.initial_message:
            score += min(len(self.initial_message) // 10, 50)
        
        # 基于时间（新咨询略微优先）
        from django.utils import timezone
        hours_ago = (timezone.now() - self.created_at).total_seconds() / 3600
        score += max(0, 24 - hours_ago)  # 24小时内逐渐降低优先级
        
        self.priority_score = int(score)
        return self.priority_score


# ChatRoom模型已移动到chat_models.py
# class ChatRoom(models.Model):
#     """聊天室模型"""
#     ROOM_STATUS_CHOICES = [
#         ('waiting', '等待匹配'),
#         ('active', '活跃'),
#         ('ended', '已结束'),
#     ]
#     
#     room_id = models.CharField(max_length=100, unique=True, db_index=True)  # 添加索引
#     user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_1', db_index=True)
#     user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_2', null=True, blank=True, db_index=True)
#     status = models.CharField(max_length=20, default='active', db_index=True)  # 添加索引
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 添加索引
#     updated_at = models.DateTimeField(auto_now=True)
# 
#     class Meta:
#         indexes = [
#             models.Index(fields=['status', 'created_at']),
#             models.Index(fields=['user1', 'status']),
#             models.Index(fields=['user2', 'status']),
#             models.Index(fields=['user1', 'user2']),
#         ]
# 
#     def __str__(self):
#         return f"聊天室 {self.room_id}"
#     
#     @property
#     def is_full(self):
#         return self.user2 is not None
#     
#     @property
#     def participants(self):
#         participants = [self.user1]
#         if self.user2:
#             participants.append(self.user2)
#         return participants
# 
#     @classmethod
#     def get_user_active_rooms(cls, user):
#         """获取用户活跃聊天室，带缓存"""
#         cache_key = f"active_rooms_{user.id}"
#         rooms = cache.get(cache_key)
#         
#         if rooms is None:
#             rooms = list(cls.objects.filter(
#                 Q(user1=user) | Q(user2=user),
#                 status='active'
#             ).select_related('user1', 'user2'))
#             cache.set(cache_key, rooms, 60)  # 缓存1分钟
#         
#         return rooms


# ChatMessage模型已移动到chat_models.py
# class ChatMessage(models.Model):
#     """聊天消息模型"""
#     MESSAGE_TYPES = [
#         ('text', '文本'),
#         ('image', '图片'),
#         ('file', '文件'),
#         ('emoji', '表情'),
#         ('video', '视频'),
#         ('audio', '语音'),
#     ]
#     
#     room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='chat_messages', db_index=True)
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', db_index=True)
#     message_type = models.CharField(max_length=20, default='text', db_index=True)  # 添加索引
#     content = models.TextField()
#     file_url = models.URLField(blank=True, null=True, verbose_name='文件URL')
#     is_read = models.BooleanField(default=False, verbose_name='是否已读', db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 添加索引
#     
#     class Meta:
#         indexes = [
#             models.Index(fields=['room', 'created_at']),
#             models.Index(fields=['sender', 'created_at']),
#             models.Index(fields=['message_type', 'created_at']),
#             models.Index(fields=['room', 'is_read']),
#         ]
#         verbose_name = '聊天消息'
#         verbose_name_plural = '聊天消息'
#         ordering = ['created_at']
#     
#     def __str__(self):
#         return f"{self.sender.username}: {self.content[:50]}"
# 
#     @classmethod
#     def get_room_messages(cls, room, limit=50, offset=0):
#         """获取聊天室消息，带分页和缓存"""
#         cache_key = f"room_messages_{room.id}_{limit}_{offset}"
#         messages = cache.get(cache_key)
#         
#         if messages is None:
#             messages = list(cls.objects.filter(room=room).select_related('sender').order_by('-created_at')[offset:offset+limit])
#             cache.set(cache_key, messages, 30)  # 缓存30秒
#         
#         return messages

    @classmethod
    def get_unread_count(cls, user, room):
        """获取用户在指定房间的未读消息数"""
        return cls.objects.filter(
            room=room,
            sender__in=room.participants,
            is_read=False
        ).exclude(sender=user).count()


# UserOnlineStatus模型已移动到chat_models.py
# class UserOnlineStatus(models.Model):
#     """用户在线状态模型"""
#     STATUS_CHOICES = [
#         ('online', '在线'),
#         ('busy', '忙碌'),
#         ('away', '离开'),
#         ('offline', '离线'),
#     ]
#     
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='online_status', verbose_name='用户')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='在线状态', db_index=True)
#     last_seen = models.DateTimeField(auto_now=True, verbose_name='最后在线时间', db_index=True)
#     is_typing = models.BooleanField(default=False, verbose_name='是否正在输入')
#     current_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_users', verbose_name='当前房间')
#     is_online = models.BooleanField(default=False, verbose_name='是否在线', db_index=True)
#     match_number = models.CharField(max_length=4, null=True, blank=True, verbose_name='匹配数字')
#     
#     class Meta:
#         verbose_name = '用户在线状态'
#         verbose_name_plural = '用户在线状态'
#         indexes = [
#             models.Index(fields=['status', 'last_seen']),
#             models.Index(fields=['is_online', 'last_seen']),
#         ]
#     
#     def __str__(self):
#         return f"{self.user.username} - {self.get_status_display()}"
# 
#     @classmethod
#     def get_online_users(cls):
#         """获取在线用户列表，带缓存"""
#         cache_key = "online_users"
#         users = cache.get(cache_key)
#         
#         if users is None:
#             users = list(cls.objects.filter(is_online=True).select_related('user'))
#             cache.set(cache_key, users, 30)  # 缓存30秒
#         
#         return users


# HeartLinkRequest模型已移动到chat_models.py
# class HeartLinkRequest(models.Model):
#     """心动链接请求模型"""
#     STATUS_CHOICES = [
#         ('pending', '等待中'),
#         ('matching', '匹配中'),
#         ('matched', '已匹配'),
#         ('expired', '已过期'),
#         ('cancelled', '已取消'),
#     ]
#     
#     requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heart_link_requests', db_index=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)  # 添加索引
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 添加索引
#     matched_at = models.DateTimeField(null=True, blank=True, verbose_name='匹配时间')
#     matched_with = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_heart_links', verbose_name='匹配用户')
#     chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='heart_link_requests', db_index=True)
#     
#     class Meta:
#         indexes = [
#             models.Index(fields=['requester', 'status']),
#             models.Index(fields=['chat_room', 'status']),
#             models.Index(fields=['status', 'created_at']),
#             models.Index(fields=['matched_with', 'status']),
#         ]
#         verbose_name = '心动链接请求'
#         verbose_name_plural = '心动链接请求'
#         ordering = ['-created_at']
#         unique_together = ['requester', 'chat_room']
#     
#     def __str__(self):
#         return f"{self.requester.username} 的心动链接请求"
#     
#     @property
#     def is_expired(self):
#         """检查请求是否过期（10分钟）"""
#         from django.utils import timezone
#         from datetime import timedelta
#         return timezone.now() > self.created_at + timedelta(minutes=10)
# 
#     @classmethod
#     def get_pending_requests(cls):
#         """获取待处理的请求，带缓存"""
#         cache_key = "pending_heart_requests"
#         requests = cache.get(cache_key)
#         
#         if requests is None:
#             requests = list(cls.objects.filter(status='pending').select_related('requester'))
#             cache.set(cache_key, requests, 30)  # 缓存30秒
#         
#         return requests


class UserAchievement(models.Model):
    """用户成就模型"""
    ACHIEVEMENT_TYPE_CHOICES = [
        ('diary', '日记成就'),
        ('goal', '目标成就'),
        ('streak', '连续成就'),
        ('milestone', '里程碑成就'),
        ('custom', '自定义成就'),
    ]
    
    ACHIEVEMENT_LEVEL_CHOICES = [
        ('bronze', '铜牌'),
        ('silver', '银牌'),
        ('gold', '金牌'),
        ('platinum', '白金'),
        ('diamond', '钻石'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', db_index=True)
    title = models.CharField(max_length=200, verbose_name='成就标题')
    description = models.TextField(blank=True, null=True, verbose_name='成就描述')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES, verbose_name='成就类型', db_index=True)
    level = models.CharField(max_length=20, choices=ACHIEVEMENT_LEVEL_CHOICES, default='bronze', verbose_name='成就等级')
    icon = models.CharField(max_length=50, default='fas fa-trophy', verbose_name='成就图标')
    is_custom = models.BooleanField(default=False, verbose_name='是否自定义')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='获得时间', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就'
        indexes = [
            models.Index(fields=['user', 'achievement_type']),
            models.Index(fields=['user', 'level']),
            models.Index(fields=['achievement_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_level_color(self):
        """获取成就等级对应的颜色"""
        colors = {
            'bronze': '#cd7f32',
            'silver': '#c0c0c0',
            'gold': '#ffd700',
            'platinum': '#e5e4e2',
            'diamond': '#b9f2ff',
        }
        return colors.get(self.level, '#cd7f32')
    
    def get_icon_class(self):
        """获取成就图标类名"""
        return self.icon if self.icon else 'fas fa-trophy'

    @classmethod
    def get_user_achievements_summary(cls, user):
        """获取用户成就摘要，带缓存"""
        cache_key = f"achievements_summary_{user.id}"
        summary = cache.get(cache_key)
        
        if summary is None:
            achievements = cls.objects.filter(user=user)
            
            summary = {
                'total_achievements': achievements.count(),
                'level_breakdown': list(achievements.values('level').annotate(count=models.Count('id'))),
                'type_breakdown': list(achievements.values('achievement_type').annotate(count=models.Count('id'))),
                'recent_achievements': list(achievements.order_by('-created_at')[:5].values('title', 'level', 'created_at')),
            }
            cache.set(cache_key, summary, 300)  # 缓存5分钟
        
        return summary


class FitnessWorkoutSession(models.Model):
    """健身训练会话模型"""
    WORKOUT_TYPE_CHOICES = [
        ('strength', '力量训练'),
        ('cardio', '有氧运动'),
        ('flexibility', '柔韧性训练'),
        ('balance', '平衡训练'),
        ('mixed', '混合训练'),
    ]
    
    INTENSITY_CHOICES = [
        ('light', '轻度'),
        ('moderate', '中度'),
        ('intense', '高强度'),
        ('extreme', '极限'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES, verbose_name='训练类型')
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, verbose_name='强度等级')
    duration_minutes = models.IntegerField(verbose_name='训练时长(分钟)')
    calories_burned = models.IntegerField(default=0, verbose_name='消耗卡路里')
    heart_rate_avg = models.IntegerField(default=0, verbose_name='平均心率')
    heart_rate_max = models.IntegerField(default=0, verbose_name='最大心率')
    exercises = models.JSONField(default=list, verbose_name='训练动作')
    notes = models.TextField(blank=True, null=True, verbose_name='训练笔记')
    audio_recording_url = models.URLField(blank=True, null=True, verbose_name='喘息录音')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='训练时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '健身训练'
        verbose_name_plural = '健身训练'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class CodeWorkoutSession(models.Model):
    """代码训练会话模型"""
    WORKOUT_TYPE_CHOICES = [
        ('pull_up', '引体向上(原生JS)'),
        ('plank', '平板支撑(拒绝AI)'),
        ('squat', '深蹲(重构函数)'),
        ('push_up', '俯卧撑(手写算法)'),
        ('burpee', '波比跳(调试代码)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPE_CHOICES, verbose_name='训练类型')
    duration_seconds = models.IntegerField(verbose_name='训练时长(秒)')
    difficulty_level = models.IntegerField(default=1, verbose_name='难度等级')
    code_snippet = models.TextField(blank=True, null=True, verbose_name='代码片段')
    ai_rejection_count = models.IntegerField(default=0, verbose_name='拒绝AI次数')
    manual_code_lines = models.IntegerField(default=0, verbose_name='手写代码行数')
    refactored_functions = models.IntegerField(default=0, verbose_name='重构函数数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='训练时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '代码训练'
        verbose_name_plural = '代码训练'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_workout_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ExhaustionProof(models.Model):
    """力竭证明NFT模型"""
    PROOF_TYPE_CHOICES = [
        ('fitness', '健身力竭'),
        ('coding', '编程力竭'),
        ('mental', '精神力竭'),
        ('mixed', '混合力竭'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    proof_type = models.CharField(max_length=20, choices=PROOF_TYPE_CHOICES, verbose_name='证明类型')
    title = models.CharField(max_length=200, verbose_name='证明标题')
    description = models.TextField(verbose_name='证明描述')
    heart_rate_data = models.JSONField(default=dict, verbose_name='心率数据')
    audio_recording_url = models.URLField(blank=True, null=True, verbose_name='录音文件')
    nft_metadata = models.JSONField(default=dict, verbose_name='NFT元数据')
    nft_token_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='NFT代币ID')
    blockchain_tx_hash = models.CharField(max_length=200, blank=True, null=True, verbose_name='区块链交易哈希')
    is_minted = models.BooleanField(default=False, verbose_name='是否已铸造')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '力竭证明'
        verbose_name_plural = '力竭证明'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_proof_type_display()} - {self.title}"


class AIDependencyMeter(models.Model):
    """AI依赖度仪表模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    total_code_lines = models.IntegerField(default=0, verbose_name='总代码行数')
    ai_generated_lines = models.IntegerField(default=0, verbose_name='AI生成代码行数')
    manual_code_lines = models.IntegerField(default=0, verbose_name='手写代码行数')
    ai_rejection_count = models.IntegerField(default=0, verbose_name='拒绝AI次数')
    dependency_score = models.FloatField(default=0.0, verbose_name='依赖度评分')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = 'AI依赖度仪表'
        verbose_name_plural = 'AI依赖度仪表'
    
    def __str__(self):
        return f"{self.user.username} - 依赖度: {self.dependency_score:.2f}%"
    
    def calculate_dependency_score(self):
        """计算AI依赖度评分"""
        if self.total_code_lines == 0:
            return 0.0
        return (self.ai_generated_lines / self.total_code_lines) * 100


class CoPilotCollaboration(models.Model):
    """AI协作声明模型"""
    COLLABORATION_TYPE_CHOICES = [
        ('skeleton', '骨架代码'),
        ('muscle', '肌肉代码'),
        ('nervous', '神经系统'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    collaboration_type = models.CharField(max_length=20, choices=COLLABORATION_TYPE_CHOICES, verbose_name='协作类型')
    original_code = models.TextField(verbose_name='原始代码')
    ai_generated_code = models.TextField(verbose_name='AI生成代码')
    final_code = models.TextField(verbose_name='最终代码')
    project_name = models.CharField(max_length=200, verbose_name='项目名称')
    description = models.TextField(blank=True, null=True, verbose_name='协作描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI协作声明'
        verbose_name_plural = 'AI协作声明'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_collaboration_type_display()} - {self.project_name}"


class DailyWorkoutChallenge(models.Model):
    """每日训练挑战模型"""
    CHALLENGE_TYPE_CHOICES = [
        ('fitness', '健身挑战'),
        ('coding', '编程挑战'),
        ('mixed', '混合挑战'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPE_CHOICES, verbose_name='挑战类型')
    date = models.DateField(auto_now_add=True, verbose_name='挑战日期')
    tasks = models.JSONField(default=list, verbose_name='挑战任务')
    completed_tasks = models.JSONField(default=list, verbose_name='完成任务')
    total_score = models.IntegerField(default=0, verbose_name='总得分')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    reward_unlocked = models.BooleanField(default=False, verbose_name='是否解锁奖励')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '每日训练挑战'
        verbose_name_plural = '每日训练挑战'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_challenge_type_display()} - {self.date}"


class PainCurrency(models.Model):
    """痛苦货币模型"""
    CURRENCY_TYPE_CHOICES = [
        ('exhaustion', '力竭币'),
        ('rejection', '拒绝币'),
        ('manual', '手写币'),
        ('breakthrough', '突破币'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    currency_type = models.CharField(max_length=20, choices=CURRENCY_TYPE_CHOICES, verbose_name='货币类型')
    amount = models.IntegerField(default=0, verbose_name='数量')
    total_earned = models.IntegerField(default=0, verbose_name='总获得')
    total_spent = models.IntegerField(default=0, verbose_name='总消费')
    last_earned = models.DateTimeField(auto_now=True, verbose_name='最后获得时间')
    
    class Meta:
        unique_together = ['user', 'currency_type']
        verbose_name = '痛苦货币'
        verbose_name_plural = '痛苦货币'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_currency_type_display()}: {self.amount}"


class WorkoutDashboard(models.Model):
    """训练仪表盘模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    total_workouts = models.IntegerField(default=0, verbose_name='总训练次数')
    total_duration = models.IntegerField(default=0, verbose_name='总训练时长(分钟)')
    total_calories = models.IntegerField(default=0, verbose_name='总消耗卡路里')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    favorite_workout = models.CharField(max_length=50, blank=True, null=True, verbose_name='最爱训练')
    weekly_stats = models.JSONField(default=dict, verbose_name='周统计')
    monthly_stats = models.JSONField(default=dict, verbose_name='月统计')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = '训练仪表盘'
        verbose_name_plural = '训练仪表盘'
    
    def __str__(self):
        return f"{self.user.username} - 训练仪表盘"


class TrainingPlan(models.Model):
    """周训练计划模型"""
    PLAN_VISIBILITY_CHOICES = [
        ('private', '私有'),
        ('public', '公开'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=200, verbose_name='计划名称')
    mode = models.CharField(max_length=50, default='五分化', verbose_name='训练模式')
    cycle_weeks = models.IntegerField(default=8, verbose_name='周期(周)')
    week_schedule = models.JSONField(default=list, verbose_name='周安排')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    visibility = models.CharField(max_length=10, choices=PLAN_VISIBILITY_CHOICES, default='private', verbose_name='可见性')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        ordering = ['-updated_at']
        verbose_name = '训练计划'
        verbose_name_plural = '训练计划'
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class DesireDashboard(models.Model):
    """欲望仪表盘模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    current_desire_level = models.IntegerField(default=50, verbose_name='当前欲望浓度')
    total_desires = models.IntegerField(default=0, verbose_name='总欲望数')
    fulfilled_desires = models.IntegerField(default=0, verbose_name='已满足欲望数')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = '欲望仪表盘'
        verbose_name_plural = '欲望仪表盘'
    
    def __str__(self):
        return f"{self.user.username} - 欲望浓度: {self.current_desire_level}%"


class DesireItem(models.Model):
    """欲望项目模型"""
    DESIRE_TYPE_CHOICES = [
        ('material', '物质欲望'),
        ('social', '社交欲望'),
        ('escape', '逃避欲望'),
        ('achievement', '成就欲望'),
        ('recognition', '认可欲望'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    desire_type = models.CharField(max_length=20, choices=DESIRE_TYPE_CHOICES, verbose_name='欲望类型')
    title = models.CharField(max_length=200, verbose_name='欲望标题')
    description = models.TextField(blank=True, null=True, verbose_name='欲望描述')
    intensity = models.IntegerField(default=3, verbose_name='欲望强度(1-5)')
    is_fulfilled = models.BooleanField(default=False, verbose_name='是否已满足')
    fulfillment_condition = models.TextField(blank=True, null=True, verbose_name='满足条件')
    fulfillment_image_url = models.URLField(blank=True, null=True, verbose_name='兑现图片URL')
    ai_generated_image = models.TextField(blank=True, null=True, verbose_name='AI生成图片描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    fulfilled_at = models.DateTimeField(null=True, blank=True, verbose_name='满足时间')
    
    class Meta:
        ordering = ['-intensity', '-created_at']
        verbose_name = '欲望项目'
        verbose_name_plural = '欲望项目'
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_intensity_stars()})"
    
    def get_intensity_stars(self):
        """获取强度星级显示"""
        return '★' * self.intensity + '☆' * (5 - self.intensity)


class DesireFulfillment(models.Model):
    """欲望兑现记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    desire = models.ForeignKey(DesireItem, on_delete=models.CASCADE, verbose_name='欲望项目')
    task_completed = models.CharField(max_length=200, verbose_name='完成任务')
    task_details = models.TextField(blank=True, null=True, verbose_name='任务详情')
    fulfillment_image_url = models.URLField(blank=True, null=True, verbose_name='兑现图片URL')
    ai_prompt = models.TextField(verbose_name='AI生成提示词')
    ai_generated_image = models.TextField(blank=True, null=True, verbose_name='AI生成图片')
    satisfaction_level = models.IntegerField(default=5, verbose_name='满足度(1-10)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='兑现时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '欲望兑现记录'
        verbose_name_plural = '欲望兑现记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.desire.title} 兑现记录"


# VanityOS 欲望驱动的开发者激励系统模型

class VanityWealth(models.Model):
    """虚拟财富模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    virtual_wealth = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name='虚拟财富')
    code_lines = models.IntegerField(default=0, verbose_name='代码行数')
    page_views = models.IntegerField(default=0, verbose_name='网站访问量')
    donations = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='赞助金额')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新')
    
    class Meta:
        verbose_name = '虚拟财富'
        verbose_name_plural = '虚拟财富'
    
    def __str__(self):
        return f"{self.user.username} - 虚拟财富: {self.virtual_wealth}"
    
    def calculate_wealth(self):
        """计算虚拟财富"""
        from decimal import Decimal
        code_wealth = Decimal(str(self.code_lines * 0.01))
        page_wealth = Decimal(str(self.page_views * 0.001))
        donation_wealth = Decimal(str(self.donations))
        self.virtual_wealth = code_wealth + page_wealth + donation_wealth
        return self.virtual_wealth


class SinPoints(models.Model):
    """罪恶积分模型"""
    ACTION_CHOICES = [
        ('code_line', '提交代码行'),
        ('reject_ai', '拒绝AI补全'),
        ('deep_work', '深度工作'),
        ('donation', '收到赞助'),
        ('manual_code', '手写代码'),
        ('refactor', '重构代码'),
        ('debug', '调试代码'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='行为类型')
    points_earned = models.IntegerField(verbose_name='获得积分')
    metadata = models.JSONField(default=dict, verbose_name='元数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='获得时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '罪恶积分'
        verbose_name_plural = '罪恶积分'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.points_earned}积分"


class Sponsor(models.Model):
    """赞助者模型"""
    EFFECT_CHOICES = [
        ('golden-bling', '金色闪耀'),
        ('diamond-sparkle', '钻石闪烁'),
        ('platinum-glow', '白金光芒'),
        ('silver-shine', '银色光辉'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='赞助者姓名')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='赞助金额')
    message = models.TextField(blank=True, null=True, verbose_name='赞助留言')
    effect = models.CharField(max_length=20, choices=EFFECT_CHOICES, default='golden-bling', verbose_name='特效类型')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='赞助时间')
    
    class Meta:
        ordering = ['-amount', '-created_at']
        verbose_name = '赞助者'
        verbose_name_plural = '赞助者'
    
    def __str__(self):
        display_name = "匿名土豪" if self.is_anonymous else self.name
        return f"{display_name} - {self.amount}元"


class VanityTask(models.Model):
    """欲望驱动待办任务模型"""
    TASK_TYPE_CHOICES = [
        ('code_refactor', '代码重构'),
        ('bug_fix', '修复Bug'),
        ('feature_dev', '功能开发'),
        ('blog_write', '写技术博客'),
        ('code_review', '代码审查'),
        ('testing', '测试编写'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='任务标题')
    description = models.TextField(blank=True, null=True, verbose_name='任务描述')
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name='任务类型')
    difficulty = models.IntegerField(default=1, verbose_name='难度等级(1-10)')
    reward_value = models.IntegerField(default=0, verbose_name='奖励价值')
    reward_description = models.CharField(max_length=200, verbose_name='奖励描述')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '欲望任务'
        verbose_name_plural = '欲望任务'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def calculate_reward(self):
        """根据难度计算奖励"""
        self.reward_value = self.difficulty * 10
        return self.reward_value


class BasedDevAvatar(models.Model):
    """反程序员形象模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    avatar_image = models.ImageField(upload_to='vanity_avatars/', verbose_name='头像图片')
    code_snippet = models.TextField(verbose_name='代码片段')
    caption = models.CharField(max_length=500, verbose_name='配文')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '反程序员形象'
        verbose_name_plural = '反程序员形象'
    
    def __str__(self):
        return f"{self.user.username} - {self.caption[:50]}"


# class TravelGuide(models.Model):
#     """旅游攻略模型"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
#     destination = models.CharField(max_length=200, verbose_name='目的地')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
#     
#     # 攻略内容
#     must_visit_attractions = models.JSONField(default=list, verbose_name='必去景点')
#     food_recommendations = models.JSONField(default=list, verbose_name='美食推荐')
#     transportation_guide = models.JSONField(default=dict, verbose_name='交通指南')
#     hidden_gems = models.JSONField(default=list, verbose_name='隐藏玩法')
#     weather_info = models.JSONField(default=dict, verbose_name='天气信息')
#     
#     # Overview信息字段
#     destination_info = models.JSONField(default=dict, verbose_name='目的地基本信息')
#     currency_info = models.JSONField(default=dict, verbose_name='汇率信息') 
#     timezone_info = models.JSONField(default=dict, verbose_name='时区信息')
#     
#     best_time_to_visit = models.TextField(blank=True, null=True, verbose_name='最佳旅行时间')
#     budget_estimate = models.JSONField(default=dict, verbose_name='预算估算')
#     travel_tips = models.JSONField(default=list, verbose_name='旅行贴士')
#     
#     # 详细攻略
#     detailed_guide = models.JSONField(default=dict, verbose_name='详细攻略')
#     daily_schedule = models.JSONField(default=list, verbose_name='每日行程')
#     activity_timeline = models.JSONField(default=list, verbose_name='活动时间线')
#     cost_breakdown = models.JSONField(default=dict, verbose_name='费用明细')
#     
#     # 个性化设置
#     travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
#     budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
#     budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
#     budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
#     budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
#     travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
#     interests = models.JSONField(default=list, verbose_name='兴趣标签')
#     
#     # 状态
#     is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
#     is_exported = models.BooleanField(default=False, verbose_name='是否已导出')
#     
#     # 缓存相关
#     is_cached = models.BooleanField(default=False, verbose_name='是否缓存数据')
#     cache_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='缓存来源')
#     cache_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='缓存过期时间')
#     api_used = models.CharField(max_length=50, default='deepseek', verbose_name='使用的API')
#     generation_mode = models.CharField(max_length=20, default='standard', verbose_name='生成模式')
#     
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = '旅游攻略'
#         verbose_name_plural = '旅游攻略'
#     
#     def __str__(self):
#         return f"{self.user.username} - {self.destination}"
#     
#     def get_attractions_count(self):
#         return len(self.must_visit_attractions)
#     
#     def get_food_count(self):
#         return len(self.food_recommendations)
#     
#     def get_hidden_gems_count(self):
#         return len(self.hidden_gems)
#     
#     def is_cache_valid(self):
#         """检查缓存是否有效"""
#         if not self.is_cached or not self.cache_expires_at:
#             return False
#         from django.utils import timezone
#         return timezone.now() < self.cache_expires_at
#     
#     def get_cache_status(self):
#         """获取缓存状态"""
#         if not self.is_cached:
#             return 'not_cached'
#         if self.is_cache_valid():
#             return 'valid'
#         return 'expired'


# class TravelGuideCache(models.Model):
#     """旅游攻略缓存模型"""
#     CACHE_SOURCE_CHOICES = [
#         ('standard_api', '标准API生成'),
#         ('fast_api', '快速API生成'),
#         ('cached_data', '缓存数据'),
#         ('fallback_data', '备用数据'),
#     ]
#     
#     API_SOURCE_CHOICES = [
#         ('deepseek', 'DeepSeek API'),
#         ('openai', 'OpenAI API'),
#         ('claude', 'Claude API'),
#         ('gemini', 'Gemini API'),
#         ('free_api_1', '免费API 1'),
#         ('free_api_2', '免费API 2'),
#         ('free_api_3', '免费API 3'),
#         ('fallback', '备用数据'),
#     ]
#     
#     # 缓存键（用于查找相同条件的攻略）
#     destination = models.CharField(max_length=200, verbose_name='目的地')
#     travel_style = models.CharField(max_length=50, verbose_name='旅行风格')
#     budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
#     budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
#     budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
#     budget_range = models.CharField(max_length=50, verbose_name='预算范围')
#     travel_duration = models.CharField(max_length=50, verbose_name='旅行时长')
#     interests_hash = models.CharField(max_length=64, verbose_name='兴趣标签哈希')
#     
#     # 缓存数据
#     guide_data = models.JSONField(verbose_name='攻略数据')
#     api_used = models.CharField(max_length=50, choices=API_SOURCE_CHOICES, verbose_name='使用的API')
#     cache_source = models.CharField(max_length=50, choices=CACHE_SOURCE_CHOICES, verbose_name='缓存来源')
#     
#     # 缓存元数据
#     generation_time = models.FloatField(verbose_name='生成时间(秒)')
#     data_quality_score = models.FloatField(default=0.0, verbose_name='数据质量评分')
#     usage_count = models.IntegerField(default=0, verbose_name='使用次数')
#     
#     # 时间戳
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     expires_at = models.DateTimeField(verbose_name='过期时间')
#     last_accessed = models.DateTimeField(auto_now=True, verbose_name='最后访问时间')
#     
#     class Meta:
#         unique_together = ['destination', 'travel_style', 'budget_min', 'budget_max', 'budget_range', 'travel_duration', 'interests_hash']
#         ordering = ['-last_accessed']
#         verbose_name = '旅游攻略缓存'
#         verbose_name_plural = '旅游攻略缓存'
#         indexes = [
#             models.Index(fields=['destination', 'travel_style', 'budget_min', 'budget_max', 'travel_duration']),
#             models.Index(fields=['expires_at']),
#             models.Index(fields=['api_used']),
#         ]
#     
#     def __str__(self):
#         return f"{self.destination} - {self.travel_style} - {self.api_used}"
#     
#     def is_expired(self):
#         """检查缓存是否过期"""
#         from django.utils import timezone
#         return timezone.now() > self.expires_at
#     
#     def increment_usage(self):
#         """增加使用次数"""
#         self.usage_count += 1
#         self.save(update_fields=['usage_count', 'last_accessed'])
#     
#     def get_cache_key(self):
#         """获取缓存键"""
#         return f"{self.destination}_{self.travel_style}_{self.budget_min}_{self.budget_max}_{self.travel_duration}_{self.interests_hash}"


class TravelDestination(models.Model):
    """旅游目的地模型"""
    name = models.CharField(max_length=200, verbose_name='目的地名称')
    country = models.CharField(max_length=100, verbose_name='国家')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='地区')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片链接')
    popularity_score = models.FloatField(default=0.0, verbose_name='热度评分')
    best_season = models.CharField(max_length=100, blank=True, null=True, verbose_name='最佳季节')
    average_cost = models.CharField(max_length=50, blank=True, null=True, verbose_name='平均花费')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-popularity_score']
        verbose_name = '旅游目的地'
        verbose_name_plural = '旅游目的地'
    
    def __str__(self):
        return f"{self.name}, {self.country}"


# class TravelReview(models.Model):
#     """旅游攻略评价模型"""
#     travel_guide = models.ForeignKey(TravelGuide, on_delete=models.CASCADE, verbose_name='旅游攻略')
#     user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
#     rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
#     comment = models.TextField(blank=True, null=True, verbose_name='评价内容')
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
#     
#     class Meta:
#         unique_together = ['travel_guide', 'user']
#         ordering = ['-created_at']
#         verbose_name = '旅游攻略评价'
#         verbose_name_plural = '旅游攻略评价'
#     
#     def __str__(self):
#         return f"{self.user.username} - {self.travel_guide.destination} - {self.rating}星"


class JobSearchRequest(models.Model):
    """自动求职请求模型"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
        ('cancelled', '已取消'),
    ]
    
    JOB_TYPE_CHOICES = [
        ('full_time', '全职'),
        ('part_time', '兼职'),
        ('internship', '实习'),
        ('freelance', '自由职业'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('fresh', '应届生'),
        ('1-3', '1-3年'),
        ('3-5', '3-5年'),
        ('5-10', '5-10年'),
        ('10+', '10年以上'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    job_title = models.CharField(max_length=200, verbose_name='职位名称')
    location = models.CharField(max_length=200, verbose_name='工作地点')
    min_salary = models.IntegerField(verbose_name='最低薪资(月薪)')
    max_salary = models.IntegerField(verbose_name='最高薪资(月薪)')
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time', verbose_name='工作类型')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='1-3', verbose_name='经验要求')
    keywords = models.JSONField(default=list, verbose_name='关键词')
    company_size = models.CharField(max_length=50, blank=True, null=True, verbose_name='公司规模')
    industry = models.CharField(max_length=100, blank=True, null=True, verbose_name='行业')
    education_level = models.CharField(max_length=50, blank=True, null=True, verbose_name='学历要求')
    
    # 自动投递设置
    auto_apply = models.BooleanField(default=True, verbose_name='自动投递')
    max_applications = models.IntegerField(default=50, verbose_name='最大投递数量')
    application_interval = models.IntegerField(default=30, verbose_name='投递间隔(秒)')
    
    # 状态和结果
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    total_jobs_found = models.IntegerField(default=0, verbose_name='找到职位数')
    total_applications_sent = models.IntegerField(default=0, verbose_name='投递简历数')
    success_rate = models.FloatField(default=0.0, verbose_name='成功率')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    # 错误信息
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '求职请求'
        verbose_name_plural = '求职请求'
    
    def __str__(self):
        return f"{self.user.username} - {self.job_title} - {self.location}"
    
    def get_salary_range(self):
        return f"{self.min_salary}K-{self.max_salary}K"
    
    def get_progress_percentage(self):
        if self.max_applications == 0:
            return 0
        return min(100, (self.total_applications_sent / self.max_applications) * 100)


class JobApplication(models.Model):
    """职位申请记录模型"""
    STATUS_CHOICES = [
        ('applied', '已投递'),
        ('viewed', '已查看'),
        ('contacted', '已联系'),
        ('interview', '面试邀请'),
        ('rejected', '已拒绝'),
        ('accepted', '已录用'),
    ]
    
    job_search_request = models.ForeignKey(JobSearchRequest, on_delete=models.CASCADE, related_name='applications', verbose_name='求职请求')
    job_id = models.CharField(max_length=100, verbose_name='职位ID')
    job_title = models.CharField(max_length=200, verbose_name='职位名称')
    company_name = models.CharField(max_length=200, verbose_name='公司名称')
    company_logo = models.URLField(blank=True, null=True, verbose_name='公司Logo')
    location = models.CharField(max_length=200, verbose_name='工作地点')
    salary_range = models.CharField(max_length=100, verbose_name='薪资范围')
    job_description = models.TextField(blank=True, null=True, verbose_name='职位描述')
    requirements = models.JSONField(default=list, verbose_name='职位要求')
    benefits = models.JSONField(default=list, verbose_name='福利待遇')
    
    # 申请状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied', verbose_name='申请状态')
    application_time = models.DateTimeField(auto_now_add=True, verbose_name='投递时间')
    response_time = models.DateTimeField(null=True, blank=True, verbose_name='回复时间')
    
    # 平台信息
    platform = models.CharField(max_length=50, default='boss', verbose_name='招聘平台')
    job_url = models.URLField(verbose_name='职位链接')
    
    # 匹配度
    match_score = models.FloatField(default=0.0, verbose_name='匹配度评分')
    match_reasons = models.JSONField(default=list, verbose_name='匹配原因')
    
    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        ordering = ['-application_time']
        verbose_name = '职位申请'
        verbose_name_plural = '职位申请'
    
    def __str__(self):
        return f"{self.job_title} - {self.company_name}"
    
    def get_status_color(self):
        status_colors = {
            'applied': 'primary',
            'viewed': 'info',
            'contacted': 'warning',
            'interview': 'success',
            'rejected': 'danger',
            'accepted': 'success',
        }
        return status_colors.get(self.status, 'secondary')


class JobSearchProfile(models.Model):
    """求职者资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基本信息
    name = models.CharField(max_length=100, verbose_name='姓名')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    avatar = models.ImageField(upload_to='job_profiles/', blank=True, null=True, verbose_name='头像')
    
    # 求职信息
    current_position = models.CharField(max_length=100, blank=True, null=True, verbose_name='当前职位')
    years_of_experience = models.IntegerField(default=0, verbose_name='工作年限')
    education_level = models.CharField(max_length=50, blank=True, null=True, verbose_name='最高学历')
    school = models.CharField(max_length=100, blank=True, null=True, verbose_name='毕业院校')
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业')
    
    # 技能和期望
    skills = models.JSONField(default=list, verbose_name='技能标签')
    expected_salary_min = models.IntegerField(default=0, verbose_name='期望最低薪资')
    expected_salary_max = models.IntegerField(default=0, verbose_name='期望最高薪资')
    preferred_locations = models.JSONField(default=list, verbose_name='期望工作地点')
    preferred_industries = models.JSONField(default=list, verbose_name='期望行业')
    
    # 简历信息
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True, verbose_name='简历文件')
    resume_text = models.TextField(blank=True, null=True, verbose_name='简历文本')
    
    # 平台账号
    boss_account = models.CharField(max_length=100, blank=True, null=True, verbose_name='Boss直聘账号')
    zhilian_account = models.CharField(max_length=100, blank=True, null=True, verbose_name='智联招聘账号')
    lagou_account = models.CharField(max_length=100, blank=True, null=True, verbose_name='拉勾网账号')
    
    # 设置
    auto_apply_enabled = models.BooleanField(default=True, verbose_name='启用自动投递')
    notification_enabled = models.BooleanField(default=True, verbose_name='启用通知')
    privacy_level = models.CharField(max_length=20, default='public', verbose_name='隐私级别')
    
    # 统计信息
    total_applications = models.IntegerField(default=0, verbose_name='总投递数')
    total_interviews = models.IntegerField(default=0, verbose_name='总面试数')
    total_offers = models.IntegerField(default=0, verbose_name='总Offer数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '求职者资料'
        verbose_name_plural = '求职者资料'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def get_expected_salary_range(self):
        if self.expected_salary_min and self.expected_salary_max:
            return f"{self.expected_salary_min}K-{self.expected_salary_max}K"
        return "未设置"
    
    def get_success_rate(self):
        if self.total_applications == 0:
            return 0
        return round((self.total_offers / self.total_applications) * 100, 2)


class JobSearchStatistics(models.Model):
    """求职统计模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    date = models.DateField(auto_now_add=True, verbose_name='统计日期')
    
    # 每日统计
    applications_sent = models.IntegerField(default=0, verbose_name='投递简历数')
    jobs_viewed = models.IntegerField(default=0, verbose_name='查看职位数')
    interviews_received = models.IntegerField(default=0, verbose_name='收到面试数')
    offers_received = models.IntegerField(default=0, verbose_name='收到Offer数')
    
    # 平台统计
    boss_applications = models.IntegerField(default=0, verbose_name='Boss直聘投递数')
    zhilian_applications = models.IntegerField(default=0, verbose_name='智联招聘投递数')
    lagou_applications = models.IntegerField(default=0, verbose_name='拉勾网投递数')
    
    # 成功率
    response_rate = models.FloatField(default=0.0, verbose_name='回复率')
    interview_rate = models.FloatField(default=0.0, verbose_name='面试率')
    offer_rate = models.FloatField(default=0.0, verbose_name='Offer率')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = '求职统计'
        verbose_name_plural = '求职统计'
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"


class PDFConversionRecord(models.Model):
    """PDF转换记录模型"""
    CONVERSION_TYPE_CHOICES = [
        ('pdf_to_word', 'PDF转Word'),
        ('word_to_pdf', 'Word转PDF'),
        ('pdf_to_image', 'PDF转图片'),
        ('image_to_pdf', '图片转PDF'),
        ('pdf_to_text', 'PDF转文本'),
        ('text_to_pdf', '文本转PDF'),
    ]
    
    STATUS_CHOICES = [
        ('success', '成功'),
        ('failed', '失败'),
        ('processing', '处理中'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    conversion_type = models.CharField(max_length=20, choices=CONVERSION_TYPE_CHOICES, verbose_name='转换类型')
    original_filename = models.CharField(max_length=255, verbose_name='原始文件名')
    output_filename = models.CharField(max_length=255, blank=True, null=True, verbose_name='输出文件名')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    conversion_time = models.FloatField(default=0.0, verbose_name='转换时间(秒)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name='转换状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    download_url = models.URLField(blank=True, null=True, verbose_name='下载链接')
    satisfaction_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='满意度评分(1-5)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'PDF转换记录'
        verbose_name_plural = 'PDF转换记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_conversion_type_display()} - {self.original_filename}"
    
    def get_file_size_display(self):
        """获取文件大小的可读格式"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_conversion_time_display(self):
        """获取转换时间的可读格式"""
        if self.conversion_time < 1:
            return f"{self.conversion_time * 1000:.0f}ms"
        else:
            return f"{self.conversion_time:.1f}s"


# 塔罗牌相关模型已移动到 tarot_models.py


class FoodRandomizer(models.Model):
    """食物随机选择器模型"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '夜宵'),
    ]
    
    CUISINE_CHOICES = [
        ('chinese', '中餐'),
        ('western', '西餐'),
        ('japanese', '日料'),
        ('korean', '韩料'),
        ('thai', '泰餐'),
        ('indian', '印度菜'),
        ('italian', '意大利菜'),
        ('french', '法餐'),
        ('mexican', '墨西哥菜'),
        ('mixed', '混合'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name='餐种')
    cuisine_preference = models.CharField(max_length=20, choices=CUISINE_CHOICES, default='mixed', verbose_name='菜系偏好')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '食物随机选择器'
        verbose_name_plural = '食物随机选择器'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()}"


class FoodItem(models.Model):
    """食物项目模型"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '夜宵'),
    ]
    
    CUISINE_CHOICES = [
        ('chinese', '中餐'),
        ('western', '西餐'),
        ('japanese', '日料'),
        ('korean', '韩料'),
        ('thai', '泰餐'),
        ('indian', '印度菜'),
        ('italian', '意大利菜'),
        ('french', '法餐'),
        ('mexican', '墨西哥菜'),
        ('mixed', '混合'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', '简单'),
        ('medium', '中等'),
        ('hard', '困难'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='食物名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    meal_types = models.JSONField(default=list, verbose_name='适用餐种')
    cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES, verbose_name='菜系')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='制作难度')
    cooking_time = models.IntegerField(default=30, verbose_name='制作时间(分钟)')
    ingredients = models.JSONField(default=list, verbose_name='主要食材')
    tags = models.JSONField(default=list, verbose_name='标签')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片链接')
    recipe_url = models.URLField(blank=True, null=True, verbose_name='食谱链接')
    popularity_score = models.FloatField(default=0.0, verbose_name='受欢迎度')
    
    # 营养信息
    calories = models.IntegerField(default=0, verbose_name='卡路里(千卡)')
    protein = models.FloatField(default=0.0, verbose_name='蛋白质(克)')
    fat = models.FloatField(default=0.0, verbose_name='脂肪(克)')
    carbohydrates = models.FloatField(default=0.0, verbose_name='碳水化合物(克)')
    fiber = models.FloatField(default=0.0, verbose_name='膳食纤维(克)')
    sugar = models.FloatField(default=0.0, verbose_name='糖分(克)')
    sodium = models.FloatField(default=0.0, verbose_name='钠(毫克)')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '食物项目'
        verbose_name_plural = '食物项目'
        ordering = ['-popularity_score', 'name']
    
    def __str__(self):
        return self.name
    
    def get_meal_types_display(self):
        return ', '.join([dict(FoodRandomizer.MEAL_TYPE_CHOICES)[meal_type] for meal_type in self.meal_types])


class FoodRandomizationSession(models.Model):
    """食物随机选择会话模型"""
    STATUS_CHOICES = [
        ('active', '进行中'),
        ('paused', '已暂停'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    meal_type = models.CharField(max_length=20, choices=FoodRandomizer.MEAL_TYPE_CHOICES, verbose_name='餐种')
    cuisine_preference = models.CharField(max_length=20, choices=FoodRandomizer.CUISINE_CHOICES, verbose_name='菜系偏好')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    
    # 随机过程数据
    animation_duration = models.IntegerField(default=3000, verbose_name='动画时长(毫秒)')
    total_cycles = models.IntegerField(default=0, verbose_name='总循环次数')
    current_cycle = models.IntegerField(default=0, verbose_name='当前循环次数')
    
    # 结果
    selected_food = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='选中的食物')
    alternative_foods = models.JSONField(default=list, verbose_name='备选食物')
    
    # 时间戳
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    paused_at = models.DateTimeField(null=True, blank=True, verbose_name='暂停时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '食物随机选择会话'
        verbose_name_plural = '食物随机选择会话'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} - {self.get_status_display()}"
    
    def get_duration(self):
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.paused_at:
            return (self.paused_at - self.started_at).total_seconds()
        else:
            return (timezone.now() - self.started_at).total_seconds()


class FoodHistory(models.Model):
    """食物选择历史记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    session = models.ForeignKey(FoodRandomizationSession, on_delete=models.CASCADE, verbose_name='随机会话')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, verbose_name='食物项目')
    meal_type = models.CharField(max_length=20, choices=FoodRandomizer.MEAL_TYPE_CHOICES, verbose_name='餐种')
    rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
    feedback = models.TextField(blank=True, null=True, verbose_name='反馈')
    was_cooked = models.BooleanField(default=False, verbose_name='是否制作')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='选择时间')
    
    class Meta:
        verbose_name = '食物选择历史'
        verbose_name_plural = '食物选择历史'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.food_item.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class CheckInCalendar(models.Model):
    """打卡日历模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkin_calendars')
    calendar_type = models.CharField(max_length=20, choices=[
        ('fitness', '健身'),
        ('diary', '日记'),
        ('guitar', '吉他')
    ])
    date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('completed', '已完成'),
        ('skipped', '跳过'),
        ('rest', '休息日')
    ], default='completed')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'calendar_type', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.get_calendar_type_display()} - {self.date}"


class CheckInDetail(models.Model):
    """打卡详情模型"""
    checkin = models.OneToOneField(CheckInCalendar, on_delete=models.CASCADE, related_name='detail')
    
    # 通用字段
    duration = models.IntegerField(help_text='持续时间（分钟）', null=True, blank=True)
    intensity = models.CharField(max_length=20, choices=[
        ('low', '低'),
        ('medium', '中'),
        ('high', '高')
    ], null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # 健身专用字段
    workout_type = models.CharField(max_length=50, choices=[
        ('strength', '力量训练'),
        ('cardio', '有氧训练'),
        ('yoga', '瑜伽'),
        ('hiit', '高强度间歇'),
        ('flexibility', '柔韧性训练'),
        ('other', '其他')
    ], null=True, blank=True)
    
    # 新增健身字段
    training_parts = models.JSONField(default=list, verbose_name='训练部位', help_text='如：胸、背、腿等')
    feeling_rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True, verbose_name='感受评分', help_text='1-5星评分')
    is_shared_to_community = models.BooleanField(default=False, verbose_name='是否分享到社区')
    
    # 日记专用字段
    mood = models.CharField(max_length=20, choices=[
        ('happy', '开心'),
        ('sad', '难过'),
        ('angry', '愤怒'),
        ('calm', '平静'),
        ('excited', '兴奋'),
        ('tired', '疲惫'),
        ('other', '其他')
    ], null=True, blank=True)
    weather = models.CharField(max_length=20, null=True, blank=True)
    
    # 吉他专用字段
    practice_type = models.CharField(max_length=50, choices=[
        ('chords', '和弦练习'),
        ('scales', '音阶练习'),
        ('songs', '歌曲练习'),
        ('theory', '乐理学习'),
        ('ear_training', '听力训练'),
        ('other', '其他')
    ], null=True, blank=True)
    song_name = models.CharField(max_length=100, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.checkin} - 详情"


class CheckInStreak(models.Model):
    """连续打卡记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkin_streaks')
    calendar_type = models.CharField(max_length=20, choices=[
        ('fitness', '健身'),
        ('diary', '日记'),
        ('guitar', '吉他')
    ])
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_checkin_date = models.DateField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'calendar_type']

    def __str__(self):
        return f"{self.user.username} - {self.get_calendar_type_display()} - 连续{self.current_streak}天"


class CheckInAchievement(models.Model):
    """打卡成就模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkin_achievements')
    calendar_type = models.CharField(max_length=20, choices=[
        ('fitness', '健身'),
        ('diary', '日记'),
        ('guitar', '吉他')
    ])
    achievement_type = models.CharField(max_length=50, choices=[
        ('streak_7', '连续7天'),
        ('streak_30', '连续30天'),
        ('streak_100', '连续100天'),
        ('total_50', '总计50次'),
        ('total_100', '总计100次'),
        ('total_365', '总计365次'),
        ('monthly_20', '月度20次'),
        ('monthly_25', '月度25次'),
        ('monthly_30', '月度30次')
    ])
    achieved_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['user', 'calendar_type', 'achievement_type']

    def __str__(self):
        return f"{self.user.username} - {self.get_calendar_type_display()} - {self.get_achievement_type_display()}"


class FoodPhotoBinding(models.Model):
    """食物照片绑定模型"""
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, verbose_name='食物项目')
    photo_name = models.CharField(max_length=255, verbose_name='照片文件名')
    photo_url = models.URLField(verbose_name='照片URL')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    # 绑定质量评估
    accuracy_score = models.FloatField(default=0.0, verbose_name='准确度评分')
    binding_source = models.CharField(max_length=50, default='manual', verbose_name='绑定来源', choices=[
        ('manual', '手动绑定'),
        ('auto', '自动匹配'),
        ('ai', 'AI推荐'),
    ])
    
    class Meta:
        unique_together = ['food_item', 'photo_name']
        verbose_name = '食物照片绑定'
        verbose_name_plural = '食物照片绑定'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.food_item.name} -> {self.photo_name}"


class FoodPhotoBindingHistory(models.Model):
    """食物照片绑定历史记录模型"""
    ACTION_CHOICES = [
        ('create', '创建绑定'),
        ('update', '更新绑定'),
        ('delete', '删除绑定'),
    ]
    
    binding = models.ForeignKey(FoodPhotoBinding, on_delete=models.CASCADE, related_name='history', verbose_name='绑定关系')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    old_photo_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='旧照片名')
    new_photo_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='新照片名')
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作者')
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '绑定历史记录'
        verbose_name_plural = '绑定历史记录'
        ordering = ['-performed_at']
    
    def __str__(self):
        return f"{self.binding.food_item.name} - {self.get_action_display()} - {self.performed_at.strftime('%Y-%m-%d %H:%M')}"


# MeeSomeone 人际档案系统模型

class LegacyRelationshipTag(models.Model):
    """关系标签模型"""
    TAG_TYPE_CHOICES = [
        ('predefined', '预定义标签'),
        ('custom', '自定义标签'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='标签名称')
    tag_type = models.CharField(max_length=20, choices=TAG_TYPE_CHOICES, default='predefined', verbose_name='标签类型')
    color = models.CharField(max_length=7, default='#9c27b0', verbose_name='标签颜色')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='创建者')
    is_global = models.BooleanField(default=True, verbose_name='是否全局标签')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '关系标签'
        verbose_name_plural = '关系标签'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class LegacyPersonProfile(models.Model):
    """人物档案模型"""
    IMPORTANCE_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]
    
    GENDER_CHOICES = [
        ('male', '男'),
        ('female', '女'),
        ('other', '其他'),
        ('unknown', '未知'),
    ]
    
    # 基础信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=100, verbose_name='姓名')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='昵称/备注名')
    avatar = models.ImageField(upload_to='lifegraph/avatars/', blank=True, null=True, verbose_name='头像')
    
    # 关系信息
    relationship_tags = models.ManyToManyField(LegacyRelationshipTag, blank=True, verbose_name='关系标签')
    first_met_date = models.DateField(blank=True, null=True, verbose_name='认识日期')
    first_met_location = models.CharField(max_length=200, blank=True, null=True, verbose_name='认识场景')
    importance_level = models.IntegerField(choices=IMPORTANCE_CHOICES, default=3, verbose_name='重要程度')
    
    # 个人背景信息
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unknown', verbose_name='性别')
    age = models.IntegerField(blank=True, null=True, verbose_name='年龄')
    occupation = models.CharField(max_length=100, blank=True, null=True, verbose_name='职业')
    company_school = models.CharField(max_length=200, blank=True, null=True, verbose_name='公司/学校')
    hometown = models.CharField(max_length=100, blank=True, null=True, verbose_name='家乡')
    
    # 特征和兴趣
    appearance_notes = models.TextField(blank=True, null=True, verbose_name='外貌特征')
    personality_traits = models.JSONField(default=list, verbose_name='性格特点')
    interests_hobbies = models.JSONField(default=list, verbose_name='兴趣爱好')
    habits_phrases = models.TextField(blank=True, null=True, verbose_name='习惯/口头禅')
    
    # 重要日期
    birthday = models.DateField(blank=True, null=True, verbose_name='生日')
    important_dates = models.JSONField(default=dict, verbose_name='重要日期')
    
    # 联系方式（谨慎使用）
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    social_accounts = models.JSONField(default=dict, verbose_name='社交媒体账号')
    
    # 共同好友
    mutual_friends = models.ManyToManyField('self', blank=True, symmetrical=False, verbose_name='共同好友')
    
    # 统计信息
    interaction_count = models.IntegerField(default=0, verbose_name='互动次数')
    last_interaction_date = models.DateField(blank=True, null=True, verbose_name='最后互动日期')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '人物档案'
        verbose_name_plural = '人物档案'
        ordering = ['-importance_level', '-last_interaction_date', 'name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        display_name = self.nickname if self.nickname else self.name
        return f"{self.user.username} - {display_name}"
    
    def get_age_display(self):
        """获取年龄显示"""
        if self.age:
            return f"{self.age}岁"
        elif self.birthday:
            from datetime import date
            today = date.today()
            age = today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
            return f"{age}岁"
        return "未知"
    
    def get_relationship_tags_display(self):
        """获取关系标签显示"""
        return ', '.join([tag.name for tag in self.relationship_tags.all()])
    
    def get_days_since_last_interaction(self):
        """获取距离上次互动的天数"""
        if not self.last_interaction_date:
            return None
        from datetime import date
        return (date.today() - self.last_interaction_date).days
    
    def increment_interaction_count(self):
        """增加互动次数"""
        self.interaction_count += 1
        self.last_interaction_date = timezone.now().date()
        self.save(update_fields=['interaction_count', 'last_interaction_date'])


class LegacyInteraction(models.Model):
    """互动记录模型"""
    INTERACTION_TYPE_CHOICES = [
        ('meeting', '见面'),
        ('phone_call', '电话'),
        ('video_call', '视频通话'),
        ('message', '消息聊天'),
        ('email', '邮件'),
        ('social_media', '社交媒体'),
        ('event', '共同活动'),
        ('gift', '送礼/收礼'),
        ('help', '互相帮助'),
        ('other', '其他'),
    ]
    
    MOOD_CHOICES = [
        ('very_happy', '非常开心'),
        ('happy', '开心'),
        ('neutral', '一般'),
        ('disappointed', '失望'),
        ('sad', '难过'),
        ('angry', '生气'),
        ('confused', '困惑'),
        ('excited', '兴奋'),
        ('nervous', '紧张'),
        ('grateful', '感激'),
    ]
    
    # 基础信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    person = models.ForeignKey(LegacyPersonProfile, on_delete=models.CASCADE, related_name='interactions', verbose_name='相关人物')
    
    # 互动详情
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES, verbose_name='互动类型')
    date = models.DateField(verbose_name='日期')
    time = models.TimeField(blank=True, null=True, verbose_name='时间')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='地点')
    
    # 内容记录
    title = models.CharField(max_length=200, verbose_name='标题/摘要')
    content = models.TextField(verbose_name='详细内容')
    topics_discussed = models.JSONField(default=list, verbose_name='讨论话题')
    agreements_made = models.TextField(blank=True, null=True, verbose_name='达成的约定/承诺')
    
    # 情感记录
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, blank=True, null=True, verbose_name='当时心情')
    impression_notes = models.TextField(blank=True, null=True, verbose_name='印象/感受')
    
    # 参与人员
    other_participants = models.ManyToManyField(LegacyPersonProfile, blank=True, related_name='group_interactions', verbose_name='其他参与者')
    
    # 附件
    photos = models.JSONField(default=list, verbose_name='相关照片')
    files = models.JSONField(default=list, verbose_name='相关文件')
    links = models.JSONField(default=list, verbose_name='相关链接')
    
    # 标签和分类
    tags = models.JSONField(default=list, verbose_name='自定义标签')
    is_important = models.BooleanField(default=False, verbose_name='是否重要')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '互动记录'
        verbose_name_plural = '互动记录'
        ordering = ['-date', '-time', '-created_at']
    
    def __str__(self):
        return f"{self.person.name} - {self.title} - {self.date}"
    
    def get_mood_emoji(self):
        """获取心情对应的表情符号"""
        mood_emojis = {
            'very_happy': '😄',
            'happy': '😊',
            'neutral': '😐',
            'disappointed': '😞',
            'sad': '😢',
            'angry': '😠',
            'confused': '😕',
            'excited': '🤩',
            'nervous': '😰',
            'grateful': '🙏',
        }
        return mood_emojis.get(self.mood, '😐')
    
    def get_duration_display(self):
        """获取时长显示（如果是会面类型）"""
        if self.interaction_type in ['meeting', 'phone_call', 'video_call']:
            # 这里可以根据需要添加时长字段
            return "待补充时长功能"
        return ""


class LegacyImportantMoment(models.Model):
    """重要时刻模型"""
    MOMENT_TYPE_CHOICES = [
        ('first_meeting', '初次见面'),
        ('friendship_milestone', '友谊里程碑'),
        ('collaboration', '重要合作'),
        ('conflict_resolution', '解决矛盾'),
        ('celebration', '共同庆祝'),
        ('farewell', '告别时刻'),
        ('reunion', '重逢'),
        ('achievement', '共同成就'),
        ('crisis_support', '危机支持'),
        ('life_change', '人生转折'),
        ('other', '其他'),
    ]
    
    # 基础信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    person = models.ForeignKey(LegacyPersonProfile, on_delete=models.CASCADE, related_name='important_moments', verbose_name='相关人物')
    related_interaction = models.OneToOneField(LegacyInteraction, on_delete=models.CASCADE, blank=True, null=True, verbose_name='关联互动记录')
    
    # 时刻详情
    moment_type = models.CharField(max_length=30, choices=MOMENT_TYPE_CHOICES, verbose_name='时刻类型')
    title = models.CharField(max_length=200, verbose_name='时刻标题')
    description = models.TextField(verbose_name='详细描述')
    date = models.DateField(verbose_name='日期')
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name='地点')
    
    # 多媒体内容
    photos = models.JSONField(default=list, verbose_name='照片')
    videos = models.JSONField(default=list, verbose_name='视频')
    audio_recordings = models.JSONField(default=list, verbose_name='录音')
    documents = models.JSONField(default=list, verbose_name='文档')
    
    # 参与人员
    other_participants = models.ManyToManyField(LegacyPersonProfile, blank=True, related_name='shared_moments', verbose_name='其他参与者')
    
    # 情感记录
    emotional_impact = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=3, verbose_name='情感影响程度')
    personal_reflection = models.TextField(blank=True, null=True, verbose_name='个人反思')
    
    # 标签
    tags = models.JSONField(default=list, verbose_name='标签')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '重要时刻'
        verbose_name_plural = '重要时刻'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.person.name} - {self.title} - {self.date}"
    
    def get_emotional_impact_stars(self):
        """获取情感影响程度星级显示"""
        return '⭐' * self.emotional_impact


class LegacyRelationshipStatistics(models.Model):
    """人际关系统计模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基础统计
    total_people = models.IntegerField(default=0, verbose_name='总人数')
    total_interactions = models.IntegerField(default=0, verbose_name='总互动次数')
    total_moments = models.IntegerField(default=0, verbose_name='重要时刻数')
    
    # 关系分布
    relationship_distribution = models.JSONField(default=dict, verbose_name='关系分布')
    interaction_frequency = models.JSONField(default=dict, verbose_name='互动频率分布')
    
    # 活跃度统计
    active_relationships = models.IntegerField(default=0, verbose_name='活跃关系数')
    dormant_relationships = models.IntegerField(default=0, verbose_name='休眠关系数')
    
    # 时间统计
    weekly_interactions = models.JSONField(default=list, verbose_name='每周互动数')
    monthly_interactions = models.JSONField(default=list, verbose_name='每月互动数')
    
    # 更新时间
    last_updated = models.DateTimeField(auto_now=True, verbose_name='最后更新时间')
    
    class Meta:
        verbose_name = '人际关系统计'
        verbose_name_plural = '人际关系统计'
    
    def __str__(self):
        return f"{self.user.username} - 人际关系统计"
    
    def calculate_statistics(self):
        """计算统计数据"""
        from collections import Counter
        
        # 获取用户的所有人物档案和互动记录
        profiles = LegacyPersonProfile.objects.filter(user=self.user)
        interactions = LegacyInteraction.objects.filter(user=self.user)
        moments = LegacyImportantMoment.objects.filter(user=self.user)
        
        # 基础统计
        self.total_people = profiles.count()
        self.total_interactions = interactions.count()
        self.total_moments = moments.count()
        
        # 关系分布统计
        relationship_tags = []
        for profile in profiles:
            relationship_tags.extend([tag.name for tag in profile.relationship_tags.all()])
        self.relationship_distribution = dict(Counter(relationship_tags))
        
        # 互动频率分布
        interaction_types = [interaction.interaction_type for interaction in interactions]
        self.interaction_frequency = dict(Counter(interaction_types))
        
        # 活跃度统计（30天内有互动的为活跃）
        from datetime import date, timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        
        self.active_relationships = profiles.filter(
            last_interaction_date__gte=thirty_days_ago
        ).count()
        self.dormant_relationships = self.total_people - self.active_relationships
        
        self.save()


class LegacyRelationshipReminder(models.Model):
    """人际关系提醒模型"""
    REMINDER_TYPE_CHOICES = [
        ('birthday', '生日提醒'),
        ('anniversary', '纪念日提醒'),
        ('contact', '联系提醒'),
        ('follow_up', '跟进提醒'),
        ('custom', '自定义提醒'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('completed', '已完成'),
        ('snoozed', '已推迟'),
        ('cancelled', '已取消'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    person = models.ForeignKey(LegacyPersonProfile, on_delete=models.CASCADE, related_name='reminders', verbose_name='相关人物')
    
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='提醒类型')
    title = models.CharField(max_length=200, verbose_name='提醒标题')
    description = models.TextField(blank=True, null=True, verbose_name='提醒描述')
    
    reminder_date = models.DateField(verbose_name='提醒日期')
    reminder_time = models.TimeField(default='09:00', verbose_name='提醒时间')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    is_recurring = models.BooleanField(default=False, verbose_name='是否重复')
    recurrence_pattern = models.CharField(max_length=50, blank=True, null=True, verbose_name='重复模式')
    
    # 推迟设置
    snooze_count = models.IntegerField(default=0, verbose_name='推迟次数')
    max_snooze = models.IntegerField(default=3, verbose_name='最大推迟次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '人际关系提醒'
        verbose_name_plural = '人际关系提醒'
        ordering = ['reminder_date', 'reminder_time']
    
    def __str__(self):
        return f"{self.person.name} - {self.title} - {self.reminder_date}"
    
    def can_snooze(self):
        """检查是否可以推迟"""
        return self.snooze_count < self.max_snooze
    
    def snooze_reminder(self, days=1):
        """推迟提醒"""
        if self.can_snooze():
            from datetime import timedelta
            self.reminder_date += timedelta(days=days)
            self.snooze_count += 1
            self.status = 'snoozed'
            self.save()
            return True
        return False


# ===== 功能推荐系统模型 =====

class Feature(models.Model):
    """功能模型 - 记录系统中的所有功能"""
    FEATURE_TYPE_CHOICES = [
        ('tool', '工具功能'),
        ('mode', '模式功能'),
        ('page', '页面功能'),
        ('api', 'API功能'),
    ]
    
    CATEGORY_CHOICES = [
        ('work', '工作效率'),
        ('life', '生活娱乐'),
        ('health', '健康管理'),
        ('social', '社交互动'),
        ('creative', '创作工具'),
        ('analysis', '数据分析'),
        ('entertainment', '娱乐休闲'),
        ('learning', '学习成长'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='功能名称')
    description = models.TextField(verbose_name='功能描述')
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES, verbose_name='功能类型')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='功能分类')
    url_name = models.CharField(max_length=100, verbose_name='URL名称', help_text='Django URL name')
    icon_class = models.CharField(max_length=100, verbose_name='图标类名', help_text='Font Awesome图标类名')
    icon_color = models.CharField(max_length=20, default='#007bff', verbose_name='图标颜色')
    
    # 权限和可见性
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    require_login = models.BooleanField(default=True, verbose_name='是否需要登录')
    require_membership = models.CharField(max_length=20, choices=[
        ('', '无要求'),
        ('basic', '基础会员'),
        ('premium', '高级会员'),
        ('vip', 'VIP会员'),
    ], blank=True, verbose_name='会员要求')
    
    # 推荐权重
    recommendation_weight = models.IntegerField(default=50, verbose_name='推荐权重', help_text='1-100，数值越高推荐概率越大')
    popularity_score = models.IntegerField(default=0, verbose_name='受欢迎程度', help_text='基于使用量自动计算')
    
    # 统计信息
    total_usage_count = models.IntegerField(default=0, verbose_name='总使用次数')
    monthly_usage_count = models.IntegerField(default=0, verbose_name='月使用次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '功能'
        verbose_name_plural = '功能管理'
        ordering = ['-recommendation_weight', '-popularity_score', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['category', 'feature_type']),
            models.Index(fields=['recommendation_weight', 'popularity_score']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_feature_type_display()})"
    
    def can_recommend_to_user(self, user):
        """检查是否可以向用户推荐此功能"""
        if not self.is_active or not self.is_public:
            return False
        
        if self.require_login and not user.is_authenticated:
            return False
            
        if self.require_membership:
            try:
                membership = user.membership
                if not membership.is_valid:
                    return False
                    
                membership_levels = {'basic': 1, 'premium': 2, 'vip': 3}
                required_level = membership_levels.get(self.require_membership, 0)
                user_level = membership_levels.get(membership.membership_type, 0)
                
                if user_level < required_level:
                    return False
            except:
                return False
        
        return True
    
    def increment_usage(self):
        """增加使用计数"""
        self.total_usage_count += 1
        self.monthly_usage_count += 1
        # 简单的受欢迎程度计算
        self.popularity_score = min(100, self.monthly_usage_count // 10)
        self.save(update_fields=['total_usage_count', 'monthly_usage_count', 'popularity_score'])


class UserFeaturePermission(models.Model):
    """用户功能权限模型 - 管理员可以控制用户能看到什么功能"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name='功能')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    is_allowed = models.BooleanField(default=True, verbose_name='是否允许使用')
    custom_weight = models.IntegerField(null=True, blank=True, verbose_name='自定义推荐权重',
                                      help_text='为特定用户设置的推荐权重，为空则使用功能默认权重')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='created_permissions', verbose_name='创建者')
    
    class Meta:
        verbose_name = '用户功能权限'
        verbose_name_plural = '用户功能权限'
        unique_together = ['user', 'feature']
        indexes = [
            models.Index(fields=['user', 'is_visible', 'is_allowed']),
            models.Index(fields=['feature', 'is_visible']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.feature.name} ({'可见' if self.is_visible else '隐藏'})"


class FeatureRecommendation(models.Model):
    """功能推荐记录模型"""
    ACTION_CHOICES = [
        ('shown', '已展示'),
        ('clicked', '已点击'),
        ('dismissed', '已忽略'),
        ('not_interested', '不感兴趣'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name='推荐功能')
    session_id = models.CharField(max_length=100, verbose_name='会话ID', help_text='用于标识同一次推荐会话')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='用户行为')
    
    # 推荐上下文信息
    recommendation_reason = models.CharField(max_length=200, blank=True, verbose_name='推荐理由')
    user_mode_preference = models.CharField(max_length=20, blank=True, verbose_name='用户模式偏好')
    recommendation_algorithm = models.CharField(max_length=50, default='random', verbose_name='推荐算法')
    
    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='推荐时间')
    action_time = models.DateTimeField(null=True, blank=True, verbose_name='行为时间')
    
    # 设备和环境信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    class Meta:
        verbose_name = '功能推荐记录'
        verbose_name_plural = '功能推荐记录'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['feature', 'action']),
            models.Index(fields=['session_id']),
            models.Index(fields=['action', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.feature.name} - {self.get_action_display()}"
    
    @classmethod
    def get_user_recommendation_history(cls, user, days=30):
        """获取用户最近的推荐历史"""
        from datetime import datetime, timedelta
        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(user=user, created_at__gte=since)
    
    @classmethod
    def has_recent_recommendation(cls, user, feature, hours=24):
        """检查最近是否已经推荐过该功能"""
        from datetime import timedelta
        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(user=user, feature=feature, created_at__gte=since).exists()


class UserFirstVisit(models.Model):
    """用户首次访问记录"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    first_visit_time = models.DateTimeField(auto_now_add=True, verbose_name='首次访问时间')
    has_seen_recommendation = models.BooleanField(default=False, verbose_name='是否已看过推荐')
    recommendation_shown_count = models.IntegerField(default=0, verbose_name='推荐展示次数')
    last_recommendation_time = models.DateTimeField(null=True, blank=True, verbose_name='最后推荐时间')
    
    # 用户行为统计
    total_login_count = models.IntegerField(default=1, verbose_name='总登录次数')
    total_feature_usage = models.IntegerField(default=0, verbose_name='总功能使用次数')
    
    class Meta:
        verbose_name = '用户首次访问记录'
        verbose_name_plural = '用户首次访问记录'
    
    def __str__(self):
        return f"{self.user.username} - 首次访问: {self.first_visit_time}"
    
    def should_show_recommendation(self):
        """判断是否应该显示推荐 - 每日只显示一次"""
        # 新用户首次访问，显示推荐
        if not self.has_seen_recommendation:
            return True
        
        # 检查是否今天已经显示过推荐
        if self.last_recommendation_time:
            from datetime import date
            today = date.today()
            last_recommendation_date = self.last_recommendation_time.date()
            
            # 如果今天已经显示过推荐，则不再显示
            if last_recommendation_date == today:
                return False
            
            # 如果不是今天显示的，则可以显示（每日一次）
            return True
        
        # 如果从未显示过推荐，则显示
        return True
    
    def mark_recommendation_shown(self):
        """标记已显示推荐"""
        self.has_seen_recommendation = True
        self.recommendation_shown_count += 1
        self.last_recommendation_time = timezone.now()
        self.save(update_fields=['has_seen_recommendation', 'recommendation_shown_count', 'last_recommendation_time'])


# 健身社区相关模型
class FitnessCommunityPost(models.Model):
    """健身社区帖子模型"""
    POST_TYPE_CHOICES = [
        ('checkin', '打卡分享'),
        ('plan', '训练计划'),
        ('video', '训练视频'),
        ('achievement', '成就分享'),
        ('motivation', '励志分享'),
        ('question', '问题讨论'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发布用户')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name='帖子类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    
    # 关联的打卡记录
    related_checkin = models.ForeignKey(CheckInCalendar, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联打卡')
    
    # 训练计划相关
    training_plan_data = models.JSONField(default=dict, blank=True, verbose_name='训练计划数据')
    
    # 视频相关
    video_url = models.URLField(blank=True, null=True, verbose_name='视频链接')
    video_thumbnail = models.ImageField(upload_to='fitness_videos/thumbnails/', blank=True, null=True, verbose_name='视频缩略图')
    video_duration = models.IntegerField(blank=True, null=True, verbose_name='视频时长(秒)')
    
    # 标签和分类
    tags = models.JSONField(default=list, verbose_name='标签')
    training_parts = models.JSONField(default=list, verbose_name='训练部位')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', '初级'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
        ('expert', '专家级')
    ], blank=True, null=True, verbose_name='难度等级')
    
    # 互动数据
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    comments_count = models.IntegerField(default=0, verbose_name='评论数')
    shares_count = models.IntegerField(default=0, verbose_name='分享数')
    views_count = models.IntegerField(default=0, verbose_name='浏览数')
    
    # 状态
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否精选')
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '健身社区帖子'
        verbose_name_plural = '健身社区帖子'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def increment_views(self):
        """增加浏览数"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def get_training_parts_display(self):
        """获取训练部位显示文本"""
        return ', '.join(self.training_parts) if self.training_parts else '全身'


class FitnessCommunityComment(models.Model):
    """健身社区评论模型"""
    post = models.ForeignKey(FitnessCommunityPost, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    
    content = models.TextField(verbose_name='评论内容')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '健身社区评论'
        verbose_name_plural = '健身社区评论'
    
    def __str__(self):
        return f"{self.user.username} 评论了 {self.post.title}"


class FitnessCommunityLike(models.Model):
    """健身社区点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    post = models.ForeignKey(FitnessCommunityPost, on_delete=models.CASCADE, related_name='likes', verbose_name='帖子')
    comment = models.ForeignKey(FitnessCommunityComment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes', verbose_name='评论')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        unique_together = [['user', 'post'], ['user', 'comment']]
        verbose_name = '健身社区点赞'
        verbose_name_plural = '健身社区点赞'
    
    def __str__(self):
        if self.post:
            return f"{self.user.username} 点赞了 {self.post.title}"
        else:
            return f"{self.user.username} 点赞了评论"


class FitnessUserProfile(models.Model):
    """健身用户档案模型"""
    GENDER_CHOICES = [
        ('male', '男性'),
        ('female', '女性'),
    ]
    
    GOAL_CHOICES = [
        ('lose_weight', '减脂'),
        ('gain_muscle', '增肌'),
        ('maintain', '维持体重'),
    ]
    
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', '久坐'),
        ('light', '轻度活动'),
        ('moderate', '中度活动'),
        ('high', '重度活动'),
    ]
    
    INTENSITY_CHOICES = [
        ('conservative', '保守型'),
        ('balanced', '均衡型'),
        ('aggressive', '激进型'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    age = models.IntegerField(default=25, verbose_name='年龄')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male', verbose_name='性别')
    height = models.FloatField(default=170.0, verbose_name='身高(cm)')
    weight = models.FloatField(default=70.0, verbose_name='当前体重(kg)')
    body_fat_percentage = models.FloatField(null=True, blank=True, verbose_name='体脂率(%)')
    bmr = models.FloatField(null=True, blank=True, verbose_name='基础代谢率')
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default='maintain', verbose_name='健身目标')
    intensity = models.CharField(max_length=20, choices=INTENSITY_CHOICES, default='balanced', verbose_name='目标强度')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVEL_CHOICES, default='moderate', verbose_name='日常活动量')
    dietary_preferences = models.JSONField(default=list, verbose_name='饮食偏好')
    allergies = models.JSONField(default=list, verbose_name='过敏食物')
    training_days_per_week = models.IntegerField(default=3, verbose_name='每周训练天数')
    training_intensity = models.CharField(max_length=20, default='moderate', verbose_name='训练强度')
    training_duration = models.IntegerField(default=60, verbose_name='训练时长(分钟)')
    selected_badge = models.ForeignKey('FitnessAchievement', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='已佩戴徽章')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '健身用户档案'
        verbose_name_plural = '健身用户档案'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_goal_display()}"

    def get_selected_badge_display(self):
        if self.selected_badge:
            return {
                'name': self.selected_badge.name,
                'description': self.selected_badge.description,
                'icon': self.selected_badge.icon,
                'color': self.selected_badge.color,
                'level': self.selected_badge.level,
            }
        return None


class DietPlan(models.Model):
    """饮食计划模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(verbose_name='结束日期')
    daily_calories = models.IntegerField(verbose_name='每日总热量')
    protein_goal = models.IntegerField(verbose_name='蛋白质目标(g)')
    carbs_goal = models.IntegerField(verbose_name='碳水目标(g)')
    fat_goal = models.IntegerField(verbose_name='脂肪目标(g)')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '饮食计划'
        verbose_name_plural = '饮食计划'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.start_date} 到 {self.end_date}"


class Meal(models.Model):
    """餐食模型"""
    MEAL_TYPE_CHOICES = [
        ('breakfast', '早餐'),
        ('lunch', '午餐'),
        ('dinner', '晚餐'),
        ('snack', '加餐'),
        ('pre_workout', '训练前'),
        ('post_workout', '训练后'),
    ]
    
    plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, verbose_name='饮食计划')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name='餐食类型')
    day_of_week = models.IntegerField(verbose_name='星期几(1-7)')
    description = models.TextField(verbose_name='餐食描述')
    ingredients = models.JSONField(default=list, verbose_name='食材清单')
    calories = models.IntegerField(verbose_name='热量')
    protein = models.FloatField(verbose_name='蛋白质(g)')
    carbs = models.FloatField(verbose_name='碳水(g)')
    fat = models.FloatField(verbose_name='脂肪(g)')
    ideal_time = models.TimeField(null=True, blank=True, verbose_name='理想用餐时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '餐食'
        verbose_name_plural = '餐食'
        ordering = ['day_of_week', 'meal_type']
    
    def __str__(self):
        return f"{self.plan.user.username} - {self.get_meal_type_display()} - 第{self.day_of_week}天"


class NutritionReminder(models.Model):
    """营养提醒模型"""
    REMINDER_TYPE_CHOICES = [
        ('meal_time', '用餐时间'),
        ('pre_workout', '训练前加餐'),
        ('post_workout', '训练后补充'),
        ('hydration', '水分补充'),
        ('meal_log', '餐食记录'),
        ('weight_track', '体重记录'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name='提醒类型')
    message = models.TextField(verbose_name='提醒内容')
    trigger_time = models.TimeField(null=True, blank=True, verbose_name='触发时间')
    trigger_days = models.JSONField(default=list, verbose_name='触发日期(1-7)')
    is_recurring = models.BooleanField(default=True, verbose_name='是否重复')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    last_sent = models.DateTimeField(null=True, blank=True, verbose_name='最后发送时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '营养提醒'
        verbose_name_plural = '营养提醒'
        ordering = ['trigger_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_reminder_type_display()}"


class MealLog(models.Model):
    """餐食记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, verbose_name='计划餐食')
    consumed_date = models.DateField(verbose_name='消费日期')
    consumed_time = models.TimeField(verbose_name='消费时间')
    actual_calories = models.IntegerField(null=True, blank=True, verbose_name='实际热量')
    actual_protein = models.FloatField(null=True, blank=True, verbose_name='实际蛋白质')
    actual_carbs = models.FloatField(null=True, blank=True, verbose_name='实际碳水')
    actual_fat = models.FloatField(null=True, blank=True, verbose_name='实际脂肪')
    notes = models.TextField(blank=True, verbose_name='备注')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '餐食记录'
        verbose_name_plural = '餐食记录'
        ordering = ['-consumed_date', '-consumed_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.meal.get_meal_type_display()} - {self.consumed_date}"


class WeightTracking(models.Model):
    """体重追踪模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    weight = models.FloatField(verbose_name='体重(kg)')
    body_fat_percentage = models.FloatField(null=True, blank=True, verbose_name='体脂率(%)')
    measurement_date = models.DateField(verbose_name='测量日期')
    notes = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '体重追踪'
        verbose_name_plural = '体重追踪'
        ordering = ['-measurement_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.weight}kg - {self.measurement_date}"


class FoodDatabase(models.Model):
    """食物数据库模型"""
    name = models.CharField(max_length=200, verbose_name='食物名称')
    category = models.CharField(max_length=100, verbose_name='食物类别')
    calories_per_100g = models.FloatField(verbose_name='每100g热量')
    protein_per_100g = models.FloatField(verbose_name='每100g蛋白质')
    carbs_per_100g = models.FloatField(verbose_name='每100g碳水')
    fat_per_100g = models.FloatField(verbose_name='每100g脂肪')
    fiber_per_100g = models.FloatField(default=0, verbose_name='每100g纤维')
    is_vegetarian = models.BooleanField(default=False, verbose_name='是否素食')
    is_gluten_free = models.BooleanField(default=False, verbose_name='是否无麸质')
    allergens = models.JSONField(default=list, verbose_name='过敏原')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '食物数据库'
        verbose_name_plural = '食物数据库'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FitnessAchievement(models.Model):
    """健身成就模型"""
    ACHIEVEMENT_TYPE_CHOICES = [
        ('streak', '连续成就'),
        ('workout', '训练成就'),
        ('social', '社交成就'),
        ('milestone', '里程碑成就'),
        ('special', '特殊成就'),
    ]
    
    ACHIEVEMENT_LEVEL_CHOICES = [
        ('bronze', '铜牌'),
        ('silver', '银牌'),
        ('gold', '金牌'),
        ('platinum', '白金'),
        ('diamond', '钻石'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='成就名称')
    description = models.TextField(verbose_name='成就描述')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES, verbose_name='成就类型')
    level = models.CharField(max_length=20, choices=ACHIEVEMENT_LEVEL_CHOICES, verbose_name='成就等级')
    
    icon = models.CharField(max_length=50, default='fas fa-trophy', verbose_name='成就图标')
    color = models.CharField(max_length=7, default='#FFD700', verbose_name='成就颜色')
    
    # 解锁条件
    unlock_condition = models.JSONField(default=dict, verbose_name='解锁条件')
    is_auto_unlock = models.BooleanField(default=True, verbose_name='是否自动解锁')
    
    # 统计
    total_earned = models.IntegerField(default=0, verbose_name='总获得次数')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '健身成就'
        verbose_name_plural = '健身成就'
        ordering = ['level', 'achievement_type', 'name']
    
    def __str__(self):
        return f"{self.get_level_display()} - {self.name}"


class UserFitnessAchievement(models.Model):
    """用户健身成就模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    achievement = models.ForeignKey(FitnessAchievement, on_delete=models.CASCADE, verbose_name='成就')
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='获得时间')
    is_shared = models.BooleanField(default=False, verbose_name='是否已分享')
    is_equipped = models.BooleanField(default=False, verbose_name='是否佩戴')
    
    class Meta:
        unique_together = ['user', 'achievement']
        verbose_name = '用户健身成就'
        verbose_name_plural = '用户健身成就'
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} 获得了 {self.achievement.name}"


class FitnessFollow(models.Model):
    """健身关注关系模型"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_fitness', verbose_name='关注者')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_fitness', verbose_name='被关注者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='关注时间')
    # 临时添加这些字段以避免迁移错误
    content = models.TextField(blank=True, default='', verbose_name='内容')
    
    class Meta:
        unique_together = ['follower', 'following']
        verbose_name = '健身关注关系'
        verbose_name_plural = '健身关注关系'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} 关注了 {self.following.username}"


# class UserGeneratedTravelGuide(models.Model):
    """用户生成的旅游攻略模型 - 好心人的攻略"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建用户')
    title = models.CharField(max_length=200, verbose_name='攻略标题')
    destination = models.CharField(max_length=200, verbose_name='目的地')
    content = models.TextField(verbose_name='攻略内容')
    summary = models.TextField(blank=True, null=True, verbose_name='攻略摘要')
    
    # 攻略分类
    travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 文件附件
    attachment = models.FileField(upload_to='travel_guides/', blank=True, null=True, verbose_name='附件')
    attachment_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='附件名称')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 状态
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户生成旅游攻略'
        verbose_name_plural = '用户生成旅游攻略'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_file_extension(self):
        """获取文件扩展名"""
        if self.attachment:
            return self.attachment.name.split('.')[-1].lower()
        return None
    
    def is_downloadable(self):
        """检查是否可下载"""
        return bool(self.attachment)
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def increment_use_count(self):
        """增加使用次数"""
        self.use_count += 1
        self.save(update_fields=['use_count'])


# class TravelGuideUsage(models.Model):
    """旅游攻略使用记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    # guide = models.ForeignKey(UserGeneratedTravelGuide, on_delete=models.CASCADE, verbose_name='攻略')
    usage_type = models.CharField(max_length=20, choices=[
        ('view', '查看'),
        ('download', '下载'),
        ('use', '使用'),
    ], verbose_name='使用类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='使用时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '攻略使用记录'
        verbose_name_plural = '攻略使用记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.guide.title} - {self.get_usage_type_display()}"


# 船宝（二手线下交易）相关模型

class ShipBaoItem(models.Model):
    """船宝物品模型"""
    CATEGORY_CHOICES = [
        ('electronics', '电子产品'),
        ('clothing', '服饰鞋包'),
        ('furniture', '家具家居'),
        ('books', '图书音像'),
        ('sports', '运动户外'),
        ('beauty', '美妆护肤'),
        ('toys', '玩具游戏'),
        ('food', '食品饮料'),
        ('other', '其他'),
    ]
    
    CONDITION_CHOICES = [
        (1, '1星 - 很旧'),
        (2, '2星 - 较旧'),
        (3, '3星 - 一般'),
        (4, '4星 - 较新'),
        (5, '5星 - 全新'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '发布中'),
        ('reserved', '交易中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    DELIVERY_CHOICES = [
        ('pickup', '仅自提'),
        ('delivery', '仅送货'),
        ('both', '自提/送货'),
    ]
    
    # 基础信息
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='卖家')
    title = models.CharField(max_length=200, verbose_name='物品标题')
    description = models.TextField(verbose_name='物品描述')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='分类')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格(元)')
    condition = models.IntegerField(choices=CONDITION_CHOICES, verbose_name='新旧程度')
    
    # 图片
    images = models.JSONField(default=list, verbose_name='图片URL列表')
    
    # 交易设置
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup', verbose_name='交易方式')
    can_bargain = models.BooleanField(default=False, verbose_name='是否可议价')
    
    # 地理位置 - 增强位置信息
    location = models.CharField(max_length=200, verbose_name='交易地点')
    location_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='所在城市')
    location_region = models.CharField(max_length=100, blank=True, null=True, verbose_name='所在地区')
    location_address = models.CharField(max_length=500, blank=True, null=True, verbose_name='详细地址')
    latitude = models.FloatField(blank=True, null=True, verbose_name='纬度')
    longitude = models.FloatField(blank=True, null=True, verbose_name='经度')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='交易状态')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    favorite_count = models.IntegerField(default=0, verbose_name='收藏次数')
    want_count = models.IntegerField(default=0, verbose_name='想要人数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '船宝物品'
        verbose_name_plural = '船宝物品'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['location_city']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.seller.username} - {self.title} - ¥{self.price}"
    
    def get_condition_stars(self):
        """获取新旧程度星级显示"""
        return '★' * self.condition + '☆' * (5 - self.condition)
    
    def get_main_image(self):
        """获取主图"""
        return self.images[0] if self.images else None
    
    def get_image_count(self):
        """获取图片数量"""
        return len(self.images)
    
    def get_location_display(self):
        """获取位置显示信息"""
        if self.location_city and self.location_region:
            return f"{self.location_city}，{self.location_region}"
        elif self.location_city:
            return self.location_city
        elif self.location_address:
            return self.location_address
        return self.location or "位置未知"
    
    def calculate_distance_to(self, target_lat, target_lon):
        """计算到指定位置的距离（公里）"""
        if not self.latitude or not self.longitude:
            return None
        
        from math import radians, cos, sin, asin, sqrt
        
        # 将经纬度转换为弧度
        lat1, lon1, lat2, lon2 = map(radians, [
            self.latitude, self.longitude, target_lat, target_lon
        ])
        
        # Haversine公式
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # 地球半径（公里）
        
        return c * r
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_favorite_count(self):
        """增加收藏次数"""
        self.favorite_count += 1
        self.save(update_fields=['favorite_count'])
    
    def increment_want_count(self):
        """增加想要人数"""
        self.want_count += 1
        self.save(update_fields=['want_count'])
    
    def decrement_want_count(self):
        """减少想要人数"""
        self.want_count = max(0, self.want_count - 1)
        self.save(update_fields=['want_count'])
    
    def increment_inquiry_count(self):
        """增加咨询次数（如果有inquiry_count字段的话）"""
        # 目前legacy模型没有inquiry_count字段，保留方法以保持兼容性
        pass


class ShipBaoTransaction(models.Model):
    """船宝交易记录模型"""
    STATUS_CHOICES = [
        ('initiated', '已发起'),
        ('negotiating', '协商中'),
        ('meeting_arranged', '已约定见面'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    # 交易信息
    item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, related_name='transactions', verbose_name='物品')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_purchases', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_sales', verbose_name='卖家')
    
    # 交易状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated', verbose_name='交易状态')
    
    # 交易详情
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='最终价格')
    meeting_location = models.CharField(max_length=200, blank=True, null=True, verbose_name='见面地点')
    meeting_time = models.DateTimeField(blank=True, null=True, verbose_name='见面时间')
    
    # 评价
    buyer_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='买家评分')
    seller_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='卖家评分')
    buyer_comment = models.TextField(blank=True, null=True, verbose_name='买家评价')
    seller_comment = models.TextField(blank=True, null=True, verbose_name='卖家评价')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发起时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '船宝交易'
        verbose_name_plural = '船宝交易'
        unique_together = ['item', 'buyer']
    
    def __str__(self):
        return f"{self.buyer.username} 购买 {self.item.title}"


class ShipBaoMessage(models.Model):
    """船宝私信模型"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('offer', '报价'),
        ('system', '系统消息'),
    ]
    
    transaction = models.ForeignKey(ShipBaoTransaction, on_delete=models.CASCADE, related_name='messages', verbose_name='交易')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='报价金额')
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '船宝私信'
        verbose_name_plural = '船宝私信'
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class ShipBaoUserProfile(models.Model):
    """船宝用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 实名认证
    is_verified = models.BooleanField(default=False, verbose_name='是否实名认证')
    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='真实姓名')
    id_card_number = models.CharField(max_length=18, blank=True, null=True, verbose_name='身份证号')
    verification_time = models.DateTimeField(blank=True, null=True, verbose_name='认证时间')
    
    # 信用评分
    credit_score = models.IntegerField(default=100, verbose_name='信用评分')
    total_transactions = models.IntegerField(default=0, verbose_name='总交易数')
    successful_transactions = models.IntegerField(default=0, verbose_name='成功交易数')
    
    # 位置信息
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在城市')
    district = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在区域')
    
    # 偏好设置
    notification_enabled = models.BooleanField(default=True, verbose_name='启用通知')
    auto_accept_offers = models.BooleanField(default=False, verbose_name='自动接受报价')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '船宝用户资料'
        verbose_name_plural = '船宝用户资料'
    
    def __str__(self):
        return f"{self.user.username} - 船宝资料"
    
    def get_success_rate(self):
        """获取交易成功率"""
        if self.total_transactions == 0:
            return 0
        return round((self.successful_transactions / self.total_transactions) * 100, 1)
    
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


class ShipBaoReport(models.Model):
    """船宝举报模型"""
    REPORT_TYPE_CHOICES = [
        ('fraud', '欺诈行为'),
        ('fake_info', '虚假信息'),
        ('inappropriate', '不当内容'),
        ('harassment', '骚扰行为'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('investigating', '调查中'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_reports', verbose_name='举报者')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_reported', verbose_name='被举报者')
    reported_item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, blank=True, null=True, verbose_name='被举报物品')
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
        verbose_name = '船宝举报'
        verbose_name_plural = '船宝举报'
    
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username}"


# 搭子（同城活动匹配）相关模型

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
    is_read_by = models.ManyToManyField(User, related_name='legacy_buddy_read_messages', blank=True, verbose_name='已读用户')
    
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


class ExerciseWeightRecord(models.Model):
    """锻炼重量记录模型"""
    EXERCISE_TYPE_CHOICES = [
        # 三大项
        ('squat', '深蹲'),
        ('bench_press', '卧推'),
        ('deadlift', '硬拉'),
        # 其他力量训练
        ('overhead_press', '推举'),
        ('barbell_row', '杠铃划船'),
        ('pull_up', '引体向上'),
        ('dip', '双杠臂屈伸'),
        ('lunge', '弓步蹲'),
        ('leg_press', '腿举'),
        ('leg_curl', '腿弯举'),
        ('leg_extension', '腿伸展'),
        ('calf_raise', '提踵'),
        ('bicep_curl', '弯举'),
        ('tricep_extension', '臂屈伸'),
        ('shoulder_press', '肩推'),
        ('lateral_raise', '侧平举'),
        ('rear_delt_fly', '后三角肌飞鸟'),
        ('chest_fly', '飞鸟'),
        ('lat_pulldown', '高位下拉'),
        ('face_pull', '面拉'),
        ('shrug', '耸肩'),
        ('upright_row', '直立划船'),
        ('good_morning', '早安式'),
        ('romanian_deadlift', '罗马尼亚硬拉'),
        ('sumo_deadlift', '相扑硬拉'),
        ('front_squat', '前蹲'),
        ('back_squat', '后蹲'),
        ('box_squat', '箱式深蹲'),
        ('pause_squat', '暂停深蹲'),
        ('close_grip_bench', '窄握卧推'),
        ('wide_grip_bench', '宽握卧推'),
        ('incline_bench', '上斜卧推'),
        ('decline_bench', '下斜卧推'),
        ('dumbbell_bench', '哑铃卧推'),
        ('dumbbell_squat', '哑铃深蹲'),
        ('goblet_squat', '高脚杯深蹲'),
        ('bulgarian_split_squat', '保加利亚分腿蹲'),
        ('step_up', '台阶上'),
        ('hip_thrust', '臀桥'),
        ('glute_bridge', '臀桥'),
        ('plank', '平板支撑'),
        ('side_plank', '侧平板'),
        ('crunch', '卷腹'),
        ('sit_up', '仰卧起坐'),
        ('russian_twist', '俄罗斯转体'),
        ('mountain_climber', '登山者'),
        ('burpee', '波比跳'),
        ('jumping_jack', '开合跳'),
        ('high_knee', '高抬腿'),
        ('butt_kick', '后踢腿'),
        ('other', '其他'),
    ]
    
    REP_TYPE_CHOICES = [
        ('1rm', '1RM'),
        ('3rm', '3RM'),
        ('5rm', '5RM'),
        ('8rm', '8RM'),
        ('10rm', '10RM'),
        ('12rm', '12RM'),
        ('15rm', '15RM'),
        ('20rm', '20RM'),
        ('max_reps', '最大次数'),
        ('custom', '自定义'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    exercise_type = models.CharField(max_length=50, choices=EXERCISE_TYPE_CHOICES, verbose_name='锻炼类型')
    weight = models.FloatField(verbose_name='重量(kg)')
    reps = models.IntegerField(verbose_name='次数')
    rep_type = models.CharField(max_length=10, choices=REP_TYPE_CHOICES, default='custom', verbose_name='次数类型')
    sets = models.IntegerField(default=1, verbose_name='组数')
    rpe = models.IntegerField(null=True, blank=True, verbose_name='RPE(1-10)')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    workout_date = models.DateField(verbose_name='训练日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')
    
    class Meta:
        ordering = ['-workout_date', '-created_at']
        verbose_name = '锻炼重量记录'
        verbose_name_plural = '锻炼重量记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_exercise_type_display()} - {self.weight}kg x {self.reps}次"
    
    def get_estimated_1rm(self):
        """估算1RM"""
        if self.reps == 1:
            return self.weight
        
        # 使用Epley公式估算1RM
        if self.reps <= 10:
            return round(self.weight * (1 + self.reps / 30), 1)
        else:
            # 对于高次数，使用更保守的估算
            return round(self.weight * (1 + self.reps / 40), 1)
    
    def get_weight_class(self):
        """获取重量等级"""
        if self.exercise_type in ['squat', 'bench_press', 'deadlift']:
            if self.weight < 50:
                return '初学者'
            elif self.weight < 100:
                return '进阶者'
            elif self.weight < 150:
                return '中级者'
            elif self.weight < 200:
                return '高级者'
            else:
                return '专家级'
        return '标准'


class FitnessStrengthProfile(models.Model):
    """健身力量档案模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 三大项最佳记录
    squat_1rm = models.FloatField(null=True, blank=True, verbose_name='深蹲1RM(kg)')
    squat_1rm_date = models.DateField(null=True, blank=True, verbose_name='深蹲1RM日期')
    bench_press_1rm = models.FloatField(null=True, blank=True, verbose_name='卧推1RM(kg)')
    bench_press_1rm_date = models.DateField(null=True, blank=True, verbose_name='卧推1RM日期')
    deadlift_1rm = models.FloatField(null=True, blank=True, verbose_name='硬拉1RM(kg)')
    deadlift_1rm_date = models.DateField(null=True, blank=True, verbose_name='硬拉1RM日期')
    
    # 总重量
    total_1rm = models.FloatField(null=True, blank=True, verbose_name='三大项总重量(kg)')
    
    # 体重相关
    bodyweight = models.FloatField(null=True, blank=True, verbose_name='记录时体重(kg)')
    bodyweight_date = models.DateField(null=True, blank=True, verbose_name='体重记录日期')
    
    # 力量系数
    strength_coefficient = models.FloatField(null=True, blank=True, verbose_name='力量系数(总重量/体重)')
    
    # 目标设定
    squat_goal = models.FloatField(null=True, blank=True, verbose_name='深蹲目标(kg)')
    bench_press_goal = models.FloatField(null=True, blank=True, verbose_name='卧推目标(kg)')
    deadlift_goal = models.FloatField(null=True, blank=True, verbose_name='硬拉目标(kg)')
    total_goal = models.FloatField(null=True, blank=True, verbose_name='总重量目标(kg)')
    
    # 统计信息
    total_workouts = models.IntegerField(default=0, verbose_name='总训练次数')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    total_duration = models.IntegerField(default=0, verbose_name='总训练时长(分钟)')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '健身力量档案'
        verbose_name_plural = '健身力量档案'
    
    def __str__(self):
        return f"{self.user.username} - 力量档案"
    
    def update_stats(self):
        """更新统计数据"""
        from datetime import datetime, timedelta
        
        # 更新总训练次数
        self.total_workouts = ExerciseWeightRecord.objects.filter(user=self.user).count()
        
        # 更新连续天数
        records = ExerciseWeightRecord.objects.filter(user=self.user).order_by('-workout_date')
        if records.exists():
            current_streak = 0
            longest_streak = 0
            temp_streak = 0
            current_date = datetime.now().date()
            
            for i, record in enumerate(records):
                if i == 0:
                    if record.workout_date == current_date:
                        temp_streak = 1
                    else:
                        break
                else:
                    prev_record = records[i-1]
                    if (prev_record.workout_date - record.workout_date).days == 1:
                        temp_streak += 1
                    else:
                        break
            
            self.current_streak = temp_streak
            
            # 计算最长连续天数
            dates = list(records.values_list('workout_date', flat=True).distinct())
            if dates:
                dates.sort(reverse=True)
                temp_streak = 1
                longest_streak = 1
                
                for i in range(1, len(dates)):
                    if (dates[i-1] - dates[i]).days == 1:
                        temp_streak += 1
                        longest_streak = max(longest_streak, temp_streak)
                    else:
                        temp_streak = 1
                
                self.longest_streak = longest_streak
        
        self.save()
    
    def update_1rm_records(self):
        """更新1RM记录 - 优化版本"""
        from django.db.models import Max, Q
        
        # 使用单次查询获取所有运动类型的最佳记录
        best_records = ExerciseWeightRecord.objects.filter(
            user=self.user,
            exercise_type__in=['squat', 'bench_press', 'deadlift']
        ).values('exercise_type').annotate(
            max_weight=Max('weight'),
            latest_date=Max('workout_date')
        ).order_by('exercise_type')
        
        # 批量获取最佳记录的详细信息
        exercise_types = ['squat', 'bench_press', 'deadlift']
        for exercise_type in exercise_types:
            best_record = ExerciseWeightRecord.objects.filter(
                user=self.user,
                exercise_type=exercise_type
            ).order_by('-weight', '-workout_date').first()
            
            if best_record:
                setattr(self, f'{exercise_type}_1rm', best_record.get_estimated_1rm())
                setattr(self, f'{exercise_type}_1rm_date', best_record.workout_date)
        
        # 更新总重量
        if self.squat_1rm and self.bench_press_1rm and self.deadlift_1rm:
            self.total_1rm = self.squat_1rm + self.bench_press_1rm + self.deadlift_1rm
        
        # 更新力量系数
        if self.total_1rm and self.bodyweight:
            self.strength_coefficient = round(self.total_1rm / self.bodyweight, 2)
        
        self.save()
    
    def get_strength_level(self):
        """获取力量等级"""
        if not self.total_1rm:
            return '未记录'
        
        if self.total_1rm < 200:
            return '初学者'
        elif self.total_1rm < 400:
            return '进阶者'
        elif self.total_1rm < 600:
            return '中级者'
        elif self.total_1rm < 800:
            return '高级者'
        else:
            return '专家级'
    
    def get_progress_percentage(self, exercise_type):
        """获取进度百分比"""
        current = getattr(self, f'{exercise_type}_1rm', 0) or 0
        goal = getattr(self, f'{exercise_type}_goal', 0) or 0
        
        if goal == 0:
            return 0
        
        return min(round((current / goal) * 100, 1), 100)


class ShipBaoWantItem(models.Model):
    """船宝商品想要记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, related_name='want_users', verbose_name='商品')
    message = models.TextField(blank=True, null=True, verbose_name='留言')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='想要时间')
    
    class Meta:
        unique_together = ['user', 'item']
        ordering = ['-created_at']
        verbose_name = '商品想要记录'
        verbose_name_plural = '商品想要记录'
    
    def __str__(self):
        return f"{self.user.username} 想要 {self.item.title}"


class ShipBaoFavorite(models.Model):
    """船宝商品收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, verbose_name='商品')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        unique_together = ['user', 'item']
        ordering = ['-created_at']
        verbose_name = '商品收藏'
        verbose_name_plural = '商品收藏'
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.item.title}"