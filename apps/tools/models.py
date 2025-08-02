from django.db import models
from django.contrib.auth.models import User


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
        ('newFollowers', '新关注'),
        ('profileChanges', '资料变化'),
    ]
    
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
        unique_together = ['user', 'platform', 'user_id']
        ordering = ['-created_at']
        verbose_name = '社交媒体订阅'
        verbose_name_plural = '社交媒体订阅'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()} - {self.target_user_name}"


class SocialMediaNotification(models.Model):
    """社交媒体通知模型"""
    NOTIFICATION_TYPE_CHOICES = [
        ('newPosts', '新动态'),
        ('newFollowers', '新关注'),
        ('profileChanges', '资料变化'),
    ]
    
    subscription = models.ForeignKey(SocialMediaSubscription, on_delete=models.CASCADE, verbose_name='订阅')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name='通知类型')
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
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