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

# 暂时从legacy_models导入其他模型，逐步迁移
from .legacy_models import (
    # 日记相关
    LifeDiaryEntry, LifeGoal, LifeGoalProgress, LifeStatistics,
    
    # 聊天相关
    ChatRoom, ChatMessage, UserOnlineStatus, HeartLinkRequest,
    
    # 成就相关
    UserAchievement,
    
    # 健身相关
    FitnessWorkoutSession, CodeWorkoutSession, ExhaustionProof,
    AIDependencyMeter, CoPilotCollaboration, DailyWorkoutChallenge,
    PainCurrency, WorkoutDashboard,
    
    # Vanity/欲望相关
    DesireDashboard, DesireItem, DesireFulfillment,
    VanityWealth, SinPoints, Sponsor, VanityTask, BasedDevAvatar,
    
    # 旅游相关
    TravelGuide, TravelGuideCache, TravelDestination, TravelReview,
    UserGeneratedTravelGuide, TravelGuideUsage,
    
    # 工作搜索相关
    JobSearchRequest, JobApplication, JobSearchProfile, JobSearchStatistics,
    
    # PDF转换相关
    PDFConversionRecord,
    
    # 食物相关
    FoodRandomizer, FoodItem, FoodRandomizationSession, FoodHistory,
    CheckInCalendar, CheckInDetail, CheckInStreak, CheckInAchievement,
    FoodPhotoBinding, FoodPhotoBindingHistory,
    
    # 人际关系相关
    RelationshipTag, PersonProfile, Interaction, ImportantMoment,
    RelationshipStatistics, RelationshipReminder,
    
    # 功能相关
    Feature, UserFeaturePermission, FeatureRecommendation, UserFirstVisit,
    
    # 健身社区相关
    FitnessCommunityPost, FitnessCommunityComment, FitnessCommunityLike,
    FitnessUserProfile, DietPlan, Meal, NutritionReminder, MealLog,
    WeightTracking, FoodDatabase, FitnessAchievement, UserFitnessAchievement,
    FitnessFollow,
    
    # 时光胶囊相关
    TimeCapsule, CapsuleUnlock, MemoryFragment, Achievement, ParallelMatch,
    
    # 船宝相关
    ShipBaoItem, ShipBaoTransaction, ShipBaoMessage, ShipBaoUserProfile,
    ShipBaoReport,
    
    # 搭子相关
    BuddyEvent, BuddyEventMember, BuddyEventChat, BuddyEventMessage,
    BuddyUserProfile, BuddyEventReview, BuddyEventReport,
    
    # 其他
    ExerciseWeightRecord, FitnessStrengthProfile
)



# 导出所有模型类
__all__ = [
    # 基础模型
    'ToolUsageLog',
    
    # 社交媒体模型
    'SocialMediaSubscription',
    'SocialMediaNotification',
    'SocialMediaPost',
    'SocialMediaComment',
    'SocialMediaLike',
    'SocialMediaShare',
    'SocialMediaUser',
    'SocialMediaPlatform',
    'SocialMediaCrawlerLog',
    'SocialMediaCrawlerConfig',
    
    # 日记模型
    'LifeDiaryEntry',
    'LifeStatistics',
    'LifeMood',
    'LifeCategory',
    'LifeTag',
    
    # 聊天模型
    'ChatRoom',
    'ChatMessage',
    'UserOnlineStatus',
    'HeartLinkRequest',
    'ChatRoomMember',
    'ChatRoomInvitation',
    
    # 目标模型
    'LifeGoal',
    'LifeGoalProgress',
    'LifeGoalCategory',
    'LifeGoalMilestone',
    
    # 健身模型
    'FitnessWorkoutSession',
    'CodeWorkoutSession',
    'ExhaustionProof',
    'AIDependencyMeter',
    'CoPilotCollaboration',
    'DailyWorkoutChallenge',
    'PainCurrency',
    'WorkoutDashboard',
    'FitnessProfile',
    'WorkoutPlan',
    'Exercise',
    'WorkoutLog',
    
    # 旅游模型
    'TravelGuide',
    'TravelDestination',
    'TravelItinerary',
    'TravelExpense',
    'TravelPhoto',
    'TravelReview',
    
    # 食物模型
    'FoodRandomizer',
    'FoodItem',
    'FoodRandomizationSession',
    'FoodHistory',
    'FoodCategory',
    'FoodNutrition',
    'FoodImage',
    'FoodRating',
    
    # 塔罗牌模型
    'TarotCard',
    'TarotSpread',
    'TarotReading',
    'TarotEnergyCalendar',
    'TarotCommunity',
    'TarotCommunityComment',
    
    # Vanity模型
    'VanityWealth',
    'SinPoints',
    'Sponsor',
    'VanityTask',
    'BasedDevAvatar',
    
    # 时光胶囊模型
    'TimeCapsule',
    'CapsuleUnlock',
    'MemoryFragment',
    'Achievement',
    'ParallelMatch',
    
    # 吉他训练模型
    'GuitarPracticeSession',
    'GuitarExercise',
    'GuitarSong',
    'GuitarProgress',
    'GuitarTab',
    
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
    
    # 欲望仪表盘模型
    'DesireDashboard',
    'DesireItem',
    'DesireFulfillment',
    
    # 人际关系模型
    'RelationshipTag',
    'PersonProfile',
    'Interaction',
    'ImportantMoment',
    'RelationshipStatistics',
    'RelationshipReminder',
]
