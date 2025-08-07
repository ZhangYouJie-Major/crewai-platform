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
            @message-retry="retryMessage"
          />

          <!-- Agent状态指示器 -->
          <AgentStatus
            v-if="agentThinking"
            :agent-name="thinkingAgentName"
          />

          <!-- 输入区域 -->
          <MessageInput
            :disabled="isProcessing"
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
import { Plus, Setting } from '@element-plus/icons-vue'
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

// Agent状态
const agentThinking = ref(false)
const thinkingAgentName = ref('')

// WebSocket连接
let websocket = null

// 计算属性
const hasConversations = computed(() => conversations.value.length > 0)

// 生命周期
onMounted(async () => {
  await loadConversations()
  await loadAvailableAgents()
  
  if (hasConversations.value) {
    selectConversation(conversations.value[0].id)
  }
})

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
  if (!currentConversationId.value || isProcessing.value) return
  
  try {
    isProcessing.value = true
    
    // 通过WebSocket发送消息
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify({
        type: 'send_message',
        content: content
      }))
    } else {
      // 降级到HTTP API
      await ApiService.chat.sendMessage(currentConversationId.value, { content })
      await loadMessages(currentConversationId.value)
    }
    
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
  } finally {
    isProcessing.value = false
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
  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${conversationId}/`
  
  try {
    websocket = new WebSocket(wsUrl)
    
    websocket.onopen = () => {
      console.log('WebSocket连接已建立')
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleWebSocketMessage(data)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket连接已断开')
      websocket = null
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket错误:', error)
    }
  } catch (error) {
    console.error('创建WebSocket连接失败:', error)
  }
}

const disconnectWebSocket = () => {
  if (websocket) {
    websocket.close()
    websocket = null
  }
}

const handleWebSocketMessage = (data) => {
  switch (data.type) {
    case 'connection_established':
      console.log('WebSocket连接成功')
      break
      
    case 'new_message':
      // 添加新消息到列表
      messages.value.push(data.message)
      scrollToBottom()
      break
      
    case 'agent_thinking':
      // 显示Agent思考状态
      agentThinking.value = data.is_thinking
      thinkingAgentName.value = data.agent_name
      break
      
    case 'typing_status':
      // 处理用户输入状态（可以显示其他用户正在输入）
      break
      
    case 'error':
      ElMessage.error(data.message)
      break
      
    default:
      console.log('未处理的WebSocket消息:', data)
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

// 组件销毁时清理WebSocket连接
onBeforeUnmount(() => {
  disconnectWebSocket()
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
</style>