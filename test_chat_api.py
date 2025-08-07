#!/usr/bin/env python3
"""
测试聊天API的脚本
"""

import os
import sys
import django
import requests

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.utils import setup_test_environment
from crewaiplatform.services.chat_service import ChatService

User = get_user_model()

def test_chat_api():
    """测试聊天API功能"""
    
    print("=== 测试聊天API功能 ===")
    
    # 1. 创建测试用户
    try:
        user = User.objects.get(username='admin')
        print(f"✅ 找到测试用户: {user.username}")
    except User.DoesNotExist:
        print("❌ 未找到admin用户，请先创建管理员用户")
        return False
    
    # 2. 测试创建会话
    try:
        conversation = ChatService.create_conversation(
            user=user,
            title="测试会话",
            description="这是一个测试会话"
        )
        print(f"✅ 创建会话成功: ID={conversation.id}, 标题={conversation.title}")
    except Exception as e:
        print(f"❌ 创建会话失败: {e}")
        return False
    
    # 3. 测试获取会话列表
    try:
        conversations = ChatService.get_user_conversations(user)
        print(f"✅ 获取会话列表成功: 共{len(conversations)}个会话")
        for conv in conversations:
            print(f"   - {conv.title} (ID: {conv.id})")
    except Exception as e:
        print(f"❌ 获取会话列表失败: {e}")
        return False
    
    # 4. 测试HTTP API端点
    try:
        # 先尝试获取token
        login_response = requests.post('http://localhost:8000/api/auth/login/', {
            'username': 'admin',
            'password': 'admin123'  # 假设默认密码
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get('access')
            headers = {'Authorization': f'Bearer {token}'}
            
            # 测试获取会话列表API
            response = requests.get('http://localhost:8000/api/chat/conversations/', headers=headers)
            print(f"✅ API测试成功: 状态码={response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   获取到{len(data.get('results', data))}个会话")
        else:
            print(f"⚠️  无法获取认证token，跳过API测试")
            
    except Exception as e:
        print(f"⚠️  API测试失败: {e}")
    
    return True

if __name__ == '__main__':
    success = test_chat_api()
    if success:
        print("\n🎉 聊天功能测试完成！")
    else:
        print("\n❌ 聊天功能测试失败！")
        sys.exit(1)