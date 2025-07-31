from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('admin', '管理员'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='用户角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户角色'
        verbose_name_plural = '用户角色'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @property
    def is_admin(self):
        return self.role == 'admin'

class UserStatus(models.Model):
    STATUS_CHOICES = [
        ('active', '正常'),
        ('suspended', '已暂停'),
        ('banned', '已封禁'),
        ('deleted', '已删除'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='用户状态')
    reason = models.TextField(blank=True, verbose_name='状态变更原因')
    suspended_until = models.DateTimeField(null=True, blank=True, verbose_name='暂停到期时间')
    banned_phone = models.CharField(max_length=20, blank=True, verbose_name='封禁手机号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户状态'
        verbose_name_plural = '用户状态'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"
    
    @property
    def is_active(self):
        if self.status == 'active':
            return True
        elif self.status == 'suspended' and self.suspended_until:
            return timezone.now() > self.suspended_until
        return False

class UserMembership(models.Model):
    MEMBERSHIP_CHOICES = [
        ('free', '免费用户'),
        ('basic', '基础会员'),
        ('premium', '高级会员'),
        ('vip', 'VIP会员'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='membership')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='free', verbose_name='会员类型')
    start_date = models.DateTimeField(auto_now_add=True, verbose_name='会员开始时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='会员结束时间')
    is_active = models.BooleanField(default=True, verbose_name='会员状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户会员'
        verbose_name_plural = '用户会员'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_membership_type_display()}"
    
    @property
    def is_valid(self):
        if not self.is_active:
            return False
        if self.membership_type == 'free':
            return True
        if self.end_date:
            return timezone.now() < self.end_date
        return True

class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ('status_change', '状态变更'),
        ('phone_ban', '手机号封禁'),
        ('account_delete', '账号删除'),
        ('membership_change', '会员变更'),
        ('role_change', '角色变更'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions', verbose_name='管理员')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_actions', verbose_name='目标用户', null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    details = models.TextField(verbose_name='操作详情')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户操作日志'
        verbose_name_plural = '用户操作日志'
    
    def __str__(self):
        return f"{self.admin_user.username} -> {self.target_user.username} - {self.get_action_display()}"

# 用户活动监控模型
class UserActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('login', '登录'),
        ('logout', '登出'),
        ('api_access', '接口访问'),
        ('page_view', '页面访问'),
        ('tool_usage', '工具使用'),
        ('suggestion_submit', '提交建议'),
        ('feedback_submit', '提交反馈'),
        ('profile_update', '资料更新'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='activity_logs')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='活动类型')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址', null=True, blank=True)
    user_agent = models.TextField(verbose_name='用户代理', null=True, blank=True)
    endpoint = models.CharField(max_length=255, verbose_name='访问端点', null=True, blank=True)
    method = models.CharField(max_length=10, verbose_name='请求方法', null=True, blank=True)
    status_code = models.IntegerField(verbose_name='状态码', null=True, blank=True)
    response_time = models.FloatField(verbose_name='响应时间(秒)', null=True, blank=True)
    details = models.JSONField(verbose_name='详细信息', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '用户活动日志'
        verbose_name_plural = '用户活动日志'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type', 'created_at']),
            models.Index(fields=['activity_type', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username if self.user else '匿名用户'} - {self.get_activity_type_display()} - {self.created_at}"

# 用户会话统计模型
class UserSessionStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_stats')
    session_start = models.DateTimeField(verbose_name='会话开始时间')
    session_end = models.DateTimeField(verbose_name='会话结束时间', null=True, blank=True)
    duration = models.IntegerField(verbose_name='会话时长(秒)', null=True, blank=True)
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    user_agent = models.TextField(verbose_name='用户代理')
    is_active = models.BooleanField(default=True, verbose_name='是否活跃')
    
    class Meta:
        verbose_name = '用户会话统计'
        verbose_name_plural = '用户会话统计'
        ordering = ['-session_start']
    
    def __str__(self):
        return f"{self.user.username} - {self.session_start}"

# API访问统计模型
class APIUsageStats(models.Model):
    endpoint = models.CharField(max_length=255, verbose_name='API端点')
    method = models.CharField(max_length=10, verbose_name='请求方法')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='api_usage')
    ip_address = models.GenericIPAddressField(verbose_name='IP地址')
    status_code = models.IntegerField(verbose_name='状态码')
    response_time = models.FloatField(verbose_name='响应时间(秒)')
    request_size = models.IntegerField(verbose_name='请求大小(字节)', null=True, blank=True)
    response_size = models.IntegerField(verbose_name='响应大小(字节)', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='访问时间')
    
    class Meta:
        verbose_name = 'API使用统计'
        verbose_name_plural = 'API使用统计'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['endpoint', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.endpoint} - {self.method} - {self.user.username if self.user else '匿名'}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    # 添加其他与你的用户相关的字段
