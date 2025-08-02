"""
CrewAI Agent配置 - 基于CrewAI框架的智能代理管理

CrewAI Agent是执行特定任务的智能代理，具有以下特性：
- 明确的角色定义和目标
- 背景故事增强人格化
- 灵活的LLM模型选择
- 丰富的工具集成能力
- 完整的执行控制参数
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .llm_model import LLMModel
import json


class CrewAIAgent(models.Model):
    """
    CrewAI Agent配置表
    管理智能代理的完整配置参数和执行控制
    """
    
    # Agent状态
    STATUS_CHOICES = [
        ('inactive', '未激活'),
        ('active', '激活'),
        ('running', '运行中'),
        ('paused', '暂停'),
        ('error', '错误'),
    ]
    
    # 基本信息
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Agent名称",
        help_text="Agent的唯一标识名称"
    )
    
    display_name = models.CharField(
        max_length=128,
        verbose_name="显示名称",
        help_text="用于界面展示的友好名称"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="Agent描述",
        help_text="Agent的功能描述和使用说明"
    )
    
    # CrewAI核心配置
    role = models.CharField(
        max_length=128,
        verbose_name="角色",
        help_text="Agent的角色定义，如'数据分析师'、'文档编写员'等"
    )
    
    goal = models.TextField(
        verbose_name="目标",
        help_text="Agent的主要目标和职责描述"
    )
    
    backstory = models.TextField(
        verbose_name="背景故事",
        help_text="Agent的背景故事，增强其人格化特征"
    )
    
    # LLM模型配置
    llm_model = models.ForeignKey(
        LLMModel,
        on_delete=models.PROTECT,
        related_name='primary_agents',
        verbose_name="主要LLM模型",
        help_text="Agent使用的主要语言模型"
    )
    
    function_calling_llm = models.ForeignKey(
        LLMModel,
        on_delete=models.PROTECT,
        related_name='function_calling_agents',
        blank=True,
        null=True,
        verbose_name="工具调用LLM",
        help_text="专门用于工具调用的语言模型，可与主模型不同"
    )
    
    # 执行控制参数
    verbose = models.BooleanField(
        default=False,
        verbose_name="详细日志",
        help_text="是否启用详细的执行日志输出"
    )
    
    memory = models.BooleanField(
        default=False,
        verbose_name="启用记忆",
        help_text="是否启用Agent的长期记忆功能"
    )
    
    max_iter = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="最大迭代次数",
        help_text="Agent执行任务时的最大迭代次数"
    )
    
    max_rpm = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name="每分钟最大请求数",
        help_text="限制Agent每分钟的API请求次数"
    )
    
    max_execution_time = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name="最大执行时间",
        help_text="单个任务的最大执行时间（秒）"
    )
    
    max_retry_limit = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="最大重试次数",
        help_text="任务失败时的最大重试次数"
    )
    
    # 高级功能配置
    allow_delegation = models.BooleanField(
        default=False,
        verbose_name="允许委托",
        help_text="是否允许Agent将任务委托给其他Agent"
    )
    
    respect_context_window = models.BooleanField(
        default=True,
        verbose_name="遵循上下文窗口",
        help_text="是否遵循LLM模型的上下文窗口限制"
    )
    
    use_system_prompt = models.BooleanField(
        default=True,
        verbose_name="使用系统提示",
        help_text="是否使用CrewAI的默认系统提示"
    )
    
    multimodal = models.BooleanField(
        default=False,
        verbose_name="多模态支持",
        help_text="是否启用多模态输入处理（图像、音频等）"
    )
    
    # 时间和日期配置
    inject_date = models.BooleanField(
        default=False,
        verbose_name="注入日期",
        help_text="是否在提示中自动注入当前日期时间"
    )
    
    date_format = models.CharField(
        max_length=32,
        default='%Y-%m-%d %H:%M:%S',
        verbose_name="日期格式",
        help_text="注入日期时使用的格式字符串"
    )
    
    # 推理功能配置
    reasoning = models.BooleanField(
        default=False,
        verbose_name="启用推理",
        help_text="是否启用Agent的推理思考功能"
    )
    
    max_reasoning_attempts = models.IntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name="最大推理尝试次数",
        help_text="推理功能的最大尝试次数"
    )
    
    # 回调和监控
    step_callback = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="步骤回调",
        help_text="每个执行步骤的回调函数名称"
    )
    
    enable_monitoring = models.BooleanField(
        default=True,
        verbose_name="启用监控",
        help_text="是否启用Agent执行过程的监控"
    )
    
    # 自定义配置
    custom_instructions = models.TextField(
        blank=True,
        verbose_name="自定义指令",
        help_text="附加的自定义指令和提示"
    )
    
    agent_kwargs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Agent参数",
        help_text="传递给CrewAI Agent的其他参数"
    )
    
    # 状态和统计
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='inactive',
        verbose_name="状态",
        help_text="Agent的当前运行状态"
    )
    
    total_tasks = models.IntegerField(
        default=0,
        verbose_name="总任务数",
        help_text="Agent处理的总任务数量"
    )
    
    completed_tasks = models.IntegerField(
        default=0,
        verbose_name="完成任务数",
        help_text="Agent成功完成的任务数量"
    )
    
    total_execution_time = models.IntegerField(
        default=0,
        verbose_name="总执行时间",
        help_text="Agent的累计执行时间（秒）"
    )
    
    last_execution = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="最后执行时间",
        help_text="Agent最后一次执行任务的时间"
    )
    
    last_error = models.TextField(
        blank=True,
        verbose_name="最后错误",
        help_text="最后一次执行错误的详细信息"
    )
    
    # 权限和访问控制
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="是否在系统中启用此Agent"
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name="是否公开",
        help_text="是否允许所有用户使用此Agent"
    )
    
    owner = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='owned_agents',
        verbose_name="所有者",
        help_text="Agent的创建者和所有者"
    )
    
    allowed_users = models.ManyToManyField(
        'User',
        blank=True,
        related_name='shared_agents',
        verbose_name="允许使用的用户",
        help_text="允许使用此Agent的用户列表"
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        db_table = 'crewai_agent'
        verbose_name = 'CrewAI Agent配置'
        verbose_name_plural = 'CrewAI Agent配置'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_public']),
            models.Index(fields=['owner']),
            models.Index(fields=['llm_model']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.role})"
    
    def clean(self):
        """验证配置数据"""
        super().clean()
        
        # 验证LLM模型可用性
        if self.llm_model and not self.llm_model.is_available:
            raise ValidationError("选择的主要LLM模型当前不可用")
        
        if self.function_calling_llm and not self.function_calling_llm.is_available:
            raise ValidationError("选择的工具调用LLM模型当前不可用")
        
        # 验证日期格式
        if self.inject_date and self.date_format:
            try:
                from datetime import datetime
                datetime.now().strftime(self.date_format)
            except ValueError:
                raise ValidationError("日期格式字符串无效")
    
    def get_success_rate(self):
        """获取任务成功率"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    def get_average_execution_time(self):
        """获取平均执行时间"""
        if self.completed_tasks == 0:
            return 0.0
        return self.total_execution_time / self.completed_tasks
    
    def get_crewai_config(self):
        """获取CrewAI Agent配置"""
        config = {
            'role': self.role,
            'goal': self.goal,
            'backstory': self.backstory,
            'verbose': self.verbose,
            'memory': self.memory,
            'max_iter': self.max_iter,
            'max_retry_limit': self.max_retry_limit,
            'allow_delegation': self.allow_delegation,
            'respect_context_window': self.respect_context_window,
            'use_system_prompt': self.use_system_prompt,
            'multimodal': self.multimodal,
            'reasoning': self.reasoning,
        }
        
        # 添加可选参数
        if self.max_rpm:
            config['max_rpm'] = self.max_rpm
        
        if self.max_execution_time:
            config['max_execution_time'] = self.max_execution_time
        
        if self.max_reasoning_attempts:
            config['max_reasoning_attempts'] = self.max_reasoning_attempts
        
        if self.inject_date:
            config['inject_date'] = True
            if self.date_format:
                config['date_format'] = self.date_format
        
        if self.step_callback:
            config['step_callback'] = self.step_callback
        
        if self.custom_instructions:
            config['custom_instructions'] = self.custom_instructions
        
        # 合并自定义参数
        config.update(self.agent_kwargs)
        
        return config
    
    def create_crewai_agent(self):
        """创建CrewAI Agent实例"""
        try:
            from crewai import Agent
            
            # 获取配置
            config = self.get_crewai_config()
            
            # 创建LLM实例
            llm = self.llm_model.create_langchain_model()
            config['llm'] = llm
            
            # 如果有专门的工具调用LLM
            if self.function_calling_llm:
                function_calling_llm = self.function_calling_llm.create_langchain_model()
                config['function_calling_llm'] = function_calling_llm
            
            # 获取绑定的工具
            tools = self.get_bound_tools()
            if tools:
                config['tools'] = tools
            
            # 创建Agent
            agent = Agent(**config)
            
            return agent
            
        except Exception as e:
            raise ValueError(f"创建CrewAI Agent失败: {str(e)}")
    
    def get_bound_tools(self):
        """获取绑定的工具列表"""
        tools = []
        
        # 通过关联表获取绑定的MCP工具
        tool_relations = self.agent_tool_relations.filter(
            tool__is_active=True,
            tool__status='healthy'
        ).order_by('order')
        
        for relation in tool_relations:
            try:
                # 创建MCP工具的CrewAI包装器
                tool_wrapper = self._create_tool_wrapper(relation)
                tools.append(tool_wrapper)
            except Exception as e:
                print(f"加载工具 {relation.tool.name} 失败: {str(e)}")
        
        return tools
    
    def _create_tool_wrapper(self, tool_relation):
        """为MCP工具创建CrewAI兼容的包装器"""
        from crewai_tools import BaseTool
        
        mcp_tool = tool_relation.tool
        
        class MCPToolWrapper(BaseTool):
            name: str = mcp_tool.name
            description: str = mcp_tool.description or f"MCP工具: {mcp_tool.display_name}"
            
            def _run(self, **kwargs):
                """执行MCP工具"""
                success, result = mcp_tool.call_tool(self.name, kwargs)
                if success:
                    return result
                else:
                    raise Exception(f"工具执行失败: {result}")
        
        return MCPToolWrapper()
    
    def start(self):
        """启动Agent"""
        if self.status in ['running']:
            return False, "Agent已在运行中"
        
        try:
            # 验证配置
            self.clean()
            
            # 更新状态
            self.status = 'active'
            self.save()
            
            return True, "Agent启动成功"
            
        except Exception as e:
            self.status = 'error'
            self.last_error = str(e)
            self.save()
            return False, str(e)
    
    def stop(self):
        """停止Agent"""
        self.status = 'inactive'
        self.save()
        return True, "Agent已停止"
    
    def pause(self):
        """暂停Agent"""
        if self.status == 'running':
            self.status = 'paused'
            self.save()
            return True, "Agent已暂停"
        return False, "Agent未在运行中"
    
    def resume(self):
        """恢复Agent"""
        if self.status == 'paused':
            self.status = 'running'
            self.save()
            return True, "Agent已恢复"
        return False, "Agent未处于暂停状态"
    
    def execute_task(self, task_description, context=None):
        """执行任务"""
        try:
            # 更新状态
            self.status = 'running'
            self.total_tasks += 1
            self.save()
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 创建Agent实例
            agent = self.create_crewai_agent()
            
            # 执行任务
            result = agent.execute(task_description, context=context)
            
            # 计算执行时间
            execution_time = int(time.time() - start_time)
            
            # 更新统计信息
            from django.utils import timezone
            self.completed_tasks += 1
            self.total_execution_time += execution_time
            self.last_execution = timezone.now()
            self.status = 'active'
            self.last_error = ""
            self.save()
            
            return True, result
            
        except Exception as e:
            # 记录错误
            from django.utils import timezone
            self.status = 'error'
            self.last_error = str(e)
            self.last_execution = timezone.now()
            self.save()
            
            return False, str(e)
    
    @classmethod
    def get_active_agents(cls):
        """获取所有活跃的Agent"""
        return cls.objects.filter(is_active=True, status__in=['active', 'running'])
    
    @classmethod
    def get_public_agents(cls):
        """获取所有公开Agent"""
        return cls.objects.filter(is_active=True, is_public=True)
    
    @classmethod
    def get_user_agents(cls, user):
        """获取用户可用的Agent"""
        from django.db.models import Q
        return cls.objects.filter(
            Q(is_public=True, is_active=True) | Q(owner=user) | Q(allowed_users=user)
        ).distinct()