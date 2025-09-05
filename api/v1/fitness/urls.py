"""
健身模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'workouts', views.FitnessWorkoutViewSet, basename='fitness-workout')
router.register(r'profile', views.FitnessProfileViewSet, basename='fitness-profile')
router.register(r'posts', views.FitnessCommunityPostViewSet, basename='fitness-post')

urlpatterns = [
    path('', include(router.urls)),
]
