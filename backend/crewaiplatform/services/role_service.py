from ..models import Role


class RoleService:
    """角色管理服务"""
    
    @staticmethod
    def get_role_list():
        """获取角色列表"""
        return Role.objects.all().order_by('name')
    
    @staticmethod
    def get_role_stats():
        """获取角色统计信息"""
        return {
            'total_count': Role.objects.count(),
        }