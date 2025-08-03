#!/usr/bin/env python3
"""
调试Agent查询问题
"""
import requests

BASE_URL = "http://localhost:8000/api"

def debug_agent_query():
    """调试Agent查询问题"""
    print("🔍 调试Agent查询问题...")
    
    # 登录
    login_data = {"username": "testuser_update", "password": "testpass123"}
    login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    token = login_response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取LLM模型
    llm_response = requests.get(f"{BASE_URL}/llm-models/", headers=headers)
    llm_models = llm_response.json()["results"]
    available_model = next(m for m in llm_models if m.get("is_available") and m.get("is_active"))
    
    # 创建测试Agent
    import time
    timestamp = int(time.time())
    create_data = {
        "name": f"debug_agent_{timestamp}",
        "display_name": f"调试Agent_{timestamp}",
        "description": "调试查询问题",
        "role": "调试工程师",
        "goal": "调试查询",
        "backstory": "调试",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False
    }
    
    create_response = requests.post(f"{BASE_URL}/crewai-agents/", json=create_data, headers=headers)
    if create_response.status_code != 201:
        print(f"❌ Agent创建失败: {create_response.text}")
        return
    
    agent = create_response.json()
    agent_id = agent["id"]
    
    print(f"✅ Agent创建: ID={agent_id}, is_active={agent['is_active']}")
    
    # 查询创建的Agent
    print(f"\n1. 查询Agent {agent_id}...")
    get_response = requests.get(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    if get_response.status_code == 200:
        print(f"✅ 查询成功: {get_response.json()['name']}")
    else:
        print(f"❌ 查询失败: {get_response.text}")
    
    # 禁用Agent
    print(f"\n2. 禁用Agent {agent_id}...")
    disable_data = {"is_active": False}
    disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=disable_data, headers=headers)
    if disable_response.status_code == 200:
        disabled_agent = disable_response.json()
        print(f"✅ 禁用成功: is_active={disabled_agent['is_active']}")
    else:
        print(f"❌ 禁用失败: {disable_response.text}")
        return
    
    # 再次查询Agent
    print(f"\n3. 禁用后查询Agent {agent_id}...")
    get_response2 = requests.get(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    if get_response2.status_code == 200:
        agent_data = get_response2.json()
        print(f"✅ 查询成功: {agent_data['name']}, is_active={agent_data['is_active']}")
    else:
        print(f"❌ 查询失败: {get_response2.text}")
    
    # 查询所有Agent列表
    print(f"\n4. 查询所有Agent列表...")
    list_response = requests.get(f"{BASE_URL}/crewai-agents/", headers=headers)
    if list_response.status_code == 200:
        agents = list_response.json()["results"]
        debug_agents = [a for a in agents if a['name'].startswith('debug_agent')]
        print(f"✅ 找到调试Agent数量: {len(debug_agents)}")
        if debug_agents:
            print(f"   Agent详情: ID={debug_agents[0]['id']}, is_active={debug_agents[0]['is_active']}")
    else:
        print(f"❌ 查询列表失败: {list_response.text}")
    
    # 清理
    print(f"\n5. 清理测试数据...")
    delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    print(f"删除结果: {delete_response.status_code}")

if __name__ == "__main__":
    debug_agent_query()