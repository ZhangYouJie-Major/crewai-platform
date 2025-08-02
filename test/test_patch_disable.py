#!/usr/bin/env python3
"""
测试Agent禁用功能 - 使用PATCH请求
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_agent_disable_patch():
    """测试Agent禁用功能 - 使用PATCH请求"""
    print("🧪 开始测试Agent禁用功能（PATCH请求）...")
    
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
    create_data = {
        "name": "test_patch_agent",
        "display_name": "测试PATCH Agent",
        "description": "测试PATCH请求功能",
        "role": "测试工程师",
        "goal": "测试PATCH更新",
        "backstory": "PATCH测试",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False
    }
    
    create_response = requests.post(f"{BASE_URL}/crewai-agents/", json=create_data, headers=headers)
    agent = create_response.json()
    agent_id = agent["id"]
    
    print(f"✅ 测试Agent创建成功: {agent['name']}, 当前状态: {agent['is_active']}")
    
    # 测试PATCH禁用
    print("\n1. 测试PATCH禁用...")
    disable_data = {"is_active": False}
    disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=disable_data, headers=headers)
    
    if disable_response.status_code == 200:
        disabled_agent = disable_response.json()
        print(f"✅ PATCH禁用成功: 状态 {agent['is_active']} -> {disabled_agent['is_active']}")
    else:
        print(f"❌ PATCH禁用失败: {disable_response.text}")
    
    # 测试PATCH启用
    print("\n2. 测试PATCH启用...")
    enable_data = {"is_active": True}
    enable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=enable_data, headers=headers)
    
    if enable_response.status_code == 200:
        enabled_agent = enable_response.json()
        print(f"✅ PATCH启用成功: 状态 {disabled_agent['is_active']} -> {enabled_agent['is_active']}")
    else:
        print(f"❌ PATCH启用失败: {enable_response.text}")
    
    # 清理
    requests.delete(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
    print(f"✅ 测试数据已清理")
    
    print("\n🎉 PATCH测试完成！")

if __name__ == "__main__":
    test_agent_disable_patch()