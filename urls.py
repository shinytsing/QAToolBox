"""
URL configuration for ModeShift project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from views import home_view, tool_view, welcome_view, theme_demo_view, custom_static_serve
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

def music_test_view(request):
    """音乐功能测试页面"""
    return render(request, 'music_test.html')

def audio_test_view(request):
    """音频播放测试页面"""
    return render(request, 'audio_test.html')

def next_song_test_view(request):
    """切换歌曲功能测试页面"""
    return render(request, 'test_next_song.html')

def modern_demo_view(request):
    """现代化UI演示页面"""
    return render(request, 'modern_demo.html')

def feedback_restriction_test_view(request):
    """反馈功能登录限制测试页面"""
    return render(request, 'test_feedback_restriction.html')

def cyberpunk_theme_test_view(request):
    """赛博哥特主题测试页面"""
    return render(request, 'test_cyberpunk_theme.html')

def anti_programmer_desire_test_view(request):
    """反程序员档案和欲望代办测试页面"""
    return render(request, 'test_anti_programmer_desire.html')

urlpatterns = [
    path('', home_view, name='home'),
    path('welcome/', welcome_view, name='welcome'),
    path('theme-demo/', theme_demo_view, name='theme_demo'),
    path('modern-demo/', modern_demo_view, name='modern_demo'),
    path('music-test/', music_test_view, name='music_test'),
    path('audio-test/', audio_test_view, name='audio_test'),
    path('next-song-test/', next_song_test_view, name='next_song_test'),
    path('feedback-restriction-test/', feedback_restriction_test_view, name='feedback_restriction_test'),
    path('cyberpunk-theme-test/', cyberpunk_theme_test_view, name='cyberpunk_theme_test'),
    path('test-anti-programmer-desire/', anti_programmer_desire_test_view, name='anti_programmer_desire_test'),
    path('admin/', admin.site.urls),
    # 工具主页面路由
    # 工具子路由（包含测试用例生成器等）
    path('tools/', include('apps.tools.urls')),
    path('users/', include('apps.users.urls')),
    path('content/', include('apps.content.urls')),
    # Favicon路由
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
]

# 开发环境下提供媒体文件访问和debug_toolbar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 自定义静态文件服务，禁用缓存
    urlpatterns += [
        path('static/<path:path>', custom_static_serve, name='custom_static'),
    ]
    try:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
    except ImportError:
        pass