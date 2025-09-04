from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_published = models.BooleanField(default=False, verbose_name="是否发布")

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments", verbose_name="文章")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者", default=1)
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_approved = models.BooleanField(default=True, verbose_name="是否审核通过")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} - {self.content[:50]}"


class Suggestion(models.Model):
    SUGGESTION_TYPE_CHOICES = [
        ("feature", "功能建议"),
        ("improvement", "改进建议"),
        ("bug", "Bug反馈"),
        ("other", "其他"),
    ]

    STATUS_CHOICES = [
        ("pending", "待处理"),
        ("reviewing", "审核中"),
        ("implemented", "已实现"),
        ("rejected", "已拒绝"),
    ]

    title = models.CharField(max_length=200, verbose_name="建议标题")
    content = models.TextField(verbose_name="建议内容")
    suggestion_type = models.CharField(
        max_length=20, choices=SUGGESTION_TYPE_CHOICES, default="feature", verbose_name="建议类型"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="处理状态")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="提交用户")
    user_name = models.CharField(max_length=100, blank=True, verbose_name="用户名称")
    user_email = models.EmailField(blank=True, verbose_name="用户邮箱")
    admin_response = models.TextField(blank=True, verbose_name="管理员回复")
    images = models.JSONField(default=list, blank=True, verbose_name="图片附件")
    videos = models.JSONField(default=list, blank=True, verbose_name="视频附件")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户建议"
        verbose_name_plural = "用户建议"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Feedback(models.Model):
    FEEDBACK_TYPE_CHOICES = [
        ("bug", "Bug反馈"),
        ("suggestion", "建议"),
        ("complaint", "投诉"),
        ("praise", "表扬"),
        ("question", "咨询"),
        ("other", "其他"),
    ]

    STATUS_CHOICES = [
        ("pending", "待处理"),
        ("processed", "已处理"),
        ("resolved", "已解决"),
        ("closed", "已关闭"),
    ]

    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES, verbose_name="反馈类型")
    content = models.TextField(verbose_name="反馈内容")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="处理状态")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="反馈用户")
    user_name = models.CharField(max_length=100, blank=True, verbose_name="用户名称")
    user_email = models.EmailField(blank=True, verbose_name="用户邮箱")
    admin_response = models.TextField(blank=True, verbose_name="管理员回复")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户反馈"
        verbose_name_plural = "用户反馈"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.content[:50]}"


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ("low", "低"),
        ("normal", "正常"),
        ("high", "高"),
        ("urgent", "紧急"),
    ]

    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("published", "已发布"),
        ("archived", "已归档"),
    ]

    title = models.CharField(max_length=200, verbose_name="公告标题")
    content = models.TextField(verbose_name="公告内容")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="normal", verbose_name="优先级")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name="状态")
    is_popup = models.BooleanField(default=False, verbose_name="是否弹窗显示")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="结束时间")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="创建者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "系统公告"
        verbose_name_plural = "系统公告"
        ordering = ["-priority", "-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

    def is_active(self):
        """判断公告是否在有效期内"""
        now = timezone.now()
        if self.start_time and now < self.start_time:
            return False
        if self.end_time and now > self.end_time:
            return False
        return True


class AILink(models.Model):
    CATEGORY_CHOICES = [
        ("ai_tools", "AI工具"),
        ("coding", "编程开发"),
        ("design", "设计创意"),
        ("productivity", "效率办公"),
        ("learning", "学习教育"),
        ("entertainment", "娱乐休闲"),
        ("other", "其他"),
    ]

    name = models.CharField(max_length=100, verbose_name="网站名称")
    url = models.URLField(verbose_name="网站链接")
    description = models.TextField(blank=True, verbose_name="网站描述")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="ai_tools", verbose_name="分类")
    icon_url = models.URLField(blank=True, verbose_name="图标URL")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    click_count = models.IntegerField(default=0, verbose_name="点击次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "AI友情链接"
        verbose_name_plural = "AI友情链接"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.name

    def get_icon_url(self):
        """获取图标URL"""
        if self.icon_url:
            return self.icon_url
        # 如果没有自定义图标，可以使用favicon服务
        return f"https://www.google.com/s2/favicons?domain={self.url}"


class FeatureAccess(models.Model):
    """功能入口访问控制模型"""

    FEATURE_CHOICES = [
        # 工具类功能
        ("food_randomizer", "食物随机器"),
        ("meditation_guide", "冥想指南"),
        ("guitar_training", "吉他训练"),
        ("life_diary", "生活日记"),
        ("life_goals", "人生目标"),
        ("checkin_calendar", "签到日历"),
        ("happy_days", "快乐日子"),
        ("douyin_analyzer", "抖音分析"),
        ("job_search", "求职搜索"),
        ("meetsomeone", "遇见某人"),
        ("bilibili_crawler", "哔哩哔哩爬虫"),
        ("vanity_tool", "虚荣工具"),
        ("wanderai_overview", "WanderAI概览"),
        ("freemind_xmind", "FreeMind XMind"),
        ("word_to_pdf", "Word转PDF"),
        ("share_feature", "分享功能"),
        ("avatar_generator", "头像生成器"),
        # 管理功能
        ("food_photo_binding", "食物照片绑定"),
        ("food_image_correction", "食物图片矫正"),
        ("content_suggestions", "内容建议"),
        ("user_feedback", "用户反馈"),
        ("admin_dashboard", "管理员仪表盘"),
        ("user_management", "用户管理"),
        ("announcement_management", "公告管理"),
        # 其他功能
        ("ai_links", "AI友情链接"),
        ("help_center", "帮助中心"),
        ("version_history", "版本历史"),
    ]

    STATUS_CHOICES = [
        ("enabled", "启用"),
        ("disabled", "禁用"),
        ("maintenance", "维护中"),
        ("beta", "测试版"),
    ]

    VISIBILITY_CHOICES = [
        ("public", "所有用户"),
        ("registered", "注册用户"),
        ("vip", "VIP用户"),
        ("admin", "管理员"),
        ("hidden", "隐藏"),
    ]

    feature_key = models.CharField(max_length=50, choices=FEATURE_CHOICES, unique=True, verbose_name="功能标识")
    feature_name = models.CharField(max_length=100, verbose_name="功能名称")
    description = models.TextField(blank=True, verbose_name="功能描述")
    url_path = models.CharField(max_length=200, blank=True, verbose_name="URL路径")
    icon = models.CharField(max_length=50, default="fas fa-cog", verbose_name="图标类名")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="enabled", verbose_name="状态")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public", verbose_name="可见性")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    access_count = models.IntegerField(default=0, verbose_name="访问次数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "功能入口"
        verbose_name_plural = "功能入口"
        ordering = ["sort_order", "feature_name"]

    def __str__(self):
        return f"{self.feature_name} ({self.get_status_display()})"

    def is_accessible_by_user(self, user):
        """检查用户是否可以访问此功能"""
        if not self.is_active or self.status == "disabled":
            return False

        if self.visibility == "public":
            return True
        elif self.visibility == "registered":
            return user.is_authenticated
        elif self.visibility == "vip":
            return (
                user.is_authenticated and hasattr(user, "membership") and user.membership.membership_type in ["vip", "premium"]
            )
        elif self.visibility == "admin":
            return user.is_authenticated and (user.is_staff or user.is_superuser)
        elif self.visibility == "hidden":
            return False

        return True


class UserFeatureAccess(models.Model):
    """用户个性化功能访问记录"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    feature = models.ForeignKey(FeatureAccess, on_delete=models.CASCADE, verbose_name="功能")
    is_enabled = models.BooleanField(default=True, verbose_name="是否启用")
    access_count = models.IntegerField(default=0, verbose_name="访问次数")
    last_accessed = models.DateTimeField(null=True, blank=True, verbose_name="最后访问时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ["user", "feature"]
        verbose_name = "用户功能访问"
        verbose_name_plural = "用户功能访问"
        ordering = ["-last_accessed"]

    def __str__(self):
        return f"{self.user.username} - {self.feature.feature_name}"
