from django.urls import path
from .views import (
    article_list, article_detail, article_create, article_edit, article_delete,
    suggestions_api, feedback_api, admin_suggestions, admin_feedback,
    admin_reply_suggestion, admin_reply_feedback, admin_dashboard,
    admin_dashboard_stats_api, admin_batch_change_status_api
)

urlpatterns = [
    path('', article_list, name='article_list'),  # 文章列表
    path('<int:pk>/', article_detail, name='article_detail'),  # 查看单个文章
    path('create/', article_create, name='article_create'),  # 创建文章
    path('edit/<int:pk>/', article_edit, name='article_edit'),  # 编辑文章
    path('delete/<int:pk>/', article_delete, name='article_delete'),  # 删除文章
    
    # 建议和反馈API
    path('api/suggestions/', suggestions_api, name='suggestions_api'),
    path('api/feedback/', feedback_api, name='feedback_api'),
    
    # 管理员管理页面
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/suggestions/', admin_suggestions, name='admin_suggestions'),
    path('admin/feedback/', admin_feedback, name='admin_feedback'),
    path('api/admin/reply-suggestion/', admin_reply_suggestion, name='admin_reply_suggestion'),
    path('api/admin/reply-feedback/', admin_reply_feedback, name='admin_reply_feedback'),
    path('api/admin/dashboard-stats/', admin_dashboard_stats_api, name='admin_dashboard_stats_api'),
    path('api/admin/batch-change-status/', admin_batch_change_status_api, name='admin_batch_change_status_api'),
]
