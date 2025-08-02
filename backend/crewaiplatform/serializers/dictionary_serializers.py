"""
数据字典管理序列化器

提供字典类型、字典项的序列化器，支持树形结构管理
"""

from rest_framework import serializers
from ..models import Dictionary, DictionaryItem


class DictionarySerializer(serializers.ModelSerializer):
    """字典类型序列化器"""
    item_count = serializers.SerializerMethodField()
    parent_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Dictionary
        fields = (
            'id', 'code', 'name', 'description', 'is_active', 'sort_order',
            'item_count', 'parent_items', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'code': {'help_text': '字典代码，用于程序识别'},
            'name': {'help_text': '字典名称'},
            'description': {'help_text': '字典描述'},
            'sort_order': {'help_text': '排序顺序，数字越小越靠前'},
        }
    
    def get_item_count(self, obj):
        """获取字典项数量"""
        return obj.items.filter(is_active=True).count()
    
    def get_parent_items(self, obj):
        """获取一级字典项（无父级的项）"""
        parent_items = obj.items.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
        return DictionaryItemSimpleSerializer(parent_items, many=True).data
    
    def validate_code(self, value):
        """验证字典代码唯一性"""
        if self.instance and self.instance.code == value:
            return value
        if Dictionary.objects.filter(code=value).exists():
            raise serializers.ValidationError("字典代码已存在")
        return value
    
    def validate_name(self, value):
        """验证字典名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Dictionary.objects.filter(name=value).exists():
            raise serializers.ValidationError("字典名称已存在")
        return value


class DictionaryItemSerializer(serializers.ModelSerializer):
    """字典项序列化器"""
    dictionary_name = serializers.CharField(source='dictionary.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    full_path = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    children_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = (
            'id', 'dictionary', 'dictionary_name', 'parent', 'parent_name',
            'code', 'name', 'value', 'description', 'is_active', 'sort_order',
            'full_path', 'level', 'children_count', 'children',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'dictionary': {'help_text': '所属字典类型'},
            'parent': {'help_text': '父级字典项（用于二级结构）'},
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
        children = obj.get_children()
        return DictionaryItemSimpleSerializer(children, many=True).data
    
    def validate(self, attrs):
        """验证字典项数据"""
        dictionary = attrs['dictionary']
        parent = attrs.get('parent')
        code = attrs['code']
        
        # 验证父级字典项是否属于同一字典类型
        if parent and parent.dictionary != dictionary:
            raise serializers.ValidationError("父级字典项必须属于同一字典类型")
        
        # 验证同一字典类型下的代码唯一性
        query = DictionaryItem.objects.filter(dictionary=dictionary, code=code)
        if self.instance:
            query = query.exclude(id=self.instance.id)
        if query.exists():
            raise serializers.ValidationError("该字典类型下已存在相同代码的字典项")
        
        # 防止循环引用
        if parent and self.instance:
            current = parent
            while current:
                if current.id == self.instance.id:
                    raise serializers.ValidationError("不能设置循环引用的父级关系")
                current = current.parent
        
        return attrs
    
    def validate_parent(self, value):
        """验证父级字典项"""
        if value:
            # 确保父级字典项是激活状态
            if not value.is_active:
                raise serializers.ValidationError("父级字典项必须是激活状态")
            
            # 限制层级深度（最多两级）
            if value.parent is not None:
                raise serializers.ValidationError("不支持超过两级的字典结构")
        
        return value


class DictionaryItemSimpleSerializer(serializers.ModelSerializer):
    """字典项简化序列化器，用于下拉选择和树形展示"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = ('id', 'code', 'name', 'sort_order', 'children')
    
    def get_children(self, obj):
        """获取子级项目"""
        children = obj.get_children()
        return DictionaryItemSimpleSerializer(children, many=True).data


class DictionaryItemTreeSerializer(serializers.ModelSerializer):
    """字典项树形结构序列化器"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = DictionaryItem
        fields = ('id', 'code', 'name', 'description', 'sort_order', 'is_active', 'children')
    
    def get_children(self, obj):
        """递归获取子级项目"""
        children = obj.children.filter(is_active=True).order_by('sort_order', 'name')
        return DictionaryItemTreeSerializer(children, many=True).data


class DictionaryOptionsSerializer(serializers.Serializer):
    """字典选项序列化器，用于前端下拉选择"""
    dictionary_code = serializers.CharField(help_text="字典代码")
    parent_code = serializers.CharField(required=False, help_text="父级字典项代码（用于获取子级选项）")
    
    def validate_dictionary_code(self, value):
        """验证字典代码存在"""
        if not Dictionary.objects.filter(code=value, is_active=True).exists():
            raise serializers.ValidationError("字典类型不存在或未激活")
        return value