"""
统计数据序列化器

提供各种统计信息的序列化器
"""

from rest_framework import serializers


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