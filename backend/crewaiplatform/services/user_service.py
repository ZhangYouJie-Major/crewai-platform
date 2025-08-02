from django.contrib.auth import get_user_model

User = get_user_model()


class UserService:
    """用户管理服务"""
    
    @staticmethod
    def get_user_list(page=1, page_size=20):
        """获取用户列表"""
        return User.objects.all().order_by('-date_joined')
    
    @staticmethod
    def get_user_stats():
        """获取用户统计信息"""
        return {
            'total_count': User.objects.count(),
            'active_count': User.objects.filter(is_active=True).count(),
            'staff_count': User.objects.filter(is_staff=True).count(),
        }