"""
健身模块视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from api.response import APIResponse, APIErrorCodes
from api.permissions import IsAuthenticated, FeaturePermission
from .serializers import (
    FitnessWorkoutSessionSerializer,
    FitnessUserProfileSerializer,
    FitnessCommunityPostSerializer,
    FitnessCommunityCommentSerializer,
    ExerciseWeightRecordSerializer
)
from apps.tools.models import (
    FitnessWorkoutSession,
    FitnessUserProfile,
    FitnessCommunityPost,
    FitnessCommunityComment,
    FitnessCommunityLike,
    ExerciseWeightRecord
)


class FitnessWorkoutViewSet(viewsets.ModelViewSet):
    """健身训练管理"""
    serializer_class = FitnessWorkoutSessionSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('fitness_center')]
    
    def get_queryset(self):
        return FitnessWorkoutSession.objects.filter(user=self.request.user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """获取训练计划列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        workout_type = request.query_params.get('workout_type')
        if workout_type:
            queryset = queryset.filter(workout_type=workout_type)
        
        # 日期范围过滤
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(workout_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(workout_date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建训练计划"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="训练计划创建成功"
            )
        return APIResponse.error(
            message="创建失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def add_weight_record(self, request, pk=None):
        """添加重量记录"""
        workout = self.get_object()
        data = request.data.copy()
        data['workout_session'] = workout.id
        
        serializer = ExerciseWeightRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="重量记录添加成功"
            )
        return APIResponse.error(
            message="添加失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )


class FitnessProfileViewSet(viewsets.ModelViewSet):
    """健身用户资料管理"""
    serializer_class = FitnessUserProfileSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('fitness_center')]
    
    def get_queryset(self):
        return FitnessUserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        profile, created = FitnessUserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    def list(self, request, *args, **kwargs):
        """获取用户健身资料"""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return APIResponse.success(data=serializer.data)
    
    def update(self, request, *args, **kwargs):
        """更新用户健身资料"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="资料更新成功"
            )
        return APIResponse.error(
            message="更新失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )


class FitnessCommunityPostViewSet(viewsets.ModelViewSet):
    """健身社区动态管理"""
    serializer_class = FitnessCommunityPostSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('fitness_community')]
    
    def get_queryset(self):
        return FitnessCommunityPost.objects.all().order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """获取社区动态列表"""
        queryset = self.get_queryset()
        
        # 搜索过滤
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        # 类型过滤
        post_type = request.query_params.get('post_type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """发布社区动态"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="动态发布成功"
            )
        return APIResponse.error(
            message="发布失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞动态"""
        post = self.get_object()
        like, created = FitnessCommunityLike.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if created:
            return APIResponse.success(message="点赞成功")
        else:
            like.delete()
            return APIResponse.success(message="取消点赞")
    
    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        """评论动态"""
        post = self.get_object()
        data = request.data.copy()
        data['post'] = post.id
        
        serializer = FitnessCommunityCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="评论成功"
            )
        return APIResponse.error(
            message="评论失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """获取动态评论"""
        post = self.get_object()
        comments = post.comments.all().order_by('created_at')
        serializer = FitnessCommunityCommentSerializer(comments, many=True)
        return APIResponse.success(data=serializer.data)
