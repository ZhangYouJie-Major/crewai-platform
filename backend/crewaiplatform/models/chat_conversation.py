"""
聊天会话模型

用于存储用户的聊天会话信息，包括会话配置、统计信息等。
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class ChatConversation(models.Model):
    """聊天会话模型"""
    
    AGENT_SELECTION_MODES = [
        ('auto', '自动选择'),
        ('manual', '手动选择'), 
        ('smart', '智能推荐'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('archived', '已归档'),
    ]
    
    # 基础信息
    title = models.CharField(
        max_length=255, 
        default='新会话',
        verbose_name='会话标题',
        help_text='用户可自定义的会话标题'
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name='会话描述',
        help_text='会话的详细描述信息'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_conversations',
        verbose_name='用户',
        help_text='会话所属用户'
    )
    
    # Agent配置
    agent_selection_mode = models.CharField(
        max_length=32,
        choices=AGENT_SELECTION_MODES,
        default='manual',
        verbose_name='Agent选择模式',
        help_text='Agent的选择方式'
    )
    primary_agent = models.ForeignKey(
        'CrewAIAgent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_conversations',
        verbose_name='主要Agent',
        help_text='手动模式下的默认Agent'
    )
    
    # 统计信息
    total_messages = models.PositiveIntegerField(
        default=0,
        verbose_name='总消息数',
        help_text='会话中的总消息数量'
    )
    total_agent_calls = models.PositiveIntegerField(
        default=0,
        verbose_name='总Agent调用数',
        help_text='会话中的总Agent调用次数'
    )
    
    # 状态管理
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态',
        help_text='会话状态'
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后活动时间',
        help_text='会话的最后活动时间'
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
        db_table = 'chat_conversation'
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-last_activity_at', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['last_activity_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity_at = timezone.now()
        self.save(update_fields=['last_activity_at'])
    
    def increment_message_count(self):
        """增加消息计数"""
        self.total_messages += 1
        self.update_activity()
        self.save(update_fields=['total_messages', 'last_activity_at'])
    
    def increment_agent_call_count(self):
        """增加Agent调用计数"""
        self.total_agent_calls += 1
        self.save(update_fields=['total_agent_calls'])
    
    @property
    def is_active(self):
        """是否为活跃会话"""
        return self.status == 'active'
    
    @property
    def latest_message(self):
        """获取最新消息"""
        return self.messages.order_by('-created_at').first()