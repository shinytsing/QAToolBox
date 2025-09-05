"""
生活工具模块视图
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
import random

from api.response import APIResponse, APIErrorCodes
from api.permissions import IsAuthenticated, FeaturePermission
from .serializers import (
    LifeDiaryEntrySerializer,
    FoodRandomizationSessionSerializer,
    FoodItemSerializer,
    CheckInDetailSerializer,
    MeditationSessionSerializer,
    AIWritingSerializer
)
from apps.tools.models import (
    LifeDiaryEntry,
    FoodRandomizationSession,
    FoodItem,
    CheckInDetail
)


class LifeDiaryViewSet(viewsets.ModelViewSet):
    """生活日记管理"""
    serializer_class = LifeDiaryEntrySerializer
    permission_classes = [IsAuthenticated, FeaturePermission('life_diary')]
    
    def get_queryset(self):
        return LifeDiaryEntry.objects.filter(author=self.request.user).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """获取日记列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        mood = request.query_params.get('mood')
        if mood:
            queryset = queryset.filter(mood=mood)
        
        weather = request.query_params.get('weather')
        if weather:
            queryset = queryset.filter(weather=weather)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """创建日记"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="日记创建成功"
            )
        return APIResponse.error(
            message="创建失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """分享日记"""
        diary = self.get_object()
        # 这里可以集成分享功能
        return APIResponse.success(
            data={'share_url': f'/diary/{diary.id}/share/'},
            message="分享链接已生成"
        )


class FoodRandomizationViewSet(viewsets.ModelViewSet):
    """食物随机化管理"""
    serializer_class = FoodRandomizationSessionSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('food_randomizer')]
    
    def get_queryset(self):
        return FoodRandomizationSession.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """开始随机化会话"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 停用其他活跃会话
            FoodRandomizationSession.objects.filter(
                user=request.user,
                is_active=True
            ).update(is_active=False)
            
            session = serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="随机化会话已开始"
            )
        return APIResponse.error(
            message="启动失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=True, methods=['post'])
    def get_random_food(self, request, pk=None):
        """获取随机食物推荐"""
        session = self.get_object()
        
        # 根据偏好和限制筛选食物
        food_items = FoodItem.objects.all()
        
        if session.dietary_restrictions:
            restrictions = session.dietary_restrictions.split(',')
            for restriction in restrictions:
                food_items = food_items.exclude(tags__icontains=restriction.strip())
        
        if session.preferences:
            preferences = session.preferences.split(',')
            for preference in preferences:
                food_items = food_items.filter(tags__icontains=preference.strip())
        
        if food_items.exists():
            random_food = random.choice(food_items)
            serializer = FoodItemSerializer(random_food)
            return APIResponse.success(data=serializer.data)
        else:
            return APIResponse.error(
                message="没有找到符合条件的食物",
                code=APIErrorCodes.NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def stop_session(self, request, pk=None):
        """停止随机化会话"""
        session = self.get_object()
        session.is_active = False
        session.save()
        
        return APIResponse.success(message="随机化会话已停止")


class CheckInViewSet(viewsets.ModelViewSet):
    """签到管理"""
    serializer_class = CheckInDetailSerializer
    permission_classes = [IsAuthenticated, FeaturePermission('checkin_calendar')]
    
    def get_queryset(self):
        return CheckInDetail.objects.filter(user=self.request.user).order_by('-checkin_date')
    
    def create(self, request, *args, **kwargs):
        """创建签到记录"""
        # 检查今天是否已经签到
        today = timezone.now().date()
        if CheckInDetail.objects.filter(
            user=request.user,
            checkin_date=today
        ).exists():
            return APIResponse.error(
                message="今天已经签到过了",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="签到成功"
            )
        return APIResponse.error(
            message="签到失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    @action(detail=False, methods=['get'])
    def streak(self, request):
        """获取连续签到天数"""
        user = request.user
        today = timezone.now().date()
        streak = 0
        
        # 计算连续签到天数
        current_date = today
        while CheckInDetail.objects.filter(
            user=user,
            checkin_date=current_date
        ).exists():
            streak += 1
            current_date -= timedelta(days=1)
        
        return APIResponse.success(data={'streak_days': streak})
    
    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """获取签到日历"""
        year = request.query_params.get('year', timezone.now().year)
        month = request.query_params.get('month', timezone.now().month)
        
        checkins = CheckInDetail.objects.filter(
            user=request.user,
            checkin_date__year=year,
            checkin_date__month=month
        ).values_list('checkin_date', flat=True)
        
        return APIResponse.success(data=list(checkins))


class MeditationViewSet(viewsets.ViewSet):
    """冥想指导"""
    permission_classes = [IsAuthenticated, FeaturePermission('meditation_guide')]
    
    @action(detail=False, methods=['post'])
    def start_session(self, request):
        """开始冥想会话"""
        serializer = MeditationSessionSerializer(data=request.data)
        if serializer.is_valid():
            session_data = serializer.validated_data
            
            # 生成冥想指导内容
            guidance = self.generate_meditation_guidance(session_data)
            
            return APIResponse.success(
                data={
                    'session_id': f"meditation_{timezone.now().timestamp()}",
                    'guidance': guidance,
                    'duration': session_data['duration'],
                    'session_type': session_data['session_type']
                },
                message="冥想会话已开始"
            )
        return APIResponse.error(
            message="启动失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    def generate_meditation_guidance(self, session_data):
        """生成冥想指导内容"""
        session_type = session_data['session_type']
        duration = session_data['duration']
        
        guidance_templates = {
            'breathing': f"请专注于您的呼吸。吸气时数1，呼气时数2，持续{duration}分钟。",
            'body_scan': f"请从头部开始，逐步扫描身体的每个部位，感受身体的感受，持续{duration}分钟。",
            'loving_kindness': f"请在心中默念：愿我平安，愿我健康，愿我快乐。然后将这份祝福送给他人，持续{duration}分钟。",
            'mindfulness': f"请专注于当下，观察您的想法和感受，不要评判，只是观察，持续{duration}分钟。",
            'sleep': f"请放松身体，从脚趾开始，逐步放松每个肌肉群，让身体进入深度放松状态，持续{duration}分钟。",
        }
        
        return guidance_templates.get(session_type, "请专注于当下，保持正念。")


class AIWritingViewSet(viewsets.ViewSet):
    """AI文案生成"""
    permission_classes = [IsAuthenticated, FeaturePermission('ai_writing')]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """生成AI文案"""
        serializer = AIWritingSerializer(data=request.data)
        if serializer.is_valid():
            content_data = serializer.validated_data
            
            # 这里可以集成AI文案生成服务
            # 暂时返回模拟内容
            generated_content = self.generate_content(content_data)
            
            return APIResponse.success(
                data={
                    'content': generated_content,
                    'content_type': content_data['content_type'],
                    'topic': content_data['topic'],
                    'style': content_data.get('style', 'casual')
                },
                message="文案生成成功"
            )
        return APIResponse.error(
            message="生成失败",
            errors=serializer.errors,
            code=APIErrorCodes.VALIDATION_ERROR
        )
    
    def generate_content(self, content_data):
        """生成内容（模拟）"""
        content_type = content_data['content_type']
        topic = content_data['topic']
        style = content_data.get('style', 'casual')
        
        templates = {
            'diary': f"今天关于{topic}的思考：这是一个值得记录的时刻...",
            'poem': f"关于{topic}的诗：\n\n在{style}的笔触下，\n{topic}如诗如画...",
            'story': f"故事：{topic}\n\n在一个{style}的午后，关于{topic}的故事开始了...",
            'article': f"文章：{topic}\n\n{style}风格的文章内容，深入探讨{topic}的各个方面...",
            'social_media': f"社交媒体内容：\n\n{topic} #生活 #思考 #{style}",
            'email': f"邮件主题：关于{topic}\n\n{style}的邮件内容，讨论{topic}相关事宜...",
        }
        
        return templates.get(content_type, f"关于{topic}的{content_type}内容")
