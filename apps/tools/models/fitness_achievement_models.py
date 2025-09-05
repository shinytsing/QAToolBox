from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# 延迟导入以避免循环导入


class FitnessAchievementModule(models.Model):
    """健身成就模块"""

    MODULE_CHOICES = [
        ("strength", "力量训练"),
        ("cardio", "有氧运动"),
        ("nutrition", "营养管理"),
        ("consistency", "连续性"),
        ("social", "社交互动"),
        ("milestone", "里程碑"),
        ("special", "特殊成就"),
    ]

    name = models.CharField(max_length=50, choices=MODULE_CHOICES, unique=True, verbose_name="模块名称")
    display_name = models.CharField(max_length=100, verbose_name="显示名称")
    description = models.TextField(verbose_name="模块描述")
    icon = models.CharField(max_length=50, default="fas fa-trophy", verbose_name="模块图标")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="主题颜色")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "健身成就模块"
        verbose_name_plural = "健身成就模块"
        ordering = ["name"]

    def __str__(self):
        return self.display_name


class EnhancedFitnessAchievement(models.Model):
    """增强版健身成就模型"""

    LEVEL_CHOICES = [
        ("bronze", "铜牌"),
        ("silver", "银牌"),
        ("gold", "金牌"),
        ("platinum", "白金"),
        ("diamond", "钻石"),
        ("legendary", "传奇"),
    ]

    RARITY_CHOICES = [
        ("common", "普通"),
        ("rare", "稀有"),
        ("epic", "史诗"),
        ("legendary", "传奇"),
    ]

    module = models.ForeignKey(FitnessAchievementModule, on_delete=models.CASCADE, verbose_name="所属模块")
    name = models.CharField(max_length=100, verbose_name="成就名称")
    description = models.TextField(verbose_name="成就描述")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, verbose_name="成就等级")
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default="common", verbose_name="稀有度")

    # 徽章设计
    icon = models.CharField(max_length=50, default="fas fa-trophy", verbose_name="成就图标")
    badge_color = models.CharField(max_length=7, default="#FFD700", verbose_name="徽章颜色")
    badge_shape = models.CharField(max_length=20, default="circle", verbose_name="徽章形状")
    badge_design = models.JSONField(default=dict, verbose_name="徽章设计")

    # 解锁条件
    unlock_condition = models.JSONField(default=dict, verbose_name="解锁条件")
    unlock_formula = models.TextField(blank=True, null=True, verbose_name="解锁公式")
    is_auto_unlock = models.BooleanField(default=True, verbose_name="是否自动解锁")
    is_hidden = models.BooleanField(default=False, verbose_name="是否隐藏成就")

    # 奖励
    points_reward = models.IntegerField(default=0, verbose_name="积分奖励")
    badge_reward = models.BooleanField(default=True, verbose_name="是否奖励徽章")
    special_reward = models.JSONField(default=dict, verbose_name="特殊奖励")

    # 统计
    total_earned = models.IntegerField(default=0, verbose_name="总获得次数")
    completion_rate = models.FloatField(default=0.0, verbose_name="完成率")

    # 排序和显示
    sort_order = models.IntegerField(default=0, verbose_name="排序顺序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "健身成就"
        verbose_name_plural = "健身成就"
        ordering = ["module", "sort_order", "level", "name"]
        indexes = [
            models.Index(fields=["module", "is_active"]),
            models.Index(fields=["level", "rarity"]),
        ]

    def __str__(self):
        return f"[{self.module.display_name}] {self.get_level_display()} - {self.name}"

    def get_unlock_progress(self, user):
        """获取用户解锁进度"""
        from .legacy_models import UserFitnessAchievement

        try:
            user_achievement = UserFitnessAchievement.objects.get(user=user, achievement=self)
            return user_achievement.progress
        except UserFitnessAchievement.DoesNotExist:
            return 0

    def check_unlock_condition(self, user):
        """检查解锁条件"""
        if not self.is_auto_unlock:
            return False

        condition = self.unlock_condition
        if not condition:
            return False

        # 根据模块类型检查不同的条件
        if self.module.name == "strength":
            return self._check_strength_condition(user, condition)
        elif self.module.name == "cardio":
            return self._check_cardio_condition(user, condition)
        elif self.module.name == "nutrition":
            return self._check_nutrition_condition(user, condition)
        elif self.module.name == "consistency":
            return self._check_consistency_condition(user, condition)
        elif self.module.name == "social":
            return self._check_social_condition(user, condition)
        elif self.module.name == "milestone":
            return self._check_milestone_condition(user, condition)

        return False

    def _check_strength_condition(self, user, condition):
        """检查力量训练条件"""
        from .fitness_models import EnhancedExerciseWeightRecord, EnhancedFitnessStrengthProfile

        if "total_1rm" in condition:
            try:
                profile = EnhancedFitnessStrengthProfile.objects.get(user=user)
                return (profile.total_1rm or 0) >= condition["total_1rm"]
            except EnhancedFitnessStrengthProfile.DoesNotExist:
                return False

        if "exercise_count" in condition:
            count = EnhancedExerciseWeightRecord.objects.filter(user=user).count()
            return count >= condition["exercise_count"]

        if "max_weight" in condition:
            exercise_type = condition.get("exercise_type", "squat")
            max_record = (
                EnhancedExerciseWeightRecord.objects.filter(user=user, exercise_type=exercise_type).order_by("-weight").first()
            )

            if max_record:
                return max_record.weight >= condition["max_weight"]

        return False

    def _check_cardio_condition(self, user, condition):
        """检查有氧运动条件"""
        from .fitness_models import EnhancedFitnessWorkoutSession

        if "total_cardio_duration" in condition:
            total_duration = (
                EnhancedFitnessWorkoutSession.objects.filter(user=user, workout_type="cardio").aggregate(
                    total=models.Sum("duration_minutes")
                )["total"]
                or 0
            )

            return total_duration >= condition["total_cardio_duration"]

        if "cardio_sessions" in condition:
            count = EnhancedFitnessWorkoutSession.objects.filter(user=user, workout_type="cardio").count()
            return count >= condition["cardio_sessions"]

        return False

    def _check_nutrition_condition(self, user, condition):
        """检查营养管理条件"""
        from .fitness_models import MealLog, WeightTracking

        if "meal_logs" in condition:
            count = MealLog.objects.filter(user=user, is_completed=True).count()
            return count >= condition["meal_logs"]

        if "weight_records" in condition:
            count = WeightTracking.objects.filter(user=user).count()
            return count >= condition["weight_records"]

        return False

    def _check_consistency_condition(self, user, condition):
        """检查连续性条件"""
        from .fitness_models import EnhancedFitnessStrengthProfile

        if "streak_days" in condition:
            try:
                profile = EnhancedFitnessStrengthProfile.objects.get(user=user)
                return profile.current_streak >= condition["streak_days"]
            except EnhancedFitnessStrengthProfile.DoesNotExist:
                return False

        if "longest_streak" in condition:
            try:
                profile = EnhancedFitnessStrengthProfile.objects.get(user=user)
                return profile.longest_streak >= condition["longest_streak"]
            except EnhancedFitnessStrengthProfile.DoesNotExist:
                return False

        return False

    def _check_social_condition(self, user, condition):
        """检查社交互动条件"""
        if "shared_achievements" in condition:
            from .legacy_models import UserFitnessAchievement

            count = UserFitnessAchievement.objects.filter(user=user, is_shared=True).count()
            return count >= condition["shared_achievements"]

        return False

    def _check_milestone_condition(self, user, condition):
        """检查里程碑条件"""
        if "total_workouts" in condition:
            from .fitness_models import EnhancedFitnessWorkoutSession

            count = EnhancedFitnessWorkoutSession.objects.filter(user=user).count()
            return count >= condition["total_workouts"]

        if "achievements_earned" in condition:
            from .legacy_models import UserFitnessAchievement

            count = UserFitnessAchievement.objects.filter(user=user).count()
            return count >= condition["achievements_earned"]

        return False


class EnhancedUserFitnessAchievement(models.Model):
    """增强版用户健身成就模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    achievement = models.ForeignKey(EnhancedFitnessAchievement, on_delete=models.CASCADE, verbose_name="成就")

    # 进度追踪
    progress = models.FloatField(default=0.0, verbose_name="完成进度")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    # 徽章管理
    is_equipped = models.BooleanField(default=False, verbose_name="是否佩戴")
    equipped_at = models.DateTimeField(null=True, blank=True, verbose_name="佩戴时间")

    # 社交功能
    is_shared = models.BooleanField(default=False, verbose_name="是否已分享")
    shared_at = models.DateTimeField(null=True, blank=True, verbose_name="分享时间")

    # 额外数据
    unlock_data = models.JSONField(default=dict, verbose_name="解锁数据")
    notes = models.TextField(blank=True, null=True, verbose_name="个人备注")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ["user", "achievement"]
        verbose_name = "用户健身成就"
        verbose_name_plural = "用户健身成就"
        ordering = ["-completed_at", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_completed"]),
            models.Index(fields=["user", "is_equipped"]),
            models.Index(fields=["achievement", "is_completed"]),
        ]

    def __str__(self):
        status = "已完成" if self.is_completed else f"进度 {self.progress:.1f}%"
        return f"{self.user.username} - {self.achievement.name} ({status})"

    def mark_completed(self):
        """标记为完成"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.progress = 100.0
            self.save()

            # 更新成就统计
            self.achievement.total_earned += 1
            self.achievement.save(update_fields=["total_earned"])

    def equip_badge(self):
        """佩戴徽章"""
        if self.is_completed and not self.is_equipped:
            # 取消其他同模块的佩戴状态
            from .legacy_models import UserFitnessAchievement

            UserFitnessAchievement.objects.filter(
                user=self.user, achievement__module=self.achievement.module, is_equipped=True
            ).update(is_equipped=False, equipped_at=None)

            # 佩戴当前徽章
            self.is_equipped = True
            self.equipped_at = timezone.now()
            self.save()

            # 更新用户档案中的选中徽章
            from .fitness_models import FitnessUserProfile

            profile, created = FitnessUserProfile.objects.get_or_create(user=self.user)
            if not hasattr(profile, "selected_badges"):
                profile.selected_badges = {}

            profile.selected_badges[self.achievement.module.name] = {
                "achievement_id": self.achievement.id,
                "achievement_name": self.achievement.name,
                "badge_color": self.achievement.badge_color,
                "icon": self.achievement.icon,
                "level": self.achievement.level,
                "equipped_at": self.equipped_at.isoformat(),
            }
            profile.save()

    def unequip_badge(self):
        """取消佩戴徽章"""
        if self.is_equipped:
            self.is_equipped = False
            self.equipped_at = None
            self.save()

            # 从用户档案中移除
            from .fitness_models import FitnessUserProfile

            try:
                profile = FitnessUserProfile.objects.get(user=self.user)
                if hasattr(profile, "selected_badges") and profile.selected_badges:
                    if self.achievement.module.name in profile.selected_badges:
                        del profile.selected_badges[self.achievement.module.name]
                        profile.save()
            except FitnessUserProfile.DoesNotExist:
                pass


class FitnessAchievementCategory(models.Model):
    """成就分类模型"""

    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(verbose_name="分类描述")
    icon = models.CharField(max_length=50, default="fas fa-star", verbose_name="分类图标")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="分类颜色")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        verbose_name = "成就分类"
        verbose_name_plural = "成就分类"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class UserBadgeShowcase(models.Model):
    """用户徽章展示模型"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="用户")

    # 展示设置
    showcase_layout = models.CharField(max_length=20, default="grid", verbose_name="展示布局")
    max_display_count = models.IntegerField(default=6, verbose_name="最大展示数量")

    # 选中的徽章
    primary_badge = models.ForeignKey(
        EnhancedUserFitnessAchievement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_showcase",
        verbose_name="主要徽章",
    )

    featured_badges = models.ManyToManyField(
        EnhancedUserFitnessAchievement, blank=True, related_name="featured_showcase", verbose_name="精选徽章"
    )

    # 展示偏好
    show_progress_badges = models.BooleanField(default=False, verbose_name="显示进度徽章")
    show_rare_only = models.BooleanField(default=False, verbose_name="仅显示稀有徽章")
    auto_update = models.BooleanField(default=True, verbose_name="自动更新展示")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户徽章展示"
        verbose_name_plural = "用户徽章展示"

    def __str__(self):
        return f"{self.user.username} - 徽章展示"

    def get_display_badges(self):
        """获取要展示的徽章"""
        badges = []

        # 添加主要徽章
        if self.primary_badge and self.primary_badge.is_completed:
            badges.append(self.primary_badge)

        # 添加精选徽章
        featured = self.featured_badges.filter(is_completed=True)
        badges.extend(featured[: self.max_display_count - len(badges)])

        # 如果还有空位，自动填充最新的徽章
        if len(badges) < self.max_display_count and self.auto_update:
            existing_ids = [badge.id for badge in badges]
            additional = (
                EnhancedUserFitnessAchievement.objects.filter(user=self.user, is_completed=True)
                .exclude(id__in=existing_ids)
                .order_by("-completed_at")[: self.max_display_count - len(badges)]
            )

            badges.extend(additional)

        return badges[: self.max_display_count]


class AchievementUnlockLog(models.Model):
    """成就解锁日志"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    achievement = models.ForeignKey(EnhancedFitnessAchievement, on_delete=models.CASCADE, verbose_name="成就")
    trigger_event = models.CharField(max_length=100, verbose_name="触发事件")
    unlock_data = models.JSONField(default=dict, verbose_name="解锁数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="解锁时间")

    class Meta:
        verbose_name = "成就解锁日志"
        verbose_name_plural = "成就解锁日志"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 解锁了 {self.achievement.name}"
