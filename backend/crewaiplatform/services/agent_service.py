"""
CrewAI Agent服务 - 提供Agent管理和执行功能

主要功能：
- Agent的创建、更新、删除
- Agent执行控制和任务调度
- Agent与工具的绑定管理
- 执行统计和监控
"""

from typing import Dict, List, Tuple, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import CrewAIAgent, User, LLMModel, MCPTool, AgentToolRelation

import logging

logger = logging.getLogger(__name__)


class AgentService:
    """CrewAI Agent管理服务"""
    
    @staticmethod
    def create_agent(data: Dict[str, Any], owner: User) -> Tuple[bool, str, Optional[CrewAIAgent]]:
        """
        创建CrewAI Agent
        
        Args:
            data: Agent配置数据
            owner: Agent所有者
            
        Returns:
            (成功状态, 消息, Agent实例)
        """
        try:
            with transaction.atomic():
                # 设置所有者
                data['owner'] = owner
                
                # 创建Agent实例
                agent = CrewAIAgent(**data)
                agent.full_clean()  # 验证数据
                agent.save()
                
                # 尝试启动Agent
                try:
                    success, message = agent.start()
                    if success:
                        logger.info(f"Agent {agent.name} 创建成功并启动")
                    else:
                        logger.warning(f"Agent {agent.name} 创建成功但启动失败: {message}")
                except Exception as e:
                    logger.warning(f"Agent {agent.name} 创建成功但启动时出错: {str(e)}")
                
                return True, "Agent创建成功", agent
                
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"创建Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_agent(agent_id: int, data: Dict[str, Any], user: User = None) -> Tuple[bool, str, Optional[CrewAIAgent]]:
        """
        更新Agent配置
        
        Args:
            agent_id: Agent ID
            data: 更新数据
            user: 操作用户
            
        Returns:
            (成功状态, 消息, Agent实例)
        """
        try:
            with transaction.atomic():
                agent = CrewAIAgent.objects.get(id=agent_id)
                
                # 权限检查
                if user and not AgentService._can_modify_agent(agent, user):
                    return False, "没有权限修改此Agent", None
                
                # 更新字段
                for field, value in data.items():
                    if hasattr(agent, field) and field != 'owner':  # 防止修改所有者
                        setattr(agent, field, value)
                
                agent.full_clean()  # 验证数据
                agent.save()
                
                logger.info(f"Agent {agent.name} 更新成功")
                return True, "Agent更新成功", agent
                
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在", None
            
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"更新Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def delete_agent(agent_id: int, user: User = None) -> Tuple[bool, str]:
        """
        删除Agent
        
        Args:
            agent_id: Agent ID
            user: 操作用户
            
        Returns:
            (成功状态, 消息)
        """
        try:
            with transaction.atomic():
                agent = CrewAIAgent.objects.get(id=agent_id)
                
                # 权限检查
                if user and not AgentService._can_modify_agent(agent, user):
                    return False, "没有权限删除此Agent", None
                
                # 检查Agent是否在运行中
                if agent.status == 'running':
                    return False, "Agent正在运行中，无法删除"
                
                agent_name = agent.name
                agent.delete()
                
                logger.info(f"Agent {agent_name} 删除成功")
                return True, "Agent删除成功"
                
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在"
            
        except Exception as e:
            error_msg = f"删除Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def start_agent(agent_id: int, user: User = None) -> Tuple[bool, str]:
        """
        启动Agent
        
        Args:
            agent_id: Agent ID
            user: 操作用户
            
        Returns:
            (成功状态, 消息)
        """
        try:
            agent = CrewAIAgent.objects.get(id=agent_id)
            
            # 权限检查
            if user and not AgentService._can_use_agent(agent, user):
                return False, "没有权限使用此Agent"
            
            return agent.start()
            
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在"
            
        except Exception as e:
            error_msg = f"启动Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def stop_agent(agent_id: int, user: User = None) -> Tuple[bool, str]:
        """
        停止Agent
        
        Args:
            agent_id: Agent ID
            user: 操作用户
            
        Returns:
            (成功状态, 消息)
        """
        try:
            agent = CrewAIAgent.objects.get(id=agent_id)
            
            # 权限检查
            if user and not AgentService._can_use_agent(agent, user):
                return False, "没有权限控制此Agent"
            
            return agent.stop()
            
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在"
            
        except Exception as e:
            error_msg = f"停止Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def execute_task(agent_id: int, task_description: str, context: Dict[str, Any] = None, user: User = None) -> Tuple[bool, Any]:
        """
        执行Agent任务
        
        Args:
            agent_id: Agent ID
            task_description: 任务描述
            context: 任务上下文
            user: 操作用户
            
        Returns:
            (成功状态, 执行结果)
        """
        try:
            agent = CrewAIAgent.objects.get(id=agent_id)
            
            # 权限检查
            if user and not AgentService._can_use_agent(agent, user):
                return False, "没有权限使用此Agent"
            
            # 检查Agent状态
            if not agent.is_active:
                return False, "Agent未激活"
            
            if agent.status == 'error':
                return False, f"Agent处于错误状态: {agent.last_error}"
            
            return agent.execute_task(task_description, context)
            
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在"
            
        except Exception as e:
            error_msg = f"执行Agent任务失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def bind_tool(agent_id: int, tool_id: int, config: Dict[str, Any] = None, user: User = None) -> Tuple[bool, str, Optional[AgentToolRelation]]:
        """
        为Agent绑定工具
        
        Args:
            agent_id: Agent ID
            tool_id: 工具ID
            config: 绑定配置
            user: 操作用户
            
        Returns:
            (成功状态, 消息, 关联实例)
        """
        try:
            with transaction.atomic():
                agent = CrewAIAgent.objects.get(id=agent_id)
                tool = MCPTool.objects.get(id=tool_id)
                
                # 权限检查
                if user and not AgentService._can_modify_agent(agent, user):
                    return False, "没有权限修改此Agent", None
                
                # 检查是否已经绑定
                if AgentToolRelation.objects.filter(agent=agent, tool=tool).exists():
                    return False, "Agent已经绑定了此工具", None
                
                # 创建关联
                relation_data = {
                    'agent': agent,
                    'tool': tool,
                    'order': config.get('order', 0) if config else 0,
                    'is_required': config.get('is_required', False) if config else False,
                    'permission_level': config.get('permission_level', 'read') if config else 'read',
                    'config_override': config.get('config_override', {}) if config else {},
                }
                
                if config:
                    for key, value in config.items():
                        if hasattr(AgentToolRelation, key):
                            relation_data[key] = value
                
                relation = AgentToolRelation(**relation_data)
                relation.full_clean()
                relation.save()
                
                logger.info(f"Agent {agent.name} 成功绑定工具 {tool.name}")
                return True, "工具绑定成功", relation
                
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在", None
        except MCPTool.DoesNotExist:
            return False, "工具不存在", None
        except ValidationError as e:
            error_msg = f"绑定配置验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"绑定工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def unbind_tool(agent_id: int, tool_id: int, user: User = None) -> Tuple[bool, str]:
        """
        为Agent解绑工具
        
        Args:
            agent_id: Agent ID
            tool_id: 工具ID
            user: 操作用户
            
        Returns:
            (成功状态, 消息)
        """
        try:
            with transaction.atomic():
                agent = CrewAIAgent.objects.get(id=agent_id)
                
                # 权限检查
                if user and not AgentService._can_modify_agent(agent, user):
                    return False, "没有权限修改此Agent"
                
                relation = AgentToolRelation.objects.get(agent_id=agent_id, tool_id=tool_id)
                
                # 检查是否为必需工具
                if relation.is_required:
                    return False, "无法解绑必需工具"
                
                tool_name = relation.tool.name
                relation.delete()
                
                logger.info(f"Agent {agent.name} 成功解绑工具 {tool_name}")
                return True, "工具解绑成功"
                
        except CrewAIAgent.DoesNotExist:
            return False, "Agent不存在"
        except AgentToolRelation.DoesNotExist:
            return False, "Agent未绑定此工具"
        except Exception as e:
            error_msg = f"解绑工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def get_agent_tools(agent_id: int) -> List[Dict[str, Any]]:
        """
        获取Agent绑定的工具列表
        
        Args:
            agent_id: Agent ID
            
        Returns:
            工具关联列表
        """
        try:
            relations = AgentToolRelation.get_agent_tools(
                CrewAIAgent.objects.get(id=agent_id)
            )
            
            tools_data = []
            for relation in relations:
                tools_data.append({
                    'relation_id': relation.id,
                    'tool_id': relation.tool.id,
                    'tool_name': relation.tool.name,
                    'tool_display_name': relation.tool.display_name,
                    'tool_description': relation.tool.description,
                    'server_type': relation.tool.server_type,
                    'status': relation.status,
                    'order': relation.order,
                    'is_required': relation.is_required,
                    'permission_level': relation.permission_level,
                    'success_rate': relation.get_success_rate(),
                    'last_used': relation.last_used,
                })
            
            return tools_data
            
        except CrewAIAgent.DoesNotExist:
            return []
        except Exception as e:
            logger.error(f"获取Agent工具列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_agents(user: User) -> List[CrewAIAgent]:
        """
        获取用户可用的Agent列表
        
        Args:
            user: 用户实例
            
        Returns:
            Agent列表
        """
        return CrewAIAgent.get_user_agents(user)
    
    @staticmethod
    def get_public_agents() -> List[CrewAIAgent]:
        """
        获取所有公开Agent
        
        Returns:
            公开Agent列表
        """
        return CrewAIAgent.get_public_agents()
    
    @staticmethod
    def get_active_agents() -> List[CrewAIAgent]:
        """
        获取所有活跃Agent
        
        Returns:
            活跃Agent列表
        """
        return CrewAIAgent.get_active_agents()
    
    @staticmethod
    def get_agent_statistics() -> Dict[str, Any]:
        """
        获取Agent统计信息
        
        Returns:
            统计信息字典
        """
        try:
            from django.db.models import Count, Q, Avg, Sum
            
            stats = {
                'total_agents': CrewAIAgent.objects.count(),
                'active_agents': CrewAIAgent.objects.filter(is_active=True).count(),
                'running_agents': CrewAIAgent.objects.filter(status='running').count(),
                'public_agents': CrewAIAgent.objects.filter(is_public=True, is_active=True).count(),
                'total_tasks': CrewAIAgent.objects.aggregate(sum=Sum('total_tasks'))['sum'] or 0,
                'completed_tasks': CrewAIAgent.objects.aggregate(sum=Sum('completed_tasks'))['sum'] or 0,
                'average_success_rate': 0,
                'by_status': {},
                'recent_executions': CrewAIAgent.objects.filter(
                    last_execution__isnull=False
                ).order_by('-last_execution')[:5].values(
                    'id', 'name', 'role', 'status', 'last_execution', 'total_tasks', 'completed_tasks'
                )
            }
            
            # 计算平均成功率
            active_agents = CrewAIAgent.objects.filter(is_active=True, total_tasks__gt=0)
            if active_agents.exists():
                total_success_rate = sum(agent.get_success_rate() for agent in active_agents)
                stats['average_success_rate'] = total_success_rate / active_agents.count()
            
            # 按状态统计
            status_stats = CrewAIAgent.objects.values('status').annotate(
                count=Count('id')
            )
            
            for stat in status_stats:
                stats['by_status'][stat['status']] = stat['count']
            
            return stats
            
        except Exception as e:
            logger.error(f"获取Agent统计信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def _can_modify_agent(agent: CrewAIAgent, user: User) -> bool:
        """检查用户是否可以修改Agent"""
        if user.is_superuser:
            return True
        return agent.owner == user
    
    @staticmethod
    def _can_use_agent(agent: CrewAIAgent, user: User) -> bool:
        """检查用户是否可以使用Agent"""
        if user.is_superuser:
            return True
        if agent.owner == user:
            return True
        if agent.is_public:
            return True
        if user in agent.allowed_users.all():
            return True
        return False
    
    @staticmethod
    def clone_agent(agent_id: int, new_name: str, owner: User) -> Tuple[bool, str, Optional[CrewAIAgent]]:
        """
        克隆Agent
        
        Args:
            agent_id: 源Agent ID
            new_name: 新Agent名称
            owner: 新Agent所有者
            
        Returns:
            (成功状态, 消息, 新Agent实例)
        """
        try:
            with transaction.atomic():
                source_agent = CrewAIAgent.objects.get(id=agent_id)
                
                # 复制Agent配置
                clone_data = {
                    'name': new_name,
                    'display_name': f"{source_agent.display_name} (副本)",
                    'description': source_agent.description,
                    'role': source_agent.role,
                    'goal': source_agent.goal,
                    'backstory': source_agent.backstory,
                    'llm_model': source_agent.llm_model,
                    'function_calling_llm': source_agent.function_calling_llm,
                    'verbose': source_agent.verbose,
                    'memory': source_agent.memory,
                    'max_iter': source_agent.max_iter,
                    'max_rpm': source_agent.max_rpm,
                    'max_execution_time': source_agent.max_execution_time,
                    'max_retry_limit': source_agent.max_retry_limit,
                    'allow_delegation': source_agent.allow_delegation,
                    'respect_context_window': source_agent.respect_context_window,
                    'use_system_prompt': source_agent.use_system_prompt,
                    'multimodal': source_agent.multimodal,
                    'inject_date': source_agent.inject_date,
                    'date_format': source_agent.date_format,
                    'reasoning': source_agent.reasoning,
                    'max_reasoning_attempts': source_agent.max_reasoning_attempts,
                    'step_callback': source_agent.step_callback,
                    'enable_monitoring': source_agent.enable_monitoring,
                    'custom_instructions': source_agent.custom_instructions,
                    'agent_kwargs': source_agent.agent_kwargs,
                    'owner': owner,
                    'is_public': False,  # 克隆的Agent默认为私有
                }
                
                # 创建新Agent
                success, message, new_agent = AgentService.create_agent(clone_data, owner)
                
                if success and new_agent:
                    # 复制工具绑定关系
                    tool_relations = AgentToolRelation.objects.filter(agent=source_agent)
                    for relation in tool_relations:
                        AgentToolRelation.objects.create(
                            agent=new_agent,
                            tool=relation.tool,
                            order=relation.order,
                            is_required=relation.is_required,
                            is_fallback=relation.is_fallback,
                            max_calls_per_task=relation.max_calls_per_task,
                            config_override=relation.config_override,
                            permission_level=relation.permission_level,
                            allowed_operations=relation.allowed_operations,
                            restricted_paths=relation.restricted_paths,
                        )
                    
                    logger.info(f"Agent {source_agent.name} 克隆成功，新Agent: {new_name}")
                    return True, "Agent克隆成功", new_agent
                else:
                    return False, f"克隆Agent失败: {message}", None
                
        except CrewAIAgent.DoesNotExist:
            return False, "源Agent不存在", None
        except Exception as e:
            error_msg = f"克隆Agent失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None