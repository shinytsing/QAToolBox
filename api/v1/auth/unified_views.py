"""
统一认证API视图
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from api.response import APIResponse, APIErrorCodes
from api.unified_auth import UnifiedAuthAPI


@api_view(['POST'])
@permission_classes([AllowAny])
def unified_login(request):
    """统一登录接口 - 支持多端登录"""
    return UnifiedAuthAPI.unified_login(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_devices(request):
    """获取用户设备列表"""
    return UnifiedAuthAPI.get_user_devices(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_device(request, device_id):
    """终止指定设备登录"""
    return UnifiedAuthAPI.terminate_device(request, device_id)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_all_devices(request):
    """终止所有设备登录（除当前设备）"""
    return UnifiedAuthAPI.terminate_all_devices(request)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_data(request):
    """获取同步数据"""
    return UnifiedAuthAPI.sync_data(request)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_user_data(request):
    """同步用户数据到所有设备"""
    from api.unified_auth import UnifiedAuthService
    
    data_type = request.data.get('data_type')
    data = request.data.get('data')
    
    if not data_type or not data:
        return APIResponse.error(
            message="缺少数据类型或数据",
            code=APIErrorCodes.BAD_REQUEST
        )
    
    sync_data = UnifiedAuthService.sync_user_data(
        request.user, data_type, data
    )
    
    return APIResponse.success(
        data=sync_data,
        message="数据同步成功"
    )
