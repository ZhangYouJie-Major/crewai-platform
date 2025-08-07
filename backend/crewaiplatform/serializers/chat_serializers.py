"""
聊天功能相关序列化器

用于处理聊天会话、消息、Agent任务的序列化和反序列化。
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import ChatConversation, ChatMessage, ChatAgentTask, CrewAIAgent


User = get_user_model()


class ChatConversationSerializer(serializers.ModelSerializer):
    """聊天会话序列化器"""
    
    primary_agent_name = serializers.SerializerMethodField(read_only=True)
    latest_message = serializers.SerializerMethodField(read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatConversation
        fields = [
            'id', 'title', 'description', 'user', 'user_username',
            'agent_selection_mode', 'primary_agent', 'primary_agent_name',
            'total_messages', 'total_agent_calls', 'status', 'latest_message',
            'last_activity_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_username', 'total_messages', 'total_agent_calls',
            'last_activity_at', 'created_at', 'updated_at'
        ]
    
    def get_primary_agent_name(self, obj):
        """获取主要Agent名称"""
        if obj.primary_agent:
            return obj.primary_agent.name
        return None
    
    def get_latest_message(self, obj):
        """获取最新消息"""
        latest = obj.latest_message
        if latest:
            return {
                'id': latest.id,
                'content': latest.content[:100] + '...' if len(latest.content) > 100 else latest.content,
                'role': latest.role,
                'created_at': latest.created_at
            }
        return None
    
    def validate_primary_agent(self, value):
        """验证主要Agent"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("只能选择自己创建的Agent")
        return value


class ChatConversationCreateSerializer(serializers.ModelSerializer):
    """创建聊天会话序列化器"""
    
    class Meta:
        model = ChatConversation
        fields = [
            'title', 'description', 'agent_selection_mode', 'primary_agent'
        ]
    
    def validate_primary_agent(self, value):
        """验证主要Agent"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("只能选择自己创建的Agent")
        return value
    
    def create(self, validated_data):
        """创建会话"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ChatMessageSerializer(serializers.ModelSerializer):
    """聊天消息序列化器"""
    
    agent_name = serializers.CharField(read_only=True)
    conversation_title = serializers.CharField(source='conversation.title', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'conversation', 'conversation_title', 'role', 'content',
            'agent', 'agent_name', 'status', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'conversation_title', 'agent_name', 'status', 'error_message',
            'created_at', 'updated_at'
        ]


class ChatMessageCreateSerializer(serializers.ModelSerializer):
    """创建聊天消息序列化器"""
    
    class Meta:
        model = ChatMessage
        fields = ['content']
    
    def validate_content(self, value):
        """验证消息内容"""
        if not value or not value.strip():
            raise serializers.ValidationError("消息内容不能为空")
        
        if len(value.strip()) > 10000:
            raise serializers.ValidationError("消息内容不能超过10000字符")
        
        return value.strip()
    
    def create(self, validated_data):
        """创建消息"""
        # 从context获取会话
        conversation = self.context['conversation']
        validated_data['conversation'] = conversation
        validated_data['role'] = 'user'  # 用户消息
        
        return super().create(validated_data)


class ChatAgentTaskSerializer(serializers.ModelSerializer):
    """Agent任务序列化器"""
    
    agent_name = serializers.CharField(read_only=True)
    conversation_title = serializers.CharField(source='conversation.title', read_only=True)
    execution_duration = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = ChatAgentTask
        fields = [
            'id', 'conversation', 'conversation_title', 'message',
            'task_description', 'agent', 'agent_name', 'status',
            'start_time', 'end_time', 'execution_time_ms', 'execution_duration',
            'result', 'error_details', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'conversation_title', 'agent_name', 'execution_duration',
            'created_at', 'updated_at'
        ]
    
    def get_execution_duration(self, obj):
        """获取执行时长描述"""
        if obj.execution_time_ms:
            if obj.execution_time_ms < 1000:
                return f"{obj.execution_time_ms}ms"
            elif obj.execution_time_ms < 60000:
                return f"{obj.execution_time_ms / 1000:.1f}s"
            else:
                minutes = obj.execution_time_ms // 60000
                seconds = (obj.execution_time_ms % 60000) // 1000
                return f"{minutes}m{seconds}s"
        return None


class AgentSimpleSerializer(serializers.ModelSerializer):
    """Agent简单序列化器（用于选择列表）"""
    
    tools_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = CrewAIAgent
        fields = [
            'id', 'name', 'role', 'goal', 'is_active', 'tools_count', 'created_at'
        ]
        read_only_fields = ['id', 'tools_count', 'created_at']
    
    def get_tools_count(self, obj):
        """获取工具数量"""
        return obj.agent_tool_relations.filter(status='active').count()


class ChatStatsSerializer(serializers.Serializer):
    """聊天统计序列化器"""
    
    total_conversations = serializers.IntegerField(read_only=True)
    active_conversations = serializers.IntegerField(read_only=True)
    total_messages = serializers.IntegerField(read_only=True)
    total_agent_calls = serializers.IntegerField(read_only=True)
    avg_messages_per_conversation = serializers.FloatField(read_only=True)
    most_used_agents = serializers.ListField(read_only=True)


class ConversationStatsSerializer(serializers.Serializer):
    """会话统计序列化器"""
    
    conversation_id = serializers.IntegerField()
    message_count = serializers.IntegerField()
    agent_call_count = serializers.IntegerField()
    duration_hours = serializers.FloatField()
    most_active_agent = serializers.CharField()
    last_activity = serializers.DateTimeField()