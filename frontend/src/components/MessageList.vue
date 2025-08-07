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
          
          <!-- 消息内容 -->
          <div v-else class="message-text" :class="{ error: message.status === 'failed' }">
            {{ message.content }}
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
    await navigator.clipboard.writeText(message.content)
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
</style>