from django.contrib import admin
from .models import User, Role, Permission, UserRole, RolePermission
from .models import LLMModel, MCPTool, CrewAIAgent, AgentToolRelation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """用户管理"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """权限管理"""
    list_display = ('name', 'codename', 'description', 'created_at')
    search_fields = ('name', 'codename', 'description')
    list_filter = ('created_at',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """用户角色关联管理"""
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__username', 'role__name')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """角色权限关联管理"""
    list_display = ('role', 'permission', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('role__name', 'permission__name')

# ============================================================================
# CrewAI 集成模型 Admin
# ============================================================================

@admin.register(LLMModel)
class LLMModelAdmin(admin.ModelAdmin):
    """LLM模型配置管理"""
    list_display = ('name', 'provider', 'model_name', 'is_available', 'is_active', 'last_validated', 'created_at')
    list_filter = ('provider', 'is_available', 'is_active', 'created_at')
    search_fields = ('name', 'model_name', 'description')
    readonly_fields = ('last_validated', 'is_available', 'validation_error', 'model_info', 'created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'provider', 'model_name', 'description')
        }),
        ('LangChain配置', {
            'fields': ('langchain_class', 'api_base_url', 'api_key', 'api_version')
        }),
        ('模型参数', {
            'fields': ('temperature', 'max_tokens', 'timeout', 'max_retries')
        }),
        ('高级配置', {
            'fields': ('extra_kwargs', 'model_kwargs'),
            'classes': ('collapse',)
        }),
        ('状态信息', {
            'fields': ('is_active', 'is_available', 'last_validated', 'validation_error', 'model_info'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(MCPTool)
class MCPToolAdmin(admin.ModelAdmin):
    """MCP工具配置管理"""
    list_display = ('name', 'display_name', 'server_type', 'status', 'is_active', 'total_calls', 'success_rate', 'last_health_check')
    list_filter = ('server_type', 'status', 'is_active', 'is_public', 'created_at')
    search_fields = ('name', 'display_name', 'description')
    readonly_fields = ('status', 'last_health_check', 'last_error', 'response_time_ms', 'total_calls', 'success_calls', 'created_at', 'updated_at')
    filter_horizontal = ('allowed_users',)
    
    def success_rate(self, obj):
        return f"{obj.get_success_rate():.1f}%"
    success_rate.short_description = '成功率'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'display_name', 'description', 'version')
        }),
        ('MCP配置', {
            'fields': ('server_type', 'connection_config', 'tool_schema')
        }),
        ('连接设置', {
            'fields': ('connection_timeout', 'request_timeout', 'max_retries', 'retry_delay')
        }),
        ('健康检查', {
            'fields': ('health_check_enabled', 'health_check_interval', 'health_check_method')
        }),
        ('权限控制', {
            'fields': ('is_active', 'is_public', 'allowed_users')
        }),
        ('状态信息', {
            'fields': ('status', 'last_health_check', 'last_error', 'response_time_ms', 'total_calls', 'success_calls'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CrewAIAgent)
class CrewAIAgentAdmin(admin.ModelAdmin):
    """CrewAI Agent配置管理"""
    list_display = ('name', 'display_name', 'role', 'status', 'owner', 'llm_model', 'is_active', 'total_tasks', 'success_rate', 'last_execution')
    list_filter = ('status', 'is_active', 'is_public', 'owner', 'llm_model', 'created_at')
    search_fields = ('name', 'display_name', 'role', 'goal', 'description')
    readonly_fields = ('status', 'total_tasks', 'completed_tasks', 'total_execution_time', 'last_execution', 'last_error', 'created_at', 'updated_at')
    filter_horizontal = ('allowed_users',)
    
    def success_rate(self, obj):
        return f"{obj.get_success_rate():.1f}%"
    success_rate.short_description = '成功率'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'display_name', 'description', 'owner')
        }),
        ('CrewAI核心配置', {
            'fields': ('role', 'goal', 'backstory')
        }),
        ('LLM配置', {
            'fields': ('llm_model', 'function_calling_llm')
        }),
        ('执行控制', {
            'fields': ('verbose', 'memory', 'max_iter', 'max_rpm', 'max_execution_time', 'max_retry_limit')
        }),
        ('高级功能', {
            'fields': ('allow_delegation', 'respect_context_window', 'use_system_prompt', 'multimodal', 'inject_date', 'date_format', 'reasoning', 'max_reasoning_attempts'),
            'classes': ('collapse',)
        }),
        ('监控和回调', {
            'fields': ('step_callback', 'enable_monitoring'),
            'classes': ('collapse',)
        }),
        ('自定义配置', {
            'fields': ('custom_instructions', 'agent_kwargs'),
            'classes': ('collapse',)
        }),
        ('权限控制', {
            'fields': ('is_active', 'is_public', 'allowed_users')
        }),
        ('状态统计', {
            'fields': ('status', 'total_tasks', 'completed_tasks', 'total_execution_time', 'last_execution', 'last_error'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(AgentToolRelation)
class AgentToolRelationAdmin(admin.ModelAdmin):
    """Agent-Tool关联管理"""
    list_display = ('agent', 'tool', 'order', 'status', 'permission_level', 'is_required', 'total_calls', 'success_rate', 'last_used')
    list_filter = ('status', 'permission_level', 'is_required', 'is_fallback', 'assigned_at')
    search_fields = ('agent__name', 'tool__name', 'agent__display_name', 'tool__display_name')
    readonly_fields = ('total_calls', 'successful_calls', 'total_execution_time', 'last_used', 'last_error', 'config_version', 'assigned_at', 'updated_at')
    
    def success_rate(self, obj):
        return f"{obj.get_success_rate():.1f}%"
    success_rate.short_description = '成功率'
    
    fieldsets = (
        ('关联信息', {
            'fields': ('agent', 'tool', 'order')
        }),
        ('使用控制', {
            'fields': ('is_required', 'is_fallback', 'max_calls_per_task')
        }),
        ('权限配置', {
            'fields': ('permission_level', 'allowed_operations', 'restricted_paths')
        }),
        ('配置覆盖', {
            'fields': ('config_override', 'prompt_template'),
            'classes': ('collapse',)
        }),
        ('状态信息', {
            'fields': ('status', 'total_calls', 'successful_calls', 'total_execution_time', 'last_used', 'last_error', 'config_version'),
            'classes': ('collapse',)
        }),
        ('时间戳', {
            'fields': ('assigned_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )