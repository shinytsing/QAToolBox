# admin.py
from django.contrib import admin
from apps.tools.models import (
    ToolUsageLog, 
    SocialMediaSubscription, 
    SocialMediaNotification, 
    SocialMediaPlatformConfig,
    TravelGuide, TravelDestination, TravelReview
)


@admin.register(ToolUsageLog)
class ToolUsageLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool_type', 'created_at')
    list_filter = ('tool_type', 'created_at')
    search_fields = ('user__username', 'tool_type')


@admin.register(SocialMediaSubscription)
class SocialMediaSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'target_user_name', 'status', 'check_frequency', 'last_check', 'created_at')
    list_filter = ('platform', 'status', 'check_frequency', 'created_at')
    search_fields = ('user__username', 'target_user_name', 'target_user_id')
    readonly_fields = ('last_check', 'last_change', 'created_at', 'updated_at')
    list_editable = ('status',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'platform', 'target_user_id', 'target_user_name', 'avatar_url')
        }),
        ('订阅设置', {
            'fields': ('subscription_types', 'check_frequency', 'status')
        }),
        ('时间信息', {
            'fields': ('last_check', 'last_change', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMediaNotification)
class SocialMediaNotificationAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'subscription__target_user_name')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    
    fieldsets = (
        ('通知信息', {
            'fields': ('subscription', 'notification_type', 'title', 'content')
        }),
        ('新动态详情', {
            'fields': ('post_content', 'post_images', 'post_video_url', 'post_tags', 'post_likes', 'post_comments', 'post_shares'),
            'classes': ('collapse',)
        }),
        ('新粉丝详情', {
            'fields': ('follower_name', 'follower_avatar', 'follower_id', 'follower_count'),
            'classes': ('collapse',)
        }),
        ('新关注详情', {
            'fields': ('following_name', 'following_avatar', 'following_id', 'following_count'),
            'classes': ('collapse',)
        }),
        ('资料变化详情', {
            'fields': ('profile_changes', 'old_profile_data', 'new_profile_data'),
            'classes': ('collapse',)
        }),
        ('通用信息', {
            'fields': ('external_url', 'platform_specific_data')
        }),
        ('状态', {
            'fields': ('is_read', 'created_at')
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """根据通知类型动态显示字段"""
        fieldsets = list(super().get_fieldsets(request, obj))
        
        if obj:
            # 根据通知类型显示相应的字段组
            if obj.notification_type == 'newPosts':
                # 显示新动态相关字段
                pass
            elif obj.notification_type == 'newFollowers':
                # 隐藏其他类型的字段组
                fieldsets = [fieldsets[0], fieldsets[2], fieldsets[5], fieldsets[6]]
            elif obj.notification_type == 'newFollowing':
                # 隐藏其他类型的字段组
                fieldsets = [fieldsets[0], fieldsets[3], fieldsets[5], fieldsets[6]]
            elif obj.notification_type == 'profileChanges':
                # 隐藏其他类型的字段组
                fieldsets = [fieldsets[0], fieldsets[4], fieldsets[5], fieldsets[6]]
        
        return fieldsets


@admin.register(SocialMediaPlatformConfig)
class SocialMediaPlatformConfigAdmin(admin.ModelAdmin):
    list_display = ('platform', 'is_active', 'rate_limit', 'updated_at')
    list_filter = ('platform', 'is_active')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'rate_limit')
    
    fieldsets = (
        ('平台配置', {
            'fields': ('platform', 'api_endpoint', 'api_key')
        }),
        ('运行设置', {
            'fields': ('is_active', 'rate_limit')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TravelGuide)
class TravelGuideAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'travel_style', 'budget_range', 'travel_duration', 'is_favorite', 'created_at')
    list_filter = ('travel_style', 'budget_range', 'is_favorite', 'created_at')
    search_fields = ('user__username', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_favorite',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'destination', 'travel_style', 'budget_range', 'travel_duration')
        }),
        ('攻略内容', {
            'fields': ('must_visit_attractions', 'food_recommendations', 'transportation_guide', 'hidden_gems')
        }),
        ('天气和预算', {
            'fields': ('weather_info', 'best_time_to_visit', 'budget_estimate', 'travel_tips')
        }),
        ('个性化设置', {
            'fields': ('interests', 'is_favorite', 'is_exported')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TravelDestination)
class TravelDestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'region', 'popularity_score', 'best_season', 'average_cost')
    list_filter = ('country', 'best_season', 'created_at')
    search_fields = ('name', 'country', 'region', 'description')
    readonly_fields = ('created_at',)
    list_editable = ('popularity_score', 'best_season', 'average_cost')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'country', 'region', 'description')
        }),
        ('详细信息', {
            'fields': ('image_url', 'popularity_score', 'best_season', 'average_cost')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(TravelReview)
class TravelReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'travel_guide', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'travel_guide__destination', 'comment')
    readonly_fields = ('created_at',)
    list_editable = ('rating',)
    
    fieldsets = (
        ('评价信息', {
            'fields': ('travel_guide', 'user', 'rating', 'comment')
        }),
        ('时间信息', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )