<template>
  <el-card 
    class="tool-card" 
    shadow="hover"
    :class="{ 'tool-unhealthy': tool.health_status !== 'healthy' }"
  >
    <!-- 卡片头部 -->
    <template #header>
      <div class="card-header">
        <div class="tool-title">
          <span class="tool-name">{{ tool.name }}</span>
          <el-tag 
            :type="getHealthType(tool.health_status)" 
            size="small"
            class="status-tag"
          >
            {{ getHealthText(tool.health_status) }}
          </el-tag>
        </div>
        <div class="card-actions">
          <el-button-group size="small">
            <el-tooltip content="测试连接" placement="top">
              <el-button 
                :icon="Monitor" 
                :loading="loading.test"
                @click="handleTest"
              />
            </el-tooltip>
            <el-tooltip content="调用工具" placement="top">
              <el-button 
                :icon="VideoPlay" 
                :disabled="tool.health_status !== 'healthy'"
                @click="handleCall"
              />
            </el-tooltip>
            <el-dropdown @command="handleDropdownCommand">
              <el-button :icon="More" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit" :icon="Edit">编辑配置</el-dropdown-item>
                  <el-dropdown-item command="copy" :icon="CopyDocument">复制配置</el-dropdown-item>
                  <el-dropdown-item 
                    command="toggle" 
                    :icon="tool.is_public ? Lock : Share"
                  >
                    {{ tool.is_public ? '设为私有' : '设为公开' }}
                  </el-dropdown-item>
                  <el-dropdown-item 
                    command="delete" 
                    :icon="Delete" 
                    class="danger-item"
                  >
                    删除工具
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-button-group>
        </div>
      </div>
    </template>

    <!-- 卡片内容 -->
    <div class="tool-content">
      <!-- 描述信息 -->
      <div class="description-section">
        <div class="description-info">
          <el-icon class="desc-icon"><Document /></el-icon>
          <div class="desc-text" :title="tool.description">
            {{ truncateText(tool.description || '无描述', 80) }}
          </div>
        </div>
      </div>

      <!-- 服务器信息 -->
      <div class="server-section">
        <div class="server-info">
          <el-icon class="server-icon"><Link /></el-icon>
          <div class="server-content">
            <div class="server-label">服务地址</div>
            <div class="server-url" :title="tool.server_url">
              {{ truncateText(tool.server_url, 40) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 配置信息 -->
      <div class="config-grid">
        <div class="config-item">
          <el-icon class="config-icon"><Key /></el-icon>
          <div class="config-content">
            <span class="config-label">认证</span>
            <span class="config-value">{{ tool.auth_required ? '需要' : '无需' }}</span>
          </div>
        </div>
        
        <div class="config-item">
          <el-icon class="config-icon"><Share /></el-icon>
          <div class="config-content">
            <span class="config-label">可见性</span>
            <span class="config-value">{{ tool.is_public ? '公开' : '私有' }}</span>
          </div>
        </div>

        <div class="config-item">
          <el-icon class="config-icon"><Timer /></el-icon>
          <div class="config-content">
            <span class="config-label">超时</span>
            <span class="config-value">{{ tool.timeout || 30 }}s</span>
          </div>
        </div>

        <div class="config-item">
          <el-icon class="config-icon"><DataAnalysis /></el-icon>
          <div class="config-content">
            <span class="config-label">版本</span>
            <span class="config-value">{{ tool.version || 'v1.0' }}</span>
          </div>
        </div>
      </div>

      <!-- 最后检查信息 -->
      <div v-if="tool.last_health_check" class="health-info">
        <el-icon class="health-icon"><Clock /></el-icon>
        <span class="health-text">
          最后检查: {{ formatDate(tool.last_health_check) }}
        </span>
      </div>
    </div>

    <!-- 卡片底部操作 -->
    <template #footer>
      <div class="card-footer">
        <div class="footer-left">
          <el-tag 
            v-if="tool.is_public" 
            type="success" 
            size="small"
            effect="plain"
          >
            公开工具
          </el-tag>
          <span class="created-info">
            创建: {{ formatShortDate(tool.created_at) }}
          </span>
        </div>
        <div class="footer-right">
          <el-button 
            type="primary" 
            size="small"
            :disabled="tool.health_status !== 'healthy'"
            @click="handleCall"
          >
            立即调用
          </el-button>
        </div>
      </div>
    </template>
  </el-card>
</template>

<script>
import { 
  Monitor, VideoPlay, More, Edit, CopyDocument, 
  Share, Lock, Delete, Document, Link, Key, 
  Timer, DataAnalysis, Clock 
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'MCPToolCard',
  props: {
    tool: {
      type: Object,
      required: true
    }
  },
  emits: ['refresh', 'edit', 'delete', 'test', 'call'],
  data() {
    return {
      loading: {
        test: false,
        toggle: false,
        delete: false
      }
    }
  },
  setup() {
    return {
      Monitor, VideoPlay, More, Edit, CopyDocument,
      Share, Lock, Delete, Document, Link, Key,
      Timer, DataAnalysis, Clock
    }
  },
  methods: {
    getHealthType(healthStatus) {
      const statusMap = {
        'healthy': 'success',
        'unhealthy': 'danger',
        'warning': 'warning'
      }
      return statusMap[healthStatus] || 'info'
    },

    getHealthText(healthStatus) {
      const statusMap = {
        'healthy': '健康',
        'unhealthy': '异常',
        'warning': '警告'
      }
      return statusMap[healthStatus] || '未知'
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

    formatShortDate(dateString) {
      if (!dateString) return '未知'
      return new Date(dateString).toLocaleDateString()
    },

    async handleTest() {
      this.loading.test = true
      try {
        this.$emit('test', this.tool)
      } finally {
        this.loading.test = false
      }
    },

    handleCall() {
      this.$emit('call', this.tool)
    },

    async handleDropdownCommand(command) {
      switch (command) {
        case 'edit':
          this.$emit('edit', this.tool)
          break
        case 'copy':
          await this.handleCopy()
          break
        case 'toggle':
          await this.handleToggleVisibility()
          break
        case 'delete':
          this.$emit('delete', this.tool)
          break
      }
    },

    async handleCopy() {
      try {
        const configText = JSON.stringify({
          name: this.tool.name + '_copy',
          description: this.tool.description,
          server_url: this.tool.server_url,
          auth_required: this.tool.auth_required,
          timeout: this.tool.timeout,
          version: this.tool.version
        }, null, 2)
        
        await navigator.clipboard.writeText(configText)
        ElMessage.success('配置已复制到剪贴板')
      } catch (error) {
        ElMessage.error('复制失败')
        console.error('Copy config error:', error)
      }
    },

    async handleToggleVisibility() {
      this.loading.toggle = true
      try {
        const action = this.tool.is_public ? '设为私有' : '设为公开'
        await ElMessageBox.confirm(
          `确定要${action}这个工具吗？`,
          `${action}工具`,
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 这里应该调用API更新工具的可见性
        // await this.$api.mcpTools.update(this.tool.id, {
        //   is_public: !this.tool.is_public
        // })
        
        ElMessage.success(`工具${action}成功`)
        this.$emit('refresh')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('操作失败')
          console.error('Toggle visibility error:', error)
        }
      } finally {
        this.loading.toggle = false
      }
    }
  }
}
</script>

<style scoped>
.tool-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.tool-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.tool-unhealthy {
  border-left: 4px solid #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0;
}

.tool-title {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.tool-name {
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

.tool-content {
  padding: 0;
}

.description-section {
  margin-bottom: 16px;
}

.description-info {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.desc-icon {
  color: #409eff;
  font-size: 18px;
  margin-top: 2px;
  flex-shrink: 0;
}

.desc-text {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.server-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.server-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.server-icon {
  color: #67c23a;
  font-size: 16px;
  flex-shrink: 0;
}

.server-content {
  min-width: 0;
  flex: 1;
}

.server-label {
  font-size: 11px;
  color: #909399;
  line-height: 1;
  margin-bottom: 4px;
}

.server-url {
  font-size: 12px;
  color: #303133;
  font-family: monospace;
  word-break: break-all;
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #ebeef5;
}

.config-icon {
  color: #909399;
  font-size: 14px;
  flex-shrink: 0;
}

.config-content {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.config-label {
  font-size: 10px;
  color: #909399;
  line-height: 1;
  margin-bottom: 2px;
}

.config-value {
  font-size: 12px;
  color: #303133;
  font-weight: 500;
  line-height: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.health-info {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  border: 1px solid #c6f7ff;
}

.health-icon {
  color: #409eff;
  font-size: 14px;
}

.health-text {
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

.created-info {
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
  .config-grid {
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