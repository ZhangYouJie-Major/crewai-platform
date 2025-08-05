#!/usr/bin/env python3
"""
Agent管理测试类
测试Agent的创建、更新、删除、克隆、启用/禁用等功能
"""

import time
from test_base import BaseTester
from test_config import API_ENDPOINTS

class AgentManagementTester(BaseTester):
    """Agent管理测试类"""
    
    def __init__(self):
        super().__init__("AgentManagementTest")
        self.created_agents = []  # 记录创建的Agent ID，用于清理
    
    def test_get_llm_models(self) -> dict:
        """获取可用的LLM模型"""
        self.logger.info("🤖 获取可用的LLM模型...")
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["llm_models"]["list"])
        
        if status_code == 200:
            models = response.get("results", []) if isinstance(response, dict) else response
            available_models = [m for m in models if m.get("is_available") and m.get("is_active")]
            
            if available_models:
                self.logger.info(f"✅ 找到 {len(available_models)} 个可用模型")
                return available_models[0]  # 返回第一个可用模型
            else:
                self.logger.warning("⚠️ 没有可用的LLM模型")
                return None
        else:
            self.logger.error(f"❌ 获取LLM模型失败: {status_code}")
            return None
    
    def test_create_agent(self) -> bool:
        """测试创建Agent"""
        self.logger.info("➕ 测试创建Agent...")
        
        # 获取可用模型
        llm_model = self.test_get_llm_models()
        if not llm_model:
            self.logger.error("无法获取LLM模型，跳过Agent创建测试")
            return False
        
        # 创建测试数据
        agent_data = self.create_test_data("agent", llm_model=llm_model["id"])
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["agents"]["create"], agent_data)
        
        success = self.assert_status_code(status_code, 201, "Agent创建")
        
        if success:
            # 验证响应数据
            success = self.assert_response_contains(response, "id", "Agent ID")
            success = self.assert_response_value(response, "name", agent_data["name"], "Agent名称")
            success = self.assert_response_value(response, "is_active", True, "Agent激活状态")
            
            # 记录创建的Agent ID用于清理
            if "id" in response:
                self.created_agents.append(response["id"])
        
        return success
    
    def test_get_agent_list(self) -> bool:
        """测试获取Agent列表"""
        self.logger.info("📋 测试获取Agent列表...")
        
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        success = self.assert_status_code(status_code, 200, "获取Agent列表")
        
        if success:
            agents = response.get("results", []) if isinstance(response, dict) else response
            self.logger.info(f"✅ 获取到 {len(agents)} 个Agent")
            
            # 验证列表结构
            if agents:
                success = self.assert_response_contains(agents[0], "id", "Agent列表项ID")
                success = self.assert_response_contains(agents[0], "name", "Agent列表项名称")
        
        return success
    
    def test_get_agent_detail(self) -> bool:
        """测试获取Agent详情"""
        self.logger.info("🔍 测试获取Agent详情...")
        
        # 先获取Agent列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取Agent列表")
            return False
        
        agents = response.get("results", []) if isinstance(response, dict) else response
        
        if not agents:
            self.logger.warning("没有Agent可测试详情")
            return True
        
        # 获取第一个Agent的详情
        agent_id = agents[0]["id"]
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["detail"].format(id=agent_id))
        
        success = self.assert_status_code(status_code, 200, "获取Agent详情")
        
        if success:
            # 验证详情数据完整性
            required_fields = ["id", "name", "display_name", "description", "role", "goal", "is_active"]
            for field in required_fields:
                success = self.assert_response_contains(response, field, f"Agent详情字段: {field}")
        
        return success
    
    def test_update_agent(self) -> bool:
        """测试更新Agent"""
        self.logger.info("✏️ 测试更新Agent...")
        
        # 先获取Agent列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取Agent列表")
            return False
        
        agents = response.get("results", []) if isinstance(response, dict) else response
        
        if not agents:
            self.logger.warning("没有Agent可测试更新")
            return True
        
        # 更新第一个Agent
        agent_id = agents[0]["id"]
        update_data = {
            "display_name": f"更新后的Agent_{int(time.time())}",
            "description": "这是更新后的描述",
            "goal": "更新后的目标"
        }
        
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["agents"]["update"].format(id=agent_id), update_data)
        
        success = self.assert_status_code(status_code, 200, "Agent更新")
        
        if success:
            # 验证更新结果
            success = self.assert_response_value(response, "display_name", update_data["display_name"], "Agent显示名称更新")
            success = self.assert_response_value(response, "description", update_data["description"], "Agent描述更新")
        
        return success
    
    def test_clone_agent(self) -> bool:
        """测试克隆Agent"""
        self.logger.info("🔄 测试克隆Agent...")
        
        # 先获取Agent列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取Agent列表")
            return False
        
        agents = response.get("results", []) if isinstance(response, dict) else response
        
        if not agents:
            self.logger.warning("没有Agent可测试克隆")
            return True
        
        # 克隆第一个Agent
        agent_id = agents[0]["id"]
        clone_data = {
            "name": f"cloned_agent_{int(time.time())}",
            "display_name": f"克隆的Agent_{int(time.time())}"
        }
        
        status_code, response = self.make_request("POST", API_ENDPOINTS["agents"]["clone"].format(id=agent_id), clone_data)
        
        success = self.assert_status_code(status_code, 201, "Agent克隆")
        
        if success:
            # 验证克隆结果
            success = self.assert_response_contains(response, "id", "克隆Agent ID")
            success = self.assert_response_value(response, "name", clone_data["name"], "克隆Agent名称")
            success = self.assert_response_value(response, "display_name", clone_data["display_name"], "克隆Agent显示名称")
            
            # 记录克隆的Agent ID用于清理
            if "id" in response:
                self.created_agents.append(response["id"])
        
        return success
    
    def test_toggle_agent_status(self) -> bool:
        """测试切换Agent状态"""
        self.logger.info("🔄 测试切换Agent状态...")
        
        # 先获取Agent列表
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取Agent列表")
            return False
        
        agents = response.get("results", []) if isinstance(response, dict) else response
        
        if not agents:
            self.logger.warning("没有Agent可测试状态切换")
            return True
        
        # 切换第一个Agent的状态
        agent_id = agents[0]["id"]
        original_status = agents[0]["is_active"]
        new_status = not original_status
        
        toggle_data = {"is_active": new_status}
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["agents"]["toggle"].format(id=agent_id), toggle_data)
        
        success = self.assert_status_code(status_code, 200, "Agent状态切换")
        
        if success:
            # 验证状态切换结果
            success = self.assert_response_value(response, "is_active", new_status, "Agent状态切换")
            
            # 再次切换回原状态
            toggle_data = {"is_active": original_status}
            status_code, response = self.make_request("PATCH", API_ENDPOINTS["agents"]["toggle"].format(id=agent_id), toggle_data)
            
            if status_code == 200:
                self.logger.info("✅ Agent状态已恢复")
        
        return success
    
    def test_disable_agent(self) -> bool:
        """测试禁用Agent"""
        self.logger.info("🚫 测试禁用Agent...")
        
        # 先获取激活状态的Agent
        status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
        
        if status_code != 200:
            self.logger.error("无法获取Agent列表")
            return False
        
        agents = response.get("results", []) if isinstance(response, dict) else response
        active_agents = [a for a in agents if a.get("is_active")]
        
        if not active_agents:
            self.logger.warning("没有激活状态的Agent可测试禁用")
            return True
        
        # 禁用第一个激活的Agent
        agent_id = active_agents[0]["id"]
        disable_data = {"is_active": False}
        
        status_code, response = self.make_request("PATCH", API_ENDPOINTS["agents"]["update"].format(id=agent_id), disable_data)
        
        success = self.assert_status_code(status_code, 200, "Agent禁用")
        
        if success:
            # 验证禁用结果
            success = self.assert_response_value(response, "is_active", False, "Agent禁用状态")
            
            # 验证禁用后的Agent仍在列表中
            status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["list"])
            if status_code == 200:
                agents = response.get("results", []) if isinstance(response, dict) else response
                disabled_agents = [a for a in agents if a["id"] == agent_id and not a["is_active"]]
                success = self.assert_response_value(
                    {"disabled_count": len(disabled_agents)}, 
                    "disabled_count", 
                    1, 
                    "禁用Agent在列表中"
                )
        
        return success
    
    def test_delete_agent(self) -> bool:
        """测试删除Agent"""
        self.logger.info("🗑️ 测试删除Agent...")
        
        # 先创建一个测试Agent用于删除
        llm_model = self.test_get_llm_models()
        if not llm_model:
            self.logger.error("无法获取LLM模型，跳过删除测试")
            return False
        
        agent_data = self.create_test_data("agent", llm_model=llm_model["id"])
        status_code, response = self.make_request("POST", API_ENDPOINTS["agents"]["create"], agent_data)
        
        if status_code != 201:
            self.logger.error("无法创建测试Agent")
            return False
        
        agent_id = response["id"]
        
        # 删除刚创建的Agent
        status_code, response = self.make_request("DELETE", API_ENDPOINTS["agents"]["delete"].format(id=agent_id))
        
        success = self.assert_status_code(status_code, 204, "Agent删除")
        
        if success:
            # 验证Agent已被删除
            status_code, response = self.make_request("GET", API_ENDPOINTS["agents"]["detail"].format(id=agent_id))
            success = self.assert_status_code(status_code, 404, "删除后Agent不存在")
        
        return success
    
    def cleanup_test_data(self):
        """清理测试数据"""
        self.logger.info("🧹 清理测试数据...")
        
        for agent_id in self.created_agents:
            try:
                status_code, response = self.make_request("DELETE", API_ENDPOINTS["agents"]["delete"].format(id=agent_id))
                if status_code in [200, 204]:
                    self.logger.info(f"✅ 清理Agent {agent_id} 成功")
                else:
                    self.logger.warning(f"⚠️ 清理Agent {agent_id} 失败: {status_code}")
            except Exception as e:
                self.logger.error(f"❌ 清理Agent {agent_id} 异常: {str(e)}")
        
        self.created_agents.clear()
    
    def run_all_tests(self):
        """运行所有Agent管理测试"""
        self.logger.info("🚀 开始运行Agent管理测试套件...")
        
        # 先进行认证
        if not self.authenticate("admin"):
            self.logger.error("认证失败，无法运行测试")
            return False
        
        tests = [
            self.test_get_llm_models,
            self.test_create_agent,
            self.test_get_agent_list,
            self.test_get_agent_detail,
            self.test_update_agent,
            self.test_clone_agent,
            self.test_toggle_agent_status,
            self.test_disable_agent,
            self.test_delete_agent
        ]
        
        for test in tests:
            self.run_test(test)
        
        # 清理测试数据
        self.cleanup_test_data()
        
        self.print_test_summary()
        return self.test_results["failed"] == 0

def main():
    """主函数"""
    print("🤖 CrewAI Platform Agent管理测试")
    print("=" * 50)
    
    tester = AgentManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("🎉 所有Agent管理测试通过!")
    else:
        print("❌ 部分Agent管理测试失败，请检查日志")
    
    return success

if __name__ == "__main__":
    main() 