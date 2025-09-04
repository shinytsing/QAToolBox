from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class MuscleGroup(models.Model):
    """肌肉群模型"""

    name = models.CharField(max_length=50, unique=True, verbose_name="肌肉群名称")
    chinese_name = models.CharField(max_length=50, verbose_name="中文名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    anatomy_image = models.URLField(blank=True, null=True, verbose_name="解剖图片")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="标识颜色")

    class Meta:
        verbose_name = "肌肉群"
        verbose_name_plural = "肌肉群"
        ordering = ["name"]

    def __str__(self):
        return self.chinese_name


class BodyPart(models.Model):
    """身体部位模型"""

    PART_CHOICES = [
        ("chest", "胸部"),
        ("back", "背部"),
        ("shoulders", "肩部"),
        ("arms", "手臂"),
        ("legs", "腿部"),
        ("core", "核心"),
        ("glutes", "臀部"),
        ("calves", "小腿"),
        ("forearms", "前臂"),
        ("neck", "颈部"),
        ("full_body", "全身"),
    ]

    name = models.CharField(max_length=20, choices=PART_CHOICES, unique=True, verbose_name="部位名称")
    display_name = models.CharField(max_length=50, verbose_name="显示名称")
    description = models.TextField(blank=True, null=True, verbose_name="部位描述")
    muscle_groups = models.ManyToManyField(MuscleGroup, verbose_name="包含肌肉群")
    icon = models.CharField(max_length=50, default="fas fa-dumbbell", verbose_name="图标")
    color = models.CharField(max_length=7, default="#667eea", verbose_name="主题色")
    sort_order = models.IntegerField(default=0, verbose_name="排序")

    class Meta:
        verbose_name = "身体部位"
        verbose_name_plural = "身体部位"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.display_name


class Equipment(models.Model):
    """器械设备模型"""

    EQUIPMENT_TYPE_CHOICES = [
        ("barbell", "杠铃"),
        ("dumbbell", "哑铃"),
        ("cable", "绳索"),
        ("machine", "器械"),
        ("bodyweight", "自重"),
        ("kettlebell", "壶铃"),
        ("resistance_band", "弹力带"),
        ("medicine_ball", "药球"),
        ("suspension", "悬吊"),
        ("cardio", "有氧器械"),
        ("other", "其他"),
    ]

    name = models.CharField(max_length=100, verbose_name="器械名称")
    equipment_type = models.CharField(max_length=20, choices=EQUIPMENT_TYPE_CHOICES, verbose_name="器械类型")
    description = models.TextField(blank=True, null=True, verbose_name="器械描述")
    image_url = models.URLField(blank=True, null=True, verbose_name="器械图片")
    availability = models.CharField(max_length=20, default="common", verbose_name="常见程度")

    class Meta:
        verbose_name = "器械设备"
        verbose_name_plural = "器械设备"
        ordering = ["equipment_type", "name"]

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """动作模型 - 增强版"""

    DIFFICULTY_CHOICES = [
        ("beginner", "初学者"),
        ("intermediate", "中级"),
        ("advanced", "高级"),
        ("expert", "专家"),
    ]

    EXERCISE_TYPE_CHOICES = [
        ("compound", "复合动作"),
        ("isolation", "孤立动作"),
        ("cardio", "有氧运动"),
        ("flexibility", "柔韧性"),
        ("balance", "平衡性"),
        ("plyometric", "爆发力"),
        ("isometric", "等长收缩"),
    ]

    # 基本信息
    name = models.CharField(max_length=200, verbose_name="动作名称")
    english_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="英文名称")
    alternative_names = models.JSONField(default=list, verbose_name="别名")

    # 分类信息
    body_parts = models.ManyToManyField(BodyPart, verbose_name="目标部位")
    primary_muscles = models.ManyToManyField(MuscleGroup, related_name="primary_exercises", verbose_name="主要肌肉群")
    secondary_muscles = models.ManyToManyField(
        MuscleGroup, related_name="secondary_exercises", blank=True, verbose_name="辅助肌肉群"
    )

    # 动作属性
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES, verbose_name="动作类型")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="难度等级")
    equipment = models.ManyToManyField(Equipment, blank=True, verbose_name="所需器械")

    # 动作描述
    description = models.TextField(verbose_name="动作描述")
    instructions = models.TextField(verbose_name="动作要领")
    setup_instructions = models.TextField(blank=True, null=True, verbose_name="准备动作")
    execution_steps = models.JSONField(default=list, verbose_name="执行步骤")

    # 技术要点
    form_cues = models.JSONField(default=list, verbose_name="技术提示")
    common_mistakes = models.JSONField(default=list, verbose_name="常见错误")
    safety_tips = models.JSONField(default=list, verbose_name="安全提示")

    # 训练参数
    recommended_sets = models.CharField(max_length=20, default="3-4", verbose_name="推荐组数")
    recommended_reps = models.CharField(max_length=20, default="8-12", verbose_name="推荐次数")
    recommended_rest = models.CharField(max_length=20, default="60-90s", verbose_name="组间休息")
    tempo = models.CharField(max_length=20, blank=True, null=True, verbose_name="动作节奏")

    # 媒体资源
    demonstration_video = models.URLField(blank=True, null=True, verbose_name="示范视频")
    form_images = models.JSONField(default=list, verbose_name="动作图片")
    animation_gif = models.URLField(blank=True, null=True, verbose_name="动作动图")

    # 变式和进阶
    prerequisites = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="advanced_versions", verbose_name="前置动作"
    )
    variations = models.JSONField(default=list, verbose_name="动作变式")
    progressions = models.JSONField(default=list, verbose_name="进阶动作")
    regressions = models.JSONField(default=list, verbose_name="简化动作")

    # 统计和评分
    popularity_score = models.FloatField(default=0.0, verbose_name="受欢迎度")
    effectiveness_rating = models.FloatField(default=0.0, verbose_name="有效性评分")
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    average_rating = models.FloatField(default=0.0, verbose_name="平均评分")

    # 标签和分类
    tags = models.JSONField(default=list, verbose_name="标签")
    categories = models.JSONField(default=list, verbose_name="分类标签")

    # 状态
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_featured = models.BooleanField(default=False, verbose_name="是否精选")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="创建者")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "健身动作"
        verbose_name_plural = "健身动作"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["difficulty", "exercise_type"]),
            models.Index(fields=["popularity_score"]),
            models.Index(fields=["is_active", "is_featured"]),
        ]

    def __str__(self):
        return self.name

    def get_primary_body_part(self):
        """获取主要训练部位"""
        return self.body_parts.first()

    def get_difficulty_color(self):
        """获取难度对应的颜色"""
        colors = {"beginner": "#28a745", "intermediate": "#ffc107", "advanced": "#fd7e14", "expert": "#dc3545"}
        return colors.get(self.difficulty, "#6c757d")

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])

    def get_equipment_list(self):
        """获取器械列表"""
        return list(self.equipment.values_list("name", flat=True))

    def get_muscle_groups_display(self):
        """获取肌肉群显示文本"""
        primary = list(self.primary_muscles.values_list("chinese_name", flat=True))
        secondary = list(self.secondary_muscles.values_list("chinese_name", flat=True))

        result = {"primary": primary, "secondary": secondary}
        return result


class ExerciseRating(models.Model):
    """动作评分模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="动作")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="评分(1-5)")
    difficulty_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True, verbose_name="难度评分(1-5)"
    )
    effectiveness_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True, verbose_name="有效性评分(1-5)"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="评价")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评价时间")

    class Meta:
        unique_together = ["user", "exercise"]
        verbose_name = "动作评分"
        verbose_name_plural = "动作评分"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} 对 {self.exercise.name} 评分 {self.rating}星"


class UserExercisePreference(models.Model):
    """用户动作偏好模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="动作")

    # 偏好设置
    is_favorite = models.BooleanField(default=False, verbose_name="是否收藏")
    is_disliked = models.BooleanField(default=False, verbose_name="是否不喜欢")
    is_mastered = models.BooleanField(default=False, verbose_name="是否已掌握")

    # 个人设置
    personal_notes = models.TextField(blank=True, null=True, verbose_name="个人笔记")
    custom_sets = models.CharField(max_length=20, blank=True, null=True, verbose_name="自定义组数")
    custom_reps = models.CharField(max_length=20, blank=True, null=True, verbose_name="自定义次数")
    custom_rest = models.CharField(max_length=20, blank=True, null=True, verbose_name="自定义休息")

    # 统计
    times_performed = models.IntegerField(default=0, verbose_name="执行次数")
    last_performed = models.DateTimeField(null=True, blank=True, verbose_name="最后执行时间")
    personal_best = models.JSONField(default=dict, verbose_name="个人最佳记录")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        unique_together = ["user", "exercise"]
        verbose_name = "用户动作偏好"
        verbose_name_plural = "用户动作偏好"
        ordering = ["-updated_at"]

    def __str__(self):
        status = []
        if self.is_favorite:
            status.append("收藏")
        if self.is_mastered:
            status.append("已掌握")
        status_str = f"({', '.join(status)})" if status else ""
        return f"{self.user.username} - {self.exercise.name} {status_str}"


class WorkoutTemplate(models.Model):
    """训练模板模型"""

    TEMPLATE_TYPE_CHOICES = [
        ("strength", "力量训练"),
        ("cardio", "有氧训练"),
        ("hiit", "HIIT训练"),
        ("circuit", "循环训练"),
        ("bodyweight", "自重训练"),
        ("flexibility", "柔韧性训练"),
        ("mixed", "混合训练"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "初学者"),
        ("intermediate", "中级"),
        ("advanced", "高级"),
    ]

    # 基本信息
    name = models.CharField(max_length=200, verbose_name="模板名称")
    description = models.TextField(verbose_name="模板描述")
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES, verbose_name="模板类型")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, verbose_name="难度等级")

    # 目标设置
    target_body_parts = models.ManyToManyField(BodyPart, verbose_name="目标部位")
    target_goals = models.JSONField(default=list, verbose_name="训练目标")
    estimated_duration = models.IntegerField(verbose_name="预计时长(分钟)")

    # 模板内容
    exercises = models.ManyToManyField(Exercise, through="TemplateExercise", verbose_name="包含动作")
    warm_up_exercises = models.JSONField(default=list, verbose_name="热身动作")
    cool_down_exercises = models.JSONField(default=list, verbose_name="放松动作")

    # 使用统计
    usage_count = models.IntegerField(default=0, verbose_name="使用次数")
    average_rating = models.FloatField(default=0.0, verbose_name="平均评分")

    # 状态和权限
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    is_official = models.BooleanField(default=False, verbose_name="是否官方模板")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "训练模板"
        verbose_name_plural = "训练模板"
        ordering = ["-usage_count", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=["usage_count"])


class TemplateExercise(models.Model):
    """模板动作关联模型"""

    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, verbose_name="训练模板")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, verbose_name="动作")

    # 训练参数
    sets = models.CharField(max_length=20, verbose_name="组数")
    reps = models.CharField(max_length=20, verbose_name="次数")
    rest_time = models.CharField(max_length=20, verbose_name="休息时间")
    weight_percentage = models.CharField(max_length=20, blank=True, null=True, verbose_name="重量百分比")

    # 排序和分组
    exercise_order = models.IntegerField(verbose_name="动作顺序")
    superset_group = models.CharField(max_length=10, blank=True, null=True, verbose_name="超级组")
    circuit_group = models.CharField(max_length=10, blank=True, null=True, verbose_name="循环组")

    # 备注
    notes = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "模板动作"
        verbose_name_plural = "模板动作"
        ordering = ["exercise_order"]
        unique_together = ["template", "exercise", "exercise_order"]

    def __str__(self):
        return f"{self.template.name} - {self.exercise.name} ({self.sets}x{self.reps})"
