#!/usr/bin/env python3
"""
流式对话集成测试

模拟前端WebSocket客户端，测试完整的流式对话流程:
1. 建立WebSocket连接
2. 发送用户消息
3. 接收思考过程更新
4. 接收流式答案输出
5. 验证完整对话流程
"""

import os
import sys
import asyncio
import json
import websockets
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent.parent
backend_path = project_root / 'backend'
sys.path.insert(0, str(backend_path))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')

try:
    import django
    django.setup()
except ImportError:
    print("❌ Django未安装，请先安装项目依赖")
    sys.exit(1)
except Exception as e:
    print(f"❌ Django环境配置失败: {e}")
    sys.exit(1)


class StreamingChatIntegrationTest:
    """流式对话集成测试类"""
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.websocket_url = f"ws://{host}:{port}/ws/chat/{{conversation_id}}/"
        self.test_results = []
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅" if success else "❌"
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
        print(f"{status} {test_name}: {message}")
    
    def setup_test_data(self):
        """设置测试数据"""
        print("🔧 设置测试数据...")
        
        try:
            from django.contrib.auth import get_user_model
            from crewaiplatform.models import ChatConversation, CrewAIAgent, LLMModel
            
            User = get_user_model()
            
            # 获取或创建测试用户
            user, created = User.objects.get_or_create(
                username='websocket_test_user',
                defaults={
                    'email': 'websocket_test@example.com',
                    'first_name': '测试',
                    'last_name': '用户'
                }
            )
            
            # 检查可用的Agent
            agent = CrewAIAgent.objects.filter(is_active=True).first()
            if not agent:
                self.log_result("测试数据设置", False, "未找到可用的Agent")
                return None, None
            
            # 创建测试会话
            conversation, created = ChatConversation.objects.get_or_create(
                user=user,
                title='WebSocket流式测试会话',
                defaults={
                    'primary_agent': agent,
                    'agent_selection_mode': 'manual',
                    'description': '用于测试WebSocket流式对话功能'
                }
            )
            
            self.log_result("测试数据设置", True, f"用户: {user.username}, 会话ID: {conversation.id}")
            return user, conversation
            
        except Exception as e:
            self.log_result("测试数据设置", False, str(e))
            return None, None
    
    async def test_websocket_connection(self, conversation_id):
        """测试WebSocket连接"""
        print("\n🔌 测试WebSocket连接...")
        
        websocket_url = self.websocket_url.format(conversation_id=conversation_id)
        
        try:
            # 尝试连接WebSocket
            async with websockets.connect(websocket_url) as websocket:
                self.log_result("WebSocket连接测试", True, f"成功连接到 {websocket_url}")
                
                # 等待连接确认消息
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'connection_established':
                        self.log_result("连接确认消息", True, f"收到确认: {data.get('message')}")
                        return True
                    else:
                        self.log_result("连接确认消息", False, f"意外消息类型: {data.get('type')}")
                        return False
                        
                except asyncio.TimeoutError:
                    self.log_result("连接确认消息", False, "超时未收到连接确认")
                    return False
                    
        except Exception as e:
            self.log_result("WebSocket连接测试", False, str(e))
            return False
    
    async def test_message_flow(self, conversation_id):
        """测试完整的消息流程"""
        print("\n💬 测试流式对话消息流程...")
        
        websocket_url = self.websocket_url.format(conversation_id=conversation_id)
        
        try:
            async with websockets.connect(websocket_url) as websocket:
                # 跳过连接确认消息
                await websocket.recv()
                
                # 发送测试消息
                test_message = {
                    "type": "send_message",
                    "content": "你好，请简单介绍一下你自己，并展示你的思考过程"
                }
                
                await websocket.send(json.dumps(test_message))
                self.log_result("发送测试消息", True, f"发送: {test_message['content']}")
                
                # 收集响应消息
                received_messages = []
                message_types = set()
                
                # 设置超时时间（30秒）
                timeout = 30.0
                start_time = asyncio.get_event_loop().time()
                
                while asyncio.get_event_loop().time() - start_time < timeout:
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(response)
                        
                        received_messages.append(data)
                        message_types.add(data.get('type'))
                        
                        msg_type = data.get('type')
                        print(f"   📨 收到消息: {msg_type}")
                        
                        # 如果收到完成消息，结束测试
                        if msg_type in ['answer_stream_complete', 'error']:
                            break
                            
                    except asyncio.TimeoutError:
                        # 没有新消息，继续等待
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self.log_result("WebSocket连接", False, "连接意外关闭")
                        break
                
                # 分析收到的消息类型
                expected_types = {
                    'new_message',  # 用户消息广播
                    'thinking_status_update',  # 思考状态更新
                    'thinking_content_update',  # 思考内容更新
                    'thinking_complete',  # 思考完成
                    'answer_stream_start',  # 开始流式输出
                    'answer_stream_update',  # 流式内容更新
                    'answer_stream_complete'  # 流式输出完成
                }
                
                # 检查关键消息类型
                if 'new_message' in message_types:
                    self.log_result("用户消息广播", True, "收到用户消息广播")
                else:
                    self.log_result("用户消息广播", False, "未收到用户消息广播")
                
                # 检查思考过程消息
                thinking_messages = [msg for msg in received_messages if 'thinking' in msg.get('type', '')]
                if thinking_messages:
                    self.log_result("思考过程消息", True, f"收到{len(thinking_messages)}条思考相关消息")
                else:
                    self.log_result("思考过程消息", False, "未收到思考过程消息")
                
                # 检查流式输出消息
                stream_messages = [msg for msg in received_messages if 'stream' in msg.get('type', '')]
                if stream_messages:
                    self.log_result("流式输出消息", True, f"收到{len(stream_messages)}条流式输出消息")
                else:
                    self.log_result("流式输出消息", False, "未收到流式输出消息")
                
                # 总体消息流程评估
                if len(received_messages) > 0:
                    self.log_result("消息流程测试", True, f"总共收到{len(received_messages)}条消息")
                    
                    # 打印消息摘要
                    print(f"   📊 消息类型统计: {dict(sorted(message_types))}")
                else:
                    self.log_result("消息流程测试", False, "未收到任何响应消息")
                
                return len(received_messages) > 0
                
        except Exception as e:
            self.log_result("消息流程测试", False, str(e))
            return False
    
    async def run_integration_tests(self):
        """运行完整的集成测试"""
        print("🚀 开始流式对话集成测试...")
        print("=" * 60)
        
        # 设置测试数据
        user, conversation = self.setup_test_data()
        if not user or not conversation:
            print("❌ 测试数据设置失败，无法继续测试")
            return
        
        conversation_id = conversation.id
        
        # 测试WebSocket连接
        connection_success = await self.test_websocket_connection(conversation_id)
        
        if connection_success:
            # 测试消息流程
            await self.test_message_flow(conversation_id)
        else:
            print("⚠️ WebSocket连接失败，跳过消息流程测试")
        
        # 输出测试结果
        self.print_summary()
    
    def print_summary(self):
        """输出测试摘要"""
        print("\n" + "=" * 60)
        print("📊 集成测试结果摘要")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests} ✅")
        print(f"失败测试: {failed_tests} ❌")
        print(f"通过率: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test']}: {result['message']}")
        
        print(f"\n💡 测试建议:")
        if failed_tests == 0:
            print("   🎉 所有集成测试通过!")
            print("   ✨ WebSocket流式对话功能工作正常")
            print("   🌐 可以在前端界面测试完整用户体验")
        else:
            print("   🔧 请确保ASGI服务器正在运行: ./backend/start_websocket.sh")
            print("   🗄️ 检查数据库中是否有可用的Agent和LLM模型")
            print("   🔌 验证WebSocket路由配置是否正确")
        
        print("=" * 60)


async def main():
    """主函数"""
    # 检查是否提供了自定义host和port
    import argparse
    parser = argparse.ArgumentParser(description='流式对话集成测试')
    parser.add_argument('--host', default='127.0.0.1', help='WebSocket服务器主机')
    parser.add_argument('--port', type=int, default=8000, help='WebSocket服务器端口')
    args = parser.parse_args()
    
    print(f"📡 测试目标: ws://{args.host}:{args.port}/ws/chat/<conversation_id>/")
    
    tester = StreamingChatIntegrationTest(host=args.host, port=args.port)
    await tester.run_integration_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试运行失败: {e}")
        import traceback
        traceback.print_exc()