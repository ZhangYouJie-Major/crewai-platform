#!/usr/bin/env python3
"""
全面测试Agent克隆和禁用功能
确保前端界面和API都正常工作
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_comprehensive_agent_functions():
    """全面测试Agent功能"""
    print("🧪 开始全面测试Agent克隆和禁用功能...")
    
    # 1. 登录
    print("\n1. 登录...")
    login_data = {"username": "testuser_update", "password": "testpass123"}
    login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return
    
    token = login_response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 登录成功")
    
    # 2. 获取LLM模型
    print("\n2. 获取LLM模型...")
    llm_response = requests.get(f"{BASE_URL}/llm-models/", headers=headers)
    if llm_response.status_code != 200:
        print(f"❌ 获取LLM模型失败: {llm_response.text}")
        return
        
    llm_models = llm_response.json()["results"]
    available_model = next((m for m in llm_models if m.get("is_available") and m.get("is_active")), None)
    if not available_model:
        print("❌ 没有可用的LLM模型")
        return
    
    print(f"✅ 找到可用模型: {available_model['name']}")
    
    # 3. 创建测试Agent
    print("\n3. 创建测试Agent...")
    timestamp = int(time.time())
    create_data = {
        "name": f"test_comprehensive_{timestamp}",
        "display_name": f"全面测试Agent_{timestamp}",
        "description": "用于全面测试克隆和禁用功能",
        "role": "全面测试工程师",
        "goal": "确保所有功能正常工作",
        "backstory": "这是一个用于全面测试的Agent",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False,
        "verbose": True,
        "memory": False,
        "max_iter": 25,
        "allow_delegation": False
    }
    
    create_response = requests.post(f"{BASE_URL}/crewai-agents/", json=create_data, headers=headers)
    if create_response.status_code != 201:
        print(f"❌ Agent创建失败: {create_response.text}")
        return
    
    original_agent = create_response.json()
    agent_id = original_agent["id"]
    print(f"✅ 原始Agent创建成功:")
    print(f"   ID: {agent_id}")
    print(f"   名称: {original_agent['name']}")
    print(f"   激活状态: {original_agent['is_active']}")
    
    # 4. 测试禁用功能
    print("\n4. 测试禁用功能...")
    disable_data = {"is_active": False}
    disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=disable_data, headers=headers)
    if disable_response.status_code != 200:
        print(f"❌ 禁用失败: {disable_response.text}")
        return
    
    disabled_agent = disable_response.json()
    print(f"✅ 禁用成功: is_active = {disabled_agent['is_active']}")
    
    # 5. 检查禁用Agent是否能在列表中查询到
    print("\n5. 检查禁用Agent是否在列表中...")
    list_response = requests.get(f"{BASE_URL}/crewai-agents/", headers=headers)
    if list_response.status_code != 200:
        print(f"❌ 获取Agent列表失败: {list_response.text}")
        return
    
    agents = list_response.json()["results"]
    test_agents = [a for a in agents if a['name'].startswith('test_comprehensive')]
    disabled_agents = [a for a in test_agents if not a['is_active']]
    
    print(f"✅ 列表中找到测试Agent数量: {len(test_agents)}")
    print(f"✅ 其中禁用的Agent数量: {len(disabled_agents)}")
    
    if len(disabled_agents) == 0:
        print("❌ 禁用的Agent没有在列表中显示！")
        return
    
    # 6. 重新启用Agent以便测试克隆
    print("\n6. 重新启用Agent...")
    enable_data = {"is_active": True}
    enable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=enable_data, headers=headers)
    if enable_response.status_code != 200:
        print(f"❌ 启用失败: {enable_response.text}")
        return
    
    enabled_agent = enable_response.json()
    print(f"✅ 启用成功: is_active = {enabled_agent['is_active']}")
    
    # 7. 获取完整的Agent信息用于克隆
    print("\n7. 获取完整Agent信息...")
    get_response = requests.get(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    if get_response.status_code != 200:
        print(f"❌ 获取Agent详情失败: {get_response.text}")
        return
    
    full_agent = get_response.json()
    print(f"✅ 获取完整Agent信息成功")
    print(f"   所有字段: {list(full_agent.keys())}")
    
    # 8. 测试克隆功能（模拟前端逻辑）
    print("\n8. 测试克隆功能...")
    clone_data = {**full_agent}
    
    # 移除不需要的字段（与前端保持一致）
    fields_to_remove = [
        'id', 'created_at', 'updated_at', 'status', 'status_display',
        'total_tasks', 'completed_tasks', 'total_execution_time',
        'last_execution', 'last_error', 'owner', 'owner_info',
        'success_rate', 'avg_execution_time', 'bound_tools_count',
        'llm_model_info', 'function_calling_llm_info', 'allowed_users'
    ]
    
    for field in fields_to_remove:
        clone_data.pop(field, None)
    
    # 修改名称
    clone_data['name'] = f"{original_agent['name']}_clone"
    clone_data['display_name'] = f"{original_agent['display_name']} (克隆)"
    clone_data['is_public'] = False
    
    print(f"准备克隆的数据字段: {list(clone_data.keys())}")
    print(f"克隆数据示例: name={clone_data['name']}, display_name={clone_data['display_name']}")
    
    clone_response = requests.post(f"{BASE_URL}/crewai-agents/", json=clone_data, headers=headers)
    if clone_response.status_code != 201:
        print(f"❌ 克隆失败: {clone_response.text}")
        print(f"发送的数据: {json.dumps(clone_data, indent=2, ensure_ascii=False)}")
        return
    
    cloned_agent = clone_response.json()
    print(f"✅ 克隆成功:")
    print(f"   克隆ID: {cloned_agent['id']}")
    print(f"   克隆名称: {cloned_agent['name']}")
    print(f"   克隆所有者: {cloned_agent.get('owner_info', 'N/A')}")
    
    # 9. 再次测试禁用克隆的Agent
    print("\n9. 测试禁用克隆的Agent...")
    clone_disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{cloned_agent['id']}/", 
                                           json={"is_active": False}, headers=headers)
    if clone_disable_response.status_code != 200:
        print(f"❌ 禁用克隆Agent失败: {clone_disable_response.text}")
    else:
        print("✅ 克隆Agent禁用成功")
    
    # 10. 最终检查所有Agent状态
    print("\n10. 最终检查所有Agent状态...")
    final_list_response = requests.get(f"{BASE_URL}/crewai-agents/", headers=headers)
    if final_list_response.status_code == 200:
        final_agents = final_list_response.json()["results"]
        test_agents_final = [a for a in final_agents if a['name'].startswith('test_comprehensive')]
        
        print(f"✅ 最终测试Agent列表:")
        for agent in test_agents_final:
            print(f"   - {agent['name']}: is_active={agent['is_active']}, id={agent['id']}")
    
    # 11. 清理测试数据
    print("\n11. 清理测试数据...")
    cleanup_count = 0
    for agent in test_agents_final:
        delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{agent['id']}/", headers=headers)
        if delete_response.status_code == 204:
            cleanup_count += 1
    
    print(f"✅ 清理完成，删除了 {cleanup_count} 个测试Agent")
    
    print("\n🎉 全面测试完成！所有功能正常工作。")
    return True

if __name__ == "__main__":
    test_comprehensive_agent_functions()