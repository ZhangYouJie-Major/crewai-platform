#!/usr/bin/env python3
"""
测试配置文件
包含测试环境的各种配置信息
"""

# API配置
API_BASE_URL = "http://localhost:8000/api"

# 测试账号配置
TEST_ACCOUNTS = {
    "admin": {
        "username": "admin",
        "password": "1234qwer*"
    },
    "testuser": {
        "username": "testuser",
        "password": "testpass123"
    }
}

# API端点配置
API_ENDPOINTS = {
    "auth": {
        "login": "/auth/login/",
        "logout": "/auth/logout/",
        "refresh": "/auth/token/refresh/"
    },
    "users": {
        "list": "/users/",
        "create": "/users/",
        "detail": "/users/{id}/",
        "update": "/users/{id}/",
        "delete": "/users/{id}/"
    },
    "agents": {
        "list": "/crewai-agents/",
        "create": "/crewai-agents/",
        "detail": "/crewai-agents/{id}/",
        "update": "/crewai-agents/{id}/",
        "delete": "/crewai-agents/{id}/",
        "clone": "/crewai-agents/{id}/clone/",
        "toggle": "/crewai-agents/{id}/toggle/"
    },
    "mcp_tools": {
        "list": "/mcp-tools/",
        "create": "/mcp-tools/",
        "detail": "/mcp-tools/{id}/",
        "update": "/mcp-tools/{id}/",
        "delete": "/mcp-tools/{id}/",
        "health_check": "/mcp-tools/{id}/health-check/"
    },
    "dictionary": {
        "list": "/dictionary/",
        "create": "/dictionary/",
        "detail": "/dictionary/{id}/",
        "update": "/dictionary/{id}/",
        "delete": "/dictionary/{id}/",
        "tree": "/dictionary/tree/"
    },
    "llm_models": {
        "list": "/llm-models/",
        "create": "/llm-models/",
        "detail": "/llm-models/{id}/",
        "update": "/llm-models/{id}/",
        "delete": "/llm-models/{id}/"
    },
    "roles": {
        "list": "/roles/",
        "create": "/roles/",
        "detail": "/roles/{id}/",
        "update": "/roles/{id}/",
        "delete": "/roles/{id}/"
    },
    "permissions": {
        "list": "/permissions/",
        "create": "/permissions/",
        "detail": "/permissions/{id}/",
        "update": "/permissions/{id}/",
        "delete": "/permissions/{id}/"
    }
}

# 测试数据配置
TEST_DATA = {
    "agent": {
        "name": "test_agent",
        "display_name": "测试Agent",
        "description": "用于测试的Agent",
        "role": "测试工程师",
        "goal": "执行测试任务",
        "backstory": "这是一个测试用的Agent",
        "is_active": True,
        "is_public": False,
        "verbose": True,
        "memory": False,
        "max_iter": 10,
        "allow_delegation": False
    },
    "mcp_tool": {
        "name": "test_tool",
        "display_name": "测试工具",
        "description": "用于测试的MCP工具",
        "server_url": "http://localhost:8080",
        "is_active": True
    },
    "dictionary": {
        "name": "测试字典",
        "description": "用于测试的字典",
        "parent": None
    },
    "user": {
        "username": "testuser_new",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }
}

# 测试超时配置
TIMEOUT = 30  # 秒

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 