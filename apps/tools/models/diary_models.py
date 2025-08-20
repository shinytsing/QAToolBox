from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Index, Q
import random
import json
from datetime import timedelta


class LifeDiaryEntry(models.Model):
    """生活日记条目模型"""
    MOOD_CHOICES = [
        ('excellent', '极好'),
        ('good', '好'),
        ('normal', '一般'),
        ('bad', '差'),
        ('terrible', '很糟'),
    ]
    
    WEATHER_CHOICES = [
        ('sunny', '晴天'),
        ('cloudy', '多云'),
        ('rainy', '雨天'),
        ('snowy', '雪天'),
        ('foggy', '雾天'),
        ('windy', '大风'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', db_index=True)
    date = models.DateField(verbose_name='日期', db_index=True)
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, verbose_name='心情')
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, blank=True, verbose_name='天气')
    tags = models.JSONField(default=list, verbose_name='标签')
    is_private = models.BooleanField(default=False, verbose_name='是否私密')
    word_count = models.IntegerField(default=0, verbose_name='字数')
    reading_time = models.IntegerField(default=0, verbose_name='阅读时间(分钟)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '生活日记'
        verbose_name_plural = '生活日记'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'mood']),
            models.Index(fields=['user', 'is_private']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.title}"

    def save(self, *args, **kwargs):
        # 自动计算字数和阅读时间
        self.word_count = len(self.content)
        self.reading_time = max(1, self.word_count // 200)  # 假设每分钟200字
        super().save(*args, **kwargs)

    @classmethod
    def get_user_diary_stats(cls, user, days=30):
        """获取用户日记统计"""
        cache_key = f"diary_stats_{user.id}_{days}"
        result = cache.get(cache_key)
        
        if result is None:
            queryset = cls.objects.filter(
                user=user,
                date__gte=timezone.now().date() - timedelta(days=days)
            )
            
            result = {
                'total_entries': queryset.count(),
                'total_words': queryset.aggregate(total=models.Sum('word_count'))['total'] or 0,
                'avg_words_per_entry': queryset.aggregate(avg=models.Avg('word_count'))['avg'] or 0,
                'mood_distribution': list(queryset.values('mood').annotate(count=models.Count('id'))),
                'writing_streak': cls.get_writing_streak(user),
            }
            cache.set(cache_key, result, 300)  # 缓存5分钟
        
        return result

    @classmethod
    def get_writing_streak(cls, user):
        """获取连续写作天数"""
        entries = cls.objects.filter(user=user).order_by('-date')
        if not entries:
            return 0
        
        streak = 0
        current_date = timezone.now().date()
        
        for entry in entries:
            if entry.date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        
        return streak


class LifeCategory(models.Model):
    """生活分类模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=100, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='描述')
    color = models.CharField(max_length=7, default='#007bff', verbose_name='颜色')
    icon = models.CharField(max_length=50, blank=True, verbose_name='图标')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '生活分类'
        verbose_name_plural = '生活分类'
        unique_together = ['user', 'name']
        ordering = ['name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class LifeTag(models.Model):
    """生活标签模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    name = models.CharField(max_length=50, verbose_name='标签名称')
    category = models.ForeignKey(LifeCategory, on_delete=models.CASCADE, verbose_name='分类')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '生活标签'
        verbose_name_plural = '生活标签'
        unique_together = ['user', 'name']
        ordering = ['-usage_count', 'name']

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
