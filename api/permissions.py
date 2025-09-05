"""
API权限控制
"""
from rest_framework.permissions import BasePermission
from .response import APIErrorCodes


class IsAuthenticated(BasePermission):
    """需要登录权限"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminUser(BasePermission):
    """需要管理员权限"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff or request.user.is_superuser)
        )


class IsVIPUser(BasePermission):
    """需要VIP用户权限"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查用户是否有VIP权限
        if hasattr(request.user, 'membership'):
            return request.user.membership.membership_type in ['vip', 'premium']
        
        return False


class FeaturePermission(BasePermission):
    """功能权限控制"""
    
    def __init__(self, feature_key):
        self.feature_key = feature_key
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # 检查功能是否启用
        from apps.content.models import FeatureAccess
        try:
            feature = FeatureAccess.objects.get(feature_key=self.feature_key)
            return feature.is_accessible_by_user(request.user)
        except FeatureAccess.DoesNotExist:
            return False


class RateLimitPermission(BasePermission):
    """API访问频率限制"""
    
    def __init__(self, rate_limit_key=None, max_requests=100, window_seconds=3600):
        self.rate_limit_key = rate_limit_key
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def has_permission(self, request, view):
        # 这里可以实现基于Redis的限流逻辑
        # 暂时返回True，后续可以集成django-ratelimit
        return True


class ClientTypePermission(BasePermission):
    """客户端类型权限控制"""
    
    def __init__(self, allowed_clients=None):
        self.allowed_clients = allowed_clients or ['web', 'miniprogram', 'mobile']
    
    def has_permission(self, request, view):
        client_type = request.META.get('HTTP_X_CLIENT_TYPE', 'web')
        return client_type in self.allowed_clients


class CombinedPermission(BasePermission):
    """组合权限控制"""
    
    def __init__(self, permissions):
        self.permissions = permissions
    
    def has_permission(self, request, view):
        return all(permission.has_permission(request, view) for permission in self.permissions)
