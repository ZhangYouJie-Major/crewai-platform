"""
Agent任务模型

用于存储Agent执行任务的详细信息，包括任务状态、执行时间、结果等。
"""

from django.db import models
from django.utils import timezone
from .chat_conversation import ChatConversation
from .chat_message import ChatMessage


class ChatAgentTask(models.Model):
    """Agent任务模型"""
    
    STATUS_CHOICES = [
        ('pending', '待执行'),
        ('running', '执行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
    ]
    
    # 关联信息
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='agent_tasks',
        verbose_name='所属会话',
        help_text='任务所属的聊天会话'
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
        related_name='agent_tasks',
        verbose_name='关联消息',
        help_text='任务关联的消息'
    )
    
    # 任务基础信息
    task_description = models.TextField(
        verbose_name='任务描述',
        help_text='Agent需要执行的任务描述'
    )
    agent = models.ForeignKey(
        'CrewAIAgent',
        on_delete=models.CASCADE,
        related_name='chat_tasks',
        verbose_name='执行Agent',
        help_text='执行此任务的Agent'
    )
    agent_name = models.CharField(
        max_length=128,
        verbose_name='Agent名称',
        help_text='Agent的显示名称'
    )
    
    # 执行状态
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='任务状态',
        help_text='任务的执行状态'
    )
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='开始时间',
        help_text='任务开始执行的时间'
    )
    end_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='结束时间',
        help_text='任务执行结束的时间'
    )
    execution_time_ms = models.PositiveIntegerField(
        default=0,
        verbose_name='执行时间(毫秒)',
        help_text='任务执行耗时，单位：毫秒'
    )
    
    # 执行结果
    result = models.TextField(
        blank=True,
        null=True,
        verbose_name='执行结果',
        help_text='Agent任务的执行结果'
    )
    error_details = models.TextField(
        blank=True,
        null=True,
        verbose_name='错误详情',
        help_text='任务执行失败时的详细错误信息'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'chat_agent_task'
        verbose_name = 'Agent任务'
        verbose_name_plural = 'Agent任务'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation', 'status']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        task_preview = self.task_description[:50] + '...' if len(self.task_description) > 50 else self.task_description
        return f"[{self.agent_name}] {task_preview} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        """重写save方法，自动处理Agent名称和统计"""
        if not self.agent_name and self.agent:
            self.agent_name = self.agent.name
        
        super().save(*args, **kwargs)
        
        # 如果是新任务，更新会话的Agent调用计数
        if self._state.adding:
            self.conversation.increment_agent_call_count()
    
    @property
    def is_pending(self):
        """是否待执行"""
        return self.status == 'pending'
    
    @property
    def is_running(self):
        """是否正在执行"""
        return self.status == 'running'
    
    @property
    def is_completed(self):
        """是否已完成"""
        return self.status == 'completed'
    
    @property
    def is_failed(self):
        """是否执行失败"""
        return self.status == 'failed'
    
    @property
    def execution_duration(self):
        """执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def start_execution(self):
        """开始执行任务"""
        self.status = 'running'
        self.start_time = timezone.now()
        self.save(update_fields=['status', 'start_time', 'updated_at'])
    
    def complete_execution(self, result=None):
        """完成任务执行"""
        self.status = 'completed'
        self.end_time = timezone.now()
        
        if result is not None:
            self.result = str(result)
        
        # 计算执行时间
        if self.start_time:
            duration = self.end_time - self.start_time
            self.execution_time_ms = int(duration.total_seconds() * 1000)
        
        self.save(update_fields=[
            'status', 'end_time', 'result', 'execution_time_ms', 'updated_at'
        ])
    
    def fail_execution(self, error_details=None):
        """任务执行失败"""
        self.status = 'failed'
        self.end_time = timezone.now()
        
        if error_details:
            self.error_details = str(error_details)
        
        # 计算执行时间
        if self.start_time:
            duration = self.end_time - self.start_time
            self.execution_time_ms = int(duration.total_seconds() * 1000)
        
        self.save(update_fields=[
            'status', 'end_time', 'error_details', 'execution_time_ms', 'updated_at'
        ])