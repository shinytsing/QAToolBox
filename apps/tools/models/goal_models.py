from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Index, Q
import random
import json
from datetime import timedelta


class LifeGoal(models.Model):
    """生活目标模型"""

    GOAL_TYPE_CHOICES = [
        ("career", "职业发展"),
        ("health", "健康生活"),
        ("relationship", "人际关系"),
        ("learning", "学习成长"),
        ("financial", "财务目标"),
        ("personal", "个人成长"),
        ("travel", "旅行探索"),
        ("hobby", "兴趣爱好"),
    ]

    PRIORITY_CHOICES = [
        ("low", "低"),
        ("medium", "中"),
        ("high", "高"),
        ("urgent", "紧急"),
    ]

    STATUS_CHOICES = [
        ("not_started", "未开始"),
        ("in_progress", "进行中"),
        ("completed", "已完成"),
        ("paused", "暂停"),
        ("cancelled", "已取消"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户", db_index=True)
    title = models.CharField(max_length=200, verbose_name="目标标题")
    description = models.TextField(verbose_name="目标描述")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, verbose_name="目标类型")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium", verbose_name="优先级")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="not_started", verbose_name="状态")
    target_date = models.DateField(null=True, blank=True, verbose_name="目标日期")
    start_date = models.DateField(auto_now_add=True, verbose_name="开始日期")
    completed_date = models.DateField(null=True, blank=True, verbose_name="完成日期")
    progress = models.IntegerField(default=0, verbose_name="进度百分比")
    tags = models.JSONField(default=list, verbose_name="标签")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "生活目标"
        verbose_name_plural = "生活目标"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "goal_type"]),
            models.Index(fields=["status", "target_date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def update_progress(self, progress):
        """更新进度"""
        self.progress = min(100, max(0, progress))
        if self.progress >= 100:
            self.status = "completed"
            self.completed_date = timezone.now().date()
        elif self.progress > 0:
            self.status = "in_progress"
        self.save()

    def get_days_remaining(self):
        """获取剩余天数"""
        if not self.target_date:
            return None
        remaining = self.target_date - timezone.now().date()
        return max(0, remaining.days)

    def is_overdue(self):
        """检查是否逾期"""
        if not self.target_date:
            return False
        return self.target_date < timezone.now().date() and self.status != "completed"


class LifeGoalProgress(models.Model):
    """生活目标进度记录模型"""

    goal = models.ForeignKey(LifeGoal, on_delete=models.CASCADE, verbose_name="目标")
    progress_value = models.IntegerField(verbose_name="进度值")
    description = models.TextField(blank=True, verbose_name="进度描述")
    evidence = models.FileField(upload_to="goal_evidence/", blank=True, verbose_name="进度证据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="记录时间")

    class Meta:
        verbose_name = "目标进度记录"
        verbose_name_plural = "目标进度记录"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["goal", "created_at"]),
        ]

    def __str__(self):
        return f"{self.goal.title} - {self.progress_value}% - {self.created_at.date()}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 更新目标的进度
        self.goal.update_progress(self.progress_value)


class LifeGoalMilestone(models.Model):
    """生活目标里程碑模型"""

    goal = models.ForeignKey(LifeGoal, on_delete=models.CASCADE, verbose_name="目标")
    title = models.CharField(max_length=200, verbose_name="里程碑标题")
    description = models.TextField(blank=True, verbose_name="描述")
    target_date = models.DateField(verbose_name="目标日期")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_date = models.DateField(null=True, blank=True, verbose_name="完成日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "目标里程碑"
        verbose_name_plural = "目标里程碑"
        ordering = ["target_date"]
        indexes = [
            models.Index(fields=["goal", "is_completed"]),
            models.Index(fields=["target_date"]),
        ]

    def __str__(self):
        return f"{self.goal.title} - {self.title}"

    def mark_completed(self):
        """标记为完成"""
        self.is_completed = True
        self.completed_date = timezone.now().date()
        self.save()

    def is_overdue(self):
        """检查是否逾期"""
        return self.target_date < timezone.now().date() and not self.is_completed


class LifeStatistics(models.Model):
    """生活统计模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    date = models.DateField(verbose_name="统计日期")
    goal_count = models.IntegerField(default=0, verbose_name="目标数量")
    completed_goals = models.IntegerField(default=0, verbose_name="完成目标数")
    active_goals = models.IntegerField(default=0, verbose_name="活跃目标数")
    overdue_goals = models.IntegerField(default=0, verbose_name="逾期目标数")
    avg_progress = models.FloatField(default=0.0, verbose_name="平均进度")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "生活统计"
        verbose_name_plural = "生活统计"
        unique_together = ["user", "date"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.date} - 统计"


class UserAchievement(models.Model):
    """用户成就模型"""

    ACHIEVEMENT_TYPE_CHOICES = [
        ("goal_completion", "目标完成"),
        ("streak", "连续记录"),
        ("milestone", "里程碑"),
        ("social", "社交互动"),
        ("learning", "学习成长"),
        ("health", "健康生活"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPE_CHOICES, verbose_name="成就类型")
    title = models.CharField(max_length=200, verbose_name="成就标题")
    description = models.TextField(verbose_name="成就描述")
    icon = models.CharField(max_length=50, blank=True, verbose_name="成就图标")
    points = models.IntegerField(default=0, verbose_name="成就点数")
    is_unlocked = models.BooleanField(default=False, verbose_name="是否解锁")
    unlocked_at = models.DateTimeField(null=True, blank=True, verbose_name="解锁时间")
    progress = models.IntegerField(default=0, verbose_name="进度")
    target = models.IntegerField(default=1, verbose_name="目标值")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户成就"
        verbose_name_plural = "用户成就"
        unique_together = ["user", "achievement_type", "title"]
        ordering = ["-unlocked_at", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_unlocked"]),
            models.Index(fields=["achievement_type", "is_unlocked"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def unlock(self):
        """解锁成就"""
        if not self.is_unlocked:
            self.is_unlocked = True
            self.unlocked_at = timezone.now()
            self.progress = self.target
            self.save()

    def update_progress(self, progress):
        """更新进度"""
        self.progress = min(self.target, progress)
        if self.progress >= self.target and not self.is_unlocked:
            self.unlock()
        else:
            self.save(update_fields=["progress"])

    def get_progress_percentage(self):
        """获取进度百分比"""
        return min(round((self.progress / self.target) * 100, 1), 100)
