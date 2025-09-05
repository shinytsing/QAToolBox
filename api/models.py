"""
API模块数据模型
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginSession(models.Model):
    """登录会话模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    device_id = models.CharField(max_length=100, unique=True)
    device_type = models.CharField(max_length=50)
    device_name = models.CharField(max_length=100, blank=True)
    platform = models.CharField(max_length=50)  # ios, android, web, miniprogram
    app_version = models.CharField(max_length=20, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'unified_login_sessions'
        ordering = ['-last_activity']
        verbose_name = '登录会话'
        verbose_name_plural = '登录会话'
    
    def __str__(self):
        return f"{self.user.username} - {self.device_type} - {self.device_name}"


class DataSyncLog(models.Model):
    """数据同步日志"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sync_logs')
    device_id = models.CharField(max_length=100)
    data_type = models.CharField(max_length=50)
    sync_id = models.CharField(max_length=100, unique=True)
    data_size = models.IntegerField(default=0)
    sync_status = models.CharField(max_length=20, choices=[
        ('pending', '待同步'),
        ('success', '同步成功'),
        ('failed', '同步失败'),
    ], default='pending')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    synced_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'data_sync_logs'
        ordering = ['-created_at']
        verbose_name = '数据同步日志'
        verbose_name_plural = '数据同步日志'
    
    def __str__(self):
        return f"{self.user.username} - {self.data_type} - {self.sync_status}"
