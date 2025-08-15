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
    # get_job_profile_api,
    # get_job_search_statistics_api, update_application_status_api, add_application_notes_api,
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
    fitness_api, follow_fitness_user_api, get_fitness_achievements_api, share_achievement_api, add_weight_record_api,
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
    audio_converter_view, audio_converter_api,
    user_generated_travel_guide_api, user_generated_travel_guide_detail_api,
    user_generated_travel_guide_download_api, user_generated_travel_guide_use_api,
    user_generated_travel_guide_upload_attachment_api,
    # 船宝（二手线下交易）相关视图
    shipbao_home, shipbao_publish, shipbao_detail, shipbao_transactions, shipbao_chat,
    shipbao_create_item_api, shipbao_items_api, shipbao_initiate_transaction_api,
    shipbao_send_message_api, shipbao_messages_api,
    # 搭子（同城活动匹配）相关视图
    buddy_home, buddy_create, buddy_detail, buddy_manage, buddy_chat,
    buddy_create_event_api, buddy_events_api, buddy_join_event_api,
    buddy_approve_member_api, buddy_send_message_api, buddy_messages_api
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

# 导入监控视图
from .monitoring_views import (
    monitoring_dashboard, get_monitoring_data, get_system_metrics,
    get_alerts, get_cache_stats, clear_cache, warm_up_cache,
    MonitoringAPIView
)

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

@login_required
def training_mode_view(request):
    """训练模式主页面"""
    return render(request, 'tools/training_mode.html')

@login_required
def guitar_training_view(request):
    """吉他训练页面"""
    return render(request, 'tools/guitar_training.html')

@login_required
def emo_mode_view(request):
    """情感模式主页面"""
    return render(request, 'tools/emo_mode.html')

def anti_programmer_profile_view(request):
    """反程序员形象页面"""
    return render(request, 'tools/anti_programmer_profile.html')

def desire_todo_enhanced_view(request):
    """欲望代办增强页面"""
    return render(request, 'tools/desire_todo_enhanced.html')

# Tools主页面视图函数
@login_required
def tools_index_view(request):
    """工具主页面"""
    return render(request, 'tools/index.html')

# 应用名称（命名空间）
app_name = 'tools'

# URL配置
urlpatterns = [
    # Tools主页面路由
    path('', tools_index_view, name='tools_index'),
    
    # 模式主页面路由
    path('work/', work_mode_view, name='work'),  # 添加work路径以修复齿轮图标404错误
    path('work_mode/', work_mode_view, name='work_mode'),
    path('life/', life_mode_view, name='life'),  # 添加life路径以修复齿轮图标404错误
    path('life_mode/', life_mode_view, name='life_mode'),
    path('training/', training_mode_view, name='training'),  # 添加training路径以修复齿轮图标404错误
    path('training_mode/', training_mode_view, name='training_mode'),
    path('cyberpunk/', cyberpunk_mode_view, name='cyberpunk'),  # 添加cyberpunk路径以修复齿轮图标404错误
    path('cyberpunk_mode/', cyberpunk_mode_view, name='cyberpunk_mode'),
    path('emo/', emo_mode_view, name='emo'),  # 添加emo路径以修复齿轮图标404错误
    path('emo_mode/', emo_mode_view, name='emo_mode'),
    path('guitar_training/', guitar_training_view, name='guitar_training'),
    path('anti_programmer_profile/', anti_programmer_profile_view, name='anti_programmer_profile'),
    path('desire_todo_enhanced/', desire_todo_enhanced_view, name='desire_todo_enhanced'),
    
    # 基础工具页面路由
    path('test_case_generator/', test_case_generator, name='test_case_generator'),
    path('redbook_generator/', redbook_generator, name='redbook_generator'),
    path('pdf_converter/', pdf_converter, name='pdf_converter'),
    path('pdf_converter_test/', pdf_converter_test, name='pdf_converter_test'),
    path('fortune_analyzer/', fortune_analyzer, name='fortune_analyzer'),
    path('web_crawler/', web_crawler, name='web_crawler'),
    path('self_analysis/', self_analysis, name='self_analysis'),
    path('storyboard/', storyboard, name='storyboard'),
    path('fitness_center/', fitness_center, name='fitness_center'),
    path('training_plan_editor/', training_plan_editor, name='training_plan_editor'),

    path('diary/', diary_entrance, name='diary'),  # 新的主要日记入口
    path('diary/record/', time_capsule_diary_view, name='diary_record'),  # 记录页面
    path('time_capsule_simple/', time_capsule_simple, name='time_capsule_simple'),
    path('time_capsule_demo/', time_capsule_demo, name='time_capsule_demo'),
    path('time_capsule_test/', time_capsule_test, name='time_capsule_test'),
    path('emo_diary/', emo_diary, name='emo_diary'),
    path('creative_writer/', creative_writer, name='creative_writer'),
    path('meditation_guide/', meditation_guide, name='meditation_guide'),
    path('peace_meditation/', peace_meditation_view, name='peace_meditation'),
    path('music_healing/', music_healing, name='music_healing'),
    path('heart_link/', heart_link, name='heart_link'),
    path('heart_link/test/', heart_link_test_view, name='heart_link_test'), # 测试页面（无需登录）
    path('click-test/', click_test_view, name='click_test'), # 点击测试页面（无需登录）
    path('heart_link/chat/<str:room_id>/', heart_link_chat, name='heart_link_chat'),
    path('chat/enhanced/<str:room_id>/', chat_enhanced, name='chat_enhanced'),
    path('chat/debug/<str:room_id>/', chat_debug_view, name='chat_debug'), # 聊天调试页面
    path('chat/', chat_entrance_view, name='chat_entrance'), # 聊天入口页面
    path('chat/active_rooms/', active_chat_rooms_view, name='active_chat_rooms'), # 活跃聊天室页面
    path('number-match/', number_match_view, name='number_match'), # 数字匹配页面
    path('video-chat/<str:room_id>/', video_chat_view, name='video_chat'),
    path('multi-video-chat/<str:room_id>/', multi_video_chat_view, name='multi_video_chat'), # 多人视频聊天页面
    path('multi-video-test/', multi_video_test_view, name='multi_video_test'), # 多人视频测试页面
    path('chat-room-error/<str:error_type>/<str:room_id>/', chat_room_error_view, name='chat_room_error'), # 聊天室错误页面
    path('douyin_analyzer/', douyin_analyzer, name='douyin_analyzer'),
    path('triple_awakening/', triple_awakening_dashboard, name='triple_awakening_dashboard'),
    path('copilot/', copilot_page, name='copilot_page'),
    path('desire_dashboard/', desire_dashboard, name='desire_dashboard'),
    path('vanity_os/', vanity_os_dashboard, name='vanity_os_dashboard'),
    path('vanity_rewards/', vanity_rewards, name='vanity_rewards'),
    path('sponsor_hall_of_fame/', sponsor_hall_of_fame, name='sponsor_hall_of_fame'),
    path('based_dev_avatar/', based_dev_avatar, name='based_dev_avatar'),
    path('vanity_todo_list/', vanity_todo_list, name='vanity_todo_list'),
    path('travel_guide/', travel_guide, name='travel_guide'),
    path('food_randomizer/', food_randomizer, name='food_randomizer'),
    path('food_image_recognition/', food_image_recognition_view, name='food_image_recognition'),
    path('food_photo_binding/', food_photo_binding_view, name='food_photo_binding'),
    
    # 音频转换器
    path('audio_converter/', audio_converter_view, name='audio_converter'),
    path('food_image_correction/', food_image_correction_view, name='food_image_correction'),
    path('fitness/', fitness_center, name='fitness'),  # 添加fitness主页面
    path('fitness/community/', fitness_community, name='fitness_community'),
    path('fitness/profile/', fitness_profile, name='fitness_profile'),
    path('fitness/add_weight_record/', add_weight_record_api, name='add_weight_record_api'),
    path('fitness/tools/', fitness_tools, name='fitness_tools'),
    path('fitness/plan-editor/', training_plan_editor, name='training_plan_editor'),

    
    # 健身工具详细页面
    path('fitness/tools/dashboard/', fitness_tools_dashboard, name='fitness_tools_dashboard'),
    path('fitness/tools/bmi-calculator/', bmi_calculator, name='bmi_calculator'),
    path('fitness/tools/workout-timer/', workout_timer, name='workout_timer'),
    path('fitness/tools/nutrition-calculator/', nutrition_calculator, name='nutrition_calculator'),
    path('fitness/tools/workout-tracker/', workout_tracker, name='workout_tracker'),
    path('fitness/tools/body-analyzer/', body_analyzer, name='body_analyzer'),
    path('fitness/tools/workout-planner/', workout_planner, name='workout_planner'),
    
    # 中优先级：添加缺失的页面路由
    path('tarot/reading/', tarot_reading_view, name='tarot_reading'),
    path('tarot/diary/', tarot_diary_view, name='tarot_diary'),
    path('meetsomeone/', meetsomeone_dashboard_view, name='meetsomeone_dashboard'),
    path('meetsomeone/timeline/', meetsomeone_timeline_view, name='meetsomeone_timeline'),
    path('meetsomeone/graph/', meetsomeone_graph_view, name='meetsomeone_graph'),
    
    # 功能推荐系统页面路由
    path('feature_discovery/', feature_discovery_view, name='feature_discovery_page'),
    path('my_recommendations/', my_recommendations_view, name='my_recommendations_page'),
    path('admin/feature_management/', admin_feature_management_view, name='admin_feature_management'),
    
    # 吉他训练系统路由
    path('guitar-training/', guitar_training_dashboard, name='guitar_training_dashboard'),
    path('guitar-practice/<str:practice_type>/<str:difficulty>/', guitar_practice_session, name='guitar_practice_session'),
    path('guitar-progress/', guitar_progress_tracking, name='guitar_progress_tracking'),
    path('guitar-theory/', guitar_theory_guide, name='guitar_theory_guide'),
    path('guitar-songs/', guitar_song_library, name='guitar_song_library'),
    
    # 时光胶囊系统路由
    path('time-capsule-diary/', time_capsule_diary_view, name='time_capsule_diary'),
    path('time-capsule-history/', time_capsule_history_view, name='time_capsule_history'),
    
    # 代理系统路由
    path('proxy-dashboard/', proxy_dashboard, name='proxy_dashboard'),
    path('proxy-guide/', proxy_guide, name='proxy_guide'),
    
    # API路由
    path('api/vanity_wealth/', get_vanity_wealth_api, name='get_vanity_wealth_api'),
    path('api/add_sin_points/', add_sin_points_api, name='add_sin_points_api'),
    path('api/sin_points/add/', add_sin_points_api, name='add_sin_points_api_alt'),  # 添加备用路径
    path('api/music/', music_api, name='music_api'),
    path('api/next_song/', next_song_api, name='next_song_api'),  # 修复：使用实际函数
    path('api/feature_recommendations/', feature_recommendations_api, name='feature_recommendations_api'),
    path('api/feature_recommendation/', feature_recommendations_api, name='feature_recommendation_api'),
    path('api/resolve_url/', resolve_url_api, name='resolve_url_api'),
    path('api/feature_list/', feature_list_api, name='feature_list_api'),
    path('api/recommendation_stats/', recommendation_stats_api, name='recommendation_stats_api'),
    path('api/achievements/', achievements_api, name='achievements_api'),
    path('api/deepseek/', deepseek_api, name='deepseek_api'),
    
    # 旅游攻略API
    path('api/travel_guide/', travel_guide_api, name='travel_guide_api'),
    path('travel_guide_api/', travel_guide_api, name='travel_guide_api_alt'),  # 添加备用路径
    path('api/travel_guide/list/', get_travel_guides_api, name='travel_guide_list_api'),
    path('api/travel_guide/check-local-data/', check_local_travel_data_api, name='travel_guide_check_local_api'),
    path('api/travel_guide/<int:guide_id>/', get_travel_guide_detail_api, name='travel_guide_detail_api'),
    path('api/travel_guide/<int:guide_id>/toggle_favorite/', toggle_favorite_guide_api, name='travel_guide_toggle_favorite_api'),
    path('api/travel_guide/<int:guide_id>/export/', export_travel_guide_api, name='travel_guide_export_api'),
    
    # 高优先级：添加缺失的API路由
    # 健身社区相关API
    path('api/fitness_community/posts/', get_fitness_community_posts_api, name='get_fitness_community_posts_api'),
    path('api/fitness_community/create_post/', create_fitness_community_post_api, name='create_fitness_community_post_api'),
    path('api/fitness_community/like_post/', like_fitness_post_api, name='like_fitness_post_api'),
    path('api/fitness_community/comment_post/', comment_fitness_post_api, name='comment_fitness_post_api'),
    path('api/fitness/user_profile/', get_fitness_user_profile_api, name='get_fitness_user_profile_api'),
    
    # BOSS直聘相关API
    path('api/boss/qr_screenshot/', generate_boss_qr_code_api, name='generate_boss_qr_code_api'),
    path('api/boss/login_page_url/', get_boss_login_page_url_api, name='get_boss_login_page_url_api'),
    path('api/boss/login_page_screenshot/', get_boss_login_page_screenshot_api, name='get_boss_login_page_screenshot_api'),
    path('api/boss/user_token/', get_boss_user_token_api, name='get_boss_user_token_api'),
    path('api/boss/check_login_selenium/', check_boss_login_status_selenium_api, name='check_boss_login_status_selenium_api'),
    path('api/boss/logout/', boss_logout_api, name='boss_logout_api'),
    path('api/boss/send_contact_request/', send_contact_request_api, name='send_contact_request_api'),
    path('api/boss/start_crawler/', start_crawler_api, name='start_crawler_api'),
    path('api/boss/crawler_status/', get_crawler_status_api, name='get_crawler_status_api'),
    
    # 求职相关API
    path('api/job_search/create_request/', create_job_search_request_api, name='create_job_search_request_api'),
    path('api/job_search/requests/', get_job_search_requests_api, name='get_job_search_requests_api'),
    # path('api/job_search/applications/', get_job_applications_api, name='get_job_applications_api'),
    # path('api/job_search/profile/', get_job_profile_api, name='get_job_profile_api'),
    # path('api/job_search/profile/save/', save_job_profile_api, name='save_job_profile_api'),
    # path('api/job_search/statistics/', get_job_search_statistics_api, name='get_job_search_statistics_api'),
    # path('api/job_search/update_application_status/', update_application_status_api, name='update_application_status_api'),
    # path('api/job_search/add_application_notes/', add_application_notes_api, name='add_application_notes_api'),
    
    # Heart Link相关API路由
    path('api/heart_link/create/', create_heart_link_request_api, name='create_heart_link_request_api'),
    path('api/heart_link/cancel/', cancel_heart_link_request_api, name='cancel_heart_link_request_api'),
    path('api/heart_link/status/', check_heart_link_status_api, name='check_heart_link_status_api'),
    path('api/heart_link/cleanup/', cleanup_heart_link_api, name='cleanup_heart_link_api'),

    # 聊天相关API路由
    path('api/chat/<str:room_id>/messages/', get_chat_messages_api, name='get_chat_messages_api'),
    path('api/chat/<str:room_id>/send/', send_message_api, name='send_message_api'),
    path('api/chat/<str:room_id>/send-image/', send_image_api, name='send_image_api'),
    path('api/chat/<str:room_id>/send-audio/', send_audio_api, name='send_audio_api'),
    path('api/chat/<str:room_id>/send-file/', send_file_api, name='send_file_api'),
    path('api/chat/<str:room_id>/send-video/', send_video_api, name='send_video_api'),
    path('api/chat/<str:room_id>/delete-message/<int:message_id>/', delete_message_api, name='delete_message_api'),
    path('api/chat/<str:room_id>/mark_read/', mark_messages_read_api, name='mark_messages_read_api'),
    path('api/chat/online_status/', update_online_status_api, name='update_online_status_api'),
    path('api/chat/<str:room_id>/online_users/', get_online_users_api, name='get_online_users_api'),
    path('api/chat/<str:room_id>/participants/', get_chat_room_participants_api, name='get_chat_room_participants_api'),
    path('api/chat/active_rooms/', get_active_chat_rooms_api, name='get_active_chat_rooms_api'),
    
    # 用户资料相关API路由
    path('api/user/<int:user_id>/profile/', get_user_profile_api, name='get_user_profile_api'),
    
    # Desire相关API路由
    path('api/desire_dashboard/', get_desire_dashboard_api, name='get_desire_dashboard_api'),
    path('api/desire_dashboard/add/', add_desire_api, name='add_desire_api'),
    path('api/desire_dashboard/check_fulfillment/', check_desire_fulfillment_api, name='check_desire_fulfillment_api'),
    path('api/desire_dashboard/generate_image/', generate_ai_image_api, name='generate_ai_image_api'),
    path('api/desire_dashboard/progress/', get_desire_progress_api, name='get_desire_progress_api'),
    path('api/desire_dashboard/history/', get_fulfillment_history_api, name='get_fulfillment_history_api'),
    path('api/desire_todos/', get_desire_todos_api, name='get_desire_todos_api'),
    path('api/desire_todos/add/', add_desire_todo_api, name='add_desire_todo_api'),
    path('api/desire_todos/complete/', complete_desire_todo_api, name='complete_desire_todo_api'),
    path('api/desire_todos/delete/', delete_desire_todo_api, name='delete_desire_todo_api'),
    path('api/desire_todos/edit/', edit_desire_todo_api, name='edit_desire_todo_api'),
    path('api/desire_todos/stats/', get_desire_todo_stats_api, name='get_desire_todo_stats_api'),
    
    # Vanity相关API路由
    path('api/vanity_tasks/', get_vanity_tasks_api, name='get_vanity_tasks_api'),
    path('api/vanity_tasks/add/', add_vanity_task_api, name='add_vanity_task_api'),
    path('api/vanity_tasks/complete/', complete_vanity_task_api, name='complete_vanity_task_api'),
    path('api/vanity_tasks/stats/', get_vanity_tasks_stats_api, name='get_vanity_tasks_stats_api'),
    path('api/vanity_tasks/delete/', delete_vanity_task_api, name='delete_vanity_task_api'),
    path('api/sponsors/', get_sponsors_api, name='get_sponsors_api'),
    path('api/sponsors/add/', add_sponsor_api, name='add_sponsor_api'),
    
    # Based Dev相关API路由
    path('api/based_dev_avatar/create/', create_based_dev_avatar_api, name='create_based_dev_avatar_api'),
    path('api/based_dev_avatar/get/', get_based_dev_avatar_api, name='get_based_dev_avatar_api'),
    path('api/based_dev_avatar/update_stats/', update_based_dev_stats_api, name='update_based_dev_stats_api'),
    path('api/based_dev_avatar/like/', like_based_dev_avatar_api, name='like_based_dev_avatar_api'),
    path('api/based_dev_avatar/achievements/', get_based_dev_achievements_api, name='get_based_dev_achievements_api'),
    
    # Douyin相关API路由
    path('api/douyin_analysis/', douyin_analysis_api, name='douyin_analysis_api'),
    path('api/douyin_analysis/result/', get_douyin_analysis_api, name='get_douyin_analysis_api'),
    path('api/douyin_analysis/preview/', generate_product_preview_api, name='generate_product_preview_api'),
    path('api/douyin_analysis/list/', get_douyin_analysis_list_api, name='get_douyin_analysis_list_api'),
    
    # Social Subscription相关API路由
    path('api/social_subscription/add/', add_social_subscription_api, name='add_social_subscription_api'),
    path('api/social_subscription/list/', get_subscriptions_api, name='get_subscriptions_api'),
    path('api/social_subscription/update/', update_subscription_api, name='update_subscription_api'),
    path('api/social_subscription/notifications/', get_notifications_api, name='get_notifications_api'),
    path('api/social_subscription/mark_read/', mark_notification_read_api, name='mark_notification_read_api'),
    path('api/social_subscription/stats/', get_subscription_stats_api, name='get_subscription_stats_api'),
    
    # Fitness相关API路由
    path('api/fitness/', fitness_api, name='fitness_api'),
    path('api/fitness_community/follow/', follow_fitness_user_api, name='follow_fitness_user_api'),
    path('api/fitness_community/achievements/', get_fitness_achievements_api, name='get_fitness_achievements_api'),
    path('api/fitness_community/share_achievement/', share_achievement_api, name='share_achievement_api'),
    path('api/fitness_community/profile/', get_fitness_user_profile_api, name='get_fitness_user_profile_api'),
    
    # 健身工具API路由
    path('api/fitness/bmi/', calculate_bmi_api, name='calculate_bmi_api'),
    path('api/fitness/heart-rate/', calculate_heart_rate_api, name='calculate_heart_rate_api'),
    path('api/fitness/calories/', calculate_calories_api, name='calculate_calories_api'),
    path('api/fitness/protein/', calculate_protein_api, name='calculate_protein_api'),
    path('api/fitness/water/', calculate_water_api, name='calculate_water_api'),
    path('api/fitness/rm/', calculate_rm_api, name='calculate_rm_api'),
    path('api/fitness/pace/', calculate_pace_api, name='calculate_pace_api'),
    path('api/fitness/body-composition/', calculate_body_composition_api, name='calculate_body_composition_api'),
    path('api/fitness/workout/save/', save_workout_record_api, name='save_workout_record_api'),
    path('api/fitness/workout/records/', get_workout_records_api, name='get_workout_records_api'),
    
    # Mode相关API路由
    path('api/mode/record_click/', record_mode_click_api, name='record_mode_click_api'),
    path('api/mode/preferred/', get_user_preferred_mode_api, name='get_user_preferred_mode_api'),
    
    # Triple Awakening相关API路由
    path('api/triple_awakening/fitness_workout/', create_fitness_workout_api, name='create_fitness_workout_api'),
    path('api/triple_awakening/code_workout/', create_code_workout_api, name='create_code_workout_api'),
    path('api/triple_awakening/complete_task/', complete_daily_task_api, name='complete_daily_task_api'),
    path('api/triple_awakening/workout_dashboard/', get_workout_dashboard_api, name='get_workout_dashboard_api'),
    path('api/triple_awakening/ai_dependency/', get_ai_dependency_api, name='get_ai_dependency_api'),
    path('api/triple_awakening/pain_currency/', get_pain_currency_api, name='get_pain_currency_api'),
    path('api/triple_awakening/record_audio/', record_exhaustion_audio_api, name='record_exhaustion_audio_api'),
    path('api/triple_awakening/exhaustion_proof/', create_exhaustion_proof_api, name='create_exhaustion_proof_api'),
    path('api/triple_awakening/copilot_collaboration/', create_copilot_collaboration_api, name='create_copilot_collaboration_api'),
    
    # Emo Diary相关API路由
    path('api/emo_diary/', emo_diary_api, name='emo_diary_api'),
    
    # Creative Writer相关API路由
    path('api/creative_writer/', creative_writer_api, name='creative_writer_api'),
    
    # Storyboard相关API路由
    path('api/storyboard/', storyboard_api, name='storyboard_api'),
    
    # Self Analysis相关API路由
    path('api/self-analysis/', self_analysis_api, name='self_analysis_api'),
    
    # PDF Converter相关API路由
    path('api/pdf-converter/', pdf_converter_api, name='pdf_converter_api'),
    path('api/pdf-converter-test/', pdf_converter_test_api, name='pdf_converter_test_api'),
    path('api/pdf-converter/status/', pdf_converter_status_api, name='pdf_converter_status'),
    path('api/pdf-converter/stats/', pdf_converter_stats_api, name='pdf_converter_stats_api'),
    path('api/pdf-converter/rating/', pdf_converter_rating_api, name='pdf_converter_rating_api'),
    path('api/pdf-converter/batch/', pdf_converter_batch, name='pdf_converter_batch'),
    path('api/pdf-converter/download/<str:filename>/', pdf_download_view, name='pdf_download_view'),
    
    # 签到相关API
    path('api/checkin/calendar/', get_checkin_calendar_api, name='checkin_calendar_api'),
    
    # 数字匹配API
    path('api/number-match/', number_match_api, name='number_match_api'),
    path('api/number-match/cancel/', cancel_number_match_api, name='cancel_number_match_api'),
    path('api/checkin/add/', checkin_add_api, name='checkin_add_api'),
    path('api/checkin/delete/', checkin_delete_api_simple, name='checkin_delete_api_simple'),  # 添加不带参数的版本
    path('api/checkin/delete/<int:checkin_id>/', checkin_delete_api, name='checkin_delete_api'),
    
    # 塔罗牌相关API
    path('api/tarot/initialize-data/', initialize_tarot_data_api, name='initialize_tarot_data_api'),
    path('api/tarot/spreads/', tarot_spreads_api, name='tarot_spreads_api'),
    path('api/tarot/create-reading/', tarot_create_reading_api, name='tarot_create_reading_api'),
    path('api/tarot/readings/', tarot_readings_api, name='tarot_readings_api'),
    path('api/tarot/daily-energy/', tarot_daily_energy_api, name='tarot_daily_energy_api'),
    
    # 冥想音频API
    path('api/meditation-audio/', meditation_audio_api, name='meditation_audio_api'),
    
    # 食物随机选择器API
    path('api/food-randomizer/pure-random/', food_randomizer_pure_random_api, name='food_randomizer_pure_random_api'),
    path('api/food-randomizer/statistics/', food_randomizer_statistics_api, name='food_randomizer_statistics_api'),
    path('api/food-randomizer/history/', food_randomizer_history_api, name='food_randomizer_history_api'),
    
    # 食品图像识别API
    path('api/food-image-recognition/', food_image_recognition_api, name='food_image_recognition_api'),
    
    # 音频转换器API
    path('api/audio_converter/', audio_converter_api, name='audio_converter_api'),
    
    # 好心人攻略API
    path('api/user_generated_travel_guide/', user_generated_travel_guide_api, name='user_generated_travel_guide_api'),
    path('api/user_generated_travel_guide/<int:guide_id>/', user_generated_travel_guide_detail_api, name='user_generated_travel_guide_detail_api'),
    path('api/user_generated_travel_guide/<int:guide_id>/download/', user_generated_travel_guide_download_api, name='user_generated_travel_guide_download_api'),
    path('api/user_generated_travel_guide/<int:guide_id>/use/', user_generated_travel_guide_use_api, name='user_generated_travel_guide_use_api'),
    path('api/user_generated_travel_guide/<int:guide_id>/upload_attachment/', user_generated_travel_guide_upload_attachment_api, name='user_generated_travel_guide_upload_attachment_api'),
    
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
    
    # ==================== 船宝（二手线下交易）相关路由 ====================
    path('shipbao/', shipbao_home, name='shipbao_home'),
    path('shipbao/publish/', shipbao_publish, name='shipbao_publish'),
    path('shipbao/item/<int:item_id>/', shipbao_detail, name='shipbao_detail'),
    path('shipbao/transactions/', shipbao_transactions, name='shipbao_transactions'),
    path('shipbao/chat/<int:transaction_id>/', shipbao_chat, name='shipbao_chat'),
    
    # 船宝API路由
    path('api/shipbao/create-item/', shipbao_create_item_api, name='shipbao_create_item_api'),
    path('api/shipbao/items/', shipbao_items_api, name='shipbao_items_api'),
    path('api/shipbao/initiate-transaction/', shipbao_initiate_transaction_api, name='shipbao_initiate_transaction_api'),
    path('api/shipbao/send-message/', shipbao_send_message_api, name='shipbao_send_message_api'),
    path('api/shipbao/messages/', shipbao_messages_api, name='shipbao_messages_api'),
    
    # ==================== 搭子（同城活动匹配）相关路由 ====================
    path('buddy/', buddy_home, name='buddy_home'),
    path('buddy/create/', buddy_create, name='buddy_create'),
    path('buddy/event/<int:event_id>/', buddy_detail, name='buddy_detail'),
    path('buddy/manage/', buddy_manage, name='buddy_manage'),
    path('buddy/chat/<int:event_id>/', buddy_chat, name='buddy_chat'),
    
    # 搭子API路由
    path('api/buddy/create-event/', buddy_create_event_api, name='buddy_create_event_api'),
    path('api/buddy/events/', buddy_events_api, name='buddy_events_api'),
    path('api/buddy/join-event/', buddy_join_event_api, name='buddy_join_event_api'),
    path('api/buddy/approve-member/', buddy_approve_member_api, name='buddy_approve_member_api'),
    path('api/buddy/send-message/', buddy_send_message_api, name='buddy_send_message_api'),
    path('api/buddy/messages/', buddy_messages_api, name='buddy_messages_api'),
]