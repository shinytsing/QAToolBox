"""
社交娱乐模块序列化器
"""
from rest_framework import serializers
from apps.tools.models import (
    ChatRoom, ChatMessage, HeartLinkRequest, BuddyEvent, 
    BuddyEventMember, BuddyEventMessage, TarotReading
)


class ChatRoomSerializer(serializers.ModelSerializer):
    """聊天室序列化器"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = (
            'id', 'name', 'description', 'creator', 'creator_name',
            'room_type', 'is_private', 'max_members', 'member_count',
            'last_message', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'creator', 'created_at', 'updated_at')
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return {
                'content': last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content,
                'sender': last_msg.sender.username,
                'timestamp': last_msg.created_at
            }
        return None
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天消息序列化器"""
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_avatar = serializers.CharField(source='sender.profile.avatar', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = (
            'id', 'room', 'sender', 'sender_name', 'sender_avatar',
            'content', 'message_type', 'is_read', 'created_at'
        )
        read_only_fields = ('id', 'sender', 'is_read', 'created_at')
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class HeartLinkRequestSerializer(serializers.ModelSerializer):
    """心链请求序列化器"""
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    requester_avatar = serializers.CharField(source='requester.profile.avatar', read_only=True)
    target_name = serializers.CharField(source='target.username', read_only=True)
    target_avatar = serializers.CharField(source='target.profile.avatar', read_only=True)
    
    class Meta:
        model = HeartLinkRequest
        fields = (
            'id', 'requester', 'requester_name', 'requester_avatar',
            'target', 'target_name', 'target_avatar', 'message',
            'status', 'created_at', 'responded_at'
        )
        read_only_fields = ('id', 'requester', 'created_at', 'responded_at')
    
    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class BuddyEventSerializer(serializers.ModelSerializer):
    """搭子活动序列化器"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_avatar = serializers.CharField(source='creator.profile.avatar', read_only=True)
    member_count = serializers.SerializerMethodField()
    is_joined = serializers.SerializerMethodField()
    
    class Meta:
        model = BuddyEvent
        fields = (
            'id', 'title', 'description', 'creator', 'creator_name', 'creator_avatar',
            'event_type', 'location', 'start_time', 'end_time', 'max_participants',
            'member_count', 'is_joined', 'status', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'creator', 'created_at', 'updated_at')
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_joined(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class BuddyEventMemberSerializer(serializers.ModelSerializer):
    """搭子活动成员序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.CharField(source='user.profile.avatar', read_only=True)
    
    class Meta:
        model = BuddyEventMember
        fields = (
            'id', 'event', 'user', 'user_name', 'user_avatar',
            'join_time', 'status', 'notes'
        )
        read_only_fields = ('id', 'join_time')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TarotReadingSerializer(serializers.ModelSerializer):
    """塔罗占卜序列化器"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TarotReading
        fields = (
            'id', 'user', 'user_name', 'question', 'spread_type',
            'cards_drawn', 'interpretation', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StoryGeneratorSerializer(serializers.Serializer):
    """故事生成序列化器"""
    story_type = serializers.ChoiceField(choices=[
        ('romance', '爱情故事'),
        ('adventure', '冒险故事'),
        ('mystery', '悬疑故事'),
        ('fantasy', '奇幻故事'),
        ('scifi', '科幻故事'),
        ('horror', '恐怖故事'),
        ('comedy', '喜剧故事'),
    ])
    theme = serializers.CharField(max_length=200)
    characters = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False
    )
    setting = serializers.CharField(max_length=200, required=False)
    length = serializers.ChoiceField(choices=[
        ('short', '短篇'),
        ('medium', '中篇'),
        ('long', '长篇'),
    ], default='short')
    style = serializers.ChoiceField(choices=[
        ('classic', '经典'),
        ('modern', '现代'),
        ('poetic', '诗意'),
        ('humorous', '幽默'),
    ], default='modern')


class TravelGuideSerializer(serializers.Serializer):
    """旅游攻略序列化器"""
    destination = serializers.CharField(max_length=200)
    travel_type = serializers.ChoiceField(choices=[
        ('solo', '独自旅行'),
        ('couple', '情侣旅行'),
        ('family', '家庭旅行'),
        ('friends', '朋友旅行'),
        ('business', '商务旅行'),
    ])
    duration = serializers.IntegerField(min_value=1, max_value=30)
    budget = serializers.ChoiceField(choices=[
        ('low', '经济型'),
        ('medium', '中等'),
        ('high', '豪华型'),
    ])
    interests = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            ('culture', '文化'),
            ('nature', '自然'),
            ('food', '美食'),
            ('shopping', '购物'),
            ('adventure', '冒险'),
            ('relaxation', '休闲'),
        ]),
        required=False
    )
    season = serializers.ChoiceField(choices=[
        ('spring', '春季'),
        ('summer', '夏季'),
        ('autumn', '秋季'),
        ('winter', '冬季'),
    ], required=False)


class FortuneAnalyzerSerializer(serializers.Serializer):
    """命运分析序列化器"""
    name = serializers.CharField(max_length=50)
    birth_date = serializers.DateField()
    birth_time = serializers.TimeField(required=False)
    birth_place = serializers.CharField(max_length=100, required=False)
    analysis_type = serializers.ChoiceField(choices=[
        ('personality', '性格分析'),
        ('career', '事业运势'),
        ('love', '爱情运势'),
        ('health', '健康运势'),
        ('wealth', '财运分析'),
        ('comprehensive', '综合分析'),
    ])
    questions = serializers.ListField(
        child=serializers.CharField(max_length=200),
        required=False
    )
