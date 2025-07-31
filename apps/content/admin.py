from django.contrib import admin
from .models import Article, Comment, Suggestion, Feedback

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'suggestion_type', 'status', 'user_name', 'created_at')
    list_filter = ('suggestion_type', 'status', 'created_at')
    search_fields = ('title', 'content', 'user_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'content', 'suggestion_type', 'status')
        }),
        ('用户信息', {
            'fields': ('user', 'user_name', 'user_email')
        }),
        ('管理回复', {
            'fields': ('admin_response',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_type', 'status', 'user_name', 'created_at')
    list_filter = ('feedback_type', 'status', 'created_at')
    search_fields = ('content', 'user_name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('feedback_type', 'content', 'status')
        }),
        ('用户信息', {
            'fields': ('user', 'user_name', 'user_email')
        }),
        ('管理回复', {
            'fields': ('admin_response',)
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
