#!/usr/bin/env python3
"""
测试Agent禁用启用功能完整流程
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_agent_toggle_complete():
    """测试Agent禁用启用功能完整流程"""
    print("🧪 开始测试Agent禁用/启用完整流程...")
    
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
        "name": f"test_toggle_agent_{timestamp}",
        "display_name": "测试禁用启用Agent",
        "description": "测试禁用启用功能",
        "role": "测试工程师",
        "goal": "测试禁用启用",
        "backstory": "禁用启用测试",
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
    
    print(f"✅ 测试Agent创建成功: {agent['name']}")
    print(f"   初始状态: is_active = {agent['is_active']}")
    
    # 测试禁用
    print("\n1. 测试禁用功能...")
    disable_data = {"is_active": False}
    disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=disable_data, headers=headers)
    
    if disable_response.status_code == 200:
        disabled_agent = disable_response.json()
        print(f"✅ 禁用成功: is_active = {disabled_agent['is_active']}")
        
        # 测试启用
        print("\n2. 测试启用功能...")
        enable_data = {"is_active": True}
        enable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=enable_data, headers=headers)
        
        if enable_response.status_code == 200:
            enabled_agent = enable_response.json()
            print(f"✅ 启用成功: is_active = {enabled_agent['is_active']}")
        else:
            print(f"❌ 启用失败: {enable_response.text}")
            
    else:
        print(f"❌ 禁用失败: {disable_response.text}")
    
    # 清理
    delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    if delete_response.status_code == 204:
        print(f"\n✅ 测试数据已清理")
    
    print("\n🎉 禁用/启用测试完成！")

if __name__ == "__main__":
    test_agent_toggle_complete()