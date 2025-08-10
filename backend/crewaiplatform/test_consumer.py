"""
简单WebSocket测试消费者

用于测试WebSocket连接和基本功能。
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class SimpleTestConsumer(AsyncWebsocketConsumer):
    """简单的WebSocket测试消费者"""
    
    async def connect(self):
        """建立WebSocket连接"""
        
        logger.info("SimpleTestConsumer: 收到WebSocket连接请求")
        
        # 直接接受连接（不需要认证）
        await self.accept()
        
        # 发送连接成功消息
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'WebSocket测试连接成功！',
            'timestamp': str(__import__('datetime').datetime.now())
        }))
        
        logger.info("SimpleTestConsumer: WebSocket连接已建立")
    
    async def disconnect(self, close_code):
        """断开WebSocket连接"""
        
        logger.info(f"SimpleTestConsumer: WebSocket连接断开，代码: {close_code}")
    
    async def receive(self, text_data):
        """接收WebSocket消息"""
        
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'unknown')
            
            logger.info(f"SimpleTestConsumer: 收到消息类型 {message_type}")
            
            # Echo回显消息
            if message_type == 'echo':
                await self.send(text_data=json.dumps({
                    'type': 'echo_response',
                    'original_message': data.get('message', ''),
                    'timestamp': str(__import__('datetime').datetime.now())
                }))
            
            # Ping-Pong测试
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': str(__import__('datetime').datetime.now())
                }))
            
            # 默认处理
            else:
                await self.send(text_data=json.dumps({
                    'type': 'message_received',
                    'received_type': message_type,
                    'message': f'收到你的消息: {data}',
                    'timestamp': str(__import__('datetime').datetime.now())
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': '无效的JSON格式',
                'timestamp': str(__import__('datetime').datetime.now())
            }))
        except Exception as e:
            logger.error(f"SimpleTestConsumer: 处理消息失败: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'处理消息失败: {str(e)}',
                'timestamp': str(__import__('datetime').datetime.now())
            }))