"""
LLM模型服务 - 提供LLM模型管理和验证功能

主要功能：
- LLM模型的创建、更新、删除
- API连接验证和模型可用性检测
- 模型信息的动态获取和同步
- 批量操作和状态管理
"""

from typing import Dict, List, Tuple, Optional, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from ..models import LLMModel
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM模型管理服务"""
    
    @staticmethod
    def create_llm_model(data: Dict[str, Any]) -> Tuple[bool, str, Optional[LLMModel]]:
        """
        创建LLM模型配置
        
        Args:
            data: 模型配置数据
            
        Returns:
            (成功状态, 消息, 模型实例)
        """
        try:
            with transaction.atomic():
                # 创建模型实例
                llm_model = LLMModel(**data)
                llm_model.full_clean()  # 验证数据
                llm_model.save()
                
                # 尝试验证连接
                try:
                    success, message = llm_model.validate_connection()
                    if success:
                        logger.info(f"LLM模型 {llm_model.name} 创建成功并验证通过")
                    else:
                        logger.warning(f"LLM模型 {llm_model.name} 创建成功但验证失败: {message}")
                except Exception as e:
                    logger.warning(f"LLM模型 {llm_model.name} 创建成功但验证时出错: {str(e)}")
                
                return True, "LLM模型创建成功", llm_model
                
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"创建LLM模型失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def update_llm_model(model_id: int, data: Dict[str, Any]) -> Tuple[bool, str, Optional[LLMModel]]:
        """
        更新LLM模型配置
        
        Args:
            model_id: 模型ID
            data: 更新数据
            
        Returns:
            (成功状态, 消息, 模型实例)
        """
        try:
            with transaction.atomic():
                llm_model = LLMModel.objects.get(id=model_id)
                
                # 更新字段
                for field, value in data.items():
                    if hasattr(llm_model, field):
                        setattr(llm_model, field, value)
                
                llm_model.full_clean()  # 验证数据
                llm_model.save()
                
                # 如果API配置有变化，重新验证连接
                critical_fields = ['api_key', 'api_base_url', 'model_name', 'provider']
                if any(field in data for field in critical_fields):
                    try:
                        success, message = llm_model.validate_connection()
                        if not success:
                            logger.warning(f"LLM模型 {llm_model.name} 更新后验证失败: {message}")
                    except Exception as e:
                        logger.warning(f"LLM模型 {llm_model.name} 更新后验证时出错: {str(e)}")
                
                return True, "LLM模型更新成功", llm_model
                
        except LLMModel.DoesNotExist:
            return False, "LLM模型不存在", None
            
        except ValidationError as e:
            error_msg = f"数据验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
            
        except Exception as e:
            error_msg = f"更新LLM模型失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def delete_llm_model(model_id: int) -> Tuple[bool, str]:
        """
        删除LLM模型
        
        Args:
            model_id: 模型ID
            
        Returns:
            (成功状态, 消息)
        """
        try:
            with transaction.atomic():
                llm_model = LLMModel.objects.get(id=model_id)
                
                # 检查是否有Agent正在使用此模型作为主要模型
                primary_agents = llm_model.primary_agents.filter(is_active=True)
                if primary_agents.exists():
                    agent_names = [agent.display_name for agent in primary_agents[:3]]
                    if primary_agents.count() > 3:
                        agent_names.append(f"等{primary_agents.count()}个")
                    return False, f"有活跃的Agent正在使用此模型作为主要模型：{', '.join(agent_names)}，无法删除"
                
                # 检查是否有Agent正在使用此模型作为工具调用模型  
                function_calling_agents = llm_model.function_calling_agents.filter(is_active=True)
                if function_calling_agents.exists():
                    agent_names = [agent.display_name for agent in function_calling_agents[:3]]
                    if function_calling_agents.count() > 3:
                        agent_names.append(f"等{function_calling_agents.count()}个")
                    return False, f"有活跃的Agent正在使用此模型作为工具调用模型：{', '.join(agent_names)}，无法删除"
                
                # 检查是否有非活跃的Agent仍在引用此模型
                all_primary_agents = llm_model.primary_agents.all()
                all_function_calling_agents = llm_model.function_calling_agents.all()
                
                if all_primary_agents.exists() or all_function_calling_agents.exists():
                    total_agents = all_primary_agents.count() + all_function_calling_agents.count()
                    return False, f"仍有{total_agents}个Agent引用此模型，请先解除关联或删除相关Agent后再删除此模型"
                
                model_name = llm_model.name
                llm_model.delete()
                
                logger.info(f"LLM模型 {model_name} 删除成功")
                return True, "LLM模型删除成功"
                
        except LLMModel.DoesNotExist:
            return False, "LLM模型不存在"
            
        except Exception as e:
            # 捕获Django的ProtectedError异常
            from django.db.models.deletion import ProtectedError
            if isinstance(e, ProtectedError):
                # 解析受保护的对象
                protected_objects = e.args[1]
                if protected_objects:
                    agent_names = [str(obj) for obj in list(protected_objects)[:3]]
                    if len(protected_objects) > 3:
                        agent_names.append(f"等{len(protected_objects)}个")
                    return False, f"无法删除模型，有Agent正在引用：{', '.join(agent_names)}"
                else:
                    return False, "无法删除模型，存在关联的Agent"
            
            error_msg = f"删除LLM模型失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    @staticmethod
    def validate_model_connection(model_id: int) -> Tuple[bool, str]:
        """
        验证模型连接
        
        Args:
            model_id: 模型ID
            
        Returns:
            (成功状态, 消息)
        """
        try:
            llm_model = LLMModel.objects.get(id=model_id)
            return llm_model.validate_connection()
            
        except LLMModel.DoesNotExist:
            return False, "LLM模型不存在"
            
        except Exception as e:
            error_msg = f"验证模型连接失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    
    
    @staticmethod
    def batch_validate_models() -> Tuple[bool, str, Dict[str, Any]]:
        """
        批量验证所有活跃模型
        
        Returns:
            (成功状态, 消息, 验证结果)
        """
        try:
            active_models = LLMModel.objects.filter(is_active=True)
            results = {
                'total': active_models.count(),
                'validated': 0,
                'available': 0,
                'failed': 0,
                'details': []
            }
            
            for model in active_models:
                try:
                    success, message = model.validate_connection()
                    results['validated'] += 1
                    
                    if success:
                        results['available'] += 1
                        status = 'available'
                    else:
                        results['failed'] += 1
                        status = 'failed'
                    
                    results['details'].append({
                        'id': model.id,
                        'name': model.name,
                        'provider': model.provider,
                        'status': status,
                        'message': message
                    })
                    
                except Exception as e:
                    results['failed'] += 1
                    results['details'].append({
                        'id': model.id,
                        'name': model.name,
                        'provider': model.provider,
                        'status': 'error',
                        'message': str(e)
                    })
            
            logger.info(f"批量验证完成: {results['available']}/{results['total']} 模型可用")
            return True, "批量验证完成", results
            
        except Exception as e:
            error_msg = f"批量验证失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, {}
    
    @staticmethod
    def get_models_by_provider(provider: str) -> List[LLMModel]:
        """
        根据提供商获取模型列表
        
        Args:
            provider: 提供商名称
            
        Returns:
            模型列表
        """
        return LLMModel.get_models_by_provider(provider)
    
    @staticmethod
    def get_available_models() -> List[LLMModel]:
        """
        获取所有可用模型
        
        Returns:
            可用模型列表
        """
        return LLMModel.get_available_models()
    
    @staticmethod
    def get_model_statistics() -> Dict[str, Any]:
        """
        获取模型统计信息
        
        Returns:
            统计信息字典
        """
        try:
            from django.db.models import Count, Q
            
            stats = {
                'total_models': LLMModel.objects.count(),
                'active_models': LLMModel.objects.filter(is_active=True).count(),
                'available_models': LLMModel.objects.filter(is_active=True, is_available=True).count(),
                'by_provider': {},
                'recent_validations': LLMModel.objects.filter(
                    last_validated__isnull=False
                ).order_by('-last_validated')[:5].values(
                    'id', 'name', 'provider', 'is_available', 'last_validated'
                )
            }
            
            # 按提供商统计
            provider_stats = LLMModel.objects.values('provider').annotate(
                total=Count('id'),
                active=Count('id', filter=Q(is_active=True)),
                available=Count('id', filter=Q(is_active=True, is_available=True))
            )
            
            for stat in provider_stats:
                stats['by_provider'][stat['provider']] = {
                    'total': stat['total'],
                    'active': stat['active'],
                    'available': stat['available']
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取模型统计信息失败: {str(e)}")
            return {}
    
