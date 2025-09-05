"""
管理模块视图
"""
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api.response import APIResponse, APIErrorCodes
from api.permissions import IsAdminUser
from .serializers import (
    UserManagementSerializer, FeatureManagementSerializer,
    UserFeatureAccessSerializer, SystemStatsSerializer,
    AnalyticsDataSerializer, LogEntrySerializer, NotificationSerializer
)
from apps.content.models import FeatureAccess, UserFeatureAccess


class UserManagementViewSet(viewsets.ModelViewSet):
    """用户管理"""
    serializer_class = UserManagementSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')
    
    def list(self, request, *args, **kwargs):
        """获取用户列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_staff = request.query_params.get('is_staff')
        if is_staff is not None:
            queryset = queryset.filter(is_staff=is_staff.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换用户激活状态"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = "激活" if user.is_active else "禁用"
        return APIResponse.success(
            message=f"用户已{status_text}"
        )
    
    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """修改用户角色"""
        user = self.get_object()
        role = request.data.get('role')
        
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif role == 'staff':
            user.is_staff = True
            user.is_superuser = False
        else:  # user
            user.is_staff = False
            user.is_superuser = False
        
        user.save()
        
        return APIResponse.success(
            message=f"用户角色已修改为{role}"
        )
    
    @action(detail=True, methods=['get'])
    def features(self, request, pk=None):
        """获取用户功能权限"""
        user = self.get_object()
        user_features = UserFeatureAccess.objects.filter(user=user)
        serializer = UserFeatureAccessSerializer(user_features, many=True)
        
        return APIResponse.success(data=serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_feature_access(self, request, pk=None):
        """更新用户功能权限"""
        user = self.get_object()
        feature_id = request.data.get('feature_id')
        is_enabled = request.data.get('is_enabled', True)
        
        try:
            feature = FeatureAccess.objects.get(id=feature_id)
            user_feature, created = UserFeatureAccess.objects.get_or_create(
                user=user,
                feature=feature,
                defaults={'is_enabled': is_enabled}
            )
            
            if not created:
                user_feature.is_enabled = is_enabled
                user_feature.save()
            
            return APIResponse.success(
                message="功能权限已更新"
            )
        except FeatureAccess.DoesNotExist:
            return APIResponse.error(
                message="功能不存在",
                code=APIErrorCodes.NOT_FOUND
            )


class FeatureManagementViewSet(viewsets.ModelViewSet):
    """功能管理"""
    serializer_class = FeatureManagementSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        return FeatureAccess.objects.all().order_by('sort_order', 'feature_name')
    
    def list(self, request, *args, **kwargs):
        """获取功能列表"""
        queryset = self.get_queryset()
        
        # 过滤条件
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        visibility = request.query_params.get('visibility')
        if visibility:
            queryset = queryset.filter(visibility=visibility)
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse.success(data=serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """切换功能状态"""
        feature = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in ['enabled', 'disabled', 'maintenance', 'beta']:
            feature.status = new_status
            feature.save()
            
            return APIResponse.success(
                message=f"功能状态已修改为{new_status}"
            )
        else:
            return APIResponse.error(
                message="无效的状态值",
                code=APIErrorCodes.VALIDATION_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """切换功能激活状态"""
        feature = self.get_object()
        feature.is_active = not feature.is_active
        feature.save()
        
        status_text = "激活" if feature.is_active else "禁用"
        return APIResponse.success(
            message=f"功能已{status_text}"
        )
    
    @action(detail=False, methods=['post'])
    def batch_update(self, request):
        """批量更新功能"""
        feature_ids = request.data.get('feature_ids', [])
        updates = request.data.get('updates', {})
        
        if not feature_ids:
            return APIResponse.error(
                message="请选择要更新的功能",
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        updated_count = FeatureAccess.objects.filter(
            id__in=feature_ids
        ).update(**updates)
        
        return APIResponse.success(
            data={'updated_count': updated_count},
            message=f"已更新{updated_count}个功能"
        )


class SystemStatsViewSet(viewsets.ViewSet):
    """系统统计"""
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取系统概览"""
        # 用户统计
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # 功能统计
        total_features = FeatureAccess.objects.count()
        enabled_features = FeatureAccess.objects.filter(is_active=True).count()
        
        # API调用统计（模拟数据）
        total_api_calls = 10000
        today_api_calls = 500
        
        # 存储使用情况（模拟数据）
        storage_used = "2.5 GB"
        
        # 系统运行时间（模拟数据）
        system_uptime = "15天 8小时 32分钟"
        
        stats = {
            'total_users': total_users,
            'active_users': active_users,
            'total_features': total_features,
            'enabled_features': enabled_features,
            'total_api_calls': total_api_calls,
            'today_api_calls': today_api_calls,
            'storage_used': storage_used,
            'system_uptime': system_uptime,
        }
        
        serializer = SystemStatsSerializer(stats)
        return APIResponse.success(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """获取分析数据"""
        days = int(request.query_params.get('days', 7))
        
        # 生成模拟分析数据
        analytics_data = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            analytics_data.append({
                'date': date,
                'users': random.randint(50, 200),
                'api_calls': random.randint(1000, 5000),
                'features_used': random.randint(20, 100),
                'errors': random.randint(0, 10),
            })
        
        serializer = AnalyticsDataSerializer(analytics_data, many=True)
        return APIResponse.success(data=serializer.data)
    
    @action(detail=False, methods=['get'])
    def logs(self, request):
        """获取系统日志"""
        level = request.query_params.get('level')
        limit = int(request.query_params.get('limit', 100))
        
        # 生成模拟日志数据
        log_levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
        if level:
            log_levels = [level]
        
        logs = []
        for i in range(limit):
            logs.append({
                'timestamp': datetime.now() - timedelta(minutes=i),
                'level': random.choice(log_levels),
                'message': f'系统日志消息 {i+1}',
                'user': f'user{i+1}' if i % 3 == 0 else None,
                'ip_address': f'192.168.1.{i % 255}',
                'user_agent': 'Mozilla/5.0...' if i % 2 == 0 else None,
            })
        
        serializer = LogEntrySerializer(logs, many=True)
        return APIResponse.success(data=serializer.data)


class NotificationViewSet(viewsets.ViewSet):
    """通知管理"""
    permission_classes = [IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def send(self, request):
        """发送通知"""
        serializer = NotificationSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="参数验证失败",
                errors=serializer.errors,
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        data = serializer.validated_data
        
        # 这里应该实现实际的通知发送逻辑
        # 例如：发送邮件、推送通知、站内消息等
        
        notification_id = str(uuid.uuid4())
        
        return APIResponse.success(
            data={'notification_id': notification_id},
            message="通知发送成功"
        )
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取通知历史"""
        # 生成模拟通知历史
        notifications = [
            {
                'id': str(uuid.uuid4()),
                'title': '系统维护通知',
                'message': '系统将于今晚进行维护，预计2小时',
                'type': 'info',
                'created_at': datetime.now() - timedelta(hours=2),
                'status': 'sent'
            },
            {
                'id': str(uuid.uuid4()),
                'title': '新功能上线',
                'message': '极客工具模块已上线，欢迎使用',
                'type': 'success',
                'created_at': datetime.now() - timedelta(days=1),
                'status': 'sent'
            }
        ]
        
        return APIResponse.success(data=notifications)
