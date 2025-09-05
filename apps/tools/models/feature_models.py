from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Feature(models.Model):
    """功能模型 - 记录系统中的所有功能"""

    FEATURE_TYPE_CHOICES = [
        ("tool", "工具功能"),
        ("mode", "模式功能"),
        ("page", "页面功能"),
        ("api", "API功能"),
    ]

    CATEGORY_CHOICES = [
        ("work", "工作效率"),
        ("life", "生活娱乐"),
        ("health", "健康管理"),
        ("social", "社交互动"),
        ("creative", "创作工具"),
        ("analysis", "数据分析"),
        ("entertainment", "娱乐休闲"),
        ("learning", "学习成长"),
        ("other", "其他"),
    ]

    name = models.CharField(max_length=100, verbose_name="功能名称")
    description = models.TextField(verbose_name="功能描述")
    feature_type = models.CharField(max_length=20, choices=FEATURE_TYPE_CHOICES, verbose_name="功能类型")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="功能分类")
    url_name = models.CharField(max_length=100, verbose_name="URL名称", help_text="Django URL name")
    icon_class = models.CharField(max_length=100, verbose_name="图标类名", help_text="Font Awesome图标类名")
    icon_color = models.CharField(max_length=20, default="#007bff", verbose_name="图标颜色")

    # 权限和可见性
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_public = models.BooleanField(default=True, verbose_name="是否公开")
    require_login = models.BooleanField(default=True, verbose_name="是否需要登录")
    require_membership = models.CharField(
        max_length=20,
        choices=[
            ("", "无要求"),
            ("basic", "基础会员"),
            ("premium", "高级会员"),
            ("vip", "VIP会员"),
        ],
        blank=True,
        verbose_name="会员要求",
    )

    # 推荐权重
    recommendation_weight = models.IntegerField(default=50, verbose_name="推荐权重", help_text="1-100，数值越高推荐概率越大")
    popularity_score = models.IntegerField(default=0, verbose_name="受欢迎程度", help_text="基于使用量自动计算")

    # 统计信息
    total_usage_count = models.IntegerField(default=0, verbose_name="总使用次数")
    monthly_usage_count = models.IntegerField(default=0, verbose_name="月使用次数")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "功能"
        verbose_name_plural = "功能管理"
        ordering = ["-recommendation_weight", "-popularity_score", "name"]
        indexes = [
            models.Index(fields=["is_active", "is_public"]),
            models.Index(fields=["category", "feature_type"]),
            models.Index(fields=["recommendation_weight", "popularity_score"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_feature_type_display()})"

    def can_recommend_to_user(self, user):
        """检查是否可以向用户推荐此功能"""
        if not self.is_active or not self.is_public:
            return False

        if self.require_login and not user.is_authenticated:
            return False

        if self.require_membership:
            try:
                membership = user.membership
                if not membership.is_valid:
                    return False

                membership_levels = {"basic": 1, "premium": 2, "vip": 3}
                required_level = membership_levels.get(self.require_membership, 0)
                user_level = membership_levels.get(membership.membership_type, 0)

                if user_level < required_level:
                    return False
            except Exception:
                return False

        return True

    def increment_usage(self):
        """增加使用计数"""
        self.total_usage_count += 1
        self.monthly_usage_count += 1
        # 简单的受欢迎程度计算
        self.popularity_score = min(100, self.monthly_usage_count // 10)
        self.save(update_fields=["total_usage_count", "monthly_usage_count", "popularity_score"])


class UserFeaturePermission(models.Model):
    """用户功能权限模型 - 管理员可以控制用户能看到什么功能"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name="功能")
    is_visible = models.BooleanField(default=True, verbose_name="是否可见")
    is_allowed = models.BooleanField(default=True, verbose_name="是否允许使用")
    custom_weight = models.IntegerField(
        null=True, blank=True, verbose_name="自定义推荐权重", help_text="为特定用户设置的推荐权重，为空则使用功能默认权重"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_permissions", verbose_name="创建者"
    )

    class Meta:
        verbose_name = "用户功能权限"
        verbose_name_plural = "用户功能权限"
        unique_together = ["user", "feature"]
        indexes = [
            models.Index(fields=["user", "is_visible", "is_allowed"]),
            models.Index(fields=["feature", "is_visible"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.feature.name} ({'可见' if self.is_visible else '隐藏'})"


class FeatureRecommendation(models.Model):
    """功能推荐记录模型"""

    ACTION_CHOICES = [
        ("shown", "已展示"),
        ("clicked", "已点击"),
        ("dismissed", "已忽略"),
        ("not_interested", "不感兴趣"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, verbose_name="推荐功能")
    session_id = models.CharField(max_length=100, verbose_name="会话ID", help_text="用于标识同一次推荐会话")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="用户行为")

    # 推荐上下文信息
    recommendation_reason = models.CharField(max_length=200, blank=True, verbose_name="推荐理由")
    user_mode_preference = models.CharField(max_length=20, blank=True, verbose_name="用户模式偏好")
    recommendation_algorithm = models.CharField(max_length=50, default="random", verbose_name="推荐算法")

    # 时间信息
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="推荐时间")
    action_time = models.DateTimeField(null=True, blank=True, verbose_name="行为时间")

    # 设备和环境信息
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    user_agent = models.TextField(blank=True, verbose_name="用户代理")

    class Meta:
        verbose_name = "功能推荐记录"
        verbose_name_plural = "功能推荐记录"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["feature", "action"]),
            models.Index(fields=["session_id"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.feature.name} - {self.get_action_display()}"

    @classmethod
    def get_user_recommendation_history(cls, user, days=30):
        """获取用户最近的推荐历史"""
        from datetime import timedelta

        since = timezone.now() - timedelta(days=days)
        return cls.objects.filter(user=user, created_at__gte=since)

    @classmethod
    def has_recent_recommendation(cls, user, feature, hours=24):
        """检查最近是否已经推荐过该功能"""
        from datetime import timedelta

        since = timezone.now() - timedelta(hours=hours)
        return cls.objects.filter(user=user, feature=feature, created_at__gte=since).exists()


class UserFirstVisit(models.Model):
    """用户首次访问记录"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")
    first_visit_time = models.DateTimeField(auto_now_add=True, verbose_name="首次访问时间")
    has_seen_recommendation = models.BooleanField(default=False, verbose_name="是否已看过推荐")
    recommendation_shown_count = models.IntegerField(default=0, verbose_name="推荐展示次数")
    last_recommendation_time = models.DateTimeField(null=True, blank=True, verbose_name="最后推荐时间")

    # 用户行为统计
    total_login_count = models.IntegerField(default=1, verbose_name="总登录次数")
    total_feature_usage = models.IntegerField(default=0, verbose_name="总功能使用次数")

    class Meta:
        verbose_name = "用户首次访问记录"
        verbose_name_plural = "用户首次访问记录"

    def __str__(self):
        return f"{self.user.username} - 首次访问: {self.first_visit_time}"

    def should_show_recommendation(self):
        """判断是否应该显示推荐 - 每日只显示一次"""
        # 新用户首次访问，显示推荐
        if not self.has_seen_recommendation:
            return True

        # 检查是否今天已经显示过推荐
        if self.last_recommendation_time:
            from datetime import date

            today = date.today()
            last_recommendation_date = self.last_recommendation_time.date()

            # 如果今天已经显示过推荐，则不再显示
            if last_recommendation_date == today:
                return False

            # 如果不是今天显示的，则可以显示（每日一次）
            return True

        # 如果从未显示过推荐，则显示
        return True

    def mark_recommendation_shown(self):
        """标记已显示推荐"""
        self.has_seen_recommendation = True
        self.recommendation_shown_count += 1
        self.last_recommendation_time = timezone.now()
        self.save(update_fields=["has_seen_recommendation", "recommendation_shown_count", "last_recommendation_time"])
