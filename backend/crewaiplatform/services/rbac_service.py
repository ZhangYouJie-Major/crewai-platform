from django.contrib.auth import get_user_model
from django.db import transaction
from ..models import Role, Permission, UserRole, RolePermission

User = get_user_model()


class RBACService:
    """权限管理相关服务"""
    
    @staticmethod
    def assign_role_to_user(user_id, role_id):
        """为用户分配角色"""
        with transaction.atomic():
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
            
            user_role, created = UserRole.objects.get_or_create(
                user=user, role=role
            )
            return user_role, created
    
    @staticmethod
    def remove_role_from_user(user_id, role_id):
        """移除用户角色"""
        UserRole.objects.filter(user_id=user_id, role_id=role_id).delete()
    
    @staticmethod
    def assign_permission_to_role(role_id, permission_id):
        """为角色分配权限"""
        with transaction.atomic():
            role = Role.objects.get(id=role_id)
            permission = Permission.objects.get(id=permission_id)
            
            role_permission, created = RolePermission.objects.get_or_create(
                role=role, permission=permission
            )
            return role_permission, created
    
    @staticmethod
    def remove_permission_from_role(role_id, permission_id):
        """移除角色权限"""
        RolePermission.objects.filter(
            role_id=role_id, permission_id=permission_id
        ).delete()
    
    @staticmethod
    def get_user_permissions(user_id):
        """获取用户所有权限"""
        return Permission.objects.filter(
            rolepermission__role__userrole__user_id=user_id
        ).distinct()
    
    @staticmethod
    def get_user_roles(user_id):
        """获取用户所有角色"""
        return Role.objects.filter(userrole__user_id=user_id)