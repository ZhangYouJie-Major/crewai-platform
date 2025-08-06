"""
平台模型包

包含以下模型:
RBAC权限管理模型:
- User: 用户模型
- Role: 角色模型  
- Permission: 权限模型
- UserRole: 用户角色关联模型
- RolePermission: 角色权限关联模型

CrewAI集成模型:
- LLMModel: LLM大语言模型配置
- MCPTool: MCP工具配置
- CrewAIAgent: CrewAI智能代理配置
- AgentToolRelation: Agent与工具的关联关系
"""

from .user import User
from .role import Role
from .permission import Permission
from .user_role import UserRole
from .role_permission import RolePermission

# CrewAI集成模型
from .llm_model import LLMModel
from .mcp_tool import MCPTool
from .crewai_agent import CrewAIAgent
from .agent_tool_relation import AgentToolRelation

# 字典管理模型
from .dictionary import Dictionary, DictType

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
    'DictType',
]