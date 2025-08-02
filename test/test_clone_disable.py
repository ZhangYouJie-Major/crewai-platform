#!/usr/bin/env python3
"""
测试Agent克隆和禁用功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_agent_clone_and_disable():
    """测试Agent克隆和禁用功能"""
    print("🧪 开始测试Agent克隆和禁用功能...")
    
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
            print(f"✅ 登录成功")
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
    
    # 3. 创建测试Agent
    print("\n3. 创建测试Agent...")
    create_data = {
        "name": "test_clone_disable_agent",
        "display_name": "测试克隆禁用Agent",
        "description": "用于测试克隆和禁用功能的Agent",
        "role": "测试工程师",
        "goal": "验证克隆和禁用功能是否正常",
        "backstory": "这是一个专门用于测试的Agent",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False
    }
    
    try:
        create_response = requests.post(f"{BASE_URL}/crewai-agents/", json=create_data, headers=headers)
        if create_response.status_code == 201:
            original_agent = create_response.json()
            agent_id = original_agent["id"]
            print(f"✅ 原始Agent创建成功:")
            print(f"   ID: {agent_id}")
            print(f"   名称: {original_agent['name']}")
            print(f"   激活状态: {original_agent['is_active']}")
        else:
            print(f"❌ Agent创建失败: {create_response.text}")
            return
    except Exception as e:
        print(f"❌ 创建Agent异常: {str(e)}")
        return
    
    # 4. 测试克隆功能
    print("\n4. 测试Agent克隆...")
    
    # 模拟前端克隆逻辑
    clone_data = {**original_agent}
    
    # 移除不需要的字段
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
    
    try:
        clone_response = requests.post(f"{BASE_URL}/crewai-agents/", json=clone_data, headers=headers)
        if clone_response.status_code == 201:
            cloned_agent = clone_response.json()
            print(f"✅ Agent克隆成功:")
            print(f"   克隆ID: {cloned_agent['id']}")
            print(f"   克隆名称: {cloned_agent['name']}")
            print(f"   原始所有者: {original_agent.get('owner_info', 'N/A')}")
            print(f"   克隆所有者: {cloned_agent.get('owner_info', 'N/A')}")
        else:
            print(f"❌ Agent克隆失败: {clone_response.text}")
    except Exception as e:
        print(f"❌ 克隆Agent异常: {str(e)}")
    
    # 5. 测试禁用功能
    print("\n5. 测试Agent禁用...")
    try:
        disable_data = {"is_active": False}
        disable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=disable_data, headers=headers)
        if disable_response.status_code == 200:
            disabled_agent = disable_response.json()
            print(f"✅ Agent禁用成功:")
            print(f"   激活状态: {disabled_agent['is_active']}")
        else:
            print(f"❌ Agent禁用失败: {disable_response.text}")
    except Exception as e:
        print(f"❌ 禁用Agent异常: {str(e)}")
    
    # 6. 测试启用功能
    print("\n6. 测试Agent启用...")
    try:
        enable_data = {"is_active": True}
        enable_response = requests.patch(f"{BASE_URL}/crewai-agents/{agent_id}/", json=enable_data, headers=headers)
        if enable_response.status_code == 200:
            enabled_agent = enable_response.json()
            print(f"✅ Agent启用成功:")
            print(f"   激活状态: {enabled_agent['is_active']}")
        else:
            print(f"❌ Agent启用失败: {enable_response.text}")
    except Exception as e:
        print(f"❌ 启用Agent异常: {str(e)}")
    
    # 7. 清理测试数据
    print("\n7. 清理测试数据...")
    try:
        # 删除原始Agent
        delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{agent_id}/", headers=headers)
        if delete_response.status_code == 204:
            print("✅ 原始Agent已删除")
        
        # 删除克隆Agent（如果创建成功）
        if 'cloned_agent' in locals():
            clone_delete_response = requests.delete(f"{BASE_URL}/crewai-agents/{cloned_agent['id']}/", headers=headers)
            if clone_delete_response.status_code == 204:
                print("✅ 克隆Agent已删除")
    except Exception as e:
        print(f"⚠️ 清理数据异常: {str(e)}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_agent_clone_and_disable()