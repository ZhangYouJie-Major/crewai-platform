#!/usr/bin/env python3
"""
简单的API测试脚本
用于验证CrewAI平台的API端点是否正常工作
"""

import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000/api"

def test_login():
    """测试登录API"""
    print("🔐 测试用户登录...")
    
    login_data = {
        "username": "testapi",
        "password": "testapi123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            print("✅ 登录成功!")
            return access_token
        else:
            print("❌ 登录失败:", response.text)
            return None
    except Exception as e:
        print(f"❌ 登录请求出错: {e}")
        return None

def test_llm_models_api(token):
    """测试LLM模型API"""
    print("🤖 测试LLM模型API...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # 测试获取模型列表
        response = requests.get(f"{BASE_URL}/llm-models/", headers=headers)
        print(f"获取模型列表响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data if isinstance(data, list) else data.get('results', [])
            print(f"✅ 成功获取模型列表，共 {len(models)} 个模型")
            for model in models[:3]:  # 只显示前3个
                print(f"  - {model.get('name', 'Unknown')} ({model.get('provider', 'Unknown')})")
            return True
        else:
            print("❌ 获取模型列表失败:", response.text)
            return False
    except Exception as e:
        print(f"❌ 请求出错: {e}")
        return False

def main():
    print("🚀 CrewAI Platform API 测试")
    print("=" * 40)
    
    # 测试登录
    token = test_login()
    if not token:
        print("❌ 无法获取访问令牌，跳过后续测试")
        return
    
    print()
    # 测试LLM模型API
    test_llm_models_api(token)
    
    print()
    print("🎉 测试完成!")

if __name__ == "__main__":
    main()