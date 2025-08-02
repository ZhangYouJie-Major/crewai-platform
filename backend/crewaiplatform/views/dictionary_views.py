from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import logging

from ..models import Dictionary, DictionaryItem
from ..serializers import (
    DictionarySerializer, DictionaryItemSerializer, DictionaryItemSimpleSerializer,
    DictionaryItemTreeSerializer, DictionaryOptionsSerializer
)

logger = logging.getLogger(__name__)


class DictionaryViewSet(viewsets.ModelViewSet):
    """字典类型管理ViewSet"""
    queryset = Dictionary.objects.all().order_by('sort_order', 'created_at')
    serializer_class = DictionarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 根据激活状态过滤
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 根据代码搜索
        code = self.request.query_params.get('code')
        if code:
            queryset = queryset.filter(code__icontains=code)
        
        # 根据名称搜索
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """获取字典的所有项目"""
        try:
            dictionary = self.get_object()
            
            # 获取查询参数
            parent_only = request.query_params.get('parent_only', 'false').lower() == 'true'
            tree_format = request.query_params.get('tree_format', 'false').lower() == 'true'
            
            if parent_only:
                # 只获取一级项目（无父级的项目）
                items = dictionary.items.filter(parent__isnull=True, is_active=True).order_by('sort_order', 'name')
            else:
                # 获取所有项目
                items = dictionary.items.filter(is_active=True).order_by('sort_order', 'name')
            
            if tree_format:
                # 树形结构返回
                serializer = DictionaryItemTreeSerializer(items, many=True)
            else:
                # 列表结构返回
                serializer = DictionaryItemSimpleSerializer(items, many=True)
            
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取字典项目失败: {str(e)}")
            return Response({
                'error': f'获取字典项目失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def options(self, request):
        """获取字典选项，用于前端下拉选择"""
        try:
            dictionary_code = request.query_params.get('code')
            parent_code = request.query_params.get('parent_code')
            
            if not dictionary_code:
                return Response({
                    'error': '缺少字典代码参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取字典类型
            try:
                dictionary = Dictionary.objects.get(code=dictionary_code, is_active=True)
            except Dictionary.DoesNotExist:
                return Response({
                    'error': '字典类型不存在或未激活'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 构建查询条件
            query = {'dictionary': dictionary, 'is_active': True}
            
            if parent_code:
                # 获取指定父级下的子项目
                try:
                    parent = DictionaryItem.objects.get(
                        dictionary=dictionary, 
                        code=parent_code, 
                        is_active=True
                    )
                    query['parent'] = parent
                except DictionaryItem.DoesNotExist:
                    return Response({
                        'error': '父级字典项不存在或未激活'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # 获取一级项目（无父级）
                query['parent__isnull'] = True
            
            # 查询字典项
            items = DictionaryItem.objects.filter(**query).order_by('sort_order', 'name')
            serializer = DictionaryItemSimpleSerializer(items, many=True)
            
            return Response({
                'dictionary': {
                    'code': dictionary.code,
                    'name': dictionary.name
                },
                'items': serializer.data
            })
        except Exception as e:
            logger.error(f"获取字典选项失败: {str(e)}")
            return Response({
                'error': f'获取字典选项失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取字典统计信息"""
        try:
            total_dictionaries = Dictionary.objects.count()
            active_dictionaries = Dictionary.objects.filter(is_active=True).count()
            total_items = DictionaryItem.objects.count()
            active_items = DictionaryItem.objects.filter(is_active=True).count()
            
            # 字典类型分布
            dictionary_distribution = {}
            dictionaries = Dictionary.objects.filter(is_active=True)
            for dictionary in dictionaries:
                item_count = dictionary.items.filter(is_active=True).count()
                dictionary_distribution[dictionary.name] = item_count
            
            return Response({
                'total_dictionaries': total_dictionaries,
                'active_dictionaries': active_dictionaries,
                'total_items': total_items,
                'active_items': active_items,
                'dictionary_distribution': dictionary_distribution,
            })
        except Exception as e:
            logger.error(f"获取字典统计信息失败: {str(e)}")
            return Response({
                'error': f'获取字典统计信息失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DictionaryItemViewSet(viewsets.ModelViewSet):
    """字典项管理ViewSet"""
    queryset = DictionaryItem.objects.all().order_by('sort_order', 'created_at')
    serializer_class = DictionaryItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 根据字典类型过滤
        dictionary_id = self.request.query_params.get('dictionary_id')
        if dictionary_id:
            queryset = queryset.filter(dictionary_id=dictionary_id)
        
        dictionary_code = self.request.query_params.get('dictionary_code')
        if dictionary_code:
            queryset = queryset.filter(dictionary__code=dictionary_code)
        
        # 根据父级过滤
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        elif self.request.query_params.get('parent_only', 'false').lower() == 'true':
            queryset = queryset.filter(parent__isnull=True)
        
        # 根据激活状态过滤
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # 根据代码搜索
        code = self.request.query_params.get('code')
        if code:
            queryset = queryset.filter(code__icontains=code)
        
        # 根据名称搜索
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取字典项的子项目"""
        try:
            parent = self.get_object()
            children = parent.get_children()
            serializer = DictionaryItemSimpleSerializer(children, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"获取子项目失败: {str(e)}")
            return Response({
                'error': f'获取子项目失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_create(self, request):
        """批量创建字典项"""
        try:
            items_data = request.data.get('items', [])
            if not items_data:
                return Response({
                    'error': '缺少字典项数据'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            created_items = []
            errors = []
            
            for item_data in items_data:
                serializer = self.get_serializer(data=item_data)
                if serializer.is_valid():
                    item = serializer.save()
                    created_items.append(serializer.data)
                else:
                    errors.append({
                        'data': item_data,
                        'errors': serializer.errors
                    })
            
            return Response({
                'success': True,
                'created_count': len(created_items),
                'created_items': created_items,
                'error_count': len(errors),
                'errors': errors
            })
        except Exception as e:
            logger.error(f"批量创建字典项失败: {str(e)}")
            return Response({
                'error': f'批量创建字典项失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取树形结构的字典项"""
        try:
            dictionary_code = request.query_params.get('dictionary_code')
            if not dictionary_code:
                return Response({
                    'error': '缺少字典代码参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                dictionary = Dictionary.objects.get(code=dictionary_code, is_active=True)
            except Dictionary.DoesNotExist:
                return Response({
                    'error': '字典类型不存在或未激活'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 获取一级项目（根节点）
            root_items = DictionaryItem.objects.filter(
                dictionary=dictionary, 
                parent__isnull=True, 
                is_active=True
            ).order_by('sort_order', 'name')
            
            serializer = DictionaryItemTreeSerializer(root_items, many=True)
            
            return Response({
                'dictionary': {
                    'code': dictionary.code,
                    'name': dictionary.name
                },
                'tree': serializer.data
            })
        except Exception as e:
            logger.error(f"获取树形结构失败: {str(e)}")
            return Response({
                'error': f'获取树形结构失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)