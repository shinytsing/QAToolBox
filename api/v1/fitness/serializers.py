"""
健身模块序列化器
"""
from rest_framework import serializers
from apps.tools.models import (
    FitnessWorkoutSession,
    FitnessUserProfile,
    FitnessCommunityPost,
    FitnessCommunityComment,
    FitnessCommunityLike,
    ExerciseWeightRecord
)


class ExerciseWeightRecordSerializer(serializers.ModelSerializer):
    """运动重量记录序列化器"""
    
    class Meta:
        model = ExerciseWeightRecord
        fields = (
            'id', 'exercise_name', 'weight', 'reps', 'sets',
            'duration', 'distance', 'notes', 'workout_date',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class FitnessWorkoutSessionSerializer(serializers.ModelSerializer):
    """健身训练会话序列化器"""
    weight_records = ExerciseWeightRecordSerializer(many=True, read_only=True)
    
    class Meta:
        model = FitnessWorkoutSession
        fields = (
            'id', 'user', 'workout_name', 'workout_type',
            'start_time', 'end_time', 'duration', 'calories_burned',
            'notes', 'weight_records', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FitnessUserProfileSerializer(serializers.ModelSerializer):
    """健身用户资料序列化器"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = FitnessUserProfile
        fields = (
            'id', 'user', 'username', 'height', 'weight',
            'fitness_goal', 'experience_level', 'preferred_workout_types',
            'available_days', 'workout_duration', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class FitnessCommunityPostSerializer(serializers.ModelSerializer):
    """健身社区动态序列化器"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.CharField(source='author.profile.avatar', read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = FitnessCommunityPost
        fields = (
            'id', 'author', 'author_name', 'author_avatar',
            'title', 'content', 'post_type', 'images',
            'like_count', 'comment_count', 'is_liked',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def get_like_count(self, obj):
        return obj.likes.count()
    
    def get_comment_count(self, obj):
        return obj.comments.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class FitnessCommunityCommentSerializer(serializers.ModelSerializer):
    """健身社区评论序列化器"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.CharField(source='author.profile.avatar', read_only=True)
    
    class Meta:
        model = FitnessCommunityComment
        fields = (
            'id', 'post', 'author', 'author_name', 'author_avatar',
            'content', 'parent_comment', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class FitnessCommunityLikeSerializer(serializers.ModelSerializer):
    """健身社区点赞序列化器"""
    
    class Meta:
        model = FitnessCommunityLike
        fields = ('id', 'post', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
