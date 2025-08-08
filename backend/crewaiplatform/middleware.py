"""
WebSocket认证中间件

为WebSocket连接提供JWT令牌认证支持
"""

from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class JWTAuthMiddleware:
    """JWT认证中间件，用于WebSocket连接"""
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        return await JWTAuthMiddlewareInstance(scope, self)(receive, send)


class JWTAuthMiddlewareInstance:
    """JWT认证中间件实例"""
    
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner
    
    async def __call__(self, receive, send):
        # 关闭数据库连接以避免连接泄漏
        close_old_connections()
        
        # 从查询参数中获取token
        query_string = self.scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        
        logger.info(f"WebSocket连接请求，查询参数: {query_params}")
        
        token = None
        user = AnonymousUser()
        
        # 尝试从查询参数获取token
        if 'token' in query_params:
            token = query_params['token'][0]
            logger.info("找到token参数")
        else:
            logger.warning("没有找到token参数")
        
        if token:
            try:
                # 验证JWT令牌
                UntypedToken(token)
                logger.info("JWT令牌验证成功")
                
                # 解码令牌获取用户ID
                decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded_data.get('user_id')
                logger.info(f"解码JWT成功，用户ID: {user_id}")
                
                if user_id:
                    # 获取用户对象（确保user_id是整数）
                    try:
                        user = await self.get_user(int(user_id))
                        logger.info(f"WebSocket JWT认证成功，用户: {user.username}")
                    except User.DoesNotExist:
                        logger.warning(f"JWT令牌中的用户ID {user_id} 不存在")
                        user = AnonymousUser()
                    except Exception as e:
                        logger.error(f"获取用户时出错: {e}")
                        user = AnonymousUser()
                else:
                    logger.warning("JWT令牌中没有用户ID")
                    user = AnonymousUser()
                    
            except (InvalidToken, TokenError) as e:
                logger.warning(f"WebSocket JWT认证失败: {e}")
                user = AnonymousUser()
            except Exception as e:
                logger.error(f"WebSocket JWT处理异常: {e}")
                import traceback
                traceback.print_exc()
                user = AnonymousUser()
        else:
            logger.info("WebSocket连接没有提供JWT令牌")
        
        # 将用户添加到scope中
        self.scope['user'] = user
        logger.info(f"设置用户到scope: {user} (authenticated: {user.is_authenticated})")
        
        # 调用下一个中间件
        try:
            return await self.inner(self.scope, receive, send)
        except Exception as e:
            logger.error(f"调用下一个中间件时出错: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def get_user(self, user_id):
        """异步获取用户对象"""
        from channels.db import database_sync_to_async
        
        return await database_sync_to_async(User.objects.get)(pk=user_id)


def JWTAuthMiddlewareStack(inner):
    """JWT认证中间件栈"""
    return JWTAuthMiddleware(inner)