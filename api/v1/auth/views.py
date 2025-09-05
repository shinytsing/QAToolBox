"""
认证模块视图
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.core.cache import cache

from api.response import APIResponse, APIErrorCodes
from api.authentication import JWTTokenGenerator
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register(request):
    """用户注册"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # 生成JWT令牌
        tokens = JWTTokenGenerator.generate_tokens(user)
        
        return APIResponse.success(
            data={
                'user': UserProfileSerializer(user.profile).data,
                'tokens': tokens
            },
            message="注册成功"
        )
    
    return APIResponse.error(
        message="注册失败",
        errors=serializer.errors,
        code=APIErrorCodes.VALIDATION_ERROR
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    """用户登录"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # 执行登录
        login(request, user)
        
        # 生成JWT令牌
        tokens = JWTTokenGenerator.generate_tokens(user)
        
        return APIResponse.success(
            data={
                'user': UserProfileSerializer(user.profile).data,
                'tokens': tokens
            },
            message="登录成功"
        )
    
    return APIResponse.error(
        message="登录失败",
        errors=serializer.errors,
        code=APIErrorCodes.INVALID_CREDENTIALS
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """用户登出"""
    logout(request)
    return APIResponse.success(message="登出成功")


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """刷新访问令牌"""
    refresh_token = request.data.get('refresh_token')
    if not refresh_token:
        return APIResponse.error(
            message="缺少刷新令牌",
            code=APIErrorCodes.BAD_REQUEST
        )
    
    try:
        tokens = JWTTokenGenerator.refresh_access_token(refresh_token)
        return APIResponse.success(data=tokens, message="令牌刷新成功")
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            code=APIErrorCodes.TOKEN_INVALID
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """获取用户资料"""
    serializer = UserProfileSerializer(request.user.profile)
    return APIResponse.success(data=serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """更新用户资料"""
    serializer = UserProfileSerializer(
        request.user.profile,
        data=request.data,
        partial=True
    )
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return APIResponse.success(message="密码修改成功")
    
    return APIResponse.error(
        message="密码修改失败",
        errors=serializer.errors,
        code=APIErrorCodes.VALIDATION_ERROR
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """忘记密码"""
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # 生成重置令牌
        reset_token = get_random_string(32)
        cache.set(f'reset_token_{reset_token}', user.id, timeout=3600)  # 1小时过期
        
        # 发送重置邮件
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        send_mail(
            subject='密码重置',
            message=f'请点击以下链接重置密码：{reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return APIResponse.success(message="重置邮件已发送")
    
    return APIResponse.error(
        message="发送失败",
        errors=serializer.errors,
        code=APIErrorCodes.VALIDATION_ERROR
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """重置密码"""
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # 验证令牌
        user_id = cache.get(f'reset_token_{token}')
        if not user_id:
            return APIResponse.error(
                message="重置令牌无效或已过期",
                code=APIErrorCodes.TOKEN_INVALID
            )
        
        # 重置密码
        user = User.objects.get(id=user_id)
        user.set_password(new_password)
        user.save()
        
        # 删除令牌
        cache.delete(f'reset_token_{token}')
        
        return APIResponse.success(message="密码重置成功")
    
    return APIResponse.error(
        message="重置失败",
        errors=serializer.errors,
        code=APIErrorCodes.VALIDATION_ERROR
    )
