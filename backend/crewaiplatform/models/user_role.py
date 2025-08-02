from django.db import models
from .user import User
from .role import Role


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