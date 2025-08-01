#!/bin/bash

# CrewAI Platform 数据库初始化脚本
# 创建初始角色和权限数据

echo "========================================="
echo "初始化CrewAI Platform数据库..."
echo "========================================="

# 切换到backend目录执行Django命令
cd "$(dirname "$0")/../backend"

# 创建超级管理员角色
echo "创建角色和权限数据..."

python manage.py shell << 'EOF'
from crewaiplatform.models import Role, Permission, RolePermission

# 创建基础角色
roles_data = [
    {'name': '超级管理员', 'description': '系统最高权限管理员'},
    {'name': '管理员', 'description': '系统管理员'},
    {'name': '用户', 'description': '普通用户'},
]

for role_data in roles_data:
    role, created = Role.objects.get_or_create(
        name=role_data['name'],
        defaults={'description': role_data['description']}
    )
    if created:
        print(f"创建角色: {role.name}")
    else:
        print(f"角色已存在: {role.name}")

# 创建基础权限
permissions_data = [
    {'name': '用户管理', 'codename': 'manage_users', 'description': '管理用户账户'},
    {'name': '角色管理', 'codename': 'manage_roles', 'description': '管理系统角色'},
    {'name': '权限管理', 'codename': 'manage_permissions', 'description': '管理系统权限'},
    {'name': '查看仪表盘', 'codename': 'view_dashboard', 'description': '查看系统仪表盘'},
    {'name': '系统配置', 'codename': 'system_config', 'description': '修改系统配置'},
]

for perm_data in permissions_data:
    permission, created = Permission.objects.get_or_create(
        codename=perm_data['codename'],
        defaults={
            'name': perm_data['name'],
            'description': perm_data['description']
        }
    )
    if created:
        print(f"创建权限: {permission.name}")
    else:
        print(f"权限已存在: {permission.name}")

# 为超级管理员分配所有权限
admin_role = Role.objects.get(name='超级管理员')
all_permissions = Permission.objects.all()

for permission in all_permissions:
    role_permission, created = RolePermission.objects.get_or_create(
        role=admin_role,
        permission=permission
    )
    if created:
        print(f"为角色 {admin_role.name} 分配权限: {permission.name}")

# 为管理员分配部分权限
manager_role = Role.objects.get(name='管理员')
manager_permissions = Permission.objects.filter(
    codename__in=['manage_users', 'view_dashboard']
)

for permission in manager_permissions:
    role_permission, created = RolePermission.objects.get_or_create(
        role=manager_role,
        permission=permission
    )
    if created:
        print(f"为角色 {manager_role.name} 分配权限: {permission.name}")

# 为普通用户分配基础权限
user_role = Role.objects.get(name='用户')
user_permissions = Permission.objects.filter(codename='view_dashboard')

for permission in user_permissions:
    role_permission, created = RolePermission.objects.get_or_create(
        role=user_role,
        permission=permission
    )
    if created:
        print(f"为角色 {user_role.name} 分配权限: {permission.name}")

print("数据库初始化完成！")
EOF

echo "========================================="
echo "数据库初始化脚本执行完成！"
echo "========================================="