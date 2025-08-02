from django.db import models


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