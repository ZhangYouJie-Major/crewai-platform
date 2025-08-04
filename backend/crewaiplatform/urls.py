from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    AuthViewSet, UserInfoView, UserViewSet, RoleViewSet, PermissionViewSet,
    UserRoleViewSet, RolePermissionViewSet, DashboardView,
    # CrewAI相关视图
    LLMModelViewSet, MCPToolViewSet, CrewAIAgentViewSet, AgentToolRelationViewSet,
    # 字典管理视图
    DictionaryViewSet
)

# 创建路由器实例，用于自动生成RESTful API路由
router = DefaultRouter()

# RBAC权限管理路由
router.register(r'users', UserViewSet)           # 用户管理CRUD接口
router.register(r'roles', RoleViewSet)           # 角色管理CRUD接口  
router.register(r'permissions', PermissionViewSet) # 权限管理CRUD接口
router.register(r'user-roles', UserRoleViewSet)  # 用户角色关联CRUD接口
router.register(r'role-permissions', RolePermissionViewSet) # 角色权限关联CRUD接口

# CrewAI集成路由
router.register(r'llm-models', LLMModelViewSet)  # LLM模型配置CRUD接口
router.register(r'mcp-tools', MCPToolViewSet)    # MCP工具配置CRUD接口  
router.register(r'crewai-agents', CrewAIAgentViewSet) # CrewAI Agent配置CRUD接口
router.register(r'agent-tool-relations', AgentToolRelationViewSet) # Agent-Tool关联CRUD接口

# 字典管理路由
router.register(r'dictionaries', DictionaryViewSet)  # 字典项CRUD接口

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),
    
    # API路由
    path('api/', include([
        # 认证相关接口
        path('auth/register/', AuthViewSet.RegisterView.as_view(), name='register'),  # 用户注册
        path('auth/login/', AuthViewSet.LoginView.as_view(), name='login'),          # 用户登录
        path('auth/logout/', AuthViewSet.LogoutView.as_view(), name='logout'),       # 用户登出
        path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # 刷新Token
        path('auth/me/', UserInfoView.as_view(), name='user_info'),                  # 获取当前用户信息
        
        # 仪表盘数据
        path('dashboard/', DashboardView.as_view(), name='dashboard'),               # 仪表盘数据
        
        # 包含路由器生成的所有CRUD接口
        path('', include(router.urls)),
    ])),
]