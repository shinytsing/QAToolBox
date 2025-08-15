# admin.py
from django.contrib import admin
from apps.tools.models import (
    ToolUsageLog, 
    SocialMediaSubscription, 
    SocialMediaNotification, 
    SocialMediaPlatformConfig,
    TravelGuide, TravelDestination, TravelReview, UserGeneratedTravelGuide, TravelGuideUsage,
    FoodRandomizer, FoodItem, FoodRandomizationSession, FoodHistory,
    # LifeGraph Models
    RelationshipTag, PersonProfile, Interaction, ImportantMoment, 
    RelationshipStatistics, RelationshipReminder,
    # Feature Recommendation Models
    Feature, UserFeaturePermission, FeatureRecommendation, UserFirstVisit
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
    list_display = ('user', 'destination', 'travel_style', 'budget_min', 'budget_max', 'budget_range', 'travel_duration', 'is_favorite', 'created_at')
    list_filter = ('travel_style', 'budget_range', 'is_favorite', 'created_at')
    search_fields = ('user__username', 'destination')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_favorite',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'destination', 'travel_style', 'budget_min', 'budget_max', 'budget_range', 'travel_duration')
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
            'fields': ('user', 'travel_guide', 'rating', 'comment')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )


# 食物随机选择器相关Admin
@admin.register(FoodRandomizer)
class FoodRandomizerAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'cuisine_preference', 'is_active', 'created_at')
    list_filter = ('meal_type', 'cuisine_preference', 'is_active', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'meal_type', 'cuisine_preference')
        }),
        ('状态', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'difficulty', 'cooking_time', 'popularity_score', 'is_active')
    list_filter = ('cuisine', 'difficulty', 'meal_types', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'ingredients', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('popularity_score', 'is_active')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'cuisine', 'difficulty', 'cooking_time')
        }),
        ('分类信息', {
            'fields': ('meal_types', 'ingredients', 'tags')
        }),
        ('链接信息', {
            'fields': ('image_url', 'recipe_url')
        }),
        ('统计信息', {
            'fields': ('popularity_score', 'is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(FoodRandomizationSession)
class FoodRandomizationSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_type', 'cuisine_preference', 'status', 'selected_food', 'started_at')
    list_filter = ('meal_type', 'cuisine_preference', 'status', 'started_at')
    search_fields = ('user__username', 'selected_food__name')
    readonly_fields = ('started_at', 'paused_at', 'completed_at', 'total_cycles', 'current_cycle')
    
    fieldsets = (
        ('会话信息', {
            'fields': ('user', 'meal_type', 'cuisine_preference', 'status')
        }),
        ('随机过程', {
            'fields': ('animation_duration', 'total_cycles', 'current_cycle')
        }),
        ('结果', {
            'fields': ('selected_food', 'alternative_foods')
        }),
        ('时间信息', {
            'fields': ('started_at', 'paused_at', 'completed_at')
        }),
    )


@admin.register(FoodHistory)
class FoodHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_item', 'meal_type', 'rating', 'was_cooked', 'created_at')
    list_filter = ('meal_type', 'rating', 'was_cooked', 'created_at')
    search_fields = ('user__username', 'food_item__name', 'feedback')
    readonly_fields = ('created_at',)
    list_editable = ('rating', 'was_cooked')
    
    fieldsets = (
        ('选择信息', {
            'fields': ('user', 'session', 'food_item', 'meal_type')
        }),
        ('反馈信息', {
            'fields': ('rating', 'feedback', 'was_cooked')
        }),
        ('时间信息', {
            'fields': ('created_at',)
        }),
    )


# LifeGraph 人际档案系统 Admin

@admin.register(RelationshipTag)
class RelationshipTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'tag_type', 'color', 'is_global', 'usage_count', 'created_by', 'created_at')
    list_filter = ('tag_type', 'is_global', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('usage_count', 'created_at')
    list_editable = ('color', 'is_global')
    ordering = ['-usage_count', 'name']
    
    fieldsets = (
        ('标签信息', {
            'fields': ('name', 'tag_type', 'color')
        }),
        ('使用设置', {
            'fields': ('is_global', 'created_by')
        }),
        ('统计信息', {
            'fields': ('usage_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PersonProfile)
class PersonProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'nickname', 'user', 'importance_level', 'interaction_count', 'last_interaction_date', 'created_at')
    list_filter = ('importance_level', 'gender', 'created_at', 'last_interaction_date')
    search_fields = ('name', 'nickname', 'user__username', 'occupation', 'company_school', 'hometown')
    readonly_fields = ('interaction_count', 'last_interaction_date', 'created_at', 'updated_at')
    list_editable = ('importance_level',)
    filter_horizontal = ('relationship_tags', 'mutual_friends')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基础信息', {
            'fields': ('user', 'name', 'nickname', 'avatar')
        }),
        ('关系信息', {
            'fields': ('relationship_tags', 'first_met_date', 'first_met_location', 'importance_level')
        }),
        ('个人背景', {
            'fields': ('gender', 'age', 'occupation', 'company_school', 'hometown'),
            'classes': ('collapse',)
        }),
        ('特征描述', {
            'fields': ('appearance_notes', 'personality_traits', 'interests_hobbies', 'habits_phrases'),
            'classes': ('collapse',)
        }),
        ('重要日期', {
            'fields': ('birthday', 'important_dates'),
            'classes': ('collapse',)
        }),
        ('联系方式', {
            'fields': ('phone', 'email', 'social_accounts'),
            'classes': ('collapse',),
            'description': '请谨慎填写联系方式信息，确保符合隐私保护要求。'
        }),
        ('关系网络', {
            'fields': ('mutual_friends',),
            'classes': ('collapse',)
        }),
        ('统计信息', {
            'fields': ('interaction_count', 'last_interaction_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """只显示当前用户的档案"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('person', 'title', 'interaction_type', 'date', 'mood', 'is_important', 'created_at')
    list_filter = ('interaction_type', 'mood', 'is_important', 'date', 'created_at')
    search_fields = ('person__name', 'title', 'content', 'location')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_important',)
    filter_horizontal = ('other_participants',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('基础信息', {
            'fields': ('user', 'person', 'interaction_type', 'date', 'time', 'location')
        }),
        ('内容记录', {
            'fields': ('title', 'content', 'topics_discussed', 'agreements_made')
        }),
        ('情感记录', {
            'fields': ('mood', 'impression_notes')
        }),
        ('参与人员', {
            'fields': ('other_participants',),
            'classes': ('collapse',)
        }),
        ('附件', {
            'fields': ('photos', 'files', 'links'),
            'classes': ('collapse',)
        }),
        ('标签分类', {
            'fields': ('tags', 'is_important')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """只显示当前用户的互动记录"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(ImportantMoment)
class ImportantMomentAdmin(admin.ModelAdmin):
    list_display = ('person', 'title', 'moment_type', 'date', 'emotional_impact', 'created_at')
    list_filter = ('moment_type', 'emotional_impact', 'date', 'created_at')
    search_fields = ('person__name', 'title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('other_participants',)
    date_hierarchy = 'date'
    
    fieldsets = (
        ('基础信息', {
            'fields': ('user', 'person', 'related_interaction', 'moment_type')
        }),
        ('时刻详情', {
            'fields': ('title', 'description', 'date', 'location')
        }),
        ('多媒体内容', {
            'fields': ('photos', 'videos', 'audio_recordings', 'documents'),
            'classes': ('collapse',)
        }),
        ('参与人员', {
            'fields': ('other_participants',),
            'classes': ('collapse',)
        }),
        ('情感记录', {
            'fields': ('emotional_impact', 'personal_reflection')
        }),
        ('标签', {
            'fields': ('tags',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """只显示当前用户的重要时刻"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(RelationshipStatistics)
class RelationshipStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_people', 'total_interactions', 'total_moments', 'active_relationships', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username',)
    readonly_fields = (
        'total_people', 'total_interactions', 'total_moments', 
        'relationship_distribution', 'interaction_frequency',
        'active_relationships', 'dormant_relationships',
        'weekly_interactions', 'monthly_interactions', 'last_updated'
    )
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user',)
        }),
        ('基础统计', {
            'fields': ('total_people', 'total_interactions', 'total_moments')
        }),
        ('关系分布', {
            'fields': ('relationship_distribution', 'interaction_frequency'),
            'classes': ('collapse',)
        }),
        ('活跃度统计', {
            'fields': ('active_relationships', 'dormant_relationships')
        }),
        ('时间统计', {
            'fields': ('weekly_interactions', 'monthly_interactions'),
            'classes': ('collapse',)
        }),
        ('更新时间', {
            'fields': ('last_updated',)
        }),
    )
    
    def get_queryset(self, request):
        """只显示当前用户的统计信息"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(RelationshipReminder)
class RelationshipReminderAdmin(admin.ModelAdmin):
    list_display = ('person', 'title', 'reminder_type', 'reminder_date', 'status', 'snooze_count', 'created_at')
    list_filter = ('reminder_type', 'status', 'is_recurring', 'reminder_date', 'created_at')
    search_fields = ('person__name', 'title', 'description')
    readonly_fields = ('snooze_count', 'created_at', 'updated_at', 'completed_at')
    list_editable = ('status',)
    date_hierarchy = 'reminder_date'
    
    fieldsets = (
        ('基础信息', {
            'fields': ('user', 'person', 'reminder_type')
        }),
        ('提醒内容', {
            'fields': ('title', 'description')
        }),
        ('时间设置', {
            'fields': ('reminder_date', 'reminder_time', 'is_recurring', 'recurrence_pattern')
        }),
        ('状态管理', {
            'fields': ('status', 'snooze_count', 'max_snooze')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """只显示当前用户的提醒"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


# ===== 功能推荐系统管理 =====

# 导入新模型
from .models import Feature, UserFeaturePermission, FeatureRecommendation, UserFirstVisit

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'feature_type', 'category', 'is_active', 'is_public', 
                   'recommendation_weight', 'popularity_score', 'total_usage_count', 'created_at')
    list_filter = ('feature_type', 'category', 'is_active', 'is_public', 'require_login', 'require_membership')
    search_fields = ('name', 'description', 'url_name')
    list_editable = ('is_active', 'is_public', 'recommendation_weight')
    readonly_fields = ('popularity_score', 'total_usage_count', 'monthly_usage_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('基础信息', {
            'fields': ('name', 'description', 'feature_type', 'category')
        }),
        ('访问配置', {
            'fields': ('url_name', 'icon_class', 'icon_color')
        }),
        ('权限设置', {
            'fields': ('is_active', 'is_public', 'require_login', 'require_membership')
        }),
        ('推荐设置', {
            'fields': ('recommendation_weight',)
        }),
        ('统计信息', {
            'fields': ('popularity_score', 'total_usage_count', 'monthly_usage_count'),
            'classes': ('collapse',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_features', 'deactivate_features', 'reset_usage_stats']
    
    def activate_features(self, request, queryset):
        """批量激活功能"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"已激活 {updated} 个功能")
    activate_features.short_description = "激活选中的功能"
    
    def deactivate_features(self, request, queryset):
        """批量停用功能"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"已停用 {updated} 个功能")
    deactivate_features.short_description = "停用选中的功能"
    
    def reset_usage_stats(self, request, queryset):
        """重置使用统计"""
        updated = queryset.update(total_usage_count=0, monthly_usage_count=0, popularity_score=0)
        self.message_user(request, f"已重置 {updated} 个功能的使用统计")
    reset_usage_stats.short_description = "重置使用统计"


@admin.register(UserFeaturePermission)
class UserFeaturePermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'feature', 'is_visible', 'is_allowed', 'custom_weight', 'created_by', 'created_at')
    list_filter = ('is_visible', 'is_allowed', 'feature__category', 'feature__feature_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'feature__name')
    list_editable = ('is_visible', 'is_allowed', 'custom_weight')
    autocomplete_fields = ['user', 'feature', 'created_by']
    
    fieldsets = (
        ('权限设置', {
            'fields': ('user', 'feature', 'is_visible', 'is_allowed', 'custom_weight')
        }),
        ('管理信息', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """保存时自动设置创建者"""
        if not change:  # 新创建的记录
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['grant_permissions', 'revoke_permissions', 'hide_features', 'show_features']
    
    def grant_permissions(self, request, queryset):
        """批量授权"""
        updated = queryset.update(is_allowed=True)
        self.message_user(request, f"已授权 {updated} 个用户功能")
    grant_permissions.short_description = "授权选中的用户功能"
    
    def revoke_permissions(self, request, queryset):
        """批量撤销权限"""
        updated = queryset.update(is_allowed=False)
        self.message_user(request, f"已撤销 {updated} 个用户功能权限")
    revoke_permissions.short_description = "撤销选中的用户功能权限"
    
    def hide_features(self, request, queryset):
        """批量隐藏功能"""
        updated = queryset.update(is_visible=False)
        self.message_user(request, f"已隐藏 {updated} 个用户功能")
    hide_features.short_description = "隐藏选中的用户功能"
    
    def show_features(self, request, queryset):
        """批量显示功能"""
        updated = queryset.update(is_visible=True)
        self.message_user(request, f"已显示 {updated} 个用户功能")
    show_features.short_description = "显示选中的用户功能"


@admin.register(FeatureRecommendation)
class FeatureRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'feature', 'action', 'recommendation_reason', 'recommendation_algorithm', 
                   'created_at', 'action_time')
    list_filter = ('action', 'recommendation_algorithm', 'feature__category', 'feature__feature_type', 
                  'created_at', 'action_time')
    search_fields = ('user__username', 'feature__name', 'recommendation_reason', 'session_id')
    readonly_fields = ('created_at', 'action_time', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('推荐信息', {
            'fields': ('user', 'feature', 'session_id', 'action')
        }),
        ('推荐上下文', {
            'fields': ('recommendation_reason', 'user_mode_preference', 'recommendation_algorithm')
        }),
        ('时间信息', {
            'fields': ('created_at', 'action_time')
        }),
        ('环境信息', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """禁止手动添加推荐记录"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许查看，不允许修改"""
        return False


@admin.register(UserFirstVisit)
class UserFirstVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_visit_time', 'has_seen_recommendation', 'recommendation_shown_count',
                   'total_login_count', 'total_feature_usage', 'last_recommendation_time')
    list_filter = ('has_seen_recommendation', 'first_visit_time', 'last_recommendation_time')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('first_visit_time', 'user')
    
    fieldsets = (
        ('用户信息', {
            'fields': ('user', 'first_visit_time')
        }),
        ('推荐状态', {
            'fields': ('has_seen_recommendation', 'recommendation_shown_count', 'last_recommendation_time')
        }),
        ('使用统计', {
            'fields': ('total_login_count', 'total_feature_usage')
        }),
    )
    
    actions = ['reset_recommendation_status']
    
    def reset_recommendation_status(self, request, queryset):
        """重置推荐状态"""
        updated = queryset.update(has_seen_recommendation=False, recommendation_shown_count=0,
                                last_recommendation_time=None)
        self.message_user(request, f"已重置 {updated} 个用户的推荐状态")
    reset_recommendation_status.short_description = "重置推荐状态"
    
    def has_add_permission(self, request):
        """禁止手动添加首次访问记录"""
        return False


@admin.register(UserGeneratedTravelGuide)
class UserGeneratedTravelGuideAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'destination', 'travel_style', 'view_count', 'download_count', 'use_count', 'is_public', 'is_featured', 'is_approved', 'created_at')
    list_filter = ('travel_style', 'budget_range', 'is_public', 'is_featured', 'is_approved', 'created_at')
    search_fields = ('title', 'destination', 'content', 'user__username')
    readonly_fields = ('view_count', 'download_count', 'use_count', 'created_at', 'updated_at')
    list_editable = ('is_public', 'is_featured', 'is_approved')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('user', 'title', 'destination', 'content', 'summary')
        }),
        ('攻略分类', {
            'fields': ('travel_style', 'budget_range', 'travel_duration', 'interests')
        }),
        ('文件附件', {
            'fields': ('attachment', 'attachment_name'),
            'classes': ('collapse',)
        }),
        ('统计信息', {
            'fields': ('view_count', 'download_count', 'use_count'),
            'classes': ('collapse',)
        }),
        ('状态设置', {
            'fields': ('is_public', 'is_featured', 'is_approved')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TravelGuideUsage)
class TravelGuideUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'guide', 'usage_type', 'created_at')
    list_filter = ('usage_type', 'created_at')
    search_fields = ('user__username', 'guide__title')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('使用记录', {
            'fields': ('user', 'guide', 'usage_type', 'created_at')
        }),
    )