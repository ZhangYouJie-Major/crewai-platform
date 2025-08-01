from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import Role, Permission, UserRole, RolePermission

User = get_user_model()

class AuthService:
    """认证相关服务"""
    
    @staticmethod
    def register_user(username, password, email="", first_name="", last_name=""):
        """用户注册服务"""
        if User.objects.filter(username=username).exists():
            raise ValueError("用户名已存在")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        return user
    
    @staticmethod
    def login_user(username, password):
        """用户登录服务"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValueError("用户名或密码错误")
        
        if not user.is_active:
            raise ValueError("用户账户已被禁用")
        
        return user
    
    @staticmethod
    def generate_tokens(user):
        """生成JWT令牌"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }

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

class UserService:
    """用户管理服务"""
    
    @staticmethod
    def get_user_list(page=1, page_size=20):
        """获取用户列表"""
        return User.objects.all().order_by('-date_joined')
    
    @staticmethod
    def get_user_stats():
        """获取用户统计信息"""
        return {
            'total_count': User.objects.count(),
            'active_count': User.objects.filter(is_active=True).count(),
            'staff_count': User.objects.filter(is_staff=True).count(),
        }

class RoleService:
    """角色管理服务"""
    
    @staticmethod
    def get_role_list():
        """获取角色列表"""
        return Role.objects.all().order_by('name')
    
    @staticmethod
    def get_role_stats():
        """获取角色统计信息"""
        return {
            'total_count': Role.objects.count(),
        }

class PermissionService:
    """权限管理服务"""
    
    @staticmethod
    def get_permission_list():
        """获取权限列表"""
        return Permission.objects.all().order_by('name')
    
    @staticmethod
    def get_permission_stats():
        """获取权限统计信息"""
        return {
            'total_count': Permission.objects.count(),
        }