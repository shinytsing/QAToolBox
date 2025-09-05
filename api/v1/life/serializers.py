"""
生活工具模块序列化器
"""
from rest_framework import serializers
from apps.tools.models import LifeDiaryEntry, FoodRandomizationSession, FoodItem, CheckInDetail


class LifeDiaryEntrySerializer(serializers.ModelSerializer):
    """生活日记序列化器"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = LifeDiaryEntry
        fields = (
            'id', 'author', 'author_name', 'title', 'content',
            'mood', 'weather', 'location', 'tags', 'is_private',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class FoodItemSerializer(serializers.ModelSerializer):
    """食物项目序列化器"""
    
    class Meta:
        model = FoodItem
        fields = (
            'id', 'name', 'category', 'description', 'image',
            'calories', 'protein', 'carbs', 'fat', 'fiber',
            'is_healthy', 'tags', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class FoodRandomizationSessionSerializer(serializers.ModelSerializer):
    """食物随机化会话序列化器"""
    food_items = FoodItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = FoodRandomizationSession
        fields = (
            'id', 'user', 'session_name', 'food_items',
            'preferences', 'dietary_restrictions', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CheckInDetailSerializer(serializers.ModelSerializer):
    """签到详情序列化器"""
    
    class Meta:
        model = CheckInDetail
        fields = (
            'id', 'user', 'checkin_date', 'mood', 'weather',
            'activities', 'notes', 'location', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MeditationSessionSerializer(serializers.Serializer):
    """冥想会话序列化器"""
    session_type = serializers.ChoiceField(choices=[
        ('breathing', '呼吸冥想'),
        ('body_scan', '身体扫描'),
        ('loving_kindness', '慈爱冥想'),
        ('mindfulness', '正念冥想'),
        ('sleep', '助眠冥想'),
    ])
    duration = serializers.IntegerField(min_value=5, max_value=120)
    background_music = serializers.ChoiceField(choices=[
        ('nature', '自然声音'),
        ('white_noise', '白噪音'),
        ('binaural', '双耳节拍'),
        ('silent', '静音'),
    ], required=False)
    guided = serializers.BooleanField(default=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class AIWritingSerializer(serializers.Serializer):
    """AI文案生成序列化器"""
    content_type = serializers.ChoiceField(choices=[
        ('diary', '日记'),
        ('poem', '诗歌'),
        ('story', '故事'),
        ('article', '文章'),
        ('social_media', '社交媒体'),
        ('email', '邮件'),
    ])
    topic = serializers.CharField(max_length=200)
    style = serializers.ChoiceField(choices=[
        ('formal', '正式'),
        ('casual', '随意'),
        ('creative', '创意'),
        ('humorous', '幽默'),
        ('romantic', '浪漫'),
    ], required=False)
    length = serializers.ChoiceField(choices=[
        ('short', '短篇'),
        ('medium', '中篇'),
        ('long', '长篇'),
    ], required=False)
    keywords = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    tone = serializers.ChoiceField(choices=[
        ('positive', '积极'),
        ('neutral', '中性'),
        ('melancholy', '忧郁'),
        ('inspiring', '励志'),
    ], required=False)
