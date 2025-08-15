# QAToolbox/apps/tools/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings

from .views import (
    test_case_generator, redbook_generator, pdf_converter, pdf_converter_test, 
    fortune_analyzer, web_crawler, self_analysis, storyboard, 
    fitness_center, training_plan_editor, 
    emo_diary, creative_writer, meditation_guide, peace_meditation_view, music_healing,
    heart_link, heart_link_chat, chat_enhanced, chat_debug_view, douyin_analyzer, triple_awakening_dashboard, copilot_page,
    desire_dashboard, vanity_os_dashboard, vanity_rewards, sponsor_hall_of_fame,
    based_dev_avatar, vanity_todo_list, travel_guide, fitness_community,
    fitness_profile, fitness_tools, get_vanity_wealth_api, add_sin_points_api, music_api,
    # 添加缺失的API函数导入
    next_song_api, get_fitness_community_posts_api, create_fitness_community_post_api,
    like_fitness_post_api, comment_fitness_post_api, get_fitness_user_profile_api,
    get_job_applications_api, save_job_profile_api, get_job_profile_api,
    get_job_search_statistics_api, update_application_status_api, add_application_notes_api,
    generate_boss_qr_code_api, get_boss_login_page_url_api, get_boss_user_token_api,
    check_boss_login_status_selenium_api, boss_logout_api, send_contact_request_api,
    start_crawler_api, get_crawler_status_api,
    # Heart Link相关API
    create_heart_link_request_api, cancel_heart_link_request_api, check_heart_link_status_api,
    cleanup_heart_link_api,
    # 聊天相关API
    get_chat_messages_api, send_message_api, send_image_api, send_audio_api, send_file_api, send_video_api,
    delete_message_api, mark_messages_read_api, update_online_status_api, get_online_users_api, get_active_chat_rooms_api,
    # 用户资料相关API
    get_user_profile_api, get_chat_room_participants_api,
    # 数字匹配API
    number_match_api, cancel_number_match_api,
    # Desire相关API
    get_desire_dashboard_api, add_desire_api, check_desire_fulfillment_api, generate_ai_image_api,
    get_desire_progress_api, get_fulfillment_history_api, get_desire_todos_api, add_desire_todo_api,
    # 冥想音频API
    meditation_audio_api,
    complete_desire_todo_api, delete_desire_todo_api, edit_desire_todo_api, get_desire_todo_stats_api,
    # Vanity相关API
    get_vanity_tasks_api, add_vanity_task_api, complete_vanity_task_api, get_sponsors_api, add_sponsor_api,
    # Based Dev相关API
    create_based_dev_avatar_api, get_based_dev_avatar_api, update_based_dev_stats_api,
    like_based_dev_avatar_api, get_based_dev_achievements_api,
    # 旅游相关API
    check_local_travel_data_api, travel_guide_api, get_travel_guides_api, get_travel_guide_detail_api,
    toggle_favorite_guide_api, delete_travel_guide_api, export_travel_guide_api,
    # 抖音相关API
    douyin_analysis_api, get_douyin_analysis_api, generate_product_preview_api, get_douyin_analysis_list_api,
    # 社交订阅相关API
    add_social_subscription_api, get_subscriptions_api, update_subscription_api, get_notifications_api,
    mark_notification_read_api, get_subscription_stats_api,
    # 健身相关API
    fitness_api, follow_fitness_user_api, get_fitness_achievements_api, share_achievement_api,
    # 模式相关API
    record_mode_click_api, get_user_preferred_mode_api,
    # 三重觉醒相关API
    create_fitness_workout_api, create_code_workout_api, complete_daily_task_api,
    get_workout_dashboard_api, get_ai_dependency_api, get_pain_currency_api,
    record_exhaustion_audio_api, create_exhaustion_proof_api, create_copilot_collaboration_api,
    # 生活日记相关API
    emo_diary_api, creative_writer_api, self_analysis_api, storyboard_api,
    # 添加缺失的页面视图函数导入
    tarot_reading_view, tarot_diary_view, meetsomeone_dashboard_view,
    chat_entrance_view, heart_link_test_view, click_test_view, number_match_view, video_chat_view, multi_video_chat_view, multi_video_test_view, chat_room_error_view, active_chat_rooms_view,
    meetsomeone_timeline_view, meetsomeone_graph_view,
    # 功能推荐系统API视图函数
    feature_recommendations_api, feature_list_api, recommendation_stats_api, resolve_url_api,
    # 打卡相关API
    get_checkin_calendar_api,
    # 食物随机选择器相关API
    start_food_randomization_api, pause_food_randomization_api, rate_food_api,
    # 食物随机选择器页面视图函数
    food_randomizer,
    # 食品图像识别相关
    food_image_recognition_view, food_image_recognition_api,
    # 音频转换器相关
    audio_converter_view, audio_converter_api
)

# 导入健身营养定制系统视图
from .fitness_nutrition_views import (
    nutrition_dashboard, nutrition_profile_setup, nutrition_generate_plan,
    nutrition_meal_log, nutrition_weight_tracking, nutrition_reminders,
    nutrition_progress, nutrition_api_generate_plan, nutrition_settings
)

# 导入代理功能视图
from .proxy_view import (
    proxy_dashboard, proxy_status_api, test_website_api, 
    proxy_list_api, test_proxy_api, get_ip_info_api,
    proxy_guide, proxy_connection_test_api, get_ip_comparison_api, test_real_proxy_api
)

from .time_capsule_views import (
    get_nearby_capsules as get_nearby_capsules_api,
)

from .missing_views import (
    # 功能推荐系统页面视图函数
    feature_discovery_view, my_recommendations_view, admin_feature_management_view,
    # 成就相关API
    achievements_api,
    # DeepSeek API
    deepseek_api,
    # Food相关API
    api_foods, api_food_photo_bindings, api_save_food_photo_bindings, api_photos,
    # MeeSomeone相关API
    get_dashboard_stats_api, get_relationship_tags_api, get_person_profiles_api, create_person_profile_api,
    get_interactions_api, create_interaction_api, create_important_moment_api, get_timeline_data_api, get_graph_data_api,
    # Food Image Crawler相关API
    food_image_crawler_api,
    # Food List相关API
    get_food_list_api,
    # Food Image Compare相关API
    compare_food_images_api,
    # Food Image Update相关API
    update_food_image_api,
    # BOSS直聘相关API
    get_boss_login_page_screenshot_api,
    # 求职相关API
    create_job_search_request_api, get_job_search_requests_api,
    # Vanity相关API
    get_vanity_tasks_stats_api, delete_vanity_task_api,
    # 健身相关API
    follow_fitness_user_api, get_fitness_achievements_api, share_achievement_api,
    # PDF转换器相关API
    pdf_converter_api, pdf_converter_status_api, pdf_converter_rating_api,
    # 签到相关API
    checkin_add_api, checkin_delete_api_simple, checkin_delete_api,
    # 塔罗牌相关API
    initialize_tarot_data_api, tarot_spreads_api, tarot_create_reading_api, tarot_readings_api, tarot_daily_energy_api,
    # 食物随机选择器相关API
    food_randomizer_pure_random_api, food_randomizer_statistics_api, food_randomizer_history_api,
)

# 导入监控视图
from .views.monitoring_views import (
    monitoring_dashboard, get_monitoring_data, get_system_metrics,
    get_alerts, get_cache_stats, clear_cache, warm_up_cache,
    MonitoringAPIView
)

from .time_capsule_views import (
    time_capsule_diary_view, save_time_capsule_api, get_time_capsules_api, 
    get_time_capsule_detail_api, unlock_time_capsule_api, get_achievements_api,
    time_capsule_history_view
)

from .guitar_training_views import (
    guitar_training_dashboard, guitar_practice_session, 
    guitar_progress_tracking, guitar_theory_guide, guitar_song_library, 
    start_practice_session_api, complete_practice_session_api, get_practice_stats_api, 
    get_recommended_exercises_api, guitar_tab_generator, upload_audio_for_tab_api, 
    generate_tab_api, get_tab_history_api, download_tab_api, food_photo_binding_view, 
    food_image_correction_view
)

from .fitness_tools_views import (
    fitness_tools_dashboard, bmi_calculator, workout_timer, nutrition_calculator,
    workout_tracker, body_analyzer, workout_planner,
    calculate_bmi_api, calculate_heart_rate_api, calculate_calories_api,
    calculate_protein_api, calculate_water_api, calculate_rm_api, calculate_pace_api,
    save_workout_record_api, get_workout_records_api, calculate_body_composition_api
)

from .pdf_converter_api import pdf_converter_batch, pdf_download_view, pdf_converter_stats_api, pdf_converter_test_api

# 时光胶囊测试页面
def time_capsule_test(request):
    context = {
        'websocket_available': hasattr(settings, 'CHANNEL_LAYERS'),
        'api_timeout': 10000,
        'retry_attempts': 3,
    }
    return render(request, 'tools/time_capsule_test.html', context)

# 简化版时光胶囊视图
def time_capsule_simple(request):
    return render(request, 'tools/time_capsule_simple.html')

# 时光胶囊演示页面
def time_capsule_demo(request):
    return render(request, 'tools/time_capsule_demo.html')

# 时光胶囊日记入口页面
def diary_entrance(request):
    return render(request, 'tools/diary_entrance.html')

# Mode主页面视图函数
@login_required
def work_mode_view(request):
    """极客模式主页面"""
    return render(request, 'tools/work_mode.html')

@login_required
def life_mode_view(request):
    """生活模式主页面"""
    return render(request, 'tools/life_mode.html')

@login_required
def cyberpunk_mode_view(request):
    """赛博朋克模式主页面"""
    return render(request, 'tools/cyberpunk_mode.html')

# URL配置
urlpatterns = [
    # 基础工具页面
    path('', test_case_generator, name='test_case_generator'),
    path('redbook/', redbook_generator, name='redbook_generator'),
    path('pdf_converter/', pdf_converter, name='pdf_converter'),
    path('pdf_converter_test/', pdf_converter_test, name='pdf_converter_test'),
    path('fortune/', fortune_analyzer, name='fortune_analyzer'),
    path('crawler/', web_crawler, name='web_crawler'),
    path('self_analysis/', self_analysis, name='self_analysis'),
    path('storyboard/', storyboard, name='storyboard'),
    
    # 健身相关页面
    path('fitness_center/', fitness_center, name='fitness_center'),
    path('training_plan_editor/', training_plan_editor, name='training_plan_editor'),
    
    # 生活相关页面
    path('emo_diary/', emo_diary, name='emo_diary'),
    path('creative_writer/', creative_writer, name='creative_writer'),
    path('meditation_guide/', meditation_guide, name='meditation_guide'),
    path('peace_meditation/', peace_meditation_view, name='peace_meditation'),
    path('music_healing/', music_healing, name='music_healing'),
    
    # Heart Link相关页面
    path('heart_link/', heart_link, name='heart_link'),
    path('heart_link_chat/', heart_link_chat, name='heart_link_chat'),
    path('chat_enhanced/', chat_enhanced, name='chat_enhanced'),
    path('chat_debug/', chat_debug_view, name='chat_debug'),
    
    # 其他功能页面
    path('douyin_analyzer/', douyin_analyzer, name='douyin_analyzer'),
    path('triple_awakening_dashboard/', triple_awakening_dashboard, name='triple_awakening_dashboard'),
    path('copilot_page/', copilot_page, name='copilot_page'),
    path('desire_dashboard/', desire_dashboard, name='desire_dashboard'),
    path('vanity_os_dashboard/', vanity_os_dashboard, name='vanity_os_dashboard'),
    path('vanity_rewards/', vanity_rewards, name='vanity_rewards'),
    path('sponsor_hall_of_fame/', sponsor_hall_of_fame, name='sponsor_hall_of_fame'),
    path('based_dev_avatar/', based_dev_avatar, name='based_dev_avatar'),
    path('vanity_todo_list/', vanity_todo_list, name='vanity_todo_list'),
    path('travel_guide/', travel_guide, name='travel_guide'),
    path('fitness_community/', fitness_community, name='fitness_community'),
    path('fitness_profile/', fitness_profile, name='fitness_profile'),
    path('fitness_tools/', fitness_tools, name='fitness_tools'),
    
    # 监控系统路由
    path('monitoring/', monitoring_dashboard, name='monitoring_dashboard'),
    path('monitoring/data/', get_monitoring_data, name='get_monitoring_data'),
    path('monitoring/system/', get_system_metrics, name='get_system_metrics'),
    path('monitoring/alerts/', get_alerts, name='get_alerts'),
    path('monitoring/cache/', get_cache_stats, name='get_cache_stats'),
    path('monitoring/clear-cache/', clear_cache, name='clear_cache'),
    path('monitoring/warm-cache/', warm_up_cache, name='warm_up_cache'),
    path('monitoring/api/<str:type>/', MonitoringAPIView.as_view(), name='monitoring_api'),
    path('monitoring/api/<str:action>/', MonitoringAPIView.as_view(), name='monitoring_action'),
    
    # API路由
    path('api/vanity_wealth/', get_vanity_wealth_api, name='get_vanity_wealth_api'),
    path('api/add_sin_points/', add_sin_points_api, name='add_sin_points_api'),
    path('api/music/', music_api, name='music_api'),
    path('api/next_song/', next_song_api, name='next_song_api'),
    path('api/fitness_community_posts/', get_fitness_community_posts_api, name='get_fitness_community_posts_api'),
    path('api/fitness_community_posts/create/', create_fitness_community_post_api, name='create_fitness_community_post_api'),
    path('api/fitness_community_posts/<int:post_id>/like/', like_fitness_post_api, name='like_fitness_post_api'),
    path('api/fitness_community_posts/<int:post_id>/comment/', comment_fitness_post_api, name='comment_fitness_post_api'),
    path('api/fitness_user_profile/', get_fitness_user_profile_api, name='get_fitness_user_profile_api'),
    
    # 求职相关API
    path('api/job_applications/', get_job_applications_api, name='get_job_applications_api'),
    path('api/job_profile/save/', save_job_profile_api, name='save_job_profile_api'),
    path('api/job_profile/', get_job_profile_api, name='get_job_profile_api'),
    path('api/job_search_statistics/', get_job_search_statistics_api, name='get_job_search_statistics_api'),
    path('api/application_status/update/', update_application_status_api, name='update_application_status_api'),
    path('api/application_notes/add/', add_application_notes_api, name='add_application_notes_api'),
    
    # BOSS直聘相关API
    path('api/boss/qr_code/', generate_boss_qr_code_api, name='generate_boss_qr_code_api'),
    path('api/boss/login_page_url/', get_boss_login_page_url_api, name='get_boss_login_page_url_api'),
    path('api/boss/user_token/', get_boss_user_token_api, name='get_boss_user_token_api'),
    path('api/boss/login_status/', check_boss_login_status_selenium_api, name='check_boss_login_status_selenium_api'),
    path('api/boss/logout/', boss_logout_api, name='boss_logout_api'),
    path('api/boss/contact_request/', send_contact_request_api, name='send_contact_request_api'),
    
    # 爬虫相关API
    path('api/crawler/start/', start_crawler_api, name='start_crawler_api'),
    path('api/crawler/status/', get_crawler_status_api, name='get_crawler_status_api'),
    
    # Heart Link相关API
    path('api/heart_link/create/', create_heart_link_request_api, name='create_heart_link_request_api'),
    path('api/heart_link/cancel/', cancel_heart_link_request_api, name='cancel_heart_link_request_api'),
    path('api/heart_link/status/', check_heart_link_status_api, name='check_heart_link_status_api'),
    path('api/heart_link/cleanup/', cleanup_heart_link_api, name='cleanup_heart_link_api'),
    
    # 聊天相关API
    path('api/chat/messages/', get_chat_messages_api, name='get_chat_messages_api'),
    path('api/chat/send_message/', send_message_api, name='send_message_api'),
    path('api/chat/send_image/', send_image_api, name='send_image_api'),
    path('api/chat/send_audio/', send_audio_api, name='send_audio_api'),
    path('api/chat/send_file/', send_file_api, name='send_file_api'),
    path('api/chat/send_video/', send_video_api, name='send_video_api'),
    path('api/chat/delete_message/', delete_message_api, name='delete_message_api'),
    path('api/chat/mark_read/', mark_messages_read_api, name='mark_messages_read_api'),
    path('api/chat/online_status/', update_online_status_api, name='update_online_status_api'),
    path('api/chat/online_users/', get_online_users_api, name='get_online_users_api'),
    path('api/chat/active_rooms/', get_active_chat_rooms_api, name='get_active_chat_rooms_api'),
    
    # 用户资料相关API
    path('api/user_profile/', get_user_profile_api, name='get_user_profile_api'),
    path('api/chat_room_participants/', get_chat_room_participants_api, name='get_chat_room_participants_api'),
    
    # 数字匹配API
    path('api/number_match/', number_match_api, name='number_match_api'),
    path('api/number_match/cancel/', cancel_number_match_api, name='cancel_number_match_api'),
    
    # Desire相关API
    path('api/desire/dashboard/', get_desire_dashboard_api, name='get_desire_dashboard_api'),
    path('api/desire/add/', add_desire_api, name='add_desire_api'),
    path('api/desire/check_fulfillment/', check_desire_fulfillment_api, name='check_desire_fulfillment_api'),
    path('api/desire/generate_image/', generate_ai_image_api, name='generate_ai_image_api'),
    path('api/desire/progress/', get_desire_progress_api, name='get_desire_progress_api'),
    path('api/desire/fulfillment_history/', get_fulfillment_history_api, name='get_fulfillment_history_api'),
    path('api/desire/todos/', get_desire_todos_api, name='get_desire_todos_api'),
    path('api/desire/todos/add/', add_desire_todo_api, name='add_desire_todo_api'),
    path('api/desire/todos/complete/', complete_desire_todo_api, name='complete_desire_todo_api'),
    path('api/desire/todos/delete/', delete_desire_todo_api, name='delete_desire_todo_api'),
    path('api/desire/todos/edit/', edit_desire_todo_api, name='edit_desire_todo_api'),
    path('api/desire/todos/stats/', get_desire_todo_stats_api, name='get_desire_todo_stats_api'),
    
    # Vanity相关API
    path('api/vanity/tasks/', get_vanity_tasks_api, name='get_vanity_tasks_api'),
    path('api/vanity/tasks/add/', add_vanity_task_api, name='add_vanity_task_api'),
    path('api/vanity/tasks/complete/', complete_vanity_task_api, name='complete_vanity_task_api'),
    path('api/vanity/sponsors/', get_sponsors_api, name='get_sponsors_api'),
    path('api/vanity/sponsors/add/', add_sponsor_api, name='add_sponsor_api'),
    
    # Based Dev相关API
    path('api/based_dev/avatar/create/', create_based_dev_avatar_api, name='create_based_dev_avatar_api'),
    path('api/based_dev/avatar/', get_based_dev_avatar_api, name='get_based_dev_avatar_api'),
    path('api/based_dev/stats/update/', update_based_dev_stats_api, name='update_based_dev_stats_api'),
    path('api/based_dev/avatar/like/', like_based_dev_avatar_api, name='like_based_dev_avatar_api'),
    path('api/based_dev/achievements/', get_based_dev_achievements_api, name='get_based_dev_achievements_api'),
    
    # 旅游相关API
    path('api/travel/check_local_data/', check_local_travel_data_api, name='check_local_travel_data_api'),
    path('api/travel/guide/', travel_guide_api, name='travel_guide_api'),
    path('api/travel/guides/', get_travel_guides_api, name='get_travel_guides_api'),
    path('api/travel/guide/<int:guide_id>/', get_travel_guide_detail_api, name='get_travel_guide_detail_api'),
    path('api/travel/guide/<int:guide_id>/favorite/', toggle_favorite_guide_api, name='toggle_favorite_guide_api'),
    path('api/travel/guide/<int:guide_id>/delete/', delete_travel_guide_api, name='delete_travel_guide_api'),
    path('api/travel/guide/<int:guide_id>/export/', export_travel_guide_api, name='export_travel_guide_api'),
    
    # 抖音相关API
    path('api/douyin/analysis/', douyin_analysis_api, name='douyin_analysis_api'),
    path('api/douyin/analysis/<int:analysis_id>/', get_douyin_analysis_api, name='get_douyin_analysis_api'),
    path('api/douyin/product_preview/', generate_product_preview_api, name='generate_product_preview_api'),
    path('api/douyin/analysis_list/', get_douyin_analysis_list_api, name='get_douyin_analysis_list_api'),
    
    # 社交订阅相关API
    path('api/social/subscription/add/', add_social_subscription_api, name='add_social_subscription_api'),
    path('api/social/subscriptions/', get_subscriptions_api, name='get_subscriptions_api'),
    path('api/social/subscription/update/', update_subscription_api, name='update_subscription_api'),
    path('api/social/notifications/', get_notifications_api, name='get_notifications_api'),
    path('api/social/notification/read/', mark_notification_read_api, name='mark_notification_read_api'),
    path('api/social/subscription/stats/', get_subscription_stats_api, name='get_subscription_stats_api'),
    
    # 健身相关API
    path('api/fitness/', fitness_api, name='fitness_api'),
    path('api/fitness/follow/', follow_fitness_user_api, name='follow_fitness_user_api'),
    path('api/fitness/achievements/', get_fitness_achievements_api, name='get_fitness_achievements_api'),
    path('api/fitness/achievement/share/', share_achievement_api, name='share_achievement_api'),
    
    # 模式相关API
    path('api/mode/click/', record_mode_click_api, name='record_mode_click_api'),
    path('api/mode/preferred/', get_user_preferred_mode_api, name='get_user_preferred_mode_api'),
    
    # 三重觉醒相关API
    path('api/triple_awakening/fitness_workout/', create_fitness_workout_api, name='create_fitness_workout_api'),
    path('api/triple_awakening/code_workout/', create_code_workout_api, name='create_code_workout_api'),
    path('api/triple_awakening/daily_task/complete/', complete_daily_task_api, name='complete_daily_task_api'),
    path('api/triple_awakening/workout_dashboard/', get_workout_dashboard_api, name='get_workout_dashboard_api'),
    path('api/triple_awakening/ai_dependency/', get_ai_dependency_api, name='get_ai_dependency_api'),
    path('api/triple_awakening/pain_currency/', get_pain_currency_api, name='get_pain_currency_api'),
    path('api/triple_awakening/exhaustion_audio/', record_exhaustion_audio_api, name='record_exhaustion_audio_api'),
    path('api/triple_awakening/exhaustion_proof/', create_exhaustion_proof_api, name='create_exhaustion_proof_api'),
    path('api/triple_awakening/copilot_collaboration/', create_copilot_collaboration_api, name='create_copilot_collaboration_api'),
    
    # 生活日记相关API
    path('api/emo_diary/', emo_diary_api, name='emo_diary_api'),
    path('api/creative_writer/', creative_writer_api, name='creative_writer_api'),
    path('api/self_analysis/', self_analysis_api, name='self_analysis_api'),
    path('api/storyboard/', storyboard_api, name='storyboard_api'),
    
    # 功能推荐系统API
    path('api/feature_recommendations/', feature_recommendations_api, name='feature_recommendations_api'),
    path('api/feature_list/', feature_list_api, name='feature_list_api'),
    path('api/recommendation_stats/', recommendation_stats_api, name='recommendation_stats_api'),
    path('api/resolve_url/', resolve_url_api, name='resolve_url_api'),
    
    # 打卡相关API
    path('api/checkin/calendar/', get_checkin_calendar_api, name='get_checkin_calendar_api'),
    
    # 食物随机选择器相关API
    path('api/food_randomizer/start/', start_food_randomization_api, name='start_food_randomization_api'),
    path('api/food_randomizer/pause/', pause_food_randomization_api, name='pause_food_randomization_api'),
    path('api/food_randomizer/rate/', rate_food_api, name='rate_food_api'),
    
    # 食品图像识别相关API
    path('api/food_image_recognition/', food_image_recognition_api, name='food_image_recognition_api'),
    
    # 音频转换器相关API
    path('api/audio_converter/', audio_converter_api, name='audio_converter_api'),
    
    # 冥想音频API
    path('api/meditation_audio/', meditation_audio_api, name='meditation_audio_api'),
    
    # 食物随机选择器API
    path('api/food-randomizer/pure-random/', food_randomizer_pure_random_api, name='food_randomizer_pure_random_api'),
    path('api/food-randomizer/statistics/', food_randomizer_statistics_api, name='food_randomizer_statistics_api'),
    path('api/food-randomizer/history/', food_randomizer_history_api, name='food_randomizer_history_api'),
    
    # 食品图像识别API
    path('api/food-image-recognition/', food_image_recognition_api, name='food_image_recognition_api'),
    
    # 音频转换器API
    path('api/audio_converter/', audio_converter_api, name='audio_converter_api'),
    
    # Food相关API路由
    path('api/food-randomizer/start/', start_food_randomization_api, name='start_food_randomization_api'),
    path('api/food-randomizer/pause/', pause_food_randomization_api, name='pause_food_randomization_api'),
    path('api/food-randomizer/rate/', rate_food_api, name='rate_food_api'),
    path('api/foods/', api_foods, name='api_foods'),
    path('api/food-photo-bindings/', api_food_photo_bindings, name='api_food_photo_bindings'),
    path('api/food-photo-bindings/save/', api_save_food_photo_bindings, name='api_save_food_photo_bindings'),
    
    # MeeSomeone相关API路由
    path('api/meetsomeone/dashboard-stats/', get_dashboard_stats_api, name='get_dashboard_stats_api'),
    path('api/meetsomeone/relationship-tags/', get_relationship_tags_api, name='get_relationship_tags_api'),
    path('api/meetsomeone/person-profiles/', get_person_profiles_api, name='get_person_profiles_api'),
    path('api/meetsomeone/person-profiles/create/', create_person_profile_api, name='create_person_profile_api'),
    path('api/meetsomeone/interactions/', get_interactions_api, name='get_interactions_api'),
    path('api/meetsomeone/interactions/create/', create_interaction_api, name='create_interaction_api'),
    path('api/meetsomeone/moments/create/', create_important_moment_api, name='create_important_moment_api'),
    path('api/meetsomeone/timeline/', get_timeline_data_api, name='get_timeline_data_api'),
    path('api/meetsomeone/graph/', get_graph_data_api, name='get_graph_data_api'),
    
    # Food Image Crawler相关API路由
    path('api/food-image-crawler/', food_image_crawler_api, name='food_image_crawler_api'),
    
    # Food List相关API路由
    path('api/food-list/', get_food_list_api, name='get_food_list_api'),
    
    # Food Image Compare相关API路由
    path('api/compare-food-images/', compare_food_images_api, name='compare_food_images_api'),
    
    # Food Image Update相关API路由
    path('api/update-food-image/', update_food_image_api, name='update_food_image_api'),
    
    # Photos相关API路由
    path('api/photos/', api_photos, name='api_photos'),
    
    # 吉他训练系统API路由
    path('api/guitar/start-practice/', start_practice_session_api, name='start_practice_session_api'),
    path('api/guitar/complete-practice/', complete_practice_session_api, name='complete_practice_session_api'),
    path('api/guitar/stats/', get_practice_stats_api, name='get_practice_stats_api'),
    path('api/guitar/recommendations/', get_recommended_exercises_api, name='get_recommended_exercises_api'),
    
    # 自动扒谱系统路由
    path('guitar-tab-generator/', guitar_tab_generator, name='guitar_tab_generator'),
    path('api/guitar/upload-audio/', upload_audio_for_tab_api, name='upload_audio_for_tab_api'),
    path('api/guitar/generate-tab/', generate_tab_api, name='generate_tab_api'),
    path('api/guitar/tab-history/', get_tab_history_api, name='get_tab_history_api'),
    path('api/guitar/download-tab/<str:tab_id>/', download_tab_api, name='download_tab_api'),
    
    # 时光胶囊系统API路由
    path('api/save-capsule/', save_time_capsule_api, name='save_time_capsule_api'),
    path('api/get-capsules/', get_time_capsules_api, name='get_time_capsules_api'),
    path('api/capsule-detail/<int:capsule_id>/', get_time_capsule_detail_api, name='get_time_capsule_detail_api'),
    path('api/unlock-capsule/<int:capsule_id>/', unlock_time_capsule_api, name='unlock_time_capsule_api'),
    path('api/nearby-capsules/', get_nearby_capsules_api, name='get_nearby_capsules_api'),
    path('api/get-achievements/', get_achievements_api, name='get_achievements_api'),
    
    # 代理系统API路由
    path('api/proxy/status/', proxy_status_api, name='proxy_status_api'),
    path('api/proxy/connection-test/', proxy_connection_test_api, name='proxy_connection_test_api'),
    path('api/proxy/test-website/', test_website_api, name='test_website_api'),
    path('api/proxy/list/', proxy_list_api, name='proxy_list_api'),
    path('api/proxy/test/', test_proxy_api, name='test_proxy_api'),
    path('api/proxy/ip-info/', get_ip_info_api, name='get_ip_info_api'),
    path('api/proxy/ip-comparison/', get_ip_comparison_api, name='get_ip_comparison_api'),
    path('api/proxy/test-real/', test_real_proxy_api, name='test_real_proxy_api'),
    
    # 健身营养定制系统路由
    path('nutrition-dashboard/', nutrition_dashboard, name='nutrition_dashboard'),
    path('nutrition-profile-setup/', nutrition_profile_setup, name='nutrition_profile_setup'),
    path('nutrition-generate-plan/', nutrition_generate_plan, name='nutrition_generate_plan'),
    path('nutrition-meal-log/', nutrition_meal_log, name='nutrition_meal_log'),
    path('nutrition-weight-tracking/', nutrition_weight_tracking, name='nutrition_weight_tracking'),
    path('nutrition-reminders/', nutrition_reminders, name='nutrition_reminders'),
    path('nutrition-progress/', nutrition_progress, name='nutrition_progress'),
    path('nutrition-settings/', nutrition_settings, name='nutrition_settings'),
    
    # 健身营养定制系统API路由
    path('api/nutrition/generate-plan/', nutrition_api_generate_plan, name='nutrition_api_generate_plan'),
]
