from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta


class TravelGuide(models.Model):
    """旅游攻略模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    destination = models.CharField(max_length=200, verbose_name='目的地')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 攻略内容
    must_visit_attractions = models.JSONField(default=list, verbose_name='必去景点')
    food_recommendations = models.JSONField(default=list, verbose_name='美食推荐')
    transportation_guide = models.JSONField(default=dict, verbose_name='交通指南')
    hidden_gems = models.JSONField(default=list, verbose_name='隐藏玩法')
    weather_info = models.JSONField(default=dict, verbose_name='天气信息')
    
    # Overview信息字段
    destination_info = models.JSONField(default=dict, verbose_name='目的地基本信息')
    currency_info = models.JSONField(default=dict, verbose_name='汇率信息') 
    timezone_info = models.JSONField(default=dict, verbose_name='时区信息')
    
    best_time_to_visit = models.TextField(blank=True, null=True, verbose_name='最佳旅行时间')
    budget_estimate = models.JSONField(default=dict, verbose_name='预算估算')
    travel_tips = models.JSONField(default=list, verbose_name='旅行贴士')
    
    # 详细攻略
    detailed_guide = models.JSONField(default=dict, verbose_name='详细攻略')
    daily_schedule = models.JSONField(default=list, verbose_name='每日行程')
    activity_timeline = models.JSONField(default=list, verbose_name='活动时间线')
    cost_breakdown = models.JSONField(default=dict, verbose_name='费用明细')
    
    # 个性化设置
    travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
    budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
    budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
    budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 状态
    is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
    is_exported = models.BooleanField(default=False, verbose_name='是否已导出')
    
    # 缓存相关
    is_cached = models.BooleanField(default=False, verbose_name='是否缓存数据')
    cache_source = models.CharField(max_length=50, blank=True, null=True, verbose_name='缓存来源')
    cache_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='缓存过期时间')
    api_used = models.CharField(max_length=50, default='deepseek', verbose_name='使用的API')
    generation_mode = models.CharField(max_length=20, default='standard', verbose_name='生成模式')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '旅游攻略'
        verbose_name_plural = '旅游攻略'
    
    def __str__(self):
        return f"{self.user.username} - {self.destination}"
    
    def get_attractions_count(self):
        return len(self.must_visit_attractions)
    
    def get_food_count(self):
        return len(self.food_recommendations)
    
    def get_hidden_gems_count(self):
        return len(self.hidden_gems)
    
    def is_cache_valid(self):
        """检查缓存是否有效"""
        if not self.is_cached or not self.cache_expires_at:
            return False
        return timezone.now() < self.cache_expires_at
    
    def get_cache_status(self):
        """获取缓存状态"""
        if not self.is_cached:
            return 'not_cached'
        if self.is_cache_valid():
            return 'valid'
        return 'expired'


class TravelGuideCache(models.Model):
    """旅游攻略缓存模型"""
    CACHE_SOURCE_CHOICES = [
        ('standard_api', '标准API生成'),
        ('fast_api', '快速API生成'),
        ('cached_data', '缓存数据'),
        ('fallback_data', '备用数据'),
    ]
    
    API_SOURCE_CHOICES = [
        ('deepseek', 'DeepSeek API'),
        ('openai', 'OpenAI API'),
        ('claude', 'Claude API'),
        ('gemini', 'Gemini API'),
        ('free_api_1', '免费API 1'),
        ('free_api_2', '免费API 2'),
        ('free_api_3', '免费API 3'),
        ('fallback', '备用数据'),
    ]
    
    # 缓存键（用于查找相同条件的攻略）
    destination = models.CharField(max_length=200, verbose_name='目的地')
    travel_style = models.CharField(max_length=50, verbose_name='旅行风格')
    budget_min = models.IntegerField(default=3000, verbose_name='最低预算(元)')
    budget_max = models.IntegerField(default=8000, verbose_name='最高预算(元)')
    budget_amount = models.IntegerField(default=5000, verbose_name='预算金额(元)')
    budget_range = models.CharField(max_length=50, verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, verbose_name='旅行时长')
    interests_hash = models.CharField(max_length=64, verbose_name='兴趣标签哈希')
    
    # 缓存数据
    guide_data = models.JSONField(verbose_name='攻略数据')
    api_used = models.CharField(max_length=50, choices=API_SOURCE_CHOICES, verbose_name='使用的API')
    cache_source = models.CharField(max_length=50, choices=CACHE_SOURCE_CHOICES, verbose_name='缓存来源')
    
    # 缓存元数据
    generation_time = models.FloatField(verbose_name='生成时间(秒)')
    data_quality_score = models.FloatField(default=0.0, verbose_name='数据质量评分')
    usage_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '旅游攻略缓存'
        verbose_name_plural = '旅游攻略缓存'
        unique_together = ['destination', 'travel_style', 'budget_range', 'travel_duration', 'interests_hash']
    
    def __str__(self):
        return f"{self.destination} - {self.travel_style} - {self.budget_range}"
    
    def is_expired(self):
        """检查缓存是否过期"""
        return timezone.now() > self.expires_at
    
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def get_cache_key(self):
        """生成缓存键"""
        return f"travel_guide_{self.destination}_{self.travel_style}_{self.budget_range}_{self.travel_duration}_{self.interests_hash}"


class TravelReview(models.Model):
    """旅游攻略评价模型"""
    travel_guide = models.ForeignKey(TravelGuide, on_delete=models.CASCADE, verbose_name='旅游攻略')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='评分')
    comment = models.TextField(blank=True, null=True, verbose_name='评价内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        unique_together = ['travel_guide', 'user']
        ordering = ['-created_at']
        verbose_name = '旅游攻略评价'
        verbose_name_plural = '旅游攻略评价'
    
    def __str__(self):
        return f"{self.user.username} - {self.travel_guide.destination} - {self.rating}星"


class TravelCity(models.Model):
    """旅行城市模型"""
    name = models.CharField(max_length=100, verbose_name='城市名称')
    country = models.CharField(max_length=100, verbose_name='国家')
    region = models.CharField(max_length=100, blank=True, null=True, verbose_name='地区')
    latitude = models.FloatField(blank=True, null=True, verbose_name='纬度')
    longitude = models.FloatField(blank=True, null=True, verbose_name='经度')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        ordering = ['country', 'name']
        verbose_name = '旅行城市'
        verbose_name_plural = '旅行城市'
        unique_together = ['name', 'country']
    
    def __str__(self):
        return f"{self.name}, {self.country}"


class TravelPost(models.Model):
    """重构后的好心人攻略模型 - 按照产品文档设计"""
    
    # 基础信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建用户')
    title = models.CharField(max_length=200, verbose_name='攻略标题')
    cover_image = models.ImageField(upload_to='travel_posts/covers/', verbose_name='封面图')
    
    # 核心筛选维度
    travel_styles = models.JSONField(default=list, verbose_name='旅行风格')
    cities = models.ManyToManyField(TravelCity, verbose_name='关联城市')
    travel_duration = models.CharField(max_length=50, verbose_name='旅行时长')
    travel_date = models.DateField(blank=True, null=True, verbose_name='出行时间')

    # 位置信息 - 新增字段
    location_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='交易城市')
    location_region = models.CharField(max_length=100, blank=True, null=True, verbose_name='交易地区')
    location_address = models.CharField(max_length=500, blank=True, null=True, verbose_name='详细地址')
    location_latitude = models.FloatField(blank=True, null=True, verbose_name='纬度')
    location_longitude = models.FloatField(blank=True, null=True, verbose_name='经度')
    location_radius = models.IntegerField(default=50, verbose_name='交易半径(公里)')
    
    # 预算信息
    budget_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='人均预算')
    budget_currency = models.CharField(max_length=10, default='CNY', verbose_name='预算货币')
    budget_type = models.CharField(max_length=20, choices=[
        ('transport', '交通'),
        ('accommodation', '住宿'),
        ('food', '美食'),
        ('shopping', '购物'),
        ('total', '总计'),
    ], default='total', verbose_name='预算类型')
    
    # 核心内容
    itinerary_details = models.JSONField(default=list, verbose_name='行程明细')
    transportation_methods = models.JSONField(default=list, verbose_name='交通方式')
    food_recommendations = models.JSONField(default=list, verbose_name='美食推荐')
    accommodation_recommendations = models.TextField(blank=True, null=True, verbose_name='住宿推荐')
    travel_tips = models.TextField(blank=True, null=True, verbose_name='实用贴士')
    custom_tags = models.JSONField(default=list, verbose_name='自定义标签')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    like_count = models.IntegerField(default=0, verbose_name='点赞次数')
    favorite_count = models.IntegerField(default=0, verbose_name='收藏次数')
    comment_count = models.IntegerField(default=0, verbose_name='评论次数')
    
    # 状态
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '旅行攻略'
        verbose_name_plural = '旅行攻略'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_cities_display(self):
        """获取城市显示名称"""
        return ', '.join([f"{city.name}, {city.country}" for city in self.cities.all()])
    
    def get_travel_styles_display(self):
        """获取旅行风格显示名称"""
        style_map = {
            'budget': '穷游',
            'luxury': '奢侈游',
            'family': '亲子游',
            'couple': '情侣度假',
            'shopping': '闺蜜购物',
            'cultural': '文化深度',
            'adventure': '户外探险',
            'food': '美食之旅',
            'photography': '摄影之旅',
        }
        return [style_map.get(style, style) for style in self.travel_styles]
    
    def get_transportation_methods_display(self):
        """获取交通方式显示名称"""
        method_map = {
            'plane': '飞机',
            'train': '高铁',
            'car': '自驾',
            'public': '公共交通',
            'walking': '徒步',
        }
        return [method_map.get(method, method) for method in self.transportation_methods]
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_like_count(self):
        """增加点赞次数"""
        self.like_count += 1
        self.save(update_fields=['like_count'])
    
    def increment_favorite_count(self):
        """增加收藏次数"""
        self.favorite_count += 1
        self.save(update_fields=['favorite_count'])
    
    def increment_comment_count(self):
        """增加评论次数"""
        self.comment_count += 1
        self.save(update_fields=['comment_count'])
    
    def extract_food_list(self):
        """从行程明细中提取美食清单"""
        food_list = []
        for day in self.itinerary_details:
            for item in day.get('items', []):
                if item.get('type') == 'food':
                    food_list.append({
                        'name': item.get('name'),
                        'location': item.get('location'),
                        'recommended_dishes': item.get('recommended_dishes', []),
                        'day': day.get('day'),
                        'description': item.get('description'),
                    })
        return food_list
    
    def extract_attractions_list(self):
        """从行程明细中提取景点清单"""
        attractions_list = []
        for day in self.itinerary_details:
            for item in day.get('items', []):
                if item.get('type') == 'attraction':
                    attractions_list.append({
                        'name': item.get('name'),
                        'location': item.get('location'),
                        'day': day.get('day'),
                        'description': item.get('description'),
                        'tips': item.get('tips', []),
                    })
        return attractions_list

def get_location_display(self):
    """获取位置显示信息"""
    if self.location_city and self.location_region:
        return f"{self.location_city}，{self.location_region}"
    elif self.location_city:
        return self.location_city
    elif self.location_address:
        return self.location_address
    return "位置信息未设置"

def has_location_info(self):
    """检查是否有位置信息"""
    return bool(self.location_city or self.location_address)

def get_location_coordinates(self):
    """获取位置坐标"""
    if self.location_latitude and self.location_longitude:
        return {
            'lat': self.location_latitude,
            'lon': self.location_longitude
        }
    return None

def calculate_distance_to(self, target_lat, target_lon):
    """计算到指定位置的距离（公里）"""
    if not self.location_latitude or not self.location_longitude:
        return None
    
    from math import radians, cos, sin, asin, sqrt
    
    # 将经纬度转换为弧度
    lat1, lon1, lat2, lon2 = map(radians, [
        self.location_latitude, self.location_longitude, target_lat, target_lon
    ])
    
    # Haversine公式
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球半径（公里）
    
    return c * r


class TravelPostLike(models.Model):
    """攻略点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(TravelPost, on_delete=models.CASCADE, verbose_name='攻略')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        verbose_name = '攻略点赞'
        verbose_name_plural = '攻略点赞'
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.post.title}"


class TravelPostFavorite(models.Model):
    """攻略收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(TravelPost, on_delete=models.CASCADE, verbose_name='攻略')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')
    
    class Meta:
        unique_together = ['user', 'post']
        ordering = ['-created_at']
        verbose_name = '攻略收藏'
        verbose_name_plural = '攻略收藏'
    
    def __str__(self):
        return f"{self.user.username} 收藏了 {self.post.title}"


class TravelPostComment(models.Model):
    """攻略评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    post = models.ForeignKey(TravelPost, on_delete=models.CASCADE, verbose_name='攻略')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name='父评论')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '攻略评论'
        verbose_name_plural = '攻略评论'
    
    def __str__(self):
        return f"{self.user.username} 评论了 {self.post.title}"


# 保留原有的UserGeneratedTravelGuide模型以兼容旧数据
class UserGeneratedTravelGuide(models.Model):
    """用户生成的旅游攻略模型 - 好心人的攻略（兼容旧版本）"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建用户')
    title = models.CharField(max_length=200, verbose_name='攻略标题')
    destination = models.CharField(max_length=200, verbose_name='目的地')
    content = models.TextField(verbose_name='攻略内容')
    summary = models.TextField(blank=True, null=True, verbose_name='攻略摘要')
    
    # 攻略分类
    travel_style = models.CharField(max_length=50, default='general', verbose_name='旅行风格')
    budget_range = models.CharField(max_length=50, default='medium', verbose_name='预算范围')
    travel_duration = models.CharField(max_length=50, default='3-5天', verbose_name='旅行时长')
    interests = models.JSONField(default=list, verbose_name='兴趣标签')
    
    # 文件附件
    attachment = models.FileField(upload_to='travel_guides/', blank=True, null=True, verbose_name='附件')
    attachment_name = models.CharField(max_length=255, blank=True, null=True, verbose_name='附件名称')
    
    # 统计信息
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    
    # 状态
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    is_featured = models.BooleanField(default=False, verbose_name='是否推荐')
    is_approved = models.BooleanField(default=True, verbose_name='是否审核通过')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '用户生成旅游攻略'
        verbose_name_plural = '用户生成旅游攻略'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_file_extension(self):
        """获取文件扩展名"""
        if self.attachment:
            return self.attachment.name.split('.')[-1].lower()
        return None
    
    def is_downloadable(self):
        """检查是否可下载"""
        return bool(self.attachment)
    
    def increment_view_count(self):
        """增加查看次数"""
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def increment_use_count(self):
        """增加使用次数"""
        self.use_count += 1
        self.save(update_fields=['use_count'])


class TravelGuideUsage(models.Model):
    """旅游攻略使用记录模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    guide = models.ForeignKey(UserGeneratedTravelGuide, on_delete=models.CASCADE, verbose_name='攻略')
    usage_type = models.CharField(max_length=20, choices=[
        ('view', '查看'),
        ('download', '下载'),
        ('use', '使用'),
    ], verbose_name='使用类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='使用时间')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '攻略使用记录'
        verbose_name_plural = '攻略使用记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.guide.title} - {self.get_usage_type_display()}"
