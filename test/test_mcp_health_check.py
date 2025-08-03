#!/usr/bin/env python3
"""
MCP工具健康检查测试脚本
测试修复后的健康检查API端点和CrewAI SDK集成
"""

import os
import sys
import django
import requests
import json
from datetime import datetime

# 添加Django项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')
django.setup()

from crewaiplatform.models import MCPTool
from crewaiplatform.services import AuthService

class MCPHealthCheckTester:
    def __init__(self):
        self.base_url = "http://localhost:8000/api"
        self.token = None
        
    def authenticate(self):
        """认证获取Token"""
        try:
            # 尝试登录（假设有测试用户）
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(f"{self.base_url}/auth/login/", json=login_data)
            if response.status_code == 200:
                self.token = response.json().get('access')
                print("✅ 认证成功")
                return True
            else:
                print(f"❌ 认证失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 认证异常: {str(e)}")
            return False
    
    def get_headers(self):
        """获取认证头"""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    def test_mcp_tools_list(self):
        """测试MCP工具列表接口"""
        print("\n🔍 测试MCP工具列表接口...")
        try:
            response = requests.get(
                f"{self.base_url}/mcp-tools/",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                tools = response.json()
                print(f"✅ 获取到 {len(tools)} 个MCP工具")
                return tools
            else:
                print(f"❌ 获取MCP工具列表失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return []
    
    def test_health_check_api(self, tool_id):
        """测试健康检查API端点"""
        print(f"\n🔍 测试健康检查API (工具ID: {tool_id})...")
        try:
            response = requests.post(
                f"{self.base_url}/mcp-tools/{tool_id}/health-check/",
                headers=self.get_headers()
            )
            
            print(f"📡 请求URL: {response.url}")
            print(f"📊 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 健康检查API调用成功")
                print(f"📈 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True, result
            else:
                print(f"❌ 健康检查API失败: {response.status_code} - {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False, None
    
    def test_crewai_connection_direct(self):
        """直接测试CrewAI SDK连接"""
        print(f"\n🔍 直接测试CrewAI SDK连接...")
        try:
            from crewai_tools import MCPServerAdapter
            
            # 测试配置
            server_configs = [
                {
                    "name": "ModelScope MCP",
                    "config": {
                        "transport": "sse", 
                        "url": "https://mcp.api-inference.modelscope.net/xxx/sse"
                    }
                },
                {
                    "name": "Local HTTP MCP",
                    "config": {
                        "transport": "http",
                        "base_url": "http://localhost:3001"
                    }
                }
            ]
            
            for test_case in server_configs:
                print(f"\n📋 测试: {test_case['name']}")
                try:
                    with MCPServerAdapter(test_case['config']) as tools:
                        tool_names = [t.name for t in tools] if tools else []
                        print(f"✅ 连接成功，可用工具：{tool_names}")
                        
                except Exception as e:
                    print(f"❌ 连接失败：{str(e)}")
                    
        except ImportError:
            print("❌ CrewAI Tools 未安装，请运行: pip install crewai-tools")
            return False
            
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    def create_test_mcp_tool(self):
        """创建测试MCP工具"""
        print(f"\n🔍 创建测试MCP工具...")
        try:
            test_tool_data = {
                "name": "test_modelscope_mcp",
                "display_name": "测试ModelScope MCP工具",
                "description": "用于测试CrewAI SDK连接的MCP工具",
                "server_type": "sse",
                "connection_config": {
                    "url": "https://mcp.api-inference.modelscope.net/test/sse"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/mcp-tools/",
                json=test_tool_data,
                headers=self.get_headers()
            )
            
            if response.status_code == 201:
                tool = response.json()
                print(f"✅ 创建测试工具成功，ID: {tool['id']}")
                return tool['id']
            else:
                print(f"❌ 创建测试工具失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 创建异常: {str(e)}")
            return None
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始MCP工具健康检查测试\n")
        
        # 1. 认证
        if not self.authenticate():
            print("❌ 认证失败，无法继续测试")
            return
        
        # 2. 获取现有工具
        tools = self.test_mcp_tools_list()
        
        # 3. 测试现有工具的健康检查
        if tools:
            print(f"\n📋 测试现有工具的健康检查...")
            for tool in tools[:2]:  # 只测试前2个工具
                self.test_health_check_api(tool['id'])
        
        # 4. 创建新的测试工具
        test_tool_id = self.create_test_mcp_tool()
        if test_tool_id:
            self.test_health_check_api(test_tool_id)
        
        # 5. 直接测试CrewAI SDK
        self.test_crewai_connection_direct()
        
        print(f"\n🎉 测试完成！时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    tester = MCPHealthCheckTester()
    tester.run_all_tests()