"""
聊天消息模型

用于存储用户与Agent之间的聊天消息，包括消息内容、状态、Agent信息等。
"""

from django.db import models
from django.contrib.auth import get_user_model
from .chat_conversation import ChatConversation


User = get_user_model()


class ChatMessage(models.Model):
    """聊天消息模型"""
    
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', '助手'),
        ('system', '系统'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('sent', '已发送'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    ]
    
    # 关联信息
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='所属会话',
        help_text='消息所属的聊天会话'
    )
    
    # 消息基础信息
    role = models.CharField(
        max_length=32,
        choices=ROLE_CHOICES,
        verbose_name='消息角色',
        help_text='消息发送者的角色'
    )
    content = models.TextField(
        verbose_name='消息内容',
        help_text='消息的文本内容'
    )
    
    # Agent信息（仅助手消息）
    agent = models.ForeignKey(
        'CrewAIAgent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_messages',
        verbose_name='响应Agent',
        help_text='处理消息的Agent'
    )
    agent_name = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Agent名称',
        help_text='Agent的显示名称'
    )
    
    # 消息状态
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='sent',
        verbose_name='消息状态',
        help_text='消息的处理状态'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='错误信息',
        help_text='消息处理失败时的错误详情'
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
        db_table = 'chat_message'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"[{self.get_role_display()}] {content_preview}"
    
    def save(self, *args, **kwargs):
        """重写save方法，自动更新会话活动时间"""
        super().save(*args, **kwargs)
        
        # 更新会话消息计数和活动时间
        if self._state.adding:  # 只在新建消息时更新
            self.conversation.increment_message_count()
    
    @property
    def is_user_message(self):
        """是否为用户消息"""
        return self.role == 'user'
    
    @property
    def is_assistant_message(self):
        """是否为助手消息"""
        return self.role == 'assistant'
    
    @property
    def is_system_message(self):
        """是否为系统消息"""
        return self.role == 'system'
    
    @property
    def is_processing(self):
        """是否正在处理中"""
        return self.status in ['pending', 'processing']
    
    @property
    def is_failed(self):
        """是否处理失败"""
        return self.status == 'failed'
    
    def mark_as_processing(self):
        """标记为处理中"""
        self.status = 'processing'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_completed(self):
        """标记为已完成"""
        self.status = 'completed'
        self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_failed(self, error_msg=None):
        """标记为失败"""
        self.status = 'failed'
        if error_msg:
            self.error_message = error_msg
        self.save(update_fields=['status', 'error_message', 'updated_at'])