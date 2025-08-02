from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

from ..models import Role, Permission, UserRole, RolePermission
from ..serializers import UserSerializer, RoleSerializer, PermissionSerializer, UserRoleSerializer, RolePermissionSerializer
from ..services import UserService, RoleService, PermissionService, RBACService

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图集"""
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取用户统计信息"""
        stats = UserService.get_user_stats()
        return Response(stats)


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Role.objects.all().order_by('name')
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取角色统计信息"""
        stats = RoleService.get_role_stats()
        return Response(stats)


class PermissionViewSet(viewsets.ModelViewSet):
    """权限管理视图集"""
    queryset = Permission.objects.all().order_by('name')
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取权限统计信息"""
        stats = PermissionService.get_permission_stats()
        return Response(stats)


class UserRoleViewSet(viewsets.ModelViewSet):
    """用户角色关联管理"""
    queryset = UserRole.objects.select_related('user', 'role').all().order_by('-assigned_at')
    serializer_class = UserRoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user')
            role_id = request.data.get('role')
            
            user_role, created = RBACService.assign_role_to_user(user_id, role_id)
            
            if created:
                serializer = self.get_serializer(user_role)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': '用户已拥有该角色'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RolePermissionViewSet(viewsets.ModelViewSet):
    """角色权限关联管理"""
    queryset = RolePermission.objects.select_related('role', 'permission').all().order_by('-assigned_at')
    serializer_class = RolePermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        try:
            role_id = request.data.get('role')
            permission_id = request.data.get('permission')
            
            role_permission, created = RBACService.assign_permission_to_role(role_id, permission_id)
            
            if created:
                serializer = self.get_serializer(role_permission)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': '角色已拥有该权限'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DashboardView(APIView):
    """仪表盘数据视图"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """获取仪表盘统计数据"""
        try:
            user_stats = UserService.get_user_stats()
            role_stats = RoleService.get_role_stats()
            permission_stats = PermissionService.get_permission_stats()
            
            return Response({
                'userCount': user_stats['total_count'],
                'roleCount': role_stats['total_count'],
                'permissionCount': permission_stats['total_count'],
                'activeUserCount': user_stats['active_count'],
                'staffCount': user_stats['staff_count'],
            })
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)