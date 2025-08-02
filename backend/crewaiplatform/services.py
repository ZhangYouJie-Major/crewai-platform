"""
服务导入文件 - 从services包中导入所有服务
为了保持向后兼容性，保留原有的导入方式
"""

# 从services包中导入所有服务
from .services import (
    AuthService,
    RBACService,
    UserService,
    RoleService,
    PermissionService,
)

# 为了向后兼容，保持原有的导入方式
__all__ = [
    'AuthService',
    'RBACService',
    'UserService',
    'RoleService',
    'PermissionService',
]