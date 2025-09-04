"""
ASGI config for QAToolBox project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 设置Django设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

# 初始化Django
django.setup()

# 导入WebSocket路由（在Django设置后导入）
try:
    from apps.tools.routing import websocket_urlpatterns

    print(f"✅ WebSocket路由加载成功，路由数量: {len(websocket_urlpatterns)}")
    for pattern in websocket_urlpatterns:
        print(f"📍 WebSocket路由: {pattern.pattern.regex.pattern}")
except Exception as e:
    print(f"❌ WebSocket路由加载失败: {e}")
    websocket_urlpatterns = []

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)

print("🚀 ASGI应用已配置完成")
