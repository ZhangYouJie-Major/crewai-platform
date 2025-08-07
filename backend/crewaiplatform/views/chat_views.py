"""
聊天功能相关视图

提供聊天会话、消息、Agent任务的REST API接口。
"""

import asyncio
import logging
from typing import Dict, Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models import ChatConversation, ChatMessage, ChatAgentTask, CrewAIAgent
from ..serializers import (
    ChatConversationSerializer,
    ChatConversationCreateSerializer,
    ChatMessageSerializer,
    ChatMessageCreateSerializer,
    ChatAgentTaskSerializer,
    AgentSimpleSerializer,
    ChatStatsSerializer
)
from ..services import (
    ChatService,
    ChatMessageService,
    ChatAgentTaskService,
    ChatStatsService,
    SimpleAgentService,
    MockAgentService
)


logger = logging.getLogger(__name__)


class ChatConversationViewSet(viewsets.ModelViewSet):
    """聊天会话视图集"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的会话列表"""
        return ChatService.get_user_conversations(self.request.user)
    
    def get_serializer_class(self):
        """根据动作选择序列化器"""
        if self.action == 'create':
            return ChatConversationCreateSerializer
        return ChatConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """创建新的聊天会话"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            conversation = ChatService.create_conversation(
                user=request.user,
                **serializer.validated_data
            )
            
            response_serializer = ChatConversationSerializer(conversation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"创建会话失败: {e}")
            return Response(
                {'error': '创建会话失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """更新会话信息"""
        conversation = self.get_object()
        serializer = self.get_serializer(conversation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_conversation = ChatService.update_conversation(
                conversation, **serializer.validated_data
            )
            response_serializer = ChatConversationSerializer(updated_conversation)
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"更新会话失败: {e}")
            return Response(
                {'error': '更新会话失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """删除会话"""
        conversation = self.get_object()
        
        try:
            success = ChatService.delete_conversation(conversation)
            if success:
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'error': '删除会话失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return Response(
                {'error': '删除会话失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """归档会话"""
        conversation = self.get_object()
        
        try:
            success = ChatService.archive_conversation(conversation)
            if success:
                response_serializer = ChatConversationSerializer(conversation)
                return Response(response_serializer.data)
            else:
                return Response(
                    {'error': '归档会话失败'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"归档会话失败: {e}")
            return Response(
                {'error': '归档会话失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的消息列表"""
        conversation = self.get_object()
        
        try:
            messages = ChatMessageService.get_conversation_messages(conversation)
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取消息列表失败: {e}")
            return Response(
                {'error': '获取消息列表失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """发送消息到会话"""
        conversation = self.get_object()
        
        serializer = ChatMessageCreateSerializer(
            data=request.data,
            context={'conversation': conversation}
        )
        serializer.is_valid(raise_exception=True)
        
        try:
            # 创建用户消息
            user_message = ChatMessageService.create_user_message(
                conversation=conversation,
                content=serializer.validated_data['content']
            )
            
            # 同步触发Agent处理（在实际项目中应该使用后台任务队列如Celery）
            # 这里使用模拟Agent服务进行演示
            try:
                self._process_message_sync(user_message)
            except Exception as e:
                logger.error(f"处理Agent响应失败: {e}")
            
            # 返回用户消息
            response_serializer = ChatMessageSerializer(user_message)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return Response(
                {'error': '发送消息失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _process_message_sync(self, user_message: ChatMessage):
        """同步处理用户消息"""
        try:
            # 使用模拟Agent服务处理消息
            assistant_message = MockAgentService.process_user_message_sync(user_message)
            
            if assistant_message:
                logger.info(f"消息 {user_message.id} 处理完成")
            else:
                logger.error(f"消息 {user_message.id} 处理失败")
                
        except Exception as e:
            logger.error(f"同步处理消息失败: {e}")
    
    @action(detail=True, methods=['get'])
    def active_tasks(self, request, pk=None):
        """获取会话的活跃任务"""
        conversation = self.get_object()
        
        try:
            tasks = ChatAgentTaskService.get_active_tasks(conversation=conversation)
            serializer = ChatAgentTaskSerializer(tasks, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取活跃任务失败: {e}")
            return Response(
                {'error': '获取活跃任务失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取用户聊天统计"""
        try:
            stats_data = ChatStatsService.get_user_chat_stats(request.user)
            serializer = ChatStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取聊天统计失败: {e}")
            return Response(
                {'error': '获取统计数据失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """聊天消息视图集（只读）"""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的消息列表"""
        return ChatMessage.objects.filter(
            conversation__user=self.request.user
        ).select_related('conversation', 'agent').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """重试失败的消息"""
        message = self.get_object()
        
        if message.role != 'user':
            return Response(
                {'error': '只能重试用户消息'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 异步重新处理消息
            asyncio.create_task(
                MockAgentService.process_user_message(message)
            )
            
            return Response({'message': '消息重试中'})
            
        except Exception as e:
            logger.error(f"重试消息失败: {e}")
            return Response(
                {'error': '重试消息失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatAgentTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """Agent任务视图集（只读）"""
    
    serializer_class = ChatAgentTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户的任务列表"""
        return ChatAgentTask.objects.filter(
            conversation__user=self.request.user
        ).select_related('agent', 'conversation', 'message').order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消任务"""
        task = self.get_object()
        
        if task.status not in ['pending', 'running']:
            return Response(
                {'error': '只能取消待执行或执行中的任务'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 简单地标记任务为失败状态
            ChatAgentTaskService.fail_task_execution(task, "用户取消任务")
            
            response_serializer = ChatAgentTaskSerializer(task)
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            return Response(
                {'error': '取消任务失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取活跃任务列表"""
        try:
            tasks = ChatAgentTaskService.get_active_tasks(user=request.user)
            serializer = ChatAgentTaskSerializer(tasks, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"获取活跃任务失败: {e}")
            return Response(
                {'error': '获取活跃任务失败', 'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AgentSelectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Agent选择视图集"""
    
    serializer_class = AgentSimpleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取当前用户可用的Agent列表"""
        return CrewAIAgent.objects.filter(
            owner=self.request.user,
            is_active=True
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """获取可用的Agent列表"""
        queryset = self.get_queryset()
        
        # 支持按名称搜索
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(role__icontains=search)
            )
        
        # 支持按角色筛选
        role = request.query_params.get('role', '')
        if role:
            queryset = queryset.filter(role__icontains=role)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)