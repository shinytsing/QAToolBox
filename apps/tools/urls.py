# QAToolbox/apps/tools/urls.py
from django.urls import path
from .views import (
    test_case_generator, redbook_generator, pdf_converter, 
    fortune_analyzer, web_crawler, self_analysis, storyboard, 
    self_analysis_api, storyboard_api, music_api, next_song_api, 
    fitness_center, life_diary, life_diary_progressive, emo_diary, creative_writer, meditation_guide, music_healing,
    # 社交媒体订阅API
    add_social_subscription_api, get_subscriptions_api, update_subscription_api,
    get_notifications_api, mark_notification_read_api, get_subscription_stats_api,
    # 生活日记API
    life_diary_api,
    # 新增API
    emo_diary_api, creative_writer_api, fitness_api, deepseek_api,
    # 心动链接API
    heart_link, heart_link_chat, create_heart_link_request_api, cancel_heart_link_request_api,
    check_heart_link_status_api, cleanup_heart_link_api, get_chat_messages_api, send_message_api, 
    send_image_api, send_audio_api, send_file_api, delete_message_api, mark_messages_read_api,
    update_online_status_api, get_online_users_api,
    # 抖音分析API
    douyin_analyzer, douyin_analysis_api, get_douyin_analysis_api, generate_product_preview_api, get_douyin_analysis_list_api,
    # 测试API
    test_heart_link_api,
    # 模式偏好API
    record_mode_click_api, get_user_preferred_mode_api,
    # 三重觉醒API
    triple_awakening_dashboard, create_fitness_workout_api, create_code_workout_api,
    complete_daily_task_api, get_workout_dashboard_api, get_ai_dependency_api,
    get_pain_currency_api, record_exhaustion_audio_api, create_exhaustion_proof_api,
    create_copilot_collaboration_api, copilot_page,
    # 欲望仪表盘API
    desire_dashboard, get_desire_dashboard_api, add_desire_api, check_desire_fulfillment_api,
    generate_ai_image_api, get_desire_progress_api, get_fulfillment_history_api,
    # VanityOS API
    vanity_os_dashboard, vanity_rewards, sponsor_hall_of_fame, based_dev_avatar, vanity_todo_list,
    get_vanity_wealth_api, add_sin_points_api, get_sponsors_api, add_sponsor_api,
    get_vanity_tasks_api, add_vanity_task_api, complete_vanity_task_api, create_based_dev_avatar_api,
    # 反程序员形象增强API
    get_based_dev_avatar_api, update_based_dev_stats_api, like_based_dev_avatar_api, get_based_dev_achievements_api,
    # 欲望代办增强API
    get_desire_todos_api, add_desire_todo_api, complete_desire_todo_api, delete_desire_todo_api, 
    edit_desire_todo_api, get_desire_todo_stats_api,
    # 测试页面
    test_desire_todo_enhanced_view, test_desire_todo_public_view,
    # 旅游攻略API
    travel_guide, travel_guide_api, get_travel_guides_api, get_travel_guide_detail_api,
    toggle_favorite_guide_api, delete_travel_guide_api, export_travel_guide_api,
    # 自动求职机API
    job_search_machine, job_search_profile, job_search_dashboard,
    create_job_search_request_api, start_job_search_api, get_job_search_requests_api,
    get_job_applications_api, save_job_profile_api, get_job_profile_api,
    get_job_search_statistics_api, update_application_status_api, add_application_notes_api,
    generate_boss_qr_code_api, check_boss_login_status_api, get_boss_login_status_api,
    boss_logout_api, send_contact_request_api
)
from views import tool_view
from .generate_test_cases_api import GenerateTestCasesAPI
from .generate_redbook_api import GenerateRedBookAPI
from .pdf_converter_api import pdf_converter_api, pdf_converter_status
from django.shortcuts import render

# Mode主页面视图函数
def work_mode_view(request):
    """极客模式主页面"""
    return render(request, 'tools/work_mode.html')

def life_mode_view(request):
    """生活模式主页面"""
    return render(request, 'tools/life_mode.html')

def cyberpunk_mode_view(request):
    """赛博哥特模式主页面"""
    return render(request, 'tools/cyberpunk_mode.html')

def training_mode_view(request):
    """狂暴模式主页面"""
    return render(request, 'tools/training_mode.html')

def emo_mode_view(request):
    """Emo模式主页面"""
    return render(request, 'tools/emo_mode.html')

def anti_programmer_profile_view(request):
    """反程序员档案页面"""
    return render(request, 'tools/anti_programmer_profile.html')

def desire_todo_enhanced_view(request):
    """欲望代办系统页面"""
    return render(request, 'tools/desire_todo_enhanced.html')



urlpatterns = [
    path('', tool_view, name='tools'),
    
    # Mode主页面路由
    path('work/', work_mode_view, name='work_mode'),
    path('life/', life_mode_view, name='life_mode'),
    path('life-mode/', life_mode_view, name='life_mode_alt'),
    path('cyberpunk/', cyberpunk_mode_view, name='cyberpunk_mode'),
    path('training/', training_mode_view, name='training_mode'),
    path('emo/', emo_mode_view, name='emo_mode'),
    
    # 工具页面路由
    path('test-case-generator/', test_case_generator, name='test_case_generator'),
    path('redbook-generator/', redbook_generator, name='redbook_generator'),
    path('pdf-converter/', pdf_converter, name='pdf_converter'),
    path('fortune-analyzer/', fortune_analyzer, name='fortune_analyzer'),
    path('web-crawler/', web_crawler, name='web_crawler'),
    path('self-analysis/', self_analysis, name='self_analysis'),
    path('storyboard/', storyboard, name='storyboard'),
    path('fitness/', fitness_center, name='fitness'),
    path('life-diary/', life_diary_progressive, name='life_diary'),
    path('life-diary-progressive/', life_diary_progressive, name='life_diary_progressive'),
    path('emo-diary/', emo_diary, name='emo_diary'),
    path('creative-writer/', creative_writer, name='creative_writer'),
    path('meditation-guide/', meditation_guide, name='meditation_guide'),
    path('music-healing/', music_healing, name='music_healing'),
    path('douyin-analyzer/', douyin_analyzer, name='douyin_analyzer'),
    
    # 三重觉醒功能路由
    path('triple-awakening/', triple_awakening_dashboard, name='triple_awakening_dashboard'),
    path('copilot/', copilot_page, name='copilot_page'),
    
    # 欲望仪表盘路由
    path('desire-dashboard/', desire_dashboard, name='desire_dashboard'),
    
    # 反程序员档案和欲望代办路由
    path('anti-programmer-profile/', anti_programmer_profile_view, name='anti_programmer_profile'),
    path('desire-todo-enhanced/', desire_todo_enhanced_view, name='desire_todo_enhanced'),
    path('test-desire-todo-enhanced/', test_desire_todo_enhanced_view, name='test_desire_todo_enhanced'),
    path('test-desire-todo-public/', test_desire_todo_public_view, name='test_desire_todo_public'),

    
    # VanityOS 路由
    path('vanity-os/', vanity_os_dashboard, name='vanity_os_dashboard'),
    path('vanity-rewards/', vanity_rewards, name='vanity_rewards'),
    path('sponsor-hall-of-fame/', sponsor_hall_of_fame, name='sponsor_hall_of_fame'),
    path('based-dev-avatar/', based_dev_avatar, name='based_dev_avatar'),
    path('vanity-todo-list/', vanity_todo_list, name='vanity_todo_list'),
    
    # API路由
    path('api/self-analysis/', self_analysis_api, name='self_analysis_api'),
    path('api/storyboard/', storyboard_api, name='storyboard_api'),
    path('api/music/', music_api, name='music_api'),
    path('api/next-song/', next_song_api, name='next_song_api'),
    path('api/generate-testcases/', GenerateTestCasesAPI.as_view(), name='generate_test_cases_api'),
    path('api/generate-redbook/', GenerateRedBookAPI.as_view(), name='generate_redbook_api'),
    
    # PDF转换API路由
    path('api/pdf-converter/', pdf_converter_api, name='pdf_converter_api'),
    path('api/pdf-converter/status/', pdf_converter_status, name='pdf_converter_status'),
    
    # 社交媒体订阅API路由
    path('api/social-subscription/add/', add_social_subscription_api, name='add_social_subscription_api'),
    path('api/social-subscription/list/', get_subscriptions_api, name='get_subscriptions_api'),
    path('api/social-subscription/update/', update_subscription_api, name='update_subscription_api'),
    path('api/social-subscription/notifications/', get_notifications_api, name='get_notifications_api'),
    path('api/social-subscription/mark-read/', mark_notification_read_api, name='mark_notification_read_api'),
    path('api/social-subscription/stats/', get_subscription_stats_api, name='get_subscription_stats_api'),
    
    # 生活日记API路由
    path('api/life-diary/', life_diary_api, name='life_diary_api'),
    
    # DeepSeek API路由
    path('api/deepseek/', deepseek_api, name='deepseek_api'),
    
    # 三重觉醒API路由
    path('api/triple-awakening/fitness-workout/', create_fitness_workout_api, name='create_fitness_workout_api'),
    path('api/triple-awakening/code-workout/', create_code_workout_api, name='create_code_workout_api'),
    path('api/triple-awakening/complete-task/', complete_daily_task_api, name='complete_daily_task_api'),
    path('api/triple-awakening/workout-dashboard/', get_workout_dashboard_api, name='get_workout_dashboard_api'),
    path('api/triple-awakening/ai-dependency/', get_ai_dependency_api, name='get_ai_dependency_api'),
    path('api/triple-awakening/pain-currency/', get_pain_currency_api, name='get_pain_currency_api'),
    path('api/triple-awakening/record-audio/', record_exhaustion_audio_api, name='record_exhaustion_audio_api'),
    path('api/triple-awakening/exhaustion-proof/', create_exhaustion_proof_api, name='create_exhaustion_proof_api'),
    path('api/triple-awakening/copilot-collaboration/', create_copilot_collaboration_api, name='create_copilot_collaboration_api'),
    
    # 欲望仪表盘API路由
    path('api/desire-dashboard/', get_desire_dashboard_api, name='get_desire_dashboard_api'),
    path('api/desire-dashboard/add/', add_desire_api, name='add_desire_api'),
    path('api/desire-dashboard/check-fulfillment/', check_desire_fulfillment_api, name='check_desire_fulfillment_api'),
    path('api/desire-dashboard/generate-image/', generate_ai_image_api, name='generate_ai_image_api'),
    path('api/desire-dashboard/progress/', get_desire_progress_api, name='get_desire_progress_api'),
    path('api/desire-dashboard/history/', get_fulfillment_history_api, name='get_fulfillment_history_api'),
    
    # VanityOS API路由
    path('api/vanity-wealth/', get_vanity_wealth_api, name='get_vanity_wealth_api'),
    path('api/sin-points/add/', add_sin_points_api, name='add_sin_points_api'),
    path('api/sponsors/', get_sponsors_api, name='get_sponsors_api'),
    path('api/sponsors/add/', add_sponsor_api, name='add_sponsor_api'),
    path('api/vanity-tasks/', get_vanity_tasks_api, name='get_vanity_tasks_api'),
    path('api/vanity-tasks/add/', add_vanity_task_api, name='add_vanity_task_api'),
    path('api/vanity-tasks/complete/', complete_vanity_task_api, name='complete_vanity_task_api'),
    path('api/based-dev-avatar/create/', create_based_dev_avatar_api, name='create_based_dev_avatar_api'),
    path('api/based-dev-avatar/get/', get_based_dev_avatar_api, name='get_based_dev_avatar_api'),
    path('api/based-dev-avatar/update-stats/', update_based_dev_stats_api, name='update_based_dev_stats_api'),
    path('api/based-dev-avatar/like/', like_based_dev_avatar_api, name='like_based_dev_avatar_api'),
    path('api/based-dev-avatar/achievements/', get_based_dev_achievements_api, name='get_based_dev_achievements_api'),
    
    # 欲望代办增强API路由
    path('api/desire-todos/', get_desire_todos_api, name='get_desire_todos_api'),
    path('api/desire-todos/add/', add_desire_todo_api, name='add_desire_todo_api'),
    path('api/desire-todos/complete/', complete_desire_todo_api, name='complete_desire_todo_api'),
    path('api/desire-todos/delete/', delete_desire_todo_api, name='delete_desire_todo_api'),
    path('api/desire-todos/edit/', edit_desire_todo_api, name='edit_desire_todo_api'),
    path('api/desire-todos/stats/', get_desire_todo_stats_api, name='get_desire_todo_stats_api'),
    
    # 情感日记API路由
    path('api/emo-diary/', emo_diary_api, name='emo_diary_api'),
    
    # 创意写作API路由
    path('api/creative-writer/', creative_writer_api, name='creative_writer_api'),
    
    # 健身中心API路由
    path('api/fitness/', fitness_api, name='fitness_api'),
    
    # 抖音分析API路由
    path('api/douyin-analysis/', douyin_analysis_api, name='douyin_analysis_api'),
    path('api/douyin-analysis/result/', get_douyin_analysis_api, name='get_douyin_analysis_api'),
    path('api/douyin-analysis/preview/', generate_product_preview_api, name='generate_product_preview_api'),
    path('api/douyin-analysis/list/', get_douyin_analysis_list_api, name='get_douyin_analysis_list_api'),
    
    # 心动链接路由
    path('heart-link/', heart_link, name='heart_link'),
    path('heart-link/chat/<str:room_id>/', heart_link_chat, name='heart_link_chat'),
    
    # 心动链接API路由
    path('api/heart-link/create/', create_heart_link_request_api, name='create_heart_link_request_api'),
    path('api/heart-link/cancel/', cancel_heart_link_request_api, name='cancel_heart_link_request_api'),
    path('api/heart-link/status/', check_heart_link_status_api, name='check_heart_link_status_api'),
    path('api/heart-link/cleanup/', cleanup_heart_link_api, name='cleanup_heart_link_api'),
    path('api/heart-link/test/', test_heart_link_api, name='test_heart_link_api'),
    path('api/chat/<str:room_id>/messages/', get_chat_messages_api, name='get_chat_messages_api'),
    path('api/chat/<str:room_id>/send/', send_message_api, name='send_message_api'),
    path('api/chat/<str:room_id>/send-image/', send_image_api, name='send_image_api'),
    path('api/chat/<str:room_id>/send-audio/', send_audio_api, name='send_audio_api'),
    path('api/chat/<str:room_id>/send-file/', send_file_api, name='send_file_api'),
    path('api/chat/<str:room_id>/delete-message/<int:message_id>/', delete_message_api, name='delete_message_api'),
    path('api/chat/<str:room_id>/mark-read/', mark_messages_read_api, name='mark_messages_read_api'),
    path('api/chat/online-status/', update_online_status_api, name='update_online_status_api'),
    path('api/chat/<str:room_id>/online-users/', get_online_users_api, name='get_online_users_api'),
    
    # 模式偏好API路由
    path('api/mode/record-click/', record_mode_click_api, name='record_mode_click_api'),
    path('api/mode/preferred/', get_user_preferred_mode_api, name='get_user_preferred_mode_api'),
    
    # 旅游攻略路由
    path('travel-guide/', travel_guide, name='travel_guide'),

    # 旅游攻略API路由
    path('api/travel-guide/', travel_guide_api, name='travel_guide_api'),
    path('api/travel-guide/list/', get_travel_guides_api, name='get_travel_guides_api'),
    path('api/travel-guide/<int:guide_id>/', get_travel_guide_detail_api, name='get_travel_guide_detail_api'),
    path('api/travel-guide/<int:guide_id>/toggle-favorite/', toggle_favorite_guide_api, name='toggle_favorite_guide_api'),
    path('api/travel-guide/<int:guide_id>/delete/', delete_travel_guide_api, name='delete_travel_guide_api'),
    path('api/travel-guide/<int:guide_id>/export/', export_travel_guide_api, name='export_travel_guide_api'),
    
    # 自动求职机路由
    path('job-search-machine/', job_search_machine, name='job_search_machine'),
    path('job-search-profile/', job_search_profile, name='job_search_profile'),
    path('job-search-dashboard/', job_search_dashboard, name='job_search_dashboard'),
    
    # 自动求职机API路由
    path('api/job-search/create-request/', create_job_search_request_api, name='create_job_search_request_api'),
    path('api/job-search/start/', start_job_search_api, name='start_job_search_api'),
    path('api/job-search/requests/', get_job_search_requests_api, name='get_job_search_requests_api'),
    path('api/job-search/applications/', get_job_applications_api, name='get_job_applications_api'),
    path('api/job-search/profile/save/', save_job_profile_api, name='save_job_profile_api'),
    path('api/job-search/profile/', get_job_profile_api, name='get_job_profile_api'),
    path('api/job-search/statistics/', get_job_search_statistics_api, name='get_job_search_statistics_api'),
    path('api/job-search/application/update-status/', update_application_status_api, name='update_application_status_api'),
    path('api/job-search/application/add-notes/', add_application_notes_api, name='add_application_notes_api'),
    
    # Boss直聘API路由
    path('api/boss/qr-code/', generate_boss_qr_code_api, name='generate_boss_qr_code_api'),
    path('api/boss/check-login/', check_boss_login_status_api, name='check_boss_login_status_api'),
    path('api/boss/login-status/', get_boss_login_status_api, name='get_boss_login_status_api'),
    path('api/boss/logout/', boss_logout_api, name='boss_logout_api'),
    path('api/boss/send-contact/', send_contact_request_api, name='send_contact_request_api'),
]