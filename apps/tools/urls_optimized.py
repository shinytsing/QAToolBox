from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 导入优化后的视图
from .views.diary_views import (
    diary_dashboard, diary_list, create_diary_entry, update_diary_entry,
    delete_diary_entry, diary_detail, diary_statistics, diary_calendar,
    mood_analysis, batch_delete_diary_entries, export_diary_entries,
    DiaryAPIView
)

from .views.chat_views import (
    chat_dashboard, chat_room_list, chat_room_detail, send_message,
    create_chat_room, join_chat_room, leave_chat_room, update_online_status,
    online_users_list, create_heart_link_request, heart_link_status,
    cancel_heart_link_request, available_heart_links, accept_heart_link,
    ChatAPIView, message_history
)

# 导入原有的其他视图（保持兼容性）
from . import views

app_name = 'tools'

# 日记相关URL
diary_patterns = [
    path('diary/', diary_dashboard, name='diary_dashboard'),
    path('diary/list/', diary_list, name='diary_list'),
    path('diary/create/', create_diary_entry, name='create_diary_entry'),
    path('diary/<int:entry_id>/', diary_detail, name='diary_detail'),
    path('diary/<int:entry_id>/update/', update_diary_entry, name='update_diary_entry'),
    path('diary/<int:entry_id>/delete/', delete_diary_entry, name='delete_diary_entry'),
    path('diary/statistics/', diary_statistics, name='diary_statistics'),
    path('diary/calendar/', diary_calendar, name='diary_calendar'),
    path('diary/mood-analysis/', mood_analysis, name='mood_analysis'),
    path('diary/batch-delete/', batch_delete_diary_entries, name='batch_delete_diary_entries'),
    path('diary/export/', export_diary_entries, name='export_diary_entries'),
    
    # API路由
    path('api/diary/', DiaryAPIView.as_view(), name='diary_api'),
]

# 聊天相关URL
chat_patterns = [
    path('chat/', chat_dashboard, name='chat_dashboard'),
    path('chat/rooms/', chat_room_list, name='chat_room_list'),
    path('chat/room/<str:room_id>/', chat_room_detail, name='chat_room_detail'),
    path('chat/room/<str:room_id>/send/', send_message, name='send_message'),
    path('chat/room/<str:room_id>/join/', join_chat_room, name='join_chat_room'),
    path('chat/room/<str:room_id>/leave/', leave_chat_room, name='leave_chat_room'),
    path('chat/room/<str:room_id>/history/', message_history, name='message_history'),
    path('chat/create-room/', create_chat_room, name='create_chat_room'),
    path('chat/online-status/', update_online_status, name='update_online_status'),
    path('chat/online-users/', online_users_list, name='online_users_list'),
    
    # 心动链接相关
    path('chat/heart-link/create/', create_heart_link_request, name='create_heart_link_request'),
    path('chat/heart-link/<int:request_id>/status/', heart_link_status, name='heart_link_status'),
    path('chat/heart-link/<int:request_id>/cancel/', cancel_heart_link_request, name='cancel_heart_link_request'),
    path('chat/heart-link/available/', available_heart_links, name='available_heart_links'),
    path('chat/heart-link/<int:request_id>/accept/', accept_heart_link, name='accept_heart_link'),
    
    # API路由
    path('api/chat/<str:room_id>/', ChatAPIView.as_view(), name='chat_api'),
    path('api/chat/<str:room_id>/mark-read/', views.mark_messages_read_api, name='mark_messages_read'),
    path('api/heart-link/cleanup/', views.cleanup_heart_link_api, name='cleanup_heart_link'),
    path('api/heart-link/create/', views.create_heart_link_request_api, name='create_heart_link_api'),
    path('api/heart-link/status/', views.check_heart_link_status_api, name='heart_link_status_api'),
]

# 目标管理相关URL
goal_patterns = [
    path('goals/', views.life_goals_dashboard, name='life_goals_dashboard'),
    path('goals/list/', views.life_goals_list, name='life_goals_list'),
    path('goals/create/', views.create_life_goal, name='create_life_goal'),
    path('goals/<int:goal_id>/', views.life_goal_detail, name='life_goal_detail'),
    path('goals/<int:goal_id>/update/', views.update_life_goal, name='update_life_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_life_goal, name='delete_life_goal'),
    path('goals/<int:goal_id>/progress/', views.update_goal_progress, name='update_goal_progress'),
    path('goals/statistics/', views.goals_statistics, name='goals_statistics'),
]

# 社交媒体订阅相关URL
social_media_patterns = [
    path('social-media/', views.social_media_dashboard, name='social_media_dashboard'),
    path('social-media/subscriptions/', views.subscription_list, name='subscription_list'),
    path('social-media/subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('social-media/subscriptions/<int:subscription_id>/', views.subscription_detail, name='subscription_detail'),
    path('social-media/subscriptions/<int:subscription_id>/update/', views.update_subscription, name='update_subscription'),
    path('social-media/subscriptions/<int:subscription_id>/delete/', views.delete_subscription, name='delete_subscription'),
    path('social-media/notifications/', views.notification_list, name='notification_list'),
    path('social-media/notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
]

# 旅游攻略相关URL
travel_patterns = [
    path('travel/', views.travel_guide_dashboard, name='travel_guide_dashboard'),
    path('travel/create/', views.create_travel_guide, name='create_travel_guide'),
    path('travel/<int:guide_id>/', views.travel_guide_detail, name='travel_guide_detail'),
    path('travel/<int:guide_id>/export/', views.export_travel_guide, name='export_travel_guide'),
    path('travel/history/', views.travel_guide_history, name='travel_guide_history'),
]

# 食物随机选择器相关URL
food_patterns = [
    path('food/', views.food_randomizer_dashboard, name='food_randomizer_dashboard'),
    path('food/randomize/', views.randomize_food, name='randomize_food'),
    path('food/history/', views.food_history, name='food_history'),
    path('food/items/', views.food_items_list, name='food_items_list'),
    path('food/items/create/', views.create_food_item, name='create_food_item'),
    path('food/items/<int:item_id>/', views.food_item_detail, name='food_item_detail'),
]

# 塔罗牌相关URL
tarot_patterns = [
    path('tarot/', views.tarot_dashboard, name='tarot_dashboard'),
    path('tarot/reading/', views.create_tarot_reading, name='create_tarot_reading'),
    path('tarot/reading/<int:reading_id>/', views.tarot_reading_detail, name='tarot_reading_detail'),
    path('tarot/history/', views.tarot_reading_history, name='tarot_reading_history'),
    path('tarot/community/', views.tarot_community, name='tarot_community'),
    path('tarot/community/post/', views.create_community_post, name='create_community_post'),
]

# 健身训练相关URL
fitness_patterns = [
    path('fitness/', views.fitness_dashboard, name='fitness_dashboard'),
    path('fitness/workout/', views.create_workout_session, name='create_workout_session'),
    path('fitness/workout/<int:session_id>/', views.workout_session_detail, name='workout_session_detail'),
    path('fitness/history/', views.fitness_history, name='fitness_history'),
    path('fitness/statistics/', views.fitness_statistics, name='fitness_statistics'),
]

# 代码训练相关URL
coding_patterns = [
    path('coding/', views.coding_dashboard, name='coding_dashboard'),
    path('coding/workout/', views.create_code_workout, name='create_code_workout'),
    path('coding/workout/<int:session_id>/', views.code_workout_detail, name='code_workout_detail'),
    path('coding/history/', views.coding_history, name='coding_history'),
    path('coding/achievements/', views.coding_achievements, name='coding_achievements'),
]

# 欲望仪表盘相关URL
desire_patterns = [
    path('desire/', views.desire_dashboard, name='desire_dashboard'),
    path('desire/items/', views.desire_items_list, name='desire_items_list'),
    path('desire/items/create/', views.create_desire_item, name='create_desire_item'),
    path('desire/items/<int:item_id>/', views.desire_item_detail, name='desire_item_detail'),
    path('desire/fulfillment/', views.desire_fulfillment, name='desire_fulfillment'),
]

# 人际关系相关URL
relationship_patterns = [
    path('relationships/', views.relationship_dashboard, name='relationship_dashboard'),
    path('relationships/people/', views.person_list, name='person_list'),
    path('relationships/people/create/', views.create_person, name='create_person'),
    path('relationships/people/<int:person_id>/', views.person_detail, name='person_detail'),
    path('relationships/interactions/', views.interaction_list, name='interaction_list'),
    path('relationships/interactions/create/', views.create_interaction, name='create_interaction'),
]

# 工具使用相关URL
tool_patterns = [
    path('tools/', views.tools_dashboard, name='tools_dashboard'),
    path('tools/usage/', views.tool_usage_list, name='tool_usage_list'),
    path('tools/usage/<int:usage_id>/', views.tool_usage_detail, name='tool_usage_detail'),
    path('tools/statistics/', views.tools_statistics, name='tools_statistics'),
]

# 管理相关URL
admin_patterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_management, name='admin_user_management'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/logs/', views.admin_logs, name='admin_logs'),
    path('admin/statistics/', views.admin_statistics, name='admin_statistics'),
]

# API版本控制
api_v1_patterns = [
    path('api/v1/diary/', include(diary_patterns)),
    path('api/v1/chat/', include(chat_patterns)),
    path('api/v1/goals/', include(goal_patterns)),
    path('api/v1/social-media/', include(social_media_patterns)),
    path('api/v1/travel/', include(travel_patterns)),
    path('api/v1/food/', include(food_patterns)),
    path('api/v1/tarot/', include(tarot_patterns)),
    path('api/v1/fitness/', include(fitness_patterns)),
    path('api/v1/coding/', include(coding_patterns)),
    path('api/v1/desire/', include(desire_patterns)),
    path('api/v1/relationships/', include(relationship_patterns)),
    path('api/v1/tools/', include(tool_patterns)),
]

# 主URL配置
urlpatterns = [
    # 基础路由
    path('', views.tools_dashboard, name='tools_dashboard'),
    
    # 功能模块路由
    path('diary/', include(diary_patterns)),
    path('chat/', include(chat_patterns)),
    path('goals/', include(goal_patterns)),
    path('social-media/', include(social_media_patterns)),
    path('travel/', include(travel_patterns)),
    path('food/', include(food_patterns)),
    path('tarot/', include(tarot_patterns)),
    path('fitness/', include(fitness_patterns)),
    path('coding/', include(coding_patterns)),
    path('desire/', include(desire_patterns)),
    path('relationships/', include(relationship_patterns)),
    path('tools/', include(tool_patterns)),
    
    # 管理路由
    path('admin/', include(admin_patterns)),
    
    # API路由
    path('api/v1/', include(api_v1_patterns)),
    
    # 保持原有路由的兼容性
    path('test-case-generator/', views.test_case_generator, name='test_case_generator'),
    path('quality-check/', views.quality_check, name='quality_check'),
    path('performance-test/', views.performance_test, name='performance_test'),
    path('redbook-generator/', views.redbook_generator, name='redbook_generator'),
    
    # 其他原有路由
    path('guitar-training/', views.guitar_training, name='guitar_training'),
    path('fitness-tools/', views.fitness_tools, name='fitness_tools'),
    path('time-capsule/', views.time_capsule, name='time_capsule'),
    path('pdf-converter/', views.pdf_converter, name='pdf_converter'),
    path('proxy/', views.proxy_view, name='proxy_view'),
    path('monitoring/', views.monitoring_view, name='monitoring_view'),
    
    # WebSocket路由
    path('ws/chat/<str:room_id>/', views.ChatConsumer.as_asgi(), name='chat_websocket'),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
