from django.contrib import admin

from .models import AILink, Announcement, Article, Comment, FeatureAccess, Feedback, Suggestion, UserFeatureAccess


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "content")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("article", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content",)


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("title", "suggestion_type", "status", "user_name", "created_at", "has_media")
    list_filter = ("suggestion_type", "status", "created_at")
    search_fields = ("title", "content", "user_name")
    readonly_fields = ("created_at", "updated_at", "media_preview")

    def has_media(self, obj):
        """显示是否有媒体文件"""
        has_images = obj.images and len(obj.images) > 0
        has_videos = obj.videos and len(obj.videos) > 0
        if has_images and has_videos:
            return f"📷{len(obj.images)} 📹{len(obj.videos)}"
        elif has_images:
            return f"📷{len(obj.images)}"
        elif has_videos:
            return f"📹{len(obj.videos)}"
        return "无"

    has_media.short_description = "媒体文件"

    def media_preview(self, obj):
        """预览媒体文件"""
        html = []
        if obj.images:
            html.append("<h4>图片文件:</h4>")
            for img in obj.images:
                html.append(f'<img src="{img["url"]}" style="max-width: 200px; max-height: 150px; margin: 5px;" />')

        if obj.videos:
            html.append("<h4>视频文件:</h4>")
            for video in obj.videos:
                html.append(
                    f'<video controls style="max-width: 300px; max-height: 200px; margin: 5px;"><source src="{video["url"]}" type="video/mp4">您的浏览器不支持视频播放。</video>'
                )

        return "".join(html) if html else "无媒体文件"

    media_preview.short_description = "媒体预览"
    media_preview.allow_tags = True

    fieldsets = (
        ("基本信息", {"fields": ("title", "content", "suggestion_type", "status")}),
        ("用户信息", {"fields": ("user", "user_name", "user_email")}),
        ("媒体文件", {"fields": ("images", "videos", "media_preview"), "classes": ("collapse",)}),
        ("管理回复", {"fields": ("admin_response",)}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("feedback_type", "status", "user_name", "created_at")
    list_filter = ("feedback_type", "status", "created_at")
    search_fields = ("content", "user_name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本信息", {"fields": ("feedback_type", "content", "status")}),
        ("用户信息", {"fields": ("user", "user_name", "user_email")}),
        ("管理回复", {"fields": ("admin_response",)}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(AILink)
class AILinkAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "url", "is_active", "sort_order", "icon_preview")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "url", "description")
    list_editable = ("is_active", "sort_order")
    readonly_fields = ("created_at", "updated_at", "icon_preview")

    def icon_preview(self, obj):
        """预览图标"""
        if obj.icon:
            return f'<img src="{obj.icon.url}" style="max-width: 28px; max-height: 28px;" />'
        elif obj.icon_url:
            return f'<img src="{obj.icon_url}" style="max-width: 28px; max-height: 28px;" />'
        return "无图标"

    icon_preview.short_description = "图标预览"
    icon_preview.allow_tags = True

    fieldsets = (
        ("基本信息", {"fields": ("name", "url", "category", "description")}),
        ("图标设置", {"fields": ("icon", "icon_url", "icon_preview")}),
        ("显示设置", {"fields": ("is_active", "sort_order")}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "priority", "status", "is_popup", "created_by", "created_at")
    list_filter = ("priority", "status", "is_popup", "created_at")
    search_fields = ("title", "content")
    list_editable = ("priority", "status", "is_popup")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("基本信息", {"fields": ("title", "content", "priority", "status")}),
        ("显示设置", {"fields": ("is_popup", "start_time", "end_time")}),
        ("管理信息", {"fields": ("created_by", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(FeatureAccess)
class FeatureAccessAdmin(admin.ModelAdmin):
    list_display = ("feature_name", "feature_key", "status", "visibility", "sort_order", "access_count", "is_active")
    list_filter = ("status", "visibility", "is_active", "created_at")
    search_fields = ("feature_name", "feature_key", "description")
    list_editable = ("status", "visibility", "sort_order", "is_active")
    readonly_fields = ("access_count", "created_at", "updated_at")

    fieldsets = (
        ("基本信息", {"fields": ("feature_key", "feature_name", "description", "url_path", "icon")}),
        ("访问控制", {"fields": ("status", "visibility", "is_active")}),
        ("显示设置", {"fields": ("sort_order",)}),
        ("统计信息", {"fields": ("access_count", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["enable_features", "disable_features", "set_public", "set_admin_only"]

    def enable_features(self, request, queryset):
        updated = queryset.update(is_active=True, status="enabled")
        self.message_user(request, f"已启用 {updated} 个功能")

    enable_features.short_description = "启用选中的功能"

    def disable_features(self, request, queryset):
        updated = queryset.update(is_active=False, status="disabled")
        self.message_user(request, f"已禁用 {updated} 个功能")

    disable_features.short_description = "禁用选中的功能"

    def set_public(self, request, queryset):
        updated = queryset.update(visibility="public")
        self.message_user(request, f"已将 {updated} 个功能设为公开")

    set_public.short_description = "设为所有用户可见"

    def set_admin_only(self, request, queryset):
        updated = queryset.update(visibility="admin")
        self.message_user(request, f"已将 {updated} 个功能设为管理员专用")

    set_admin_only.short_description = "设为管理员专用"


@admin.register(UserFeatureAccess)
class UserFeatureAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "feature", "is_enabled", "access_count", "last_accessed")
    list_filter = ("is_enabled", "feature__status", "last_accessed", "created_at")
    search_fields = ("user__username", "feature__feature_name")
    list_editable = ("is_enabled",)
    readonly_fields = ("access_count", "last_accessed", "created_at")

    fieldsets = (
        ("基本信息", {"fields": ("user", "feature", "is_enabled")}),
        ("统计信息", {"fields": ("access_count", "last_accessed", "created_at"), "classes": ("collapse",)}),
    )
