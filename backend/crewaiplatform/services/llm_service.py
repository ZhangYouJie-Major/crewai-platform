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
                
                # 检查是否有Agent正在使用此模型
                if llm_model.primary_agents.filter(is_active=True).exists():
                    return False, "有活跃的Agent正在使用此模型，无法删除"
                
                if llm_model.function_calling_agents.filter(is_active=True).exists():
                    return False, "有活跃的Agent将此模型用作工具调用模型，无法删除"
                
                model_name = llm_model.name
                llm_model.delete()
                
                logger.info(f"LLM模型 {model_name} 删除成功")
                return True, "LLM模型删除成功"
                
        except LLMModel.DoesNotExist:
            return False, "LLM模型不存在"
            
        except Exception as e:
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
    def get_available_models_list(model_id: int) -> Tuple[bool, str, Optional[List[str]]]:
        """
        获取可用模型列表
        
        Args:
            model_id: 模型ID
            
        Returns:
            (成功状态, 消息, 模型列表)
        """
        try:
            llm_model = LLMModel.objects.get(id=model_id)
            
            # 根据提供商获取可用模型列表
            if llm_model.provider == 'openai':
                models = LLMService._get_openai_models(llm_model)
            elif llm_model.provider == 'anthropic':
                models = LLMService._get_anthropic_models(llm_model)
            elif llm_model.provider == 'azure_openai':
                models = LLMService._get_azure_openai_models(llm_model)
            elif llm_model.provider == 'ollama':
                models = LLMService._get_ollama_models(llm_model)
            else:
                models = []
            
            # 更新模型信息
            llm_model.model_info = {'available_models': models, 'last_sync': timezone.now().isoformat()}
            llm_model.save()
            
            return True, "获取模型列表成功", models
            
        except LLMModel.DoesNotExist:
            return False, "LLM模型不存在", None
            
        except Exception as e:
            error_msg = f"获取模型列表失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    @staticmethod
    def _get_openai_models(llm_model: LLMModel) -> List[str]:
        """获取OpenAI可用模型列表"""
        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=llm_model.get_decrypted_api_key(),
                base_url=llm_model.api_base_url or None
            )
            
            models = client.models.list()
            return [model.id for model in models.data if model.id.startswith(('gpt-', 'text-', 'davinci', 'curie', 'babbage', 'ada'))]
            
        except Exception as e:
            logger.error(f"获取OpenAI模型列表失败: {str(e)}")
            return []
    
    @staticmethod
    def _get_anthropic_models(llm_model: LLMModel) -> List[str]:
        """获取Anthropic可用模型列表"""
        # Anthropic目前的可用模型（相对固定）
        return [
            'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku-20241022',
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307',
        ]
    
    @staticmethod
    def _get_azure_openai_models(llm_model: LLMModel) -> List[str]:
        """获取Azure OpenAI可用模型列表"""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=llm_model.get_decrypted_api_key(),
                azure_endpoint=llm_model.api_base_url,
                api_version=llm_model.api_version or "2024-02-01"
            )
            
            deployments = client.models.list()
            return [deployment.id for deployment in deployments.data]
            
        except Exception as e:
            logger.error(f"获取Azure OpenAI模型列表失败: {str(e)}")
            return []
    
    @staticmethod
    def _get_ollama_models(llm_model: LLMModel) -> List[str]:
        """获取Ollama可用模型列表"""
        try:
            import requests
            
            base_url = llm_model.api_base_url or "http://localhost:11434"
            response = requests.get(f"{base_url}/api/tags", timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
            
        except Exception as e:
            logger.error(f"获取Ollama模型列表失败: {str(e)}")
            return []
    
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
    
    @staticmethod
    def sync_model_info(model_id: int) -> Tuple[bool, str]:
        """
        同步模型信息
        
        Args:
            model_id: 模型ID
            
        Returns:
            (成功状态, 消息)
        """
        try:
            success, message, models = LLMService.get_available_models_list(model_id)
            if success:
                return True, f"模型信息同步成功，发现 {len(models)} 个可用模型"
            else:
                return False, f"模型信息同步失败: {message}"
                
        except Exception as e:
            error_msg = f"同步模型信息失败: {str(e)}"
            logger.error(error_msg)
            return False, error_msg