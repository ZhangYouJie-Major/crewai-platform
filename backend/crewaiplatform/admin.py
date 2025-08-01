from django.contrib import admin
from .models import User, Role, Permission, UserRole, RolePermission

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """用户管理"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """角色管理"""
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """权限管理"""
    list_display = ('name', 'codename', 'description', 'created_at')
    search_fields = ('name', 'codename', 'description')
    list_filter = ('created_at',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """用户角色关联管理"""
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__username', 'role__name')

@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """角色权限关联管理"""
    list_display = ('role', 'permission', 'assigned_at')
    list_filter = ('role', 'assigned_at')
    search_fields = ('role__name', 'permission__name')