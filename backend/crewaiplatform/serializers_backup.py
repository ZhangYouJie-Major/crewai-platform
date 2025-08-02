from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserRole, RolePermission
from .models import LLMModel, MCPTool, CrewAIAgent, AgentToolRelation
from .models import Dictionary, DictionaryItem

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="密码至少8位字符"
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ("id", "username", "password", "password_confirm", "email", "first_name", "last_name")
        extra_kwargs = {
            'username': {'help_text': '用户名，用于登录'},
            'email': {'help_text': '邮箱地址'},
            'first_name': {'help_text': '名字'},
            'last_name': {'help_text': '姓氏'},
        }

    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_password(self, value):
        """基础密码验证 - 复杂验证已移至前端"""
        if len(value) < 8:
            raise serializers.ValidationError("密码至少需要8位字符")
        return value

    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        attrs.pop('password_confirm')
        return attrs

    def create(self, validated_data):
        """创建新用户"""
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", "full_name",
            "is_active", "is_staff", "is_superuser", "date_joined", "roles", "phone"
        )
        read_only_fields = ("id", "username", "date_joined")

    def get_full_name(self, obj):
        """获取用户全名"""
        return f"{obj.last_name}{obj.first_name}".strip()

    def get_roles(self, obj):
        """获取用户角色列表"""
        roles = Role.objects.filter(userrole__user=obj)
        return RoleSerializer(roles, many=True).data

class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    user_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ("id", "name", "description", "user_count", "permission_count", "permissions", "created_at")
        extra_kwargs = {
            'name': {'help_text': '角色名称'},
            'description': {'help_text': '角色描述'},
        }

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.userrole_set.count()

    def get_permission_count(self, obj):
        """获取该角色拥有的权限数量"""
        return obj.rolepermission_set.count()

    def get_permissions(self, obj):
        """获取角色权限列表"""
        permissions = Permission.objects.filter(rolepermission__role=obj)
        return PermissionSerializer(permissions, many=True).data

    def validate_name(self, value):
        """验证角色名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("角色名称已存在")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    role_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ("id", "name", "codename", "description", "role_count", "created_at")
        extra_kwargs = {
            'name': {'help_text': '权限名称'},
            'codename': {'help_text': '权限代码'},
            'description': {'help_text': '权限描述'},
        }

    def get_role_count(self, obj):
        """获取拥有该权限的角色数量"""
        return obj.rolepermission_set.count()

    def validate_name(self, value):
        """验证权限名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Permission.objects.filter(name=value).exists():
            raise serializers.ValidationError("权限名称已存在")
        return value

    def validate_codename(self, value):
        """验证权限代码唯一性"""
        if self.instance and self.instance.codename == value:
            return value
        if Permission.objects.filter(codename=value).exists():
            raise serializers.ValidationError("权限代码已存在")
        return value

class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色关联序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ("id", "user", "role", "user_username", "role_name", "assigned_at")
        extra_kwargs = {
            'user': {'help_text': '用户ID'},
            'role': {'help_text': '角色ID'},
        }

    def validate(self, attrs):
        """验证用户角色关联的唯一性"""
        user = attrs['user']
        role = attrs['role']
        
        if self.instance is None:
            if UserRole.objects.filter(user=user, role=role).exists():
                raise serializers.ValidationError("用户已拥有该角色")
        
        return attrs

class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限关联序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ("id", "role", "permission", "role_name", "permission_name", "assigned_at")
        extra_kwargs = {
            'role': {'help_text': '角色ID'},
            'permission': {'help_text': '权限ID'},
        }

    def validate(self, attrs):
        """验证角色权限关联的唯一性"""
        role = attrs['role']
        permission = attrs['permission']
        
        if self.instance is None:
            if RolePermission.objects.filter(role=role, permission=permission).exists():
                raise serializers.ValidationError("角色已拥有该权限")
        
        return attrs


# ============================================================================
# CrewAI 集成序列化器
# ============================================================================

class LLMModelSerializer(serializers.ModelSerializer):
    """LLM模型配置序列化器"""
    api_key = serializers.CharField(write_only=True, help_text="API密钥，仅写入时需要")
    is_available_display = serializers.CharField(source='get_is_available_display', read_only=True)
    provider_display = serializers.CharField(source='get_provider_display', read_only=True)
    
    class Meta:
        model = LLMModel
        fields = (
            'id', 'name', 'provider', 'provider_display', 'model_name', 'description',
            'langchain_class', 'api_base_url', 'api_key', 'api_version',
            'temperature', 'max_tokens', 'timeout', 'max_retries',
            'extra_kwargs', 'model_kwargs', 'model_info',
            'last_validated', 'is_available', 'is_available_display', 
            'validation_error', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'model_info', 'last_validated', 'is_available', 
            'validation_error', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'name': {'help_text': 'LLM模型的显示名称'},
            'provider': {'help_text': 'LLM提供商类型'},
            'model_name': {'help_text': 'LangChain中的模型标识'},
            'langchain_class': {'help_text': '对应的LangChain模型类名'},
            'api_base_url': {'help_text': '自定义API端点URL'},
            'temperature': {'help_text': '生成温度参数(0-2)'},
            'max_tokens': {'help_text': '最大token数量'},
            'timeout': {'help_text': 'API超时时间(秒)'},
        }
    
    def validate_name(self, value):
        """验证模型名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if LLMModel.objects.filter(name=value).exists():
            raise serializers.ValidationError("模型名称已存在")
        return value
    
    def validate_temperature(self, value):
        """验证温度参数范围"""
        if not 0.0 <= value <= 2.0:
            raise serializers.ValidationError("温度参数必须在0.0-2.0之间")
        return value
    
    def create(self, validated_data):
        """创建LLM模型配置"""
        return LLMModel.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """更新LLM模型配置"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LLMModelSimpleSerializer(serializers.ModelSerializer):
    """LLM模型简化序列化器，用于下拉选择"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = LLMModel
        fields = ('id', 'name', 'provider', 'model_name', 'display_name', 'is_available')
    
    def get_display_name(self, obj):
        """获取显示名称"""
        return f"{obj.name} ({obj.provider}/{obj.model_name})"


class MCPToolSerializer(serializers.ModelSerializer):
    """MCP工具配置序列化器"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    server_type_display = serializers.CharField(source='get_server_type_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    available_tools = serializers.SerializerMethodField()
    
    class Meta:
        model = MCPTool
        fields = (
            'id', 'name', 'display_name', 'description', 'version',
            'server_type', 'server_type_display', 'connection_config', 'tool_schema',
            'connection_timeout', 'request_timeout', 'max_retries', 'retry_delay',
            'health_check_enabled', 'health_check_interval', 'health_check_method',
            'status', 'status_display', 'last_health_check', 'last_error', 'response_time_ms',
            'total_calls', 'success_calls', 'success_rate', 'available_tools',
            'is_active', 'is_public', 'allowed_users', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'status', 'last_health_check', 'last_error', 'response_time_ms',
            'total_calls', 'success_calls', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'name': {'help_text': 'MCP工具的唯一标识名称'},
            'display_name': {'help_text': '用于界面展示的友好名称'},
            'server_type': {'help_text': 'MCP服务器传输类型'},
            'connection_config': {'help_text': 'MCP服务器连接配置'},
            'tool_schema': {'help_text': '工具的Schema定义'},
        }
    
    def get_success_rate(self, obj):
        """获取成功率"""
        return obj.get_success_rate()
    
    def get_available_tools(self, obj):
        """获取可用工具列表"""
        return obj.get_available_tools()
    
    def validate_name(self, value):
        """验证工具名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if MCPTool.objects.filter(name=value).exists():
            raise serializers.ValidationError("工具名称已存在")
        return value
    
    def validate_connection_config(self, value):
        """验证连接配置"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("连接配置必须是有效的JSON对象")
        return value
    
    def validate_tool_schema(self, value):
        """验证工具Schema"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("工具Schema必须是有效的JSON对象")
        return value


class MCPToolSimpleSerializer(serializers.ModelSerializer):
    """MCP工具简化序列化器，用于下拉选择"""
    display_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MCPTool
        fields = ('id', 'name', 'display_name', 'server_type', 'status', 'display_info')
    
    def get_display_info(self, obj):
        """获取显示信息"""
        return f"{obj.display_name} ({obj.server_type}) - {obj.get_status_display()}"


class CrewAIAgentSerializer(serializers.ModelSerializer):
    """CrewAI Agent配置序列化器"""
    llm_model_info = LLMModelSimpleSerializer(source='llm_model', read_only=True)
    function_calling_llm_info = LLMModelSimpleSerializer(source='function_calling_llm', read_only=True)
    owner_info = serializers.CharField(source='owner.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    avg_execution_time = serializers.SerializerMethodField()
    bound_tools_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CrewAIAgent
        fields = (
            'id', 'name', 'display_name', 'description', 'role', 'goal', 'backstory',
            'llm_model', 'llm_model_info', 'function_calling_llm', 'function_calling_llm_info',
            'verbose', 'memory', 'max_iter', 'max_rpm', 'max_execution_time', 'max_retry_limit',
            'allow_delegation', 'respect_context_window', 'use_system_prompt', 'multimodal',
            'inject_date', 'date_format', 'reasoning', 'max_reasoning_attempts',
            'step_callback', 'enable_monitoring', 'custom_instructions', 'agent_kwargs',
            'status', 'status_display', 'total_tasks', 'completed_tasks', 'success_rate',
            'total_execution_time', 'avg_execution_time', 'last_execution', 'last_error',
            'bound_tools_count', 'is_active', 'is_public', 'owner', 'owner_info', 
            'allowed_users', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'status', 'total_tasks', 'completed_tasks', 'total_execution_time',
            'last_execution', 'last_error', 'owner', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'name': {'help_text': 'Agent的唯一标识名称'},
            'display_name': {'help_text': '用于界面展示的友好名称'},
            'role': {'help_text': 'Agent的角色定义'},
            'goal': {'help_text': 'Agent的主要目标'},
            'backstory': {'help_text': 'Agent的背景故事'},
            'llm_model': {'help_text': '主要使用的LLM模型'},
            'max_iter': {'help_text': '最大迭代次数(1-100)'},
        }
    
    def get_success_rate(self, obj):
        """获取任务成功率"""
        return obj.get_success_rate()
    
    def get_avg_execution_time(self, obj):
        """获取平均执行时间"""
        return obj.get_average_execution_time()
    
    def get_bound_tools_count(self, obj):
        """获取绑定工具数量"""
        return obj.agent_tool_relations.filter(status='active').count()
    
    def validate_name(self, value):
        """验证Agent名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if CrewAIAgent.objects.filter(name=value).exists():
            raise serializers.ValidationError("Agent名称已存在")
        return value
    
    def validate_llm_model(self, value):
        """验证LLM模型可用性"""
        if not value.is_available:
            raise serializers.ValidationError("选择的LLM模型当前不可用")
        return value
    
    def validate_function_calling_llm(self, value):
        """验证工具调用LLM模型可用性"""
        if value and not value.is_available:
            raise serializers.ValidationError("选择的工具调用LLM模型当前不可用")
        return value
    
    def validate_max_iter(self, value):
        """验证最大迭代次数"""
        if not 1 <= value <= 100:
            raise serializers.ValidationError("最大迭代次数必须在1-100之间")
        return value
    
    def create(self, validated_data):
        """创建Agent时设置所有者"""
        validated_data['owner'] = self.context['request'].user
        return CrewAIAgent.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """更新Agent时保护owner字段不被覆盖"""
        # 移除owner字段，防止被意外覆盖
        validated_data.pop('owner', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CrewAIAgentSimpleSerializer(serializers.ModelSerializer):
    """CrewAI Agent简化序列化器，用于下拉选择"""
    display_info = serializers.SerializerMethodField()
    
    class Meta:
        model = CrewAIAgent
        fields = ('id', 'name', 'display_name', 'role', 'status', 'display_info')
    
    def get_display_info(self, obj):
        """获取显示信息"""
        return f"{obj.display_name} ({obj.role}) - {obj.get_status_display()}"


class AgentToolRelationSerializer(serializers.ModelSerializer):
    """Agent-Tool关联序列化器"""
    agent_info = CrewAIAgentSimpleSerializer(source='agent', read_only=True)
    tool_info = MCPToolSimpleSerializer(source='tool', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    permission_level_display = serializers.CharField(source='get_permission_level_display', read_only=True)
    success_rate = serializers.SerializerMethodField()
    avg_execution_time = serializers.SerializerMethodField()
    
    class Meta:
        model = AgentToolRelation
        fields = (
            'id', 'agent', 'agent_info', 'tool', 'tool_info',
            'order', 'is_required', 'is_fallback', 'max_calls_per_task',
            'config_override', 'prompt_template', 'permission_level', 'permission_level_display',
            'allowed_operations', 'restricted_paths', 'status', 'status_display',
            'total_calls', 'successful_calls', 'success_rate', 'total_execution_time',
            'avg_execution_time', 'last_used', 'last_error', 'config_version',
            'assigned_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'status', 'total_calls', 'successful_calls', 'total_execution_time',
            'last_used', 'last_error', 'config_version', 'assigned_at', 'updated_at'
        )
        extra_kwargs = {
            'agent': {'help_text': '关联的Agent'},
            'tool': {'help_text': '关联的MCP工具'},
            'order': {'help_text': '工具使用优先级，数字越小优先级越高'},
            'permission_level': {'help_text': 'Agent对该工具的权限级别'},
            'config_override': {'help_text': '对工具默认配置的覆盖'},
        }
    
    def get_success_rate(self, obj):
        """获取调用成功率"""
        return obj.get_success_rate()
    
    def get_avg_execution_time(self, obj):
        """获取平均执行时间"""
        return obj.get_average_execution_time()
    
    def validate(self, attrs):
        """验证关联的唯一性和状态"""
        agent = attrs['agent']
        tool = attrs['tool']
        
        # 检查唯一性
        if self.instance is None:
            if AgentToolRelation.objects.filter(agent=agent, tool=tool).exists():
                raise serializers.ValidationError("该Agent已绑定此工具")
        
        # 检查Agent和工具状态
        if not agent.is_active:
            raise serializers.ValidationError("不能绑定未激活的Agent")
        
        if not tool.is_active:
            raise serializers.ValidationError("不能绑定未激活的工具")
        
        return attrs
    
    def validate_config_override(self, value):
        """验证配置覆盖格式"""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("配置覆盖必须是有效的JSON对象")
        return value
    
    def validate_allowed_operations(self, value):
        """验证允许的操作列表"""
        if value and not isinstance(value, list):
            raise serializers.ValidationError("允许的操作必须是数组格式")
        return value


class AgentToolBindingSerializer(serializers.Serializer):
    """Agent工具绑定专用序列化器"""
    tool_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="要绑定的工具ID列表"
    )
    permission_level = serializers.ChoiceField(
        choices=AgentToolRelation._meta.get_field('permission_level').choices,
        default='read',
        help_text="权限级别"
    )
    
    def validate_tool_ids(self, value):
        """验证工具ID列表"""
        if not value:
            raise serializers.ValidationError("工具ID列表不能为空")
        
        # 检查工具是否存在且激活
        tools = MCPTool.objects.filter(id__in=value, is_active=True)
        if len(tools) != len(value):
            raise serializers.ValidationError("部分工具不存在或未激活")
        
        return value


# ============================================================================
# 统计和监控序列化器
# ============================================================================

class LLMModelStatsSerializer(serializers.Serializer):
    """LLM模型统计序列化器"""
    total_models = serializers.IntegerField()
    available_models = serializers.IntegerField()
    provider_distribution = serializers.DictField()
    usage_stats = serializers.DictField()


class MCPToolStatsSerializer(serializers.Serializer):
    """MCP工具统计序列化器"""
    total_tools = serializers.IntegerField()
    healthy_tools = serializers.IntegerField()
    server_type_distribution = serializers.DictField()
    usage_stats = serializers.DictField()


class CrewAIAgentStatsSerializer(serializers.Serializer):
    """CrewAI Agent统计序列化器"""
    total_agents = serializers.IntegerField()
    active_agents = serializers.IntegerField()
    task_stats = serializers.DictField()
    performance_stats = serializers.DictField()


# ============================================================================
# 字典管理序列化器
# ============================================================================

class DictionarySerializer(serializers.ModelSerializer):
    """字典类型序列化器"""
    item_count = serializers.SerializerMethodField()
    parent_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = (
            'id', 'code', 'name', 'description', 'is_active', 'sort_order',
            'item_count', 'parent_items', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'code': {'help_text': '字典代码，用于程序识别'},
            'name': {'help_text': '字典名称'},
            'description': {'help_text': '字典描述'},
            'sort_order': {'help_text': '排序顺序，数字越小越靠前'},
        }
    
    def get_item_count(self, obj):
        """获取字典项数量"""
        return obj.items.filter(is_active=True).count()
    
    def get_parent_items(self, obj):
        """获取一级字典项（无父级的项）"""
        parent_items = obj.items.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
        return DictionaryItemSimpleSerializer(parent_items, many=True).data
    
    def validate_code(self, value):
        """验证字典代码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        if Dictionary.objects.filter(code=value).exists():
            raise serializers.ValidationError("字典代码已存在")
        return value
    
    def validate_name(self, value):
        """验证字典名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Dictionary.objects.filter(name=value).exists():
            raise serializers.ValidationError("字典名称已存在")
        return value


class DictionaryItemSerializer(serializers.ModelSerializer):
    """字典项序列化器"""
    dictionary_name = serializers.CharField(source='dictionary.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = (
            'id', 'dictionary', 'dictionary_name', 'parent', 'parent_name',
            'code', 'name', 'value', 'description', 'is_active', 'sort_order',
            'full_path', 'level', 'children_count', 'children',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'dictionary': {'help_text': '所属字典类型'},
            'parent': {'help_text': '父级字典项（用于二级结构）'},
            'code': {'help_text': '字典项代码'},
            'name': {'help_text': '字典项名称'},
            'value': {'help_text': '字典项值（额外信息）'},
            'sort_order': {'help_text': '排序顺序，数字越小越靠前'},
        }
    
    def get_full_path(self, obj):
        """获取完整路径"""
        return obj.get_full_path()
    
    def get_level(self, obj):
        """获取层级深度"""
        return obj.get_level()
    
    def get_children_count(self, obj):
        """获取子级项目数量"""
        return obj.get_children().count()
    
    def get_children(self, obj):
        """获取子级项目列表"""
        children = obj.get_children()
        return DictionaryItemSimpleSerializer(children, many=True).data
    
    def validate(self, attrs):
        """验证字典项数据"""
        dictionary = attrs['dictionary']
        parent = attrs.get('parent')
        code = attrs['code']
        
        # 验证父级字典项是否属于同一字典类型
        if parent and parent.dictionary != dictionary:
            raise serializers.ValidationError("父级字典项必须属于同一字典类型")
        
        # 验证同一字典类型下的代码唯一性
        query = DictionaryItem.objects.filter(dictionary=dictionary, code=code)
        if self.instance:
            query = query.exclude(id=self.instance.id)
        if query.exists():
            raise serializers.ValidationError("该字典类型下已存在相同代码的字典项")
        
        # 防止循环引用
        if parent and self.instance:
            current = parent
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError("不能设置循环引用的父级关系")
                current = current.parent
        
        return attrs
    
    def validate_parent(self, value):
        """验证父级字典项"""
        if value:
            # 确保父级字典项是激活状态
            if not value.is_active:
                raise serializers.ValidationError("父级字典项必须是激活状态")
            
            # 限制层级深度（最多两级）
            if value.parent is not None:
                raise serializers.ValidationError("不支持超过两级的字典结构")
        
        return value


class DictionaryItemSimpleSerializer(serializers.ModelSerializer):
    """字典项简化序列化器，用于下拉选择和树形展示"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = ('id', 'code', 'name', 'sort_order', 'children')
    
    def get_children(self, obj):
        """获取子级项目"""
        children = obj.get_children()
        return DictionaryItemSimpleSerializer(children, many=True).data


class DictionaryItemTreeSerializer(serializers.ModelSerializer):
    """字典项树形结构序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = ('id', 'code', 'name', 'description', 'sort_order', 'is_active', 'children')
    
    def get_children(self, obj):
        """递归获取子级项目"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return DictionaryItemTreeSerializer(children, many=True).data


class DictionaryOptionsSerializer(serializers.Serializer):
    """字典选项序列化器，用于前端下拉选择"""
    dictionary_code = serializers.CharField(help_text="字典代码")
    parent_code = serializers.CharField(required=False, help_text="父级字典项代码（用于获取子级选项）")
    
    def validate_dictionary_code(self, value):
        """验证字典代码存在"""
        if not Dictionary.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("字典类型不存在或未激活")
        return value