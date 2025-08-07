from rest_framework import viewsets, permissions, status
from rest_framework.response import Response  
from rest_framework.decorators import action
from django.db import models
import logging

from ..models import LLMModel, MCPTool, CrewAIAgent, AgentToolRelation
from ..serializers import (
    LLMModelSerializer, LLMModelSimpleSerializer,
    MCPToolSerializer, MCPToolSimpleSerializer,
    CrewAIAgentSerializer, CrewAIAgentSimpleSerializer,
    AgentToolRelationSerializer, AgentToolBindingSerializer,
    LLMModelStatsSerializer, MCPToolStatsSerializer, CrewAIAgentStatsSerializer
)

logger = logging.getLogger(__name__)


class LLMModelViewSet(viewsets.ModelViewSet):
    """LLM模型配置管理"""
    queryset = LLMModel.objects.all().order_by('-updated_at', '-is_active', 'name')
    serializer_class = LLMModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 可以根据查询参数过滤
        provider = self.request.query_params.get('provider')
        if provider:
            queryset = queryset.filter(provider=provider)
        
        is_available = self.request.query_params.get('is_available')
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == 'true')
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """删除LLM模型"""
        try:
            from ..services import LLMService
            
            model_id = kwargs.get('pk')
            success, message = LLMService.delete_llm_model(int(model_id))
            
            if success:
                return Response({
                    'success': True,
                    'message': message
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except ValueError:
            return Response({
                'success': False,
                'error': '无效的模型ID'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'删除操作失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def validate_connection(self, request, pk=None):
        """验证LLM模型连接"""
        try:
            model = self.get_object()
            success, message = model.validate_connection()
            
            return Response({
                'success': success,
                'message': message,
                'is_available': model.is_available,
                'last_validated': model.last_validated,
                'validation_error': model.validation_error
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """测试连接配置（用于创建前验证）"""
        try:
            from ..services import LLMService
            
            # 创建临时模型实例进行测试
            temp_data = request.data.copy()
            
            # 创建临时模型实例
            temp_model = LLMModel(**temp_data)
            
            # 验证连接
            success, message = temp_model.validate_connection()
            
            response_data = {
                'success': success,
                'message': message
            }
            
            # 如果连接成功，尝试获取可用模型列表
            if success:
                try:
                    # 保存临时模型以获取ID
                    temp_model.save()
                    success_models, message_models, models_list = LLMService.get_available_models_list(temp_model.id)
                    
                    if success_models:
                        response_data['available_models'] = models_list
                    
                    # 删除临时模型
                    temp_model.delete()
                    
                except Exception as e:
                    # 如果出错，确保删除临时模型
                    try:
                        temp_model.delete()
                    except:
                        pass
                    logger.warning(f"获取模型列表时出错: {str(e)}")
            
            return Response(response_data)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def batch_validate(self, request):
        """批量验证所有模型"""
        try:
            from ..services import LLMService
            
            success, message, results = LLMService.batch_validate_models()
            
            return Response({
                'success': success,
                'message': message,
                'total': results.get('total', 0),
                'available': results.get('available', 0),
                'failed': results.get('failed', 0),
                'details': results.get('details', [])
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取所有可用的模型"""
        available_models = LLMModel.get_available_models()
        serializer = LLMModelSimpleSerializer(available_models, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取LLM模型统计信息"""
        try:
            total_models = LLMModel.objects.count()
            available_models = LLMModel.objects.filter(is_available=True).count()
            
            # 提供商分布
            provider_dist = {}
            for choice in LLMModel.PROVIDER_CHOICES:
                provider = choice[0]
                count = LLMModel.objects.filter(provider=provider).count()
                if count > 0:
                    provider_dist[choice[1]] = count
            
            # 使用统计（这里可以扩展更多统计）
            usage_stats = {
                'active_models': LLMModel.objects.filter(is_active=True).count(),
                'models_with_errors': LLMModel.objects.exclude(validation_error='').count(),
            }
            
            stats_data = {
                'total_models': total_models,
                'available_models': available_models,
                'provider_distribution': provider_dist,
                'usage_stats': usage_stats
            }
            
            serializer = LLMModelStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MCPToolViewSet(viewsets.ModelViewSet):
    """MCP工具配置管理"""
    queryset = MCPTool.objects.all().order_by('-created_at')
    serializer_class = MCPToolSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 可以根据查询参数过滤
        server_type = self.request.query_params.get('server_type')
        if server_type:
            queryset = queryset.filter(server_type=server_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # 用户权限过滤
        user = self.request.user
        if not user.is_superuser:
            queryset = MCPTool.get_user_tools(user)
        
        return queryset
    
    @action(detail=True, methods=['post'], url_path='health-check')
    def health_check(self, request, pk=None):
        """执行工具健康检查"""
        try:
            tool = self.get_object()
            success, message, result = tool.test_connection()
            
            return Response({
                'success': success,
                'message': message,
                'result': result,
                'status': tool.status,
                'last_health_check': tool.last_health_check,
                'response_time_ms': tool.response_time_ms
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def call_tool(self, request, pk=None):
        """调用MCP工具"""
        try:
            tool = self.get_object()
            tool_name = request.data.get('tool_name')
            arguments = request.data.get('arguments', {})
            
            if not tool_name:
                return Response({
                    'error': '缺少tool_name参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success, result = tool.call_tool(tool_name, arguments)
            
            return Response({
                'success': success,
                'result': result,
                'tool_name': tool_name,
                'arguments': arguments
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def healthy(self, request):
        """获取所有健康的工具"""
        healthy_tools = MCPTool.get_healthy_tools()
        serializer = MCPToolSimpleSerializer(healthy_tools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """获取所有公开工具"""
        public_tools = MCPTool.get_public_tools()
        serializer = MCPToolSimpleSerializer(public_tools, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取MCP工具统计信息"""
        try:
            total_tools = MCPTool.objects.count()
            healthy_tools = MCPTool.objects.filter(status='healthy').count()
            
            # 服务器类型分布
            server_type_dist = {}
            for choice in MCPTool.SERVER_TYPE_CHOICES:
                server_type = choice[0]
                count = MCPTool.objects.filter(server_type=server_type).count()
                if count > 0:
                    server_type_dist[choice[1]] = count
            
            # 使用统计
            usage_stats = {
                'active_tools': MCPTool.objects.filter(is_active=True).count(),
                'public_tools': MCPTool.objects.filter(is_public=True).count(),
                'tools_with_errors': MCPTool.objects.filter(status='error').count(),
            }
            
            stats_data = {
                'total_tools': total_tools,
                'healthy_tools': healthy_tools,
                'server_type_distribution': server_type_dist,
                'usage_stats': usage_stats
            }
            
            serializer = MCPToolStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CrewAIAgentViewSet(viewsets.ModelViewSet):
    """CrewAI Agent配置管理"""
    queryset = CrewAIAgent.objects.select_related('llm_model', 'function_calling_llm', 'owner').all().order_by('-created_at')
    serializer_class = CrewAIAgentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 可以根据查询参数过滤
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # 用户权限过滤
        user = self.request.user
        if not user.is_superuser:
            queryset = CrewAIAgent.get_user_agents(user)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """启动Agent"""
        try:
            agent = self.get_object()
            success, message = agent.start()
            
            return Response({
                'success': success,
                'message': message,
                'status': agent.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """停止Agent"""
        try:
            agent = self.get_object()
            success, message = agent.stop()
            
            return Response({
                'success': success,
                'message': message,
                'status': agent.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """暂停Agent"""
        try:
            agent = self.get_object()
            success, message = agent.pause()
            
            return Response({
                'success': success,
                'message': message,
                'status': agent.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """恢复Agent"""
        try:
            agent = self.get_object()
            success, message = agent.resume()
            
            return Response({
                'success': success,
                'message': message,
                'status': agent.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def execute_task(self, request, pk=None):
        """执行任务"""
        try:
            agent = self.get_object()
            task_description = request.data.get('task_description')
            context = request.data.get('context')
            
            if not task_description:
                return Response({
                    'error': '缺少task_description参数'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success, result = agent.execute_task(task_description, context)
            
            return Response({
                'success': success,
                'result': result,
                'task_description': task_description,
                'status': agent.status,
                'total_tasks': agent.total_tasks,
                'completed_tasks': agent.completed_tasks
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def tools(self, request, pk=None):
        """获取Agent绑定的工具"""
        try:
            agent = self.get_object()
            relations = AgentToolRelation.get_agent_tools(agent)
            serializer = AgentToolRelationSerializer(relations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def bind_tools(self, request, pk=None):
        """批量绑定工具"""
        try:
            agent = self.get_object()
            serializer = AgentToolBindingSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            tool_ids = serializer.validated_data['tool_ids']
            permission_level = serializer.validated_data['permission_level']
            
            # 批量创建关联
            created_relations = []
            for tool_id in tool_ids:
                try:
                    tool = MCPTool.objects.get(id=tool_id, is_active=True)
                    relation, created = AgentToolRelation.objects.get_or_create(
                        agent=agent,
                        tool=tool,
                        defaults={'permission_level': permission_level}
                    )
                    if created:
                        created_relations.append(relation)
                except MCPTool.DoesNotExist:
                    continue
            
            # 返回创建的关联
            result_serializer = AgentToolRelationSerializer(created_relations, many=True)
            return Response({
                'success': True,
                'message': f'成功绑定 {len(created_relations)} 个工具',
                'relations': result_serializer.data
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取所有活跃的Agent"""
        active_agents = CrewAIAgent.get_active_agents()
        serializer = CrewAIAgentSimpleSerializer(active_agents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def public(self, request):
        """获取所有公开Agent"""
        public_agents = CrewAIAgent.get_public_agents()
        serializer = CrewAIAgentSimpleSerializer(public_agents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取Agent统计信息"""
        try:
            total_agents = CrewAIAgent.objects.count()
            active_agents = CrewAIAgent.objects.filter(status__in=['active', 'running']).count()
            
            # 任务统计
            task_stats = {
                'total_tasks': CrewAIAgent.objects.aggregate(
                    total=models.Sum('total_tasks'))['total'] or 0,
                'completed_tasks': CrewAIAgent.objects.aggregate(
                    completed=models.Sum('completed_tasks'))['completed'] or 0,
            }
            if task_stats['total_tasks'] > 0:
                task_stats['success_rate'] = (task_stats['completed_tasks'] / task_stats['total_tasks']) * 100
            else:
                task_stats['success_rate'] = 0
            
            # 性能统计
            performance_stats = {
                'agents_with_tasks': CrewAIAgent.objects.filter(total_tasks__gt=0).count(),
                'agents_with_errors': CrewAIAgent.objects.exclude(last_error='').count(),
            }
            
            stats_data = {
                'total_agents': total_agents,
                'active_agents': active_agents,
                'task_stats': task_stats,
                'performance_stats': performance_stats
            }
            
            serializer = CrewAIAgentStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgentToolRelationViewSet(viewsets.ModelViewSet):
    """Agent-Tool关联管理"""
    queryset = AgentToolRelation.objects.select_related('agent', 'tool').all().order_by('agent', 'order')
    serializer_class = AgentToolRelationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        
        # 可以根据查询参数过滤
        agent_id = self.request.query_params.get('agent_id')
        if agent_id:
            queryset = queryset.filter(agent_id=agent_id)
        
        tool_id = self.request.query_params.get('tool_id')
        if tool_id:
            queryset = queryset.filter(tool_id=tool_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    def destroy(self, request, *args, **kwargs):
        """解绑Agent-Tool"""
        try:
            relation_id = kwargs.get('pk')
            relation = AgentToolRelation.objects.get(id=relation_id)
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AgentToolRelation.DoesNotExist:
            return Response({
                'success': False,
                'error': '指定的关联不存在或无权访问。'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'解绑失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def agent_tools(self, request):
        """
            获取指定Agent的所有工具关联（包含详细工具信息）
        """
        agent_id = request.query_params.get('agent_id')
        if not agent_id:
            return Response({'error': '缺少agent_id参数'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            relations = AgentToolRelation.objects.filter(agent_id=agent_id).select_related('tool')
            serializer = AgentToolRelationSerializer(relations, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """测试工具连接"""
        try:
            relation = self.get_object()
            success, message = relation.test_connection()
            
            return Response({
                'success': success,
                'message': message,
                'status': relation.status,
                'last_error': relation.last_error
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """激活关联"""
        try:
            relation = self.get_object()
            success, message = relation.activate()
            
            return Response({
                'success': success,
                'message': message,
                'status': relation.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """停用关联"""
        try:
            relation = self.get_object()
            success, message = relation.deactivate()
            
            return Response({
                'success': success,
                'message': message,
                'status': relation.status
            })
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def high_usage(self, request):
        """获取高使用频率的关联"""
        min_calls = int(request.query_params.get('min_calls', 100))
        relations = AgentToolRelation.get_high_usage_relations(min_calls)
        serializer = self.get_serializer(relations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def problematic(self, request):
        """获取问题关联（成功率低）"""
        max_success_rate = float(request.query_params.get('max_success_rate', 80))
        relations = AgentToolRelation.get_problematic_relations(max_success_rate)
        serializer = self.get_serializer(relations, many=True)
        return Response(serializer.data)