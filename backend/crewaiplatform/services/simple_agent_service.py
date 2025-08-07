"""
简单Agent调用服务

实现基础的单Agent调用功能，为v0.0.1版本提供简单的对话能力。
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from django.conf import settings
from ..models import CrewAIAgent, ChatAgentTask, ChatMessage, LLMModel
from .chat_service import ChatMessageService, ChatAgentTaskService


logger = logging.getLogger(__name__)


class SimpleAgentService:
    """简单Agent服务"""
    
    @staticmethod
    async def process_user_message(user_message: ChatMessage) -> Optional[ChatMessage]:
        """
        处理用户消息，调用Agent生成响应
        
        Args:
            user_message: 用户消息对象
            
        Returns:
            助手响应消息，如果失败返回None
        """
        
        try:
            conversation = user_message.conversation
            
            # 选择要使用的Agent
            agent = SimpleAgentService._select_agent(conversation)
            if not agent:
                # 创建错误消息
                return ChatMessageService.create_system_message(
                    conversation, "抱歉，当前没有可用的Agent，请先配置Agent。"
                )
            
            # 创建Agent任务
            task = ChatAgentTaskService.create_agent_task(
                conversation=conversation,
                message=user_message,
                agent=agent,
                task_description=f"回复用户消息: {user_message.content}"
            )
            
            # 异步执行Agent任务
            asyncio.create_task(SimpleAgentService._execute_agent_task(task))
            
            # 创建处理中的消息
            processing_message = ChatMessageService.create_assistant_message(
                conversation=conversation,
                content="正在思考中...",
                agent=agent,
                agent_name=agent.name
            )
            processing_message.status = 'processing'
            processing_message.save(update_fields=['status'])
            
            return processing_message
            
        except Exception as e:
            logger.error(f"处理用户消息失败: {e}")
            return ChatMessageService.create_system_message(
                user_message.conversation, f"处理消息时发生错误: {str(e)}"
            )
    
    @staticmethod
    def _select_agent(conversation) -> Optional[CrewAIAgent]:
        """选择要使用的Agent"""
        
        # 优先使用会话配置的主要Agent
        if conversation.primary_agent and conversation.primary_agent.is_active:
            return conversation.primary_agent
        
        # 否则选择用户的第一个可用Agent
        available_agents = CrewAIAgent.objects.filter(
            owner=conversation.user,
            is_active=True
        ).order_by('-created_at')
        
        return available_agents.first()
    
    @staticmethod
    async def _execute_agent_task(task: ChatAgentTask):
        """执行Agent任务"""
        
        try:
            # 标记任务开始执行
            ChatAgentTaskService.start_task_execution(task)
            
            # 调用Agent生成响应
            response = await SimpleAgentService._call_agent(
                task.agent, 
                task.task_description,
                task.conversation
            )
            
            # 完成任务
            ChatAgentTaskService.complete_task_execution(task, response)
            
            # 更新对应的助手消息
            await SimpleAgentService._update_assistant_message(task, response)
            
            logger.info(f"Agent任务 {task.id} 执行完成")
            
        except Exception as e:
            # 标记任务失败
            ChatAgentTaskService.fail_task_execution(task, str(e))
            
            # 更新对应的助手消息为错误状态
            await SimpleAgentService._update_assistant_message(
                task, f"抱歉，处理您的请求时遇到了问题: {str(e)}", is_error=True
            )
            
            logger.error(f"Agent任务 {task.id} 执行失败: {e}")
    
    @staticmethod
    async def _call_agent(agent: CrewAIAgent, task_description: str, 
                         conversation) -> str:
        """调用Agent生成响应"""
        
        try:
            # 构建对话上下文
            context = await SimpleAgentService._build_conversation_context(conversation)
            
            # 构建提示词
            prompt = SimpleAgentService._build_agent_prompt(
                agent, task_description, context
            )
            
            # 调用LLM
            response = await SimpleAgentService._call_llm(agent.llm_model, prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"调用Agent失败: {e}")
            raise e
    
    @staticmethod
    async def _build_conversation_context(conversation, max_messages: int = 10) -> str:
        """构建对话上下文"""
        
        try:
            # 获取最近的消息
            recent_messages = ChatMessage.objects.filter(
                conversation=conversation,
                role__in=['user', 'assistant']
            ).order_by('-created_at')[:max_messages]
            
            # 反向排序以保持时间顺序
            recent_messages = list(reversed(recent_messages))
            
            # 构建上下文字符串
            context_parts = []
            for message in recent_messages:
                role = "用户" if message.role == "user" else f"助手({message.agent_name})"
                context_parts.append(f"{role}: {message.content}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"构建对话上下文失败: {e}")
            return ""
    
    @staticmethod
    def _build_agent_prompt(agent: CrewAIAgent, task_description: str, 
                           context: str) -> str:
        """构建Agent提示词"""
        
        prompt_parts = []
        
        # Agent角色设定
        if agent.role:
            prompt_parts.append(f"你是一个{agent.role}。")
        
        # Agent目标
        if agent.goal:
            prompt_parts.append(f"你的目标是: {agent.goal}")
        
        # Agent背景故事
        if agent.backstory:
            prompt_parts.append(f"背景信息: {agent.backstory}")
        
        # 对话上下文
        if context:
            prompt_parts.append(f"\n以下是之前的对话历史:\n{context}")
        
        # 当前任务
        prompt_parts.append(f"\n当前任务: {task_description}")
        
        # 响应要求
        prompt_parts.append(
            "\n请根据你的角色和目标，结合对话历史，为当前任务提供准确、有用的响应。"
            "请保持友好、专业的语气，直接回答问题，不需要重复任务描述。"
        )
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    async def _call_llm(llm_model: LLMModel, prompt: str) -> str:
        """调用LLM生成响应"""
        
        try:
            # 根据不同的LLM提供商调用相应的API
            if llm_model.provider == 'openai':
                return await SimpleAgentService._call_openai_api(llm_model, prompt)
            elif llm_model.provider == 'anthropic':
                return await SimpleAgentService._call_anthropic_api(llm_model, prompt)
            elif llm_model.provider == 'qwen':
                return await SimpleAgentService._call_qwen_api(llm_model, prompt)
            else:
                raise ValueError(f"不支持的LLM提供商: {llm_model.provider}")
                
        except Exception as e:
            logger.error(f"调用LLM失败: {e}")
            raise e
    
    @staticmethod
    async def _call_openai_api(llm_model: LLMModel, prompt: str) -> str:
        """调用OpenAI API"""
        
        import openai
        
        try:
            config = llm_model.config
            
            # 配置OpenAI客户端
            client = openai.AsyncOpenAI(
                api_key=config.get('api_key'),
                base_url=config.get('base_url')
            )
            
            # 调用API
            response = await client.chat.completions.create(
                model=llm_model.model_name,
                messages=[
                    {"role": "system", "content": prompt}
                ],
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 1000),
                timeout=config.get('timeout', 30)
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise e
    
    @staticmethod
    async def _call_anthropic_api(llm_model: LLMModel, prompt: str) -> str:
        """调用Anthropic API"""
        
        try:
            # TODO: 实现Anthropic API调用
            # 这里使用模拟响应
            await asyncio.sleep(1)  # 模拟API调用延迟
            return f"[Anthropic] 基于您的问题，我来为您提供帮助... (模拟响应)"
            
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise e
    
    @staticmethod
    async def _call_qwen_api(llm_model: LLMModel, prompt: str) -> str:
        """调用Qwen API"""
        
        try:
            # Qwen通常兼容OpenAI格式，复用OpenAI调用逻辑
            return await SimpleAgentService._call_openai_api(llm_model, prompt)
            
        except Exception as e:
            logger.error(f"Qwen API调用失败: {e}")
            raise e
    
    @staticmethod
    async def _update_assistant_message(task: ChatAgentTask, content: str, 
                                      is_error: bool = False):
        """更新助手消息内容"""
        
        try:
            # 查找对应的助手消息
            assistant_message = ChatMessage.objects.filter(
                conversation=task.conversation,
                role='assistant',
                agent=task.agent,
                status='processing'
            ).order_by('-created_at').first()
            
            if assistant_message:
                assistant_message.content = content
                assistant_message.status = 'failed' if is_error else 'completed'
                if is_error:
                    assistant_message.error_message = content
                
                assistant_message.save(update_fields=[
                    'content', 'status', 'error_message', 'updated_at'
                ])
                
                logger.info(f"助手消息 {assistant_message.id} 已更新")
            
        except Exception as e:
            logger.error(f"更新助手消息失败: {e}")


class MockAgentService:
    """模拟Agent服务（用于开发测试）"""
    
    @staticmethod
    async def process_user_message(user_message: ChatMessage) -> Optional[ChatMessage]:
        """处理用户消息（模拟版本）"""
        
        try:
            conversation = user_message.conversation
            agent = SimpleAgentService._select_agent(conversation)
            
            if not agent:
                return ChatMessageService.create_system_message(
                    conversation, "抱歉，当前没有可用的Agent。"
                )
            
            # 模拟处理延迟
            await asyncio.sleep(1)
            
            # 生成模拟响应
            mock_responses = [
                f"我理解您说的是: {user_message.content}",
                f"根据我的分析，关于「{user_message.content}」这个问题...",
                f"让我来帮您解答: {user_message.content}",
                "这是一个很好的问题！让我为您详细解释一下。",
                "基于我的专业知识，我建议...",
            ]
            
            import random
            response_content = random.choice(mock_responses)
            
            # 创建助手响应
            return ChatMessageService.create_assistant_message(
                conversation=conversation,
                content=response_content,
                agent=agent,
                agent_name=agent.name
            )
            
        except Exception as e:
            logger.error(f"模拟Agent处理失败: {e}")
            return ChatMessageService.create_system_message(
                user_message.conversation, f"模拟Agent处理错误: {str(e)}"
            )
    
    @staticmethod
    def process_user_message_sync(user_message: ChatMessage) -> Optional[ChatMessage]:
        """处理用户消息（模拟版本-同步）"""
        
        try:
            conversation = user_message.conversation
            agent = SimpleAgentService._select_agent(conversation)
            
            if not agent:
                return ChatMessageService.create_system_message(
                    conversation, "抱歉，当前没有可用的Agent。"
                )
            
            # 生成模拟响应
            mock_responses = [
                f"感谢您的问题！作为{agent.role}，我很高兴为您解答。",
                f"根据我的专业知识，我认为这个问题的答案是...",
                f"让我从{agent.role}的角度来回答您的问题...",
                "这是一个很好的问题！让我为您详细解释一下。",
                "基于我的专业知识，我建议...",
            ]
            
            import random
            response_content = random.choice(mock_responses)
            
            # 创建助手响应
            return ChatMessageService.create_assistant_message(
                conversation=conversation,
                content=response_content,
                agent=agent,
                agent_name=agent.name
            )
            
        except Exception as e:
            logger.error(f"模拟Agent处理失败: {e}")
            return ChatMessageService.create_system_message(
                user_message.conversation, f"模拟Agent处理错误: {str(e)}"
            )