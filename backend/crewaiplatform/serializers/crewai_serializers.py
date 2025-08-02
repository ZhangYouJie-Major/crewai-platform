"""
CrewAI相关序列化器

提供LLM模型、MCP工具、CrewAI Agent、Agent工具关联的序列化器
"""

from rest_framework import serializers
from ..models import LLMModel, MCPTool, CrewAIAgent, AgentToolRelation


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
            'description': {'help_text': '工具功能描述'},
            'server_type': {'help_text': 'MCP服务器类型'},
            'connection_config': {'help_text': '连接配置信息'},
            'tool_schema': {'help_text': '工具架构定义'},
        }
    
    def get_success_rate(self, obj):
        """获取成功率"""
        if obj.total_calls == 0:
            return 0.0
        return (obj.success_calls / obj.total_calls) * 100
    
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


class MCPToolSimpleSerializer(serializers.ModelSerializer):
    """MCP工具简化序列化器，用于下拉选择"""
    display_info = serializers.SerializerMethodField()
    
    class Meta:
        model = MCPTool
        fields = ('id', 'name', 'display_name', 'status', 'display_info')
    
    def get_display_info(self, obj):
        """获取显示信息"""
        return f"{obj.display_name} ({obj.name}) - {obj.get_status_display()}"


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
    
    def validate(self, attrs):
        """验证Agent数据"""
        # 验证LLM模型可用性（业务逻辑错误）
        llm_model = attrs.get('llm_model')
        if llm_model and not llm_model.is_available:
            raise serializers.ValidationError({
                'non_field_errors': ['选择的主要LLM模型当前不可用，请选择其他模型']
            })
        
        function_calling_llm = attrs.get('function_calling_llm')
        if function_calling_llm and not function_calling_llm.is_available:
            raise serializers.ValidationError({
                'non_field_errors': ['选择的工具调用LLM模型当前不可用，请选择其他模型']
            })
            
        return attrs
    
    def validate_llm_model(self, value):
        """验证LLM模型存在性（字段验证）"""
        # 这里只做基本的存在性检查，可用性检查在validate方法中
        return value
    
    def validate_function_calling_llm(self, value):
        """验证工具调用LLM模型存在性（字段验证）"""
        # 这里只做基本的存在性检查，可用性检查在validate方法中
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
        """获取成功率"""
        if obj.total_calls == 0:
            return 0.0
        return (obj.successful_calls / obj.total_calls) * 100
    
    def get_avg_execution_time(self, obj):
        """获取平均执行时间"""
        if obj.successful_calls == 0:
            return 0.0
        return obj.total_execution_time / obj.successful_calls
    
    def validate(self, attrs):
        """验证Agent-Tool关联的唯一性"""
        agent = attrs['agent']
        tool = attrs['tool']
        
        if self.instance is None:
            if AgentToolRelation.objects.filter(agent=agent, tool=tool).exists():
                raise serializers.ValidationError("该Agent已绑定此工具")
        
        return attrs


class AgentToolBindingSerializer(serializers.Serializer):
    """Agent工具绑定批量操作序列化器"""
    agent_id = serializers.IntegerField(help_text="Agent ID")
    tool_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="工具ID列表"
    )
    config_override = serializers.JSONField(
        required=False,
        help_text="配置覆盖"
    )
    permission_level = serializers.ChoiceField(
        choices=AgentToolRelation.PERMISSION_LEVEL_CHOICES,
        default='read',
        help_text="权限级别"
    )
    
    def validate_agent_id(self, value):
        """验证Agent存在性"""
        try:
            CrewAIAgent.objects.get(id=value)
        except CrewAIAgent.DoesNotExist:
            raise serializers.ValidationError("指定的Agent不存在")
        return value
    
    def validate_tool_ids(self, value):
        """验证工具存在性"""
        existing_tools = MCPTool.objects.filter(id__in=value).values_list('id', flat=True)
        missing_tools = set(value) - set(existing_tools)
        if missing_tools:
            raise serializers.ValidationError(f"以下工具不存在: {list(missing_tools)}")
        return value