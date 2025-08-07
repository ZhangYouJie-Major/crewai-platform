<template>
  <div class="message-input">
    <div class="input-container">
      <el-input
        v-model="messageText"
        type="textarea"
        :autosize="{ minRows: 1, maxRows: 6 }"
        placeholder="输入消息... (Shift+Enter换行，Enter发送)"
        :disabled="disabled"
        @keydown="handleKeyDown"
        @input="handleInput"
        resize="none"
        ref="inputRef"
      />
      
      <div class="input-actions">
        <el-button
          type="primary"
          :disabled="!canSend"
          @click="sendMessage"
          :loading="disabled"
          circle
          :icon="Position"
        />
      </div>
    </div>
    
    <!-- 输入提示 -->
    <div class="input-hints" v-if="showHints">
      <div class="hint-item">
        <el-tag size="small" type="info">Enter</el-tag>
        <span>发送消息</span>
      </div>
      <div class="hint-item">
        <el-tag size="small" type="info">Shift+Enter</el-tag>
        <span>换行</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { Position } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: '输入消息...'
  }
})

// Emits
const emit = defineEmits(['send-message'])

// Refs
const inputRef = ref(null)
const messageText = ref('')
const showHints = ref(false)

// 计算属性
const canSend = computed(() => {
  return messageText.value.trim().length > 0 && !props.disabled
})

// 监听disabled状态变化，自动聚焦
watch(() => props.disabled, (newVal) => {
  if (!newVal) {
    nextTick(() => {
      focusInput()
    })
  }
})

// 方法
const handleKeyDown = (event) => {
  if (event.key === 'Enter') {
    if (event.shiftKey) {
      // Shift+Enter: 换行，不处理
      return
    } else {
      // Enter: 发送消息
      event.preventDefault()
      sendMessage()
    }
  }
}

const handleInput = () => {
  // 可以在这里处理输入事件，比如显示正在输入状态
}

const sendMessage = () => {
  if (!canSend.value) return
  
  const content = messageText.value.trim()
  if (content) {
    emit('send-message', content)
    messageText.value = ''
    
    // 重新聚焦输入框
    nextTick(() => {
      focusInput()
    })
  }
}

const focusInput = () => {
  if (inputRef.value) {
    inputRef.value.focus()
  }
}

const clearInput = () => {
  messageText.value = ''
  focusInput()
}

// 暴露方法给父组件
defineExpose({
  focusInput,
  clearInput
})

// 组件挂载后自动聚焦
onMounted(() => {
  focusInput()
})
</script>

<style scoped>
.message-input {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e4e7ed;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.input-container :deep(.el-textarea) {
  flex: 1;
}

.input-container :deep(.el-textarea__inner) {
  border-radius: 12px;
  padding: 12px 16px;
  border: 1px solid #dcdfe6;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  transition: border-color 0.2s;
}

.input-container :deep(.el-textarea__inner):focus {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.input-container :deep(.el-textarea__inner)::placeholder {
  color: #c0c4cc;
}

.input-actions {
  display: flex;
  align-items: center;
  padding-bottom: 2px;
}

.input-hints {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-input {
    padding: 12px 16px;
  }
  
  .input-container {
    gap: 8px;
  }
  
  .input-hints {
    display: none;
  }
}
</style>