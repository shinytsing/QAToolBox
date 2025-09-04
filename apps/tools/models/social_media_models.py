from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class SocialMediaSubscription(models.Model):
    """社交媒体订阅模型"""

    PLATFORM_CHOICES = [
        ("xiaohongshu", "小红书"),
        ("douyin", "抖音"),
        ("netease", "网易云音乐"),
        ("weibo", "微博"),
        ("bilibili", "B站"),
        ("zhihu", "知乎"),
    ]

    SUBSCRIPTION_TYPE_CHOICES = [
        ("newPosts", "新动态"),
        ("newFollowers", "新粉丝"),
        ("newFollowing", "新关注"),
        ("profileChanges", "资料变化"),
    ]

    # 订阅类型详细说明
    SUBSCRIPTION_TYPE_DESCRIPTIONS = {
        "newPosts": "用户发布的新内容，包括帖子、视频、文章等",
        "newFollowers": "有新用户关注了被订阅者（被订阅者获得新粉丝）",
        "newFollowing": "被订阅者新关注了其他用户（被订阅者关注了别人）",
        "profileChanges": "用户资料信息的变化，如头像、昵称、简介等",
    }

    FREQUENCY_CHOICES = [
        (5, "5分钟"),
        (15, "15分钟"),
        (30, "30分钟"),
        (60, "1小时"),
    ]

    STATUS_CHOICES = [
        ("active", "活跃"),
        ("paused", "暂停"),
        ("error", "错误"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", db_index=True)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, verbose_name="平台", db_index=True)
    target_user_id = models.CharField(max_length=100, verbose_name="目标用户ID", db_index=True)
    target_user_name = models.CharField(max_length=200, verbose_name="目标用户名")
    subscription_types = models.JSONField(default=list, verbose_name="订阅类型")
    check_frequency = models.IntegerField(choices=FREQUENCY_CHOICES, default=15, verbose_name="检查频率")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active", verbose_name="状态", db_index=True)
    last_check = models.DateTimeField(auto_now=True, verbose_name="最后检查时间", db_index=True)
    last_change = models.DateTimeField(null=True, blank=True, verbose_name="最后变化时间")
    avatar_url = models.URLField(blank=True, null=True, verbose_name="头像URL")

    # 用于存储上次检查的数据，避免重复通知
    last_follower_count = models.IntegerField(default=0, blank=True, null=True, verbose_name="上次粉丝数")
    last_video_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="上次最新视频ID")
    last_following_count = models.IntegerField(default=0, blank=True, null=True, verbose_name="上次关注数")
    last_profile_data = models.JSONField(default=dict, blank=True, null=True, verbose_name="上次资料数据")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = "tools"
        unique_together = ["user", "platform", "target_user_id"]
        ordering = ["-created_at"]
        verbose_name = "社交媒体订阅"
        verbose_name_plural = "社交媒体订阅"
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["platform", "status"]),
            models.Index(fields=["status", "last_check"]),
            models.Index(fields=["user", "platform"]),
            # 复合索引优化查询性能
            models.Index(fields=["user", "status", "last_check"]),
            models.Index(fields=["platform", "status", "last_check"]),
            models.Index(fields=["user", "platform", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_platform_display()} - {self.target_user_name}"

    @classmethod
    def get_active_subscriptions(cls, user=None, platform=None):
        """获取活跃订阅，带缓存"""
        cache_key = f"active_subscriptions_{user.id if user else 'all'}_{platform or 'all'}"
        result = cache.get(cache_key)

        if result is None:
            queryset = cls.objects.filter(status="active")
            if user:
                queryset = queryset.filter(user=user)
            if platform:
                queryset = queryset.filter(platform=platform)
            result = list(queryset.select_related("user"))
            cache.set(cache_key, result, 60)  # 缓存1分钟

        return result

    def needs_check(self):
        """检查是否需要检查更新"""
        from datetime import timedelta

        return timezone.now() - self.last_check > timedelta(minutes=self.check_frequency)

    @classmethod
    def get_user_subscription_stats(cls, user):
        """获取用户订阅统计信息"""
        from django.db.models import Count, Q

        total_subscriptions = cls.objects.filter(user=user).count()
        active_subscriptions = cls.objects.filter(user=user, status="active").count()
        paused_subscriptions = cls.objects.filter(user=user, status="paused").count()
        error_subscriptions = cls.objects.filter(user=user, status="error").count()

        # 按平台统计
        platform_stats = cls.objects.filter(user=user).values("platform").annotate(count=Count("id")).order_by("-count")

        return {
            "total_subscriptions": total_subscriptions,
            "active_subscriptions": active_subscriptions,
            "paused_subscriptions": paused_subscriptions,
            "error_subscriptions": error_subscriptions,
            "platform_stats": list(platform_stats),
        }


class SocialMediaNotification(models.Model):
    """社交媒体通知模型"""

    NOTIFICATION_TYPE_CHOICES = [
        ("newPosts", "新动态"),
        ("newFollowers", "新粉丝"),
        ("newFollowing", "新关注"),
        ("profileChanges", "资料变化"),
    ]

    subscription = models.ForeignKey(SocialMediaSubscription, on_delete=models.CASCADE, verbose_name="订阅", db_index=True)
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="通知类型", db_index=True
    )
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    data = models.JSONField(default=dict, verbose_name="详细数据")
    is_read = models.BooleanField(default=False, verbose_name="是否已读", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_index=True)

    # Additional fields added in migration 0014
    external_url = models.URLField(blank=True, null=True, verbose_name="外部链接")
    follower_avatar = models.URLField(blank=True, null=True, verbose_name="粉丝头像")
    follower_count = models.IntegerField(blank=True, default=0, null=True, verbose_name="当前粉丝总数")
    follower_id = models.CharField(blank=True, max_length=100, null=True, verbose_name="粉丝ID")
    follower_name = models.CharField(blank=True, max_length=200, null=True, verbose_name="粉丝名称")
    following_avatar = models.URLField(blank=True, null=True, verbose_name="关注对象头像")
    following_count = models.IntegerField(blank=True, default=0, null=True, verbose_name="当前关注总数")
    following_id = models.CharField(blank=True, max_length=100, null=True, verbose_name="关注对象ID")
    following_name = models.CharField(blank=True, max_length=200, null=True, verbose_name="关注对象名称")
    new_profile_data = models.JSONField(blank=True, default=dict, null=True, verbose_name="变化后资料")
    old_profile_data = models.JSONField(blank=True, default=dict, null=True, verbose_name="变化前资料")
    platform_specific_data = models.JSONField(blank=True, default=dict, null=True, verbose_name="平台特定数据")
    post_comments = models.IntegerField(blank=True, default=0, null=True, verbose_name="评论数")
    post_content = models.TextField(blank=True, null=True, verbose_name="帖子内容")
    post_images = models.JSONField(blank=True, default=list, null=True, verbose_name="帖子图片")
    post_likes = models.IntegerField(blank=True, default=0, null=True, verbose_name="点赞数")
    post_shares = models.IntegerField(blank=True, default=0, null=True, verbose_name="分享数")
    post_tags = models.JSONField(blank=True, default=list, null=True, verbose_name="帖子标签")
    post_video_url = models.URLField(blank=True, null=True, verbose_name="视频链接")
    profile_changes = models.JSONField(blank=True, default=dict, null=True, verbose_name="资料变化详情")

    class Meta:
        app_label = "tools"
        ordering = ["-created_at"]
        verbose_name = "社交媒体通知"
        verbose_name_plural = "社交媒体通知"
        indexes = [
            models.Index(fields=["subscription", "created_at"]),
            models.Index(fields=["is_read", "created_at"]),
        ]

    def __str__(self):
        return f"{self.subscription.target_user_name} - {self.get_notification_type_display()}"

    @classmethod
    def get_user_notification_stats(cls, user):
        """获取用户通知统计信息"""
        from django.db.models import Count

        total_notifications = cls.objects.filter(subscription__user=user).count()
        unread_notifications = cls.objects.filter(subscription__user=user, is_read=False).count()
        read_notifications = cls.objects.filter(subscription__user=user, is_read=True).count()

        # 按类型统计
        type_stats = (
            cls.objects.filter(subscription__user=user)
            .values("notification_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # 按平台统计
        platform_stats = (
            cls.objects.filter(subscription__user=user)
            .values("subscription__platform")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return {
            "total_notifications": total_notifications,
            "unread_notifications": unread_notifications,
            "read_notifications": read_notifications,
            "type_stats": list(type_stats),
            "platform_stats": list(platform_stats),
        }


class SocialMediaPlatformConfig(models.Model):
    """社交媒体平台配置模型"""

    platform = models.CharField(max_length=20, unique=True, verbose_name="平台")
    name = models.CharField(max_length=50, verbose_name="平台名称")
    is_enabled = models.BooleanField(default=True, verbose_name="是否启用")
    api_config = models.JSONField(default=dict, verbose_name="API配置")
    crawler_config = models.JSONField(default=dict, verbose_name="爬虫配置")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        app_label = "tools"
        verbose_name = "平台配置"
        verbose_name_plural = "平台配置"

    def __str__(self):
        return f"{self.name} ({'启用' if self.is_enabled else '禁用'})"


class DouyinVideoAnalysis(models.Model):
    """抖音视频分析模型"""

    video_url = models.URLField(default="", verbose_name="视频URL")
    video_id = models.CharField(max_length=100, unique=True, default="", verbose_name="视频ID")
    author_name = models.CharField(max_length=100, default="", verbose_name="作者名称")
    title = models.TextField(default="", verbose_name="视频标题")
    description = models.TextField(blank=True, verbose_name="视频描述")
    music_info = models.JSONField(default=dict, verbose_name="音乐信息")
    statistics = models.JSONField(default=dict, verbose_name="统计数据")
    hashtags = models.JSONField(default=list, verbose_name="话题标签")
    created_time = models.DateTimeField(default=timezone.now, verbose_name="视频创建时间")
    analyzed_at = models.DateTimeField(default=timezone.now, verbose_name="分析时间")

    class Meta:
        app_label = "tools"
        ordering = ["-analyzed_at"]
        verbose_name = "抖音视频分析"
        verbose_name_plural = "抖音视频分析"

    def __str__(self):
        return f"{self.author_name} - {self.title[:50]}"


class DouyinVideo(models.Model):
    """抖音视频模型"""

    video_id = models.CharField(max_length=100, unique=True, default="", verbose_name="视频ID")
    author_id = models.CharField(max_length=100, verbose_name="作者ID", blank=True, null=True)
    author_name = models.CharField(max_length=100, verbose_name="作者名称", blank=True, null=True)
    title = models.TextField(verbose_name="视频标题", blank=True, null=True)
    cover_url = models.URLField(verbose_name="封面URL", blank=True, null=True)
    video_url = models.URLField(default="", verbose_name="视频URL")
    duration = models.IntegerField(default=0, verbose_name="时长(秒)")
    likes = models.IntegerField(default=0, verbose_name="点赞数")
    comments = models.IntegerField(default=0, verbose_name="评论数")
    shares = models.IntegerField(default=0, verbose_name="分享数")
    music = models.JSONField(default=dict, verbose_name="音乐信息")
    hashtags = models.JSONField(default=list, verbose_name="话题标签")
    created_time = models.DateTimeField(default=timezone.now, verbose_name="视频创建时间")
    crawled_at = models.DateTimeField(default=timezone.now, verbose_name="爬取时间")

    class Meta:
        app_label = "tools"
        ordering = ["-created_time"]
        verbose_name = "抖音视频"
        verbose_name_plural = "抖音视频"

    def __str__(self):
        return f"{self.author_name} - {self.title[:50]}"
