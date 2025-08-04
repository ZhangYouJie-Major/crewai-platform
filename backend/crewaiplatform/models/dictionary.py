"""
字典管理模型

简化的单级字典结构：
- Dictionary: 字典项，支持层级关系（通过parent字段实现）

设计支持：
1. 层级关系：通过parent自关联实现多级结构
2. 数据规范化：统一管理下拉选项
3. 扩展性：可支持更多类型的字典配置
"""

from django.db import models
from django.core.validators import RegexValidator


class Dictionary(models.Model):
    """
    字典模型 - 支持层级结构的字典项
    
    可用于存储各种字典数据，如：
    - 供应商：OpenAI、Google等
    - 模型：gpt-4、gemini-pro等（通过parent关联到供应商）
    - 其他分类数据
    """
    
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
        ordering = ['sort_order', 'created_at']
        
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name
    
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