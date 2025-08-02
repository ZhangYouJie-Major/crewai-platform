from django.db import models
from .role import Role
from .permission import Permission


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