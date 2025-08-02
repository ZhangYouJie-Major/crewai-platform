from django.db import models


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