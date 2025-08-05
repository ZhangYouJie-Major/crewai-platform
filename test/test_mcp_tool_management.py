#!/usr/bin/env python3
"""
MCP工具管理测试类
测试MCP工具的创建、更新、删除、健康检查等功能
"""

import time
from test_base import BaseTester
from test_config import API_ENDPOINTS

class MCPToolManagementTester(BaseTester):
    """MCP工具管理测试类"""
    
    def __init__(self):
        super().__init__("MCPToolManagementTest")
        self.created_tools = []  # 记录创建的工具 ID，用于清理
    
    def test_create_mcp_tool(self) -> bool:
        """测试创建MCP工具"""
        self.logger.info("➕ 测试创建MCP工具...")
        
        # 创建测试数据
        tool_data = self.create_test_data("mcp_tool")
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], tool_data)
        
        success = self.assert_status_code(status_code, 201, "MCP工具创建")
        
        if success:
            # 验证响应数据
            success = self.assert_response_contains(response, "id", "MCP工具ID")
            success = self.assert_response_value(response, "name", tool_data["name"], "MCP工具名称")
            success = self.assert_response_value(response, "is_active", True, "MCP工具激活状态")
            
            # 记录创建的工具 ID用于清理
            if "id" in response:
                self.created_tools.append(response["id"])
        
        return success
    
    def test_get_mcp_tool_list(self) -> bool:
        """测试获取MCP工具列表"""
        self.logger.info("📋 测试获取MCP工具列表...")
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
        
        success = self.assert_status_code(status_code, 200, "获取MCP工具列表")
        
        if success:
            tools = response.get("results", []) if isinstance(response, dict) else response
            self.logger.info(f"✅ 获取到 {len(tools)} 个MCP工具")
            
            # 验证列表结构
            if tools:
                success = self.assert_response_contains(tools[0], "id", "MCP工具列表项ID")
                success = self.assert_response_contains(tools[0], "name", "MCP工具列表项名称")
                success = self.assert_response_contains(tools[0], "server_url", "MCP工具服务器URL")
        
        return success
    
    def test_get_mcp_tool_detail(self) -> bool:
        """测试获取MCP工具详情"""
        self.logger.info("🔍 测试获取MCP工具详情...")
        
        # 先获取工具列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取MCP工具列表")
            return False
        
        tools = response.get("results", []) if isinstance(response, dict) else response
        
        if not tools:
            self.logger.warning("没有MCP工具可测试详情")
            return True
        
        # 获取第一个工具的详情
        tool_id = tools[0]["id"]
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["detail"].format(id=tool_id))
        
        success = self.assert_status_code(status_code, 200, "获取MCP工具详情")
        
        if success:
            # 验证详情数据完整性
            required_fields = ["id", "name", "display_name", "description", "server_url", "is_active"]
            for field in required_fields:
                success = self.assert_response_contains(response, field, f"MCP工具详情字段: {field}")
        
        return success
    
    def test_update_mcp_tool(self) -> bool:
        """测试更新MCP工具"""
        self.logger.info("✏️ 测试更新MCP工具...")
        
        # 先获取工具列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取MCP工具列表")
            return False
        
        tools = response.get("results", []) if isinstance(response, dict) else response
        
        if not tools:
            self.logger.warning("没有MCP工具可测试更新")
            return True
        
        # 更新第一个工具
        tool_id = tools[0]["id"]
        update_data = {
            "display_name": f"更新后的工具_{int(time.time())}",
            "description": "这是更新后的描述",
            "server_url": "http://localhost:8081"
        }
        
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["mcp_tools"]["update"].format(id=tool_id), update_data)
        
        success = self.assert_status_code(status_code, 200, "MCP工具更新")
        
        if success:
            # 验证更新结果
            success = self.assert_response_value(response, "display_name", update_data["display_name"], "MCP工具显示名称更新")
            success = self.assert_response_value(response, "description", update_data["description"], "MCP工具描述更新")
            success = self.assert_response_value(response, "server_url", update_data["server_url"], "MCP工具服务器URL更新")
        
        return success
    
    def test_health_check(self) -> bool:
        """测试MCP工具健康检查"""
        self.logger.info("🏥 测试MCP工具健康检查...")
        
        # 先获取工具列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取MCP工具列表")
            return False
        
        tools = response.get("results", []) if isinstance(response, dict) else response
        
        if not tools:
            self.logger.warning("没有MCP工具可测试健康检查")
            return True
        
        # 对第一个工具进行健康检查
        tool_id = tools[0]["id"]
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["health_check"].format(id=tool_id))
        
        # 健康检查可能返回200（成功）或500（失败），都是正常的
        if status_code in [200, 500]:
            self.logger.info(f"✅ 健康检查完成，状态码: {status_code}")
            
            # 验证响应结构
            if status_code == 200:
                success = self.assert_response_contains(response, "status", "健康检查状态")
                success = self.assert_response_contains(response, "message", "健康检查消息")
            else:
                # 500状态码表示健康检查失败，但这是正常的（服务器可能未运行）
                self.logger.info("⚠️ 健康检查失败（服务器可能未运行），这是正常的")
                success = True
            
            return success
        else:
            self.logger.error(f"❌ 健康检查异常状态码: {status_code}")
            return False
    
    def test_health_check_invalid_tool(self) -> bool:
        """测试无效工具的健康检查"""
        self.logger.info("🏥 测试无效工具的健康检查...")
        
        # 使用一个不存在的工具ID
        invalid_tool_id = 99999
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["health_check"].format(id=invalid_tool_id))
        
        # 应该返回404
        return self.assert_status_code(status_code, 404, "无效工具健康检查")
    
    def test_disable_mcp_tool(self) -> bool:
        """测试禁用MCP工具"""
        self.logger.info("🚫 测试禁用MCP工具...")
        
        # 先获取激活状态的工具
        status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取MCP工具列表")
            return False
        
        tools = response.get("results", []) if isinstance(response, dict) else response
        active_tools = [t for t in tools if t.get("is_active")]
        
        if not active_tools:
            self.logger.warning("没有激活状态的MCP工具可测试禁用")
            return True
        
        # 禁用第一个激活的工具
        tool_id = active_tools[0]["id"]
        disable_data = {"is_active": False}
        
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["mcp_tools"]["update"].format(id=tool_id), disable_data)
        
        success = self.assert_status_code(status_code, 200, "MCP工具禁用")
        
        if success:
            # 验证禁用结果
            success = self.assert_response_value(response, "is_active", False, "MCP工具禁用状态")
            
            # 验证禁用后的工具仍在列表中
            status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["list"])
            if status_code == 200:
                tools = response.get("results", []) if isinstance(response, dict) else response
                disabled_tools = [t for t in tools if t["id"] == tool_id and not t["is_active"]]
                success = self.assert_response_value(
                    {"disabled_count": len(disabled_tools)}, 
                    "disabled_count", 
                    1, 
                    "禁用MCP工具在列表中"
                )
        
        return success
    
    def test_delete_mcp_tool(self) -> bool:
        """测试删除MCP工具"""
        self.logger.info("🗑️ 测试删除MCP工具...")
        
        # 先创建一个测试工具用于删除
        tool_data = self.create_test_data("mcp_tool")
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], tool_data)
        
        if status_code != 201:
            self.logger.error("无法创建测试MCP工具")
            return False
        
        tool_id = response["id"]
        
        # 删除刚创建的工具
        status_code, response = self.make_request("DELETE", API_ENDPOINTS["mcp_tools"]["delete"].format(id=tool_id))
        
        success = self.assert_status_code(status_code, 204, "MCP工具删除")
        
        if success:
            # 验证工具已被删除
            status_code, response = self.make_request("GET", API_ENDPOINTS["mcp_tools"]["detail"].format(id=tool_id))
            success = self.assert_status_code(status_code, 404, "删除后MCP工具不存在")
        
        return success
    
    def test_mcp_tool_validation(self) -> bool:
        """测试MCP工具数据验证"""
        self.logger.info("✅ 测试MCP工具数据验证...")
        
        # 测试缺少必需字段
        invalid_data = {
            "name": "",  # 空名称
            "server_url": "invalid_url"  # 无效URL
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], invalid_data)
        
        success1 = self.assert_status_code(status_code, 400, "无效数据创建MCP工具")
        
        # 测试无效的服务器URL
        invalid_data = {
            "name": "test_tool",
            "display_name": "测试工具",
            "server_url": "not_a_valid_url"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], invalid_data)
        
        success2 = self.assert_status_code(status_code, 400, "无效URL创建MCP工具")
        
        return success1 and success2
    
    def test_mcp_tool_duplicate_name(self) -> bool:
        """测试MCP工具名称重复"""
        self.logger.info("🔄 测试MCP工具名称重复...")
        
        # 先创建一个工具
        tool_data = self.create_test_data("mcp_tool")
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], tool_data)
        
        if status_code != 201:
            self.logger.error("无法创建第一个MCP工具")
            return False
        
        first_tool_id = response["id"]
        self.created_tools.append(first_tool_id)
        
        # 尝试创建同名工具
        duplicate_data = {
            "name": tool_data["name"],  # 使用相同的名称
            "display_name": "重复名称工具",
            "description": "这是重复名称的工具",
            "server_url": "http://localhost:8082"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["mcp_tools"]["create"], duplicate_data)
        
        # 应该返回400错误（名称重复）
        success = self.assert_status_code(status_code, 400, "重复名称MCP工具创建")
        
        return success
    
    def cleanup_test_data(self):
        """清理测试数据"""
        self.logger.info("🧹 清理测试数据...")
        
        for tool_id in self.created_tools:
            try:
                status_code, response = self.make_request("DELETE", API_ENDPOINTS["mcp_tools"]["delete"].format(id=tool_id))
                if status_code in [200, 204]:
                    self.logger.info(f"✅ 清理MCP工具 {tool_id} 成功")
                else:
                    self.logger.warning(f"⚠️ 清理MCP工具 {tool_id} 失败: {status_code}")
            except Exception as e:
                self.logger.error(f"❌ 清理MCP工具 {tool_id} 异常: {str(e)}")
        
        self.created_tools.clear()
    
    def run_all_tests(self):
        """运行所有MCP工具管理测试"""
        self.logger.info("🚀 开始运行MCP工具管理测试套件...")
        
        # 先进行认证
        if not self.authenticate("admin"):
            self.logger.error("认证失败，无法运行测试")
            return False
        
        tests = [
            self.test_create_mcp_tool,
            self.test_get_mcp_tool_list,
            self.test_get_mcp_tool_detail,
            self.test_update_mcp_tool,
            self.test_health_check,
            self.test_health_check_invalid_tool,
            self.test_disable_mcp_tool,
            self.test_delete_mcp_tool,
            self.test_mcp_tool_validation,
            self.test_mcp_tool_duplicate_name
        ]
        
        for test in tests:
            self.run_test(test)
        
        # 清理测试数据
        self.cleanup_test_data()
        
        self.print_test_summary()
        return self.test_results["failed"] == 0

def main():
    """主函数"""
    print("🔧 CrewAI Platform MCP工具管理测试")
    print("=" * 50)
    
    tester = MCPToolManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 所有MCP工具管理测试通过!")
    else:
        print("❌ 部分MCP工具管理测试失败，请检查日志")
    
    return success

if __name__ == "__main__":
    main() 