"""
WebSocket消费者

提供实时聊天功能的WebSocket支持，包括：
- 实时消息推送
- 任务状态更新
- Agent响应流式输出
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatConversation, ChatMessage, ChatAgentTask


User = get_user_model()
logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """聊天WebSocket消费者"""
    
    async def connect(self):
        """建立WebSocket连接"""
        
        # 获取会话ID
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user = self.scope['user']
        
        # 验证用户认证
        if not self.user.is_authenticated:
            await self.close(code=4001)  # 未认证错误
            return
        
        # 验证会话权限
        conversation = await self.get_conversation()
        if not conversation:
            await self.close(code=4004)  # 会话不存在或无权限
            return
        
        # 加入会话群组
        self.conversation_group_name = f'chat_{self.conversation_id}'
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        # 接受连接
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'conversation_id': self.conversation_id,
            'message': '连接成功'
        }))
        
        logger.info(f"用户 {self.user.username} 连接到会话 {self.conversation_id}")
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        
        # 离开会话群组
        if hasattr(self, 'conversation_group_name'):
            await self.channel_layer.group_discard(
                self.conversation_group_name,
                self.channel_name
            )
        
        logger.info(f"用户 {self.user.username if hasattr(self, 'user') else 'Unknown'} 断开连接，代码: {close_code}")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            # 根据消息类型处理
            if message_type == 'send_message':
                await self.handle_send_message(data)
            elif message_type == 'typing_start':
                await self.handle_typing_start(data)
            elif message_type == 'typing_stop':
                await self.handle_typing_stop(data)
            elif message_type == 'ping':
                await self.handle_ping(data)
            else:
                await self.send_error(f"未知的消息类型: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("无效的JSON格式")
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
            await self.send_error(f"处理消息失败: {str(e)}")
    
    async def handle_send_message(self, data):
        """处理发送消息请求"""
        
        content = data.get('content', '').strip()
        if not content:
            await self.send_error("消息内容不能为空")
            return
        
        try:
            # 获取会话
            conversation = await self.get_conversation()
            if not conversation:
                await self.send_error("会话不存在")
                return
            
            # 创建用户消息
            user_message = await self.create_user_message(conversation, content)
            
            # 广播新消息
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'new_message',
                    'message': await self.serialize_message(user_message)
                }
            )
            
            # 触发Agent处理（这里使用简单的模拟）
            await self.trigger_agent_response(conversation, user_message)
            
        except Exception as e:
            logger.error(f"处理发送消息失败: {e}")
            await self.send_error(f"发送消息失败: {str(e)}")
    
    async def handle_typing_start(self, data):
        """处理开始输入事件"""
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': True
            }
        )
    
    async def handle_typing_stop(self, data):
        """处理停止输入事件"""
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': False
            }
        )
    
    async def handle_ping(self, data):
        """处理心跳包"""
        
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': data.get('timestamp')
        }))
    
    async def new_message(self, event):
        """广播新消息"""
        
        await self.send(text_data=json.dumps({
            'type': 'new_message',
            'message': event['message']
        }))
    
    async def typing_status(self, event):
        """广播输入状态"""
        
        # 不向自己发送输入状态
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_status',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing']
            }))
    
    async def agent_thinking(self, event):
        """广播Agent思考状态"""
        
        await self.send(text_data=json.dumps({
            'type': 'agent_thinking',
            'agent_id': event['agent_id'],
            'agent_name': event['agent_name'],
            'is_thinking': event['is_thinking']
        }))
    
    async def task_status_update(self, event):
        """广播任务状态更新"""
        
        await self.send(text_data=json.dumps({
            'type': 'task_status_update',
            'task': event['task']
        }))
    
    async def send_error(self, error_message):
        """发送错误消息"""
        
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    @database_sync_to_async
    def get_conversation(self):
        """获取会话对象"""
        
        try:
            return ChatConversation.objects.select_related('primary_agent').get(
                id=self.conversation_id,
                user=self.user
            )
        except ChatConversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_user_message(self, conversation, content):
        """创建用户消息"""
        
        return ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=content,
            status='sent'
        )
    
    @database_sync_to_async
    def create_assistant_message(self, conversation, content, agent=None):
        """创建助手消息"""
        
        return ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=content,
            agent=agent,
            agent_name=agent.name if agent else 'Assistant',
            status='completed'
        )
    
    @database_sync_to_async
    def serialize_message(self, message):
        """序列化消息对象"""
        
        return {
            'id': message.id,
            'conversation_id': message.conversation_id,
            'role': message.role,
            'content': message.content,
            'agent_id': message.agent_id,
            'agent_name': message.agent_name,
            'status': message.status,
            'error_message': message.error_message,
            'created_at': message.created_at.isoformat(),
            'updated_at': message.updated_at.isoformat()
        }
    
    async def trigger_agent_response(self, conversation, user_message):
        """触发Agent响应（简化版本）"""
        
        try:
            # 发送Agent思考状态
            agent = conversation.primary_agent
            if agent:
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        'type': 'agent_thinking',
                        'agent_id': agent.id,
                        'agent_name': agent.name,
                        'is_thinking': True
                    }
                )
                
                # 模拟思考时间
                import asyncio
                await asyncio.sleep(2)
                
                # 生成模拟响应
                mock_responses = [
                    f"我理解您的问题：{user_message.content}",
                    "这是一个很有趣的问题，让我来为您分析一下...",
                    "基于我的理解，我建议...",
                    "让我来帮您解决这个问题。",
                ]
                
                import random
                response_content = random.choice(mock_responses)
                
                # 创建助手消息
                assistant_message = await self.create_assistant_message(
                    conversation, response_content, agent
                )
                
                # 停止思考状态
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        'type': 'agent_thinking',
                        'agent_id': agent.id,
                        'agent_name': agent.name,
                        'is_thinking': False
                    }
                )
                
                # 广播助手消息
                await self.channel_layer.group_send(
                    self.conversation_group_name,
                    {
                        'type': 'new_message',
                        'message': await self.serialize_message(assistant_message)
                    }
                )
                
        except Exception as e:
            logger.error(f"触发Agent响应失败: {e}")


class NotificationConsumer(AsyncWebsocketConsumer):
    """通知消费者（用于全局通知）"""
    
    async def connect(self):
        """建立连接"""
        
        self.user = self.scope['user']
        
        # 验证用户认证
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # 加入用户通知群组
        self.notification_group_name = f'user_{self.user.id}_notifications'
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'message': '通知服务已连接'
        }))
    
    async def disconnect(self, close_code):
        """断开连接"""
        
        # 离开通知群组
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )
    
    async def notification_message(self, event):
        """发送通知消息"""
        
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))