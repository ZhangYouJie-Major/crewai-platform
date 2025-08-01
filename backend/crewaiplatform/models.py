from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    用户模型 - 扩展Django默认用户模型
    继承AbstractUser获得用户名、密码、邮箱等基本字段
    """
    phone = models.CharField(max_length=11, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, verbose_name='头像')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'auth_user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

class Role(models.Model):
    """
    角色模型 - 定义系统中的角色
    """
    name = models.CharField(
        max_length=64, 
        unique=True,
        verbose_name='角色名称',
        help_text='角色的唯一标识名称'
    )
    description = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='角色描述',
        help_text='角色的详细描述信息'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_role'
        verbose_name = '角色'
        verbose_name_plural = '角色'
        ordering = ['name']

    def __str__(self):
        return self.name

class Permission(models.Model):
    """
    权限模型 - 定义系统中的权限
    """
    name = models.CharField(
        max_length=64, 
        unique=True,
        verbose_name='权限名称',
        help_text='权限的显示名称'
    )
    codename = models.CharField(
        max_length=100, 
        unique=True,
        verbose_name='权限代码',
        help_text='权限的唯一标识代码，用于程序中的权限检查'
    )
    description = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='权限描述',
        help_text='权限的详细描述信息'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'sys_permission'
        verbose_name = '权限'
        verbose_name_plural = '权限'
        ordering = ['name']

    def __str__(self):
        return self.name

class UserRole(models.Model):
    """
    用户角色关联模型 - 用户与角色的多对多关系
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='用户',
        help_text='关联的用户'
    )
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE,
        verbose_name='角色',
        help_text='关联的角色'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='分配时间')

    class Meta:
        db_table = 'sys_user_role'
        verbose_name = '用户角色关联'
        verbose_name_plural = '用户角色关联'
        unique_together = ('user', 'role')
        ordering = ['user__username', 'role__name']

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

class RolePermission(models.Model):
    """
    角色权限关联模型 - 角色与权限的多对多关系
    """
    role = models.ForeignKey(
        Role, 
        on_delete=models.CASCADE,
        verbose_name='角色',
        help_text='关联的角色'
    )
    permission = models.ForeignKey(
        Permission, 
        on_delete=models.CASCADE,
        verbose_name='权限',
        help_text='关联的权限'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='分配时间')

    class Meta:
        db_table = 'sys_role_permission'
        verbose_name = '角色权限关联'
        verbose_name_plural = '角色权限关联'
        unique_together = ('role', 'permission')
        ordering = ['role__name', 'permission__name']

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"