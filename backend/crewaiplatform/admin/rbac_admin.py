"""
RBAC权限管理 - Django Admin配置

包含用户、角色、权限等RBAC相关模型的管理配置
"""

from django.contrib import admin
from ..models import User, Role, Permission, UserRole, RolePermission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """用户管理"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone')
        }),
        ('权限状态', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('时间信息', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        })
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    
    fieldsets = (
        ('角色信息', {
            'fields': ('name', 'description')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """权限管理"""
    list_display = ('name', 'codename', 'description', 'created_at')
    search_fields = ('name', 'codename', 'description')
    list_filter = ('created_at',)
    
    fieldsets = (
        ('权限信息', {
            'fields': ('name', 'codename', 'description')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """用户角色关联管理"""
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__username', 'role__name')
    
    fieldsets = (
        ('关联信息', {
            'fields': ('user', 'role')
        }),
        ('时间信息', {
            'fields': ('assigned_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """角色权限关联管理"""
    list_display = ('role', 'permission', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('role__name', 'permission__name')
    
    fieldsets = (
        ('关联信息', {
            'fields': ('role', 'permission')
        }),
        ('时间信息', {
            'fields': ('assigned_at',),
            'classes': ('collapse',)
        })
    ) 