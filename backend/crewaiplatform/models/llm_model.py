"""
LLM模型配置 - 基于LangChain框架的大语言模型管理

支持的LangChain模型类型:
- ChatOpenAI (OpenAI GPT系列)
- ChatAnthropic (Claude系列) 
- AzureChatOpenAI (Azure OpenAI)
- ChatOllama (本地Ollama模型)
- 其他LangChain兼容模型
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from cryptography.fernet import Fernet
from django.conf import settings
import json


class LLMModel(models.Model):
    """
    LLM模型配置表
    基于LangChain框架，支持多种大语言模型提供商
    """
    
    # LangChain支持的主要模型提供商
    PROVIDER_CHOICES = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic (Claude)'),
        ('azure_openai', 'Azure OpenAI'),
        ('ollama', 'Ollama (本地)'),
        ('huggingface', 'HuggingFace'),
        ('google', 'Google (PaLM/Gemini)'),
        ('cohere', 'Cohere'),
        ('custom', '自定义'),
    ]
    
    # 基本信息
    name = models.CharField(
        max_length=64, 
        unique=True,
        verbose_name="模型名称",
        help_text="显示名称，用于界面展示"
    )
    
    provider = models.CharField(
        max_length=32,
        choices=PROVIDER_CHOICES,
        verbose_name="提供商",
        help_text="LangChain支持的模型提供商"
    )
    
    model_name = models.CharField(
        max_length=128,
        verbose_name="模型标识",
        help_text="LangChain中的模型名称，如 gpt-4, claude-3-sonnet"
    )
    
    description = models.TextField(
        blank=True,
        verbose_name="模型描述",
        help_text="模型的详细描述信息"
    )
    
    # LangChain连接配置
    langchain_class = models.CharField(
        max_length=128,
        verbose_name="LangChain类名",
        help_text="对应的LangChain模型类，如 ChatOpenAI, ChatAnthropic",
        default="ChatOpenAI"
    )
    
    api_base_url = models.URLField(
        blank=True,
        verbose_name="API基础URL",
        help_text="自定义API端点，为空则使用默认"
    )
    
    api_key = models.TextField(
        verbose_name="API密钥",
        help_text="加密存储的API密钥"
    )
    
    api_version = models.CharField(
        max_length=16,
        blank=True,
        verbose_name="API版本",
        help_text="API版本号，主要用于Azure OpenAI"
    )
    
    # LangChain模型参数
    temperature = models.FloatField(
        default=0.7,
        validators=[MinValueValidator(0.0), MaxValueValidator(2.0)],
        verbose_name="温度参数",
        help_text="控制生成文本的随机性，0-2之间"
    )
    
    max_tokens = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1)],
        verbose_name="最大Token数",
        help_text="单次生成的最大token数量"
    )
    
    timeout = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(300)],
        verbose_name="超时时间",
        help_text="API请求超时时间（秒）"
    )
    
    max_retries = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name="最大重试次数",
        help_text="API请求失败时的重试次数"
    )
    
    # 扩展配置
    extra_kwargs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="额外参数",
        help_text="LangChain模型的其他参数配置"
    )
    
    model_kwargs = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="模型参数",
        help_text="传递给模型的额外参数"
    )
    
    # 模型信息（从API获取）
    model_info = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="模型信息",
        help_text="从API动态获取的模型详细信息"
    )
    
    # 状态信息
    last_validated = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="最后验证时间",
        help_text="最后一次成功连接验证的时间"
    )
    
    is_available = models.BooleanField(
        default=False,
        verbose_name="是否可用",
        help_text="模型连接状态，通过API验证确定"
    )
    
    validation_error = models.TextField(
        blank=True,
        verbose_name="验证错误",
        help_text="最后一次验证失败的错误信息"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="是否启用",
        help_text="是否在系统中启用此模型"
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="创建时间"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="更新时间"
    )
    
    class Meta:
        db_table = 'llm_model'
        verbose_name = 'LLM模型配置'
        verbose_name_plural = 'LLM模型配置'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_available']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.provider})"
    
    def save(self, *args, **kwargs):
        """保存时加密API密钥"""
        if self.api_key and not self._is_encrypted(self.api_key):
            self.api_key = self._encrypt_api_key(self.api_key)
        super().save(*args, **kwargs)
    
    def get_decrypted_api_key(self):
        """获取解密后的API密钥"""
        if self.api_key:
            return self._decrypt_api_key(self.api_key)
        return None
    
    def _is_encrypted(self, value):
        """检查值是否已加密"""
        try:
            # 尝试解密，如果成功说明已加密
            self._decrypt_api_key(value)
            return True
        except:
            return False
    
    def _encrypt_api_key(self, api_key):
        """加密API密钥"""
        try:
            # 使用Django的SECRET_KEY生成加密密钥
            key = self._get_encryption_key()
            f = Fernet(key)
            encrypted_key = f.encrypt(api_key.encode())
            return encrypted_key.decode()
        except Exception as e:
            raise ValueError(f"加密API密钥失败: {str(e)}")
    
    def _decrypt_api_key(self, encrypted_api_key):
        """解密API密钥"""
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted_key = f.decrypt(encrypted_api_key.encode())
            return decrypted_key.decode()
        except Exception as e:
            raise ValueError(f"解密API密钥失败: {str(e)}")
    
    def _get_encryption_key(self):
        """生成加密密钥"""
        from django.utils.encoding import force_bytes
        import base64
        import hashlib
        
        # 使用Django SECRET_KEY生成Fernet兼容的密钥
        secret = force_bytes(settings.SECRET_KEY)
        key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
        return key
    
    def get_langchain_config(self):
        """获取LangChain模型配置"""
        config = {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
        }
        
        # 添加API密钥
        decrypted_key = self.get_decrypted_api_key()
        if decrypted_key:
            if self.provider == 'openai':
                config['openai_api_key'] = decrypted_key
            elif self.provider == 'anthropic':
                config['anthropic_api_key'] = decrypted_key
            elif self.provider == 'azure_openai':
                config['openai_api_key'] = decrypted_key
                config['azure_endpoint'] = self.api_base_url
                config['api_version'] = self.api_version or '2024-02-01'
            else:
                config['api_key'] = decrypted_key
        
        # 添加自定义URL
        if self.api_base_url and self.provider != 'azure_openai':
            if self.provider == 'openai':
                config['openai_api_base'] = self.api_base_url
            else:
                config['base_url'] = self.api_base_url
        
        # 添加max_tokens
        if self.max_tokens:
            config['max_tokens'] = self.max_tokens
        
        # 合并额外参数
        config.update(self.extra_kwargs)
        config.update(self.model_kwargs)
        
        return config
    
    def create_langchain_model(self):
        """创建LangChain模型实例"""
        try:
            config = self.get_langchain_config()
            
            # 根据提供商创建对应的LangChain模型
            if self.provider == 'openai':
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(**config)
            
            elif self.provider == 'anthropic':
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(**config)
            
            elif self.provider == 'azure_openai':
                from langchain_openai import AzureChatOpenAI
                return AzureChatOpenAI(**config)
            
            elif self.provider == 'ollama':
                from langchain_ollama import ChatOllama
                return ChatOllama(**config)
            
            elif self.provider == 'huggingface':
                from langchain_huggingface import ChatHuggingFace
                return ChatHuggingFace(**config)
            
            elif self.provider == 'google':
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(**config)
            
            elif self.provider == 'cohere':
                from langchain_cohere import ChatCohere
                return ChatCohere(**config)
            
            else:
                # 自定义提供商，动态导入
                module_path, class_name = self.langchain_class.rsplit('.', 1)
                module = __import__(module_path, fromlist=[class_name])
                model_class = getattr(module, class_name)
                return model_class(**config)
                
        except Exception as e:
            raise ValueError(f"创建LangChain模型失败: {str(e)}")
    
    def validate_connection(self):
        """验证模型连接"""
        try:
            # 创建LangChain模型实例
            llm = self.create_langchain_model()
            
            # 发送测试消息
            from langchain_core.messages import HumanMessage
            test_message = HumanMessage(content="Hello, this is a connection test.")
            
            # 调用模型
            response = llm.invoke([test_message])
            
            # 更新状态
            from django.utils import timezone
            self.is_available = True
            self.last_validated = timezone.now()
            self.validation_error = ""
            self.save()
            
            return True, "连接成功"
            
        except Exception as e:
            # 更新错误状态
            self.is_available = False
            self.validation_error = str(e)
            self.save()
            
            return False, str(e)
    
    @classmethod
    def get_available_models(cls):
        """获取所有可用的模型"""
        return cls.objects.filter(is_active=True, is_available=True)
    
    @classmethod
    def get_models_by_provider(cls, provider):
        """根据提供商获取模型"""
        return cls.objects.filter(provider=provider, is_active=True)