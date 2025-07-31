from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('generate-captcha/', views.generate_captcha, name='generate_captcha'),
    
    # 管理员用户管理
    path('admin/users/', views.admin_user_management, name='admin_user_management'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/logs/', views.admin_user_logs, name='admin_user_logs'),
    
    # 管理员用户管理API
    path('api/admin/change-status/<int:user_id>/', views.admin_change_user_status_api, name='admin_change_user_status_api'),
    path('api/admin/change-membership/<int:user_id>/', views.admin_change_membership_api, name='admin_change_membership_api'),
    path('api/admin/change-role/<int:user_id>/', views.admin_change_role_api, name='admin_change_role_api'),
    path('api/admin/delete-user/<int:user_id>/', views.admin_delete_user_api, name='admin_delete_user_api'),
    path('api/admin/batch-operation/', views.admin_batch_operation_api, name='admin_batch_operation_api'),
]
