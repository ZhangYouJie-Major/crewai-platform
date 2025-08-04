#!/usr/bin/env python3
"""
字典树形结构展示测试脚本

测试修复后的字典列表查询和树形展示功能
"""

import requests
import json
import sys
import os

# Django 设置
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')

import django
django.setup()

from crewaiplatform.models import Dictionary

def test_dictionary_tree_structure():
    """测试字典树形结构"""
    print("=" * 50)
    print("字典树形结构测试")
    print("=" * 50)
    
    # 1. 检查数据库中的字典项
    print("\n1. 数据库中的字典项:")
    all_dicts = Dictionary.objects.all().order_by('sort_order', 'created_at')
    for dict_item in all_dicts:
        level_prefix = "  " * (dict_item.get_level() - 1)
        print(f"{level_prefix}├─ {dict_item.name} ({dict_item.code}) - Parent: {dict_item.parent.name if dict_item.parent else 'None'}")
    
    # 2. 测试根节点查询
    print("\n2. 根节点查询:")
    root_items = Dictionary.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
    for item in root_items:
        print(f"根节点: {item.name} ({item.code})")
        children = item.get_children()
        for child in children:
            print(f"  └─ 子项: {child.name} ({child.code})")
    
    # 3. 测试序列化器
    print("\n3. 测试序列化器输出:")
    from crewaiplatform.serializers import DictionarySerializer
    from django.test import RequestFactory
    
    # 模拟树形查询请求
    factory = RequestFactory()
    tree_request = factory.get('/dictionaries/', {'tree': 'true'})
    
    # 测试树形序列化
    root_items = Dictionary.objects.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
    serializer = DictionarySerializer(root_items, many=True, context={'request': tree_request})
    tree_data = serializer.data
    
    print("树形序列化结果:")
    print(json.dumps(tree_data, indent=2, ensure_ascii=False))
    
    return tree_data

def test_api_endpoints():
    """测试API端点"""
    print("\n" + "=" * 50)
    print("API端点测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # 测试需要认证，这里只做结构测试
    endpoints = [
        "/dictionaries/",
        "/dictionaries/?tree=true", 
        "/dictionaries/tree/",
        "/dictionaries/stats/"
    ]
    
    for endpoint in endpoints:
        print(f"\n测试端点: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"状态码: {response.status_code}")
            if response.status_code == 401:
                print("需要认证 - 正常")
            elif response.status_code == 200:
                data = response.json()
                print(f"响应数据结构: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
        except requests.exceptions.ConnectionError:
            print("连接失败 - 服务器可能未启动")
        except Exception as e:
            print(f"请求错误: {e}")

def create_test_data():
    """创建测试数据"""
    print("\n" + "=" * 50)
    print("创建测试数据")
    print("=" * 50)
    
    # 检查是否已有数据
    if Dictionary.objects.exists():
        print("已存在字典数据，跳过创建")
        return
    
    # 创建供应商（根节点）
    providers = [
        {"code": "openai", "name": "OpenAI", "description": "OpenAI AI模型供应商"},
        {"code": "google", "name": "Google", "description": "Google AI模型供应商"},
        {"code": "anthropic", "name": "Anthropic", "description": "Anthropic AI模型供应商"}
    ]
    
    created_providers = {}
    for provider_data in providers:
        provider = Dictionary.objects.create(
            code=provider_data["code"],
            name=provider_data["name"],
            description=provider_data["description"],
            sort_order=0,
            is_active=True
        )
        created_providers[provider_data["code"]] = provider
        print(f"创建供应商: {provider.name}")
    
    # 创建模型（子节点）
    models = [
        {"code": "gpt-4", "name": "GPT-4", "parent": "openai", "description": "OpenAI GPT-4模型"},
        {"code": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "parent": "openai", "description": "OpenAI GPT-3.5 Turbo模型"},
        {"code": "gemini-pro", "name": "Gemini Pro", "parent": "google", "description": "Google Gemini Pro模型"},
        {"code": "claude-3", "name": "Claude 3", "parent": "anthropic", "description": "Anthropic Claude 3模型"}
    ]
    
    for model_data in models:
        parent = created_providers[model_data["parent"]]
        model = Dictionary.objects.create(
            parent=parent,
            code=model_data["code"],
            name=model_data["name"],
            description=model_data["description"],
            sort_order=0,
            is_active=True
        )
        print(f"创建模型: {model.name} -> {parent.name}")

if __name__ == "__main__":
    try:
        # 创建测试数据（如果需要）
        create_test_data()
        
        # 测试树形结构
        tree_data = test_dictionary_tree_structure()
        
        # 测试API端点
        test_api_endpoints()
        
        print("\n" + "=" * 50)
        print("测试完成")
        print("=" * 50)
        
        # 验证树形结构是否正确
        if tree_data:
            has_children = any(item.get('children') for item in tree_data)
            print(f"树形结构验证: {'✓ 正确' if has_children else '✗ 缺少子级数据'}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()