"""
MCP工具配置 - Model Context Protocol 工具管理

MCP (Model Context Protocol) 是一个开放标准，用于在AI应用和数据源之间建立安全连接。
支持三种传输方式：
1. stdio - 通过标准输入输出与本地进程通信
2. SSE (Server-Sent Events) - 通过HTTP流式传输
3. HTTP - 标准HTTP请求响应
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import json


class MCPTool(models.Model):
    """
    MCP工具配置表
    管理Model Context Protocol工具的连接配置和健康状态
    """
    
    # MCP服务器传输类型
    SERVER_TYPE_CHOICES = [
        ('stdio', 'Standard I/O'),
        ('sse', 'Server-Sent Events'),
        ('http', 'HTTP'),
    ]
    
    # 工具状态
    STATUS_CHOICES = [
        ('unknown', '未知'),
        ('healthy', '健康'),
        ('unhealthy', '不健康'),
        ('error', '错误'),
    ]
    
    # 基本信息
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="工具名称",
        help_text="MCP工具的唯一标识名称"
    )
    
    display_name = models.CharField(
        max_length=128,
        verbose_name="显示名称",
        help_text="用于界面展示的友好名称"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="工具描述",
        help_text="工具的功能描述和使用说明"
    )
    
    version = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="工具版本",
        help_text="工具的版本号"
    )
    
    # MCP连接配置
    server_type = models.CharField(
        max_length=32,
        choices=SERVER_TYPE_CHOICES,
        verbose_name="服务器类型",
        help_text="MCP服务器的传输协议类型"
    )
    
    connection_config = models.JSONField(
        default=dict,
        verbose_name="连接配置",
        help_text="MCP服务器的连接参数配置"
    )
    
    # stdio配置示例:
    # {
    #   "command": "npx",
    #   "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/directory"],
    #   "env": {"DEBUG": "true"}
    # }
    
    # sse配置示例:
    # {
    #   "url": "http://localhost:3001/sse",
    #   "headers": {"Authorization": "Bearer token"}
    # }
    
    # http配置示例:
    # {
    #   "base_url": "http://localhost:3001",
    #   "headers": {"Authorization": "Bearer token"}
    # }
    
    # 工具Schema定义
    tool_schema = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="工具Schema",
        help_text="工具的输入输出Schema定义（JSON Schema格式）"
    )
    
    # 示例Schema:
    # {
    #   "tools": [
    #     {
    #       "name": "read_file",
    #       "description": "Read the contents of a file",
    #       "inputSchema": {
    #         "type": "object",
    #         "properties": {
    #           "path": {"type": "string", "description": "File path to read"}
    #         },
    #         "required": ["path"]
    #       }
    #     }
    #   ]
    # }
    
    # 超时和重试配置
    connection_timeout = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        verbose_name="连接超时",
        help_text="建立连接的超时时间（秒）"
    )
    
    request_timeout = models.IntegerField(
        default=60,
        validators=[MinValueValidator(1), MaxValueValidator(600)],
        verbose_name="请求超时",
        help_text="单个请求的超时时间（秒）"
    )
    
    max_retries = models.IntegerField(
        default=3,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="最大重试次数",
        help_text="连接失败时的重试次数"
    )
    
    retry_delay = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(60.0)],
        verbose_name="重试延迟",
        help_text="重试之间的延迟时间（秒）"
    )
    
    # 健康检查配置
    health_check_enabled = models.BooleanField(
        default=True,
        verbose_name="启用健康检查",
        help_text="是否定期进行健康检查"
    )
    
    health_check_interval = models.IntegerField(
        default=300,
        validators=[MinValueValidator(60), MaxValueValidator(3600)],
        verbose_name="健康检查间隔",
        help_text="健康检查的间隔时间（秒）"
    )
    
    health_check_method = models.CharField(
        max_length=64,
        default="ping",
        verbose_name="健康检查方法",
        help_text="健康检查使用的方法名称"
    )
    
    # 状态信息
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='unknown',
        verbose_name="状态",
        help_text="工具的当前健康状态"
    )
    
    last_health_check = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="最后健康检查时间",
        help_text="最后一次健康检查的时间"
    )
    
    last_error = models.TextField(
        blank=True,
        verbose_name="最后错误",
        help_text="最后一次连接或调用错误的详细信息"
    )
    
    response_time_ms = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="响应时间",
        help_text="最近一次请求的响应时间（毫秒）"
    )
    
    # 使用统计
    total_calls = models.IntegerField(
        default=0,
        verbose_name="总调用次数",
        help_text="工具被调用的总次数"
    )
    
    success_calls = models.IntegerField(
        default=0,
        verbose_name="成功调用次数",
        help_text="成功调用的次数"
    )
    
    # 权限和访问控制
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="是否在系统中启用此工具"
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name="是否公开",
        help_text="是否允许所有用户使用此工具"
    )
    
    allowed_users = models.ManyToManyField(
        'User',
        blank=True,
        verbose_name="允许使用的用户",
        help_text="允许使用此工具的用户列表"
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
        db_table = 'mcp_tool'
        verbose_name = 'MCP工具配置'
        verbose_name_plural = 'MCP工具配置'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['server_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.server_type})"
    
    def clean(self):
        """验证配置数据"""
        super().clean()
        
        # 验证连接配置
        if not self.connection_config:
            raise ValidationError("连接配置不能为空")
        
        # 根据服务器类型验证必需的配置项
        if self.server_type == 'stdio':
            required_fields = ['command']
            for field in required_fields:
                if field not in self.connection_config:
                    raise ValidationError(f"stdio类型需要配置 {field} 字段")
        
        elif self.server_type == 'sse':
            required_fields = ['url']
            for field in required_fields:
                if field not in self.connection_config:
                    raise ValidationError(f"sse类型需要配置 {field} 字段")
        
        elif self.server_type == 'http':
            required_fields = ['base_url']
            for field in required_fields:
                if field not in self.connection_config:
                    raise ValidationError(f"http类型需要配置 {field} 字段")
        
        # 验证tool_schema格式
        if self.tool_schema:
            self._validate_tool_schema()
    
    def _validate_tool_schema(self):
        """验证工具Schema格式"""
        try:
            if 'tools' not in self.tool_schema:
                raise ValidationError("tool_schema必须包含 'tools' 字段")
            
            tools = self.tool_schema['tools']
            if not isinstance(tools, list):
                raise ValidationError("tools必须是数组格式")
            
            for tool in tools:
                required_fields = ['name', 'description']
                for field in required_fields:
                    if field not in tool:
                        raise ValidationError(f"工具定义必须包含 {field} 字段")
                        
        except (ValueError, TypeError) as e:
            raise ValidationError(f"tool_schema格式错误: {str(e)}")
    
    def get_success_rate(self):
        """获取成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.success_calls / self.total_calls) * 100
    
    def get_mcp_config(self):
        """获取MCP客户端配置"""
        config = {
            'name': self.name,
            'server_type': self.server_type,
            'connection_timeout': self.connection_timeout,
            'request_timeout': self.request_timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
        }
        
        # 合并连接配置
        config.update(self.connection_config)
        
        return config
    
    def create_mcp_client(self):
        """创建MCP客户端实例"""
        try:
            from mcp import Client  # 假设使用的MCP客户端库
            
            config = self.get_mcp_config()
            
            if self.server_type == 'stdio':
                return Client.create_stdio(**config)
            elif self.server_type == 'sse':
                return Client.create_sse(**config)
            elif self.server_type == 'http':
                return Client.create_http(**config)
            else:
                raise ValueError(f"不支持的服务器类型: {self.server_type}")
                
        except Exception as e:
            raise ValueError(f"创建MCP客户端失败: {str(e)}")
    
    def test_connection(self):
        """测试MCP连接"""
        try:
            client = self.create_mcp_client()
            
            # 记录开始时间
            import time
            start_time = time.time()
            
            # 执行健康检查
            result = client.call_tool(self.health_check_method, {})
            
            # 计算响应时间
            response_time = int((time.time() - start_time) * 1000)
            
            # 更新状态
            from django.utils import timezone
            self.status = 'healthy'
            self.last_health_check = timezone.now()
            self.last_error = ""
            self.response_time_ms = response_time
            self.save()
            
            return True, "连接成功", result
            
        except Exception as e:
            # 更新错误状态
            from django.utils import timezone
            self.status = 'unhealthy'
            self.last_health_check = timezone.now()
            self.last_error = str(e)
            self.save()
            
            return False, str(e), None
    
    def call_tool(self, tool_name, arguments=None):
        """调用MCP工具"""
        if arguments is None:
            arguments = {}
        
        try:
            client = self.create_mcp_client()
            
            # 记录调用
            self.total_calls += 1
            
            # 调用工具
            result = client.call_tool(tool_name, arguments)
            
            # 记录成功
            self.success_calls += 1
            self.save()
            
            return True, result
            
        except Exception as e:
            # 记录失败但不增加success_calls
            self.save()
            return False, str(e)
    
    def get_available_tools(self):
        """获取可用的工具列表"""
        if self.tool_schema and 'tools' in self.tool_schema:
            return [tool['name'] for tool in self.tool_schema['tools']]
        return []
    
    def get_tool_info(self, tool_name):
        """获取特定工具的信息"""
        if self.tool_schema and 'tools' in self.tool_schema:
            for tool in self.tool_schema['tools']:
                if tool['name'] == tool_name:
                    return tool
        return None
    
    @classmethod
    def get_healthy_tools(cls):
        """获取所有健康的工具"""
        return cls.objects.filter(is_active=True, status='healthy')
    
    @classmethod
    def get_public_tools(cls):
        """获取所有公开工具"""
        return cls.objects.filter(is_active=True, is_public=True)
    
    @classmethod
    def get_user_tools(cls, user):
        """获取用户可用的工具"""
        from django.db.models import Q
        return cls.objects.filter(
            Q(is_public=True) | Q(allowed_users=user),
            is_active=True
        ).distinct()