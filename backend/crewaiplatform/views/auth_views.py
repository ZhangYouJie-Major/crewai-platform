from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import logging
import traceback

from ..serializers import UserRegisterSerializer, UserSerializer
from ..services import AuthService

User = get_user_model()
logger = logging.getLogger(__name__)


class AuthViewSet(APIView):
    """认证相关视图"""
    
    class RegisterView(APIView):
        """用户注册"""
        permission_classes = [permissions.AllowAny]
        
        def post(self, request):
            logger.info(f"注册请求开始 - 数据: {request.data}")
            try:
                # 验证数据
                serializer = UserRegisterSerializer(data=request.data)
                logger.info(f"序列化器创建成功")
                
                if not serializer.is_valid():
                    logger.error(f"数据验证失败: {serializer.errors}")
                    
                    # 处理密码验证错误，提供用户友好的提示
                    if 'password' in serializer.errors:
                        password_errors = serializer.errors['password']
                        friendly_messages = []
                        
                        for error in password_errors:
                            error_code = getattr(error, 'code', '')
                            if 'password_too_common' in str(error) or 'password_too_common' == error_code:
                                friendly_messages.append("密码过于简单，请使用更复杂的密码")
                            elif 'password_entirely_numeric' in str(error) or 'password_entirely_numeric' == error_code:
                                friendly_messages.append("密码不能只包含数字，请添加字母")
                            elif 'password_too_short' in str(error) or 'password_too_short' == error_code:
                                friendly_messages.append("密码长度至少8位")
                            elif 'password_too_similar' in str(error) or 'password_too_similar' == error_code:
                                friendly_messages.append("密码不能与用户名过于相似")
                            else:
                                friendly_messages.append("密码不符合要求，请使用包含字母和数字的8位以上密码")
                        
                        return Response({
                            'detail': '密码验证失败',
                            'errors': {'password': friendly_messages}
                        }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 处理其他验证错误
                    friendly_errors = {}
                    for field, errors in serializer.errors.items():
                        if field == 'username':
                            if any('already exists' in str(error) or '已存在' in str(error) for error in errors):
                                friendly_errors[field] = ["用户名已存在，请选择其他用户名"]
                            else:
                                friendly_errors[field] = ["用户名格式不正确"]
                        elif field == 'email':
                            friendly_errors[field] = ["邮箱格式不正确"]
                        elif field == 'non_field_errors':
                            if any('不一致' in str(error) for error in errors):
                                friendly_errors['password_confirm'] = ["两次输入的密码不一致"]
                        else:
                            friendly_errors[field] = [str(error) for error in errors]
                    
                    return Response({
                        'detail': '注册信息有误，请检查后重试',
                        'errors': friendly_errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.info(f"数据验证成功: {serializer.validated_data}")
                
                # 创建用户
                user = AuthService.register_user(**serializer.validated_data)
                logger.info(f"用户创建成功: {user.username}")
                
                # 生成token
                tokens = AuthService.generate_tokens(user)
                logger.info(f"Token生成成功")
                
                response_data = {
                    **tokens,
                    'user': UserSerializer(user).data
                }
                logger.info(f"注册成功响应: {response_data}")
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except ValueError as e:
                logger.error(f"业务逻辑错误: {str(e)}")
                error_msg = str(e)
                if "用户名已存在" in error_msg:
                    return Response({
                        'detail': '注册失败',
                        'errors': {'username': ['用户名已存在，请选择其他用户名']}
                    }, status=status.HTTP_400_BAD_REQUEST)
                return Response({'detail': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"注册失败 - 异常: {str(e)}")
                logger.error(f"异常堆栈: {traceback.format_exc()}")
                return Response({'detail': '注册失败，请稍后重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    class LoginView(APIView):
        """用户登录"""
        permission_classes = [permissions.AllowAny]
        
        def post(self, request):
            try:
                username = request.data.get('username')
                password = request.data.get('password')
                
                if not username or not password:
                    return Response({'detail': '用户名和密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
                
                user = AuthService.login_user(username, password)
                tokens = AuthService.generate_tokens(user)
                
                return Response({
                    **tokens,
                    'user': UserSerializer(user).data
                })
                
            except ValueError as e:
                return Response({'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({'detail': '登录失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    class LogoutView(APIView):
        """用户登出"""
        permission_classes = [permissions.IsAuthenticated]
        
        def post(self, request):
            try:
                refresh_token = request.data.get("refresh")
                if refresh_token:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                return Response({'detail': '登出成功'}, status=status.HTTP_200_OK)
            except Exception:
                return Response({'detail': '登出失败'}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(generics.RetrieveAPIView):
    """获取当前用户信息"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user