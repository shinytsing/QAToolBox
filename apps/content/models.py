from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Suggestion(models.Model):
    SUGGESTION_TYPES = [
        ('feature', '功能建议'),
        ('ui', '界面改进'),
        ('bug', 'Bug报告'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('reviewing', '审核中'),
        ('implemented', '已实现'),
        ('rejected', '已拒绝'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='建议标题')
    content = models.TextField(verbose_name='建议内容')
    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPES, default='feature', verbose_name='建议类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='提交用户')
    user_name = models.CharField(max_length=100, blank=True, verbose_name='用户名称')
    user_email = models.EmailField(blank=True, verbose_name='用户邮箱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    admin_response = models.TextField(blank=True, verbose_name='管理员回复')
    
    # 新增媒体文件字段
    images = models.JSONField(default=list, blank=True, verbose_name='图片文件列表')
    videos = models.JSONField(default=list, blank=True, verbose_name='视频文件列表')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户建议'
        verbose_name_plural = '用户建议'
    
    def __str__(self):
        return f"{self.title} - {self.get_suggestion_type_display()}"

class Feedback(models.Model):
    FEEDBACK_TYPES = [
        ('bug', 'Bug报告'),
        ('feature', '功能建议'),
        ('ui', '界面改进'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('closed', '已关闭'),
    ]
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='bug', verbose_name='反馈类型')
    content = models.TextField(verbose_name='反馈内容')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='提交用户')
    user_name = models.CharField(max_length=100, blank=True, verbose_name='用户名称')
    user_email = models.EmailField(blank=True, verbose_name='用户邮箱')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    admin_response = models.TextField(blank=True, verbose_name='管理员回复')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户反馈'
        verbose_name_plural = '用户反馈'
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.content[:50]}"


class Announcement(models.Model):
    """公告模型"""
    PRIORITY_CHOICES = [
        ('low', '普通'),
        ('medium', '重要'), 
        ('high', '紧急'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已发布'),
        ('archived', '已归档'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='公告标题')
    content = models.TextField(verbose_name='公告内容')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    is_popup = models.BooleanField(default=True, verbose_name='是否弹窗显示')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = '公告'
        verbose_name_plural = '公告管理'
    
    def __str__(self):
        return f'[{self.get_priority_display()}] {self.title}'
    
    def is_active(self):
        """判断公告是否在有效期内"""
        now = timezone.now()
        if self.status != 'published':
            return False
        if self.start_time > now:
            return False
        if self.end_time and self.end_time < now:
            return False
        return True

class AILink(models.Model):
    """AI友情链接模型"""
    CATEGORY_CHOICES = [
        ('visual', '视觉'),
        ('music', '音乐'),
        ('programming', '编程'),
        ('image', '图片'),
        ('other', '其他'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='网站名称')
    url = models.URLField(verbose_name='网站链接')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='分类')
    description = models.TextField(blank=True, verbose_name='描述')
    icon = models.ImageField(upload_to='ai_links/icons/', blank=True, null=True, verbose_name='网站图标')
    icon_url = models.URLField(blank=True, verbose_name='图标URL')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    sort_order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = 'AI友情链接'
        verbose_name_plural = 'AI友情链接'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def get_icon_url(self):
        """获取图标URL，优先使用本地图标"""
        if self.icon:
            return self.icon.url
        return self.icon_url