"""
字典管理 - Django Admin配置

包含字典相关模型的管理配置
"""

from django.contrib import admin
from ..models import Dictionary


@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    """字典管理"""
    list_display = ('code', 'name', 'parent', 'is_active', 'sort_order', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('code', 'name', 'description')
    list_editable = ('is_active', 'sort_order')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('code', 'name', 'value', 'description')
        }),
        ('层级关系', {
            'fields': ('parent',)
        }),
        ('状态控制', {
            'fields': ('is_active', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """优化查询，预加载父级关系"""
        return super().get_queryset(request).select_related('parent') 