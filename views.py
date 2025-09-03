from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, FileResponse
from django.views.static import serve
from django.conf import settings
import os
import mimetypes

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

def public_media_serve(request, path):
    """公共媒体文件服务，无需登录验证"""
    try:
        # 检查文件路径是否在媒体目录内
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(full_path):
            raise Http404("文件不存在")
        
        # 获取文件信息
        file_size = os.path.getsize(full_path)
        file_name = os.path.basename(full_path)
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # 创建文件响应
        response = FileResponse(open(full_path, 'rb'), content_type=mime_type)
        
        # 设置响应头
        response['Content-Length'] = file_size
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        return response
        
    except Exception as e:
        raise Http404("文件访问错误")

@login_required
def secure_media_serve(request, path):
    """安全的媒体文件服务，需要登录验证"""
    try:
        # 检查文件路径是否在媒体目录内
        full_path = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(full_path):
            raise Http404("文件不存在")
        
        # 检查文件是否在允许的目录内
        allowed_dirs = ['chat_images', 'chat_files', 'chat_audio', 'chat_videos', 'avatars']
        path_parts = path.split('/')
        
        # 允许根目录下的文件（如vx.jpg）
        if len(path_parts) == 1:
            # 根目录文件，允许访问
            pass
        elif not any(allowed_dir in path_parts for allowed_dir in allowed_dirs):
            raise Http404("无权访问此文件")
        
        # 获取文件信息
        file_size = os.path.getsize(full_path)
        file_name = os.path.basename(full_path)
        
        # 获取MIME类型
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        # 创建文件响应
        response = FileResponse(open(full_path, 'rb'), content_type=mime_type)
        
        # 设置响应头
        response['Content-Length'] = file_size
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        # 如果是图片，允许内联显示
        if mime_type.startswith('image/'):
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
        else:
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response
        
    except Exception as e:
        print(f"媒体文件服务错误: {e}")
        raise Http404("文件访问失败")