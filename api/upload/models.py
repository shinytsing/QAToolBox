from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FileUpload(models.Model):
    UPLOAD_TYPES = [
        ('general', '通用文件'),
        ('image', '图片'),
        ('document', '文档'),
        ('video', '视频'),
        ('audio', '音频'),
        ('avatar', '头像'),
        ('diary', '日记图片'),
        ('workout', '训练图片'),
        ('chat', '聊天文件'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_uploads')
    original_name = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255, unique=True)
    file_path = models.CharField(max_length=500)
    thumbnail_path = models.CharField(max_length=500, blank=True, null=True)
    file_size = models.PositiveIntegerField()
    mime_type = models.CharField(max_length=100)
    upload_type = models.CharField(max_length=20, choices=UPLOAD_TYPES, default='general')
    is_public = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'file_uploads'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.original_name}"
    
    @property
    def file_url(self):
        from django.conf import settings
        return f"{settings.MEDIA_URL}{self.file_path}"
    
    @property
    def thumbnail_url(self):
        if self.thumbnail_path:
            from django.conf import settings
            return f"{settings.MEDIA_URL}{self.thumbnail_path}"
        return None
    
    @property
    def file_size_human(self):
        """返回人类可读的文件大小"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class FileShare(models.Model):
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='shares')
    share_code = models.CharField(max_length=32, unique=True)
    password = models.CharField(max_length=100, blank=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_downloads = models.PositiveIntegerField(null=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'file_shares'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file.original_name} - {self.share_code}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_download_limit_reached(self):
        if self.max_downloads:
            return self.download_count >= self.max_downloads
        return False

class FileAccessLog(models.Model):
    file = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='access_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    action = models.CharField(max_length=20, choices=[
        ('download', '下载'),
        ('view', '查看'),
        ('share', '分享'),
        ('delete', '删除'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'file_access_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file.original_name} - {self.action} - {self.created_at}"
