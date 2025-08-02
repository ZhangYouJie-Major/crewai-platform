<template>
  <div class="agent-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>CrewAI Agent管理</h2>
        <p class="page-description">管理和配置您的CrewAI智能代理</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          icon="Plus" 
          @click="handleCreateAgent"
          :loading="loading"
        >
          创建Agent
        </el-button>
        <el-button 
          icon="Refresh" 
          @click="fetchAgents"
          :loading="loading"
        >
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-row :gutter="20">
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            placeholder="搜索Agent名称或描述"
            prefix-icon="Search"
            clearable
            @input="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="statusFilter"
            placeholder="筛选状态"
            clearable
            @change="handleFilter"
          >
            <el-option label="全部" value="" />
            <el-option label="活跃" value="active" />
            <el-option label="非活跃" value="inactive" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="modelFilter"
            placeholder="筛选模型"
            clearable
            @change="handleFilter"
          >
            <el-option label="全部模型" value="" />
            <el-option 
              v-for="model in llmModels" 
              :key="model.id" 
              :label="model.name" 
              :value="model.id"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="viewMode"
            @change="handleViewModeChange"
          >
            <el-option label="卡片视图" value="card" />
            <el-option label="列表视图" value="list" />
          </el-select>
        </el-col>
      </el-row>
    </div>

    <!-- 统计信息 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ totalAgents }}</div>
              <div class="stat-label">总Agent数</div>
            </div>
            <el-icon class="stat-icon" color="#409EFF"><User /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ activeAgents }}</div>
              <div class="stat-label">活跃Agent</div>
            </div>
            <el-icon class="stat-icon" color="#67C23A"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ totalTools }}</div>
              <div class="stat-label">绑定工具数</div>
            </div>
            <el-icon class="stat-icon" color="#E6A23C"><Tools /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ llmModels.length }}</div>
              <div class="stat-label">可用模型</div>
            </div>
            <el-icon class="stat-icon" color="#F56C6C"><Cpu /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Agent列表 -->
    <div class="agents-section">
      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="agents-grid">
        <el-row :gutter="20">
          <el-col 
            v-for="agent in filteredAgents" 
            :key="agent.id" 
            :xl="6" 
            :lg="8" 
            :md="12" 
            :sm="24"
            class="agent-col"
          >
            <AgentCard
              :agent="agent"
              @refresh="fetchAgents"
              @view-details="handleViewDetails"
              @manage-tools="handleManageTools"
              @execute-task="handleExecuteTask"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 列表视图 -->
      <div v-else class="agents-table">
        <el-table
          :data="filteredAgents"
          v-loading="loading"
          stripe
          border
          style="width: 100%"
          @row-click="handleRowClick"
        >
          <el-table-column prop="name" label="Agent名称" min-width="150">
            <template #default="{ row }">
              <div class="agent-name">
                <el-avatar :size="32" class="agent-avatar">
                  {{ row.name.charAt(0).toUpperCase() }}
                </el-avatar>
                <div class="name-info">
                  <div class="name">{{ row.name }}</div>
                  <div class="role">{{ row.role || '未设置角色' }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="llm_model" label="LLM模型" width="120">
            <template #default="{ row }">
              <el-tag size="small" type="info">
                {{ getLLMModelName(row.llm_model) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="绑定工具" width="100">
            <template #default="{ row }">
              <el-badge :value="getAgentToolCount(row.id)" class="tool-badge">
                <el-icon><Tools /></el-icon>
              </el-badge>
            </template>
          </el-table-column>
          
          <el-table-column prop="is_active" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '活跃' : '非活跃' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="350" fixed="right">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button type="primary" icon="Edit" @click.stop="handleEditAgent(row)">
                  编辑
                </el-button>
                <el-button type="success" icon="CopyDocument" @click.stop="handleCloneAgent(row)">
                  克隆
                </el-button>
                <el-button 
                  :type="row.is_active ? 'warning' : 'success'" 
                  :icon="row.is_active ? 'VideoPause' : 'VideoPlay'"
                  @click.stop="handleToggleStatus(row)"
                >
                  {{ row.is_active ? '停用' : '启用' }}
                </el-button>
                <el-button type="info" icon="Tools" @click.stop="handleManageTools(row)">
                  工具
                </el-button>
                <el-button type="danger" icon="Delete" @click.stop="handleDeleteAgent(row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredAgents.length === 0 && !loading" 
        description="暂无Agent数据"
        :image-size="120"
      >
        <el-button type="primary" @click="handleCreateAgent">
          创建第一个Agent
        </el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div class="pagination-section" v-if="totalAgents > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="totalAgents"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- Agent配置弹窗 -->
    <AgentConfigDialog
      v-model="configDialogVisible"
      :agent="currentAgent"
      @saved="handleConfigSuccess"
    />

    <!-- 工具绑定弹窗 -->
    <ToolBindingDialog
      v-model:visible="toolBindingVisible"
      :agent="currentAgent"
      :mcp-tools="mcpTools"
      @success="handleToolBindingSuccess"
    />

    <!-- 任务执行弹窗 -->
    <TaskExecutionDialog
      v-model:visible="taskExecutionVisible"
      :agent="currentAgent"
      @success="handleTaskExecutionSuccess"
    />

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, User, CircleCheck, Tools, Cpu,
  Edit, Delete, VideoPause, VideoPlay, CopyDocument
} from '@element-plus/icons-vue'
import AgentCard from '@/components/AgentCard.vue'
import AgentConfigDialog from '@/components/AgentConfigDialog.vue'
import ToolBindingDialog from '@/components/ToolBindingDialog.vue'
import TaskExecutionDialog from '@/components/TaskExecutionDialog.vue'
import api from '@/services/api'

// 响应式数据
const loading = ref(false)
const agents = ref([])
const llmModels = ref([])
const mcpTools = ref([])
const agentToolRelations = ref([])

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')
const modelFilter = ref('')
const viewMode = ref('card')

// 分页
const currentPage = ref(1)
const pageSize = ref(24)

// 弹窗状态
const configDialogVisible = ref(false)
const toolBindingVisible = ref(false)
const taskExecutionVisible = ref(false)
const currentAgent = ref(null)
const isEditMode = ref(false)

// 计算属性
const totalAgents = computed(() => agents.value.length)
const activeAgents = computed(() => agents.value.filter(agent => agent.is_active).length)
const totalTools = computed(() => agentToolRelations.value.length)

const filteredAgents = computed(() => {
  let filtered = agents.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(agent => 
      agent.name.toLowerCase().includes(query) ||
      (agent.role && agent.role.toLowerCase().includes(query)) ||
      (agent.goal && agent.goal.toLowerCase().includes(query))
    )
  }

  // 状态筛选
  if (statusFilter.value) {
    if (statusFilter.value === 'active') {
      filtered = filtered.filter(agent => agent.is_active)
    } else if (statusFilter.value === 'inactive') {
      filtered = filtered.filter(agent => !agent.is_active)
    }
  }

  // 模型筛选
  if (modelFilter.value) {
    filtered = filtered.filter(agent => agent.llm_model == modelFilter.value)
  }

  return filtered
})

// 方法
const fetchAgents = async () => {
  try {
    loading.value = true
    const response = await api.getCrewAIAgents()
    // 处理分页数据或直接数组数据
    agents.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取Agent列表失败:', error)
    ElMessage.error('获取Agent列表失败')
  } finally {
    loading.value = false
  }
}

const fetchLLMModels = async () => {
  try {
    const response = await api.getLLMModels()
    llmModels.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取LLM模型列表失败:', error)
  }
}

const fetchMCPTools = async () => {
  try {
    const response = await api.getMCPTools()
    mcpTools.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取MCP工具列表失败:', error)
  }
}

const fetchAgentToolRelations = async () => {
  try {
    const response = await api.getAgentToolRelations()
    agentToolRelations.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取Agent工具关联失败:', error)
  }
}

const getLLMModelName = (modelId) => {
  const model = llmModels.value.find(m => m.id === modelId)
  return model ? model.name : '未知模型'
}

const getAgentToolCount = (agentId) => {
  return agentToolRelations.value.filter(rel => rel.agent === agentId).length
}

const getAgentTools = (agentId) => {
  const relationIds = agentToolRelations.value
    .filter(rel => rel.agent === agentId)
    .map(rel => rel.mcp_tool)
  return mcpTools.value.filter(tool => relationIds.includes(tool.id))
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 事件处理
const handleCreateAgent = () => {
  currentAgent.value = null
  isEditMode.value = false
  configDialogVisible.value = true
}

const handleEditAgent = (agent) => {
  currentAgent.value = { ...agent }
  isEditMode.value = true
  configDialogVisible.value = true
}

const handleCloneAgent = async (agent) => {
  try {
    // 创建克隆的Agent数据，移除ID和时间戳字段
    const clonedAgent = { ...agent }
    
    // 移除不需要的字段（只读字段、统计字段、关联信息等）
    delete clonedAgent.id
    delete clonedAgent.created_at
    delete clonedAgent.updated_at
    delete clonedAgent.status
    delete clonedAgent.status_display
    delete clonedAgent.total_tasks
    delete clonedAgent.completed_tasks
    delete clonedAgent.total_execution_time
    delete clonedAgent.last_execution
    delete clonedAgent.last_error
    delete clonedAgent.owner
    delete clonedAgent.owner_info
    delete clonedAgent.success_rate
    delete clonedAgent.avg_execution_time
    delete clonedAgent.bound_tools_count
    delete clonedAgent.llm_model_info
    delete clonedAgent.function_calling_llm_info
    delete clonedAgent.allowed_users
    
    // 修改名称以避免重复
    clonedAgent.name = `${agent.name}_copy_${Date.now()}`
    clonedAgent.display_name = `${agent.display_name || agent.name} (副本)`
    clonedAgent.is_public = false // 克隆的Agent默认为私有
    
    // 创建新Agent
    await api.createCrewAIAgent(clonedAgent)
    ElMessage.success('Agent克隆成功')
    await fetchAgents()
  } catch (error) {
    console.error('克隆Agent失败:', error)
    ElMessage.error('克隆Agent失败')
  }
}

const handleDeleteAgent = async (agent) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除Agent "${agent.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await api.deleteCrewAIAgent(agent.id)
    ElMessage.success('删除成功')
    await fetchAgents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除Agent失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleToggleStatus = async (agent) => {
  try {
    const newStatus = !agent.is_active
    await api.updateCrewAIAgent(agent.id, { is_active: newStatus })
    ElMessage.success(`Agent已${newStatus ? '启用' : '停用'}`)
    await fetchAgents()
  } catch (error) {
    console.error('更新Agent状态失败:', error)
    ElMessage.error('状态更新失败')
  }
}


const handleExecuteTask = (agent) => {
  currentAgent.value = agent
  taskExecutionVisible.value = true
}

const handleManageTools = (agent) => {
  currentAgent.value = agent
  toolBindingVisible.value = true
}

const handleViewDetails = (agent) => {
  handleEditAgent(agent)
}

const handleRowClick = (row) => {
  handleViewDetails(row)
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleViewModeChange = () => {
  // 视图模式切换时保持当前筛选状态
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

const handleConfigSuccess = () => {
  configDialogVisible.value = false
  fetchAgents()
}

const handleToolBindingSuccess = () => {
  toolBindingVisible.value = false
  fetchAgentToolRelations()
}

const handleTaskExecutionSuccess = () => {
  taskExecutionVisible.value = false
}

// 初始化
onMounted(async () => {
  await Promise.all([
    fetchAgents(),
    fetchLLMModels(),
    fetchMCPTools(),
    fetchAgentToolRelations()
  ])
})
</script>

<style scoped>
.agent-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 12px;
}

.filter-section {
  margin-bottom: 20px;
}

.stats-section {
  margin-bottom: 20px;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-content .stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-content .stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.stat-icon {
  font-size: 32px;
  opacity: 0.8;
}

.agents-section {
  margin-bottom: 20px;
}

.agents-grid .agent-col {
  margin-bottom: 20px;
}

.agents-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.agent-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: bold;
}

.name-info .name {
  font-weight: 500;
  color: #303133;
}

.name-info .role {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.tool-badge {
  cursor: pointer;
}

.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}


@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-right {
    width: 100%;
    justify-content: flex-end;
  }

  .filter-section .el-row {
    flex-direction: column;
    gap: 12px;
  }

  .agents-grid .agent-col {
    padding: 0 10px;
  }
}
</style>