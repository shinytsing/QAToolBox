from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ShareRecord(models.Model):
    """分享记录模型"""
    class Meta:
        app_label = 'share'
    
    SHARE_PLATFORMS = [
        ('wechat', '微信'),
        ('weibo', '微博'),
        ('douyin', '抖音'),
        ('xiaohongshu', '小红书'),
        ('qq', 'QQ'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
        ('email', '邮件'),
        ('link', '链接'),
        ('qrcode', '二维码'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    platform = models.CharField(max_length=20, choices=SHARE_PLATFORMS, verbose_name='分享平台')
    page_url = models.URLField(verbose_name='分享页面URL')
    page_title = models.CharField(max_length=200, verbose_name='页面标题')
    share_time = models.DateTimeField(default=timezone.now, verbose_name='分享时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    class Meta:
        verbose_name = '分享记录'
        verbose_name_plural = '分享记录'
        ordering = ['-share_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()} - {self.page_title}"


class ShareLink(models.Model):
    """分享链接模型"""
    class Meta:
        app_label = 'share'
    
    original_url = models.URLField(verbose_name='原始URL')
    short_code = models.CharField(max_length=10, unique=True, verbose_name='短链接代码')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    image_url = models.URLField(blank=True, verbose_name='图片URL')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    click_count = models.PositiveIntegerField(default=0, verbose_name='点击次数')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '分享链接'
        verbose_name_plural = '分享链接'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.short_code}"


class ShareAnalytics(models.Model):
    """分享分析模型"""
    class Meta:
        app_label = 'share'
    
    date = models.DateField(verbose_name='日期')
    platform = models.CharField(max_length=20, choices=ShareRecord.SHARE_PLATFORMS, verbose_name='平台')
    share_count = models.PositiveIntegerField(default=0, verbose_name='分享次数')
    click_count = models.PositiveIntegerField(default=0, verbose_name='点击次数')
    
    class Meta:
        verbose_name = '分享分析'
        verbose_name_plural = '分享分析'
        unique_together = ['date', 'platform']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.get_platform_display()} - {self.share_count}"
