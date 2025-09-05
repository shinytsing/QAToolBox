"""
管理模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'users', views.UserManagementViewSet, basename='user-management')
router.register(r'features', views.FeatureManagementViewSet, basename='feature-management')
router.register(r'stats', views.SystemStatsViewSet, basename='system-stats')
router.register(r'notifications', views.NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]
