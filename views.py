from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.static import serve
from django.conf import settings
import os

@login_required  # 仅允许登录用户访问
def tool_view(request):
    # 获取用户偏好模式
    try:
        from apps.users.models import UserModePreference
        preferred_mode = UserModePreference.get_user_preferred_mode(request.user)
    except:
        preferred_mode = 'work'  # 默认极客模式
    
    context = {
        'preferred_mode': preferred_mode,
        'mode_names': {
            'work': '极客模式',
            'life': '生活模式',
            'training': '狂暴模式',
            'emo': 'Emo模式'
        }
    }
    
    return render(request, 'tool.html', context)  # 确保这里指向你的工具模板

# 添加一个根视图函数
def home_view(request):
    return render(request, 'home.html')  # 显示首页

def welcome_view(request):
    return render(request, 'welcome.html')

def theme_demo_view(request):
    return render(request, 'theme_demo.html')

def version_history_view(request):
    """版本迭代记录页面"""
    return render(request, 'version_history.html')

def help_page_view(request):
    """帮助中心页面"""
    return render(request, 'tools/help_page.html')

def custom_static_serve(request, path):
    """自定义静态文件服务，禁用缓存"""
    response = serve(request, path, document_root=settings.STATIC_ROOT)
    # 添加缓存控制头，禁用缓存
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response