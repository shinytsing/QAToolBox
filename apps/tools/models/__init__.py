# 🏗️ 优化的模型导入结构 - 逐步分离legacy_models

# 基础模型
from .base_models import ToolUsageLog

# 社交媒体模型（已分离）
from .social_media_models import (
    SocialMediaSubscription, SocialMediaNotification, SocialMediaPlatformConfig,
    DouyinVideoAnalysis, DouyinVideo
)

# 塔罗牌模型从tarot_models导入
from .tarot_models import (
    TarotCard, TarotSpread, TarotReading, TarotEnergyCalendar,
    TarotCommunity, TarotCommunityComment
)

# 聊天模型从chat_models导入
from .chat_models import (
    ChatRoom, ChatMessage, ChatRoomMember, MessageRead, UserOnlineStatus, HeartLinkRequest
)

# 日记相关模型（已分离）
from .diary_models import (
    LifeDiaryEntry, DiaryAchievement, DiaryTemplate, DailyQuestion,
    LifeCategory, LifeTag
)

# 旅游攻略模型从travel_models导入
from .travel_models import (
    TravelGuide, TravelGuideCache, TravelReview, TravelCity,
    TravelPost, TravelPostLike, TravelPostFavorite, TravelPostComment,
    UserGeneratedTravelGuide, TravelGuideUsage
)

# 船宝二手交易模型从shipbao_models导入（暂时注释，避免与legacy_models冲突）
# from .shipbao_models import (
#     ShipBaoItem, ShipBaoItemImage, ShipBaoFavorite, ShipBaoInquiry,
#     ShipBaoTransaction, ShipBaoUserProfile
# )

# 暂时从legacy_models导入其他模型，逐步迁移
from .legacy_models import (
    # 生活目标相关
    LifeGoal, LifeGoalProgress, LifeStatistics,
    
    # 成就相关
    UserAchievement,
    
    # 健身相关
    FitnessWorkoutSession, CodeWorkoutSession, ExhaustionProof,
    AIDependencyMeter, CoPilotCollaboration, DailyWorkoutChallenge,
    PainCurrency, WorkoutDashboard,
    TrainingPlan,
    
    # Vanity/欲望相关
    DesireDashboard, DesireItem, DesireFulfillment,
    VanityWealth, SinPoints, Sponsor, VanityTask, BasedDevAvatar,
    
    # 旅游相关（已移至travel_models.py）
    
    # 工作搜索相关
    JobSearchRequest, JobApplication, JobSearchProfile, JobSearchStatistics,
    
    # PDF转换相关
    PDFConversionRecord,
    
    # 食物相关
    FoodRandomizer, FoodItem, FoodRandomizationSession, FoodHistory,
    CheckInCalendar, CheckInDetail, CheckInStreak, CheckInAchievement,
    FoodPhotoBinding, FoodPhotoBindingHistory,
    
    # 人际关系相关 - 已移至relationship_models.py
    # RelationshipTag, PersonProfile, Interaction, ImportantMoment,
    # RelationshipStatistics, RelationshipReminder,
    
    # 功能相关
    Feature, UserFeaturePermission, FeatureRecommendation, UserFirstVisit,
    
    # 健身社区相关
    FitnessCommunityPost, FitnessCommunityComment, FitnessCommunityLike,
    FitnessUserProfile, 
    # NutriCoach Pro相关模型已隐藏
    # DietPlan, Meal, NutritionReminder, MealLog,
    # WeightTracking, FoodDatabase, 
    FitnessAchievement, UserFitnessAchievement,
    FitnessFollow,
    

    
    # 船宝相关
    ShipBaoItem, ShipBaoTransaction, ShipBaoMessage, ShipBaoUserProfile, ShipBaoReport,
    
    # 旅游目的地相关
    TravelDestination,
    
    # 搭子相关
    BuddyEvent, BuddyEventMember, BuddyEventChat, BuddyEventMessage,
    BuddyUserProfile, BuddyEventReview, BuddyEventReport,
    
    # 其他
    ExerciseWeightRecord, FitnessStrengthProfile
)

# 从relationship_models导入人际关系相关模型
from .relationship_models import (
    RelationshipTag, PersonProfile, Interaction, ImportantMoment,
    RelationshipStatistics, RelationshipReminder
)

# 从nutrition_models导入营养信息相关模型
from .nutrition_models import (
    NutritionCategory, FoodNutrition, FoodNutritionHistory, FoodRandomizationLog
)

# 导出所有模型类
__all__ = [
    # 基础模型
    'ToolUsageLog',
    
    # 社交媒体模型
    'SocialMediaSubscription',
    'SocialMediaNotification',
    'SocialMediaPlatformConfig',
    'DouyinVideoAnalysis',
    'DouyinVideo',
    
    # 塔罗牌模型
    'TarotCard',
    'TarotSpread',
    'TarotReading',
    'TarotEnergyCalendar',
    'TarotCommunity',
    'TarotCommunityComment',
    
    # 聊天模型
    'ChatRoom',
    'ChatMessage',
    'ChatRoomMember',
    'MessageRead',
    'UserOnlineStatus',
    'HeartLinkRequest',
    
    # 日记模型
    'LifeDiaryEntry',
    'LifeGoal',
    'LifeGoalProgress',
    'LifeStatistics',
    
    # 成就模型
    'UserAchievement',
    
    # 健身模型
    'FitnessWorkoutSession',
    'CodeWorkoutSession',
    'ExhaustionProof',
    'AIDependencyMeter',
    'CoPilotCollaboration',
    'DailyWorkoutChallenge',
    'PainCurrency',
    'WorkoutDashboard',
    'TrainingPlan',
    'FitnessUserProfile',
    # NutriCoach Pro相关模型已隐藏
    # 'DietPlan',
    # 'Meal', 
    # 'NutritionReminder',
    # 'MealLog',
    # 'WeightTracking',
    # 'FoodDatabase',
    'FitnessAchievement',
    'UserFitnessAchievement',
    'FitnessFollow',
    'ExerciseWeightRecord',
    'FitnessStrengthProfile',
    
    # 健身社区模型
    'FitnessCommunityPost',
    'FitnessCommunityComment',
    'FitnessCommunityLike',
    
    # 旅游模型
    'TravelGuide',
    'TravelGuideCache',
    'TravelReview',
    'TravelCity',
    'TravelPost',
    'TravelPostLike',
    'TravelPostFavorite',
    'TravelPostComment',
    'UserGeneratedTravelGuide',
    'TravelGuideUsage',
    
    # 食物模型
    'FoodRandomizer',
    'FoodItem',
    'FoodRandomizationSession',
    'FoodHistory',
    'FoodPhotoBinding',
    'FoodPhotoBindingHistory',
    
    # 营养信息模型
    'NutritionCategory',
    'FoodNutrition',
    'FoodNutritionHistory',
    'FoodRandomizationLog',
    
    # 签到模型
    'CheckInCalendar',
    'CheckInDetail',
    'CheckInStreak',
    'CheckInAchievement',
    
    # Vanity模型
    'DesireDashboard',
    'DesireItem',
    'DesireFulfillment',
    'VanityWealth',
    'SinPoints',
    'Sponsor',
    'VanityTask',
    'BasedDevAvatar',
    

    
    # 搭子模型
    'BuddyEvent',
    'BuddyEventMember',
    'BuddyEventChat',
    'BuddyEventMessage',
    'BuddyUserProfile',
    'BuddyEventReview',
    'BuddyEventReport',
    
    # 船宝模型
    'ShipBaoItem',
    'ShipBaoTransaction',
    'ShipBaoMessage',
    'ShipBaoUserProfile',
    'ShipBaoReport',
    # 旅游目的地模型
    'TravelDestination',
    
    # 人际关系模型
    'RelationshipTag',
    'PersonProfile',
    'Interaction',
    'ImportantMoment',
    'RelationshipStatistics',
    'RelationshipReminder',
    
    # 功能模型
    'Feature',
    'UserFeaturePermission',
    'FeatureRecommendation',
    'UserFirstVisit',
    
    # 工作搜索模型
    'JobSearchRequest',
    'JobApplication',
    'JobSearchProfile',
    'JobSearchStatistics',
    
    # PDF转换模型
    'PDFConversionRecord',
]
