# admin.py
from django.contrib import admin
from apps.tools.models import (
    ToolUsageLog, 
    SocialMediaSubscription, 
    SocialMediaNotification, 
    SocialMediaPlatformConfig
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
        ('状态', {
            'fields': ('is_read', 'created_at')
        }),
    )


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