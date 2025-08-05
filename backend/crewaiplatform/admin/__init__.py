"""
Django Admin 配置包

按功能模块组织的管理后台配置：
- rbac_admin.py: 用户权限管理
- crewai_admin.py: CrewAI集成管理
- dictionary_admin.py: 字典管理
"""

from .rbac_admin import *
from .crewai_admin import *
from .dictionary_admin import * 