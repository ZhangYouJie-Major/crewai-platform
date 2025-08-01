from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserRole, RolePermission

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        help_text="密码至少8位字符"
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ("id", "username", "password", "password_confirm", "email", "first_name", "last_name")
        extra_kwargs = {
            'username': {'help_text': '用户名，用于登录'},
            'email': {'help_text': '邮箱地址'},
            'first_name': {'help_text': '名字'},
            'last_name': {'help_text': '姓氏'},
        }

    def validate_username(self, value):
        """验证用户名唯一性"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已存在")
        return value

    def validate_password(self, value):
        """基础密码验证 - 复杂验证已移至前端"""
        if len(value) < 8:
            raise serializers.ValidationError("密码至少需要8位字符")
        return value

    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        attrs.pop('password_confirm')
        return attrs

    def create(self, validated_data):
        """创建新用户"""
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    full_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", "full_name",
            "is_active", "is_staff", "is_superuser", "date_joined", "roles", "phone"
        )
        read_only_fields = ("id", "username", "date_joined")

    def get_full_name(self, obj):
        """获取用户全名"""
        return f"{obj.last_name}{obj.first_name}".strip()

    def get_roles(self, obj):
        """获取用户角色列表"""
        roles = Role.objects.filter(userrole__user=obj)
        return RoleSerializer(roles, many=True).data

class RoleSerializer(serializers.ModelSerializer):
    """角色序列化器"""
    user_count = serializers.SerializerMethodField()
    permission_count = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ("id", "name", "description", "user_count", "permission_count", "permissions", "created_at")
        extra_kwargs = {
            'name': {'help_text': '角色名称'},
            'description': {'help_text': '角色描述'},
        }

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.userrole_set.count()

    def get_permission_count(self, obj):
        """获取该角色拥有的权限数量"""
        return obj.rolepermission_set.count()

    def get_permissions(self, obj):
        """获取角色权限列表"""
        permissions = Permission.objects.filter(rolepermission__role=obj)
        return PermissionSerializer(permissions, many=True).data

    def validate_name(self, value):
        """验证角色名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("角色名称已存在")
        return value

class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""
    role_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ("id", "name", "codename", "description", "role_count", "created_at")
        extra_kwargs = {
            'name': {'help_text': '权限名称'},
            'codename': {'help_text': '权限代码'},
            'description': {'help_text': '权限描述'},
        }

    def get_role_count(self, obj):
        """获取拥有该权限的角色数量"""
        return obj.rolepermission_set.count()

    def validate_name(self, value):
        """验证权限名称唯一性"""
        if self.instance and self.instance.name == value:
            return value
        if Permission.objects.filter(name=value).exists():
            raise serializers.ValidationError("权限名称已存在")
        return value

    def validate_codename(self, value):
        """验证权限代码唯一性"""
        if self.instance and self.instance.codename == value:
            return value
        if Permission.objects.filter(codename=value).exists():
            raise serializers.ValidationError("权限代码已存在")
        return value

class UserRoleSerializer(serializers.ModelSerializer):
    """用户角色关联序列化器"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ("id", "user", "role", "user_username", "role_name", "assigned_at")
        extra_kwargs = {
            'user': {'help_text': '用户ID'},
            'role': {'help_text': '角色ID'},
        }

    def validate(self, attrs):
        """验证用户角色关联的唯一性"""
        user = attrs['user']
        role = attrs['role']
        
        if self.instance is None:
            if UserRole.objects.filter(user=user, role=role).exists():
                raise serializers.ValidationError("用户已拥有该角色")
        
        return attrs

class RolePermissionSerializer(serializers.ModelSerializer):
    """角色权限关联序列化器"""
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = ("id", "role", "permission", "role_name", "permission_name", "assigned_at")
        extra_kwargs = {
            'role': {'help_text': '角色ID'},
            'permission': {'help_text': '权限ID'},
        }

    def validate(self, attrs):
        """验证角色权限关联的唯一性"""
        role = attrs['role']
        permission = attrs['permission']
        
        if self.instance is None:
            if RolePermission.objects.filter(role=role, permission=permission).exists():
                raise serializers.ValidationError("角色已拥有该权限")
        
        return attrs