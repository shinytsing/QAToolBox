#!/usr/bin/env python3
"""
QAToolBox 移动端API增强脚本
为移动端和小程序添加必要的API接口和优化
"""

# 1. 移动端API视图增强
MOBILE_API_VIEWS = """
# apps/tools/mobile_api.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import json

@api_view(['POST'])
def mobile_login(request):
    \"\"\"移动端登录接口\"\"\"
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            },
            'token': 'session_based'  # 可以改为JWT token
        })
    else:
        return Response({
            'success': False,
            'message': '用户名或密码错误'
        }, status=400)

@api_view(['POST'])
def mobile_register(request):
    \"\"\"移动端注册接口\"\"\"
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    if User.objects.filter(username=username).exists():
        return Response({
            'success': False,
            'message': '用户名已存在'
        }, status=400)
    
    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        return Response({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }, status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_tools_list(request):
    \"\"\"移动端工具列表\"\"\"
    tools = [
        {
            'id': 'test_case_generator',
            'name': '测试用例生成器',
            'description': '智能生成测试用例',
            'icon': '🧪',
            'category': 'testing'
        },
        {
            'id': 'redbook_generator',
            'name': '小红书文案生成器',
            'description': '生成吸引人的小红书文案',
            'icon': '📝',
            'category': 'content'
        },
        {
            'id': 'pdf_converter',
            'name': 'PDF转换器',
            'description': '文档格式转换工具',
            'icon': '📄',
            'category': 'utility'
        },
        {
            'id': 'fitness_center',
            'name': '健身中心',
            'description': '个人健身管理',
            'icon': '💪',
            'category': 'health'
        },
        {
            'id': 'diary',
            'name': '智能日记',
            'description': '记录美好生活',
            'icon': '📖',
            'category': 'life'
        }
    ]
    
    return Response({
        'success': True,
        'tools': tools
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mobile_image_upload(request):
    \"\"\"移动端图片上传\"\"\"
    if 'image' not in request.FILES:
        return Response({
            'success': False,
            'message': '没有上传图片'
        }, status=400)
    
    image = request.FILES['image']
    
    # 保存图片
    file_name = default_storage.save(f'uploads/{image.name}', image)
    file_url = default_storage.url(file_name)
    
    return Response({
        'success': True,
        'file_url': file_url,
        'file_name': file_name
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mobile_user_profile(request):
    \"\"\"移动端用户信息\"\"\"
    user = request.user
    
    # 获取用户扩展信息
    profile_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'date_joined': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
    }
    
    # 尝试获取用户Profile
    try:
        from apps.users.models import Profile
        profile = Profile.objects.get(user=user)
        profile_data.update({
            'avatar': profile.avatar.url if profile.avatar else None,
            'phone': profile.phone,
        })
    except:
        pass
    
    return Response({
        'success': True,
        'profile': profile_data
    })
"""

# 2. 小程序专用API
MINIPROGRAM_API = """
# apps/tools/miniprogram_api.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests
import json

@api_view(['POST'])
def miniprogram_login(request):
    \"\"\"小程序登录\"\"\"
    code = request.data.get('code')
    
    # 这里需要配置小程序的AppID和AppSecret
    APPID = 'your_miniprogram_appid'
    SECRET = 'your_miniprogram_secret'
    
    # 获取session_key和openid
    url = f'https://api.weixin.qq.com/sns/jscode2session'
    params = {
        'appid': APPID,
        'secret': SECRET,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'openid' in data:
            # 创建或获取用户
            openid = data['openid']
            session_key = data.get('session_key')
            
            # 这里可以创建或更新用户信息
            return Response({
                'success': True,
                'openid': openid,
                'session_key': session_key
            })
        else:
            return Response({
                'success': False,
                'message': '登录失败',
                'error': data
            }, status=400)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': f'登录异常: {str(e)}'
        }, status=500)

@api_view(['GET'])
def miniprogram_config(request):
    \"\"\"小程序配置信息\"\"\"
    return Response({
        'success': True,
        'config': {
            'app_name': 'QAToolBox',
            'version': '1.0.0',
            'features': [
                'test_case_generator',
                'redbook_generator',
                'pdf_converter',
                'fitness_center',
                'diary'
            ],
            'theme': {
                'primary_color': '#667eea',
                'secondary_color': '#764ba2'
            }
        }
    })
"""

# 3. URL配置增强
URL_PATTERNS = """
# apps/tools/mobile_urls.py
from django.urls import path
from . import mobile_api, miniprogram_api

app_name = 'mobile'

urlpatterns = [
    # 移动端API
    path('api/mobile/login/', mobile_api.mobile_login, name='mobile_login'),
    path('api/mobile/register/', mobile_api.mobile_register, name='mobile_register'),
    path('api/mobile/tools/', mobile_api.mobile_tools_list, name='mobile_tools'),
    path('api/mobile/upload/', mobile_api.mobile_image_upload, name='mobile_upload'),
    path('api/mobile/profile/', mobile_api.mobile_user_profile, name='mobile_profile'),
    
    # 小程序API
    path('api/miniprogram/login/', miniprogram_api.miniprogram_login, name='miniprogram_login'),
    path('api/miniprogram/config/', miniprogram_api.miniprogram_config, name='miniprogram_config'),
]
"""

# 4. 设置优化
SETTINGS_ENHANCEMENT = """
# config/settings/mobile.py
from .base import *

# 移动端特殊配置
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# 允许的域名（包含小程序域名）
ALLOWED_HOSTS += [
    'servicewechat.com',  # 小程序域名
    '*.servicewechat.com',
]

# 文件上传配置
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

# 移动端Session配置
SESSION_COOKIE_AGE = 30 * 24 * 60 * 60  # 30天
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# API限流配置
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
"""

print("移动端API增强文件已生成！")
print("请按照以下步骤集成到项目中：")
print("1. 创建 apps/tools/mobile_api.py")
print("2. 创建 apps/tools/miniprogram_api.py") 
print("3. 创建 apps/tools/mobile_urls.py")
print("4. 在主urls.py中包含移动端路由")
print("5. 更新settings配置")


