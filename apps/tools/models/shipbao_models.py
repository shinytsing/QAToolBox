from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class ShipBaoItem(models.Model):
    """船宝物品模型"""
    CATEGORY_CHOICES = [
        ('electronics', '电子产品'),
        ('clothing', '服饰鞋包'),
        ('furniture', '家具家居'),
        ('books', '图书音像'),
        ('sports', '运动户外'),
        ('beauty', '美妆护肤'),
        ('toys', '玩具游戏'),
        ('food', '食品饮料'),
        ('other', '其他'),
    ]
    
    CONDITION_CHOICES = [
        (1, '1星 - 很旧'),
        (2, '2星 - 较旧'),
        (3, '3星 - 一般'),
        (4, '4星 - 较新'),
        (5, '5星 - 全新'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '发布中'),
        ('reserved', '交易中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    DELIVERY_CHOICES = [
        ('pickup', '仅自提'),
        ('delivery', '仅送货'),
        ('both', '自提/送货'),
    ]
    
    # 基础信息
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='卖家')
    title = models.CharField(max_length=200, verbose_name='物品标题')
    description = models.TextField(verbose_name='物品描述')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='分类')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格(元)')
    condition = models.IntegerField(choices=CONDITION_CHOICES, verbose_name='新旧程度')
    
    # 图片
    images = models.JSONField(default=list, verbose_name='图片URL列表')
    
    # 交易设置
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='pickup', verbose_name='交易方式')
    can_bargain = models.BooleanField(default=False, verbose_name='是否可议价')
    
    # 地理位置
    location = models.CharField(max_length=200, verbose_name='交易地点')
    latitude = models.FloatField(blank=True, null=True, verbose_name='纬度')
    longitude = models.FloatField(blank=True, null=True, verbose_name='经度')
    
    # 状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='交易状态')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='浏览次数')
    favorite_count = models.IntegerField(default=0, verbose_name='收藏次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '船宝物品'
        verbose_name_plural = '船宝物品'
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.seller.username} - {self.title} - ¥{self.price}"
    
    def get_condition_stars(self):
        """获取新旧程度星级显示"""
        return '★' * self.condition + '☆' * (5 - self.condition)
    
    def get_main_image(self):
        """获取主图"""
        return self.images[0] if self.images else None
    
    def get_image_count(self):
        """获取图片数量"""
        return len(self.images)


class ShipBaoTransaction(models.Model):
    """船宝交易记录模型"""
    STATUS_CHOICES = [
        ('initiated', '已发起'),
        ('negotiating', '协商中'),
        ('meeting_arranged', '已约定见面'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    # 交易信息
    item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, related_name='transactions', verbose_name='物品')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_purchases', verbose_name='买家')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_sales', verbose_name='卖家')
    
    # 交易状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated', verbose_name='交易状态')
    
    # 交易详情
    final_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='最终价格')
    meeting_location = models.CharField(max_length=200, blank=True, null=True, verbose_name='见面地点')
    meeting_time = models.DateTimeField(blank=True, null=True, verbose_name='见面时间')
    
    # 评价
    buyer_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='买家评分')
    seller_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)], verbose_name='卖家评分')
    buyer_comment = models.TextField(blank=True, null=True, verbose_name='买家评价')
    seller_comment = models.TextField(blank=True, null=True, verbose_name='卖家评价')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发起时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='完成时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '船宝交易'
        verbose_name_plural = '船宝交易'
        unique_together = ['item', 'buyer']
    
    def __str__(self):
        return f"{self.buyer.username} 购买 {self.item.title}"


class ShipBaoMessage(models.Model):
    """船宝私信模型"""
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('offer', '报价'),
        ('system', '系统消息'),
    ]
    
    transaction = models.ForeignKey(ShipBaoTransaction, on_delete=models.CASCADE, related_name='messages', verbose_name='交易')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发送者')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    content = models.TextField(verbose_name='消息内容')
    image_url = models.URLField(blank=True, null=True, verbose_name='图片URL')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='报价金额')
    
    # 消息状态
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '船宝私信'
        verbose_name_plural = '船宝私信'
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"


class ShipBaoUserProfile(models.Model):
    """船宝用户资料模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    
    # 实名认证
    is_verified = models.BooleanField(default=False, verbose_name='是否实名认证')
    real_name = models.CharField(max_length=50, blank=True, null=True, verbose_name='真实姓名')
    id_card_number = models.CharField(max_length=18, blank=True, null=True, verbose_name='身份证号')
    verification_time = models.DateTimeField(blank=True, null=True, verbose_name='认证时间')
    
    # 信用评分
    credit_score = models.IntegerField(default=100, verbose_name='信用评分')
    total_transactions = models.IntegerField(default=0, verbose_name='总交易数')
    successful_transactions = models.IntegerField(default=0, verbose_name='成功交易数')
    
    # 位置信息
    city = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在城市')
    district = models.CharField(max_length=50, blank=True, null=True, verbose_name='所在区域')
    
    # 偏好设置
    notification_enabled = models.BooleanField(default=True, verbose_name='启用通知')
    auto_accept_offers = models.BooleanField(default=False, verbose_name='自动接受报价')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '船宝用户资料'
        verbose_name_plural = '船宝用户资料'
    
    def __str__(self):
        return f"{self.user.username} - 船宝资料"
    
    def get_success_rate(self):
        """获取交易成功率"""
        if self.total_transactions == 0:
            return 0
        return round((self.successful_transactions / self.total_transactions) * 100, 1)
    
    def get_credit_level(self):
        """获取信用等级"""
        if self.credit_score >= 90:
            return '优秀'
        elif self.credit_score >= 80:
            return '良好'
        elif self.credit_score >= 70:
            return '一般'
        else:
            return '较差'


class ShipBaoReport(models.Model):
    """船宝举报模型"""
    REPORT_TYPE_CHOICES = [
        ('fraud', '欺诈行为'),
        ('fake_info', '虚假信息'),
        ('inappropriate', '不当内容'),
        ('harassment', '骚扰行为'),
        ('other', '其他'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('investigating', '调查中'),
        ('resolved', '已处理'),
        ('dismissed', '已驳回'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_reports', verbose_name='举报者')
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipbao_reported', verbose_name='被举报者')
    reported_item = models.ForeignKey(ShipBaoItem, on_delete=models.CASCADE, blank=True, null=True, verbose_name='被举报物品')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name='举报类型')
    description = models.TextField(verbose_name='举报描述')
    evidence = models.JSONField(default=list, verbose_name='证据材料')
    
    # 处理状态
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='处理状态')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='管理员备注')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='举报时间')
    resolved_at = models.DateTimeField(blank=True, null=True, verbose_name='处理时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '船宝举报'
        verbose_name_plural = '船宝举报'
    
    def __str__(self):
        return f"{self.reporter.username} 举报 {self.reported_user.username}"
