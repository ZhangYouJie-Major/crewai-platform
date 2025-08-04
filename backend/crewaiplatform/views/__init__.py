"""
Views包，包含所有业务模块的视图

按业务模块划分：
- auth_views: 认证相关视图 (登录、注册、登出)
- user_views: 用户管理视图 (用户、角色、权限管理) 
- crewai_views: CrewAI集成视图 (LLM模型、MCP工具、Agent管理)
- dictionary_views: 字典管理视图 (字典类型、字典项管理)
"""

# 认证相关视图
from .auth_views import (
    AuthViewSet,
    UserInfoView,
)

# 用户管理相关视图
from .user_views import (
    UserViewSet,
    RoleViewSet, 
    PermissionViewSet,
    UserRoleViewSet,
    RolePermissionViewSet,
    DashboardView,
)

# CrewAI集成相关视图
from .crewai_views import (
    LLMModelViewSet,
    MCPToolViewSet,
    CrewAIAgentViewSet,
    AgentToolRelationViewSet,
)

# 字典管理相关视图
from .dictionary_views import (
    DictionaryViewSet,
)

# 导出所有视图类
__all__ = [
    # 认证相关
    'AuthViewSet',
    'UserInfoView',
    
    # 用户管理相关
    'UserViewSet',
    'RoleViewSet', 
    'PermissionViewSet',
    'UserRoleViewSet',
    'RolePermissionViewSet',
    'DashboardView',
    
    # CrewAI集成相关
    'LLMModelViewSet',
    'MCPToolViewSet',
    'CrewAIAgentViewSet',
    'AgentToolRelationViewSet',
    
    # 字典管理相关
    'DictionaryViewSet',
]