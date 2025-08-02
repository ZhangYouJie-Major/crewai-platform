<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    title="调用MCP工具"
    width="800px"
    :close-on-click-modal="false"
  >
    <div class="tool-call-container">
      <!-- 工具信息 -->
      <div class="tool-info">
        <el-card>
          <template #header>
            <div class="tool-header">
              <span class="tool-name">{{ tool?.name }}</span>
              <el-tag :type="getHealthType(tool?.health_status)" size="small">
                {{ getHealthText(tool?.health_status) }}
              </el-tag>
            </div>
          </template>
          <div class="tool-details">
            <p><strong>描述:</strong> {{ tool?.description || '无描述' }}</p>
            <p><strong>服务地址:</strong> {{ tool?.server_url }}</p>
            <p><strong>版本:</strong> {{ tool?.version || 'v1.0.0' }}</p>
          </div>
        </el-card>
      </div>

      <!-- 调用参数 -->
      <div class="call-params">
        <el-card>
          <template #header>
            <span>调用参数</span>
          </template>
          
          <el-form :model="callData" label-width="100px">
            <el-form-item label="调用方法">
              <el-select 
                v-model="callData.method" 
                placeholder="请选择调用方法"
                style="width: 100%"
                @change="handleMethodChange"
              >
                <el-option 
                  v-for="method in availableMethods" 
                  :key="method.value"
                  :label="method.label" 
                  :value="method.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="请求参数">
              <div class="params-editor">
                <el-tabs v-model="paramMode" type="border-card">
                  <el-tab-pane label="表单模式" name="form">
                    <div class="form-params">
                      <el-button @click="addParam" size="small" type="primary" icon="Plus">
                        添加参数
                      </el-button>
                      <div class="params-list">
                        <div 
                          v-for="(param, index) in callData.params" 
                          :key="index"
                          class="param-item"
                        >
                          <el-input
                            v-model="param.key"
                            placeholder="参数名"
                            style="width: 30%"
                          />
                          <el-select
                            v-model="param.type"
                            placeholder="类型"
                            style="width: 20%"
                          >
                            <el-option label="字符串" value="string" />
                            <el-option label="数字" value="number" />
                            <el-option label="布尔" value="boolean" />
                            <el-option label="对象" value="object" />
                          </el-select>
                          <el-input
                            v-model="param.value"
                            placeholder="参数值"
                            style="width: 35%"
                          />
                          <el-button
                            @click="removeParam(index)"
                            size="small"
                            type="danger"
                            icon="Delete"
                          />
                        </div>
                      </div>
                    </div>
                  </el-tab-pane>
                  
                  <el-tab-pane label="JSON模式" name="json">
                    <div class="json-params">
                      <el-input
                        v-model="callData.jsonParams"
                        type="textarea"
                        :rows="8"
                        placeholder="请输入JSON格式的参数，例如：&#10;{&#10;  &quot;param1&quot;: &quot;value1&quot;,&#10;  &quot;param2&quot;: 123&#10;}"
                      />
                      <div class="json-actions">
                        <el-button @click="formatJson" size="small">格式化</el-button>
                        <el-button @click="validateJson" size="small" type="info">验证</el-button>
                        <el-button @click="clearJson" size="small" type="warning">清空</el-button>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </el-form-item>

            <el-form-item label="超时时间">
              <el-input-number
                v-model="callData.timeout"
                :min="1"
                :max="300"
                :step="1"
                controls-position="right"
                style="width: 200px"
              />
              <span style="margin-left: 10px; color: #909399;">秒</span>
            </el-form-item>
          </el-form>
        </el-card>
      </div>

      <!-- 调用历史 -->
      <div class="call-history" v-if="callHistory.length > 0">
        <el-card>
          <template #header>
            <div class="history-header">
              <span>调用历史</span>
              <el-button @click="clearHistory" size="small" type="danger" plain>
                清空历史
              </el-button>
            </div>
          </template>
          <div class="history-list">
            <div 
              v-for="(record, index) in callHistory" 
              :key="index"
              class="history-item"
              @click="loadHistoryRecord(record)"
            >
              <div class="history-info">
                <span class="history-method">{{ record.method }}</span>
                <span class="history-time">{{ formatTime(record.timestamp) }}</span>
                <el-tag 
                  :type="record.success ? 'success' : 'danger'" 
                  size="small"
                >
                  {{ record.success ? '成功' : '失败' }}
                </el-tag>
              </div>
              <div class="history-duration">
                耗时: {{ record.duration }}ms
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 调用结果 -->
      <div class="call-result" v-if="callResult">
        <el-card>
          <template #header>
            <div class="result-header">
              <span>调用结果</span>
              <div class="result-actions">
                <el-button @click="copyResult" size="small" icon="CopyDocument">
                  复制结果
                </el-button>
                <el-button @click="downloadResult" size="small" icon="Download">
                  下载结果
                </el-button>
              </div>
            </div>
          </template>
          <div class="result-content">
            <el-tabs type="border-card">
              <el-tab-pane label="响应数据" name="data">
                <pre class="result-json">{{ formatJsonResult(callResult.data) }}</pre>
              </el-tab-pane>
              <el-tab-pane label="响应详情" name="details">
                <div class="result-details">
                  <p><strong>状态码:</strong> {{ callResult.status }}</p>
                  <p><strong>调用时间:</strong> {{ formatTime(callResult.timestamp) }}</p>
                  <p><strong>执行耗时:</strong> {{ callResult.duration }}ms</p>
                  <p><strong>响应大小:</strong> {{ formatBytes(JSON.stringify(callResult.data).length) }}</p>
                </div>
              </el-tab-pane>
              <el-tab-pane label="错误信息" name="error" v-if="callResult.error">
                <div class="result-error">
                  <pre>{{ callResult.error }}</pre>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">关闭</el-button>
        <el-button type="primary" @click="handleCall" :loading="calling">
          <el-icon><VideoPlay /></el-icon>
          调用工具
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete, CopyDocument, Download, VideoPlay } from '@element-plus/icons-vue'
import api from '@/services/api'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  tool: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:visible', 'success'])

// 状态管理
const calling = ref(false)
const paramMode = ref('form')

// 可用方法列表
const availableMethods = ref([
  { label: 'execute - 执行工具', value: 'execute' },
  { label: 'test - 测试连接', value: 'test' },
  { label: 'info - 获取信息', value: 'info' },
  { label: 'status - 检查状态', value: 'status' }
])

// 调用数据
const callData = reactive({
  method: 'execute',
  params: [],
  jsonParams: '{}',
  timeout: 30
})

// 调用历史
const callHistory = ref([])

// 调用结果
const callResult = ref(null)

// 监听弹窗显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initCallData()
  }
})

// 初始化调用数据
const initCallData = () => {
  callData.method = 'execute'
  callData.params = []
  callData.jsonParams = '{}'
  callData.timeout = 30
  callResult.value = null
}

// 工具状态相关方法
const getHealthType = (healthStatus) => {
  const statusMap = {
    'healthy': 'success',
    'unhealthy': 'danger',
    'warning': 'warning'
  }
  return statusMap[healthStatus] || 'info'
}

const getHealthText = (healthStatus) => {
  const statusMap = {
    'healthy': '健康',
    'unhealthy': '异常',
    'warning': '警告'
  }
  return statusMap[healthStatus] || '未知'
}

// 参数管理方法
const addParam = () => {
  callData.params.push({ key: '', type: 'string', value: '' })
}

const removeParam = (index) => {
  callData.params.splice(index, 1)
}

// JSON处理方法
const formatJson = () => {
  try {
    const parsed = JSON.parse(callData.jsonParams)
    callData.jsonParams = JSON.stringify(parsed, null, 2)
    ElMessage.success('JSON格式化成功')
  } catch (error) {
    ElMessage.error('JSON格式错误，无法格式化')
  }
}

const validateJson = () => {
  try {
    JSON.parse(callData.jsonParams)
    ElMessage.success('JSON格式正确')
  } catch (error) {
    ElMessage.error('JSON格式错误: ' + error.message)
  }
}

const clearJson = () => {
  callData.jsonParams = '{}'
}

// 处理方法变化
const handleMethodChange = () => {
  // 根据方法设置默认参数
  switch (callData.method) {
    case 'execute':
      callData.jsonParams = JSON.stringify({
        action: 'run',
        input: 'your input here'
      }, null, 2)
      break
    case 'test':
      callData.jsonParams = '{}'
      break
    case 'info':
      callData.jsonParams = JSON.stringify({
        detail: true
      }, null, 2)
      break
    case 'status':
      callData.jsonParams = '{}'
      break
  }
}

// 调用工具
const handleCall = async () => {
  try {
    calling.value = true
    const startTime = Date.now()
    
    // 准备调用参数
    let params = {}
    if (paramMode.value === 'form') {
      // 表单模式：将参数数组转换为对象
      callData.params.forEach(param => {
        if (param.key && param.value) {
          let value = param.value
          // 根据类型转换值
          switch (param.type) {
            case 'number':
              value = Number(value)
              break
            case 'boolean':
              value = value === 'true'
              break
            case 'object':
              try {
                value = JSON.parse(value)
              } catch (e) {
                throw new Error(`参数 ${param.key} 的对象格式错误`)
              }
              break
          }
          params[param.key] = value
        }
      })
    } else {
      // JSON模式：直接解析JSON
      try {
        params = JSON.parse(callData.jsonParams)
      } catch (error) {
        throw new Error('JSON参数格式错误: ' + error.message)
      }
    }
    
    // 构造调用数据
    const requestData = {
      method: callData.method,
      params: params,
      timeout: callData.timeout
    }
    
    // 调用API
    const response = await api.callMCPTool(props.tool.id, requestData)
    const endTime = Date.now()
    const duration = endTime - startTime
    
    // 设置调用结果
    callResult.value = {
      data: response.data,
      status: response.status,
      timestamp: new Date(),
      duration: duration,
      success: true
    }
    
    // 添加到历史记录
    callHistory.value.unshift({
      method: callData.method,
      params: params,
      timestamp: new Date(),
      duration: duration,
      success: true,
      result: response.data
    })
    
    ElMessage.success('工具调用成功')
    emit('success')
    
  } catch (error) {
    const endTime = Date.now()
    const duration = endTime - (calling.value ? Date.now() - 1000 : Date.now())
    
    // 设置错误结果
    callResult.value = {
      data: null,
      status: error.response?.status || 500,
      timestamp: new Date(),
      duration: duration,
      success: false,
      error: error.response?.data?.message || error.message
    }
    
    // 添加到历史记录
    callHistory.value.unshift({
      method: callData.method,
      params: paramMode.value === 'json' ? JSON.parse(callData.jsonParams || '{}') : {},
      timestamp: new Date(),
      duration: duration,
      success: false,
      error: error.response?.data?.message || error.message
    })
    
    console.error('工具调用失败:', error)
    ElMessage.error('工具调用失败: ' + (error.response?.data?.message || error.message))
  } finally {
    calling.value = false
  }
}

// 加载历史记录
const loadHistoryRecord = (record) => {
  callData.method = record.method
  if (record.params && Object.keys(record.params).length > 0) {
    paramMode.value = 'json'
    callData.jsonParams = JSON.stringify(record.params, null, 2)
  }
}

// 清空历史
const clearHistory = () => {
  callHistory.value = []
  ElMessage.success('历史记录已清空')
}

// 格式化时间
const formatTime = (date) => {
  return new Date(date).toLocaleString('zh-CN')
}

// 格式化JSON结果
const formatJsonResult = (data) => {
  try {
    return JSON.stringify(data, null, 2)
  } catch (error) {
    return String(data)
  }
}

// 格式化字节大小
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 复制结果
const copyResult = async () => {
  try {
    const resultText = formatJsonResult(callResult.value.data)
    await navigator.clipboard.writeText(resultText)
    ElMessage.success('结果已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 下载结果
const downloadResult = () => {
  try {
    const resultText = formatJsonResult(callResult.value.data)
    const blob = new Blob([resultText], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${props.tool.name}_result_${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('结果已下载')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 取消操作
const handleCancel = () => {
  emit('update:visible', false)
}
</script>

<style scoped>
.tool-call-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 70vh;
  overflow-y: auto;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
}

.tool-details p {
  margin: 5px 0;
  font-size: 14px;
}

.params-editor {
  width: 100%;
}

.form-params {
  padding: 10px 0;
}

.params-list {
  margin-top: 10px;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.json-params {
  padding: 10px 0;
}

.json-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-list {
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  padding: 10px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  background-color: #f5f7fa;
  border-color: #409eff;
}

.history-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.history-method {
  font-weight: 600;
  color: #303133;
}

.history-time {
  font-size: 12px;
  color: #909399;
}

.history-duration {
  font-size: 12px;
  color: #606266;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-actions {
  display: flex;
  gap: 10px;
}

.result-content {
  max-height: 400px;
  overflow-y: auto;
}

.result-json {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow-y: auto;
}

.result-details p {
  margin: 8px 0;
  font-size: 14px;
}

.result-error {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  padding: 15px;
}

.result-error pre {
  color: #f56c6c;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.el-card__header) {
  padding: 15px 20px;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>