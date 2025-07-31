from django.db import models
from django.contrib.auth.models import User

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