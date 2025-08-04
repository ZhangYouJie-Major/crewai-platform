#!/usr/bin/env python3
"""
测试字典管理中子项目编辑时父项目显示的问题
"""

import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_dictionary_parent_display():
    """测试字典管理中子项目编辑时父项目显示"""
    
    print("=== 测试字典管理中子项目编辑时父项目显示 ===")
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
        login_response.raise_for_status()
        token = login_response.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✓ 登录成功")
    except Exception as e:
        print(f"✗ 登录失败: {e}")
        return
    
    # 2. 创建父级字典项
    print("\n2. 创建父级字典项...")
    parent_data = {
        "code": "test_parent",
        "name": "测试父级项目",
        "description": "用于测试的父级字典项",
        "sort_order": 1,
        "is_active": True
    }
    
    try:
        parent_response = requests.post(
            f"{API_BASE}/dictionaries/", 
            json=parent_data, 
            headers=headers
        )
        parent_response.raise_for_status()
        parent_dict = parent_response.json()
        parent_id = parent_dict["id"]
        print(f"✓ 创建父级字典项成功: {parent_dict['name']} (ID: {parent_id})")
    except Exception as e:
        print(f"✗ 创建父级字典项失败: {e}")
        return
    
    # 3. 创建子级字典项
    print("\n3. 创建子级字典项...")
    child_data = {
        "parent": parent_id,
        "code": "test_child",
        "name": "测试子级项目",
        "description": "用于测试的子级字典项",
        "sort_order": 1,
        "is_active": True
    }
    
    try:
        child_response = requests.post(
            f"{API_BASE}/dictionaries/", 
            json=child_data, 
            headers=headers
        )
        child_response.raise_for_status()
        child_dict = child_response.json()
        child_id = child_dict["id"]
        print(f"✓ 创建子级字典项成功: {child_dict['name']} (ID: {child_id})")
    except Exception as e:
        print(f"✗ 创建子级字典项失败: {e}")
        return
    
    # 4. 测试获取字典列表（包含父级信息）
    print("\n4. 测试获取字典列表（包含父级信息）...")
    try:
        list_response = requests.get(
            f"{API_BASE}/dictionaries/?include_parents=true", 
            headers=headers
        )
        list_response.raise_for_status()
        dictionaries = list_response.json()
        print(f"✓ 获取字典列表成功，共 {len(dictionaries.get('results', dictionaries))} 项")
        
        # 查找子级项目
        child_item = None
        for item in dictionaries.get('results', dictionaries):
            if item['id'] == child_id:
                child_item = item
                break
        
        if child_item:
            print(f"✓ 找到子级项目: {child_item['name']}")
            print(f"  父级ID: {child_item.get('parent')}")
            print(f"  父级名称: {child_item.get('parent_name', 'N/A')}")
            print(f"  父级代码: {child_item.get('parent_code', 'N/A')}")
        else:
            print("✗ 未找到子级项目")
            
    except Exception as e:
        print(f"✗ 获取字典列表失败: {e}")
    
    # 5. 测试获取单个字典项详情
    print("\n5. 测试获取单个字典项详情...")
    try:
        detail_response = requests.get(
            f"{API_BASE}/dictionaries/{child_id}/", 
            headers=headers
        )
        detail_response.raise_for_status()
        detail = detail_response.json()
        print(f"✓ 获取字典项详情成功: {detail['name']}")
        print(f"  父级ID: {detail.get('parent')}")
        print(f"  父级名称: {detail.get('parent_name', 'N/A')}")
        print(f"  父级代码: {detail.get('parent_code', 'N/A')}")
        
    except Exception as e:
        print(f"✗ 获取字典项详情失败: {e}")
    
    # 6. 清理测试数据
    print("\n6. 清理测试数据...")
    try:
        # 删除子级项目
        requests.delete(f"{API_BASE}/dictionaries/{child_id}/", headers=headers)
        print("✓ 删除子级项目成功")
        
        # 删除父级项目
        requests.delete(f"{API_BASE}/dictionaries/{parent_id}/", headers=headers)
        print("✓ 删除父级项目成功")
        
    except Exception as e:
        print(f"✗ 清理测试数据失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_dictionary_parent_display() 