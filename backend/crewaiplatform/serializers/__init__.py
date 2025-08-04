"""
序列化器模块

提供统一的序列化器接口，支持：
- 用户认证和权限管理
- CrewAI Agent配置
- LLM模型管理
- MCP工具管理
- 数据字典管理
"""

# 认证和用户管理序列化器
from .auth_serializers import (
    UserRegisterSerializer,
    UserSerializer,
)

# RBAC权限管理序列化器  
from .rbac_serializers import (
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    RolePermissionSerializer,
)

# CrewAI相关序列化器
from .crewai_serializers import (
    LLMModelSerializer,
    LLMModelSimpleSerializer,
    MCPToolSerializer,
    MCPToolSimpleSerializer,
    CrewAIAgentSerializer,
    CrewAIAgentSimpleSerializer,
    AgentToolRelationSerializer,
    AgentToolBindingSerializer,
)

# 统计数据序列化器
from .stats_serializers import (
    LLMModelStatsSerializer,
    MCPToolStatsSerializer,
    CrewAIAgentStatsSerializer,
)

# 数据字典序列化器
from .dictionary_serializers import (
    DictionarySerializer,
    DictionarySimpleSerializer,
    DictionaryTreeSerializer,
    DictionaryOptionsSerializer,
)

__all__ = [
    # 认证和用户
    'UserRegisterSerializer',
    'UserSerializer',
    
    # RBAC权限
    'RoleSerializer',
    'PermissionSerializer', 
    'UserRoleSerializer',
    'RolePermissionSerializer',
    
    # CrewAI相关
    'LLMModelSerializer',
    'LLMModelSimpleSerializer',
    'MCPToolSerializer',
    'MCPToolSimpleSerializer',
    'CrewAIAgentSerializer',
    'CrewAIAgentSimpleSerializer',
    'AgentToolRelationSerializer',
    'AgentToolBindingSerializer',
    
    # 统计数据
    'LLMModelStatsSerializer',
    'MCPToolStatsSerializer', 
    'CrewAIAgentStatsSerializer',
    
    # 数据字典
    'DictionarySerializer',
    'DictionarySimpleSerializer',
    'DictionaryTreeSerializer',
    'DictionaryOptionsSerializer',
]