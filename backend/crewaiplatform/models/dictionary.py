"""
字典管理模型

支持分类的层级字典结构：
- Dictionary: 字典项，支持层级关系和类型分类

设计支持：
1. 类型分类：通过dict_type字段区分不同用途的字典树（完全开放）
2. 层级关系：通过parent自关联实现多级结构
3. 数据规范化：统一管理各类下拉选项
4. 扩展性：可支持任意类型的字典配置
"""

from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


# 字典类型常量（用于代码中引用，不限制数据库）
class DictType:
    """字典类型常量定义"""
    LLM = 'llm'                        # LLM供应商和模型的完整树
    MCP_SERVER_TYPE = 'mcp_server_type' # MCP服务器类型枚举
    AGENT_ROLE = 'agent_role'          # Agent角色类型枚举
    SYSTEM_STATUS = 'system_status'     # 系统状态枚举
    TASK_PRIORITY = 'task_priority'     # 任务优先级枚举


class Dictionary(models.Model):
    """
    字典模型 - 支持分类和层级结构的字典项
    
    可用于存储各种字典数据，如：
    - LLM配置：供应商（OpenAI、Google等）和模型（gpt-4、gemini-pro等）
    - MCP服务器类型：filesystem、database、api等
    - Agent角色类型：研究员、分析师、写作助手等
    - 其他任意分类数据
    """
    
    # 字典类型（完全开放，不限制选择）
    dict_type = models.CharField(
        max_length=50,
        default='general',  # 为现有数据提供默认值
        verbose_name='字典类型',
        help_text='字典数据的分类类型，如：llm、mcp_server_type、agent_role等'
    )
    
    # 父级字典项（支持多级结构）
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        verbose_name='父级字典项',
        help_text='用于建立层级关系，如模型隶属于供应商'
    )
    
    # 字典项代码
    code = models.CharField(
        max_length=100,
        verbose_name='字典项代码',
        help_text='用于程序识别的代码，如：openai、gpt-4'
    )
    
    # 字典项名称
    name = models.CharField(
        max_length=100,
        verbose_name='字典项名称',
        help_text='显示给用户的名称，如：OpenAI、GPT-4'
    )
    
    # 字典项值（可选，用于存储额外信息）
    value = models.TextField(
        blank=True,
        null=True,
        verbose_name='字典项值',
        help_text='额外的配置信息，如API端点等'
    )
    
    # 字典项描述
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='字典项描述',
        help_text='详细说明信息'
    )
    
    # 是否启用
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='是否启用此字典项'
    )
    
    # 排序顺序
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name='排序顺序',
        help_text='数字越小排序越靠前'
    )
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'sys_dictionary'
        verbose_name = '字典项'
        verbose_name_plural = '字典项'
        ordering = ['dict_type', 'sort_order', 'created_at']
        # 同一类型下的同一层级中code唯一
        unique_together = [
            ('dict_type', 'parent', 'code'),
        ]
        
    def __str__(self):
        if self.parent:
            return f"[{self.dict_type}] {self.parent.name} -> {self.name}"
        return f"[{self.dict_type}] {self.name}"
    
    def get_full_path(self):
        """获取完整路径，用于显示层级关系"""
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name
    
    def get_children(self):
        """获取子级字典项"""
        return self.children.filter(is_active=True).order_by('sort_order', 'created_at')
    
    def get_level(self):
        """获取层级深度"""
        if self.parent:
            return self.parent.get_level() + 1
        return 1
    
    def clean(self):
        """模型数据验证"""
        super().clean()
        
        # 防止循环引用
        if self.parent and self.pk:
            current = self.parent
            while current:
                if current.pk == self.pk:
                    raise ValidationError("不能设置循环引用的父级关系")
                current = current.parent
        
        # 确保父子级的dict_type一致
        if self.parent and self.parent.dict_type != self.dict_type:
            raise ValidationError(
                f"父级字典项类型为 '{self.parent.dict_type}'，"
                f"子级字典项类型必须一致，不能为 '{self.dict_type}'"
            )