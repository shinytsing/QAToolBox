"""
管理模块序列化器
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.content.models import FeatureAccess, UserFeatureAccess
from apps.users.models import Profile, UserMembership


class UserManagementSerializer(serializers.ModelSerializer):
    """用户管理序列化器"""
    profile = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'last_login',
            'date_joined', 'profile', 'membership'
        )
        read_only_fields = ('id', 'last_login', 'date_joined')
    
    def get_profile(self, obj):
        try:
            profile = obj.profile
            return {
                'avatar': profile.avatar.url if profile.avatar else None,
                'phone': profile.phone,
                'bio': profile.bio,
                'location': profile.location,
            }
        except:
            return None
    
    def get_membership(self, obj):
        try:
            membership = obj.membership
            return {
                'membership_type': membership.membership_type,
                'is_active': membership.is_active,
                'expires_at': membership.expires_at,
            }
        except:
            return None


class FeatureManagementSerializer(serializers.ModelSerializer):
    """功能管理序列化器"""
    
    class Meta:
        model = FeatureAccess
        fields = (
            'id', 'feature_key', 'feature_name', 'description',
            'url_path', 'icon', 'status', 'visibility', 'sort_order',
            'is_active', 'access_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserFeatureAccessSerializer(serializers.ModelSerializer):
    """用户功能访问序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    feature_name = serializers.CharField(source='feature.feature_name', read_only=True)
    
    class Meta:
        model = UserFeatureAccess
        fields = (
            'id', 'user', 'user_name', 'feature', 'feature_name',
            'is_enabled', 'custom_settings', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class SystemStatsSerializer(serializers.Serializer):
    """系统统计序列化器"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_features = serializers.IntegerField()
    enabled_features = serializers.IntegerField()
    total_api_calls = serializers.IntegerField()
    today_api_calls = serializers.IntegerField()
    storage_used = serializers.CharField()
    system_uptime = serializers.CharField()


class AnalyticsDataSerializer(serializers.Serializer):
    """分析数据序列化器"""
    date = serializers.DateField()
    users = serializers.IntegerField()
    api_calls = serializers.IntegerField()
    features_used = serializers.IntegerField()
    errors = serializers.IntegerField()


class LogEntrySerializer(serializers.Serializer):
    """日志条目序列化器"""
    timestamp = serializers.DateTimeField()
    level = serializers.CharField()
    message = serializers.CharField()
    user = serializers.CharField(required=False)
    ip_address = serializers.CharField(required=False)
    user_agent = serializers.CharField(required=False)


class NotificationSerializer(serializers.Serializer):
    """通知序列化器"""
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(choices=[
        ('info', '信息'),
        ('warning', '警告'),
        ('error', '错误'),
        ('success', '成功'),
    ])
    target_users = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    is_global = serializers.BooleanField(default=False)
    expires_at = serializers.DateTimeField(required=False)
