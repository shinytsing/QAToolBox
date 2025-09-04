from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    # 验证码相关
    path("generate-progressive-captcha/", views.generate_progressive_captcha, name="generate_progressive_captcha"),
    path("verify-progressive-captcha/", views.verify_progressive_captcha, name="verify_progressive_captcha"),
    # 管理员用户管理
    path("admin/users/", views.admin_user_management, name="admin_user_management"),
    path("admin/users/<int:user_id>/", views.admin_user_detail, name="admin_user_detail"),
    path("admin/logs/", views.admin_user_logs, name="admin_user_logs"),
    path("admin/monitoring/", views.admin_user_monitoring, name="admin_user_monitoring"),
    # 管理员用户管理API
    path("api/admin/change-status/<int:user_id>/", views.admin_change_user_status_api, name="admin_change_user_status_api"),
    path("api/admin/change-membership/<int:user_id>/", views.admin_change_membership_api, name="admin_change_membership_api"),
    path("api/admin/change-role/<int:user_id>/", views.admin_change_role_api, name="admin_change_role_api"),
    path("api/admin/delete-user/<int:user_id>/", views.admin_delete_user_api, name="admin_delete_user_api"),
    path("api/admin/batch-operation/", views.admin_batch_operation_api, name="admin_batch_operation_api"),
    path("api/admin/monitoring-stats/", views.admin_monitoring_stats_api, name="admin_monitoring_stats_api"),
    path("api/admin/force-logout/<int:user_id>/", views.admin_force_logout_api, name="admin_force_logout_api"),
    # 主题API
    path("theme/", views.theme_api, name="theme_api"),
    # 头像上传API
    path("upload_avatar/", views.upload_avatar, name="upload_avatar"),
    # 头像上传测试页面
    path("avatar_test/", views.avatar_test_view, name="avatar_test"),
    # 用户认证API - 修复路径
    path("api/session-status/", views.session_status_api, name="session_status_api"),
    path("api/logout/", views.user_logout_api, name="user_logout_api"),
    path("api/extend-session/", views.extend_session_api, name="extend_session_api"),
    # 测试页面
    path("test-logout/", views.test_logout_view, name="test_logout"),
]
