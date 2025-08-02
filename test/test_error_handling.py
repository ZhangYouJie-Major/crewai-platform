#!/usr/bin/env python3
"""
测试Agent错误处理改进
验证业务逻辑错误和字段验证错误的区别处理
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_error_handling():
    """测试错误处理改进"""
    print("🧪 开始测试错误处理改进...")
    
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
    
    # 2. 获取不可用的LLM模型ID（模拟业务逻辑错误）
    print("\n2. 获取LLM模型...")
    llm_response = requests.get(f"{BASE_URL}/llm-models/", headers=headers)
    llm_models = llm_response.json()["results"]
    
    # 找到一个不可用的模型
    unavailable_model = next((m for m in llm_models if not m.get("is_available")), None)
    available_model = next((m for m in llm_models if m.get("is_available") and m.get("is_active")), None)
    
    if not unavailable_model:
        print("❌ 没有找到不可用的LLM模型，无法测试业务逻辑错误")
        # 创建一个假的不可用模型ID来测试
        unavailable_model_id = 999
    else:
        unavailable_model_id = unavailable_model["id"]
        print(f"✅ 找到不可用模型: {unavailable_model.get('name', f'ID={unavailable_model_id}')}")
    
    if not available_model:
        print("❌ 没有可用的LLM模型")
        return
    
    # 3. 测试字段验证错误（必填字段缺失）
    print("\n3. 测试字段验证错误（必填字段缺失）...")
    field_error_data = {
        "name": "test_field_error",
        # 缺少必填字段: display_name, role, goal, backstory, llm_model
    }
    
    field_error_response = requests.post(f"{BASE_URL}/crewai-agents/", json=field_error_data, headers=headers)
    print(f"状态码: {field_error_response.status_code}")
    if field_error_response.status_code == 400:
        field_errors = field_error_response.json()
        print(f"字段验证错误响应: {json.dumps(field_errors, indent=2, ensure_ascii=False)}")
        
        # 检查是否包含non_field_errors
        if 'non_field_errors' in field_errors:
            print("❌ 字段验证错误不应该包含non_field_errors")
        else:
            print("✅ 字段验证错误格式正确")
    
    # 4. 测试业务逻辑错误（不可用的LLM模型）
    print("\n4. 测试业务逻辑错误（不可用的LLM模型）...")
    business_error_data = {
        "name": "test_business_error",
        "display_name": "测试业务逻辑错误",
        "description": "测试不可用LLM模型错误",
        "role": "测试工程师",
        "goal": "测试业务逻辑错误",
        "backstory": "测试",
        "llm_model": unavailable_model_id,
        "is_active": True,
        "is_public": False
    }
    
    business_error_response = requests.post(f"{BASE_URL}/crewai-agents/", json=business_error_data, headers=headers)
    print(f"状态码: {business_error_response.status_code}")
    if business_error_response.status_code == 400:
        business_errors = business_error_response.json()
        print(f"业务逻辑错误响应: {json.dumps(business_errors, indent=2, ensure_ascii=False)}")
        
        # 检查是否包含non_field_errors
        if 'non_field_errors' in business_errors:
            print("✅ 业务逻辑错误包含non_field_errors")
            print(f"   错误消息: {business_errors['non_field_errors']}")
        else:
            print("❌ 业务逻辑错误应该包含non_field_errors")
    
    # 5. 测试正常创建（对比）
    print("\n5. 测试正常创建（对比）...")
    normal_data = {
        "name": "test_normal_agent",
        "display_name": "正常测试Agent",
        "description": "正常创建测试",
        "role": "测试工程师",
        "goal": "正常创建",
        "backstory": "正常测试",
        "llm_model": available_model["id"],
        "is_active": True,
        "is_public": False
    }
    
    normal_response = requests.post(f"{BASE_URL}/crewai-agents/", json=normal_data, headers=headers)
    print(f"状态码: {normal_response.status_code}")
    if normal_response.status_code == 201:
        normal_agent = normal_response.json()
        print(f"✅ 正常创建成功: {normal_agent['name']}")
        
        # 清理
        requests.delete(f"{BASE_URL}/crewai-agents/{normal_agent['id']}/", headers=headers)
        print("✅ 测试数据已清理")
    else:
        print(f"❌ 正常创建失败: {normal_response.text}")
    
    print("\n🎉 错误处理测试完成！")

if __name__ == "__main__":
    test_error_handling()