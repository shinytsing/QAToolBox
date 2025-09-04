from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class TarotCard(models.Model):
    """塔罗牌模型"""

    CARD_TYPE_CHOICES = [
        ("major", "大阿卡纳"),
        ("minor", "小阿卡纳"),
    ]

    SUIT_CHOICES = [
        ("wands", "权杖"),
        ("cups", "圣杯"),
        ("swords", "宝剑"),
        ("pentacles", "钱币"),
        ("major", "大阿卡纳"),
    ]

    name = models.CharField(max_length=100, verbose_name="牌名")
    name_en = models.CharField(max_length=100, verbose_name="英文名")
    card_type = models.CharField(max_length=10, choices=CARD_TYPE_CHOICES, verbose_name="牌类型")
    suit = models.CharField(max_length=20, choices=SUIT_CHOICES, verbose_name="花色")
    number = models.IntegerField(verbose_name="数字")
    image_url = models.URLField(blank=True, null=True, verbose_name="牌面图片")

    # 牌义
    upright_meaning = models.TextField(verbose_name="正位含义")
    reversed_meaning = models.TextField(verbose_name="逆位含义")
    keywords = models.JSONField(default=list, verbose_name="关键词")

    # 详细解读
    description = models.TextField(blank=True, null=True, verbose_name="牌面描述")
    symbolism = models.TextField(blank=True, null=True, verbose_name="象征意义")
    advice = models.TextField(blank=True, null=True, verbose_name="建议")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["card_type", "suit", "number"]
        verbose_name = "塔罗牌"
        verbose_name_plural = "塔罗牌"

    def __str__(self):
        return f"{self.name} ({self.get_suit_display()})"


class TarotSpread(models.Model):
    """塔罗牌阵模型"""

    SPREAD_TYPE_CHOICES = [
        ("classic", "经典牌阵"),
        ("situation", "情景牌阵"),
        ("custom", "自定义牌阵"),
    ]

    name = models.CharField(max_length=100, verbose_name="牌阵名称")
    spread_type = models.CharField(max_length=20, choices=SPREAD_TYPE_CHOICES, verbose_name="牌阵类型")
    description = models.TextField(verbose_name="牌阵描述")
    card_count = models.IntegerField(verbose_name="牌数")
    positions = models.JSONField(default=list, verbose_name="位置定义")
    image_url = models.URLField(blank=True, null=True, verbose_name="牌阵图片")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        ordering = ["spread_type", "card_count"]
        verbose_name = "塔罗牌阵"
        verbose_name_plural = "塔罗牌阵"

    def __str__(self):
        return f"{self.name} ({self.card_count}张牌)"


class TarotReading(models.Model):
    """塔罗牌占卜记录模型"""

    READING_TYPE_CHOICES = [
        ("daily", "每日运势"),
        ("love", "爱情占卜"),
        ("career", "事业占卜"),
        ("health", "健康占卜"),
        ("spiritual", "灵性占卜"),
        ("custom", "自定义占卜"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    spread = models.ForeignKey(TarotSpread, on_delete=models.CASCADE, verbose_name="牌阵")
    reading_type = models.CharField(max_length=20, choices=READING_TYPE_CHOICES, verbose_name="占卜类型")
    question = models.TextField(verbose_name="问题")

    # 抽牌结果
    drawn_cards = models.JSONField(default=list, verbose_name="抽到的牌")
    card_positions = models.JSONField(default=list, verbose_name="牌的位置")

    # AI解读结果
    ai_interpretation = models.TextField(blank=True, null=True, verbose_name="AI解读")
    detailed_reading = models.JSONField(default=dict, verbose_name="详细解读")

    # 用户反馈
    user_feedback = models.TextField(blank=True, null=True, verbose_name="用户反馈")
    accuracy_rating = models.IntegerField(blank=True, null=True, verbose_name="准确度评分")

    # 心情标签
    mood_before = models.CharField(max_length=50, blank=True, null=True, verbose_name="占卜前心情")
    mood_after = models.CharField(max_length=50, blank=True, null=True, verbose_name="占卜后心情")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="占卜时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "塔罗占卜"
        verbose_name_plural = "塔罗占卜"

    def __str__(self):
        return f"{self.user.username} - {self.get_reading_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"


# 删除塔罗日记模型


class TarotEnergyCalendar(models.Model):
    """塔罗能量日历模型"""

    ENERGY_TYPE_CHOICES = [
        ("new_moon", "新月"),
        ("full_moon", "满月"),
        ("eclipse", "日食/月食"),
        ("solstice", "夏至/冬至"),
        ("equinox", "春分/秋分"),
        ("daily", "日常能量"),
    ]

    date = models.DateField(verbose_name="日期")
    energy_type = models.CharField(max_length=20, choices=ENERGY_TYPE_CHOICES, verbose_name="能量类型")
    energy_level = models.IntegerField(choices=[(i, i) for i in range(1, 11)], verbose_name="能量等级")
    description = models.TextField(verbose_name="能量描述")
    recommended_cards = models.JSONField(default=list, verbose_name="推荐牌")
    special_reading = models.TextField(blank=True, null=True, verbose_name="特殊占卜")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ["date", "energy_type"]
        ordering = ["-date"]
        verbose_name = "塔罗能量日历"
        verbose_name_plural = "塔罗能量日历"

    def __str__(self):
        return f"{self.date} - {self.get_energy_type_display()}"


class TarotCommunity(models.Model):
    """塔罗社区模型"""

    POST_TYPE_CHOICES = [
        ("story", "故事分享"),
        ("question", "解牌求助"),
        ("experience", "经验分享"),
        ("discussion", "讨论"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name="帖子类型")
    title = models.CharField(max_length=200, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    tags = models.JSONField(default=list, verbose_name="标签")
    is_anonymous = models.BooleanField(default=False, verbose_name="是否匿名")
    likes_count = models.IntegerField(default=0, verbose_name="点赞数")
    comments_count = models.IntegerField(default=0, verbose_name="评论数")
    is_featured = models.BooleanField(default=False, verbose_name="是否精选")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "塔罗社区"
        verbose_name_plural = "塔罗社区"

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class TarotCommunityComment(models.Model):
    """塔罗社区评论模型"""

    post = models.ForeignKey(TarotCommunity, on_delete=models.CASCADE, related_name="comments", verbose_name="帖子")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    content = models.TextField(verbose_name="评论内容")
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies", verbose_name="父评论"
    )
    likes_count = models.IntegerField(default=0, verbose_name="点赞数")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "塔罗社区评论"
        verbose_name_plural = "塔罗社区评论"

    def __str__(self):
        return f"{self.user.username} 回复 {self.post.title}"
