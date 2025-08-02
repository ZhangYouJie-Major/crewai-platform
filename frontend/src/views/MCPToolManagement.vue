<template>
  <div class="mcp-tool-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h2>MCP工具管理</h2>
        <p class="page-description">管理和配置您的MCP（Model Context Protocol）工具</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          icon="Plus" 
          @click="handleCreateTool"
          :loading="loading"
        >
          添加工具
        </el-button>
        <el-button 
          icon="Refresh" 
          @click="fetchTools"
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
            placeholder="搜索工具名称或描述"
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
            <el-option label="健康" value="healthy" />
            <el-option label="异常" value="unhealthy" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select
            v-model="typeFilter"
            placeholder="筛选类型"
            clearable
            @change="handleFilter"
          >
            <el-option label="全部类型" value="" />
            <el-option label="公开" value="public" />
            <el-option label="私有" value="private" />
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
              <div class="stat-number">{{ totalTools }}</div>
              <div class="stat-label">总工具数</div>
            </div>
            <el-icon class="stat-icon" color="#409EFF"><Tools /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ healthyTools }}</div>
              <div class="stat-label">健康工具</div>
            </div>
            <el-icon class="stat-icon" color="#67C23A"><CircleCheck /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ publicTools }}</div>
              <div class="stat-label">公开工具</div>
            </div>
            <el-icon class="stat-icon" color="#E6A23C"><Share /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-number">{{ privateTools }}</div>
              <div class="stat-label">私有工具</div>
            </div>
            <el-icon class="stat-icon" color="#F56C6C"><Lock /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 工具列表 -->
    <div class="tools-section">
      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="tools-grid">
        <el-row :gutter="20">
          <el-col 
            v-for="tool in filteredTools" 
            :key="tool.id" 
            :xl="6" 
            :lg="8" 
            :md="12" 
            :sm="24"
            class="tool-col"
          >
            <MCPToolCard
              :tool="tool"
              @edit="handleEditTool"
              @delete="handleDeleteTool"
              @test="handleTestTool"
              @call="handleCallTool"
            />
          </el-col>
        </el-row>
      </div>

      <!-- 列表视图 -->
      <div v-else class="tools-table">
        <el-table
          :data="filteredTools"
          v-loading="loading"
          stripe
          border
          style="width: 100%"
          @row-click="handleRowClick"
        >
          <el-table-column prop="name" label="工具名称" min-width="150">
            <template #default="{ row }">
              <div class="tool-name">
                <el-icon class="tool-icon" :style="{ color: getToolIconColor(row.health_status) }">
                  <Tools />
                </el-icon>
                <div class="name-info">
                  <div class="name">{{ row.name }}</div>
                  <div class="description">{{ row.description || '无描述' }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="server_url" label="服务地址" width="200">
            <template #default="{ row }">
              <el-text class="url-text" size="small">{{ row.server_url }}</el-text>
            </template>
          </el-table-column>
          
          <el-table-column label="健康状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getHealthType(row.health_status)" size="small">
                {{ getHealthText(row.health_status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="is_public" label="可见性" width="80">
            <template #default="{ row }">
              <el-tag :type="row.is_public ? 'success' : 'info'" size="small">
                {{ row.is_public ? '公开' : '私有' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="250" fixed="right">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button type="primary" icon="Edit" @click.stop="handleEditTool(row)">
                  编辑
                </el-button>
                <el-button type="info" icon="Monitor" @click.stop="handleTestTool(row)">
                  测试
                </el-button>
                <el-button type="success" icon="VideoPlay" @click.stop="handleCallTool(row)">
                  调用
                </el-button>
                <el-button type="danger" icon="Delete" @click.stop="handleDeleteTool(row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty 
        v-if="filteredTools.length === 0 && !loading" 
        description="暂无工具数据"
        :image-size="120"
      >
        <el-button type="primary" @click="handleCreateTool">
          添加第一个工具
        </el-button>
      </el-empty>
    </div>

    <!-- 分页 -->
    <div class="pagination-section" v-if="totalTools > 0">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 48, 96]"
        :total="totalTools"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 工具配置弹窗 -->
    <MCPToolConfigDialog
      v-model:visible="configDialogVisible"
      :tool="currentTool"
      :is-edit="isEditMode"
      @success="handleConfigSuccess"
    />

    <!-- 工具调用弹窗 -->
    <MCPToolCallDialog
      v-model:visible="callDialogVisible"
      :tool="currentTool"
      @success="handleCallSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Refresh, Search, Tools, CircleCheck, Share, Lock,
  Edit, Delete, Monitor, VideoPlay
} from '@element-plus/icons-vue'
import MCPToolCard from '@/components/MCPToolCard.vue'
import MCPToolConfigDialog from '@/components/MCPToolConfigDialog.vue'
import MCPToolCallDialog from '@/components/MCPToolCallDialog.vue'
import api from '@/services/api'

// 响应式数据
const loading = ref(false)
const tools = ref([])

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const viewMode = ref('card')

// 分页
const currentPage = ref(1)
const pageSize = ref(24)

// 弹窗状态
const configDialogVisible = ref(false)
const callDialogVisible = ref(false)
const currentTool = ref(null)
const isEditMode = ref(false)

// 计算属性
const totalTools = computed(() => tools.value.length)
const healthyTools = computed(() => tools.value.filter(tool => tool.health_status === 'healthy').length)
const publicTools = computed(() => tools.value.filter(tool => tool.is_public).length)
const privateTools = computed(() => tools.value.filter(tool => !tool.is_public).length)

const filteredTools = computed(() => {
  let filtered = tools.value

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tool => 
      tool.name.toLowerCase().includes(query) ||
      (tool.description && tool.description.toLowerCase().includes(query)) ||
      (tool.server_url && tool.server_url.toLowerCase().includes(query))
    )
  }

  // 健康状态筛选
  if (statusFilter.value) {
    if (statusFilter.value === 'healthy') {
      filtered = filtered.filter(tool => tool.health_status === 'healthy')
    } else if (statusFilter.value === 'unhealthy') {
      filtered = filtered.filter(tool => tool.health_status !== 'healthy')
    }
  }

  // 类型筛选
  if (typeFilter.value) {
    if (typeFilter.value === 'public') {
      filtered = filtered.filter(tool => tool.is_public)
    } else if (typeFilter.value === 'private') {
      filtered = filtered.filter(tool => !tool.is_public)
    }
  }

  return filtered
})

// 方法
const fetchTools = async () => {
  try {
    loading.value = true
    const response = await api.getMCPTools()
    tools.value = response.data.results || response.data || []
  } catch (error) {
    console.error('获取工具列表失败:', error)
    ElMessage.error('获取工具列表失败')
  } finally {
    loading.value = false
  }
}

const getToolIconColor = (healthStatus) => {
  const colorMap = {
    'healthy': '#67C23A',
    'unhealthy': '#F56C6C',
    'warning': '#E6A23C'
  }
  return colorMap[healthStatus] || '#909399'
}

const getHealthType = (healthStatus) => {
  const typeMap = {
    'healthy': 'success',
    'unhealthy': 'danger',
    'warning': 'warning'
  }
  return typeMap[healthStatus] || 'info'
}

const getHealthText = (healthStatus) => {
  const textMap = {
    'healthy': '健康',
    'unhealthy': '异常',
    'warning': '警告'
  }
  return textMap[healthStatus] || '未知'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

// 事件处理
const handleCreateTool = () => {
  currentTool.value = null
  isEditMode.value = false
  configDialogVisible.value = true
}

const handleEditTool = (tool) => {
  currentTool.value = { ...tool }
  isEditMode.value = true
  configDialogVisible.value = true
}

const handleDeleteTool = async (tool) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除工具 "${tool.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    await api.deleteMCPTool(tool.id)
    ElMessage.success('删除成功')
    await fetchTools()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除工具失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleTestTool = async (tool) => {
  try {
    loading.value = true
    const response = await api.healthCheckMCPTool(tool.id)
    if (response.data.healthy) {
      ElMessage.success('工具健康检查通过')
    } else {
      ElMessage.warning('工具健康检查失败')
    }
    await fetchTools() // 刷新状态
  } catch (error) {
    console.error('测试工具失败:', error)
    ElMessage.error('测试失败')
  } finally {
    loading.value = false
  }
}

const handleCallTool = (tool) => {
  currentTool.value = tool
  callDialogVisible.value = true
}

const handleRowClick = (row) => {
  // 点击行时的处理逻辑
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
  fetchTools()
}

const handleCallSuccess = () => {
  callDialogVisible.value = false
}

// 初始化
onMounted(async () => {
  await fetchTools()
})
</script>

<style scoped>
.mcp-tool-management {
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

.tools-section {
  margin-bottom: 20px;
}

.tools-grid .tool-col {
  margin-bottom: 20px;
}

.tools-table {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tool-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.name-info .name {
  font-weight: 500;
  color: #303133;
}

.name-info .description {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.url-text {
  font-family: monospace;
  font-size: 12px;
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

  .tools-grid .tool-col {
    padding: 0 10px;
  }
}
</style>