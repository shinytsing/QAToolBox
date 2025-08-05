from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
        self.virtual_wealth = (self.code_lines * 0.01) + (self.page_views * 0.001) + (self.donations * 1)
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
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 状态
    is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
    is_exported = models.BooleanField(default=False, verbose_name='是否已导出')
    
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