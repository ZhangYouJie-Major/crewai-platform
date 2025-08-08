"""
ASGI config for crewaiplatform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# 设置Django设置模块
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewaiplatform.settings")

# 获取Django ASGI应用
django_asgi_app = get_asgi_application()

# 导入WebSocket路由和JWT认证中间件
from .routing import websocket_urlpatterns
from .middleware import JWTAuthMiddlewareStack

# ASGI应用配置
application = ProtocolTypeRouter({
    # HTTP请求使用Django处理
    "http": django_asgi_app,
    
    # WebSocket请求使用JWT认证中间件
    "websocket": JWTAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
