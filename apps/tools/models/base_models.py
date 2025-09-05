from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.utils import timezone


class ToolUsageLog(models.Model):
    """工具使用日志模型"""

    class Meta:
        app_label = "apps.tools"

    TOOL_CHOICES = [
        ("TEST_CASE", "Test Case Generator"),
        ("QUALITY_CHECK", "Code Quality Check"),
        ("PERF_TEST", "Performance Simulator"),
        ("REDBOOK", "RedBook Generator"),
        ("PDF_CONVERTER", "PDF Converter"),
        ("FORTUNE_ANALYZER", "Fortune Analyzer"),
        ("WEB_CRAWLER", "Web Crawler"),
        ("SOCIAL_SUBSCRIPTION", "Social Subscription"),
        ("SELF_ANALYSIS", "Self Analysis"),
        ("STORYBOARD", "Storyboard"),
        ("FITNESS_CENTER", "Fitness Center"),
        ("TRAINING_PLAN", "Training Plan Editor"),
        ("DEEPSEEK", "DeepSeek API"),
        ("EMO_DIARY", "Emo Diary"),
        ("CREATIVE_WRITER", "Creative Writer"),
        ("MEDITATION_GUIDE", "Meditation Guide"),
        ("MUSIC_HEALING", "Music Healing"),
        ("HEART_LINK", "Heart Link"),
        ("LIFE_DIARY", "Life Diary"),
        ("DOUYIN_ANALYZER", "Douyin Analyzer"),
        ("TRIPLE_AWAKENING", "Triple Awakening"),
        ("DESIRE_DASHBOARD", "Desire Dashboard"),
        ("VANITY_OS", "VanityOS"),
        ("TAROT", "Tarot"),
        ("FOOD_RANDOMIZER", "Food Randomizer"),
        ("TIME_CAPSULE", "Time Capsule"),
        ("GUITAR_TRAINING", "Guitar Training"),
        ("FITNESS_TOOLS", "Fitness Tools"),
        ("BUDDY", "Buddy"),
        ("SHIPBAO", "ShipBao"),
    ]

    preview_image = models.ImageField(upload_to="tool_previews/", null=True, blank=True)
    raw_response = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    tool_type = models.CharField(max_length=20, choices=TOOL_CHOICES, db_index=True)
    input_data = models.TextField()
    output_file = models.FileField(upload_to="tool_outputs/")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    execution_time = models.FloatField(null=True, blank=True)  # 执行时间（秒）
    success = models.BooleanField(default=True)  # 是否成功
    error_message = models.TextField(null=True, blank=True)  # 错误信息

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "tool_type"]),
            models.Index(fields=["created_at", "tool_type"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["success", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_tool_type_display()} - {self.created_at}"

    @classmethod
    def get_user_tool_usage(cls, user, tool_type=None, days=30):
        """获取用户工具使用统计，带缓存"""
        cache_key = f"tool_usage_{user.id}_{tool_type}_{days}"
        result = cache.get(cache_key)

        if result is None:
            queryset = cls.objects.filter(user=user, created_at__gte=timezone.now() - timedelta(days=days))
            if tool_type:
                queryset = queryset.filter(tool_type=tool_type)

            result = {
                "total_usage": queryset.count(),
                "recent_usage": queryset.filter(created_at__gte=timezone.now() - timedelta(days=7)).count(),
                "success_rate": queryset.filter(success=True).count() / max(queryset.count(), 1) * 100,
                "avg_execution_time": queryset.aggregate(avg_time=models.Avg("execution_time"))["avg_time"] or 0,
                "tool_breakdown": list(
                    queryset.values("tool_type").annotate(
                        count=models.Count("id"), success_count=models.Count("id", filter=Q(success=True))
                    )
                ),
            }
            cache.set(cache_key, result, 300)  # 缓存5分钟

        return result

    @classmethod
    def get_tool_statistics(cls, tool_type=None, days=30):
        """获取工具使用统计"""
        cache_key = f"tool_stats_{tool_type}_{days}"
        result = cache.get(cache_key)

        if result is None:
            queryset = cls.objects.filter(created_at__gte=timezone.now() - timedelta(days=days))
            if tool_type:
                queryset = queryset.filter(tool_type=tool_type)

            result = {
                "total_usage": queryset.count(),
                "unique_users": queryset.values("user").distinct().count(),
                "success_rate": queryset.filter(success=True).count() / max(queryset.count(), 1) * 100,
                "avg_execution_time": queryset.aggregate(avg_time=models.Avg("execution_time"))["avg_time"] or 0,
                "daily_usage": list(
                    queryset.extra(select={"day": "date(created_at)"})
                    .values("day")
                    .annotate(count=models.Count("id"))
                    .order_by("day")
                ),
            }
            cache.set(cache_key, result, 600)  # 缓存10分钟

        return result


class SystemLog(models.Model):
    """系统日志模型"""

    LOG_LEVEL_CHOICES = [
        ("DEBUG", "Debug"),
        ("INFO", "Info"),
        ("WARNING", "Warning"),
        ("ERROR", "Error"),
        ("CRITICAL", "Critical"),
    ]

    LOG_TYPE_CHOICES = [
        ("SYSTEM", "System"),
        ("USER_ACTION", "User Action"),
        ("API_CALL", "API Call"),
        ("ERROR", "Error"),
        ("PERFORMANCE", "Performance"),
        ("SECURITY", "Security"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES, db_index=True)
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    message = models.TextField()
    details = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    request_path = models.CharField(max_length=500, null=True, blank=True)
    execution_time = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp", "level"]),
            models.Index(fields=["log_type", "timestamp"]),
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["level", "log_type"]),
        ]

    def __str__(self):
        return f"{self.timestamp} - {self.level} - {self.message[:50]}"

    @classmethod
    def log_info(cls, message, user=None, details=None, **kwargs):
        """记录信息日志"""
        return cls.objects.create(level="INFO", log_type="SYSTEM", user=user, message=message, details=details, **kwargs)

    @classmethod
    def log_error(cls, message, user=None, details=None, **kwargs):
        """记录错误日志"""
        return cls.objects.create(level="ERROR", log_type="ERROR", user=user, message=message, details=details, **kwargs)

    @classmethod
    def log_performance(cls, message, execution_time, user=None, **kwargs):
        """记录性能日志"""
        return cls.objects.create(
            level="INFO", log_type="PERFORMANCE", user=user, message=message, execution_time=execution_time, **kwargs
        )


class UserActivity(models.Model):
    """用户活动模型"""

    ACTIVITY_TYPE_CHOICES = [
        ("LOGIN", "Login"),
        ("LOGOUT", "Logout"),
        ("PAGE_VIEW", "Page View"),
        ("TOOL_USAGE", "Tool Usage"),
        ("API_CALL", "API Call"),
        ("DATA_CREATE", "Data Create"),
        ("DATA_UPDATE", "Data Update"),
        ("DATA_DELETE", "Data Delete"),
        ("FILE_UPLOAD", "File Upload"),
        ("FILE_DOWNLOAD", "File Download"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    description = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["activity_type", "timestamp"]),
            models.Index(fields=["user", "activity_type"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} - {self.timestamp}"

    @classmethod
    def track_activity(cls, user, activity_type, description, **kwargs):
        """跟踪用户活动"""
        return cls.objects.create(user=user, activity_type=activity_type, description=description, **kwargs)

    @classmethod
    def get_user_activity_summary(cls, user, days=30):
        """获取用户活动摘要"""
        cache_key = f"user_activity_{user.id}_{days}"
        result = cache.get(cache_key)

        if result is None:
            queryset = cls.objects.filter(user=user, timestamp__gte=timezone.now() - timedelta(days=days))

            result = {
                "total_activities": queryset.count(),
                "activity_breakdown": list(
                    queryset.values("activity_type").annotate(count=models.Count("id")).order_by("-count")
                ),
                "recent_activities": list(
                    queryset.order_by("-timestamp")[:10].values("activity_type", "description", "timestamp")
                ),
                "daily_activity": list(
                    queryset.extra(select={"day": "date(timestamp)"})
                    .values("day")
                    .annotate(count=models.Count("id"))
                    .order_by("day")
                ),
            }
            cache.set(cache_key, result, 300)  # 缓存5分钟

        return result


class SystemConfiguration(models.Model):
    """系统配置模型"""

    CONFIG_TYPE_CHOICES = [
        ("GENERAL", "General"),
        ("PERFORMANCE", "Performance"),
        ("SECURITY", "Security"),
        ("CACHE", "Cache"),
        ("API", "API"),
        ("FEATURE", "Feature"),
    ]

    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, db_index=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["config_type", "key"]
        indexes = [
            models.Index(fields=["config_type", "is_active"]),
            models.Index(fields=["key", "is_active"]),
        ]

    def __str__(self):
        return f"{self.key} = {self.value}"

    @classmethod
    def get_config(cls, key, default=None):
        """获取配置值"""
        cache_key = f"config_{key}"
        value = cache.get(cache_key)

        if value is None:
            try:
                config = cls.objects.get(key=key, is_active=True)
                value = config.value
                cache.set(cache_key, value, 3600)  # 缓存1小时
            except cls.DoesNotExist:
                value = default

        return value

    @classmethod
    def set_config(cls, key, value, config_type="GENERAL", description=None):
        """设置配置值"""
        config, created = cls.objects.get_or_create(
            key=key,
            defaults={
                "value": value,
                "config_type": config_type,
                "description": description,
            },
        )

        if not created:
            config.value = value
            config.config_type = config_type
            if description:
                config.description = description
            config.save()

        # 清除缓存
        cache.delete(f"config_{key}")

        return config


class FeatureFlag(models.Model):
    """功能开关模型"""

    FLAG_TYPE_CHOICES = [
        ("BOOLEAN", "Boolean"),
        ("PERCENTAGE", "Percentage"),
        ("USER_LIST", "User List"),
        ("TIME_BASED", "Time Based"),
    ]

    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField()
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPE_CHOICES, db_index=True)
    is_enabled = models.BooleanField(default=False, db_index=True)
    percentage = models.IntegerField(default=0)  # 百分比启用
    user_list = models.JSONField(null=True, blank=True)  # 用户ID列表
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_enabled", "flag_type"]),
            models.Index(fields=["name", "is_enabled"]),
        ]

    def __str__(self):
        return f"{self.name} ({'Enabled' if self.is_enabled else 'Disabled'})"

    def is_enabled_for_user(self, user):
        """检查功能是否对用户启用"""
        if not self.is_enabled:
            return False

        if self.flag_type == "BOOLEAN":
            return True
        elif self.flag_type == "PERCENTAGE":
            return user.id % 100 < self.percentage
        elif self.flag_type == "USER_LIST":
            return user.id in (self.user_list or [])
        elif self.flag_type == "TIME_BASED":
            now = timezone.now()
            return (not self.start_time or now >= self.start_time) and (not self.end_time or now <= self.end_time)

        return False

    @classmethod
    def is_feature_enabled(cls, feature_name, user=None):
        """检查功能是否启用"""
        cache_key = f"feature_flag_{feature_name}"
        flag = cache.get(cache_key)

        if flag is None:
            try:
                flag = cls.objects.get(name=feature_name)
                cache.set(cache_key, flag, 300)  # 缓存5分钟
            except cls.DoesNotExist:
                return False

        if user:
            return flag.is_enabled_for_user(user)
        else:
            return flag.is_enabled
