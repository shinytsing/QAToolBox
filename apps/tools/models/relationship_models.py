from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    
    def is_overdue(self):
        """检查是否过期"""
        from datetime import date
        return self.reminder_date < date.today() and self.status == 'active'
    
    def can_snooze(self):
        """检查是否可以推迟"""
        return self.snooze_count < self.max_snooze and self.status == 'active'
    
    def snooze(self, days=1):
        """推迟提醒"""
        if self.can_snooze():
            from datetime import date, timedelta
            self.reminder_date = self.reminder_date + timedelta(days=days)
            self.snooze_count += 1
            self.save()
            return True
        return False
    
    def mark_completed(self):
        """标记为已完成"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self):
        """取消提醒"""
        self.status = 'cancelled'
        self.save()
