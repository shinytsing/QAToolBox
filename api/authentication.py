"""
JWT认证配置
"""
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .response import APIErrorCodes

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """JWT认证类"""
    
    def authenticate(self, request):
        """认证用户"""
        token = self.get_token_from_request(request)
        if not token:
            return None
            
        try:
            payload = self.decode_token(token)
            user = self.get_user_from_payload(payload)
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token已过期", code=APIErrorCodes.TOKEN_EXPIRED)
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Token无效", code=APIErrorCodes.TOKEN_INVALID)
        except User.DoesNotExist:
            raise AuthenticationFailed("用户不存在", code=APIErrorCodes.USER_NOT_FOUND)
    
    def get_token_from_request(self, request):
        """从请求中获取Token"""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None
    
    def decode_token(self, token):
        """解码JWT Token"""
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=['HS256']
        )
    
    def get_user_from_payload(self, payload):
        """从payload中获取用户"""
        user_id = payload.get('user_id')
        if not user_id:
            raise AuthenticationFailed("Token中缺少用户ID")
        
        user = User.objects.get(id=user_id)
        if not user.is_active:
            raise AuthenticationFailed("用户已被禁用", code=APIErrorCodes.USER_DISABLED)
        
        return user


class JWTTokenGenerator:
    """JWT Token生成器"""
    
    @staticmethod
    def generate_tokens(user):
        """生成访问令牌和刷新令牌"""
        now = datetime.utcnow()
        
        # 访问令牌 (1小时过期)
        access_payload = {
            'user_id': user.id,
            'username': user.username,
            'type': 'access',
            'iat': now,
            'exp': now + timedelta(hours=1)
        }
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # 刷新令牌 (7天过期)
        refresh_payload = {
            'user_id': user.id,
            'username': user.username,
            'type': 'refresh',
            'iat': now,
            'exp': now + timedelta(days=7)
        }
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """刷新访问令牌"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                raise AuthenticationFailed("无效的刷新令牌")
            
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                raise AuthenticationFailed("用户已被禁用")
            
            return JWTTokenGenerator.generate_tokens(user)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("刷新令牌已过期")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("无效的刷新令牌")
        except User.DoesNotExist:
            raise AuthenticationFailed("用户不存在")
