"""
社交娱乐模块路由
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建路由器
router = DefaultRouter()
router.register(r'chat', views.ChatRoomViewSet, basename='chat-room')
router.register(r'messages', views.ChatMessageViewSet, basename='chat-message')
router.register(r'heart-link', views.HeartLinkViewSet, basename='heart-link')
router.register(r'buddy-events', views.BuddyEventViewSet, basename='buddy-event')
router.register(r'tarot', views.TarotReadingViewSet, basename='tarot-reading')
router.register(r'story', views.StoryGeneratorViewSet, basename='story-generator')
router.register(r'travel', views.TravelGuideViewSet, basename='travel-guide')
router.register(r'fortune', views.FortuneAnalyzerViewSet, basename='fortune-analyzer')

urlpatterns = [
    path('', include(router.urls)),
]
