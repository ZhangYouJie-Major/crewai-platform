<template>
  <el-dialog
    v-model="visible"
    title="执行Agent任务"
    width="700px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <div class="task-execution-content">
      <!-- Agent信息 -->
      <div class="agent-info-section">
        <h3>
          <el-icon><Monitor /></el-icon>
          Agent信息
        </h3>
        <div class="agent-details">
          <div class="agent-detail-item">
            <span class="label">名称:</span>
            <span class="value">{{ agent?.name }}</span>
          </div>
          <div class="agent-detail-item">
            <span class="label">角色:</span>
            <span class="value">{{ agent?.role }}</span>
          </div>
          <div class="agent-detail-item">
            <span class="label">状态:</span>
            <el-tag :type="agent?.is_active ? 'success' : 'info'" size="small">
              {{ agent?.is_active ? '活跃' : '非活跃' }}
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 任务表单 -->
      <div class="task-form-section">
        <h3>
          <el-icon><Document /></el-icon>
          任务配置
        </h3>
        
        <el-form 
          ref="taskFormRef" 
          :model="taskForm" 
          :rules="taskRules"
          label-width="100px"
        >
          <el-form-item label="任务描述" prop="description">
            <el-input
              v-model="taskForm.description"
              type="textarea"
              :rows="4"
              placeholder="请详细描述要执行的任务，包括目标、要求和期望结果"
              show-word-limit
              maxlength="1000"
            />
            <div class="form-tip">
              任务描述越详细，Agent执行效果越好
            </div>
          </el-form-item>

          <el-form-item label="执行模式" prop="mode">
            <el-radio-group v-model="taskForm.mode">
              <el-radio value="sync">
                <div class="mode-option">
                  <div class="mode-title">同步执行</div>
                  <div class="mode-desc">等待任务完成后返回结果</div>
                </div>
              </el-radio>
              <el-radio value="async">
                <div class="mode-option">
                  <div class="mode-title">异步执行</div>
                  <div class="mode-desc">立即返回，任务在后台执行</div>
                </div>
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="超时时间" prop="timeout">
            <el-input-number
              v-model="taskForm.timeout"
              :min="30"
              :max="3600"
              :step="30"
              style="width: 200px"
            />
            <span style="margin-left: 10px; color: #909399;">秒</span>
            <div class="form-tip">
              超过此时间未完成的任务将被强制终止
            </div>
          </el-form-item>

          <el-form-item label="优先级" prop="priority">
            <el-select 
              v-model="taskForm.priority" 
              style="width: 200px"
              placeholder="选择优先级"
            >
              <el-option label="低优先级" value="low" />
              <el-option label="普通优先级" value="normal" />
              <el-option label="高优先级" value="high" />
              <el-option label="紧急优先级" value="urgent" />
            </el-select>
          </el-form-item>

          <el-form-item label="结果格式">
            <el-select 
              v-model="taskForm.resultFormat" 
              style="width: 200px"
              placeholder="选择结果格式"
            >
              <el-option label="纯文本" value="text" />
              <el-option label="JSON格式" value="json" />
              <el-option label="Markdown" value="markdown" />
            </el-select>
          </el-form-item>

          <el-form-item label="自动保存">
            <el-switch v-model="taskForm.autoSave" />
            <span style="margin-left: 10px; color: #909399;">
              自动保存执行结果到历史记录
            </span>
          </el-form-item>
        </el-form>
      </div>

      <!-- 执行状态 -->
      <div v-if="executing" class="execution-status">
        <h3>
          <el-icon><Loading /></el-icon>
          执行状态
        </h3>
        <div class="status-content">
          <el-progress 
            :percentage="executionProgress" 
            :status="executionStatus"
            :stroke-width="8"
          />
          <div class="status-message">{{ executionMessage }}</div>
          <div class="execution-time">
            执行时间: {{ formatDuration(executionDuration) }}
          </div>
        </div>
      </div>

      <!-- 执行结果 -->
      <div v-if="executionResult" class="execution-result">
        <h3>
          <el-icon><Check /></el-icon>
          执行结果
        </h3>
        <div class="result-content">
          <el-alert
            :type="executionResult.success ? 'success' : 'error'"
            :title="executionResult.success ? '任务执行成功' : '任务执行失败'"
            :description="executionResult.message"
            show-icon
            :closable="false"
          />
          
          <div v-if="executionResult.data" class="result-data">
            <div class="result-header">
              <span>执行输出:</span>
              <el-button-group size="small">
                <el-button icon="CopyDocument" @click="copyResult">
                  复制
                </el-button>
                <el-button icon="Download" @click="downloadResult">
                  下载
                </el-button>
              </el-button-group>
            </div>
            <div class="result-viewer">
              <pre class="result-text">{{ formatResult(executionResult.data) }}</pre>
            </div>
          </div>

          <div v-if="executionResult.metrics" class="result-metrics">
            <h4>执行统计</h4>
            <el-row :gutter="16">
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">执行时间</div>
                  <div class="metric-value">{{ executionResult.metrics.duration }}s</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">使用工具</div>
                  <div class="metric-value">{{ executionResult.metrics.toolsUsed || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">输出长度</div>
                  <div class="metric-value">{{ executionResult.metrics.outputLength || 0 }}</div>
                </div>
              </el-col>
              <el-col :span="6">
                <div class="metric-item">
                  <div class="metric-label">消耗Token</div>
                  <div class="metric-value">{{ executionResult.metrics.tokensUsed || 0 }}</div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="executing">
          {{ executing ? '执行中...' : '取消' }}
        </el-button>
        <el-button 
          v-if="!executing && !executionResult"
          type="primary" 
          @click="executeTask"
          :disabled="!taskForm.description.trim()"
        >
          <el-icon><VideoPlay /></el-icon>
          执行任务
        </el-button>
        <el-button 
          v-if="executing"
          type="danger" 
          @click="stopExecution"
        >
          <el-icon><VideoPause /></el-icon>
          停止执行
        </el-button>
        <el-button 
          v-if="executionResult && !executing"
          type="primary" 
          @click="handleClose"
        >
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor, Document, Loading, Check, VideoPlay, VideoPause,
  CopyDocument, Download
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
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 响应式数据
const taskFormRef = ref()
const executing = ref(false)
const executionProgress = ref(0)
const executionStatus = ref('')
const executionMessage = ref('')
const executionDuration = ref(0)
const executionResult = ref(null)
const executionTimer = ref(null)
const startTime = ref(null)

const taskForm = ref({
  description: '',
  mode: 'sync',
  timeout: 300,
  priority: 'normal',
  resultFormat: 'text',
  autoSave: true
})

const taskRules = {
  description: [
    { required: true, message: '请输入任务描述', trigger: 'blur' },
    { min: 10, message: '任务描述至少需要10个字符', trigger: 'blur' }
  ],
  mode: [
    { required: true, message: '请选择执行模式', trigger: 'change' }
  ],
  timeout: [
    { required: true, message: '请设置超时时间', trigger: 'blur' },
    { type: 'number', min: 30, max: 3600, message: '超时时间范围为30-3600秒', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
  ]
}

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})

// 方法
const executeTask = async () => {
  if (!taskFormRef.value) return
  
  try {
    const valid = await taskFormRef.value.validate()
    if (!valid) return

    executing.value = true
    executionProgress.value = 0
    executionStatus.value = 'active'
    executionMessage.value = '准备执行任务...'
    executionResult.value = null
    startTime.value = Date.now()

    // 开始计时器
    startExecutionTimer()

    const taskData = {
      description: taskForm.value.description,
      mode: taskForm.value.mode,
      timeout: taskForm.value.timeout,
      priority: taskForm.value.priority,
      result_format: taskForm.value.resultFormat,
      auto_save: taskForm.value.autoSave
    }

    executionMessage.value = '正在执行任务...'
    executionProgress.value = 20

    const response = await api.executeCrewAIAgentTask(props.agent.id, taskData)
    
    if (taskForm.value.mode === 'sync') {
      // 同步执行，直接处理结果
      handleExecutionComplete(response.data)
    } else {
      // 异步执行，启动轮询检查状态
      const taskId = response.data.task_id
      pollTaskStatus(taskId)
    }

  } catch (error) {
    console.error('执行任务失败:', error)
    handleExecutionError(error)
  }
}

const pollTaskStatus = async (taskId) => {
  try {
    const response = await api.getTaskStatus(taskId)
    const status = response.data

    executionMessage.value = status.message || '任务执行中...'
    executionProgress.value = Math.min(status.progress || 30, 90)

    if (status.status === 'completed') {
      handleExecutionComplete(status)
    } else if (status.status === 'failed') {
      handleExecutionError(new Error(status.error || '任务执行失败'))
    } else {
      // 继续轮询
      setTimeout(() => pollTaskStatus(taskId), 2000)
    }
  } catch (error) {
    handleExecutionError(error)
  }
}

const handleExecutionComplete = (result) => {
  stopExecutionTimer()
  executing.value = false
  executionProgress.value = 100
  executionStatus.value = 'success'
  executionMessage.value = '任务执行完成'
  
  executionResult.value = {
    success: true,
    message: '任务执行成功完成',
    data: result.result || result.output,
    metrics: {
      duration: Math.round((Date.now() - startTime.value) / 1000),
      toolsUsed: result.tools_used,
      outputLength: result.result?.length || 0,
      tokensUsed: result.tokens_used
    }
  }

  ElMessage.success('任务执行完成')
}

const handleExecutionError = (error) => {
  stopExecutionTimer()
  executing.value = false
  executionProgress.value = 100
  executionStatus.value = 'exception'
  executionMessage.value = '任务执行失败'
  
  executionResult.value = {
    success: false,
    message: error.message || '任务执行失败',
    data: null,
    metrics: {
      duration: Math.round((Date.now() - startTime.value) / 1000)
    }
  }

  ElMessage.error('任务执行失败')
}

const stopExecution = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要停止当前任务的执行吗？',
      '停止确认',
      {
        confirmButtonText: '停止',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.stopCrewAIAgent(props.agent.id)
    handleExecutionError(new Error('用户手动停止任务'))
  } catch (error) {
    if (error !== 'cancel') {
      console.error('停止任务失败:', error)
      ElMessage.error('停止任务失败')
    }
  }
}

const startExecutionTimer = () => {
  executionTimer.value = setInterval(() => {
    if (startTime.value) {
      executionDuration.value = Math.round((Date.now() - startTime.value) / 1000)
    }
  }, 1000)
}

const stopExecutionTimer = () => {
  if (executionTimer.value) {
    clearInterval(executionTimer.value)
    executionTimer.value = null
  }
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatResult = (data) => {
  if (typeof data === 'string') {
    return data
  }
  return JSON.stringify(data, null, 2)
}

const copyResult = async () => {
  try {
    const text = formatResult(executionResult.value.data)
    await navigator.clipboard.writeText(text)
    ElMessage.success('结果已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const downloadResult = () => {
  const text = formatResult(executionResult.value.data)
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = `agent_task_result_${new Date().toISOString().split('T')[0]}.txt`
  link.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('结果已下载')
}

const handleClose = () => {
  if (executing.value) {
    ElMessage.warning('任务执行中，无法关闭')
    return
  }
  visible.value = false
}

const handleClosed = () => {
  // 重置表单和状态
  taskForm.value = {
    description: '',
    mode: 'sync',
    timeout: 300,
    priority: 'normal',
    resultFormat: 'text',
    autoSave: true
  }
  
  executing.value = false
  executionProgress.value = 0
  executionStatus.value = ''
  executionMessage.value = ''
  executionDuration.value = 0
  executionResult.value = null
  
  stopExecutionTimer()
}

// 生命周期
onUnmounted(() => {
  stopExecutionTimer()
})
</script>

<style scoped>
.task-execution-content {
  max-height: 70vh;
  overflow-y: auto;
}

.agent-info-section,
.task-form-section,
.execution-status,
.execution-result {
  margin-bottom: 30px;
}

.agent-info-section h3,
.task-form-section h3,
.execution-status h3,
.execution-result h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.agent-details {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.agent-detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.agent-detail-item:last-child {
  margin-bottom: 0;
}

.agent-detail-item .label {
  font-weight: 500;
  color: #606266;
  width: 60px;
  margin-right: 12px;
}

.agent-detail-item .value {
  color: #303133;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.mode-option {
  margin-left: 8px;
}

.mode-title {
  font-weight: 500;
  color: #303133;
}

.mode-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.status-content {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  text-align: center;
}

.status-message {
  margin: 16px 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.execution-time {
  font-size: 12px;
  color: #909399;
}

.result-content {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.result-data {
  margin-top: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 500;
  color: #303133;
}

.result-viewer {
  background: white;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.result-text {
  padding: 16px;
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: #303133;
  background: white;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.result-metrics {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #ebeef5;
}

.result-metrics h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #303133;
}

.metric-item {
  text-align: center;
  padding: 12px;
  background: white;
  border-radius: 4px;
  border: 1px solid #ebeef5;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .result-metrics .el-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .metric-item {
    margin-bottom: 8px;
  }
}
</style>