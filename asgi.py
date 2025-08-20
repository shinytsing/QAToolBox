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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# 初始化Django
django.setup()

# 导入WebSocket路由（在Django设置后导入）
from apps.tools.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
