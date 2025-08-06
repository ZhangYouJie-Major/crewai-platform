from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
import logging

from ..models import Dictionary
from ..serializers import (
    DictionarySerializer, DictionarySimpleSerializer,
    DictionaryTreeSerializer, DictionaryOptionsSerializer
)

logger = logging.getLogger(__name__)


class DictionaryViewSet(viewsets.ModelViewSet):
    """字典项管理ViewSet"""
    queryset = Dictionary.objects.all().order_by('sort_order', 'created_at')
    serializer_class = DictionarySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """获取查询集"""
        queryset = super().get_queryset()
        
        # 根据字典类型过滤
        dict_type = self.request.query_params.get('dict_type')
        if dict_type:
            queryset = queryset.filter(dict_type=dict_type)
        
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
        
        # 总是预加载父级信息，用于显示完整路径
        queryset = queryset.select_related('parent')
        
        # 支持树形结构参数 - 只有在明确要求时才获取完整树形结构
        tree = self.request.query_params.get('tree', 'false').lower() == 'true'
        if tree:
            # 只获取根节点，子级数据通过序列化器递归获取
            queryset = queryset.filter(parent__isnull=True)
            queryset = queryset.prefetch_related('children')
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """获取字典项的子项目"""
        try:
            parent = self.get_object()
            children = parent.get_children()
            serializer = DictionarySimpleSerializer(children, many=True)
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
            # 获取字典类型参数
            dict_type = request.query_params.get('dict_type')
            
            # 构建查询条件
            query = {'parent__isnull': True, 'is_active': True}
            if dict_type:
                query['dict_type'] = dict_type
            
            # 获取一级项目（根节点）
            root_items = Dictionary.objects.filter(**query).order_by('sort_order', 'name')
            
            serializer = DictionaryTreeSerializer(root_items, many=True)
            
            return Response({
                'tree': serializer.data
            })
        except Exception as e:
            logger.error(f"获取树形结构失败: {str(e)}")
            return Response({
                'error': f'获取树形结构失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def options(self, request):
        """获取字典选项，用于前端下拉选择"""
        try:
            dict_type = request.query_params.get('dict_type')
            parent_code = request.query_params.get('parent_code')
            
            # 构建查询条件
            query = {'is_active': True}
            
            # 字典类型过滤
            if dict_type:
                query['dict_type'] = dict_type
            
            if parent_code:
                # 获取指定父级下的子项目
                try:
                    parent = Dictionary.objects.get(
                        code=parent_code,
                        is_active=True
                    )
                    if dict_type and parent.dict_type != dict_type:
                        return Response({
                            'error': f'父级字典项类型不匹配，期望：{dict_type}，实际：{parent.dict_type}'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    query['parent'] = parent
                except Dictionary.DoesNotExist:
                    return Response({
                        'error': '父级字典项不存在或未激活'
                    }, status=status.HTTP_404_NOT_FOUND)
            else:
                # 获取一级项目（无父级）
                query['parent__isnull'] = True
            
            # 查询字典项
            items = Dictionary.objects.filter(**query).order_by('sort_order', 'name')
            serializer = DictionarySimpleSerializer(items, many=True)
            
            return Response({
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
            total_items = Dictionary.objects.count()
            active_items = Dictionary.objects.filter(is_active=True).count()
            root_items = Dictionary.objects.filter(parent__isnull=True, is_active=True).count()
            child_items = Dictionary.objects.filter(parent__isnull=False, is_active=True).count()
            
            return Response({
                'total_items': total_items,
                'active_items': active_items,
                'root_items': root_items,
                'child_items': child_items,
            })
        except Exception as e:
            logger.error(f"获取字典统计信息失败: {str(e)}")
            return Response({
                'error': f'获取字典统计信息失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)