<template>
  <div class="agent-panel">
    <!-- 面板头部 -->
    <div class="panel-header">
      <h4>智能助手</h4>
    </div>
    
    <!-- 当前Agent信息 -->
    <div class="current-agent-section" v-if="currentAgent">
      <div class="section-title">当前助手</div>
      <div class="agent-card current">
        <div class="agent-avatar">
          <el-avatar :size="40">
            <el-icon><Avatar /></el-icon>
          </el-avatar>
        </div>
        <div class="agent-info">
          <div class="agent-name">{{ currentAgent.name }}</div>
          <div class="agent-role">{{ currentAgent.role }}</div>
          <div class="agent-description">{{ currentAgent.goal || '暂无描述' }}</div>
        </div>
      </div>
    </div>
    
    <!-- Agent选择模式 -->
    <div class="selection-mode-section">
      <div class="section-title">选择模式</div>
      <el-radio-group 
        :model-value="conversation.agent_selection_mode" 
        size="small"
        @change="handleModeChange"
      >
        <el-radio-button label="manual">手动选择</el-radio-button>
        <el-radio-button label="auto">自动选择</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 可用Agent列表 -->
    <div class="available-agents-section" v-if="conversation.agent_selection_mode === 'manual'">
      <div class="section-title">
        <span>可用助手</span>
        <el-tag size="small">{{ availableAgents.length }}</el-tag>
      </div>
      
      <div class="agent-list" v-loading="agentsLoading">
        <div 
          v-for="agent in availableAgents" 
          :key="agent.id"
          class="agent-card"
          :class="{ selected: agent.id === conversation.primary_agent }"
          @click="selectAgent(agent.id)"
        >
          <div class="agent-avatar">
            <el-avatar :size="32">
              <el-icon><Avatar /></el-icon>
            </el-avatar>
          </div>
          
          <div class="agent-info">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="agent-role">{{ agent.role }}</div>
            <div class="agent-stats">
              <el-tag size="small" type="info">
                工具: {{ agent.tools_count || 0 }}
              </el-tag>
            </div>
          </div>
          
          <div class="agent-status" v-if="agent.id === conversation.primary_agent">
            <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="!agentsLoading && availableAgents.length === 0" class="empty-agents">
          <el-empty 
            description="暂无可用助手"
            :image-size="60"
          >
            <el-button type="primary" size="small" @click="$emit('create-agent')">
              创建助手
            </el-button>
          </el-empty>
        </div>
      </div>
    </div>
    
    <!-- 自动模式提示 -->
    <div class="auto-mode-tip" v-else>
      <el-alert
        title="自动选择模式"
        description="系统将根据对话内容自动选择最合适的助手"
        type="info"
        :closable="false"
        :show-icon="true"
      />
    </div>
    
    <!-- 会话设置 -->
    <div class="conversation-settings-section">
      <div class="section-title">对话设置</div>
      
      <div class="setting-item">
        <label>对话标题</label>
        <el-input
          :model-value="conversation.title"
          @blur="updateTitle"
          size="small"
          placeholder="输入对话标题..."
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Avatar, CircleCheckFilled } from '@element-plus/icons-vue'
import { ApiService } from '@/services/api'

// Props
const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  availableAgents: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['agent-select', 'settings-change', 'create-agent'])

// 响应式数据
const agentsLoading = ref(false)

// 计算属性
const currentAgent = computed(() => {
  return props.availableAgents.find(agent => agent.id === props.conversation.primary_agent)
})

// 方法
const selectAgent = async (agentId) => {
  if (agentId === props.conversation.primary_agent) return
  
  try {
    emit('agent-select', agentId)
  } catch (error) {
    console.error('选择Agent失败:', error)
    ElMessage.error('选择助手失败')
  }
}

const handleModeChange = (mode) => {
  emit('settings-change', { agent_selection_mode: mode })
}

const updateTitle = (event) => {
  const newTitle = event.target.value.trim()
  if (newTitle && newTitle !== props.conversation.title) {
    emit('settings-change', { title: newTitle })
  }
}
</script>

<style scoped>
.agent-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 20px;
  overflow-y: auto;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

.agent-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 8px;
}

.agent-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.agent-card.current {
  border-color: #67c23a;
  background: #f0f9ff;
}

.agent-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-role {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-description {
  font-size: 11px;
  color: #c0c4cc;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.agent-status {
  display: flex;
  align-items: center;
}

.selection-mode-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.selection-mode-section :deep(.el-radio-group) {
  width: 100%;
}

.selection-mode-section :deep(.el-radio-button) {
  flex: 1;
}

.selection-mode-section :deep(.el-radio-button__inner) {
  width: 100%;
  text-align: center;
}

.available-agents-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.agent-list {
  max-height: 300px;
  overflow-y: auto;
}

.empty-agents {
  text-align: center;
  padding: 20px;
}

.auto-mode-tip {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.conversation-settings-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.setting-item {
  margin-bottom: 12px;
}

.setting-item label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 4px;
}
</style>