from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone


class VanityWealth(models.Model):
    """虚拟财富模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    virtual_wealth = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name="虚拟财富")
    code_lines = models.IntegerField(default=0, verbose_name="代码行数")
    page_views = models.IntegerField(default=0, verbose_name="网站访问量")
    donations = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="赞助金额")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")

    class Meta:
        verbose_name = "虚拟财富"
        verbose_name_plural = "虚拟财富"

    def __str__(self):
        return f"{self.user.username} - 虚拟财富: {self.virtual_wealth}"

    def calculate_wealth(self):
        """计算虚拟财富"""
        from decimal import Decimal

        code_wealth = Decimal(str(self.code_lines * 0.01))
        page_wealth = Decimal(str(self.page_views * 0.001))
        donation_wealth = Decimal(str(self.donations))
        self.virtual_wealth = code_wealth + page_wealth + donation_wealth
        return self.virtual_wealth


class SinPoints(models.Model):
    """罪恶积分模型"""

    ACTION_CHOICES = [
        ("code_line", "提交代码行"),
        ("reject_ai", "拒绝AI补全"),
        ("deep_work", "深度工作"),
        ("donation", "收到赞助"),
        ("manual_code", "手写代码"),
        ("refactor", "重构代码"),
        ("debug", "调试代码"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="行为类型")
    points_earned = models.IntegerField(verbose_name="获得积分")
    metadata = models.JSONField(default=dict, verbose_name="元数据")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="获得时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "罪恶积分"
        verbose_name_plural = "罪恶积分"

    def __str__(self):
        return f"{self.user.username} - {self.get_action_type_display()} - {self.points_earned}积分"


class Sponsor(models.Model):
    """赞助者模型"""

    EFFECT_CHOICES = [
        ("golden-bling", "金色闪耀"),
        ("diamond-sparkle", "钻石闪烁"),
        ("platinum-glow", "白金光芒"),
        ("silver-shine", "银色光辉"),
    ]

    name = models.CharField(max_length=200, verbose_name="赞助者姓名")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="赞助金额")
    message = models.TextField(blank=True, null=True, verbose_name="赞助留言")
    effect = models.CharField(max_length=20, choices=EFFECT_CHOICES, default="golden-bling", verbose_name="特效类型")
    is_anonymous = models.BooleanField(default=False, verbose_name="是否匿名")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="赞助时间")

    class Meta:
        ordering = ["-amount", "-created_at"]
        verbose_name = "赞助者"
        verbose_name_plural = "赞助者"

    def __str__(self):
        display_name = "匿名土豪" if self.is_anonymous else self.name
        return f"{display_name} - {self.amount}元"


class VanityTask(models.Model):
    """欲望驱动待办任务模型"""

    TASK_TYPE_CHOICES = [
        ("code_refactor", "代码重构"),
        ("bug_fix", "修复Bug"),
        ("feature_dev", "功能开发"),
        ("blog_write", "写技术博客"),
        ("code_review", "代码审查"),
        ("testing", "测试编写"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=200, verbose_name="任务标题")
    description = models.TextField(blank=True, null=True, verbose_name="任务描述")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, verbose_name="任务类型")
    difficulty = models.IntegerField(default=1, verbose_name="难度等级(1-10)")
    reward_value = models.IntegerField(default=0, verbose_name="奖励价值")
    reward_description = models.CharField(max_length=200, verbose_name="奖励描述")
    is_completed = models.BooleanField(default=False, verbose_name="是否完成")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "欲望任务"
        verbose_name_plural = "欲望任务"

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def calculate_reward(self):
        """根据难度计算奖励"""
        self.reward_value = self.difficulty * 10
        return self.reward_value


class BasedDevAvatar(models.Model):
    """反程序员形象模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    avatar_image = models.ImageField(upload_to="vanity_avatars/", verbose_name="头像图片")
    code_snippet = models.TextField(verbose_name="代码片段")
    caption = models.CharField(max_length=500, verbose_name="配文")
    is_public = models.BooleanField(default=True, verbose_name="是否公开")
    likes_count = models.IntegerField(default=0, verbose_name="点赞数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "反程序员形象"
        verbose_name_plural = "反程序员形象"

    def __str__(self):
        return f"{self.user.username} - {self.caption[:50]}"


class DesireDashboard(models.Model):
    """欲望仪表盘模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    current_desire_level = models.IntegerField(default=50, verbose_name="当前欲望浓度")
    total_desires = models.IntegerField(default=0, verbose_name="总欲望数")
    fulfilled_desires = models.IntegerField(default=0, verbose_name="已满足欲望数")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")

    class Meta:
        verbose_name = "欲望仪表盘"
        verbose_name_plural = "欲望仪表盘"

    def __str__(self):
        return f"{self.user.username} - 欲望浓度: {self.current_desire_level}%"


class DesireItem(models.Model):
    """欲望项目模型"""

    DESIRE_TYPE_CHOICES = [
        ("material", "物质欲望"),
        ("social", "社交欲望"),
        ("escape", "逃避欲望"),
        ("achievement", "成就欲望"),
        ("recognition", "认可欲望"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    desire_type = models.CharField(max_length=20, choices=DESIRE_TYPE_CHOICES, verbose_name="欲望类型")
    title = models.CharField(max_length=200, verbose_name="欲望标题")
    description = models.TextField(blank=True, null=True, verbose_name="欲望描述")
    intensity = models.IntegerField(default=3, verbose_name="欲望强度(1-5)")
    is_fulfilled = models.BooleanField(default=False, verbose_name="是否已满足")
    fulfillment_condition = models.TextField(blank=True, null=True, verbose_name="满足条件")
    fulfillment_image_url = models.URLField(blank=True, null=True, verbose_name="兑现图片URL")
    ai_generated_image = models.TextField(blank=True, null=True, verbose_name="AI生成图片描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    fulfilled_at = models.DateTimeField(null=True, blank=True, verbose_name="满足时间")

    class Meta:
        ordering = ["-intensity", "-created_at"]
        verbose_name = "欲望项目"
        verbose_name_plural = "欲望项目"

    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.get_intensity_stars()})"

    def get_intensity_stars(self):
        """获取强度星级显示"""
        return "★" * self.intensity + "☆" * (5 - self.intensity)


class DesireFulfillment(models.Model):
    """欲望兑现记录模型"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    desire = models.ForeignKey(DesireItem, on_delete=models.CASCADE, verbose_name="欲望项目")
    task_completed = models.CharField(max_length=200, verbose_name="完成任务")
    task_details = models.TextField(blank=True, null=True, verbose_name="任务详情")
    fulfillment_image_url = models.URLField(blank=True, null=True, verbose_name="兑现图片URL")
    ai_prompt = models.TextField(verbose_name="AI生成提示词")
    ai_generated_image = models.TextField(blank=True, null=True, verbose_name="AI生成图片")
    satisfaction_level = models.IntegerField(default=5, verbose_name="满足度(1-10)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="兑现时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "欲望兑现记录"
        verbose_name_plural = "欲望兑现记录"

    def __str__(self):
        return f"{self.user.username} - {self.desire.title} 兑现记录"
