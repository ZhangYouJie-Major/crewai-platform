"""
MCP工具服务 - 提供MCP工具管理和监控功能

主要功能：
- MCP工具的创建、更新、删除
- 工具连接测试和健康检查
- 工具调用和使用统计
- 批量操作和状态管理
"""

from typing import Dict, List, Tuple, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import MCPTool, User
import logging

logger = logging.getLogger(__name__)


class MCPService:
    """MCP工具管理服务"""
    
    @staticmethod
    def create_mcp_tool(data: Dict[str, Any]) -> Tuple[bool, str, Optional[MCPTool]]:
        """
        创建MCP工具配置
        
        Args:
            data: 工具配置数据
            
        Returns:
            (成功状态, 消息, 工具实例)
        """
        try:
            with transaction.atomic():
                # 创建工具实例
                mcp_tool = MCPTool(**data)
                mcp_tool.full_clean()  # 验证数据
                mcp_tool.save()
                
                # 尝试测试连接
                try:
                    success, message, _ = mcp_tool.test_connection()
                    if success:
                        logger.info(f"MCP工具 {mcp_tool.name} 创建成功并连接测试通过")
                    else:
                        logger.warning(f"MCP工具 {mcp_tool.name} 创建成功但连接测试失败: {message}")
                except Exception as e:
                    logger.warning(f"MCP工具 {mcp_tool.name} 创建成功但连接测试时出错: {str(e)}")
                
                return True, "MCP工具创建成功", mcp_tool
                
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"创建MCP工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_mcp_tool(tool_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[MCPTool]]:
        """
        更新MCP工具配置
        
        Args:
            tool_id: 工具ID
            data: 更新数据
            
        Returns:
            (成功状态, 消息, 工具实例)
        """
        try:
            with transaction.atomic():
                mcp_tool = MCPTool.objects.get(id=tool_id)
                
                # 更新字段
                for field, value in data.items():
                    if hasattr(mcp_tool, field):
                        setattr(mcp_tool, field, value)
                
                mcp_tool.full_clean()  # 验证数据
                mcp_tool.save()
                
                # 如果连接配置有变化，重新测试连接
                critical_fields = ['connection_config', 'server_type']
                if any(field in data for field in critical_fields):
                    try:
                        success, message, _ = mcp_tool.test_connection()
                        if not success:
                            logger.warning(f"MCP工具 {mcp_tool.name} 更新后连接测试失败: {message}")
                    except Exception as e:
                        logger.warning(f"MCP工具 {mcp_tool.name} 更新后连接测试时出错: {str(e)}")
                
                return True, "MCP工具更新成功", mcp_tool
                
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在", None
            
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"更新MCP工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def delete_mcp_tool(tool_id: int) -> Tuple[bool, str]:
        """
        删除MCP工具
        
        Args:
            tool_id: 工具ID
            
        Returns:
            (成功状态, 消息)
        """
        try:
            with transaction.atomic():
                mcp_tool = MCPTool.objects.get(id=tool_id)
                
                # 检查是否有Agent正在使用此工具
                if mcp_tool.tool_agent_relations.filter(status='active').exists():
                    return False, "有活跃的Agent正在使用此工具，无法删除"
                
                tool_name = mcp_tool.name
                mcp_tool.delete()
                
                logger.info(f"MCP工具 {tool_name} 删除成功")
                return True, "MCP工具删除成功"
                
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在"
            
        except Exception as e:
            error_msg = f"删除MCP工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def test_tool_connection(tool_id: int) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        测试工具连接
        
        Args:
            tool_id: 工具ID
            
        Returns:
            (成功状态, 消息, 测试结果)
        """
        try:
            mcp_tool = MCPTool.objects.get(id=tool_id)
            success, message, result = mcp_tool.test_connection()
            
            return success, message, result
            
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在", None
            
        except Exception as e:
            error_msg = f"测试工具连接失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def call_tool(tool_id: int, tool_name: str, arguments: Dict[str, Any] = None) -> Tuple[bool, Any]:
        """
        调用MCP工具
        
        Args:
            tool_id: 工具ID
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            (成功状态, 结果)
        """
        try:
            mcp_tool = MCPTool.objects.get(id=tool_id)
            return mcp_tool.call_tool(tool_name, arguments or {})
            
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在"
            
        except Exception as e:
            error_msg = f"调用工具失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def batch_health_check() -> Tuple[bool, str, Dict[str, Any]]:
        """
        批量健康检查所有活跃工具
        
        Returns:
            (成功状态, 消息, 检查结果)
        """
        try:
            active_tools = MCPTool.objects.filter(is_active=True, health_check_enabled=True)
            results = {
                'total': active_tools.count(),
                'checked': 0,
                'healthy': 0,
                'unhealthy': 0,
                'details': []
            }
            
            for tool in active_tools:
                try:
                    success, message, _ = tool.test_connection()
                    results['checked'] += 1
                    
                    if success:
                        results['healthy'] += 1
                        status = 'healthy'
                    else:
                        results['unhealthy'] += 1
                        status = 'unhealthy'
                    
                    results['details'].append({
                        'id': tool.id,
                        'name': tool.name,
                        'server_type': tool.server_type,
                        'status': status,
                        'message': message,
                        'response_time_ms': tool.response_time_ms
                    })
                    
                except Exception as e:
                    results['unhealthy'] += 1
                    results['details'].append({
                        'id': tool.id,
                        'name': tool.name,
                        'server_type': tool.server_type,
                        'status': 'error',
                        'message': str(e),
                        'response_time_ms': None
                    })
            
            logger.info(f"批量健康检查完成: {results['healthy']}/{results['total']} 工具健康")
            return True, "批量健康检查完成", results
            
        except Exception as e:
            error_msg = f"批量健康检查失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, {}
    
    @staticmethod
    def get_user_tools(user: User) -> List[MCPTool]:
        """
        获取用户可用的工具
        
        Args:
            user: 用户实例
            
        Returns:
            工具列表
        """
        return MCPTool.get_user_tools(user)
    
    @staticmethod
    def get_public_tools() -> List[MCPTool]:
        """
        获取所有公开工具
        
        Returns:
            公开工具列表
        """
        return MCPTool.get_public_tools()
    
    @staticmethod
    def get_healthy_tools() -> List[MCPTool]:
        """
        获取所有健康的工具
        
        Returns:
            健康工具列表
        """
        return MCPTool.get_healthy_tools()
    
    @staticmethod
    def get_tool_statistics() -> Dict[str, Any]:
        """
        获取工具统计信息
        
        Returns:
            统计信息字典
        """
        try:
            from django.db.models import Count, Q, Avg
            
            stats = {
                'total_tools': MCPTool.objects.count(),
                'active_tools': MCPTool.objects.filter(is_active=True).count(),
                'healthy_tools': MCPTool.objects.filter(is_active=True, status='healthy').count(),
                'public_tools': MCPTool.objects.filter(is_public=True, is_active=True).count(),
                'by_server_type': {},
                'average_response_time': MCPTool.objects.filter(
                    response_time_ms__isnull=False
                ).aggregate(avg=Avg('response_time_ms'))['avg'] or 0,
                'recent_health_checks': MCPTool.objects.filter(
                    last_health_check__isnull=False
                ).order_by('-last_health_check')[:5].values(
                    'id', 'name', 'server_type', 'status', 'last_health_check', 'response_time_ms'
                )
            }
            
            # 按服务器类型统计
            server_type_stats = MCPTool.objects.values('server_type').annotate(
                total=Count('id'),
                active=Count('id', filter=Q(is_active=True)),
                healthy=Count('id', filter=Q(is_active=True, status='healthy'))
            )
            
            for stat in server_type_stats:
                stats['by_server_type'][stat['server_type']] = {
                    'total': stat['total'],
                    'active': stat['active'],
                    'healthy': stat['healthy']
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取工具统计信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def discover_tools(tool_id: int) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        发现工具的可用功能
        
        Args:
            tool_id: 工具ID
            
        Returns:
            (成功状态, 消息, 工具功能列表)
        """
        try:
            mcp_tool = MCPTool.objects.get(id=tool_id)
            
            # 获取工具的可用功能列表
            available_tools = mcp_tool.get_available_tools()
            
            tool_details = []
            for tool_name in available_tools:
                tool_info = mcp_tool.get_tool_info(tool_name)
                if tool_info:
                    tool_details.append(tool_info)
                else:
                    tool_details.append({
                        'name': tool_name,
                        'description': f'工具: {tool_name}',
                        'inputSchema': {}
                    })
            
            return True, "工具功能发现成功", tool_details
            
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在", []
            
        except Exception as e:
            error_msg = f"发现工具功能失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, []
    
    @staticmethod
    def update_tool_schema(tool_id: int, schema: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新工具Schema
        
        Args:
            tool_id: 工具ID
            schema: 新的Schema
            
        Returns:
            (成功状态, 消息)
        """
        try:
            with transaction.atomic():
                mcp_tool = MCPTool.objects.get(id=tool_id)
                mcp_tool.tool_schema = schema
                mcp_tool.full_clean()
                mcp_tool.save()
                
                logger.info(f"MCP工具 {mcp_tool.name} Schema更新成功")
                return True, "工具Schema更新成功"
                
        except MCPTool.DoesNotExist:
            return False, "MCP工具不存在"
            
        except ValidationError as e:
            error_msg = f"Schema验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"更新工具Schema失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg