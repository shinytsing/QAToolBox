from django.urls import path

app_name = "content"

from .views import (
    admin_announcements,
    admin_batch_change_status_api,
    admin_dashboard,
    admin_dashboard_stats_api,
    admin_feedback,
    admin_reply_feedback,
    admin_reply_suggestion,
    admin_suggestions,
    ai_links_view,
    announcement_admin_api,
    announcement_delete_api,
    announcement_list_api,
    article_create,
    article_delete,
    article_detail,
    article_edit,
    article_list,
    create_ai_links_from_list,
    feedback_api,
    fetch_ai_link_icon,
    suggestions_api,
    upload_media_api,
)
from .views_admin_features import (
    admin_feature_management,
    admin_init_default_features_api,
    admin_user_feature_access,
    batch_update_feature_status_api,
    batch_update_user_feature_access_api,
    feature_list_api,
    update_feature_status_api,
    update_user_feature_access_api,
)

urlpatterns = [
    path("", article_list, name="article_list"),  # 文章列表
    path("<int:pk>/", article_detail, name="article_detail"),  # 查看单个文章
    path("create/", article_create, name="article_create"),  # 创建文章
    path("edit/<int:pk>/", article_edit, name="article_edit"),  # 编辑文章
    path("delete/<int:pk>/", article_delete, name="article_delete"),  # 删除文章
    # AI友情链接
    path("ai-links/", ai_links_view, name="ai_links"),
    path("api/ai-links/fetch-icon/", fetch_ai_link_icon, name="fetch_ai_link_icon"),
    path("api/ai-links/create-from-list/", create_ai_links_from_list, name="create_ai_links_from_list"),
    # 建议和反馈API
    path("api/suggestions/", suggestions_api, name="suggestions_api"),
    path("api/feedback/", feedback_api, name="feedback_api"),
    path("api/upload-media/", upload_media_api, name="upload_media_api"),
    # 公告API
    path("api/announcements/", announcement_list_api, name="announcement_list_api"),
    path("api/admin/announcements/", announcement_admin_api, name="announcement_admin_api"),
    path("api/admin/announcements/<int:announcement_id>/", announcement_delete_api, name="announcement_delete_api"),
    # 管理员管理页面
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("admin/suggestions/", admin_suggestions, name="admin_suggestions"),
    path("admin/feedback/", admin_feedback, name="admin_feedback"),
    path("admin/announcements/", admin_announcements, name="admin_announcements"),
    path("admin/features/", admin_feature_management, name="admin_feature_management"),
    path("admin/users/<int:user_id>/features/", admin_user_feature_access, name="admin_user_feature_access"),
    # 管理员API
    path("api/admin/reply-suggestion/", admin_reply_suggestion, name="admin_reply_suggestion"),
    path("api/admin/reply-feedback/", admin_reply_feedback, name="admin_reply_feedback"),
    path("api/admin/dashboard-stats/", admin_dashboard_stats_api, name="admin_dashboard_stats_api"),
    path("api/admin/batch-change-status/", admin_batch_change_status_api, name="admin_batch_change_status_api"),
    # 功能管理API
    path("api/admin/features/", feature_list_api, name="feature_list_api"),
    path("api/admin/features/update/", update_feature_status_api, name="update_feature_status_api"),
    path("api/admin/features/batch-update/", batch_update_feature_status_api, name="batch_update_feature_status_api"),
    path("api/admin/features/init-default/", admin_init_default_features_api, name="admin_init_default_features_api"),
    path("api/admin/user-features/update/", update_user_feature_access_api, name="update_user_feature_access_api"),
    path(
        "api/admin/user-features/batch-update/",
        batch_update_user_feature_access_api,
        name="batch_update_user_feature_access_api",
    ),
]
