"""
聊天服务

提供聊天会话、消息、Agent任务的业务逻辑处理。
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import ChatConversation, ChatMessage, ChatAgentTask, CrewAIAgent


User = get_user_model()
logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务"""
    
    @staticmethod
    def create_conversation(user: User, title: str = None, description: str = None, 
                          agent_selection_mode: str = 'manual', 
                          primary_agent: CrewAIAgent = None) -> ChatConversation:
        """创建新的聊天会话"""
        
        try:
            with transaction.atomic():
                conversation = ChatConversation.objects.create(
                    user=user,
                    title=title or '新会话',
                    description=description,
                    agent_selection_mode=agent_selection_mode,
                    primary_agent=primary_agent,
                    last_activity_at=timezone.now()
                )
                
                # 创建欢迎消息
                ChatMessage.objects.create(
                    conversation=conversation,
                    role='system',
                    content='欢迎使用CrewAI平台！您可以开始与智能助手对话了。'
                )
                
                logger.info(f"用户 {user.username} 创建了新会话: {conversation.id}")
                return conversation
                
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            raise e
    
    @staticmethod
    def get_user_conversations(user: User, status: str = None) -> List[ChatConversation]:
        """获取用户的会话列表"""
        
        queryset = ChatConversation.objects.filter(user=user)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('primary_agent').order_by('-last_activity_at')
    
    @staticmethod
    def get_conversation_by_id(user: User, conversation_id: int) -> Optional[ChatConversation]:
        """根据ID获取用户的会话"""
        
        try:
            return ChatConversation.objects.select_related('primary_agent').get(
                id=conversation_id,
                user=user
            )
        except ChatConversation.DoesNotExist:
            return None
    
    @staticmethod
    def update_conversation(conversation: ChatConversation, **kwargs) -> ChatConversation:
        """更新会话信息"""
        
        try:
            for field, value in kwargs.items():
                if hasattr(conversation, field):
                    setattr(conversation, field, value)
            
            conversation.save()
            logger.info(f"会话 {conversation.id} 已更新")
            return conversation
            
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            raise e
    
    @staticmethod
    def archive_conversation(conversation: ChatConversation) -> bool:
        """归档会话"""
        
        try:
            conversation.status = 'archived'
            conversation.save(update_fields=['status', 'updated_at'])
            logger.info(f"会话 {conversation.id} 已归档")
            return True
            
        except Exception as e:
            logger.error(f"归档会话失败: {e}")
            return False
    
    @staticmethod
    def delete_conversation(conversation: ChatConversation) -> bool:
        """删除会话"""
        
        try:
            conversation_id = conversation.id
            conversation.delete()
            logger.info(f"会话 {conversation_id} 已删除")
            return True
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False


class ChatMessageService:
    """聊天消息服务"""
    
    @staticmethod
    def create_user_message(conversation: ChatConversation, content: str) -> ChatMessage:
        """创建用户消息"""
        
        try:
            with transaction.atomic():
                message = ChatMessage.objects.create(
                    conversation=conversation,
                    role='user',
                    content=content,
                    status='sent'
                )
                
                # 自动触发消息计数更新（在模型的save方法中处理）
                logger.info(f"用户消息已创建: {message.id}")
                return message
                
        except Exception as e:
            logger.error(f"创建用户消息失败: {e}")
            raise e
    
    @staticmethod
    def create_assistant_message(conversation: ChatConversation, content: str, 
                               agent: CrewAIAgent = None, agent_name: str = None) -> ChatMessage:
        """创建助手消息"""
        
        try:
            message = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=content,
                agent=agent,
                agent_name=agent_name or (agent.name if agent else 'Assistant'),
                status='completed'
            )
            
            logger.info(f"助手消息已创建: {message.id}")
            return message
            
        except Exception as e:
            logger.error(f"创建助手消息失败: {e}")
            raise e
    
    @staticmethod
    def create_system_message(conversation: ChatConversation, content: str) -> ChatMessage:
        """创建系统消息"""
        
        try:
            message = ChatMessage.objects.create(
                conversation=conversation,
                role='system',
                content=content,
                status='sent'
            )
            
            logger.info(f"系统消息已创建: {message.id}")
            return message
            
        except Exception as e:
            logger.error(f"创建系统消息失败: {e}")
            raise e
    
    @staticmethod
    def get_conversation_messages(conversation: ChatConversation, limit: int = None) -> List[ChatMessage]:
        """获取会话的消息列表"""
        
        queryset = ChatMessage.objects.filter(conversation=conversation).order_by('created_at')
        
        if limit:
            queryset = queryset[:limit]
        
        return list(queryset.select_related('agent'))
    
    @staticmethod
    def update_message_status(message: ChatMessage, status: str, error_message: str = None) -> ChatMessage:
        """更新消息状态"""
        
        try:
            message.status = status
            if error_message:
                message.error_message = error_message
            
            message.save(update_fields=['status', 'error_message', 'updated_at'])
            return message
            
        except Exception as e:
            logger.error(f"更新消息状态失败: {e}")
            raise e


class ChatAgentTaskService:
    """Agent任务服务"""
    
    @staticmethod
    def create_agent_task(conversation: ChatConversation, message: ChatMessage,
                         agent: CrewAIAgent, task_description: str) -> ChatAgentTask:
        """创建Agent任务"""
        
        try:
            task = ChatAgentTask.objects.create(
                conversation=conversation,
                message=message,
                agent=agent,
                agent_name=agent.name,
                task_description=task_description,
                status='pending'
            )
            
            logger.info(f"Agent任务已创建: {task.id}")
            return task
            
        except Exception as e:
            logger.error(f"创建Agent任务失败: {e}")
            raise e
    
    @staticmethod
    def get_active_tasks(conversation: ChatConversation = None, 
                        user: User = None) -> List[ChatAgentTask]:
        """获取活跃的任务列表"""
        
        queryset = ChatAgentTask.objects.filter(
            status__in=['pending', 'running']
        ).select_related('agent', 'conversation')
        
        if conversation:
            queryset = queryset.filter(conversation=conversation)
        elif user:
            queryset = queryset.filter(conversation__user=user)
        
        return list(queryset.order_by('-created_at'))
    
    @staticmethod
    def get_task_by_id(task_id: int, user: User = None) -> Optional[ChatAgentTask]:
        """根据ID获取任务"""
        
        try:
            queryset = ChatAgentTask.objects.select_related('agent', 'conversation')
            
            if user:
                queryset = queryset.filter(conversation__user=user)
            
            return queryset.get(id=task_id)
            
        except ChatAgentTask.DoesNotExist:
            return None
    
    @staticmethod
    def start_task_execution(task: ChatAgentTask) -> ChatAgentTask:
        """开始执行任务"""
        
        try:
            task.start_execution()
            logger.info(f"任务 {task.id} 开始执行")
            return task
            
        except Exception as e:
            logger.error(f"启动任务执行失败: {e}")
            raise e
    
    @staticmethod
    def complete_task_execution(task: ChatAgentTask, result: str) -> ChatAgentTask:
        """完成任务执行"""
        
        try:
            task.complete_execution(result)
            logger.info(f"任务 {task.id} 执行完成")
            return task
            
        except Exception as e:
            logger.error(f"完成任务执行失败: {e}")
            raise e
    
    @staticmethod
    def fail_task_execution(task: ChatAgentTask, error_details: str) -> ChatAgentTask:
        """任务执行失败"""
        
        try:
            task.fail_execution(error_details)
            logger.error(f"任务 {task.id} 执行失败: {error_details}")
            return task
            
        except Exception as e:
            logger.error(f"标记任务失败出错: {e}")
            raise e


class ChatStatsService:
    """聊天统计服务"""
    
    @staticmethod
    def get_user_chat_stats(user: User) -> Dict[str, Any]:
        """获取用户聊天统计"""
        
        try:
            conversations = ChatConversation.objects.filter(user=user)
            active_conversations = conversations.filter(status='active')
            messages = ChatMessage.objects.filter(conversation__user=user)
            agent_calls = ChatAgentTask.objects.filter(conversation__user=user)
            
            total_conversations = conversations.count()
            total_messages = messages.count()
            total_agent_calls = agent_calls.count()
            
            # 计算平均消息数
            avg_messages = 0
            if total_conversations > 0:
                avg_messages = total_messages / total_conversations
            
            # 最常使用的Agent
            most_used_agents = (
                agent_calls.values('agent__name')
                .annotate(call_count=Count('id'))
                .order_by('-call_count')[:5]
            )
            
            return {
                'total_conversations': total_conversations,
                'active_conversations': active_conversations.count(),
                'total_messages': total_messages,
                'total_agent_calls': total_agent_calls,
                'avg_messages_per_conversation': round(avg_messages, 2),
                'most_used_agents': list(most_used_agents)
            }
            
        except Exception as e:
            logger.error(f"获取聊天统计失败: {e}")
            return {
                'total_conversations': 0,
                'active_conversations': 0,
                'total_messages': 0,
                'total_agent_calls': 0,
                'avg_messages_per_conversation': 0,
                'most_used_agents': []
            }
    
    @staticmethod
    def get_conversation_stats(conversation: ChatConversation) -> Dict[str, Any]:
        """获取单个会话统计"""
        
        try:
            messages = ChatMessage.objects.filter(conversation=conversation)
            agent_calls = ChatAgentTask.objects.filter(conversation=conversation)
            
            # 计算会话持续时间
            duration_hours = 0
            if conversation.last_activity_at and conversation.created_at:
                duration = conversation.last_activity_at - conversation.created_at
                duration_hours = duration.total_seconds() / 3600
            
            # 最活跃的Agent
            most_active_agent = (
                agent_calls.values('agent__name')
                .annotate(call_count=Count('id'))
                .order_by('-call_count')
                .first()
            )
            
            return {
                'conversation_id': conversation.id,
                'message_count': messages.count(),
                'agent_call_count': agent_calls.count(),
                'duration_hours': round(duration_hours, 2),
                'most_active_agent': most_active_agent['agent__name'] if most_active_agent else None,
                'last_activity': conversation.last_activity_at
            }
            
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
            return {
                'conversation_id': conversation.id,
                'message_count': 0,
                'agent_call_count': 0,
                'duration_hours': 0,
                'most_active_agent': None,
                'last_activity': None
            }