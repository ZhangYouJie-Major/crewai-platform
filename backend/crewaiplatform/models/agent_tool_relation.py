"""
Agent-Tool关联 - CrewAI Agent与MCP工具的绑定管理

管理Agent与MCP工具之间的多对多关系，支持：
- 工具使用顺序控制
- 个性化配置覆盖
- 动态绑定和解绑
- 使用统计和监控
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from .crewai_agent import CrewAIAgent
from .mcp_tool import MCPTool
import json


class AgentToolRelation(models.Model):
    """
    Agent-Tool关联表
    管理CrewAI Agent与MCP工具的绑定关系
    """
    
    # 关联状态
    STATUS_CHOICES = [
        ('active', '激活'),
        ('inactive', '未激活'),
        ('error', '错误'),
        ('deprecated', '已弃用'),
    ]
    
    # 权限级别选择
    PERMISSION_LEVEL_CHOICES = [
        ('read', '只读'),
        ('write', '读写'),
        ('execute', '执行'),
        ('admin', '管理员'),
    ]
    
    # 核心关联
    agent = models.ForeignKey(
        CrewAIAgent,
        on_delete=models.CASCADE,
        related_name='agent_tool_relations',
        verbose_name="关联Agent",
        help_text="绑定的CrewAI Agent"
    )
    
    tool = models.ForeignKey(
        MCPTool,
        on_delete=models.CASCADE,
        related_name='tool_agent_relations',
        verbose_name="关联工具",
        help_text="绑定的MCP工具"
    )
    
    # 使用控制
    order = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="使用顺序",
        help_text="工具在Agent中的使用优先级，数字越小优先级越高"
    )
    
    is_required = models.BooleanField(
        default=False,
        verbose_name="是否必需",
        help_text="该工具是否为Agent执行任务的必需工具"
    )
    
    is_fallback = models.BooleanField(
        default=False,
        verbose_name="是否为备用工具",
        help_text="当主要工具失败时是否作为备用工具使用"
    )
    
    max_calls_per_task = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name="每任务最大调用次数",
        help_text="单个任务中对该工具的最大调用次数"
    )
    
    # 配置覆盖
    config_override = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="配置覆盖",
        help_text="对工具默认配置的覆盖参数"
    )
    
    # 示例配置覆盖:
    # {
    #   "timeout": 60,
    #   "retry_attempts": 5,
    #   "custom_headers": {"X-Agent-ID": "agent_123"},
    #   "tool_specific_params": {
    #     "max_file_size": "10MB",
    #     "allowed_extensions": [".txt", ".md", ".py"]
    #   }
    # }
    
    prompt_template = models.TextField(
        blank=True,
        verbose_name="提示模板",
        help_text="调用该工具时使用的自定义提示模板"
    )
    
    # 权限和限制
    permission_level = models.CharField(
        max_length=32,
        choices=PERMISSION_LEVEL_CHOICES,
        default='read',
        verbose_name="权限级别",
        help_text="Agent对该工具的权限级别"
    )
    
    allowed_operations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="允许的操作",
        help_text="Agent可以使用的工具操作列表"
    )
    
    # 示例allowed_operations:
    # ["read_file", "write_file", "list_directory"]
    
    restricted_paths = models.JSONField(
        default=list,
        blank=True,
        verbose_name="限制路径",
        help_text="工具访问的限制路径列表（如果适用）"
    )
    
    # 监控和统计
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="状态",
        help_text="关联关系的当前状态"
    )
    
    total_calls = models.IntegerField(
        default=0,
        verbose_name="总调用次数",
        help_text="Agent对该工具的总调用次数"
    )
    
    successful_calls = models.IntegerField(
        default=0,
        verbose_name="成功调用次数",
        help_text="成功调用的次数"
    )
    
    total_execution_time = models.IntegerField(
        default=0,
        verbose_name="总执行时间",
        help_text="该工具的累计执行时间（毫秒）"
    )
    
    last_used = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="最后使用时间",
        help_text="Agent最后一次使用该工具的时间"
    )
    
    last_error = models.TextField(
        blank=True,
        verbose_name="最后错误",
        help_text="最后一次调用错误的详细信息"
    )
    
    # 版本控制
    config_version = models.CharField(
        max_length=32,
        default='1.0',
        verbose_name="配置版本",
        help_text="配置的版本号，用于跟踪配置变更"
    )
    
    # 时间戳
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="绑定时间",
        help_text="Agent与工具绑定的时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        db_table = 'agent_tool_relation'
        verbose_name = 'Agent-Tool关联'
        verbose_name_plural = 'Agent-Tool关联'
        ordering = ['agent', 'order', '-assigned_at']
        
        # 确保同一个Agent不会重复绑定相同工具
        unique_together = [['agent', 'tool']]
        
        indexes = [
            models.Index(fields=['agent', 'order']),
            models.Index(fields=['tool', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['is_required']),
            models.Index(fields=['is_fallback']),
        ]
    
    def __str__(self):
        return f"{self.agent.name} → {self.tool.name} (优先级: {self.order})"
    
    def clean(self):
        """验证关联配置"""
        super().clean()
        
        # 验证Agent和工具都是激活状态
        if not self.agent.is_active:
            raise ValidationError("不能绑定未激活的Agent")
        
        if not self.tool.is_active:
            raise ValidationError("不能绑定未激活的工具")
        
        # 验证权限级别与工具类型的兼容性
        self._validate_permission_compatibility()
        
        # 验证允许的操作
        self._validate_allowed_operations()
        
        # 验证配置覆盖格式
        self._validate_config_override()
    
    def _validate_permission_compatibility(self):
        """验证权限级别与工具类型的兼容性"""
        # 这里可以添加特定工具类型的权限验证逻辑
        pass
    
    def _validate_allowed_operations(self):
        """验证允许的操作是否在工具支持范围内"""
        if self.allowed_operations:
            available_tools = self.tool.get_available_tools()
            for operation in self.allowed_operations:
                if operation not in available_tools:
                    raise ValidationError(f"操作 '{operation}' 不在工具支持的操作列表中")
    
    def _validate_config_override(self):
        """验证配置覆盖格式"""
        if self.config_override:
            # 验证JSON格式
            try:
                json.dumps(self.config_override)
            except (TypeError, ValueError) as e:
                raise ValidationError(f"配置覆盖格式错误: {str(e)}")
    
    def get_success_rate(self):
        """获取调用成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.successful_calls / self.total_calls) * 100
    
    def get_average_execution_time(self):
        """获取平均执行时间"""
        if self.successful_calls == 0:
            return 0.0
        return self.total_execution_time / self.successful_calls
    
    def get_effective_config(self):
        """获取有效的工具配置（合并默认配置和覆盖配置）"""
        base_config = self.tool.get_mcp_config()
        
        # 合并配置覆盖
        if self.config_override:
            base_config.update(self.config_override)
        
        # 添加关联特定的配置
        base_config.update({
            'agent_id': self.agent.id,
            'relation_id': self.id,
            'permission_level': self.permission_level,
            'allowed_operations': self.allowed_operations,
            'restricted_paths': self.restricted_paths,
        })
        
        return base_config
    
    def call_tool(self, operation, arguments=None, context=None):
        """通过关联调用工具"""
        if arguments is None:
            arguments = {}
        
        try:
            # 检查状态
            if self.status != 'active':
                raise ValueError(f"关联状态为 {self.status}，无法调用工具")
            
            # 检查操作权限
            if self.allowed_operations and operation not in self.allowed_operations:
                raise ValueError(f"操作 '{operation}' 不在允许的操作列表中")
            
            # 检查调用限制
            if self.max_calls_per_task:
                # 这里可以添加任务级别的调用次数检查逻辑
                pass
            
            # 记录调用
            import time
            start_time = time.time()
            self.total_calls += 1
            
            # 获取有效配置
            config = self.get_effective_config()
            
            # 调用工具
            success, result = self.tool.call_tool(operation, arguments)
            
            if success:
                # 记录成功
                execution_time = int((time.time() - start_time) * 1000)
                self.successful_calls += 1
                self.total_execution_time += execution_time
                
                from django.utils import timezone
                self.last_used = timezone.now()
                self.last_error = ""
                self.save()
                
                return True, result
            else:
                # 记录失败
                self.last_error = str(result)
                self.save()
                return False, result
                
        except Exception as e:
            # 记录异常
            self.last_error = str(e)
            self.save()
            return False, str(e)
    
    def test_connection(self):
        """测试工具连接"""
        try:
            # 使用工具的健康检查方法
            success, message, _ = self.tool.test_connection()
            
            if success:
                self.status = 'active'
                self.last_error = ""
            else:
                self.status = 'error'
                self.last_error = message
            
            self.save()
            return success, message
            
        except Exception as e:
            self.status = 'error'
            self.last_error = str(e)
            self.save()
            return False, str(e)
    
    def activate(self):
        """激活关联"""
        if self.agent.is_active and self.tool.is_active:
            self.status = 'active'
            self.save()
            return True, "关联已激活"
        else:
            return False, "Agent或工具未激活，无法激活关联"
    
    def deactivate(self):
        """停用关联"""
        self.status = 'inactive'
        self.save()
        return True, "关联已停用"
    
    def update_config_version(self):
        """更新配置版本"""
        try:
            # 简单的版本号递增逻辑
            current_version = self.config_version
            if current_version.count('.') == 1:
                major, minor = current_version.split('.')
                new_version = f"{major}.{int(minor) + 1}"
            else:
                new_version = "1.1"
            
            self.config_version = new_version
            self.save()
            
        except Exception:
            # 如果版本号格式不正确，重置为1.0
            self.config_version = "1.0"
            self.save()
    
    @classmethod
    def get_agent_tools(cls, agent):
        """获取Agent的所有工具关联"""
        return cls.objects.filter(
            agent=agent,
            status='active'
        ).order_by('order')
    
    @classmethod
    def get_tool_agents(cls, tool):
        """获取工具的所有Agent关联"""
        return cls.objects.filter(
            tool=tool,
            status='active'
        ).order_by('-assigned_at')
    
    @classmethod
    def get_high_usage_relations(cls, min_calls=100):
        """获取高使用频率的关联"""
        return cls.objects.filter(
            total_calls__gte=min_calls,
            status='active'
        ).order_by('-total_calls')
    
    @classmethod
    def get_problematic_relations(cls, max_success_rate=80):
        """获取问题关联（成功率低）"""
        relations = []
        for relation in cls.objects.filter(status='active', total_calls__gt=0):
            if relation.get_success_rate() < max_success_rate:
                relations.append(relation)
        return relations
    
    def save(self, *args, **kwargs):
        """保存时更新配置版本"""
        if self.pk:  # 如果是更新操作
            try:
                old_relation = AgentToolRelation.objects.get(pk=self.pk)
                # 检查关键配置是否有变化
                if (old_relation.config_override != self.config_override or
                    old_relation.permission_level != self.permission_level or
                    old_relation.allowed_operations != self.allowed_operations):
                    self.update_config_version()
            except AgentToolRelation.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)