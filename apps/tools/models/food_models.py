from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class FoodRandomizer(models.Model):
    """食物随机选择器模型"""

    MEAL_TYPE_CHOICES = [
        ("breakfast", "早餐"),
        ("lunch", "午餐"),
        ("dinner", "晚餐"),
        ("snack", "夜宵"),
    ]

    CUISINE_CHOICES = [
        ("chinese", "中餐"),
        ("western", "西餐"),
        ("japanese", "日料"),
        ("korean", "韩料"),
        ("thai", "泰餐"),
        ("indian", "印度菜"),
        ("italian", "意大利菜"),
        ("french", "法餐"),
        ("mexican", "墨西哥菜"),
        ("mixed", "混合"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, verbose_name="餐种")
    cuisine_preference = models.CharField(max_length=20, choices=CUISINE_CHOICES, default="mixed", verbose_name="菜系偏好")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "食物随机选择器"
        verbose_name_plural = "食物随机选择器"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()}"


class FoodItem(models.Model):
    """食物项目模型"""

    MEAL_TYPE_CHOICES = [
        ("breakfast", "早餐"),
        ("lunch", "午餐"),
        ("dinner", "晚餐"),
        ("snack", "夜宵"),
    ]

    CUISINE_CHOICES = [
        ("chinese", "中餐"),
        ("western", "西餐"),
        ("japanese", "日料"),
        ("korean", "韩料"),
        ("thai", "泰餐"),
        ("indian", "印度菜"),
        ("italian", "意大利菜"),
        ("french", "法餐"),
        ("mexican", "墨西哥菜"),
        ("mixed", "混合"),
    ]

    DIFFICULTY_CHOICES = [
        ("easy", "简单"),
        ("medium", "中等"),
        ("hard", "困难"),
    ]

    name = models.CharField(max_length=200, verbose_name="食物名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    meal_types = models.JSONField(default=list, verbose_name="适用餐种")
    cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES, verbose_name="菜系")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="medium", verbose_name="制作难度")
    cooking_time = models.IntegerField(default=30, verbose_name="制作时间(分钟)")
    ingredients = models.JSONField(default=list, verbose_name="主要食材")
    tags = models.JSONField(default=list, verbose_name="标签")
    image_url = models.URLField(blank=True, null=True, verbose_name="图片链接")
    recipe_url = models.URLField(blank=True, null=True, verbose_name="食谱链接")
    popularity_score = models.FloatField(default=0.0, verbose_name="受欢迎度")

    # 营养信息
    calories = models.IntegerField(default=0, verbose_name="卡路里(千卡)")
    protein = models.FloatField(default=0.0, verbose_name="蛋白质(克)")
    fat = models.FloatField(default=0.0, verbose_name="脂肪(克)")
    carbohydrates = models.FloatField(default=0.0, verbose_name="碳水化合物(克)")
    fiber = models.FloatField(default=0.0, verbose_name="膳食纤维(克)")
    sugar = models.FloatField(default=0.0, verbose_name="糖分(克)")
    sodium = models.FloatField(default=0.0, verbose_name="钠(毫克)")

    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "食物项目"
        verbose_name_plural = "食物项目"
        ordering = ["-popularity_score", "name"]

    def __str__(self):
        return self.name

    def get_meal_types_display(self):
        return ", ".join([dict(FoodRandomizer.MEAL_TYPE_CHOICES)[meal_type] for meal_type in self.meal_types])


class FoodRandomizationSession(models.Model):
    """食物随机选择会话模型"""

    STATUS_CHOICES = [
        ("active", "进行中"),
        ("paused", "已暂停"),
        ("completed", "已完成"),
        ("cancelled", "已取消"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    meal_type = models.CharField(max_length=20, choices=FoodRandomizer.MEAL_TYPE_CHOICES, verbose_name="餐种")
    cuisine_preference = models.CharField(max_length=20, choices=FoodRandomizer.CUISINE_CHOICES, verbose_name="菜系偏好")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="状态")

    # 随机过程数据
    animation_duration = models.IntegerField(default=3000, verbose_name="动画时长(毫秒)")
    total_cycles = models.IntegerField(default=0, verbose_name="总循环次数")
    current_cycle = models.IntegerField(default=0, verbose_name="当前循环次数")

    # 结果
    selected_food = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="选中的食物")
    alternative_foods = models.JSONField(default=list, verbose_name="备选食物")

    # 时间戳
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="开始时间")
    paused_at = models.DateTimeField(null=True, blank=True, verbose_name="暂停时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    class Meta:
        verbose_name = "食物随机选择会话"
        verbose_name_plural = "食物随机选择会话"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} - {self.get_meal_type_display()} - {self.get_status_display()}"

    def get_duration(self):
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.paused_at:
            return (self.paused_at - self.started_at).total_seconds()
        else:
            return (timezone.now() - self.started_at).total_seconds()


class FoodHistory(models.Model):
    """食物选择历史记录模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    session = models.ForeignKey(FoodRandomizationSession, on_delete=models.CASCADE, verbose_name="随机会话")
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, verbose_name="食物项目")
    meal_type = models.CharField(max_length=20, choices=FoodRandomizer.MEAL_TYPE_CHOICES, verbose_name="餐种")
    rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name="评分")
    feedback = models.TextField(blank=True, null=True, verbose_name="反馈")
    was_cooked = models.BooleanField(default=False, verbose_name="是否制作")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="选择时间")

    class Meta:
        verbose_name = "食物选择历史"
        verbose_name_plural = "食物选择历史"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.food_item.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class FoodPhotoBinding(models.Model):
    """食物照片绑定模型"""

    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, verbose_name="食物项目")
    photo_name = models.CharField(max_length=255, verbose_name="照片文件名")
    photo_url = models.URLField(verbose_name="照片URL")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")

    # 绑定质量评估
    accuracy_score = models.FloatField(default=0.0, verbose_name="准确度评分")
    binding_source = models.CharField(
        max_length=50,
        default="manual",
        verbose_name="绑定来源",
        choices=[
            ("manual", "手动绑定"),
            ("auto", "自动匹配"),
            ("ai", "AI推荐"),
        ],
    )

    class Meta:
        unique_together = ["food_item", "photo_name"]
        verbose_name = "食物照片绑定"
        verbose_name_plural = "食物照片绑定"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.food_item.name} -> {self.photo_name}"


class FoodPhotoBindingHistory(models.Model):
    """食物照片绑定历史记录模型"""

    ACTION_CHOICES = [
        ("create", "创建绑定"),
        ("update", "更新绑定"),
        ("delete", "删除绑定"),
    ]

    binding = models.ForeignKey(FoodPhotoBinding, on_delete=models.CASCADE, related_name="history", verbose_name="绑定关系")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="操作类型")
    old_photo_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="旧照片名")
    new_photo_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="新照片名")
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="操作者")
    performed_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")
    notes = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "绑定历史记录"
        verbose_name_plural = "绑定历史记录"
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.binding.food_item.name} - {self.get_action_display()} - {self.performed_at.strftime('%Y-%m-%d %H:%M')}"
