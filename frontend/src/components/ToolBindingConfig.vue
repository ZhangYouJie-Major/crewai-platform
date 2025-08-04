<template>
  <div class="tool-binding-config">
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
              优先级: {{ binding.order }}
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
                :disabled="binding.order <= 1"
                title="提高优先级"
              />
              <el-button 
                icon="Bottom" 
                @click="adjustPriority(binding, 'down')"
                :disabled="binding.order >= currentBindings.length"
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
            v-for="tool in availableToolsForBinding"
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
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tools, Plus, Top, Bottom, Delete } from '@element-plus/icons-vue'
import api from '@/services/api'

const props = defineProps({
  agentId: {
    type: [String, Number],
    required: true
  },
  availableTools: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['tools-updated'])

// 响应式数据
const currentBindings = ref([])
const selectedToolId = ref('')
const newToolPriority = ref(1)
const loading = ref(false)

// 计算属性
const availableToolsForBinding = computed(() => {
  const boundToolIds = currentBindings.value.map(binding => binding.tool)
  return props.availableTools.filter(tool => !boundToolIds.includes(tool.id))
})

// 方法
const loadCurrentBindings = async () => {
  if (!props.agentId) return
  
  try {
    loading.value = true
    const response = await api.getAgentToolRelations({ agent_id: props.agentId })
    const relations = response.data.results || response.data || []
    currentBindings.value = relations.sort((a, b) => a.order - b.order)
    console.log('加载到的工具绑定:', relations)
  } catch (error) {
    console.error('加载工具绑定失败:', error)
    ElMessage.error('加载工具绑定失败')
  } finally {
    loading.value = false
  }
}

const getToolName = (toolId) => {
  const tool = props.availableTools.find(t => t.id === toolId)
  return tool ? tool.name : '未知工具'
}

const getToolDescription = (toolId) => {
  const tool = props.availableTools.find(t => t.id === toolId)
  return tool ? tool.description || '无描述' : ''
}

const addBinding = async () => {
  if (!selectedToolId.value || !props.agentId) return

  try {
    const bindingData = {
      agent: props.agentId,
      tool: selectedToolId.value,
      order: newToolPriority.value
    }

    await api.createAgentToolRelation(bindingData)
    ElMessage.success('工具绑定成功')
    
    selectedToolId.value = ''
    newToolPriority.value = currentBindings.value.length + 2
    await loadCurrentBindings()
    emit('tools-updated')
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
    emit('tools-updated')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除工具绑定失败:', error)
      ElMessage.error('移除工具绑定失败')
    }
  }
}

const adjustPriority = async (binding, direction) => {
  try {
    let newOrder = binding.order
    
    if (direction === 'up') {
      newOrder = Math.max(1, binding.order - 1)
    } else {
      newOrder = Math.min(currentBindings.value.length, binding.order + 1)
    }

    // 交换优先级
    const targetBinding = currentBindings.value.find(b => b.order === newOrder)
    if (targetBinding) {
      await api.updateAgentToolRelation(targetBinding.id, { order: binding.order })
    }
    
    await api.updateAgentToolRelation(binding.id, { order: newOrder })
    ElMessage.success('优先级调整成功')
    await loadCurrentBindings()
    emit('tools-updated')
  } catch (error) {
    console.error('调整优先级失败:', error)
    ElMessage.error('调整优先级失败')
  }
}

// 监听器
watch(() => props.agentId, (newAgentId) => {
  if (newAgentId) {
    loadCurrentBindings()
    newToolPriority.value = currentBindings.value.length + 1
  }
})

// 生命周期
onMounted(() => {
  if (props.agentId) {
    loadCurrentBindings()
  }
})
</script>

<style scoped>
.tool-binding-config {
  max-height: 600px;
  overflow-y: auto;
}

.current-tools-section,
.add-tools-section {
  margin-bottom: 30px;
}

.current-tools-section h3,
.add-tools-section h3 {
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
</style> 