#!/usr/bin/env python3
"""
LLM/Agent/Tool ORM 查询调试专用测试
点击方法即可运行，便于调试SQL/ORM逻辑
"""

import os
import sys

# 添加Django项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewaiplatform.settings')

import django
django.setup()

from crewaiplatform.models.llm_model import LLMModel
from crewaiplatform.models.crewai_agent import CrewAIAgent
from crewaiplatform.models.mcp_tool import MCPTool
from crewaiplatform.models.agent_tool_relation import AgentToolRelation


def query_all_available_llms():
    print("\n【查询所有可用LLM】")
    for llm in LLMModel.objects.filter(is_active=True, is_available=True):
        print(f"id={llm.id}, name={llm.name}, provider={llm.provider}, model_name={llm.model_name}")

def query_active_agents_with_llm():
    print("\n【查询所有活跃Agent及其关联LLM】")
    agents = CrewAIAgent.objects.filter(is_active=True, status__in=['active', 'running']).select_related('llm_model')
    for agent in agents:
        print(f"id={agent.id}, name={agent.name}, llm={agent.llm_model.name if agent.llm_model else None}")

def query_healthy_tools():
    print("\n【查询所有健康Tool】")
    for tool in MCPTool.objects.filter(is_active=True, status='healthy'):
        print(f"id={tool.id}, name={tool.name}, status={tool.status}, server_type={tool.server_type}")

def query_agent_tools(agent_id):
    print(f"\n【查询Agent({agent_id})绑定的所有Tool】")
    relations = AgentToolRelation.objects.filter(agent_id=agent_id, status='active').select_related('tool').order_by('order')
    for rel in relations:
        print(f"tool_id={rel.tool.id}, tool_name={rel.tool.name}, order={rel.order}, tool_status={rel.tool.status}")

def query_high_usage_relations(min_calls=100):
    print(f"\n【查询高频使用的Agent-Tool关联（调用次数>={min_calls}）】")
    for rel in AgentToolRelation.objects.filter(total_calls__gte=min_calls, status='active').order_by('-total_calls'):
        print(f"agent={rel.agent.name}, tool={rel.tool.name}, total_calls={rel.total_calls}")

def query_agent_tool_mapping():
    # 预取相关 LLMModel，避免 N+1 查询
    agents = CrewAIAgent.objects.filter(is_active=True).select_related('llm_model').all()
    # 预取所有 agent 的工具关系和工具
    agent_ids = [agent.id for agent in agents]
    agent_tools = AgentToolRelation.objects.filter(
        agent_id__in=agent_ids, status='active'
    ).select_related('tool').order_by('order')

    # 构建 agent_id 到 tools 的映射
    from collections import defaultdict
    agent_tools_map = defaultdict(list)
    for at in agent_tools:
        agent_tools_map[at.agent_id].append(at)

    for agent in agents:
        llm = getattr(agent, 'llm_model', None)
        tools = agent_tools_map.get(agent.id, [])
        print(f"agent={agent}, llm={llm}, tools={tools}")

if __name__ == "__main__":
    # 你可以注释/取消注释下列方法，点击运行
    query_agent_tool_mapping()
    # query_active_agents_with_llm()
    # query_healthy_tools()
    # query_agent_tools(agent_id=1)  # 修改为实际agent_id
    # query_high_usage_relations(min_calls=100)