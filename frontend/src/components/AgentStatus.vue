<template>
  <div class="agent-status">
    <div class="status-indicator">
      <el-icon class="thinking-icon is-loading"><Loading /></el-icon>
      <span class="status-text">{{ agentName }} 正在思考中...</span>
    </div>
  </div>
</template>

<script setup>
import { Loading } from '@element-plus/icons-vue'

// Props
defineProps({
  agentName: {
    type: String,
    default: 'Assistant'
  }
})
</script>

<style scoped>
.agent-status {
  padding: 12px 20px;
  background: rgba(64, 158, 255, 0.05);
  border-top: 1px solid #e4e7ed;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #409eff;
}

.thinking-icon {
  font-size: 16px;
}

.status-text {
  font-style: italic;
}

@keyframes thinking {
  0% { opacity: 0.5; }
  50% { opacity: 1; }
  100% { opacity: 0.5; }
}

.status-indicator {
  animation: thinking 1.5s ease-in-out infinite;
}
</style>