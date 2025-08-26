"""
QAToolBox 简化URL配置
避免复杂应用导入问题
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.http import JsonResponse

def health_check(request):
    """简单健康检查"""
    return JsonResponse({'status': 'ok', 'message': 'ModeShift is running'})

def home_view(request):
    """主页视图"""
    from django.shortcuts import render
    return render(request, 'home.html', {
        'title': 'ModeShift - Four Modes, One Beast',
        'modes': [
            {'name': '极客模式', 'icon': '🤖', 'color': 'cyan'},
            {'name': '生活模式', 'icon': '🌿', 'color': 'green'},
            {'name': '狂暴模式', 'icon': '🔥', 'color': 'red'},
            {'name': 'Emo模式', 'icon': '🎭', 'color': 'purple'},
        ]
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health'),
    path('', home_view, name='home'),
]

# 尝试包含其他应用URL（如果存在）
try:
    from apps.users.urls import urlpatterns as users_urls
    urlpatterns.append(path('users/', include('apps.users.urls')))
except (ImportError, ModuleNotFoundError):
    pass

try:
    from apps.content.urls import urlpatterns as content_urls
    urlpatterns.append(path('content/', include('apps.content.urls')))
except (ImportError, ModuleNotFoundError):
    pass

# 静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
