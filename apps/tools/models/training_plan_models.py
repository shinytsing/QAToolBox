from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .exercise_library_models import BodyPart, Exercise


class TrainingPlanCategory(models.Model):
    """训练计划分类"""

    name = models.CharField(max_length=100, verbose_name="分类名称")
    description = models.TextField(blank=True, null=True, verbose_name="分类描述")
    icon = models.CharField(max_length=50, default="fas fa-dumbbell", verbose_name="分类图标")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="分类颜色")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    class Meta:
        verbose_name = "训练计划分类"
        verbose_name_plural = "训练计划分类"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class EnhancedTrainingPlan(models.Model):
    """增强版训练计划模型"""

    PLAN_TYPE_CHOICES = [
        ("strength", "力量训练"),
        ("hypertrophy", "增肌训练"),
        ("endurance", "耐力训练"),
        ("weight_loss", "减脂训练"),
        ("powerlifting", "力量举"),
        ("bodybuilding", "健美"),
        ("functional", "功能性训练"),
        ("rehabilitation", "康复训练"),
        ("sport_specific", "专项训练"),
        ("general_fitness", "综合健身"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "初学者"),
        ("intermediate", "中级"),
        ("advanced", "高级"),
        ("expert", "专家"),
    ]

    PLAN_STATUS_CHOICES = [
        ("draft", "草稿"),
        ("active", "激活"),
        ("completed", "已完成"),
        ("paused", "已暂停"),
        ("archived", "已归档"),
    ]

    VISIBILITY_CHOICES = [
        ("private", "私有"),
        ("shared", "分享"),
        ("public", "公开"),
        ("template", "模板"),
    ]

    # 基本信息
    name = models.CharField(max_length=200, verbose_name="计划名称")
    description = models.TextField(blank=True, null=True, verbose_name="计划描述")
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, verbose_name="计划类型")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="难度等级")
    category = models.ForeignKey(
        TrainingPlanCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="计划分类"
    )

    # 计划设置
    duration_weeks = models.IntegerField(default=8, verbose_name="计划周期(周)")
    training_days_per_week = models.IntegerField(default=3, verbose_name="每周训练天数")
    session_duration = models.IntegerField(default=60, verbose_name="单次训练时长(分钟)")

    # 目标设置
    target_body_parts = models.ManyToManyField(BodyPart, blank=True, verbose_name="目标部位")
    primary_goals = models.JSONField(default=list, verbose_name="主要目标")
    secondary_goals = models.JSONField(default=list, verbose_name="次要目标")

    # 计划内容
    week_schedule = models.JSONField(default=list, verbose_name="周安排")
    exercise_library = models.ManyToManyField(Exercise, blank=True, verbose_name="动作库")
    progression_scheme = models.JSONField(default=dict, verbose_name="进阶方案")

    # 用户和权限
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_plans", verbose_name="创建者")
    users = models.ManyToManyField(User, through="UserTrainingPlan", verbose_name="使用用户")

    # 状态管理
    status = models.CharField(max_length=20, choices=PLAN_STATUS_CHOICES, default="draft", verbose_name="计划状态")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="private", verbose_name="可见性")

    # 统计信息
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    completion_rate = models.FloatField(default=0.0, verbose_name="完成率")
    average_rating = models.FloatField(default=0.0, verbose_name="平均评分")
    total_ratings = models.IntegerField(default=0, verbose_name="评分总数")

    # 标签和搜索
    tags = models.JSONField(default=list, verbose_name="标签")
    search_keywords = models.TextField(blank=True, null=True, verbose_name="搜索关键词")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")

    class Meta:
        verbose_name = "训练计划"
        verbose_name_plural = "训练计划"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["creator", "status"]),
            models.Index(fields=["plan_type", "difficulty"]),
            models.Index(fields=["visibility", "published_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"

    def get_total_sessions(self):
        """获取总训练次数"""
        return self.duration_weeks * self.training_days_per_week

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])

    def publish(self):
        """发布计划"""
        if self.status == "draft":
            self.status = "active"
            self.published_at = timezone.now()
            self.save()

    def get_week_data(self, week_number):
        """获取指定周的训练数据"""
        if 0 <= week_number < len(self.week_schedule):
            return self.week_schedule[week_number]
        return None

    def calculate_completion_rate(self):
        """计算完成率"""
        user_plans = self.usertrainingplan_set.filter(status="completed")
        total_users = self.usertrainingplan_set.count()

        if total_users > 0:
            self.completion_rate = (user_plans.count() / total_users) * 100
            self.save(update_fields=["completion_rate"])

    def get_difficulty_color(self):
        """获取难度颜色"""
        colors = {"beginner": "#28a745", "intermediate": "#ffc107", "advanced": "#fd7e14", "expert": "#dc3545"}
        return colors.get(self.difficulty, "#6c757d")


class UserTrainingPlan(models.Model):
    """用户训练计划关联模型"""

    STATUS_CHOICES = [
        ("not_started", "未开始"),
        ("in_progress", "进行中"),
        ("completed", "已完成"),
        ("paused", "已暂停"),
        ("abandoned", "已放弃"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    plan = models.ForeignKey(EnhancedTrainingPlan, on_delete=models.CASCADE, verbose_name="训练计划")

    # 计划状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started", verbose_name="状态")
    current_week = models.IntegerField(default=0, verbose_name="当前周")
    current_day = models.IntegerField(default=0, verbose_name="当前天")

    # 进度追踪
    completed_sessions = models.IntegerField(default=0, verbose_name="已完成训练")
    total_sessions = models.IntegerField(default=0, verbose_name="总训练次数")
    completion_percentage = models.FloatField(default=0.0, verbose_name="完成百分比")

    # 个性化设置
    custom_settings = models.JSONField(default=dict, verbose_name="个人设置")
    modifications = models.JSONField(default=list, verbose_name="计划修改")

    # 时间管理
    start_date = models.DateField(null=True, blank=True, verbose_name="开始日期")
    target_end_date = models.DateField(null=True, blank=True, verbose_name="目标结束日期")
    actual_end_date = models.DateField(null=True, blank=True, verbose_name="实际结束日期")
    last_session_date = models.DateField(null=True, blank=True, verbose_name="最后训练日期")

    # 评价和反馈
    rating = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)], verbose_name="评分")
    feedback = models.TextField(blank=True, null=True, verbose_name="反馈")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="加入时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户训练计划"
        verbose_name_plural = "用户训练计划"
        unique_together = ["user", "plan"]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.get_status_display()})"

    def start_plan(self):
        """开始计划"""
        if self.status == "not_started":
            self.status = "in_progress"
            self.start_date = timezone.now().date()
            self.total_sessions = self.plan.get_total_sessions()

            # 计算目标结束日期
            from datetime import timedelta

            self.target_end_date = self.start_date + timedelta(weeks=self.plan.duration_weeks)

            self.save()

    def complete_session(self):
        """完成一次训练"""
        if self.status == "in_progress":
            self.completed_sessions += 1
            self.last_session_date = timezone.now().date()

            # 更新完成百分比
            if self.total_sessions > 0:
                self.completion_percentage = (self.completed_sessions / self.total_sessions) * 100

            # 检查是否完成整个计划
            if self.completed_sessions >= self.total_sessions:
                self.status = "completed"
                self.actual_end_date = timezone.now().date()

            self.save()

    def pause_plan(self):
        """暂停计划"""
        if self.status == "in_progress":
            self.status = "paused"
            self.save()

    def resume_plan(self):
        """恢复计划"""
        if self.status == "paused":
            self.status = "in_progress"
            self.save()


class TrainingSession(models.Model):
    """训练会话模型"""

    SESSION_TYPE_CHOICES = [
        ("scheduled", "计划训练"),
        ("makeup", "补训"),
        ("extra", "加练"),
        ("test", "测试"),
    ]

    STATUS_CHOICES = [
        ("planned", "计划中"),
        ("in_progress", "进行中"),
        ("completed", "已完成"),
        ("skipped", "已跳过"),
        ("cancelled", "已取消"),
    ]

    user_plan = models.ForeignKey(UserTrainingPlan, on_delete=models.CASCADE, verbose_name="用户计划")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default="scheduled", verbose_name="会话类型")

    # 会话信息
    week_number = models.IntegerField(verbose_name="周次")
    day_number = models.IntegerField(verbose_name="天数")
    session_name = models.CharField(max_length=200, verbose_name="会话名称")

    # 训练内容
    planned_exercises = models.JSONField(default=list, verbose_name="计划动作")
    actual_exercises = models.JSONField(default=list, verbose_name="实际动作")

    # 状态和时间
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned", verbose_name="状态")
    scheduled_date = models.DateField(verbose_name="计划日期")
    actual_date = models.DateField(null=True, blank=True, verbose_name="实际日期")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")

    # 训练数据
    duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="训练时长")
    calories_burned = models.IntegerField(null=True, blank=True, verbose_name="消耗卡路里")
    average_heart_rate = models.IntegerField(null=True, blank=True, verbose_name="平均心率")
    max_heart_rate = models.IntegerField(null=True, blank=True, verbose_name="最大心率")

    # 主观感受
    rpe_score = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 11)], verbose_name="RPE评分")
    energy_level = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)], verbose_name="精力水平")
    mood_score = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)], verbose_name="情绪评分")

    # 笔记和反馈
    pre_workout_notes = models.TextField(blank=True, null=True, verbose_name="训练前笔记")
    post_workout_notes = models.TextField(blank=True, null=True, verbose_name="训练后笔记")
    achievements = models.JSONField(default=list, verbose_name="训练成就")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "训练会话"
        verbose_name_plural = "训练会话"
        ordering = ["scheduled_date", "week_number", "day_number"]
        indexes = [
            models.Index(fields=["user_plan", "status"]),
            models.Index(fields=["scheduled_date"]),
        ]

    def __str__(self):
        return f"{self.user_plan.user.username} - {self.session_name} ({self.scheduled_date})"

    def start_session(self):
        """开始训练会话"""
        if self.status == "planned":
            self.status = "in_progress"
            self.start_time = timezone.now()
            self.actual_date = timezone.now().date()
            self.save()

    def complete_session(self):
        """完成训练会话"""
        if self.status == "in_progress":
            self.status = "completed"
            self.end_time = timezone.now()

            # 计算训练时长
            if self.start_time:
                duration = self.end_time - self.start_time
                self.duration_minutes = int(duration.total_seconds() / 60)

            self.save()

            # 更新用户计划进度
            self.user_plan.complete_session()


class ExerciseSet(models.Model):
    """动作组数模型"""

    SET_TYPE_CHOICES = [
        ("working", "正式组"),
        ("warmup", "热身组"),
        ("dropset", "递减组"),
        ("superset", "超级组"),
        ("rest_pause", "休息暂停"),
        ("cluster", "集群组"),
        ("amrap", "AMRAP"),
        ("failure", "力竭组"),
    ]

    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, verbose_name="训练会话")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="动作")

    # 组数信息
    set_number = models.IntegerField(verbose_name="组数")
    set_type = models.CharField(max_length=20, choices=SET_TYPE_CHOICES, default="working", verbose_name="组数类型")

    # 训练数据
    weight = models.FloatField(null=True, blank=True, verbose_name="重量(kg)")
    reps = models.IntegerField(null=True, blank=True, verbose_name="次数")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="持续时间(秒)")
    distance_meters = models.FloatField(null=True, blank=True, verbose_name="距离(米)")

    # 主观感受
    rpe = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 11)], verbose_name="RPE")
    difficulty = models.IntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)], verbose_name="难度感受")

    # 状态
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    is_personal_best = models.BooleanField(default=False, verbose_name="是否个人最佳")

    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name="备注")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "动作组数"
        verbose_name_plural = "动作组数"
        ordering = ["session", "exercise", "set_number"]

    def __str__(self):
        weight_str = f"{self.weight}kg" if self.weight else ""
        reps_str = f"{self.reps}次" if self.reps else ""
        return f"{self.exercise.name} - 第{self.set_number}组 {weight_str} {reps_str}"

    def get_volume(self):
        """计算训练量"""
        if self.weight and self.reps:
            return self.weight * self.reps
        return 0


class PlanLibrary(models.Model):
    """计划库模型"""

    LIBRARY_TYPE_CHOICES = [
        ("official", "官方计划"),
        ("community", "社区计划"),
        ("premium", "付费计划"),
        ("user_shared", "用户分享"),
    ]

    plan = models.OneToOneField(EnhancedTrainingPlan, on_delete=models.CASCADE, verbose_name="训练计划")
    library_type = models.CharField(max_length=20, choices=LIBRARY_TYPE_CHOICES, verbose_name="库类型")

    # 展示信息
    featured_image = models.URLField(blank=True, null=True, verbose_name="特色图片")
    preview_video = models.URLField(blank=True, null=True, verbose_name="预览视频")
    detailed_description = models.TextField(verbose_name="详细描述")

    # 适用人群
    target_audience = models.JSONField(default=list, verbose_name="目标人群")
    prerequisites = models.JSONField(default=list, verbose_name="前置条件")
    equipment_required = models.JSONField(default=list, verbose_name="所需器械")

    # 库管理
    is_featured = models.BooleanField(default=False, verbose_name="是否精选")
    is_trending = models.BooleanField(default=False, verbose_name="是否热门")
    is_new = models.BooleanField(default=True, verbose_name="是否新计划")

    # 统计
    view_count = models.IntegerField(default=0, verbose_name="浏览次数")
    download_count = models.IntegerField(default=0, verbose_name="下载次数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")

    # 管理信息
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="添加者")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")

    class Meta:
        verbose_name = "计划库"
        verbose_name_plural = "计划库"
        ordering = ["-is_featured", "-is_trending", "-added_at"]

    def __str__(self):
        return f"[{self.get_library_type_display()}] {self.plan.name}"

    def increment_view(self):
        """增加浏览次数"""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def increment_download(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=["download_count"])


class UserPlanCollection(models.Model):
    """用户计划收藏模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    plan = models.ForeignKey(EnhancedTrainingPlan, on_delete=models.CASCADE, verbose_name="训练计划")

    # 收藏信息
    collection_name = models.CharField(max_length=100, default="我的收藏", verbose_name="收藏夹名称")
    personal_notes = models.TextField(blank=True, null=True, verbose_name="个人备注")

    # 状态
    is_bookmarked = models.BooleanField(default=True, verbose_name="是否收藏")
    is_liked = models.BooleanField(default=False, verbose_name="是否点赞")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        verbose_name = "用户计划收藏"
        verbose_name_plural = "用户计划收藏"
        unique_together = ["user", "plan"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.plan.name}"
