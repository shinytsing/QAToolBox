"""
生活工具模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'diary', views.LifeDiaryViewSet, basename='life-diary')
router.register(r'food', views.FoodRandomizationViewSet, basename='food-randomization')
router.register(r'checkin', views.CheckInViewSet, basename='checkin')
router.register(r'meditation', views.MeditationViewSet, basename='meditation')
router.register(r'ai-writing', views.AIWritingViewSet, basename='ai-writing')

urlpatterns = [
    path('', include(router.urls)),
]
