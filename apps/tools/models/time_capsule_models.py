from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class TimeCapsule(models.Model):
    """时光胶囊模型"""
    CAPSULE_TYPES = [
        ('memory', '记忆胶囊'),
        ('wish', '愿望胶囊'),
        ('secret', '秘密胶囊'),
    ]
    
    UNLOCK_CONDITIONS = [
        ('time', '时间解锁'),
        ('location', '位置解锁'),
        ('event', '事件解锁'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', '仅自己'),
        ('public', '公开分享'),
        ('anonymous', '匿名分享'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='time_capsules', db_index=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    emotions = models.JSONField(default=list)  # 存储情绪组合
    location = models.JSONField(null=True, blank=True)  # 存储位置信息
    weather = models.JSONField(null=True, blank=True)  # 存储天气信息
    keywords = models.JSONField(default=list, blank=True)  # 存储AI生成的关键词
    
    # 胶囊设置
    capsule_type = models.CharField(max_length=20, choices=CAPSULE_TYPES, default='memory')
    unlock_condition = models.CharField(max_length=20, choices=UNLOCK_CONDITIONS, default='time')
    unlock_time = models.DateTimeField(null=True, blank=True, db_index=True)  # 添加索引
    unlock_location = models.JSONField(null=True, blank=True)  # 位置解锁条件
    unlock_event = models.CharField(max_length=200, blank=True)  # 事件解锁条件
    
    # 可见性设置
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private', db_index=True)  # 添加索引
    is_anonymous = models.BooleanField(default=False)
    
    # 媒体文件
    images = models.JSONField(default=list, blank=True)  # 存储图片URL列表
    audio = models.URLField(blank=True)  # 音频文件URL
    
    # 状态
    is_locked = models.BooleanField(default=True)
    is_unlocked = models.BooleanField(default=False)
    unlock_count = models.IntegerField(default=0)  # 被解锁次数
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # 添加索引
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '时光胶囊'
        verbose_name_plural = '时光胶囊'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['visibility', 'created_at']),
            models.Index(fields=['unlock_time', 'unlock_condition']),
            models.Index(fields=['emotions'], name='timecapsule_emotions_gin'),
        ]
    
    def __str__(self):
        return f"{self.user.username}的{self.get_capsule_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def can_be_unlocked_by(self, user):
        """检查胶囊是否可以被指定用户解锁"""
        if self.user == user:
            return True
        
        if self.visibility == 'private':
            return False
        
        # 检查时间解锁条件
        if self.unlock_condition == 'time' and self.unlock_time:
            return timezone.now() >= self.unlock_time
        
        # 检查位置解锁条件
        if self.unlock_condition == 'location' and self.unlock_location:
            # 这里需要实现位置距离计算
            pass
        
        return False


class CapsuleUnlock(models.Model):
    """胶囊解锁记录"""
    capsule = models.ForeignKey(TimeCapsule, on_delete=models.CASCADE, related_name='unlocks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='unlocked_capsules')
    unlocked_at = models.DateTimeField(auto_now_add=True)
    location = models.JSONField(null=True, blank=True)  # 解锁时的位置
    
    class Meta:
        unique_together = ['capsule', 'user']
        ordering = ['-unlocked_at']
        verbose_name = '胶囊解锁记录'
        verbose_name_plural = '胶囊解锁记录'
    
    def __str__(self):
        return f"{self.user.username}解锁了{self.capsule.user.username}的胶囊"


class MemoryFragment(models.Model):
    """记忆碎片"""
    FRAGMENT_TYPES = [
        ('text', '文字碎片'),
        ('image', '图片碎片'),
        ('audio', '音频碎片'),
        ('location', '位置碎片'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memory_fragments')
    capsule = models.ForeignKey(TimeCapsule, on_delete=models.CASCADE, related_name='fragments')
    fragment_type = models.CharField(max_length=20, choices=FRAGMENT_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict)  # 存储额外信息
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '记忆碎片'
        verbose_name_plural = '记忆碎片'
    
    def __str__(self):
        return f"{self.user.username}的{self.get_fragment_type_display()}"


class Achievement(models.Model):
    """成就系统"""
    ACHIEVEMENT_TYPES = [
        ('traveler', '时光旅人'),
        ('explorer', '城市探险家'),
        ('prophet', '预言家'),
        ('collector', '记忆收藏家'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)  # 进度值
    
    class Meta:
        unique_together = ['user', 'achievement_type']
        ordering = ['-unlocked_at']
        verbose_name = '成就'
        verbose_name_plural = '成就'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_achievement_type_display()}"


class ParallelMatch(models.Model):
    """平行宇宙匹配"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parallel_matches_1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parallel_matches_2')
    match_date = models.DateField(auto_now_add=True)
    keywords = models.JSONField(default=list)  # 匹配的关键词
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user1', 'user2', 'match_date']
        ordering = ['-match_date']
        verbose_name = '平行匹配'
        verbose_name_plural = '平行匹配'
    
    def __str__(self):
        return f"{self.user1.username} ↔ {self.user2.username} ({self.match_date})"
