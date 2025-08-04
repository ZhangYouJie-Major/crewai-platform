<template>
  <el-dialog
    v-model="visible"
    title="管理Agent工具"
    width="800px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <div class="tool-binding-content">
      <!-- 当前绑定的工具 -->
      <div class="current-tools-section">
        <h3>
          <el-icon><Tools /></el-icon>
          当前绑定工具 ({{ currentBindings.length }})
        </h3>
        
        <div v-if="currentBindings.length === 0" class="empty-tools">
          <el-empty description="暂未绑定任何工具" :image-size="80" />
        </div>
        
        <div v-else class="tools-list">
          <div
            v-for="binding in currentBindings"
            :key="binding.id"
            class="tool-item"
          >
            <div class="tool-info">
              <div class="tool-header">
                <span class="tool-name">{{ getToolName(binding.tool) }}</span>
                <el-tag type="info" size="small">
                  优先级: {{ binding.priority }}
                </el-tag>
              </div>
              <div class="tool-description">
                {{ getToolDescription(binding.tool) }}
              </div>
            </div>
            <div class="tool-actions">
              <el-button-group size="small">
                <el-button 
                  icon="Top" 
                  @click="adjustPriority(binding, 'up')"
                  :disabled="binding.priority <= 1"
                  title="提高优先级"
                />
                <el-button 
                  icon="Bottom" 
                  @click="adjustPriority(binding, 'down')"
                  :disabled="binding.priority >= currentBindings.length"
                  title="降低优先级"
                />
                <el-button 
                  type="danger" 
                  icon="Delete" 
                  @click="removeBinding(binding)"
                  title="移除绑定"
                />
              </el-button-group>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加新工具 -->
      <div class="add-tools-section">
        <h3>
          <el-icon><Plus /></el-icon>
          添加工具
        </h3>
        
        <div class="tool-selector">
          <el-select
            v-model="selectedToolId"
            placeholder="选择要添加的工具"
            style="width: 300px; margin-right: 12px;"
            filterable
          >
            <el-option
              v-for="tool in availableTools"
              :key="tool.id"
              :label="tool.name"
              :value="tool.id"
            >
              <div class="option-content">
                <span class="option-name">{{ tool.name }}</span>
                <span class="option-protocol">{{ tool.protocol }}</span>
              </div>
            </el-option>
          </el-select>
          
          <el-input-number
            v-model="newToolPriority"
            :min="1"
            :max="100"
            placeholder="优先级"
            style="width: 120px; margin-right: 12px;"
          />
          
          <el-button 
            type="primary" 
            @click="addBinding"
            :disabled="!selectedToolId"
          >
            <el-icon><Plus /></el-icon>
            添加绑定
          </el-button>
        </div>
      </div>

      <!-- 工具健康检查 -->
      <div class="health-check-section">
        <h3>
          <el-icon><Monitor /></el-icon>
          工具健康检查
        </h3>
        
        <el-button 
          @click="performHealthCheck" 
          :loading="healthChecking"
          style="margin-bottom: 16px;"
        >
          <el-icon><Refresh /></el-icon>
          执行健康检查
        </el-button>
        
        <div v-if="healthResults.length > 0" class="health-results">
          <div
            v-for="result in healthResults"
            :key="result.tool_id"
            class="health-item"
          >
            <div class="health-info">
              <span class="tool-name">{{ getToolName(result.tool_id) }}</span>
              <el-tag 
                :type="result.status === 'healthy' ? 'success' : 'danger'"
                size="small"
              >
                {{ result.status === 'healthy' ? '健康' : '异常' }}
              </el-tag>
            </div>
            <div v-if="result.message" class="health-message">
              {{ result.message }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Tools, Plus, Top, Bottom, Delete, Monitor, Refresh
} from '@element-plus/icons-vue'
import api from '@/services/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  agent: {
    type: Object,
    default: () => null
  },
  mcpTools: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const currentBindings = ref([])
const selectedToolId = ref('')
const newToolPriority = ref(1)
const healthChecking = ref(false)
const healthResults = ref([])
const loading = ref(false)

// 计算属性
const availableTools = computed(() => {
  const boundToolIds = currentBindings.value.map(binding => binding.tool)
  return props.mcpTools.filter(tool => !boundToolIds.includes(tool.id))
})

const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const loadCurrentBindings = async () => {
  if (!props.agent?.id) return
  
  try {
    loading.value = true
    // 使用正确的参数名agent_id进行后端过滤
    const response = await api.getAgentToolRelations({ agent_id: props.agent.id })
    const relations = response.data.results || response.data || []
    currentBindings.value = relations.sort((a, b) => a.priority - b.priority)
    console.log('加载到的工具绑定:', relations)
  } catch (error) {
    console.error('加载工具绑定失败:', error)
    ElMessage.error('加载工具绑定失败')
  } finally {
    loading.value = false
  }
}

const getToolName = (toolId) => {
  const tool = props.mcpTools.find(t => t.id === toolId)
  return tool ? tool.name : '未知工具'
}

const getToolDescription = (toolId) => {
  const tool = props.mcpTools.find(t => t.id === toolId)
  return tool ? tool.description || '无描述' : ''
}

const addBinding = async () => {
  if (!selectedToolId.value || !props.agent?.id) return

  try {
    const bindingData = {
      agent: props.agent.id,
      tool: selectedToolId.value,
      priority: newToolPriority.value
    }

    await api.createAgentToolRelation(bindingData)
    ElMessage.success('工具绑定成功')
    
    selectedToolId.value = ''
    newToolPriority.value = currentBindings.value.length + 2
    await loadCurrentBindings()
  } catch (error) {
    console.error('添加工具绑定失败:', error)
    ElMessage.error('添加工具绑定失败')
  }
}

const removeBinding = async (binding) => {
  try {
    await ElMessageBox.confirm(
      `确定要移除工具 "${getToolName(binding.tool)}" 的绑定吗？`,
      '确认移除',
      {
        confirmButtonText: '移除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.deleteAgentToolRelation(binding.id)
    ElMessage.success('工具绑定已移除')
    await loadCurrentBindings()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除工具绑定失败:', error)
      ElMessage.error('移除工具绑定失败')
    }
  }
}

const adjustPriority = async (binding, direction) => {
  try {
    let newPriority = binding.priority
    
    if (direction === 'up') {
      newPriority = Math.max(1, binding.priority - 1)
    } else {
      newPriority = Math.min(currentBindings.value.length, binding.priority + 1)
    }

    // 交换优先级
    const targetBinding = currentBindings.value.find(b => b.priority === newPriority)
    if (targetBinding) {
      await api.updateAgentToolRelation(targetBinding.id, { priority: binding.priority })
    }
    
    await api.updateAgentToolRelation(binding.id, { priority: newPriority })
    ElMessage.success('优先级调整成功')
    await loadCurrentBindings()
  } catch (error) {
    console.error('调整优先级失败:', error)
    ElMessage.error('调整优先级失败')
  }
}

const performHealthCheck = async () => {
  if (currentBindings.value.length === 0) {
    ElMessage.warning('没有绑定的工具需要检查')
    return
  }

  try {
    healthChecking.value = true
    healthResults.value = []

    for (const binding of currentBindings.value) {
      try {
        const response = await api.healthCheckMCPTool(binding.tool)
        healthResults.value.push({
          tool_id: binding.tool,
          status: response.data.status,
          message: response.data.message
        })
      } catch (error) {
        console.error(`健康检查失败: ${binding.tool}`, error)
        healthResults.value.push({
          tool_id: binding.tool,
          status: 'error',
          message: error.response?.data?.message || error.message || '健康检查失败'
        })
      }
    }

    console.log(healthResults.value)
    const healthyCount = healthResults.value.filter(r => r.status === 'healthy').length
    const totalCount = healthResults.value.length
    
    if (healthyCount === totalCount) {
      ElMessage.success(`健康检查完成，所有工具 (${totalCount}) 运行正常`)
    } else {
      ElMessage.warning(`健康检查完成，${healthyCount}/${totalCount} 个工具正常`)
    }
  } catch (error) {
    console.error('健康检查失败:', error)
    ElMessage.error('健康检查失败')
  } finally {
    healthChecking.value = false
  }
}

const handleSave = () => {
  emit('success')
  visible.value = false
}

const handleClose = () => {
  visible.value = false
}

const handleClosed = () => {
  currentBindings.value = []
  selectedToolId.value = ''
  newToolPriority.value = 1
  healthResults.value = []
}

// 监听器
watch(() => props.visible, (newVisible) => {
  if (newVisible && props.agent) {
    loadCurrentBindings()
    newToolPriority.value = currentBindings.value.length + 1
  }
})

// 生命周期
onMounted(() => {
  if (props.visible && props.agent) {
    loadCurrentBindings()
  }
})
</script>

<style scoped>
.tool-binding-content {
  max-height: 600px;
  overflow-y: auto;
}

.current-tools-section,
.add-tools-section,
.health-check-section {
  margin-bottom: 30px;
}

.current-tools-section h3,
.add-tools-section h3,
.health-check-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.empty-tools {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.tools-list {
  space-y: 12px;
}

.tool-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  margin-bottom: 12px;
}

.tool-info {
  flex: 1;
  margin-right: 16px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.tool-name {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.tool-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.tool-actions {
  flex-shrink: 0;
}

.tool-selector {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.option-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.option-name {
  font-weight: 500;
}

.option-protocol {
  font-size: 12px;
  color: #909399;
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.health-results {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
}

.health-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.health-item:last-child {
  border-bottom: none;
}

.health-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.health-message {
  font-size: 12px;
  color: #606266;
  margin-left: 16px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tool-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .tool-info {
    margin-right: 0;
    width: 100%;
  }
  
  .tool-actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
  
  .tool-selector {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tool-selector .el-select,
  .tool-selector .el-input-number,
  .tool-selector .el-button {
    width: 100%;
    margin: 0 0 8px 0;
  }
}
</style>