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
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def select_agent():
                return SimpleAgentService._select_agent(conversation)
            
            agent = await select_agent()
            if not agent:
                # 创建错误消息 - 使用sync_to_async包装
                @sync_to_async
                def create_error_message():
                    return ChatMessageService.create_system_message(
                        conversation, "抱歉，当前没有可用的Agent，请先配置Agent。"
                    )
                
                return await create_error_message()
            
            # 创建Agent任务 - 使用sync_to_async包装
            @sync_to_async
            def create_task():
                return ChatAgentTaskService.create_agent_task(
                    conversation=conversation,
                    message=user_message,
                    agent=agent,
                    task_description=f"回复用户消息: {user_message.content}"
                )
            
            task = await create_task()
            
            # 对于HTTP API调用，我们直接返回处理中状态
            # 实际的Agent任务处理应该通过WebSocket触发
            # 这里不创建后台任务，避免任务被销毁的警告
            
            # 创建处理中的消息 - 使用sync_to_async包装
            @sync_to_async
            def create_processing_message():
                processing_message = ChatMessageService.create_assistant_message(
                    conversation=conversation,
                    content="正在思考中...",
                    agent=agent,
                    agent_name=agent.name
                )
                processing_message.status = 'processing'
                processing_message.save(update_fields=['status'])
                return processing_message
            
            return await create_processing_message()
            
        except Exception as e:
            logger.error(f"处理用户消息失败: {e}")
            
            # 创建错误消息 - 使用sync_to_async包装
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def create_error_message():
                return ChatMessageService.create_system_message(
                    user_message.conversation, f"处理消息时发生错误: {str(e)}"
                )
            
            return await create_error_message()
    
    @staticmethod
    async def process_user_message_with_websocket(user_message: ChatMessage, websocket_consumer) -> Optional[ChatMessage]:
        """
        通过WebSocket处理用户消息（完整流式功能）
        
        Args:
            user_message: 用户消息对象
            websocket_consumer: WebSocket消费者实例
            
        Returns:
            助手响应消息，如果失败返回None
        """
        
        try:
            conversation = user_message.conversation
            
            # 选择要使用的Agent
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def select_agent():
                return SimpleAgentService._select_agent(conversation)
            
            agent = await select_agent()
            if not agent:
                # 创建错误消息 - 使用sync_to_async包装
                @sync_to_async
                def create_error_message():
                    return ChatMessageService.create_system_message(
                        conversation, "抱歉，当前没有可用的Agent，请先配置Agent。"
                    )
                
                return await create_error_message()
            
            # 创建Agent任务 - 使用sync_to_async包装
            @sync_to_async
            def create_task():
                return ChatAgentTaskService.create_agent_task(
                    conversation=conversation,
                    message=user_message,
                    agent=agent,
                    task_description=f"回复用户消息: {user_message.content}"
                )
            
            task = await create_task()
            
            # 创建处理中的消息 - 使用sync_to_async包装
            @sync_to_async
            def create_processing_message():
                processing_message = ChatMessageService.create_assistant_message(
                    conversation=conversation,
                    content="正在思考中...",
                    agent=agent,
                    agent_name=agent.name
                )
                processing_message.status = 'processing'
                processing_message.save(update_fields=['status'])
                return processing_message
            
            await create_processing_message()
            
            # 直接执行Agent任务，传递websocket_consumer
            await SimpleAgentService._execute_agent_task(task, websocket_consumer)
            
            # 返回最后的助手消息
            @sync_to_async
            def get_latest_assistant_message():
                return ChatMessage.objects.filter(
                    conversation=conversation,
                    role='assistant'
                ).order_by('-created_at').first()
            
            return await get_latest_assistant_message()
            
        except Exception as e:
            logger.error(f"通过WebSocket处理用户消息失败: {e}")
            
            # 创建错误消息 - 使用sync_to_async包装
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def create_error_message():
                return ChatMessageService.create_system_message(
                    user_message.conversation, f"处理消息时发生错误: {str(e)}"
                )
            
            return await create_error_message()
    
    @staticmethod
    def _select_agent(conversation) -> Optional[CrewAIAgent]:
        """选择要使用的Agent"""
        
        # 优先使用会话配置的主要Agent - 预加载llm_model关系
        if conversation.primary_agent and conversation.primary_agent.is_active:
            # 使用select_related预加载llm_model
            return CrewAIAgent.objects.select_related('llm_model').get(pk=conversation.primary_agent.pk)
        
        # 否则选择用户的第一个可用Agent - 预加载llm_model关系
        available_agents = CrewAIAgent.objects.filter(
            owner=conversation.user,
            is_active=True
        ).select_related('llm_model').order_by('-created_at')
        
        return available_agents.first()
    
    @staticmethod
    async def _execute_agent_task(task: ChatAgentTask, websocket_consumer=None):
        """执行Agent任务"""
        
        try:
            # 标记任务开始执行 - 使用sync_to_async包装
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def start_task():
                return ChatAgentTaskService.start_task_execution(task)
            
            await start_task()
            
            # 调用Agent生成响应，传递websocket_consumer
            response = await SimpleAgentService._call_agent(
                task.agent, 
                task.task_description,
                task.conversation,
                websocket_consumer
            )
            
            # 完成任务 - 使用sync_to_async包装
            @sync_to_async
            def complete_task():
                return ChatAgentTaskService.complete_task_execution(task, response)
            
            await complete_task()
            
            # 更新对应的助手消息
            await SimpleAgentService._update_assistant_message(task, response)
            
            logger.info(f"Agent任务 {task.id} 执行完成")
            
        except Exception as e:
            # 标记任务失败 - 使用sync_to_async包装
            from asgiref.sync import sync_to_async
            
            @sync_to_async
            def fail_task():
                return ChatAgentTaskService.fail_task_execution(task, str(e))
            
            await fail_task()
            
            # 更新对应的助手消息为错误状态
            await SimpleAgentService._update_assistant_message(
                task, f"抱歉，处理您的请求时遇到了问题: {str(e)}", is_error=True
            )
            
            logger.error(f"Agent任务 {task.id} 执行失败: {e}")
    
    @staticmethod
    async def _call_agent(agent: CrewAIAgent, task_description: str, 
                         conversation, websocket_consumer=None) -> str:
        """调用Agent生成响应"""
        
        try:
            # 构建对话上下文
            context = await SimpleAgentService._build_conversation_context(conversation)
            
            # 构建提示词
            prompt = SimpleAgentService._build_agent_prompt(
                agent, task_description, context
            )
            
            # 调用LLM，传递websocket_consumer以支持思考过程
            # 从预加载的关系中获取模型信息，避免同步查询
            llm_model_name = getattr(agent.llm_model, 'name', 'unknown') if agent.llm_model else 'unknown'
            llm_model_provider = getattr(agent.llm_model, 'provider', 'unknown') if agent.llm_model else 'unknown'
            
            logger.info(f"准备调用LLM，模型: {llm_model_name}, 提供商: {llm_model_provider}")
            logger.info(f"Prompt长度: {len(prompt)}")
            
            response = await SimpleAgentService._call_llm(
                agent.llm_model, prompt, websocket_consumer
            )
            
            logger.info(f"LLM调用成功，响应长度: {len(response) if response else 0}")
            logger.info(f"响应内容预览: {response[:200] if response else 'None'}...")
            
            return response
            
        except Exception as e:
            logger.error(f"调用Agent失败: {e}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise e
    
    @staticmethod
    async def _build_conversation_context(conversation, max_messages: int = 10) -> str:
        """构建对话上下文"""
        
        from asgiref.sync import sync_to_async
        
        try:
            @sync_to_async
            def get_recent_messages():
                # 获取最近的消息
                recent_messages = ChatMessage.objects.filter(
                    conversation=conversation,
                    role__in=['user', 'assistant']
                ).order_by('-created_at')[:max_messages]
                
                # 反向排序以保持时间顺序
                return list(reversed(recent_messages))
            
            recent_messages = await get_recent_messages()
            
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
    async def _call_llm(llm_model: LLMModel, prompt: str, websocket_consumer=None) -> str:
        """使用LangChain调用LLM生成响应，支持思考过程流式输出"""
        
        try:
            logger.info(f"开始调用LLM: {llm_model.name} ({llm_model.provider})")
            
            # 检查LLM模型是否可用
            if not llm_model.is_available:
                error_msg = f"LLM模型 {llm_model.name} 当前不可用，请检查配置"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"LLM模型可用，准备调用")
            
            # 对于支持思考的模型，使用流式调用
            if llm_model.provider in ['qwen', 'moonshot'] and websocket_consumer:
                logger.info("使用思考过程流式调用")
                return await SimpleAgentService._call_llm_with_thinking(
                    llm_model, prompt, websocket_consumer
                )
            else:
                # 普通调用
                logger.info("使用普通LangChain调用")
                
                # 使用sync_to_async包装create_langchain_model调用
                from asgiref.sync import sync_to_async
                
                @sync_to_async
                def create_model():
                    return llm_model.create_langchain_model()
                
                langchain_model = await create_model()
                logger.info(f"LangChain模型创建成功: {type(langchain_model).__name__}")
                
                from langchain_core.messages import HumanMessage
                message = HumanMessage(content=prompt)
                logger.info("发送消息到LangChain模型")
                
                response = await langchain_model.ainvoke([message])
                logger.info(f"LangChain模型响应成功，内容长度: {len(response.content) if response.content else 0}")
                
                return response.content
            
        except Exception as e:
            logger.error(f"LangChain调用失败: {e}")
            import traceback
            logger.error(f"LangChain调用错误堆栈: {traceback.format_exc()}")
            raise e
    
    @staticmethod
    async def _call_llm_with_thinking(llm_model: LLMModel, prompt: str, websocket_consumer) -> str:
        """调用支持思考过程的LLM模型并流式输出"""
        
        try:
            if llm_model.provider == 'qwen':
                return await SimpleAgentService._call_qwen_with_thinking(
                    llm_model, prompt, websocket_consumer
                )
            elif llm_model.provider == 'moonshot':
                return await SimpleAgentService._call_moonshot_with_thinking(
                    llm_model, prompt, websocket_consumer
                )
            else:
                raise ValueError(f"模型 {llm_model.provider} 不支持思考过程")
                
        except Exception as e:
            logger.error(f"思考过程调用失败: {e}")
            raise e
    
    @staticmethod
    async def _call_qwen_with_thinking(llm_model: LLMModel, prompt: str, websocket_consumer) -> str:
        """调用Qwen模型获取思考过程"""
        
        import openai
        import json
        
        try:
            # 获取API配置
            api_key = llm_model.get_decrypted_api_key()
            base_url = llm_model.api_base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"
            
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # 构建支持思考的消息
            messages = [
                {
                    "role": "system", 
                    "content": "请在回答问题时展示你的思考过程。先思考，然后给出最终答案。"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # 流式调用
            stream = await client.chat.completions.create(
                model=llm_model.model_name,
                messages=messages,
                temperature=llm_model.temperature,
                max_tokens=llm_model.max_tokens or 1000,
                stream=True
            )
            
            full_response = ""
            thinking_content = ""
            answer_content = ""
            is_thinking = True
            
            # 发送思考开始信号
            await websocket_consumer.send_thinking_status(True, "开始思考...")
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # 检测是否从思考转换到答案
                    if "最终答案" in content or "答案是" in content or "总结" in content:
                        if is_thinking:
                            is_thinking = False
                            # 发送思考完成
                            await websocket_consumer.send_thinking_complete(thinking_content)
                            # 开始流式输出答案
                            await websocket_consumer.send_answer_stream_start()
                    
                    if is_thinking:
                        thinking_content += content
                        # 发送思考过程更新
                        await websocket_consumer.send_thinking_update(thinking_content)
                    else:
                        answer_content += content
                        # 发送答案流式更新
                        await websocket_consumer.send_answer_stream_update(content)
            
            # 发送流式完成
            await websocket_consumer.send_answer_stream_complete(answer_content)
            
            return answer_content if answer_content else full_response
            
        except Exception as e:
            logger.error(f"Qwen思考过程调用失败: {e}")
            await websocket_consumer.send_thinking_status(False, f"思考失败: {str(e)}")
            raise e
    
    @staticmethod
    async def _call_moonshot_with_thinking(llm_model: LLMModel, prompt: str, websocket_consumer) -> str:
        """调用Moonshot(Kimi)模型获取思考过程"""
        
        import openai
        
        try:
            # 获取API配置
            api_key = llm_model.get_decrypted_api_key()
            base_url = llm_model.api_base_url or "https://api.moonshot.cn/v1"
            
            client = openai.AsyncOpenAI(
                api_key=api_key,
                base_url=base_url
            )
            
            # 构建支持思考的消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个善于思考的AI助手。请在回答问题时，先展示你的思考过程，然后给出最终答案。思考过程用<thinking>标签包围，最终答案用<answer>标签包围。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # 流式调用
            stream = await client.chat.completions.create(
                model=llm_model.model_name,
                messages=messages,
                temperature=llm_model.temperature,
                max_tokens=llm_model.max_tokens or 1000,
                stream=True
            )
            
            full_response = ""
            thinking_content = ""
            answer_content = ""
            current_mode = "thinking"  # thinking, answer, normal
            
            # 发送思考开始信号
            await websocket_consumer.send_thinking_status(True, "Kimi正在思考...")
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    
                    # 解析标签
                    if "<thinking>" in content:
                        current_mode = "thinking"
                        content = content.replace("<thinking>", "")
                    elif "</thinking>" in content:
                        content = content.replace("</thinking>", "")
                        await websocket_consumer.send_thinking_complete(thinking_content)
                        current_mode = "answer"
                        await websocket_consumer.send_answer_stream_start()
                    elif "<answer>" in content:
                        current_mode = "answer"
                        content = content.replace("<answer>", "")
                        await websocket_consumer.send_answer_stream_start()
                    elif "</answer>" in content:
                        content = content.replace("</answer>", "")
                        if content.strip():
                            answer_content += content
                            await websocket_consumer.send_answer_stream_update(content)
                        break
                    
                    if current_mode == "thinking":
                        thinking_content += content
                        await websocket_consumer.send_thinking_update(thinking_content)
                    elif current_mode == "answer":
                        answer_content += content
                        await websocket_consumer.send_answer_stream_update(content)
            
            # 发送流式完成
            await websocket_consumer.send_answer_stream_complete(answer_content)
            
            return answer_content if answer_content else full_response
            
        except Exception as e:
            logger.error(f"Moonshot思考过程调用失败: {e}")
            await websocket_consumer.send_thinking_status(False, f"思考失败: {str(e)}")
            raise e
    
    @staticmethod
    async def _generate_test_response(llm_model: LLMModel, prompt: str) -> str:
        """生成智能的测试响应"""
        
        import asyncio
        import random
        
        # 模拟处理时间
        await asyncio.sleep(random.uniform(1, 3))
        
        # 解析prompt中的问题内容
        lines = prompt.split('\n')
        user_question = ""
        for line in lines:
            if '当前任务:' in line:
                user_question = line.replace('当前任务:', '').strip()
                break
        
        if not user_question:
            user_question = "您的问题"
        
        # 根据问题类型生成不同的响应
        responses = []
        
        if any(keyword in user_question.lower() for keyword in ['美食', '吃', '菜', '餐厅', '食物']):
            responses = [
                f"关于美食推荐，我建议您可以尝试一些当地特色菜品。比如川菜的麻婆豆腐，粤菜的白切鸡，或者淮扬菜的蟹粉狮子头都是不错的选择。",
                f"根据您提到的美食需求，我推荐几道经典菜品：红烧肉、糖醋里脊、宫保鸡丁。这些都是老少皆宜的家常菜。",
                f"对于美食选择，建议您考虑营养搭配：主食、蛋白质、维生素缺一不可。可以试试蒸蛋羹配青菜，营养又美味。"
            ]
        elif any(keyword in user_question.lower() for keyword in ['天气', '温度', '下雨', '晴天']):
            responses = [
                f"关于天气信息，建议您查看当地天气预报获取最准确的信息。记得根据天气变化适当增减衣物哦！",
                f"天气变化多端，建议您随身携带雨具，并关注气温变化及时调整着装。",
            ]
        elif any(keyword in user_question.lower() for keyword in ['学习', '知识', '技能', '教程']):
            responses = [
                f"关于学习建议，我认为循序渐进很重要。建议您制定学习计划，每天坚持一点点进步。",
                f"学习新技能确实需要时间和耐心。建议您找到适合的学习资源，多实践多思考。",
            ]
        else:
            # 通用响应
            responses = [
                f"您提出了一个很有意思的问题。基于我的理解，这个问题涉及多个方面，我建议您可以从以下角度来思考...",
                f"这是一个值得深入探讨的话题。让我为您分析一下相关的要点和可能的解决方案。",
                f"感谢您的提问！根据我的分析，我认为这个问题的关键在于理解核心需求，然后制定相应的策略。",
                f"您的问题很实际，我建议采用循序渐进的方法来解决。首先明确目标，然后制定可行的行动计划。"
            ]
        
        return random.choice(responses)
    
    @staticmethod
    async def _fallback_llm_call(llm_model: LLMModel, prompt: str) -> str:
        """降级LLM调用（如果LangChain失败）"""
        
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
            logger.error(f"降级调用失败: {e}")
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
        
        from asgiref.sync import sync_to_async
        
        try:
            # 使用sync_to_async包装数据库操作
            @sync_to_async
            def get_assistant_message():
                return ChatMessage.objects.filter(
                    conversation=task.conversation,
                    role='assistant',
                    agent=task.agent,
                    status='processing'
                ).order_by('-created_at').first()
            
            @sync_to_async
            def update_message(message, new_content, error_status, error_msg=None):
                message.content = new_content
                message.status = 'failed' if error_status else 'completed'
                if error_status:
                    message.error_message = error_msg or new_content
                
                message.save(update_fields=[
                    'content', 'status', 'error_message', 'updated_at'
                ])
                return message.id
            
            # 查找对应的助手消息
            assistant_message = await get_assistant_message()
            
            if assistant_message:
                message_id = await update_message(assistant_message, content, is_error, 
                                                content if is_error else None)
                logger.info(f"助手消息 {message_id} 已更新")
            else:
                logger.warning(f"未找到待更新的助手消息，任务ID: {task.id}")
            
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