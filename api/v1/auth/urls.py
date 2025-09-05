"""
认证模块路由
"""
from django.urls import path
from . import views
from . import unified_views

urlpatterns = [
    # 统一认证（多端登录）
    path('unified/login/', unified_views.unified_login, name='unified_login'),
    path('unified/devices/', unified_views.get_user_devices, name='get_user_devices'),
    path('unified/devices/<str:device_id>/terminate/', unified_views.terminate_device, name='terminate_device'),
    path('unified/devices/terminate-all/', unified_views.terminate_all_devices, name='terminate_all_devices'),
    path('unified/sync/', unified_views.sync_data, name='sync_data'),
    path('unified/sync-user-data/', unified_views.sync_user_data, name='sync_user_data'),
    
    # 传统认证（向后兼容）
    path('register/', views.user_register, name='user_register'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('refresh/', views.refresh_token, name='refresh_token'),
    
    # 用户资料
    path('profile/', views.get_profile, name='get_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # 密码管理
    path('change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
