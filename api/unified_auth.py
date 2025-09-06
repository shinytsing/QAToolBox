"""
统一账户登录机制
支持多端登录状态同步和数据共享
"""
import json
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db import models
from api.models import LoginSession
from rest_framework import serializers
from api.response import APIResponse, APIErrorCodes

User = get_user_model()


class DeviceType:
    """设备类型常量"""
    WEB = 'web'
    MINIPROGRAM_WECHAT = 'miniprogram_wechat'
    MINIPROGRAM_ALIPAY = 'miniprogram_alipay'
    MOBILE_FITNESS = 'mobile_fitness'
    MOBILE_LIFE = 'mobile_life'
    MOBILE_GEEK = 'mobile_geek'
    MOBILE_SOCIAL = 'mobile_social'
    ADMIN = 'admin'


# LoginSession 模型已移至 api.models 中


class UnifiedAuthService:
    """统一认证服务"""
    
    @staticmethod
    def create_login_session(user, device_info, request):
        """创建登录会话"""
        device_id = device_info.get('device_id', str(uuid.uuid4()))
        device_type = device_info.get('device_type', DeviceType.WEB)
        device_name = device_info.get('device_name', 'Unknown Device')
        platform = device_info.get('platform', 'web')
        app_version = device_info.get('app_version', '1.0.0')
        
        # 获取客户端IP
        ip_address = UnifiedAuthService.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # 确保 device_id 不为空
        if not device_id:
            device_id = str(uuid.uuid4())
        
        # 创建或更新会话
        session, created = LoginSession.objects.get_or_create(
            device_id=device_id,
            defaults={
                'user': user,
                'device_type': device_type,
                'device_name': device_name,
                'platform': platform,
                'app_version': app_version,
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        if not created:
            # 更新现有会话
            session.user = user
            session.device_type = device_type
            session.device_name = device_name
            session.platform = platform
            session.app_version = app_version
            session.ip_address = ip_address
            session.user_agent = user_agent
            session.is_active = True
            session.last_activity = datetime.now()
            session.save()
        
        return session
    
    @staticmethod
    def get_client_ip(request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_user_sessions(user):
        """获取用户所有活跃会话"""
        return LoginSession.objects.filter(
            user=user,
            is_active=True
        ).order_by('-last_activity')
    
    @staticmethod
    def terminate_session(device_id, user=None):
        """终止指定会话"""
        try:
            session = LoginSession.objects.get(device_id=device_id)
            if user and session.user != user:
                return False
            session.is_active = False
            session.save()
            return True
        except LoginSession.DoesNotExist:
            return False
    
    @staticmethod
    def terminate_all_sessions(user, exclude_device_id=None):
        """终止用户所有会话（除指定设备）"""
        sessions = LoginSession.objects.filter(user=user, is_active=True)
        if exclude_device_id:
            sessions = sessions.exclude(device_id=exclude_device_id)
        
        sessions.update(is_active=False)
        return sessions.count()
    
    @staticmethod
    def sync_user_data(user, data_type, data):
        """同步用户数据到所有设备"""
        # 将数据推送到所有活跃设备
        sessions = UnifiedAuthService.get_user_sessions(user)
        
        sync_data = {
            'user_id': user.id,
            'data_type': data_type,
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'sync_id': str(uuid.uuid4())
        }
        
        # 这里可以集成WebSocket或推送服务
        # 暂时使用缓存存储同步数据
        for session in sessions:
            cache_key = f"sync_data_{session.device_id}"
            cache.set(cache_key, sync_data, timeout=300)  # 5分钟过期
        
        return sync_data
    
    @staticmethod
    def get_sync_data(device_id):
        """获取设备同步数据"""
        cache_key = f"sync_data_{device_id}"
        return cache.get(cache_key)
    
    @staticmethod
    def validate_device_access(user, device_type, required_permissions=None):
        """验证设备访问权限"""
        # 检查用户是否有权限使用该设备类型
        if not user.is_active:
            return False, "用户已被禁用"
        
        # 检查功能权限
        if required_permissions:
            for permission in required_permissions:
                if not UnifiedAuthService.check_feature_permission(user, permission):
                    return False, f"缺少权限: {permission}"
        
        return True, "验证通过"
    
    @staticmethod
    def check_feature_permission(user, feature_key):
        """检查功能权限"""
        # 简化权限检查：所有活跃用户都有基本权限
        if user.is_active:
            return True
        return False


class UnifiedLoginSerializer(serializers.Serializer):
    """统一登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField()
    device_id = serializers.CharField(required=False)
    device_type = serializers.ChoiceField(choices=[
        (DeviceType.WEB, 'Web端'),
        (DeviceType.MINIPROGRAM_WECHAT, '微信小程序'),
        (DeviceType.MINIPROGRAM_ALIPAY, '支付宝小程序'),
        (DeviceType.MOBILE_FITNESS, '健身App'),
        (DeviceType.MOBILE_LIFE, '生活App'),
        (DeviceType.MOBILE_GEEK, '极客App'),
        (DeviceType.MOBILE_SOCIAL, '社交App'),
        (DeviceType.ADMIN, '管理端'),
    ], default=DeviceType.WEB)
    device_name = serializers.CharField(required=False, default='Unknown Device')
    platform = serializers.CharField(required=False, default='web')
    app_version = serializers.CharField(required=False, default='1.0.0')
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            if not user.is_active:
                raise serializers.ValidationError("用户已被禁用")
            attrs['user'] = user
        else:
            raise serializers.ValidationError("用户名和密码不能为空")
        
        return attrs


class DeviceInfoSerializer(serializers.ModelSerializer):
    """设备信息序列化器"""
    
    class Meta:
        model = LoginSession
        fields = [
            'device_id', 'device_type', 'device_name', 'platform',
            'app_version', 'ip_address', 'last_activity', 'created_at'
        ]
        read_only_fields = ['ip_address', 'last_activity', 'created_at']


class UnifiedAuthAPI:
    """统一认证API"""
    
    @staticmethod
    def unified_login(request):
        """统一登录接口"""
        serializer = UnifiedLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(
                message="登录失败",
                errors=serializer.errors,
                code=APIErrorCodes.VALIDATION_ERROR
            )
        
        user = serializer.validated_data['user']
        device_info = {
            'device_id': serializer.validated_data.get('device_id'),
            'device_type': serializer.validated_data.get('device_type'),
            'device_name': serializer.validated_data.get('device_name'),
            'platform': serializer.validated_data.get('platform'),
            'app_version': serializer.validated_data.get('app_version'),
        }
        
        # 验证设备访问权限
        device_type = device_info['device_type']
        required_permissions = UnifiedAuthAPI.get_required_permissions(device_type)
        
        is_valid, message = UnifiedAuthService.validate_device_access(
            user, device_type, required_permissions
        )
        
        if not is_valid:
            return APIResponse.error(
                message=message,
                code=APIErrorCodes.INSUFFICIENT_PERMISSIONS
            )
        
        # 创建登录会话
        session = UnifiedAuthService.create_login_session(user, device_info, request)
        
        # 生成JWT令牌
        from api.authentication import JWTTokenGenerator
        tokens = JWTTokenGenerator.generate_tokens(user)
        
        # 获取用户所有设备信息
        user_sessions = UnifiedAuthService.get_user_sessions(user)
        device_serializer = DeviceInfoSerializer(user_sessions, many=True)
        
        return APIResponse.success(
            data={
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_staff': user.is_staff,
                },
                'tokens': tokens,
                'current_device': {
                    'device_id': session.device_id,
                    'device_type': session.device_type,
                    'device_name': session.device_name,
                },
                'devices': device_serializer.data,
            },
            message="登录成功"
        )
    
    @staticmethod
    def get_required_permissions(device_type):
        """获取设备类型所需权限"""
        permission_map = {
            DeviceType.WEB: ['web_access'],
            DeviceType.MINIPROGRAM_WECHAT: ['miniprogram_access'],
            DeviceType.MINIPROGRAM_ALIPAY: ['miniprogram_access'],
            DeviceType.MOBILE_FITNESS: ['fitness_center'],
            DeviceType.MOBILE_LIFE: ['life_diary', 'meditation_guide'],
            DeviceType.MOBILE_GEEK: ['pdf_converter', 'web_crawler'],
            DeviceType.MOBILE_SOCIAL: ['chat_room', 'heart_link'],
            DeviceType.ADMIN: ['admin_access'],
        }
        return permission_map.get(device_type, [])
    
    @staticmethod
    def get_user_devices(request):
        """获取用户设备列表"""
        user = request.user
        sessions = UnifiedAuthService.get_user_sessions(user)
        serializer = DeviceInfoSerializer(sessions, many=True)
        
        return APIResponse.success(data=serializer.data)
    
    @staticmethod
    def terminate_device(request, device_id):
        """终止指定设备登录"""
        user = request.user
        success = UnifiedAuthService.terminate_session(device_id, user)
        
        if success:
            return APIResponse.success(message="设备已下线")
        else:
            return APIResponse.error(
                message="设备不存在或无权限",
                code=APIErrorCodes.NOT_FOUND
            )
    
    @staticmethod
    def terminate_all_devices(request):
        """终止所有设备登录（除当前设备）"""
        user = request.user
        current_device_id = request.META.get('HTTP_X_DEVICE_ID')
        
        count = UnifiedAuthService.terminate_all_sessions(user, current_device_id)
        
        return APIResponse.success(
            data={'terminated_count': count},
            message=f"已下线 {count} 个设备"
        )
    
    @staticmethod
    def sync_data(request):
        """获取同步数据"""
        device_id = request.META.get('HTTP_X_DEVICE_ID')
        if not device_id:
            return APIResponse.error(
                message="缺少设备ID",
                code=APIErrorCodes.BAD_REQUEST
            )
        
        sync_data = UnifiedAuthService.get_sync_data(device_id)
        if sync_data:
            return APIResponse.success(data=sync_data)
        else:
            return APIResponse.success(data=None, message="无同步数据")
