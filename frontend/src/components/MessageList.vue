<template>
  <div class="message-list" ref="messageContainer" v-loading="loading">
    <div class="message-wrapper" v-for="message in messages" :key="message.id">
      <!-- 用户消息 -->
      <div v-if="message.role === 'user'" class="message user-message">
        <div class="message-content">
          <div class="message-text">{{ message.content }}</div>
        </div>
        <div class="message-meta">
          <span class="message-time">{{ formatTime(message.created_at) }}</span>
        </div>
      </div>

      <!-- 助手消息 -->
      <div v-else-if="message.role === 'assistant'" class="message assistant-message">
        <div class="agent-avatar">
          <el-avatar :size="36">
            <el-icon><Avatar /></el-icon>
          </el-avatar>
        </div>
        
        <div class="message-content">
          <div class="agent-name">{{ message.agent_name || 'Assistant' }}</div>
          
          <!-- 消息状态 -->
          <div v-if="message.status === 'processing'" class="processing-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在思考中...</span>
          </div>
          
          <!-- 流式输出状态 -->
          <div v-else-if="message.status === 'streaming'" class="streaming-indicator">
            <div class="message-text streaming-text">
              {{ parseMessageContent(message.content) }}
              <span class="typing-cursor">|</span>
            </div>
          </div>
          
          <!-- 消息内容 -->
          <div v-else class="message-text" :class="{ error: message.status === 'failed' }">
            {{ parseMessageContent(message.content) }}
          </div>
          
          <!-- 错误信息 -->
          <div v-if="message.status === 'failed' && message.error_message" class="error-details">
            <el-alert 
              :title="message.error_message" 
              type="error" 
              :closable="false"
              size="small"
            />
          </div>
          
          <!-- 操作按钮 -->
          <div class="message-actions" v-if="message.role === 'user'">
            <el-button 
              size="small" 
              text 
              @click="copyMessage(message)"
              :icon="CopyDocument"
            >
              复制
            </el-button>
            <el-button 
              size="small" 
              text 
              type="warning"
              @click="retryMessage(message)"
              :icon="RefreshRight"
            >
              重试
            </el-button>
          </div>
          
          <!-- 助手消息操作 -->
          <div class="message-actions" v-else-if="message.role === 'assistant'">
            <el-button 
              size="small" 
              text 
              @click="copyMessage(message)"
              :icon="CopyDocument"
            >
              复制
            </el-button>
          </div>
        </div>
        
        <div class="message-meta">
          <span class="message-time">{{ formatTime(message.created_at) }}</span>
        </div>
      </div>

      <!-- 系统消息 -->
      <div v-else-if="message.role === 'system'" class="message system-message">
        <div class="system-content">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ message.content }}</span>
        </div>
      </div>
    </div>

    <!-- 思考过程显示 -->
    <div v-if="thinkingContent" class="thinking-display">
      <div class="thinking-message">
        <div class="agent-avatar">
          <el-avatar :size="36">
            <el-icon><Avatar /></el-icon>
          </el-avatar>
        </div>
        <div class="thinking-content">
          <div class="agent-name">{{ thinkingAgentName || 'Assistant' }}</div>
          <div class="thinking-bubble">
            <div class="thinking-header">
              <el-icon class="is-loading thinking-icon"><Loading /></el-icon>
              <span class="thinking-label">正在思考...</span>
            </div>
            <div class="thinking-text" v-if="thinkingContent.trim()">
              {{ thinkingContent }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && messages.length === 0" class="empty-state">
      <el-empty 
        description="开始对话吧！"
        :image-size="100"
      >
        <template #image>
          <el-icon size="100" color="#c0c4cc">
            <ChatDotRound />
          </el-icon>
        </template>
      </el-empty>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  CopyDocument, 
  RefreshRight, 
  Loading, 
  InfoFilled, 
  Avatar,
  ChatDotRound
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  thinkingContent: {
    type: String,
    default: ''
  },
  thinkingAgentName: {
    type: String,
    default: 'Assistant'
  }
})

// Emits
const emit = defineEmits(['message-retry'])

// Refs
const messageContainer = ref(null)

// 监听消息变化，自动滚动到底部
watch(() => props.messages.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// 方法
const parseMessageContent = (content) => {
  if (!content) return ''
  
  // 检查是否包含<answer>标签
  const answerMatch = content.match(/<answer>([\s\S]*?)<\/answer>/)
  if (answerMatch && answerMatch[1]) {
    // 返回answer标签内的内容，去除首尾空白
    return answerMatch[1].trim()
  }
  
  // 如果没有answer标签，检查是否包含thinking标签
  const thinkingMatch = content.match(/<thinking>([\s\S]*?)<\/thinking>/)
  if (thinkingMatch) {
    // 如果只有thinking标签，返回一个友好的提示
    return '正在思考中...'
  }
  
  // 如果都没有，返回原始内容
  return content
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 24小时内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
}

const copyMessage = async (message) => {
  try {
    // 复制解析后的内容而不是原始内容
    const contentToCopy = parseMessageContent(message.content)
    await navigator.clipboard.writeText(contentToCopy)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

const retryMessage = (message) => {
  emit('message-retry', message)
}

const scrollToBottom = () => {
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}

// 暴露方法给父组件
defineExpose({
  scrollToBottom
})
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 100%;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background: #409eff;
  color: white;
  padding: 12px 16px;
  border-radius: 18px 4px 18px 18px;
  max-width: 70%;
  word-break: break-word;
}

.assistant-message {
  align-items: flex-start;
}

.agent-avatar {
  flex-shrink: 0;
  margin-top: 4px;
}

.assistant-message .message-content {
  background: white;
  padding: 16px;
  border-radius: 4px 18px 18px 18px;
  border: 1px solid #e4e7ed;
  max-width: 80%;
  word-break: break-word;
}

.agent-name {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
  font-weight: 500;
}

.processing-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-style: italic;
  font-size: 14px;
}

.message-text {
  line-height: 1.6;
  white-space: pre-wrap;
  font-size: 14px;
  color: #303133; /* 设置深色文字颜色 */
}

.message-text.error {
  color: #f56c6c;
}

.error-details {
  margin-top: 8px;
}

.message-actions {
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  gap: 8px;
}

.message:hover .message-actions {
  opacity: 1;
}

.message-meta {
  align-self: flex-end;
  margin-top: 4px;
}

.message-time {
  font-size: 11px;
  color: #c0c4cc;
}

.system-message {
  justify-content: center;
  margin: 12px 0;
}

.system-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f4f4f5;
  border-radius: 12px;
  font-size: 13px;
  color: #606266;
  max-width: 80%;
}

.empty-state {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 流式输出样式 */
.streaming-indicator {
  margin-bottom: 12px;
}

.streaming-text {
  position: relative;
}

.typing-cursor {
  display: inline-block;
  background-color: #409eff;
  color: #409eff;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* 思考过程显示 */
.thinking-display {
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in-out;
}

.thinking-message {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.thinking-content {
  flex: 1;
  min-width: 0;
}

.thinking-bubble {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border: 1px solid #e1bee7;
  border-radius: 12px;
  padding: 16px;
  position: relative;
  animation: pulse 2s infinite;
}

.thinking-bubble::before {
  content: '';
  position: absolute;
  top: 15px;
  left: -6px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 6px 6px 6px 0;
  border-color: transparent #e1bee7 transparent transparent;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.thinking-icon {
  color: #9c27b0;
}

.thinking-label {
  font-weight: 500;
  color: #7b1fa2;
  font-size: 14px;
}

.thinking-text {
  color: #5e35b1;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px 0;
  border-top: 1px solid rgba(156, 39, 176, 0.2);
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(156, 39, 176, 0.2); }
  70% { box-shadow: 0 0 0 10px rgba(156, 39, 176, 0); }
  100% { box-shadow: 0 0 0 0 rgba(156, 39, 176, 0); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>