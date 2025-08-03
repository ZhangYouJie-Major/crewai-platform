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
    
    async def create_mcp_client(self):
        """根据类型创建对应的 MCP 客户端（官方 SDK）"""
        try:
            from mcp import Client
            config = self.get_mcp_config()
            
            if self.server_type == 'stdio':
                from mcp.client.stdio import stdio_client
                return Client(stdio_client(**config))
                
            elif self.server_type == 'sse':
                from mcp.client.sse import sse_client
                return Client(sse_client(**config))
                
            elif self.server_type == 'http':
                from mcp.client.http import http_client
                return Client(http_client(**config))
                
            else:
                raise ValueError(f"不支持的服务器类型: {self.server_type}")
                
        except ImportError as e:
            # 如果 MCP 库不可用，返回错误信息但不中断程序
            raise ValueError(f"MCP库未安装或版本不兼容: {str(e)}。建议使用 pip install mcp 安装官方SDK")
        except Exception as e:
            raise ValueError(f"创建MCP客户端失败: {str(e)}")
    
    async def test_mcp_client_connection(self):
        """使用官方 MCP SDK 测试连接（可选）"""
        try:
            import asyncio
            from django.utils import timezone
            import time
            
            start_time = time.time()
            
            # 创建客户端
            client = await self.create_mcp_client()
            
            # 使用异步上下文管理器
            async with client:
                # 尝试列出可用工具
                tools = await client.list_tools()
                
                response_time = int((time.time() - start_time) * 1000)
                
                # 更新状态
                self.status = 'healthy'
                self.last_health_check = timezone.now()
                self.last_error = ""
                self.response_time_ms = response_time
                
                # 更新工具 schema
                if tools and hasattr(tools, 'tools'):
                    self.tool_schema = {
                        'tools': [
                            {
                                'name': tool.name,
                                'description': tool.description,
                                'inputSchema': getattr(tool, 'inputSchema', {})
                            }
                            for tool in tools.tools
                        ]
                    }
                
                self.save()
                
                return True, "MCP连接成功", {
                    'tools_count': len(tools.tools) if tools and hasattr(tools, 'tools') else 0,
                    'response_time_ms': response_time
                }
                
        except ImportError:
            # MCP 库不可用，回退到标准 HTTP 测试
            return await self._fallback_to_http_test()
        except Exception as e:
            # 更新错误状态
            self.status = 'error'
            self.last_health_check = timezone.now()
            self.last_error = str(e)
            self.save()
            
            return False, f"MCP连接失败: {str(e)}", None
    
    async def _fallback_to_http_test(self):
        """当MCP库不可用时的回退测试方案"""
        return self.test_connection()  # 使用之前实现的标准HTTP测试
    
    def test_connection_with_crewai(self):
        """使用CrewAI SDK测试MCP连接（推荐方法）"""
        import time
        from django.utils import timezone
        
        start_time = time.time()
        
        try:
            # 优先使用CrewAI SDK进行测试
            from crewai_tools import MCPServerAdapter
            
            # 构建CrewAI兼容的服务器配置
            server_config = {
                "transport": self.server_type,
                **self.connection_config
            }
            
            # 使用MCPServerAdapter进行连接测试
            with MCPServerAdapter(server_config) as tools:
                tool_names = [t.name for t in tools] if tools else []
                
                # 计算响应时间
                response_time = int((time.time() - start_time) * 1000)
                
                # 更新状态
                self.status = 'healthy'
                self.last_error = ""
                self.response_time_ms = response_time
                self.last_health_check = timezone.now()
                
                # 更新工具schema
                if tools:
                    try:
                        self.tool_schema = {
                            'tools': [
                                {
                                    'name': tool.name,
                                    'description': getattr(tool, 'description', ''),
                                    'inputSchema': getattr(tool, 'args_schema', {})
                                }
                                for tool in tools
                            ]
                        }
                    except Exception as schema_error:
                        # 如果schema更新失败，记录但不中断测试
                        pass
                
                self.save()
                
                return True, f"✅ 连接成功，可用工具：{len(tool_names)}个", {
                    'tools_count': len(tool_names),
                    'tool_names': tool_names,
                    'response_time_ms': response_time,
                    'sdk': 'crewai_tools'
                }
                
        except ImportError:
            # CrewAI SDK不可用，回退到标准测试
            return self._fallback_connection_test()
            
        except Exception as e:
            # CrewAI连接失败，记录错误
            response_time = int((time.time() - start_time) * 1000)
            error_msg = f"❌ 连接失败：{str(e)}"
            
            self.status = 'error'
            self.last_error = error_msg
            self.response_time_ms = response_time
            self.last_health_check = timezone.now()
            self.save()
            
            return False, error_msg, None
    
    def test_connection(self):
        """测试MCP连接 - 智能选择最佳方法"""
        # 优先使用CrewAI SDK测试
        try:
            return self.test_connection_with_crewai()
        except Exception:
            # 如果CrewAI测试失败，回退到标准测试
            return self._fallback_connection_test()
    
    def _fallback_connection_test(self):
        """回退到标准连接测试方法"""
        import time
        import requests
        import subprocess
        import os
        from django.utils import timezone
        
        start_time = time.time()
        
        try:
            config = self.connection_config or {}
            
            if self.server_type == 'sse':
                # SSE (Server-Sent Events) 连接测试
                success, message, result = self._test_sse_connection(config)
                
            elif self.server_type == 'http':
                # HTTP 连接测试
                success, message, result = self._test_http_connection(config)
                
            elif self.server_type == 'stdio':
                # STDIO 连接测试
                success, message, result = self._test_stdio_connection(config)
                
            else:
                raise ValueError(f"不支持的服务器类型: {self.server_type}")
            
            # 计算响应时间
            response_time = int((time.time() - start_time) * 1000)
            
            # 更新状态
            if success:
                self.status = 'healthy'
                self.last_error = ""
                self.response_time_ms = response_time
            else:
                self.status = 'unhealthy'
                self.last_error = message
                
            self.last_health_check = timezone.now()
            self.save()
            
            return success, message, result
            
        except Exception as e:
            # 更新错误状态
            self.status = 'error'
            self.last_health_check = timezone.now()
            self.last_error = str(e)
            self.response_time_ms = int((time.time() - start_time) * 1000)
            self.save()
            
            return False, f"连接测试失败: {str(e)}", None
    
    def _test_sse_connection(self, config):
        """测试SSE连接"""
        try:
            import requests
            
            url = config.get('url')
            if not url:
                return False, "SSE配置中缺少URL", None
                
            headers = config.get('headers', {})
            timeout = self.connection_timeout or 30
            
            # 尝试连接到SSE端点
            response = requests.get(
                url, 
                headers=headers, 
                timeout=timeout,
                stream=True
            )
            
            if response.status_code == 200:
                # 检查是否是SSE响应
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type or 'text/plain' in content_type:
                    return True, "SSE连接成功", {
                        "status_code": response.status_code,
                        "content_type": content_type,
                        "headers": dict(response.headers)
                    }
                else:
                    return False, f"响应类型不是SSE: {content_type}", None
            else:
                return False, f"HTTP状态码错误: {response.status_code}", None
                
        except requests.exceptions.Timeout:
            return False, "连接超时", None
        except requests.exceptions.ConnectionError:
            return False, "连接失败，无法访问服务器", None
        except Exception as e:
            return False, f"SSE连接测试失败: {str(e)}", None
    
    def _test_http_connection(self, config):
        """测试HTTP连接"""
        try:
            import requests
            
            base_url = config.get('base_url') or config.get('url')
            if not base_url:
                return False, "HTTP配置中缺少base_url或url", None
                
            headers = config.get('headers', {})
            timeout = self.connection_timeout or 30
            
            # 尝试发送健康检查请求
            health_endpoint = base_url.rstrip('/') + '/health'
            
            try:
                response = requests.get(
                    health_endpoint,
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code in [200, 404]:  # 404也表示服务器在运行
                    return True, "HTTP连接成功", {
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000,
                        "headers": dict(response.headers)
                    }
                else:
                    return False, f"HTTP状态码: {response.status_code}", None
                    
            except requests.exceptions.RequestException:
                # 如果/health端点不存在，尝试根路径
                response = requests.get(
                    base_url,
                    headers=headers,
                    timeout=timeout
                )
                
                if response.status_code < 500:  # 任何非服务器错误都表示连接成功
                    return True, "HTTP连接成功（根路径）", {
                        "status_code": response.status_code,
                        "response_time_ms": response.elapsed.total_seconds() * 1000
                    }
                else:
                    return False, f"HTTP状态码: {response.status_code}", None
                    
        except requests.exceptions.Timeout:
            return False, "HTTP连接超时", None
        except requests.exceptions.ConnectionError:
            return False, "HTTP连接失败，无法访问服务器", None
        except Exception as e:
            return False, f"HTTP连接测试失败: {str(e)}", None
    
    def _test_stdio_connection(self, config):
        """测试STDIO连接"""
        try:
            import subprocess
            import os
            
            command = config.get('command')
            args = config.get('args', [])
            env = config.get('env', {})
            
            if not command:
                return False, "STDIO配置中缺少command", None
                
            # 构造完整的命令
            full_command = [command] + args
            timeout = self.connection_timeout or 30
            
            # 尝试执行命令并检查是否可以启动
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                env={**os.environ, **env} if env else None
            )
            
            # 检查命令是否成功执行
            if result.returncode == 0 or result.stderr == "":
                return True, "STDIO连接成功", {
                    "command": " ".join(full_command),
                    "return_code": result.returncode,
                    "stdout": result.stdout[:500] if result.stdout else "",
                    "stderr": result.stderr[:500] if result.stderr else ""
                }
            else:
                return False, f"命令执行失败: {result.stderr}", None
                
        except subprocess.TimeoutExpired:
            return False, "STDIO命令执行超时", None
        except FileNotFoundError:
            return False, f"命令不存在: {command}", None
        except Exception as e:
            return False, f"STDIO连接测试失败: {str(e)}", None
    
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