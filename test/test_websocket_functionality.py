#!/usr/bin/env python3
"""
WebSocket流式对话功能测试

测试内容:
1. WebSocket配置验证
2. Django Channels集成测试
3. 流式对话功能测试
4. 思考过程传输测试
"""

import os
import sys
import asyncio
import json
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


class WebSocketFunctionalityTest:
    """WebSocket功能测试类"""
    
    def __init__(self):
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
    
    def test_django_configuration(self):
        """测试Django基础配置"""
        print("\n🔧 测试Django基础配置...")
        
        try:
            from django.conf import settings
            
            # 检查Channels在INSTALLED_APPS中
            if 'channels' in settings.INSTALLED_APPS:
                self.log_result("Channels安装检查", True, "channels已在INSTALLED_APPS中")
            else:
                self.log_result("Channels安装检查", False, "channels未在INSTALLED_APPS中")
            
            # 检查ASGI应用配置
            if hasattr(settings, 'ASGI_APPLICATION'):
                self.log_result("ASGI配置检查", True, f"ASGI应用: {settings.ASGI_APPLICATION}")
            else:
                self.log_result("ASGI配置检查", False, "ASGI_APPLICATION未配置")
            
            # 检查Channel Layers配置
            if hasattr(settings, 'CHANNEL_LAYERS'):
                backend_type = settings.CHANNEL_LAYERS['default']['BACKEND']
                self.log_result("Channel Layers配置", True, f"后端类型: {backend_type}")
            else:
                self.log_result("Channel Layers配置", False, "CHANNEL_LAYERS未配置")
                
        except Exception as e:
            self.log_result("Django配置检查", False, str(e))
    
    def test_websocket_routing(self):
        """测试WebSocket路由配置"""
        print("\n🛣️ 测试WebSocket路由配置...")
        
        try:
            from crewaiplatform.routing import websocket_urlpatterns
            
            if websocket_urlpatterns:
                self.log_result("WebSocket路由配置", True, f"配置了{len(websocket_urlpatterns)}个路由")
                
                # 检查具体路由
                for i, pattern in enumerate(websocket_urlpatterns):
                    route_pattern = pattern.pattern.pattern
                    print(f"   路由 {i+1}: {route_pattern}")
            else:
                self.log_result("WebSocket路由配置", False, "未配置WebSocket路由")
                
        except ImportError as e:
            self.log_result("WebSocket路由导入", False, f"导入失败: {e}")
        except Exception as e:
            self.log_result("WebSocket路由检查", False, str(e))
    
    def test_consumer_classes(self):
        """测试WebSocket Consumer类"""
        print("\n🔌 测试WebSocket Consumer类...")
        
        try:
            from crewaiplatform.consumers import ChatConsumer, NotificationConsumer
            
            # 检查ChatConsumer
            if hasattr(ChatConsumer, 'connect') and hasattr(ChatConsumer, 'receive'):
                self.log_result("ChatConsumer类检查", True, "包含必要的异步方法")
            else:
                self.log_result("ChatConsumer类检查", False, "缺少必要方法")
            
            # 检查流式传输方法
            streaming_methods = [
                'send_thinking_status', 'send_thinking_update', 
                'send_thinking_complete', 'send_answer_stream_start',
                'send_answer_stream_update', 'send_answer_stream_complete'
            ]
            
            missing_methods = []
            for method in streaming_methods:
                if not hasattr(ChatConsumer, method):
                    missing_methods.append(method)
            
            if not missing_methods:
                self.log_result("流式传输方法检查", True, "所有流式传输方法已定义")
            else:
                self.log_result("流式传输方法检查", False, f"缺少方法: {missing_methods}")
                
        except ImportError as e:
            self.log_result("Consumer类导入", False, f"导入失败: {e}")
        except Exception as e:
            self.log_result("Consumer类检查", False, str(e))
    
    def test_models_and_services(self):
        """测试数据模型和服务"""
        print("\n📊 测试数据模型和服务...")
        
        try:
            from crewaiplatform.models import ChatConversation, ChatMessage, CrewAIAgent, LLMModel
            from crewaiplatform.services.simple_agent_service import SimpleAgentService
            
            # 检查模型
            self.log_result("聊天模型检查", True, "ChatConversation和ChatMessage已定义")
            self.log_result("Agent模型检查", True, "CrewAIAgent模型已定义")
            self.log_result("LLM模型检查", True, "LLMModel模型已定义")
            
            # 检查流式服务方法
            if hasattr(SimpleAgentService, 'process_user_message_with_websocket'):
                self.log_result("WebSocket流式服务", True, "process_user_message_with_websocket方法已定义")
            else:
                self.log_result("WebSocket流式服务", False, "缺少WebSocket专用处理方法")
            
            # 检查支持思考的LLM调用方法
            thinking_methods = ['_call_qwen_with_thinking', '_call_moonshot_with_thinking']
            for method in thinking_methods:
                if hasattr(SimpleAgentService, method):
                    self.log_result(f"思考过程支持 ({method})", True, "方法已定义")
                else:
                    self.log_result(f"思考过程支持 ({method})", False, "方法未定义")
                    
        except ImportError as e:
            self.log_result("模型和服务导入", False, f"导入失败: {e}")
        except Exception as e:
            self.log_result("模型和服务检查", False, str(e))
    
    def test_database_data(self):
        """测试数据库数据"""
        print("\n🗄️ 测试数据库数据...")
        
        try:
            from crewaiplatform.models import CrewAIAgent, LLMModel
            
            # 检查Agent数据
            agent_count = CrewAIAgent.objects.filter(is_active=True).count()
            if agent_count > 0:
                self.log_result("可用Agent检查", True, f"找到{agent_count}个可用Agent")
            else:
                self.log_result("可用Agent检查", False, "未找到可用Agent")
            
            # 检查支持思考的LLM模型
            thinking_models = LLMModel.objects.filter(
                provider__in=['qwen', 'moonshot'],
                is_active=True
            ).count()
            
            if thinking_models > 0:
                self.log_result("思考模型检查", True, f"找到{thinking_models}个支持思考的模型")
            else:
                self.log_result("思考模型检查", False, "未找到支持思考的模型")
            
            # 检查所有LLM模型
            total_models = LLMModel.objects.filter(is_active=True).count()
            self.log_result("LLM模型统计", True, f"总共{total_models}个可用模型")
            
        except Exception as e:
            self.log_result("数据库数据检查", False, f"数据库访问失败: {e}")
    
    def test_asgi_application(self):
        """测试ASGI应用"""
        print("\n⚙️ 测试ASGI应用...")
        
        try:
            from crewaiplatform.asgi import application
            
            # 检查应用类型
            app_type = str(type(application).__name__)
            self.log_result("ASGI应用检查", True, f"应用类型: {app_type}")
            
            # 检查是否配置了WebSocket协议
            if hasattr(application, 'application_mapping'):
                protocols = list(application.application_mapping.keys())
                if 'websocket' in protocols:
                    self.log_result("WebSocket协议支持", True, f"支持的协议: {protocols}")
                else:
                    self.log_result("WebSocket协议支持", False, f"仅支持: {protocols}")
            else:
                self.log_result("协议映射检查", False, "无法检查协议映射")
                
        except ImportError as e:
            self.log_result("ASGI应用导入", False, f"导入失败: {e}")
        except Exception as e:
            self.log_result("ASGI应用检查", False, str(e))
    
    async def test_consumer_instantiation(self):
        """测试Consumer实例化"""
        print("\n🏗️ 测试Consumer实例化...")
        
        try:
            from crewaiplatform.consumers import ChatConsumer
            
            # 创建模拟scope
            mock_scope = {
                'type': 'websocket',
                'path': '/ws/chat/1/',
                'url_route': {'kwargs': {'conversation_id': 1}},
                'user': type('User', (), {'is_authenticated': True, 'id': 1, 'username': 'test'})()
            }
            
            # 实例化Consumer
            consumer = ChatConsumer(mock_scope)
            self.log_result("Consumer实例化", True, "ChatConsumer实例化成功")
            
            # 检查WebSocket流式方法
            streaming_methods = [
                'send_thinking_status', 'send_thinking_update', 
                'send_thinking_complete', 'send_answer_stream_start'
            ]
            
            for method_name in streaming_methods:
                if hasattr(consumer, method_name):
                    method = getattr(consumer, method_name)
                    if asyncio.iscoroutinefunction(method):
                        self.log_result(f"异步方法检查 ({method_name})", True, "方法为异步")
                    else:
                        self.log_result(f"异步方法检查 ({method_name})", False, "方法非异步")
                else:
                    self.log_result(f"方法存在检查 ({method_name})", False, "方法不存在")
            
        except Exception as e:
            self.log_result("Consumer实例化测试", False, str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始WebSocket功能测试...")
        print("=" * 50)
        
        # 运行同步测试
        self.test_django_configuration()
        self.test_websocket_routing()
        self.test_consumer_classes()
        self.test_models_and_services()
        self.test_database_data()
        self.test_asgi_application()
        
        # 运行异步测试
        try:
            asyncio.run(self.test_consumer_instantiation())
        except Exception as e:
            self.log_result("异步测试运行", False, str(e))
        
        # 输出测试结果
        self.print_summary()
    
    def print_summary(self):
        """输出测试摘要"""
        print("\n" + "=" * 50)
        print("📊 测试结果摘要")
        print("=" * 50)
        
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
        
        print("\n💡 下一步:")
        if failed_tests == 0:
            print("   所有测试通过! 🎉")
            print("   可以启动ASGI服务器测试WebSocket连接:")
            print("   ./backend/start_websocket.sh")
        else:
            print("   请修复失败的测试项目后重新测试")
        
        print("=" * 50)


if __name__ == "__main__":
    tester = WebSocketFunctionalityTest()
    tester.run_all_tests()