"""
数据字典管理序列化器

提供字典项的序列化器，支持分类和树形结构管理
"""

from rest_framework import serializers
from ..models import Dictionary


class DictionarySerializer(serializers.ModelSerializer):
    """字典项序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_code = serializers.CharField(source='parent.code', read_only=True)
    full_path = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = (
            'id', 'dict_type', 'parent', 'parent_name', 'parent_code',
            'code', 'name', 'value', 'description', 'is_active', 'sort_order',
            'full_path', 'level', 'children_count', 'children',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'dict_type': {'help_text': '字典类型，如：llm、mcp_server_type等'},
            'parent': {'help_text': '父级字典项（用于层级结构）'},
            'code': {'help_text': '字典项代码'},
            'name': {'help_text': '字典项名称'},
            'value': {'help_text': '字典项值（额外信息）'},
            'sort_order': {'help_text': '排序顺序，数字越小越靠前'},
        }
    
    def get_full_path(self, obj):
        """获取完整路径"""
        return obj.get_full_path()
    
    def get_level(self, obj):
        """获取层级深度"""
        return obj.get_level()
    
    def get_children_count(self, obj):
        """获取子级项目数量"""
        return obj.get_children().count()
    
    def get_children(self, obj):
        """获取子级项目列表"""
        # 只在树形查询时返回子级数据，避免无限递归
        request = self.context.get('request')
        if request:
            # 兼容DRF的query_params和Django原生的GET参数
            query_params = getattr(request, 'query_params', request.GET)
            if query_params.get('tree', 'false').lower() == 'true':
                children = obj.get_children()
                return DictionarySimpleSerializer(children, many=True).data
        return []
    
    def validate(self, attrs):
        """验证字典项数据"""
        parent = attrs.get('parent')
        dict_type = attrs.get('dict_type')
        code = attrs.get('code')
        
        # 防止循环引用
        if parent and self.instance:
            current = parent
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError("不能设置循环引用的父级关系")
                current = current.parent
        
        # 确保父子级的dict_type一致
        if parent and parent.dict_type != dict_type:
            raise serializers.ValidationError(
                f"父级字典项类型为 '{parent.dict_type}'，子级字典项类型必须一致"
            )
        
        return attrs
    
    def validate_parent(self, value):
        """验证父级字典项"""
        if value:
            # 确保父级字典项是激活状态
            if not value.is_active:
                raise serializers.ValidationError("父级字典项必须是激活状态")
        
        return value


class DictionarySimpleSerializer(serializers.ModelSerializer):
    """字典项简化序列化器，用于下拉选择和树形展示"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = ('id', 'dict_type', 'code', 'name', 'sort_order', 'children')
    
    def get_children(self, obj):
        """获取子级项目"""
        children = obj.get_children()
        return DictionarySimpleSerializer(children, many=True).data


class DictionaryTreeSerializer(serializers.ModelSerializer):
    """字典项树形结构序列化器"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    parent_code = serializers.CharField(source='parent.code', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = ('id', 'dict_type', 'parent', 'parent_name', 'parent_code', 'code', 'name', 'description', 'sort_order', 'is_active', 'children')
    
    def get_children(self, obj):
        """递归获取子级项目"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return DictionaryTreeSerializer(children, many=True).data


class DictionaryOptionsSerializer(serializers.Serializer):
    """字典选项序列化器，用于前端下拉选择"""
    parent_code = serializers.CharField(required=False, help_text="父级字典项代码（用于获取子级选项）")