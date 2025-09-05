"""
分享模块序列化器
"""
from rest_framework import serializers
from apps.share.models import ShareRecord, ShareLink


class ShareRecordSerializer(serializers.ModelSerializer):
    """分享记录序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    
    class Meta:
        model = ShareRecord
        fields = (
            'id', 'user', 'user_name', 'platform', 'platform_display',
            'page_url', 'page_title', 'share_time', 'ip_address',
            'user_agent'
        )
        read_only_fields = ('id', 'user', 'share_time')


class ShareLinkSerializer(serializers.ModelSerializer):
    """分享链接序列化器"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    short_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = ShareLink
        fields = (
            'id', 'creator', 'creator_name', 'original_url', 'short_code',
            'short_url', 'title', 'description', 'expires_at', 'is_active',
            'click_count', 'created_at'
        )
        read_only_fields = ('id', 'creator', 'short_code', 'click_count', 'created_at')
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class ShareAnalyticsSerializer(serializers.Serializer):
    """分享分析序列化器"""
    total_shares = serializers.IntegerField()
    platform_stats = serializers.DictField()
    daily_shares = serializers.ListField()
    top_pages = serializers.ListField()
    click_through_rate = serializers.FloatField()


class PWAManifestSerializer(serializers.Serializer):
    """PWA清单序列化器"""
    name = serializers.CharField()
    short_name = serializers.CharField()
    description = serializers.CharField()
    start_url = serializers.CharField()
    display = serializers.CharField()
    background_color = serializers.CharField()
    theme_color = serializers.CharField()
    icons = serializers.ListField()
