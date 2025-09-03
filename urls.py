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

import time
from django.contrib import admin
from django.urls import include, path
from apps.tools.views.health_views import HealthCheckView, DetailedHealthCheckView
from views import home_view, tool_view, welcome_view, theme_demo_view, version_history_view, help_page_view, custom_static_serve, secure_media_serve, public_media_serve
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

def modern_demo_view(request):
    """现代化UI演示页面"""
    return render(request, 'modern_demo.html')

def health_check_view(request):
    """健康检查视图"""
    from django.http import JsonResponse
    return JsonResponse({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('health/detailed/', DetailedHealthCheckView.as_view(), name='detailed_health_check'),
    path('', home_view, name='home'),
    path('welcome/', welcome_view, name='welcome'),
    path('theme-demo/', theme_demo_view, name='theme_demo'),
    path('modern-demo/', modern_demo_view, name='modern_demo'),

    path('version-history/', version_history_view, name='version_history'),
    path('help/', help_page_view, name='help_page'),
    path('admin/', admin.site.urls),
    # 工具主页面路由
    # 工具子路由（包含测试用例生成器等）
    path('tools/', include('apps.tools.urls', namespace='tools')),
    path('users/', include('apps.users.urls', namespace='users')),
    path('content/', include('apps.content.urls', namespace='content')),
    # path('share/', include('apps.share.urls')),
    # Favicon路由
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    # Apple Touch Icon路由
    path('apple-touch-icon.png', RedirectView.as_view(url='/static/apple-touch-icon.png', permanent=True)),
    path('apple-touch-icon-precomposed.png', RedirectView.as_view(url='/static/apple-touch-icon-precomposed.png', permanent=True)),
]

# 开发环境下提供媒体文件访问和debug_toolbar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # 使用Django标准静态文件服务
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    # 备用：直接使用staticfiles目录
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # 自定义静态文件服务，禁用缓存（备用）
    # urlpatterns += [
    #     path('static/<path:path>', custom_static_serve, name='custom_static'),
    # ]
    # 开发环境添加debug_toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        try:
            import debug_toolbar
            urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns
        except ImportError:
            pass
else:
    # 生产环境使用公共媒体文件服务
    urlpatterns += [
        path('media/<path:path>', public_media_serve, name='public_media'),
    ]