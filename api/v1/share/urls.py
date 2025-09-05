"""
分享模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'records', views.ShareRecordViewSet, basename='share-record')
router.register(r'links', views.ShareLinkViewSet, basename='share-link')
router.register(r'pwa', views.PWAViewSet, basename='pwa')
router.register(r'widget', views.ShareWidgetViewSet, basename='share-widget')

urlpatterns = [
    path('', include(router.urls)),
]
