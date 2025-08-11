<template>
  <div class="chat-interface">
    <!-- 顶部导航栏 -->
    <el-header class="chat-header" height="60px">
      <div class="header-left">
        <h3 class="chat-title">
          {{ currentConversation ? currentConversation.title : 'CrewAI 智能助手' }}
        </h3>
      </div>
      <div class="header-right">
        <!-- WebSocket连接状态 -->
        <div class="connection-status" :class="{ connected: isConnected, disconnected: !isConnected }">
          <el-icon><Connection /></el-icon>
          <span>{{ isConnected ? '已连接' : '未连接' }}</span>
          <el-button 
            v-if="!isConnected && currentConversationId" 
            type="text" 
            size="small" 
            @click="forceReconnect"
            style="margin-left: 8px;"
          >
            重连
          </el-button>
        </div>
        
        <el-button 
          type="primary" 
          :icon="Plus" 
          @click="createNewConversation"
          size="small"
        >
          新对话
        </el-button>
        <el-button 
          :icon="Setting" 
          @click="showSettings = true"
          size="small"
        >
          设置
        </el-button>
      </div>
    </el-header>

    <!-- 主体区域 -->
    <el-container class="main-container">
      <!-- 左侧边栏 -->
      <el-aside width="300px" class="sidebar">
        <ChatSidebar
          :conversations="conversations"
          :current-conversation-id="currentConversationId"
          :loading="conversationsLoading"
          @conversation-select="selectConversation"
          @conversation-delete="deleteConversation"
          @conversation-archive="archiveConversation"
        />
      </el-aside>

      <!-- 中间聊天区域 -->
      <el-main class="chat-main">
        <div class="chat-container" v-if="currentConversation">
          <!-- 消息列表 -->
          <MessageList
            ref="messageList"
            :messages="messages"
            :loading="messagesLoading"
            :chat-state="chatState"
            @message-retry="retryMessage"
            @toggle-thinking="toggleThinkingCollapse"
          />

          <!-- Agent状态指示器 -->
          <AgentStatus
            v-if="agentThinking"
            :agent-name="thinkingAgentName"
          />

          <!-- 输入区域 -->
          <MessageInput
            :disabled="chatState.status === 'sending' || chatState.status === 'thinking'"
            @send-message="sendMessage"
          />
        </div>
        
        <!-- 欢迎界面 -->
        <div v-else class="welcome-screen">
          <div class="welcome-content">
            <el-empty description="请选择一个对话或创建新对话开始聊天">
              <el-button type="primary" @click="createNewConversation">
                创建新对话
              </el-button>
            </el-empty>
          </div>
        </div>
      </el-main>

      <!-- 右侧Agent面板 -->
      <el-aside width="320px" class="agent-panel">
        <AgentPanel
          v-if="currentConversation"
          :conversation="currentConversation"
          :available-agents="availableAgents"
          @agent-select="selectAgent"
          @settings-change="updateConversationSettings"
        />
      </el-aside>
    </el-container>

    <!-- 设置对话框 -->
    <SettingsDialog
      v-model="showSettings"
      @save="saveSettings"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick, computed, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Setting, Connection } from '@element-plus/icons-vue'
import { ApiService } from '@/services/api'
import ChatSidebar from '@/components/ChatSidebar.vue'
import MessageList from '@/components/MessageList.vue'
import MessageInput from '@/components/MessageInput.vue'
import AgentPanel from '@/components/AgentPanel.vue'
import AgentStatus from '@/components/AgentStatus.vue'
import SettingsDialog from '@/components/SettingsDialog.vue'

// 响应式数据
const currentConversationId = ref(null)
const currentConversation = ref(null)
const conversations = ref([])
const messages = ref([])
const availableAgents = ref([])

const conversationsLoading = ref(false)
const messagesLoading = ref(false)
const isProcessing = ref(false)
const showSettings = ref(false)

// 统一的聊天状态管理
const chatState = reactive({
  // 当前聊天状态: 'idle', 'sending', 'thinking', 'answering', 'streaming', 'completed'
  status: 'idle',
  // AI思考相关
  isThinking: false,
  thinkingContent: '',  // 思考的完整内容
  thinkingCollapsed: false,  // 思考内容是否折叠
  thinkingAgentName: '',
  // 流式输出相关
  isStreaming: false,
  streamingMessage: null,
  answerContent: '',  // 答案的完整内容
  // 错误处理
  hasError: false,
  errorMessage: ''
})

// WebSocket连接
let websocket = null
let reconnectTimer = null
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const reconnectInterval = 3000 // 3秒

// 状态管理相关
let stateTimeoutTimer = null
const stateTimeoutDuration = 30000 // 30秒超时

// 兼容性属性（保持向后兼容）
const agentThinking = computed(() => chatState.isThinking)
const thinkingMessage = computed(() => chatState.thinkingContent)
const thinkingAgentName = computed(() => chatState.thinkingAgentName)
const streamingMessage = computed(() => chatState.streamingMessage)
const isStreaming = computed(() => chatState.isStreaming)
const isConnected = ref(false)

// 计算属性
const hasConversations = computed(() => conversations.value.length > 0)

// 生命周期
onMounted(async () => {
  await loadConversations()
  await loadAvailableAgents()
  
  if (hasConversations.value) {
    selectConversation(conversations.value[0].id)
  }
  
  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

// 页面可见性变化处理
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    // 页面变为可见，检查WebSocket连接
    if (currentConversationId.value && !isConnected.value) {
      console.log('页面重新可见，尝试重连WebSocket')
      connectWebSocket(currentConversationId.value)
    }
  }
}

// 监听会话变化
watch(currentConversationId, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await loadMessages(newId)
    connectWebSocket(newId)
  }
})

// API调用方法
const loadConversations = async () => {
  try {
    conversationsLoading.value = true
    const response = await ApiService.chat.getConversations()
    conversations.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载对话列表失败:', error)
    ElMessage.error('加载对话列表失败')
  } finally {
    conversationsLoading.value = false
  }
}

const loadMessages = async (conversationId) => {
  try {
    messagesLoading.value = true
    const response = await ApiService.chat.getMessages(conversationId)
    messages.value = response.data || []
    
    // 滚动到底部
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
    ElMessage.error('加载消息失败')
  } finally {
    messagesLoading.value = false
  }
}

const loadAvailableAgents = async () => {
  try {
    const response = await ApiService.chat.getAvailableAgents()
    availableAgents.value = response.data || []
  } catch (error) {
    console.error('加载Agent列表失败:', error)
  }
}

// 会话管理方法
const createNewConversation = async () => {
  try {
    const response = await ApiService.chat.createConversation({
      title: '新对话',
      agent_selection_mode: 'manual'
    })
    
    const newConversation = response.data
    conversations.value.unshift(newConversation)
    selectConversation(newConversation.id)
    
    ElMessage.success('创建新对话成功')
  } catch (error) {
    console.error('创建对话失败:', error)
    ElMessage.error('创建对话失败')
  }
}

const selectConversation = async (conversationId) => {
  if (currentConversationId.value === conversationId) return
  
  // 断开旧的WebSocket连接
  disconnectWebSocket()
  
  // 更新当前会话
  currentConversationId.value = conversationId
  currentConversation.value = conversations.value.find(c => c.id === conversationId)
}

const deleteConversation = async (conversationId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个对话吗？删除后无法恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    console.log('🗑️ 删除会话:', conversationId)
    
    // 如果删除的是当前会话，先断开WebSocket连接并清理状态
    if (currentConversationId.value === conversationId) {
      console.log('🔌 断开当前会话的WebSocket连接')
      disconnectWebSocket()
      
      // 清空当前会话相关状态
      agentThinking.value = false
      isStreaming.value = false
      streamingMessage.value = null
      thinkingMessage.value = ''
      isProcessing.value = false
    }
    
    await ApiService.chat.deleteConversation(conversationId)
    
    // 从列表中移除
    conversations.value = conversations.value.filter(c => c.id !== conversationId)
    
    // 如果删除的是当前会话，切换到第一个会话
    if (currentConversationId.value === conversationId) {
      if (conversations.value.length > 0) {
        selectConversation(conversations.value[0].id)
      } else {
        currentConversationId.value = null
        currentConversation.value = null
        messages.value = []
      }
    }
    
    ElMessage.success('对话已删除')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除对话失败:', error)
      ElMessage.error('删除对话失败')
    }
  }
}

const archiveConversation = async (conversationId) => {
  try {
    await ApiService.chat.archiveConversation(conversationId)
    
    // 从列表中移除
    conversations.value = conversations.value.filter(c => c.id !== conversationId)
    
    ElMessage.success('对话已归档')
  } catch (error) {
    console.error('归档对话失败:', error)
    ElMessage.error('归档对话失败')
  }
}

// 消息处理方法
const sendMessage = async (content) => {
  if (!currentConversationId.value || chatState.status === 'sending') {
    console.warn('⚠️ 无法发送消息:', {
      hasConversation: !!currentConversationId.value,
      chatStatus: chatState.status
    })
    return
  }
  
  console.log('📤 准备发送消息:', {
    conversationId: currentConversationId.value,
    content: content,
    websocketStatus: websocket ? websocket.readyState : 'null',
    isConnected: isConnected.value
  })
  
  try {
    // 1. 立即更新聊天状态为发送中
    setChatState('sending')
    
    // 2. 立即在UI中显示用户消息
    const userMessage = {
      id: Date.now() + Math.random(), // 临时ID
      role: 'user',
      content: content,
      status: 'sending',
      created_at: new Date().toISOString(),
      temp: true // 标记为临时消息
    }
    messages.value.push(userMessage)
    scrollToBottom()
    
    // 3. 立即显示AI思考状态
    setChatState('thinking', {
      isThinking: true,
      thinkingMessage: '正在思考中...',
      thinkingAgentName: currentConversation.value?.primary_agent_name || 'Assistant'
    })
    
    // 4. 启动状态超时保护
    startStateTimeout()
    
    // 检查WebSocket连接，如果未连接则尝试连接
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
      console.log('🔗 WebSocket未连接，尝试建立连接')
      connectWebSocket(currentConversationId.value)
      
      // 等待连接建立（最多等待3秒）
      let waitTime = 0
      const maxWaitTime = 3000
      const checkInterval = 100
      
      while ((!websocket || websocket.readyState !== WebSocket.OPEN) && waitTime < maxWaitTime) {
        await new Promise(resolve => setTimeout(resolve, checkInterval))
        waitTime += checkInterval
      }
    }
    
    // 通过WebSocket发送消息
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const messageData = {
        type: 'send_message',
        content: content
      }
      
      console.log('🚀 通过WebSocket发送消息:', messageData)
      websocket.send(JSON.stringify(messageData))
      
    } else {
      console.warn('⚠️ WebSocket仍未连接，使用HTTP API降级')
      // 降级到HTTP API
      const response = await ApiService.chat.sendMessage(currentConversationId.value, { content })
      console.log('📡 HTTP API响应:', response)
      
      // 移除临时用户消息，重新加载所有消息
      messages.value = messages.value.filter(msg => !msg.temp)
      await loadMessages(currentConversationId.value)
    }
    
  } catch (error) {
    console.error('❌ 发送消息失败:', error)
    
    // 清理临时消息
    messages.value = messages.value.filter(msg => !msg.temp)
    
    // 设置错误状态
    setChatState('idle', {
      hasError: true,
      errorMessage: '发送消息失败：' + error.message
    })
    
    ElMessage.error('发送消息失败')
  }
}

const retryMessage = async (message) => {
  try {
    await ApiService.chat.retryMessage(message.id)
    ElMessage.success('消息重试中...')
  } catch (error) {
    console.error('重试消息失败:', error)
    ElMessage.error('重试消息失败')
  }
}

// Agent和设置方法
const selectAgent = async (agentId) => {
  try {
    await ApiService.chat.updateConversation(currentConversationId.value, {
      primary_agent: agentId
    })
    
    // 更新本地数据
    if (currentConversation.value) {
      currentConversation.value.primary_agent = agentId
    }
    
    ElMessage.success('Agent已切换')
  } catch (error) {
    console.error('切换Agent失败:', error)
    ElMessage.error('切换Agent失败')
  }
}

const updateConversationSettings = async (settings) => {
  try {
    await ApiService.chat.updateConversation(currentConversationId.value, settings)
    
    // 更新本地数据
    Object.assign(currentConversation.value, settings)
    
    ElMessage.success('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败')
  }
}

const saveSettings = (settings) => {
  console.log('保存全局设置:', settings)
  ElMessage.success('设置已保存')
}

// WebSocket管理方法
const connectWebSocket = (conversationId) => {
  disconnectWebSocket()
  
  // 使用环境变量配置WebSocket URL
  const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'
  
  // 获取JWT token并添加到WebSocket URL
  const token = localStorage.getItem('access')
  const wsUrl = token 
    ? `${wsBaseUrl}/ws/chat/${conversationId}/?token=${token}`
    : `${wsBaseUrl}/ws/chat/${conversationId}/`
  
  console.log('🔗 尝试连接WebSocket:', {
    url: wsUrl.replace(/token=[^&]+/, 'token=***'), // 隐藏token在日志中
    conversationId: conversationId,
    wsBaseUrl: wsBaseUrl,
    hasToken: !!token
  })
  
  try {
    websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('✅ WebSocket连接已建立')
      isConnected.value = true
      reconnectAttempts = 0 // 重置重连计数
      
      // 清除重连定时器
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
        reconnectTimer = null
      }
      
      ElMessage({
        message: 'WebSocket连接成功',
        type: 'success',
        duration: 2000
      })
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
    
    websocket.onclose = (event) => {
      console.log('🔌 WebSocket连接已断开:', {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean
      })
      isConnected.value = false
      websocket = null
      
      // 如果不是正常关闭（代码1000）且在活跃页面，尝试重连
      if (event.code !== 1000 && document.visibilityState === 'visible' && currentConversationId.value) {
        console.log('⚠️ 非正常断开，尝试重连')
        attemptReconnect(conversationId)
      }
    }
    
    websocket.onerror = (error) => {
      console.error('❌ WebSocket错误:', error)
      ElMessage.error('WebSocket连接出错')
    }
  } catch (error) {
    console.error('❌ 创建WebSocket连接失败:', error)
    ElMessage.error('无法建立WebSocket连接')
  }
}

const attemptReconnect = (conversationId) => {
  if (reconnectAttempts >= maxReconnectAttempts) {
    ElMessage.error('WebSocket重连失败，请刷新页面')
    return
  }
  
  reconnectAttempts++
  console.log(`🔄 尝试WebSocket重连 (${reconnectAttempts}/${maxReconnectAttempts})`)
  
  ElMessage({
    message: `WebSocket重连中... (${reconnectAttempts}/${maxReconnectAttempts})`,
    type: 'info',
    duration: 2000
  })
  
  reconnectTimer = setTimeout(() => {
    connectWebSocket(conversationId)
  }, reconnectInterval)
}

// 强制重连WebSocket
const forceReconnect = () => {
  if (currentConversationId.value) {
    console.log('🔄 用户手动触发重连')
    reconnectAttempts = 0 // 重置重连计数
    connectWebSocket(currentConversationId.value)
  }
}

const disconnectWebSocket = () => {
  // 清理重连定时器
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
    reconnectTimer = null
  }
  
  // 关闭WebSocket连接
  if (websocket) {
    websocket.close(1000) // 正常关闭代码
    websocket = null
  }
  
  isConnected.value = false
  reconnectAttempts = 0
}

const handleWebSocketMessage = (data) => {
  // 详细的调试日志
  console.log('📨 WebSocket收到消息:', {
    type: data.type,
    timestamp: new Date().toISOString(),
    data: data
  })
  
  // 清除状态超时（有活动说明正常）
  clearStateTimeout()
  
  switch (data.type) {
    case 'connection_established':
      console.log('✅ WebSocket连接建立成功')
      break
      
    case 'new_message':
      console.log('💬 收到新消息:', data.message)
      // 移除临时用户消息（如果存在）
      messages.value = messages.value.filter(msg => !msg.temp)
      // 添加真实消息到列表
      messages.value.push(data.message)
      scrollToBottom()
      break
      
    case 'agent_thinking':
      console.log(`🤔 Agent思考状态: ${data.is_thinking ? '开始' : '结束'}`, {
        agent_id: data.agent_id,
        agent_name: data.agent_name
      })
      // 更新思考状态
      setChatState(data.is_thinking ? 'thinking' : 'idle', {
        isThinking: data.is_thinking,
        thinkingAgentName: data.agent_name
      })
      break
      
    case 'thinking_status_update':
      console.log('💭 思考状态更新:', {
        is_thinking: data.is_thinking,
        message: data.message
      })
      setChatState(data.is_thinking ? 'thinking' : 'idle', {
        isThinking: data.is_thinking,
        thinkingContent: data.message
      })
      break
      
    case 'thinking_content_update':
      console.log('📝 思考内容更新:', data.content.substring(0, 100) + '...')
      // 解析thinking标签内容
      const thinkingContent = parseThinkingContent(data.content)
      setChatState('thinking', {
        thinkingContent: thinkingContent
      })
      break
      
    case 'thinking_complete':
      console.log('✨ 思考完成，准备回答')
      // 思考完成，进入回答阶段
      setChatState('answering', {
        isThinking: false
      })
      break
      
    case 'answer_stream_start':
      console.log('📋 开始流式输出答案')
      // 开始流式输出答案 - 折叠思考内容
      const newStreamingMessage = {
        id: Date.now() + Math.random(), // 临时ID
        role: 'assistant',
        content: '',
        agent_name: chatState.thinkingAgentName || 'Assistant',
        status: 'streaming',
        created_at: new Date().toISOString(),
        thinking_content: chatState.thinkingContent // 保存思考内容
      }
      
      setChatState('streaming', {
        isStreaming: true,
        streamingMessage: newStreamingMessage,
        thinkingCollapsed: true, // 折叠思考内容
        answerContent: '' // 重置答案内容
      })
      
      messages.value.push(newStreamingMessage)
      scrollToBottom()
      break
      
    case 'answer_stream_update':
      console.log('⚡ 流式内容更新:', data.content.substring(0, 50) + '...')
      // 流式更新答案内容
      // 若尚未收到start事件（后端已做兜底，但前端也要健壮），则本地创建流式消息
      if (!chatState.streamingMessage) {
        const autoStreamingMessage = {
          id: Date.now() + Math.random(),
          role: 'assistant',
          content: '',
          agent_name: chatState.thinkingAgentName || 'Assistant',
          status: 'streaming',
          created_at: new Date().toISOString(),
          thinking_content: chatState.thinkingContent
        }
        chatState.streamingMessage = autoStreamingMessage
        messages.value.push(autoStreamingMessage)
        setChatState('streaming', { isStreaming: true, thinkingCollapsed: true })
      }

      // 解析answer标签内容，后端已发送累计内容，这里直接覆盖展示
      const answerContent = parseAnswerContent(data.content || '')
      chatState.streamingMessage.content = answerContent
      chatState.answerContent = answerContent
      scrollToBottom()
      break
      
    case 'answer_stream_complete':
      console.log('✅ 流式输出完成:', {
        content_length: data.content ? data.content.length : 0
      })
      // 流式输出完成
      if (!chatState.streamingMessage) {
        // 如果没有start/update，也要能展示最终答案
        const finalMsg = {
          id: Date.now() + Math.random(),
          role: 'assistant',
          content: '',
          agent_name: chatState.thinkingAgentName || 'Assistant',
          status: 'streaming',
          created_at: new Date().toISOString(),
          thinking_content: chatState.thinkingContent
        }
        chatState.streamingMessage = finalMsg
        messages.value.push(finalMsg)
      }
      {
        const finalAnswerContent = parseAnswerContent(data.content || chatState.answerContent || '')
        chatState.streamingMessage.content = finalAnswerContent
        chatState.streamingMessage.status = 'completed'
      }
      
      // 完全重置到idle状态
      setChatState('completed')
      
      // 延迟一点时间后完全重置状态
      setTimeout(() => {
        setChatState('idle')
      }, 1000)
      
      ElMessage({
        message: '回答完成',
        type: 'success',
        duration: 1500
      })
      break
      
    case 'typing_status':
      console.log('⌨️ 输入状态:', data)
      // 处理用户输入状态（可以显示其他用户正在输入）
      break
      
    case 'error':
      console.error('❌ WebSocket错误消息:', data.message)
      setChatState('idle', {
        hasError: true,
        errorMessage: data.message
      })
      ElMessage.error(data.message)
      break
      
    default:
      console.warn('❓ 未处理的WebSocket消息类型:', data.type, data)
  }
}

// 更新思考过程显示
const updateThinkingDisplay = (content) => {
  // 可以在这里实现思考过程的实时显示逻辑
  // 例如在MessageList组件中显示思考气泡
  console.log('思考过程:', content)
}

// 内容解析方法
const parseThinkingContent = (content) => {
  // 提取<thinking>标签内的内容
  const thinkingMatch = content.match(/<thinking[^>]*>([\s\S]*?)<\/thinking>/i)
  return thinkingMatch ? thinkingMatch[1].trim() : ''
}

const parseAnswerContent = (content) => {
  // 提取<answer>标签内的内容
  if (!content) return ''
  const answerMatch = content.match(/<answer[^>]*>([\s\S]*?)<\/answer>/i)
  if (answerMatch) return answerMatch[1].trim()
  // 无<answer>时，剥离<thinking>块
  const withoutThinking = content.replace(/<thinking[^>]*>[\s\S]*?<\/thinking>/ig, '').trim()
  return withoutThinking || content
}

// 切换思考内容的折叠状态
const toggleThinkingCollapse = () => {
  chatState.thinkingCollapsed = !chatState.thinkingCollapsed
}

// 状态管理方法
const setChatState = (status, updates = {}) => {
  console.log(`🔄 状态变化: ${chatState.status} → ${status}`, updates)
  
  // 根据状态设置默认值
  const stateDefaults = {
    idle: {
      isThinking: false,
      thinkingMessage: '',
      thinkingContent: '',
      isStreaming: false,
      streamingMessage: null,
      hasError: false,
      errorMessage: ''
    },
    sending: {
      hasError: false,
      errorMessage: ''
    },
    thinking: {
      isThinking: true,
      isStreaming: false,
      streamingMessage: null,
      thinkingCollapsed: false
    },
    answering: {
      isThinking: false,
      thinkingCollapsed: true, // 开始回答时折叠思考内容
      isStreaming: false
    },
    streaming: {
      isThinking: false,
      isStreaming: true,
      thinkingCollapsed: true // 流式输出时保持思考内容折叠
    },
    completed: {
      isThinking: false,
      isStreaming: false,
      streamingMessage: null,
      thinkingCollapsed: false, // 完成后可以展开查看思考过程
      thinkingContent: ''      // 完成后清空思考内容，避免残留导致显示“再次思考”
    }
  }
  
  // 应用状态默认值
  Object.assign(chatState, stateDefaults[status] || {})
  
  // 应用额外的更新
  Object.assign(chatState, updates)
  
  // 设置状态
  chatState.status = status
  
  // 重新启动超时保护（除了idle状态）
  if (status !== 'idle' && status !== 'completed') {
    startStateTimeout()
  } else {
    clearStateTimeout()
  }
}

const startStateTimeout = () => {
  clearStateTimeout()
  stateTimeoutTimer = setTimeout(() => {
    console.warn('⏰ 聊天状态超时，自动重置为idle')
    setChatState('idle', {
      hasError: true,
      errorMessage: '响应超时，请重试'
    })
    ElMessage.warning('响应超时，请重试')
  }, stateTimeoutDuration)
}

const clearStateTimeout = () => {
  if (stateTimeoutTimer) {
    clearTimeout(stateTimeoutTimer)
    stateTimeoutTimer = null
  }
}

// 工具方法
const scrollToBottom = () => {
  nextTick(() => {
    const messageList = document.querySelector('.message-list')
    if (messageList) {
      messageList.scrollTop = messageList.scrollHeight
    }
  })
}

// 组件销毁时清理WebSocket连接和事件监听
onBeforeUnmount(() => {
  disconnectWebSocket()
  clearStateTimeout()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.chat-interface {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.chat-header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-left .chat-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 8px;
}

.main-container {
  flex: 1;
  min-height: 0;
}

.sidebar {
  background: white;
  border-right: 1px solid #e4e7ed;
  overflow-y: auto;
}

.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-content {
  text-align: center;
  padding: 40px;
}

.agent-panel {
  background: white;
  border-left: 1px solid #e4e7ed;
  overflow-y: auto;
}

/* WebSocket连接状态样式 */
.connection-status {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  transition: all 0.3s;
}

.connection-status.connected {
  color: #67c23a;
  background-color: rgba(103, 194, 58, 0.1);
}

.connection-status.disconnected {
  color: #f56c6c;
  background-color: rgba(245, 108, 108, 0.1);
}

.connection-status.disconnected .el-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>