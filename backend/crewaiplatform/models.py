"""
模型导入文件 - 从models包中导入所有模型
为了保持向后兼容性，保留原有的导入方式
"""

# 从models包中导入所有模型
from .models import (
    # RBAC权限管理模型
    User,
    Role,
    Permission,
    UserRole,
    RolePermission,
    
    # CrewAI集成模型
    LLMModel,
    MCPTool,
    CrewAIAgent,
    AgentToolRelation,
    
    # 字典管理模型
    Dictionary,
    DictionaryItem,
)

# 为了向后兼容，保持原有的导入方式
__all__ = [
    # RBAC模型
    'User',
    'Role',
    'Permission',
    'UserRole',
    'RolePermission',
    
    # CrewAI集成模型
    'LLMModel',
    'MCPTool',
    'CrewAIAgent', 
    'AgentToolRelation',
    
    # 字典管理模型
    'Dictionary',
    'DictionaryItem',
]