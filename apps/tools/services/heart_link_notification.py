#!/usr/bin/env python3
"""
Heart Link 通知服务
用于在请求即将过期时通知用户
"""

from django.utils import timezone
from datetime import timedelta
from apps.tools.models import HeartLinkRequest, UserOnlineStatus


class HeartLinkNotificationService:
    """Heart Link 通知服务"""
    
    def __init__(self):
        self.warning_threshold = 8  # 8分钟时开始警告
        self.expiry_threshold = 10  # 10分钟过期
    
    def check_and_notify_expiring_requests(self):
        """检查并通知即将过期的请求"""
        from django.contrib import messages
        
        # 查找即将过期的请求（8-10分钟之间）
        warning_time = timezone.now() - timedelta(minutes=self.warning_threshold)
        expiry_time = timezone.now() - timedelta(minutes=self.expiry_threshold)
        
        expiring_requests = HeartLinkRequest.objects.filter(
            status='pending',
            created_at__gte=warning_time,
            created_at__lt=expiry_time
        )
        
        for request in expiring_requests:
            # 检查用户是否在线
            if self.is_user_online(request.requester):
                # 这里可以发送实时通知
                # 由于这是API环境，我们返回一个特殊的响应
                pass
    
    def is_user_online(self, user):
        """检查用户是否在线"""
        try:
            online_status = UserOnlineStatus.objects.filter(user=user).first()
            if online_status and online_status.last_seen:
                return timezone.now() - online_status.last_seen < timedelta(minutes=5)
            return False
        except:
            return False
    
    def get_expiry_warning_message(self, request):
        """获取过期警告消息"""
        time_remaining = self.expiry_threshold - (timezone.now() - request.created_at).total_seconds() / 60
        return f"您的匹配请求将在 {int(time_remaining)} 分钟后过期，请保持在线状态"
    
    def should_show_warning(self, request):
        """判断是否应该显示警告"""
        time_elapsed = (timezone.now() - request.created_at).total_seconds() / 60
        return self.warning_threshold <= time_elapsed < self.expiry_threshold


# 全局通知服务实例
notification_service = HeartLinkNotificationService()
