"""
WebSocket路由配置

定义WebSocket连接的URL路由。
"""

from django.urls import re_path
from . import consumers
from .test_consumer import SimpleTestConsumer

websocket_urlpatterns = [
    # 简单测试WebSocket
    re_path(r'ws/test/$', SimpleTestConsumer.as_asgi()),
    
    # 聊天WebSocket - 连接到特定会话
    re_path(r'ws/chat/(?P<conversation_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    
    # 通知WebSocket - 用户全局通知
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]