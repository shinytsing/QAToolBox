# views package

# 从分模块的视图文件导入
from .basic_tools_views import *
from .music_views import *
from .vanity_views import *
from .desire_views import *
from .travel_views import *
# from .chat_views import *  # 暂时注释掉，直到修复导入问题
from .social_media_views import (
    social_subscription_demo,
    add_social_subscription_api,
    get_subscriptions_api,
    update_subscription_api,
    get_notifications_api,
    mark_notification_read_api,
    get_subscription_stats_api,
    delete_subscription_api,
    batch_update_subscriptions_api,
    batch_delete_subscriptions_api,
    SocialMediaAPIView,
)
from .diary_views import *
from .goal_views import *
from .health_views import *
from .fitness_views import *

# 从legacy_views导入核心函数（避免循环导入）
from ..legacy_views import (
    # 音频转换相关
    convert_audio_file,
    decrypt_ncm_file,
    audio_converter_api,
    
    # 旅行指南相关
    generate_travel_guide,
    generate_travel_guide_with_deepseek,
    export_travel_guide_api,
    format_travel_guide_for_export,
    
    # 心链相关
    create_heart_link_request_api,
    check_heart_link_status_api,
    cleanup_expired_heart_link_requests,
    disconnect_inactive_users,
    
    # 聊天相关API
    get_chat_messages_api,
    send_message_api,
    update_online_status_api,
    get_online_users_api,
    get_active_chat_rooms_api,
    
    # 生活日记相关API
    life_diary_api,
    emo_diary_api,
    creative_writer_api,
    fitness_api,
    
    # 社交订阅相关API
    add_social_subscription_api,
    get_subscriptions_api,
    update_subscription_api,
    get_notifications_api,
    mark_notification_read_api,
    get_subscription_stats_api,
    
    # 抖音分析相关API
    douyin_analysis_api,
    get_douyin_analysis_api,
    generate_product_preview_api,
    get_douyin_analysis_list_api,
    
    # 模式相关API
    record_mode_click_api,
    get_user_preferred_mode_api,
    
    # 三重觉醒相关API
    create_fitness_workout_api,
    create_code_workout_api,
    complete_daily_task_api,
    get_workout_dashboard_api,
    get_ai_dependency_api,
    get_pain_currency_api,
    record_exhaustion_audio_api,
    create_exhaustion_proof_api,
    create_copilot_collaboration_api,
    
    # 食物随机选择器相关API
    start_food_randomization_api,
    pause_food_randomization_api,
    rate_food_api,
    
    # 页面视图
    emo_diary,
    creative_writer,
    meditation_guide,
    peace_meditation_view,
    heart_link,
    heart_link_chat,
    chat_enhanced,
    chat_debug_view,
    douyin_analyzer,
    triple_awakening_dashboard,
    copilot_page,
    fitness_community,
    fitness_profile,
    fitness_tools,
    food_randomizer,
    audio_converter_view,
    
    # 其他常用函数
    is_admin,
    admin_required,
    validate_budget_range,
)

# 通用文件下载视图
from .file_download_views import generic_file_download