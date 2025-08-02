from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AuthService:
    """认证相关服务"""
    
    @staticmethod
    def register_user(username, password, email="", first_name="", last_name=""):
        """用户注册服务"""
        if User.objects.filter(username=username).exists():
            raise ValueError("用户名已存在")
        
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        return user
    
    @staticmethod
    def login_user(username, password):
        """用户登录服务"""
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValueError("用户名或密码错误")
        
        if not user.is_active:
            raise ValueError("用户账户已被禁用")
        
        return user
    
    @staticmethod
    def generate_tokens(user):
        """生成JWT令牌"""
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }