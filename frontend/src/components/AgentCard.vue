<template>
  <el-card 
    class="agent-card" 
    shadow="hover"
    :class="{ 'agent-inactive': !agent.is_active }"
  >
    <!-- 卡片头部 -->
    <template #header>
      <div class="card-header">
        <div class="agent-title">
          <span class="agent-name">{{ agent.display_name || agent.name }}</span>
          <el-tag 
            :type="getStatusType(agent.status)" 
            size="small"
            class="status-tag"
          >
            {{ getStatusText(agent.status) }}
          </el-tag>
        </div>
        <div class="card-actions">
          <el-button-group size="small">
            <el-dropdown @command="handleDropdownCommand">
              <el-button :icon="More" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="details" :icon="View">查看详情</el-dropdown-item>
                  <el-dropdown-item command="clone" :icon="CopyDocument">克隆Agent</el-dropdown-item>
                  <el-dropdown-item command="tools" :icon="Tools">管理工具</el-dropdown-item>
                  <el-dropdown-item 
                    command="toggle" 
                    :icon="agent.is_active ? SwitchButton : Open"
                  >
                    {{ agent.is_active ? '禁用' : '启用' }}
                  </el-dropdown-item>
                  <el-dropdown-item 
                    command="delete" 
                    :icon="Delete" 
                    :disabled="agent.status === 'running'"
                    class="danger-item"
                  >
                    删除Agent
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-button-group>
        </div>
      </div>
    </template>

    <!-- 卡片内容 -->
    <div class="agent-content">
      <!-- 角色和目标 -->
      <div class="role-section">
        <div class="role-info">
          <el-icon class="role-icon"><Avatar /></el-icon>
          <div>
            <div class="role-title">{{ agent.role }}</div>
            <div class="goal-desc" :title="agent.goal">{{ truncateText(agent.goal, 100) }}</div>
          </div>
        </div>
      </div>

      <!-- 模型和工具信息 -->
      <div class="info-grid">
        <div class="info-item">
          <el-icon class="info-icon"><Cpu /></el-icon>
          <div class="info-content">
            <span class="info-label">LLM模型</span>
            <span class="info-value">{{ agent.llm_model_info?.name || '未配置' }}</span>
          </div>
        </div>
        
        <div class="info-item">
          <el-icon class="info-icon"><Tools /></el-icon>
          <div class="info-content">
            <span class="info-label">绑定工具</span>
            <span class="info-value">{{ agent.bound_tools_count || 0 }} 个</span>
          </div>
        </div>

        <div class="info-item">
          <el-icon class="info-icon"><DataAnalysis /></el-icon>
          <div class="info-content">
            <span class="info-label">成功率</span>
            <span class="info-value">{{ agent.success_rate?.toFixed(1) || '0.0' }}%</span>
          </div>
        </div>

        <div class="info-item">
          <el-icon class="info-icon"><Timer /></el-icon>
          <div class="info-content">
            <span class="info-label">任务数</span>
            <span class="info-value">{{ agent.completed_tasks || 0 }}/{{ agent.total_tasks || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- 最后执行信息 -->
      <div v-if="agent.last_execution" class="execution-info">
        <el-icon class="execution-icon"><Clock /></el-icon>
        <span class="execution-text">
          最后执行: {{ formatDate(agent.last_execution) }}
        </span>
      </div>
    </div>

    <!-- 卡片底部操作 -->
    <template #footer>
      <div class="card-footer">
        <div class="footer-left">
          <el-tag 
            v-if="agent.is_public" 
            type="info" 
            size="small"
            effect="plain"
          >
            公开
          </el-tag>
          <span class="owner-info">
            创建者: {{ agent.owner_info || '未知' }}
          </span>
        </div>
        <div class="footer-right">
          <el-button 
            type="primary" 
            size="small"
            :disabled="!agent.is_active || agent.status === 'error'"
            @click="handleExecuteTask"
          >
            执行任务
          </el-button>
        </div>
      </div>
    </template>
  </el-card>
</template>

<script>
import { 
  More, View, CopyDocument, 
  Tools, SwitchButton, Open, Delete, Avatar, Cpu, DataAnalysis, 
  Timer, Clock 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/services/api'

export default {
  name: 'AgentCard',
  props: {
    agent: {
      type: Object,
      required: true
    }
  },
  emits: ['refresh', 'view-details', 'manage-tools', 'execute-task'],
  data() {
    return {
      loading: {
        toggle: false,
        delete: false
      }
    }
  },
  setup() {
    return {
      More, View, CopyDocument,
      Tools, SwitchButton, Open, Delete, Avatar, Cpu, DataAnalysis,
      Timer, Clock
    }
  },
  methods: {
    getStatusType(status) {
      const statusMap = {
        'inactive': 'info',
        'active': 'success',
        'running': 'warning',
        'paused': 'warning',
        'error': 'danger'
      }
      return statusMap[status] || 'info'
    },

    getStatusText(status) {
      const statusMap = {
        'inactive': '未激活',
        'active': '激活',
        'running': '运行中',
        'paused': '暂停',
        'error': '错误'
      }
      return statusMap[status] || status
    },

    truncateText(text, maxLength) {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    },

    formatDate(dateString) {
      if (!dateString) return '从未'
      const date = new Date(dateString)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      return date.toLocaleDateString()
    },



    handleExecuteTask() {
      this.$emit('execute-task', this.agent)
    },

    async handleDropdownCommand(command) {
      switch (command) {
        case 'details':
          this.$emit('view-details', this.agent)
          break
        case 'clone':
          await this.handleClone()
          break
        case 'tools':
          this.$emit('manage-tools', this.agent)
          break
        case 'toggle':
          await this.handleToggleActive()
          break
        case 'delete':
          await this.handleDelete()
          break
      }
    },

    async handleClone() {
      try {
        const { value: newName } = await ElMessageBox.prompt(
          '请输入新Agent的名称',
          '克隆Agent',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            inputPattern: /^.{1,64}$/,
            inputErrorMessage: '名称长度应在1-64个字符之间'
          }
        )

        // 创建克隆的Agent数据
        const cloneData = {
          ...this.agent,
          name: newName.replace(/\s+/g, '_').toLowerCase(),
          display_name: newName,
          is_public: false // 克隆的Agent默认为私有
        }
        
        // 移除不需要的字段（只读字段、统计字段、关联信息等）
        delete cloneData.id
        delete cloneData.created_at
        delete cloneData.updated_at
        delete cloneData.status
        delete cloneData.status_display
        delete cloneData.total_tasks
        delete cloneData.completed_tasks
        delete cloneData.total_execution_time
        delete cloneData.last_execution
        delete cloneData.last_error
        delete cloneData.owner
        delete cloneData.owner_info
        delete cloneData.success_rate
        delete cloneData.avg_execution_time
        delete cloneData.bound_tools_count
        delete cloneData.llm_model_info
        delete cloneData.function_calling_llm_info
        delete cloneData.allowed_users

        await api.createCrewAIAgent(cloneData)
        ElMessage.success('Agent克隆成功')
        this.$emit('refresh')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('克隆Agent失败')
          console.error('Clone agent error:', error)
        }
      }
    },

    async handleToggleActive() {
      this.loading.toggle = true
      try {
        const action = this.agent.is_active ? '禁用' : '启用'
        await ElMessageBox.confirm(
          `确定要${action}这个Agent吗？`,
          `${action}Agent`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        await api.updateCrewAIAgent(this.agent.id, {
          is_active: !this.agent.is_active
        })
        
        ElMessage.success(`Agent${action}成功`)
        this.$emit('refresh')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('操作失败')
          console.error('Toggle agent error:', error)
        }
      } finally {
        this.loading.toggle = false
      }
    },

    async handleDelete() {
      try {
        await ElMessageBox.confirm(
          '删除后将无法恢复，确定要删除这个Agent吗？',
          '删除Agent',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'error',
            confirmButtonClass: 'el-button--danger'
          }
        )

        this.loading.delete = true
        await api.deleteCrewAIAgent(this.agent.id)
        ElMessage.success('Agent删除成功')
        this.$emit('refresh')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除Agent失败')
          console.error('Delete agent error:', error)
        }
      } finally {
        this.loading.delete = false
      }
    }
  }
}
</script>

<style scoped>
.agent-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.agent-inactive {
  opacity: 0.7;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.agent-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.agent-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.status-tag {
  font-size: 11px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.agent-content {
  padding: 0;
}

.role-section {
  margin-bottom: 16px;
}

.role-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.role-icon {
  color: #409eff;
  font-size: 20px;
  margin-top: 2px;
}

.role-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.goal-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.info-icon {
  color: #909399;
  font-size: 16px;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.info-label {
  font-size: 11px;
  color: #909399;
  line-height: 1;
  margin-bottom: 2px;
}

.info-value {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.execution-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #c6f7ff;
}

.execution-icon {
  color: #409eff;
  font-size: 14px;
}

.execution-text {
  font-size: 12px;
  color: #606266;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.owner-info {
  font-size: 12px;
  color: #909399;
}

.footer-right {
  display: flex;
  gap: 8px;
}

.danger-item {
  color: #f56c6c !important;
}

.danger-item:hover {
  background-color: #fef0f0 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .card-actions {
    align-self: stretch;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>