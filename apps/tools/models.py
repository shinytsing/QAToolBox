from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random


class ToolUsageLog(models.Model):
    TOOL_CHOICES = [
        ('TEST_CASE', 'Test Case Generator'),
        ('QUALITY_CHECK', 'Code Quality Check'),
        ('PERF_TEST', 'Performance Simulator'),
        ('REDBOOK', 'RedBook Generator'),  # 添加小红书生成器
    ]
    # 在 models.py 中添加
    preview_image = models.ImageField(upload_to='tool_previews/', null=True, blank=True)
    raw_response = models.TextField(null=True, blank=True)  # 添加原始响应字段
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tool_type = models.CharField(max_length=20, choices=TOOL_CHOICES)
    input_data = models.TextField()
    output_file = models.FileField(upload_to='tool_outputs/')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class SocialMediaSubscription(models.Model):
    """社交媒体订阅模型"""
    PLATFORM_CHOICES = [
        ('xiaohongshu', '小红书'),
        ('douyin', '抖音'),
        ('netease', '网易云音乐'),
        ('weibo', '微博'),
        ('bilibili', 'B站'),
        ('zhihu', '知乎'),
    ]
    
    SUBSCRIPTION_TYPE_CHOICES = [
        ('newPosts', '新动态'),
        ('newFollowers', '新粉丝'),
        ('newFollowing', '新关注'),
        ('profileChanges', '资料变化'),
    ]
    
    # 订阅类型详细说明
    SUBSCRIPTION_TYPE_DESCRIPTIONS = {
        'newPosts': '用户发布的新内容，包括帖子、视频、文章等',
        'newFollowers': '有新用户关注了被订阅者（被订阅者获得新粉丝）',
        'newFollowing': '被订阅者新关注了其他用户（被订阅者关注了别人）',
        'profileChanges': '用户资料信息的变化，如头像、昵称、简介等',
    }
    
    FREQUENCY_CHOICES = [
        (5, '5分钟'),
        (15, '15分钟'),
        (30, '30分钟'),
        (60, '1小时'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('paused', '暂停'),
        ('error', '错误'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name='平台')
    target_user_id = models.CharField(max_length=100, verbose_name='目标用户ID')
    target_user_name = models.CharField(max_length=200, verbose_name='目标用户名')
    subscription_types = models.JSONField(default=list, verbose_name='订阅类型')
    check_frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=15, verbose_name='检查频率')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    last_check = models.DateTimeField(auto_now=True, verbose_name='最后检查时间')
    last_change = models.DateTimeField(null=True, blank=True, verbose_name='最后变化时间')
    avatar_url = models.URLField(blank=True, null=True, verbose_name='头像URL')
    
    # 用于存储上次检查的数据，避免重复通知
    last_follower_count = models.IntegerField(default=0, blank=True, null=True, verbose_name='上次粉丝数')
    last_video_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='上次最新视频ID')
    last_following_count = models.IntegerField(default=0, blank=True, null=True, verbose_name='上次关注数')
    last_profile_data = models.JSONField(default=dict, blank=True, null=True, verbose_name='上次资料数据')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        unique_together = ['user', 'platform', 'target_user_id']
        ordering = ['-created_at']
        verbose_name = '社交媒体订阅'
        verbose_name_plural = '社交媒体订阅'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()} - {self.target_user_name}"


class SocialMediaNotification(models.Model):
    """社交媒体通知模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('newPosts', '新动态'),
        ('newFollowers', '新粉丝'),
        ('newFollowing', '新关注'),
        ('profileChanges', '资料变化'),
    ]
    
    # 通知类型详细说明
    NOTIFICATION_TYPE_DESCRIPTIONS = {
        'newPosts': '用户发布的新内容，包括帖子、视频、文章等',
        'newFollowers': '有新用户关注了被订阅者（被订阅者获得新粉丝）',
        'newFollowing': '被订阅者新关注了其他用户（被订阅者关注了别人）',
        'profileChanges': '用户资料信息的变化，如头像、昵称、简介等',
    }
    
    subscription = models.ForeignKey(SocialMediaSubscription, on_delete=models.CASCADE, verbose_name='订阅')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    # 新增字段用于存储详细内容
    post_content = models.TextField(blank=True, null=True, verbose_name='帖子内容')
    post_images = models.JSONField(default=list, blank=True, null=True, verbose_name='帖子图片')
    post_video_url = models.URLField(blank=True, null=True, verbose_name='视频链接')
    post_tags = models.JSONField(default=list, blank=True, null=True, verbose_name='帖子标签')
    post_likes = models.IntegerField(default=0, blank=True, null=True, verbose_name='点赞数')
    post_comments = models.IntegerField(default=0, blank=True, null=True, verbose_name='评论数')
    post_shares = models.IntegerField(default=0, blank=True, null=True, verbose_name='分享数')
    
    # 新粉丝相关字段
    follower_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='粉丝名称')
    follower_avatar = models.URLField(blank=True, null=True, verbose_name='粉丝头像')
    follower_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='粉丝ID')
    follower_count = models.IntegerField(default=0, blank=True, null=True, verbose_name='当前粉丝总数')
    
    # 新关注相关字段
    following_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='关注对象名称')
    following_avatar = models.URLField(blank=True, null=True, verbose_name='关注对象头像')
    following_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='关注对象ID')
    following_count = models.IntegerField(default=0, blank=True, null=True, verbose_name='当前关注总数')
    
    # 资料变化相关字段
    profile_changes = models.JSONField(default=dict, blank=True, null=True, verbose_name='资料变化详情')
    old_profile_data = models.JSONField(default=dict, blank=True, null=True, verbose_name='变化前资料')
    new_profile_data = models.JSONField(default=dict, blank=True, null=True, verbose_name='变化后资料')
    
    # 通用字段
    external_url = models.URLField(blank=True, null=True, verbose_name='外部链接')
    platform_specific_data = models.JSONField(default=dict, blank=True, null=True, verbose_name='平台特定数据')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '社交媒体通知'
        verbose_name_plural = '社交媒体通知'
    
    def __str__(self):
        return f"{self.subscription.target_user_name} - {self.get_notification_type_display()} - {self.title}"


class SocialMediaPlatformConfig(models.Model):
    """社交媒体平台配置模型"""
    platform = models.CharField(max_length=20, choices=SocialMediaSubscription.PLATFORM_CHOICES, verbose_name='平台')
    api_endpoint = models.URLField(verbose_name='API端点')
    api_key = models.CharField(max_length=200, blank=True, null=True, verbose_name='API密钥')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    rate_limit = models.IntegerField(default=100, verbose_name='速率限制(次/小时)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        unique_together = ['platform']
        verbose_name = '平台配置'
        verbose_name_plural = '平台配置'
    
    def __str__(self):
        return f"{self.get_platform_display()} 配置"


class LifeDiaryEntry(models.Model):
    """生活日记条目模型"""
    MOOD_CHOICES = [
        ('happy', '开心'),
        ('calm', '平静'),
        ('excited', '兴奋'),
        ('sad', '难过'),
        ('angry', '生气'),
        ('neutral', '一般'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    date = models.DateField(default=timezone.now, verbose_name='日期')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, verbose_name='心情')
    mood_note = models.TextField(blank=True, null=True, verbose_name='心情备注')
    tags = models.JSONField(default=list, verbose_name='标签')
    question_answers = models.JSONField(default=list, verbose_name='问题回答')
    music_recommendation = models.TextField(blank=True, null=True, verbose_name='音乐推荐')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = '生活日记'
        verbose_name_plural = '生活日记'
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.title}"
    
    def get_mood_emoji(self):
        """获取心情对应的表情符号"""
        mood_emojis = {
            'happy': '😊',
            'calm': '😌',
            'excited': '⭐',
            'sad': '😢',
            'angry': '😠',
            'neutral': '😐'
        }
        return mood_emojis.get(self.mood, '😐')
    
    def get_word_count(self):
        """获取内容字数"""
        return len(self.content) if self.content else 0
    
    def get_tags_display(self):
        """获取标签显示文本"""
        return ', '.join(self.tags) if self.tags else '无标签'


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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='目标标题')
    description = models.TextField(blank=True, null=True, verbose_name='目标描述')
    category = models.CharField(max_length=20, choices=GOAL_CATEGORY_CHOICES, verbose_name='目标类别')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='daily', verbose_name='目标类型')
    status = models.CharField(max_length=20, choices=GOAL_STATUS_CHOICES, default='active', verbose_name='状态')
    start_date = models.DateField(null=True, blank=True, verbose_name='开始日期')
    target_date = models.DateField(null=True, blank=True, verbose_name='目标日期')
    progress = models.IntegerField(default=0, verbose_name='进度百分比')
    priority = models.IntegerField(default=5, verbose_name='优先级(1-10)')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='难度等级')
    milestones = models.JSONField(default=list, verbose_name='里程碑')
    tags = models.JSONField(default=list, verbose_name='标签')
    reminder_enabled = models.BooleanField(default=True, verbose_name='启用提醒')
    reminder_frequency = models.CharField(max_length=20, default='daily', verbose_name='提醒频率')
    reminder_time = models.TimeField(default='09:00', verbose_name='提醒时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = '生活目标'
        verbose_name_plural = '生活目标'
    
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


class LifeGoalProgress(models.Model):
    """生活目标进度记录模型"""
    goal = models.ForeignKey(LifeGoal, on_delete=models.CASCADE, verbose_name='目标')
    date = models.DateField(auto_now_add=True, verbose_name='日期')
    progress_value = models.IntegerField(verbose_name='进度值')
    notes = models.TextField(blank=True, null=True, verbose_name='进度备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ['goal', 'date']
        ordering = ['-date']
        verbose_name = '目标进度'
        verbose_name_plural = '目标进度'
    
    def __str__(self):
        return f"{self.goal.title} - {self.date} - {self.progress_value}%"


class LifeStatistics(models.Model):
    """生活统计数据模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    date = models.DateField(auto_now_add=True, verbose_name='日期')
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
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - 统计"


class ChatRoom(models.Model):
    """聊天室模型"""
    ROOM_STATUS_CHOICES = [
        ('waiting', '等待匹配'),
        ('active', '活跃'),
        ('ended', '已结束'),
    ]
    
    room_id = models.CharField(max_length=50, unique=True, verbose_name='房间ID')
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user1', verbose_name='用户1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user2', verbose_name='用户2', null=True, blank=True)
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='waiting', verbose_name='房间状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    
    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"聊天室 {self.room_id}"
    
    @property
    def is_full(self):
        return self.user2 is not None
    
    @property
    def participants(self):
        participants = [self.user1]
        if self.user2:
            participants.append(self.user2)
        return participants

class ChatMessage(models.Model):
    """聊天消息模型"""
    MESSAGE_TYPES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
        ('emoji', '表情'),
        ('video', '视频'),
        ('audio', '语音'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name='聊天室')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    file_url = models.URLField(blank=True, null=True, verbose_name='文件URL')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"

class UserOnlineStatus(models.Model):
    """用户在线状态模型"""
    STATUS_CHOICES = [
        ('online', '在线'),
        ('busy', '忙碌'),
        ('away', '离开'),
        ('offline', '离线'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='online_status', verbose_name='用户')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline', verbose_name='在线状态')
    last_seen = models.DateTimeField(auto_now=True, verbose_name='最后在线时间')
    is_typing = models.BooleanField(default=False, verbose_name='是否正在输入')
    current_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='online_users', verbose_name='当前房间')
    is_online = models.BooleanField(default=False, verbose_name='是否在线')
    match_number = models.CharField(max_length=4, null=True, blank=True, verbose_name='匹配数字')
    
    class Meta:
        verbose_name = '用户在线状态'
        verbose_name_plural = '用户在线状态'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

class HeartLinkRequest(models.Model):
    """心动链接请求模型"""
    STATUS_CHOICES = [
        ('pending', '等待中'),
        ('matching', '匹配中'),
        ('matched', '已匹配'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
    ]
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heart_link_requests', verbose_name='请求者')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    matched_at = models.DateTimeField(null=True, blank=True, verbose_name='匹配时间')
    matched_with = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_heart_links', verbose_name='匹配用户')
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.SET_NULL, null=True, blank=True, related_name='heart_link_requests', verbose_name='聊天室')
    
    class Meta:
        verbose_name = '心动链接请求'
        verbose_name_plural = '心动链接请求'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.requester.username} 的心动链接请求"
    
    @property
    def is_expired(self):
        """检查请求是否过期（10分钟）"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)


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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    title = models.CharField(max_length=200, verbose_name='成就标题')
    description = models.TextField(blank=True, null=True, verbose_name='成就描述')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES, verbose_name='成就类型')
    level = models.CharField(max_length=20, choices=ACHIEVEMENT_LEVEL_CHOICES, default='bronze', verbose_name='成就等级')
    icon = models.CharField(max_length=50, default='fas fa-trophy', verbose_name='成就图标')
    is_custom = models.BooleanField(default=False, verbose_name='是否自定义')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='获得时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户成就'
        verbose_name_plural = '用户成就'
    
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


class DouyinVideoAnalysis(models.Model):
    """抖音视频分析模型"""
    ANALYSIS_STATUS_CHOICES = [
        ('pending', '待分析'),
        ('processing', '分析中'),
        ('completed', '已完成'),
        ('failed', '分析失败'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    up主_id = models.CharField(max_length=100, verbose_name='UP主ID')
    up主_name = models.CharField(max_length=200, verbose_name='UP主名称')
    up主_url = models.URLField(verbose_name='UP主主页URL')
    analysis_status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, default='pending', verbose_name='分析状态')
    
    # 分析结果
    video_count = models.IntegerField(default=0, verbose_name='视频总数')
    total_likes = models.BigIntegerField(default=0, verbose_name='总点赞数')
    total_comments = models.BigIntegerField(default=0, verbose_name='总评论数')
    total_shares = models.BigIntegerField(default=0, verbose_name='总分享数')
    follower_count = models.BigIntegerField(default=0, verbose_name='粉丝数')
    
    # 内容分析
    content_themes = models.JSONField(default=list, verbose_name='内容主题')
    video_tags = models.JSONField(default=list, verbose_name='视频标签')
    popular_videos = models.JSONField(default=list, verbose_name='热门视频')
    posting_frequency = models.CharField(max_length=50, blank=True, null=True, verbose_name='发布频率')
    
    # 截图和预览
    screenshots = models.JSONField(default=list, verbose_name='视频截图')
    product_preview = models.TextField(blank=True, null=True, verbose_name='产品功能预览')
    analysis_summary = models.TextField(blank=True, null=True, verbose_name='分析总结')
    
    # 错误信息
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '抖音视频分析'
        verbose_name_plural = '抖音视频分析'
    
    def __str__(self):
        return f"{self.up主_name} - {self.get_analysis_status_display()}"
    
    def get_progress_percentage(self):
        """获取分析进度百分比"""
        if self.analysis_status == 'completed':
            return 100
        elif self.analysis_status == 'failed':
            return 0
        elif self.analysis_status == 'processing':
            return 50
        else:
            return 0


class DouyinVideo(models.Model):
    """抖音视频详情模型"""
    analysis = models.ForeignKey(DouyinVideoAnalysis, on_delete=models.CASCADE, related_name='videos', verbose_name='分析记录')
    video_id = models.CharField(max_length=100, verbose_name='视频ID')
    video_url = models.URLField(verbose_name='视频URL')
    title = models.CharField(max_length=500, verbose_name='视频标题')
    description = models.TextField(blank=True, null=True, verbose_name='视频描述')
    
    # 统计数据
    likes = models.BigIntegerField(default=0, verbose_name='点赞数')
    comments = models.BigIntegerField(default=0, verbose_name='评论数')
    shares = models.BigIntegerField(default=0, verbose_name='分享数')
    views = models.BigIntegerField(default=0, verbose_name='播放量')
    
    # 内容分析
    tags = models.JSONField(default=list, verbose_name='标签')
    theme = models.CharField(max_length=100, blank=True, null=True, verbose_name='主题')
    duration = models.IntegerField(default=0, verbose_name='时长(秒)')
    
    # 截图
    thumbnail_url = models.URLField(blank=True, null=True, verbose_name='缩略图URL')
    screenshot_urls = models.JSONField(default=list, verbose_name='截图URL列表')
    
    # 时间戳
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-likes']
        verbose_name = '抖音视频'
        verbose_name_plural = '抖音视频'
    
    def __str__(self):
        return f"{self.title} - {self.likes}赞"
    
    def get_engagement_rate(self):
        """计算互动率"""
        if self.views > 0:
            return round((self.likes + self.comments + self.shares) / self.views * 100, 2)
        return 0


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


class TravelGuide(models.Model):
    """旅游攻略模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    destination = models.CharField(max_length=200, verbose_name='目的地')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 攻略内容
    must_visit_attractions = models.JSONField(default=list, verbose_name='必去景点')
    food_recommendations = models.JSONField(default=list, verbose_name='美食推荐')
    transportation_guide = models.JSONField(default=dict, verbose_name='交通指南')
    hidden_gems = models.JSONField(default=list, verbose_name='隐藏玩法')
    weather_info = models.JSONField(default=dict, verbose_name='天气信息')
    
    # Overview信息字段
    destination_info = models.JSONField(default=dict, verbose_name='目的地基本信息')
    currency_info = models.JSONField(default=dict, verbose_name='汇率信息') 
    timezone_info = models.JSONField(default=dict, verbose_name='时区信息')
    
    best_time_to_visit = models.TextField(blank=True, null=True, verbose_name='最佳旅行时间')
    budget_estimate = models.JSONField(default=dict, verbose_name='预算估算')
    travel_tips = models.JSONField(default=list, verbose_name='旅行贴士')
    
    # 详细攻略
    detailed_guide = models.JSONField(default=dict, verbose_name='详细攻略')
    daily_schedule = models.JSONField(default=list, verbose_name='每日行程')
    activity_timeline = models.JSONField(default=list, verbose_name='活动时间线')
    cost_breakdown = models.JSONField(default=dict, verbose_name='费用明细')
    
    # 个性化设置
    travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
    budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
    budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
    budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 状态
    is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
    is_exported = models.BooleanField(default=False, verbose_name='是否已导出')
    
    # 缓存相关
    is_cached = models.BooleanField(default=False, verbose_name='是否缓存数据')
    cache_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='缓存来源')
    cache_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='缓存过期时间')
    api_used = models.CharField(max_length=50, default='deepseek', verbose_name='使用的API')
    generation_mode = models.CharField(max_length=20, default='standard', verbose_name='生成模式')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '旅游攻略'
        verbose_name_plural = '旅游攻略'
    
    def __str__(self):
        return f"{self.user.username} - {self.destination}"
    
    def get_attractions_count(self):
        return len(self.must_visit_attractions)
    
    def get_food_count(self):
        return len(self.food_recommendations)
    
    def get_hidden_gems_count(self):
        return len(self.hidden_gems)
    
    def is_cache_valid(self):
        """检查缓存是否有效"""
        if not self.is_cached or not self.cache_expires_at:
            return False
        from django.utils import timezone
        return timezone.now() < self.cache_expires_at
    
    def get_cache_status(self):
        """获取缓存状态"""
        if not self.is_cached:
            return 'not_cached'
        if self.is_cache_valid():
            return 'valid'
        return 'expired'


class TravelGuideCache(models.Model):
    """旅游攻略缓存模型"""
    CACHE_SOURCE_CHOICES = [
        ('standard_api', '标准API生成'),
        ('fast_api', '快速API生成'),
        ('cached_data', '缓存数据'),
        ('fallback_data', '备用数据'),
    ]
    
    API_SOURCE_CHOICES = [
        ('deepseek', 'DeepSeek API'),
        ('openai', 'OpenAI API'),
        ('claude', 'Claude API'),
        ('gemini', 'Gemini API'),
        ('free_api_1', '免费API 1'),
        ('free_api_2', '免费API 2'),
        ('free_api_3', '免费API 3'),
        ('fallback', '备用数据'),
    ]
    
    # 缓存键（用于查找相同条件的攻略）
    destination = models.CharField(max_length=200, verbose_name='目的地')
    travel_style = models.CharField(max_length=50, verbose_name='旅行风格')
    budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
    budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
    budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
    budget_range = models.CharField(max_length=50, verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, verbose_name='旅行时长')
    interests_hash = models.CharField(max_length=64, verbose_name='兴趣标签哈希')
    
    # 缓存数据
    guide_data = models.JSONField(verbose_name='攻略数据')
    api_used = models.CharField(max_length=50, choices=API_SOURCE_CHOICES, verbose_name='使用的API')
    cache_source = models.CharField(max_length=50, choices=CACHE_SOURCE_CHOICES, verbose_name='缓存来源')
    
    # 缓存元数据
    generation_time = models.FloatField(verbose_name='生成时间(秒)')
    data_quality_score = models.FloatField(default=0.0, verbose_name='数据质量评分')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    last_accessed = models.DateTimeField(auto_now=True, verbose_name='最后访问时间')
    
    class Meta:
        unique_together = ['destination', 'travel_style', 'budget_min', 'budget_max', 'budget_range', 'travel_duration', 'interests_hash']
        ordering = ['-last_accessed']
        verbose_name = '旅游攻略缓存'
        verbose_name_plural = '旅游攻略缓存'
        indexes = [
            models.Index(fields=['destination', 'travel_style', 'budget_min', 'budget_max', 'travel_duration']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['api_used']),
        ]
    
    def __str__(self):
        return f"{self.destination} - {self.travel_style} - {self.api_used}"
    
    def is_expired(self):
        """检查缓存是否过期"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'last_accessed'])
    
    def get_cache_key(self):
        """获取缓存键"""
        return f"{self.destination}_{self.travel_style}_{self.budget_min}_{self.budget_max}_{self.travel_duration}_{self.interests_hash}"


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


class TravelReview(models.Model):
    """旅游攻略评价模型"""
    travel_guide = models.ForeignKey(TravelGuide, on_delete=models.CASCADE, verbose_name='旅游攻略')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
    comment = models.TextField(blank=True, null=True, verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ['travel_guide', 'user']
        ordering = ['-created_at']
        verbose_name = '旅游攻略评价'
        verbose_name_plural = '旅游攻略评价'
    
    def __str__(self):
        return f"{self.user.username} - {self.travel_guide.destination} - {self.rating}星"


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


class TarotCard(models.Model):
    """塔罗牌模型"""
    CARD_TYPE_CHOICES = [
        ('major', '大阿卡纳'),
        ('minor', '小阿卡纳'),
    ]
    
    SUIT_CHOICES = [
        ('wands', '权杖'),
        ('cups', '圣杯'),
        ('swords', '宝剑'),
        ('pentacles', '钱币'),
        ('major', '大阿卡纳'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='牌名')
    name_en = models.CharField(max_length=100, verbose_name='英文名')
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES, verbose_name='牌类型')
    suit = models.CharField(max_length=20, choices=SUIT_CHOICES, verbose_name='花色')
    number = models.IntegerField(verbose_name='数字')
    image_url = models.URLField(blank=True, null=True, verbose_name='牌面图片')
    
    # 牌义
    upright_meaning = models.TextField(verbose_name='正位含义')
    reversed_meaning = models.TextField(verbose_name='逆位含义')
    keywords = models.JSONField(default=list, verbose_name='关键词')
    
    # 详细解读
    description = models.TextField(blank=True, null=True, verbose_name='牌面描述')
    symbolism = models.TextField(blank=True, null=True, verbose_name='象征意义')
    advice = models.TextField(blank=True, null=True, verbose_name='建议')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['card_type', 'suit', 'number']
        verbose_name = '塔罗牌'
        verbose_name_plural = '塔罗牌'
    
    def __str__(self):
        return f"{self.name} ({self.get_suit_display()})"


class TarotSpread(models.Model):
    """塔罗牌阵模型"""
    SPREAD_TYPE_CHOICES = [
        ('classic', '经典牌阵'),
        ('situation', '情景牌阵'),
        ('custom', '自定义牌阵'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='牌阵名称')
    spread_type = models.CharField(max_length=20, choices=SPREAD_TYPE_CHOICES, verbose_name='牌阵类型')
    description = models.TextField(verbose_name='牌阵描述')
    card_count = models.IntegerField(verbose_name='牌数')
    positions = models.JSONField(default=list, verbose_name='位置定义')
    image_url = models.URLField(blank=True, null=True, verbose_name='牌阵图片')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['spread_type', 'card_count']
        verbose_name = '塔罗牌阵'
        verbose_name_plural = '塔罗牌阵'
    
    def __str__(self):
        return f"{self.name} ({self.card_count}张牌)"


class TarotReading(models.Model):
    """塔罗牌占卜记录模型"""
    READING_TYPE_CHOICES = [
        ('daily', '每日运势'),
        ('love', '爱情占卜'),
        ('career', '事业占卜'),
        ('health', '健康占卜'),
        ('spiritual', '灵性占卜'),
        ('custom', '自定义占卜'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, verbose_name='牌阵')
    reading_type = models.CharField(max_length=20, choices=READING_TYPE_CHOICES, verbose_name='占卜类型')
    question = models.TextField(verbose_name='问题')
    
    # 抽牌结果
    drawn_cards = models.JSONField(default=list, verbose_name='抽到的牌')
    card_positions = models.JSONField(default=list, verbose_name='牌的位置')
    
    # AI解读结果
    ai_interpretation = models.TextField(blank=True, null=True, verbose_name='AI解读')
    detailed_reading = models.JSONField(default=dict, verbose_name='详细解读')
    
    # 用户反馈
    user_feedback = models.TextField(blank=True, null=True, verbose_name='用户反馈')
    accuracy_rating = models.IntegerField(blank=True, null=True, verbose_name='准确度评分')
    
    # 心情标签
    mood_before = models.CharField(max_length=50, blank=True, null=True, verbose_name='占卜前心情')
    mood_after = models.CharField(max_length=50, blank=True, null=True, verbose_name='占卜后心情')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='占卜时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '塔罗占卜'
        verbose_name_plural = '塔罗占卜'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_reading_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"


class TarotDiary(models.Model):
    """塔罗日记模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    reading = models.ForeignKey(TarotReading, on_delete=models.CASCADE, verbose_name='占卜记录')
    title = models.CharField(max_length=200, verbose_name='日记标题')
    content = models.TextField(verbose_name='日记内容')
    tags = models.JSONField(default=list, verbose_name='标签')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '塔罗日记'
        verbose_name_plural = '塔罗日记'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class TarotEnergyCalendar(models.Model):
    """塔罗能量日历模型"""
    ENERGY_TYPE_CHOICES = [
        ('new_moon', '新月'),
        ('full_moon', '满月'),
        ('eclipse', '日食/月食'),
        ('solstice', '夏至/冬至'),
        ('equinox', '春分/秋分'),
        ('daily', '日常能量'),
    ]
    
    date = models.DateField(verbose_name='日期')
    energy_type = models.CharField(max_length=20, choices=ENERGY_TYPE_CHOICES, verbose_name='能量类型')
    energy_level = models.IntegerField(choices=[(i, i) for i in range(1, 11)], verbose_name='能量等级')
    description = models.TextField(verbose_name='能量描述')
    recommended_cards = models.JSONField(default=list, verbose_name='推荐牌')
    special_reading = models.TextField(blank=True, null=True, verbose_name='特殊占卜')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ['date', 'energy_type']
        ordering = ['-date']
        verbose_name = '塔罗能量日历'
        verbose_name_plural = '塔罗能量日历'
    
    def __str__(self):
        return f"{self.date} - {self.get_energy_type_display()}"


class TarotCommunity(models.Model):
    """塔罗社区模型"""
    POST_TYPE_CHOICES = [
        ('story', '故事分享'),
        ('question', '解牌求助'),
        ('experience', '经验分享'),
        ('discussion', '讨论'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name='帖子类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    tags = models.JSONField(default=list, verbose_name='标签')
    is_anonymous = models.BooleanField(default=False, verbose_name='是否匿名')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    comments_count = models.IntegerField(default=0, verbose_name='评论数')
    is_featured = models.BooleanField(default=False, verbose_name='是否精选')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '塔罗社区'
        verbose_name_plural = '塔罗社区'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class TarotCommunityComment(models.Model):
    """塔罗社区评论模型"""
    post = models.ForeignKey(TarotCommunity, on_delete=models.CASCADE, related_name='comments', verbose_name='帖子')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    content = models.TextField(verbose_name='评论内容')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name='父评论')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '塔罗社区评论'
        verbose_name_plural = '塔罗社区评论'
    
    def __str__(self):
        return f"{self.user.username} 回复 {self.post.title}"


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

class RelationshipTag(models.Model):
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


class PersonProfile(models.Model):
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
    relationship_tags = models.ManyToManyField(RelationshipTag, blank=True, verbose_name='关系标签')
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


class Interaction(models.Model):
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
    person = models.ForeignKey(PersonProfile, on_delete=models.CASCADE, related_name='interactions', verbose_name='相关人物')
    
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
    other_participants = models.ManyToManyField(PersonProfile, blank=True, related_name='group_interactions', verbose_name='其他参与者')
    
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


class ImportantMoment(models.Model):
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
    person = models.ForeignKey(PersonProfile, on_delete=models.CASCADE, related_name='important_moments', verbose_name='相关人物')
    related_interaction = models.OneToOneField(Interaction, on_delete=models.CASCADE, blank=True, null=True, verbose_name='关联互动记录')
    
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
    other_participants = models.ManyToManyField(PersonProfile, blank=True, related_name='shared_moments', verbose_name='其他参与者')
    
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


class RelationshipStatistics(models.Model):
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
        profiles = PersonProfile.objects.filter(user=self.user)
        interactions = Interaction.objects.filter(user=self.user)
        moments = ImportantMoment.objects.filter(user=self.user)
        
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


class RelationshipReminder(models.Model):
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
    person = models.ForeignKey(PersonProfile, on_delete=models.CASCADE, related_name='reminders', verbose_name='相关人物')
    
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
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 基础信息
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='健身昵称')
    avatar = models.ImageField(upload_to='fitness_avatars/', blank=True, null=True, verbose_name='头像')
    bio = models.TextField(blank=True, null=True, verbose_name='个人简介')
    
    # 健身信息
    fitness_level = models.CharField(max_length=20, choices=[
        ('beginner', '初学者'),
        ('intermediate', '进阶者'),
        ('advanced', '高级者'),
        ('expert', '专家级')
    ], default='beginner', verbose_name='健身水平')
    
    primary_goals = models.JSONField(default=list, verbose_name='主要目标', help_text='如：增肌、减脂、塑形等')
    favorite_workouts = models.JSONField(default=list, verbose_name='喜欢的运动类型')
    
    # 统计数据
    total_workouts = models.IntegerField(default=0, verbose_name='总训练次数')
    total_duration = models.IntegerField(default=0, verbose_name='总训练时长(分钟)')
    current_streak = models.IntegerField(default=0, verbose_name='当前连续天数')
    longest_streak = models.IntegerField(default=0, verbose_name='最长连续天数')
    
    # 社交设置
    is_public_profile = models.BooleanField(default=True, verbose_name='是否公开档案')
    allow_followers = models.BooleanField(default=True, verbose_name='允许关注')
    show_achievements = models.BooleanField(default=True, verbose_name='显示成就')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '健身用户档案'
        verbose_name_plural = '健身用户档案'
    
    def __str__(self):
        return f"{self.user.username} 的健身档案"
    
    def get_display_name(self):
        """获取显示名称"""
        return self.nickname or self.user.username
    
    def update_stats(self):
        """更新统计数据"""
        checkins = CheckInCalendar.objects.filter(
            user=self.user,
            calendar_type='fitness',
            status='completed'
        )
        
        self.total_workouts = checkins.count()
        self.total_duration = sum(
            checkin.detail.duration or 0 
            for checkin in checkins 
            if hasattr(checkin, 'detail') and checkin.detail
        )
        
        # 计算连续天数
        streak, _ = CheckInStreak.objects.get_or_create(
            user=self.user,
            calendar_type='fitness',
            defaults={'current_streak': 0, 'longest_streak': 0}
        )
        
        self.current_streak = streak.current_streak
        self.longest_streak = streak.longest_streak
        
        self.save()


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
    
    class Meta:
        unique_together = ['follower', 'following']
        verbose_name = '健身关注关系'
        verbose_name_plural = '健身关注关系'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} 关注了 {self.following.username}"