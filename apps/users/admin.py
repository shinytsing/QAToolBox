from django.contrib import admin
from .models import Profile, UserRole, UserStatus, UserMembership, UserActionLog, UserTheme, UserModePreference


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "phone")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at", "updated_at")
    list_filter = ("role", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "suspended_until", "banned_phone", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("user__username", "user__email", "banned_phone")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本信息", {"fields": ("user", "status", "reason")}),
        ("暂停设置", {"fields": ("suspended_until",)}),
        ("封禁设置", {"fields": ("banned_phone",)}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "membership_type", "is_active", "start_date", "end_date")
    list_filter = ("membership_type", "is_active", "start_date", "end_date")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本信息", {"fields": ("user", "membership_type", "is_active")}),
        ("时间设置", {"fields": ("start_date", "end_date")}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ("admin_user", "target_user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("admin_user__username", "target_user__username", "details")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("操作信息", {"fields": ("admin_user", "target_user", "action", "details")}),
        ("时间信息", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(UserTheme)
class UserThemeAdmin(admin.ModelAdmin):
    list_display = ("user", "mode", "theme_style", "switch_count", "last_switch_time", "created_at", "updated_at")
    list_filter = ("mode", "theme_style", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "switch_count", "last_switch_time")
    fieldsets = (
        ("基本信息", {"fields": ("user", "mode", "theme_style")}),
        ("使用统计", {"fields": ("switch_count", "last_switch_time"), "classes": ("collapse",)}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(UserModePreference)
class UserModePreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "mode", "click_count", "last_click_time", "created_at", "updated_at")
    list_filter = ("mode", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "last_click_time")
    ordering = ("-click_count", "-last_click_time")
    fieldsets = (
        ("基本信息", {"fields": ("user", "mode", "click_count")}),
        ("使用统计", {"fields": ("last_click_time",), "classes": ("collapse",)}),
        ("时间信息", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        """优化查询，减少数据库访问"""
        return super().get_queryset(request).select_related("user")
