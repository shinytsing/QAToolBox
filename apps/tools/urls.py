# QAToolbox/apps/tools/urls.py
from django.urls import path
from .views import (
    test_case_generator, redbook_generator, pdf_converter, 
    fortune_analyzer, web_crawler, self_analysis, storyboard, 
    self_analysis_api, storyboard_api, music_api, next_song_api, 
    fitness_center, life_diary, emo_diary, creative_writer,
    # 社交媒体订阅API
    add_social_subscription_api, get_subscriptions_api, update_subscription_api,
    get_notifications_api, mark_notification_read_api, get_subscription_stats_api
)
from views import tool_view
from .generate_test_cases_api import GenerateTestCasesAPI
from .generate_redbook_api import GenerateRedBookAPI
from .pdf_converter_api import pdf_converter_api, pdf_converter_status

urlpatterns = [
    path('', tool_view, name='tools'),
    path('test-case-generator/', test_case_generator, name='test_case_generator'),
    path('redbook-generator/', redbook_generator, name='redbook_generator'),
    path('pdf_converter_modern/', pdf_converter, name='pdf_converter'),
    path('fortune-analyzer/', fortune_analyzer, name='fortune_analyzer'),
    path('web-crawler/', web_crawler, name='web_crawler'),
    path('self-analysis/', self_analysis, name='self_analysis'),
    path('storyboard/', storyboard, name='storyboard'),
    path('fitness/', fitness_center, name='fitness'),
    path('life-diary/', life_diary, name='life_diary'),
    path('emo-diary/', emo_diary, name='emo_diary'),
    path('creative-writer/', creative_writer, name='creative_writer'),
    
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
]