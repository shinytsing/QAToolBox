# QAToolbox/apps/tools/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .views import (
    test_case_generator, redbook_generator, pdf_converter, 
    fortune_analyzer, web_crawler, self_analysis, storyboard, 
    fitness_center, training_plan_editor, life_diary, life_diary_progressive, 
    emo_diary, creative_writer, meditation_guide, peace_meditation_view, music_healing,
    heart_link, heart_link_chat, chat_enhanced, douyin_analyzer, triple_awakening_dashboard, copilot_page,
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
    delete_message_api, mark_messages_read_api, update_online_status_api, get_online_users_api,
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
    life_diary_api, emo_diary_api, creative_writer_api, self_analysis_api, storyboard_api,
               # 添加缺失的页面视图函数导入
           tarot_reading_view, tarot_diary_view, meetsomeone_dashboard_view,
           chat_entrance_view, heart_link_test_view, click_test_view, number_match_view, video_chat_view,
    meetsomeone_timeline_view, meetsomeone_graph_view,
    # 功能推荐系统API视图函数
    feature_recommendations_api, feature_list_api, recommendation_stats_api, resolve_url_api,
    # 打卡相关API
    get_checkin_calendar_api,
    # 食物随机选择器相关API
    start_food_randomization_api, pause_food_randomization_api, rate_food_api,
    # 食物随机选择器页面视图函数
    food_randomizer
)
from .missing_views import (
    # 功能推荐系统页面视图函数
    feature_discovery_view, my_recommendations_view, admin_feature_management_view,
    # 成就相关API
    achievements_api,
    # DeepSeek API
    deepseek_api,
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
    # Food相关API
    api_foods, api_food_photo_bindings, api_save_food_photo_bindings,
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
    # Photos相关API
    api_photos
)
from .pdf_converter_api import pdf_converter_batch, pdf_download_view, pdf_converter_stats_api  # 添加PDF转换器批量API、下载视图和统计API导入
from django.shortcuts import render

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
    path('fortune_analyzer/', fortune_analyzer, name='fortune_analyzer'),
    path('web_crawler/', web_crawler, name='web_crawler'),
    path('self_analysis/', self_analysis, name='self_analysis'),
    path('storyboard/', storyboard, name='storyboard'),
    path('fitness_center/', fitness_center, name='fitness_center'),
    path('training_plan_editor/', training_plan_editor, name='training_plan_editor'),
    path('life_diary/', life_diary, name='life_diary'),
    path('life_diary_progressive/', life_diary_progressive, name='life_diary_progressive'),
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
    path('chat/', chat_entrance_view, name='chat_entrance'), # 聊天入口页面
    path('number-match/', number_match_view, name='number_match'), # 数字匹配页面
    path('video-chat/<str:room_id>/', video_chat_view, name='video_chat'), # 视频对话页面
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
    path('fitness/', fitness_center, name='fitness'),  # 添加fitness主页面
    path('fitness/community/', fitness_community, name='fitness_community'),
    path('fitness/profile/', fitness_profile, name='fitness_profile'),
    path('fitness/tools/', fitness_tools, name='fitness_tools'),
    
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
    path('api/job_search/applications/', get_job_applications_api, name='get_job_applications_api'),
    path('api/job_search/profile/', get_job_profile_api, name='get_job_profile_api'),
    path('api/job_search/profile/save/', save_job_profile_api, name='save_job_profile_api'),
    path('api/job_search/statistics/', get_job_search_statistics_api, name='get_job_search_statistics_api'),
    path('api/job_search/update_application_status/', update_application_status_api, name='update_application_status_api'),
    path('api/job_search/add_application_notes/', add_application_notes_api, name='add_application_notes_api'),
    
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
    
    # Life Diary相关API路由
    path('api/life_diary/', life_diary_api, name='life_diary_api'),
    
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
]
