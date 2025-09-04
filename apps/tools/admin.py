# admin.py
from django.contrib import admin

# 导入模型
try:
    from .models import (
        Feature,
        FeatureRecommendation,
        FoodHistory,
        FoodItem,
        FoodRandomizationSession,
        FoodRandomizer,
        ImportantMoment,
        Interaction,
        PersonProfile,
        RelationshipReminder,
        RelationshipStatistics,
        RelationshipTag,
        SocialMediaNotification,
        SocialMediaSubscription,
        ToolUsageLog,
        TravelDestination,
        TravelGuide,
        TravelGuideUsage,
        TravelReview,
        UserFeaturePermission,
        UserFirstVisit,
        UserGeneratedTravelGuide,
    )

    @admin.register(ToolUsageLog)
    class ToolUsageLogAdmin(admin.ModelAdmin):
        list_display = ("user", "tool_type", "created_at")
        list_filter = ("tool_type", "created_at")
        search_fields = ("user__username", "tool_type")

    @admin.register(SocialMediaSubscription)
    class SocialMediaSubscriptionAdmin(admin.ModelAdmin):
        list_display = ("user", "platform", "target_user_name", "status", "check_frequency", "last_check", "created_at")
        list_filter = ("platform", "status", "check_frequency", "created_at")
        search_fields = ("user__username", "target_user_name", "target_user_id")
        readonly_fields = ("last_check", "last_change", "created_at", "updated_at")
        list_editable = ("status",)

    @admin.register(SocialMediaNotification)
    class SocialMediaNotificationAdmin(admin.ModelAdmin):
        list_display = ("subscription", "notification_type", "title", "created_at")
        list_filter = ("notification_type", "created_at")
        search_fields = ("title", "content", "subscription__target_user_name")
        readonly_fields = ("created_at",)

except ImportError as e:
    print(f"Admin import error: {e}")
    pass

# 导入营养信息管理配置
try:
    from .admin_nutrition import *
except ImportError as e:
    print(f"Nutrition admin import error: {e}")
    pass
