#!/usr/bin/env python3
"""
测试Agent更新功能的完整流程
验证owner字段在更新时是否正确处理
"""
import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api"

def test_agent_crud():
    """测试Agent的创建、读取、更新、删除流程"""
    print("🧪 开始测试Agent CRUD功能...")
    
    # 1. 登录获取token
    print("\n1. 正在登录...")
    login_data = {
        "username": "testuser_update", 
        "password": "testpass123"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if login_response.status_code == 200:
            token = login_response.json()["access"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"✅ 登录成功，获取到token")
        else:
            print(f"❌ 登录失败: {login_response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        return
    
    # 2. 获取可用的LLM模型
    print("\n2. 获取LLM模型...")
    try:
        llm_response = requests.get(f"{BASE_URL}/llm-models/", headers=headers)
        if llm_response.status_code == 200:
            llm_models = llm_response.json()["results"]
            available_model = None
            for model in llm_models:
                if model.get("is_available") and model.get("is_active"):
                    available_model = model
                    break
            
            if not available_model:
                print("❌ 没有可用的LLM模型")
                return
            
            print(f"✅ 找到可用模型: {available_model['name']}")
        else:
            print(f"❌ 获取LLM模型失败: {llm_response.text}")
            return
    except Exception as e:
        print(f"❌ 获取LLM模型异常: {str(e)}")
        return
    
    # 3. 创建Agent
    print("\n3. 创建Agent...")
    create_data = {
        "name": "test_update_agent",
        "display_name": "测试更新Agent",
        "description": "用于测试更新功能的Agent",
        "role": "测试工程师",
        "goal": "验证Agent更新功能是否正常",
        "backstory": "这是一个专门用于测试的Agent，用来验证owner字段的处理",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False,
        "verbose": False,
        "memory": False,
        "max_iter": 20,
        "allow_delegation": False
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/crewai-agents/", json=create_data, headers=headers)
        if create_response.status_code == 201:
            agent = create_response.json()
            agent_id = agent["id"]
            print(f"✅ Agent创建成功:")
            print(f"   ID: {agent_id}")
            print(f"   名称: {agent['name']}")
            print(f"   所有者: {agent['owner_info']}")
        else:
            print(f"❌ Agent创建失败: {create_response.text}")
            return
    except Exception as e:
        print(f"❌ 创建Agent异常: {str(e)}")
        return
    
    # 4. 更新Agent（不包含owner字段）
    print("\n4. 更新Agent...")
    update_data = {
        "name": "test_update_agent",  # 保持原名称
        "display_name": "测试更新Agent-已修改",
        "description": "更新后的描述：验证owner字段不会被覆盖",
        "role": "高级测试工程师",
        "goal": "验证Agent更新功能和owner字段保护",
        "backstory": "更新后的背景：确保owner字段在更新时保持不变",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": True,  # 从false改为true
        "verbose": True,    # 从false改为true
        "memory": True,     # 从false改为true
        "max_iter": 25,     # 从20改为25
        "allow_delegation": True  # 从false改为true
    }
    
    try:
        update_response = requests.put(f"{BASE_URL}/crewai-agents/{agent_id}/", json=update_data, headers=headers)
        if update_response.status_code == 200:
            updated_agent = update_response.json()
            print(f"✅ Agent更新成功:")
            print(f"   显示名称: {updated_agent['display_name']}")
            print(f"   角色: {updated_agent['role']}")
            print(f"   所有者: {updated_agent['owner_info']} (应该保持不变)")
            print(f"   公开状态: {updated_agent['is_public']} (应该是True)")
            print(f"   详细日志: {updated_agent['verbose']} (应该是True)")
            print(f"   记忆功能: {updated_agent['memory']} (应该是True)")
            print(f"   最大迭代: {updated_agent['max_iter']} (应该是25)")
            
            # 验证owner是否保持不变
            if updated_agent['owner_info'] == agent['owner_info']:
                print("✅ Owner字段保护成功：更新时owner字段保持不变")
            else:
                print(f"❌ Owner字段保护失败：原owner={agent['owner_info']}, 新owner={updated_agent['owner_info']}")
        else:
            print(f"❌ Agent更新失败: {update_response.text}")
    except Exception as e:
        print(f"❌ 更新Agent异常: {str(e)}")
    
    # 5. 清理：删除测试Agent
    print("\n5. 清理测试数据...")
    try:
        delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
        if delete_response.status_code == 204:
            print("✅ 测试Agent已删除")
        else:
            print(f"⚠️ 删除Agent失败: {delete_response.text}")
    except Exception as e:
        print(f"⚠️ 删除Agent异常: {str(e)}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_agent_crud()