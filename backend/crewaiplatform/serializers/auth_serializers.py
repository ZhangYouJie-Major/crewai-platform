"""
认证相关序列化器

提供用户注册、登录、用户信息管理的序列化器
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

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
        from .rbac_serializers import RoleSerializer
        from ..models import Role
        
        roles = Role.objects.filter(userrole__user=obj)
        return RoleSerializer(roles, many=True).data