from ..models import Permission


class PermissionService:
    """权限管理服务"""
    
    @staticmethod
    def get_permission_list():
        """获取权限列表"""
        return Permission.objects.all().order_by('name')
    
    @staticmethod
    def get_permission_stats():
        """获取权限统计信息"""
        return {
            'total_count': Permission.objects.count(),
        }